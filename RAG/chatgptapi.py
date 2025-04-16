from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import json
from dotenv import load_dotenv
import requests
import numpy as np
from langchain_openai.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.schema import ChatMessage, AIMessage
import logging
from openai import OpenAI, RateLimitError

# Load environment variables from .env file if present
load_dotenv()

API_KEY = os.getenv('OPENAI_API_KEY')
MODEL_NAME = 'gpt-3.5-turbo'
TEXT_API_URL = 'http://localhost:3000/'

def initialize_openai_client(api_key):
    return OpenAI(api_key=api_key)

def initialize_vector_store(client):
    return client.beta.vector_stores.create(name="Asssessment Creator From JSON")

def create_assistant(client):
    assistant = client.beta.assistants.create(
    name="Asssessment Creator and Analyst Assistant",
    instructions="You are an assessment expert. Use your knowledge base to create and analyze assessments.You can create similar and some better assessments.",
    model="gpt-4o",
    tools=[{"type": "file_search"}],
    )
    return assistant




# Initialize OpenAI client and other configurations
client = initialize_openai_client(API_KEY)
vector_store = initialize_vector_store(client)
assistant = create_assistant(client)
model = ChatOpenAI(api_key=API_KEY, model=MODEL_NAME)
parser = StrOutputParser()
vector_storage = None

class MockEmbeddings:
    """Mock class for generating random embeddings (for demonstration purposes)."""
    def __call__(self, text):
        return np.random.rand(512).tolist()

    def embed_documents(self, texts):
        return [np.random.rand(512).tolist() for _ in texts]

    def embed_query(self, text):
        return np.random.rand(512).tolist()

class Document:
    """Class to represent a document with page content and metadata."""
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}

def fetch_text_from_api(api_url):
    """Fetch text from the given API."""
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching text from API: {e}")
        return ""

def load_and_split_text(text):
    """Load and split text into chunks."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
    chunks = splitter.split_text(text)
    return [Document(page_content=chunk) for chunk in chunks]

def create_vector_storage(pages):
    """Create vector storage (FAISS index) from document pages."""
    mock_embeddings = MockEmbeddings()
    return FAISS.from_documents(pages, mock_embeddings)

def create_prompt_template():
    """Create a prompt template for generating context-based questions."""
    question_template = """
    You are a smart bot that answers questions based on the context given to you only.
    You don't make things up.
    Context: {context}
    Question: {question}
    """
    return PromptTemplate.from_template(template=question_template)

class RetrieveAndAnswer:
    """Class for handling document retrieval and answering questions."""
    def __init__(self, retriever, model, prompt_template, parser):
        self.retriever = retriever
        self.model = model
        self.prompt_template = prompt_template
        self.parser = parser

    def invoke(self, question):
        try:
            docs = self.retriever.get_relevant_documents(question)
            context = ' '.join([doc.page_content for doc in docs])
            formatted_prompt = self.prompt_template.format(context=context, question=question)
            chat_message = ChatMessage(role="user", content=formatted_prompt)
            response = self.model.invoke([chat_message])

            if isinstance(response, list) and response:
                response_content = response[0].content
            elif isinstance(response, AIMessage):
                response_content = response.content
            else:
                response_content = str(response)

            result = self.parser.parse(response_content)

            if isinstance(result, dict) and 'content' in result:
                return result['content']
            else:
                return response_content
        except RateLimitError as e:
            logging.error(f"API quota exceeded: {e}")
            return "API quota exceeded, please try again later."
        except Exception as e:
            logging.error(f"Error invoking model: {e}")
            return "Error processing the request, please try again later."

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler class derived from BaseHTTPRequestHandler."""
    def _set_headers(self):
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _set_response(self, code=200, message=None):
        self.send_response(code)
        self._set_headers()
        if message:
            self.wfile.write(json.dumps({"message": message}).encode())
        else:
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_headers()

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self._set_headers()
            with open('index.html', 'rb') as file:
                self.wfile.write(file.read())
        else:
            self._set_response(404, "Not Found")

    def do_POST(self):
        global vector_storage
        if self.path == '/performance_bot':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)
                question = data.get('question', '')
                text_api_url = data.get('json_data', '')

                if not vector_storage:
                    text = text_api_url#fetch_text_from_api(text_api_url)
                    # text = fetch_text_from_api(TEXT_API_URL)
                    if text:
                        pages = load_and_split_text(text)
                        vector_storage = create_vector_storage(pages)
                    else:
                        self._set_response(500, "Failed to fetch text from API")
                        return

                retriever = vector_storage.as_retriever()
                prompt = create_prompt_template()
                retrieve_and_answer = RetrieveAndAnswer(retriever, model, prompt, parser)
                answer = retrieve_and_answer.invoke(question)

                self._set_response(200)
                self.wfile.write(json.dumps({"answer": answer}).encode())
            except Exception as e:
                logging.error(f"Error handling question: {e}")
                self._set_response(500, f"Server error: {str(e)}")

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=3000):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info(f'Starting httpd server on port {port}...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd server...')

if __name__ == "__main__":
    run()
