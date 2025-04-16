import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv
import requests
from langchain_openai.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import ChatMessage, AIMessage

# Load environment variables
load_dotenv()
API_KEY = os.getenv('OPENAI_API_KEY')

# Verify the API key
if not API_KEY:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY in your .env file.")

Model = 'gpt-3.5-turbo'

# Initialize the model
model = ChatOpenAI(api_key=API_KEY, model=Model)
parser = StrOutputParser()

# Define API call function
def fetch_api_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()  # Fetch and parse JSON data
    except requests.exceptions.RequestException as e:
        print(f"API call error: {e}")
        return None

# Example API URL (replace with actual API URL)
api_url = 'http://localhost:3000/'

# Fetch data from API
api_response = fetch_api_data(api_url)
if api_response:
    def json_to_readable_text(json_obj, level=0):
        """Convert JSON object to a readable string with indentation."""
        indent = '  ' * level
        readable_text = ""
        if isinstance(json_obj, dict):
            for key, value in json_obj.items():
                readable_text += f"{indent}{key}:"
                if isinstance(value, (dict, list)):
                    readable_text += f"\n{json_to_readable_text(value, level + 1)}"
                else:
                    readable_text += f" {value}\n"
        elif isinstance(json_obj, list):
            for item in json_obj:
                readable_text += f"\n{json_to_readable_text(item, level + 1)}"
        else:
            readable_text += f"{indent}{json_obj}\n"
        return readable_text

    readable_texts = [json_to_readable_text(record) for record in api_response]

    page_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    pages = page_splitter.create_documents(readable_texts)

    if len(pages) == 0:
        raise ValueError("No pages found in the API response. Please check the API content and URL.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=500)
    chunks = []
    for page in pages:
        chunks.extend(splitter.create_documents([page.page_content]))

    from langchain_openai.embeddings import OpenAIEmbeddings
    openai_embeddings = OpenAIEmbeddings(api_key=API_KEY)

    try:
        vector_storage = FAISS.from_documents(chunks, openai_embeddings)
        retriever = vector_storage.as_retriever()
    except Exception as e:
        print(f"Error creating vector storage: {e}")
else:
    raise ValueError("Failed to fetch data from the API.")

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
            response = self.model.invoke(input=[chat_message])

            # Handle the response correctly
            if isinstance(response, AIMessage):
                ai_message_content = response.content
            else:
                ai_message_content = str(response)

            result = self.parser.parse(ai_message_content)
            return result
        except Exception as e:
            print(f"Error invoking model: {e}")
            return None

prompt_template = """
You are a smart bot that answers questions based on the context given to you only.
You don't make things up.
Context:{context}
Question:{question}
"""

prompt = PromptTemplate.from_template(template=prompt_template)
retrieve_and_answer = RetrieveAndAnswer(retriever, model, prompt, parser)

class RequestHandler(BaseHTTPRequestHandler):
    def _set_response(self, response_body, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(response_body).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request_body = json.loads(post_data.decode('utf-8'))
        question = request_body.get('question')

        if not question:
            self._set_response({'error': 'Question not provided'}, status_code=400)
            return

        result = retrieve_and_answer.invoke(question)
        if result:
            self._set_response({'answer': result})
        else:
            self._set_response({'error': 'Failed to get answer'}, status_code=500)

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
