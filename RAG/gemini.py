
import os
import logging
import numpy as np
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from langchain.schema import Document  # ✅ Use built-in class
from langchain.embeddings.base import Embeddings  # make sure this is imported

# Load environment variables
load_dotenv()
API_KEY = os.getenv('GEMINI_API_KEY')
MODEL_NAME = 'models/gemini-2.0-flash'
genai.configure(api_key=API_KEY)

# ✅ Global variables
vector_storage = None
last_uploaded_pdf_text = None  # to detect new upload


class MockEmbeddings(Embeddings):
    def embed_documents(self, texts):
        return [np.random.rand(512).tolist() for _ in texts]

    def embed_query(self, text):
        return np.random.rand(512).tolist()



def load_and_split_text(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
    chunks = splitter.split_text(text)
    return [Document(page_content=chunk, metadata={"id": str(i)}) for i, chunk in enumerate(chunks)]


def create_vector_storage(pages):
    mock_embeddings = MockEmbeddings()
    return FAISS.from_documents(pages, mock_embeddings)

def create_prompt_template():
    question_template = """
    You are a smart bot that answers questions based only on the context given to you.
    You don't make things up.
    Context: {context}
    Question: {question}
    """
    return PromptTemplate.from_template(template=question_template)


class RetrieveAndAnswer:
    def __init__(self, retriever, prompt_template):
        self.retriever = retriever
        self.prompt_template = prompt_template
        self.model = genai.GenerativeModel('models/gemini-2.0-flash')  # correct model name

    def invoke(self, question):
        try:
            docs = self.retriever.invoke(question)  # updated for deprecation
            context = ' '.join([doc.page_content for doc in docs])
            formatted_prompt = self.prompt_template.format(context=context, question=question)

            response = self.model.generate_content(formatted_prompt)

            return response.text if response.text else "No answer generated."
        except ResourceExhausted as e:
            logging.error(f"Gemini API quota exceeded: {e}")
            return "Gemini API quota exceeded, try again later."
        except Exception as e:
            logging.error(f"Error invoking Gemini model: {e}")
            return "Error processing request, try again."


# ✅ Function 1: Upload PDF and create/update vector DB
def upload_pdf_and_create_db(pdf_text):
    global vector_storage, last_uploaded_pdf_text
    try:
        # Check if this is a new PDF
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


# ✅ Function 2: Answer user question using existing vector DB
def answer_question(question):
    global vector_storage
    try:
        if not vector_storage:
            logging.warning("Tried answering without uploading PDF.")
            return "No PDF uploaded yet. Please upload a PDF first."
        
        retriever = vector_storage.as_retriever()
        prompt = create_prompt_template()
        bot = RetrieveAndAnswer(retriever, prompt)
        return bot.invoke(question)
    except Exception as e:
        logging.error(f"Error answering question: {e}")
        return "Error while answering the question."


