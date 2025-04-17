import os
import logging
import numpy as np
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from langchain.schema import Document
from langchain.embeddings.base import Embeddings

# Load environment variables
load_dotenv()
API_KEY = os.getenv('GEMINI_API_KEY')
MODEL_NAME = 'models/gemini-2.0-flash'
genai.configure(api_key=API_KEY)

# Global variables
vector_storage = None
last_uploaded_pdf_text = None


# Mock Embedding class 
class MockEmbeddings(Embeddings):
    def embed_documents(self, texts):
        return [np.random.rand(512).tolist() for _ in texts]

    def embed_query(self, text):
        return np.random.rand(512).tolist()


# Splitting PDF text into chunks and creating Document objects
def load_and_split_text(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=50)
    chunks = splitter.split_text(text)
    return [Document(page_content=chunk, metadata={"id": str(i)}) for i, chunk in enumerate(chunks)]


# Creating vector storage from chunks
def create_vector_storage(pages):
    mock_embeddings = MockEmbeddings()
    return FAISS.from_documents(pages, mock_embeddings)


# Creating a prompt template for the language model
def create_prompt_template():
    question_template = """
    You are a smart bot that answers questions based only on the context given to you.
    You don't make things up.
    Context: {context}
    Question: {question}
    """
    return PromptTemplate.from_template(template=question_template)


# Class to retrieve relevant chunks and generate answers using Gemini
class RetrieveAndAnswer:
    def __init__(self, retriever, prompt_template):
        self.retriever = retriever
        self.prompt_template = prompt_template
        self.model = genai.GenerativeModel(MODEL_NAME)

    def invoke(self, question):
        try:
            docs = self.retriever.invoke(question)
            context = ' '.join([doc.page_content for doc in docs])
            formatted_prompt = self.prompt_template.format(context=context, question=question)

            response = self.model.generate_content(formatted_prompt)

            if response.text:
                response_text = response.text
                confidence_score = self.calculate_confidence(response_text, question)
                return response_text, confidence_score
            else:
                return "No answer generated.", 0
        except ResourceExhausted as e:
            logging.error(f"Gemini API quota exceeded: {e}")
            return "Gemini API quota exceeded, try again later.", 0
        except Exception as e:
            logging.error(f"Error invoking Gemini model: {e}")
            return "Error processing request, try again.", 0
    def calculate_confidence(self, response_text, question):
        import re
        from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
        from sentence_transformers import SentenceTransformer, util

        model = SentenceTransformer('all-MiniLM-L6-v2')

        question_embedding = model.encode(question, convert_to_tensor=True)
        response_embedding = model.encode(response_text, convert_to_tensor=True)

        similarity_score = float(util.cos_sim(question_embedding, response_embedding)[0][0])
        semantic_boost = int(similarity_score * 100)  # Scale to 0–100

        irrelevant_phrases = [
            "not contain information",
            "not contain any information",
            "i cannot answer",
            "no information available",
            "context does not mention",
            "cannot find",
            "i don’t know",
            "i do not know"
        ]

        response_lower = response_text.strip().lower()
        response_sentences = [s.strip() for s in re.split(r'[.!?]', response_lower) if s.strip()]

        irrelevant_count = sum(
            any(phrase in sentence for phrase in irrelevant_phrases)
            for sentence in response_sentences
        )

        irrelevant_ratio = irrelevant_count / max(len(response_sentences), 1)

        if similarity_score < 0.3 and irrelevant_ratio > 0.5:
            return 10

        ending_bonus = 5 if response_text.strip().endswith(('.', '?')) else 0

        confidence = semantic_boost + ending_bonus
        return max(min(confidence, 100), 0)




# Upload PDF and create/update vector DB
def upload_pdf_and_create_db(pdf_text):
    global vector_storage, last_uploaded_pdf_text
    try:
        if pdf_text != last_uploaded_pdf_text:
            pages = load_and_split_text(pdf_text)
            vector_storage = create_vector_storage(pages)
            last_uploaded_pdf_text = pdf_text
            return "PDF processed and vector DB updated.", True
        else:
            return "Same PDF detected. Using existing vector DB.", True
    except Exception as e:
        logging.error(f"Error uploading PDF: {e}")
        return "Error while processing the uploaded PDF.", False


# Answer user question
def answer_question(question):
    global vector_storage
    try:
        if not vector_storage:
            logging.warning("Tried answering without uploading PDF.")
            return "No PDF uploaded yet. Please upload a PDF first."

        retriever = vector_storage.as_retriever()
        prompt = create_prompt_template()
        bot = RetrieveAndAnswer(retriever, prompt)

        response_text, confidence_score = bot.invoke(question)

        return f"Response: {response_text}\nConfidence: {confidence_score}"
    except Exception as e:
        logging.error(f"Error answering question: {e}")
        return "Error while answering the question."
