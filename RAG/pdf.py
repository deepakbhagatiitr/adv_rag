from http.server import BaseHTTPRequestHandler, HTTPServer  # For handling HTTP requests
import os  # For interacting with the operating system
import json  # For handling JSON data
from dotenv import load_dotenv  # For loading environment variables from a .env file
import numpy as np  # NumPy for numerical operations
from langchain_openai.chat_models import ChatOpenAI  # Custom module for AI chat models
from langchain.prompts import PromptTemplate  # Custom module for generating prompts
from langchain_core.output_parsers import StrOutputParser  # Custom module for parsing output
from langchain_community.document_loaders import PyPDFLoader  # Custom module for loading PDF documents
from langchain.text_splitter import RecursiveCharacterTextSplitter  # Custom module for text splitting
from langchain_community.vectorstores import FAISS  # Custom module for vector storage and retrieval
from langchain.schema import ChatMessage, AIMessage  # Custom module for defining message schemas
import logging  # For logging messages

try:
    from openai import RateLimitError  # Import RateLimitError from OpenAI SDK if available
except ImportError:
    from openai.error import RateLimitError  # Import RateLimitError from OpenAI SDK otherwise

# Define constants and configurations
UPLOAD_FOLDER = 'uploads'  # Folder where uploaded files will be saved
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

load_dotenv()  # Load environment variables from .env file if present
API_KEY = os.getenv('OPENAI_API_KEY')  # Retrieve OpenAI API key from environment variables
Model = 'gpt-3.5-turbo'  # Specify the OpenAI model to use

# Initialize chat model, output parser, and vector storage variables
model = ChatOpenAI(api_key=API_KEY, model=Model)
parser = StrOutputParser()
vector_storage = None

# Mock class for generating random embeddings (for demonstration purposes)
class MockEmbeddings:
    def __call__(self, text):
        return np.random.rand(512).tolist()

    def embed_documents(self, texts):
        return [np.random.rand(512).tolist() for _ in texts]

    def embed_query(self, text):
        return np.random.rand(512).tolist()

# Function to load and split PDF documents into pages
def load_and_split_pdf(file_path):
    file_loader = PyPDFLoader(file_path)
    pages = file_loader.load_and_split()
    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
    return splitter.split_documents(pages)

# Function to create vector storage (FAISS index) from document pages
def create_vector_storage(pages):
    mock_embeddings = MockEmbeddings()
    return FAISS.from_documents(pages, mock_embeddings)

# Function to create a prompt template for generating context-based questions
def create_prompt_template():
    question_template = """
    You are a smart bot that answers questions based on the context given to you only.
    You don't make things up.
    Context: {context}
    Question: {question}
    """
    return PromptTemplate.from_template(template=question_template)

# Class for handling document retrieval and answering questions
class RetrieveAndAnswer:
    def __init__(self, retriever, model, prompt_template, parser):
        self.retriever = retriever
        self.model = model
        self.prompt_template = prompt_template
        self.parser = parser

    def invoke(self, question):
        try:
            # Retrieve relevant documents
            docs = self.retriever.invoke(question)
            context = ' '.join([doc.page_content for doc in docs])
            formatted_prompt = self.prompt_template.format(context=context, question=question)
            chat_message = ChatMessage(role="user", content=formatted_prompt)
            response = self.model.invoke([chat_message])

            # Ensure the response is handled correctly
            if isinstance(response, list) and response:
                response_content = response[0].content
            elif isinstance(response, AIMessage):
                response_content = response.content
            else:
                response_content = str(response)

            result = self.parser.parse(response_content)

            # Ensure result is correctly formatted and accessed
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

# HTTP request handler class derived from BaseHTTPRequestHandler
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    # Method to set HTTP response headers
    def _set_headers(self):
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    # Method to set HTTP response with status code and optional message
    def _set_response(self, code=200, message=None):
        self.send_response(code)
        self._set_headers()
        if message:
            self.wfile.write(json.dumps({"message": message}).encode())
        else:
            self.end_headers()

    # Handler for OPTIONS request (preflight request for CORS)
    def do_OPTIONS(self):
        self.send_response(200)
        self._set_headers()

    # Handler for GET request
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self._set_headers()
            with open('index.html', 'rb') as file:
                self.wfile.write(file.read())
        else:
            self._set_response(404, "Not Found")

    # Handler for POST request
    def do_POST(self):
        global vector_storage
        if self.path == '/upload':  # Endpoint for file upload
            try:
                content_type = self.headers['Content-Type']
                if 'multipart/form-data' not in content_type:
                    self._set_response(400, "Content-Type must be multipart/form-data")
                    return

                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)
                boundary = content_type.split('=')[1].encode()
                parts = body.split(b'--' + boundary)

                for part in parts:
                    if part:
                        part = part.strip()
                        if not part:
                            continue

                        headers, content = part.split(b'\r\n\r\n', 1)
                        headers = headers.decode('utf-8')
                        disposition = headers.split('\r\n')[0]

                        if 'filename' in disposition:
                            filename = disposition.split('filename=')[1].strip('"')
                            print(filename)
                            file_path = os.path.join(UPLOAD_FOLDER, filename)

                            with open(file_path, 'wb') as output_file:
                                output_file.write(content.strip())

                            pages = load_and_split_pdf(file_path)
                            vector_storage = create_vector_storage(pages)

                            self._set_response(200, "File uploaded successfully")
                            return

                self._set_response(400, "File part not found in the request")
            except Exception as e:
                logging.error(f"Error handling upload: {e}")
                self._set_response(500, f"Server error: {str(e)}")
        elif self.path == '/':  # Endpoint for handling questions
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)
                question = data.get('question', '')
                print(question)
                if vector_storage:
                    retriever = vector_storage.as_retriever()
                    prompt = create_prompt_template()
                    retrieve_and_answer = RetrieveAndAnswer(retriever, model, prompt, parser)
                    answer = retrieve_and_answer.invoke(question)

                    self._set_response(200)
                    self.wfile.write(json.dumps({"answer": answer}).encode())
                else:
                    self._set_response(400, "No PDF uploaded or processed")
            except Exception as e:
                logging.error(f"Error handling question: {e}")
                self._set_response(500, f"Server error: {str(e)}")

# Function to run the HTTP server
def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    logging.basicConfig(level=logging.INFO)  # Configure logging level
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info(f'Starting httpd server on port {port}...')
    try:
        httpd.serve_forever()  # Start the HTTP server
    except KeyboardInterrupt:
        pass
    httpd.server_close()  # Close the HTTP server
    logging.info('Stopping httpd server...')

# Entry point of the script
if __name__ == "__main__":
    run()  # Start the HTTP server when the script is executed directly
