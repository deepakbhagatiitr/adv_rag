# **Adv_Rag**

Adv_Rag is an advanced document processing and question-answering system built with various cutting-edge technologies, enabling users to upload PDF or image documents, process them, and ask questions based on the extracted content. The system uses a custom AI-powered backend, powered by Google's Gemini API, and integrates with popular Python libraries and cloud services.

## **Features**
- **PDF and Image Upload**: Upload PDF or image files for text extraction using the Vision API and pdfplumber.
- **Question Answering**: Use an advanced AI model (Gemini 2.0 Flash) to answer questions based on the content of the uploaded documents.
- **JWT Authentication**: Secure the backend routes with JWT tokens, ensuring only authenticated users can access the system.
- **Vector Storage**: Vectorize document text using FAISS for efficient search and retrieval of relevant document chunks.
- **Smart Confidence Scoring**: Provide confidence scores along with the answers to indicate the model's certainty.

## **Technologies Used**
- **Backend**: Python, Flask
- **Frontend**: ReactJS, Tailwind CSS (via npm run dev)
- **Text Extraction**: `pdfplumber` for PDF text extraction, Google Cloud Vision API for image-to-text extraction.
- **Vector Database**: FAISS for efficient document search and retrieval.
- **AI Model**: Google Gemini 2.0 Flash for natural language processing and question answering.
- **Authentication**: JWT-based token system for user authentication.

## **Installation Guide**

### **Prerequisites**
- **Python** 3.10 or +
- **Node.js** and **npm** for running the frontend
- **Google Cloud Account** for API keys and credentials
- **Gemini API Key** for integrating the AI model

### **Setup**

#### 1. Clone the repository:
```bash
git clone https://github.com/yourusername/Adv_Rag.git
cd RAG
```

#### 2. Install the backend dependencies:
```bash
pip install -r requirements.txt
```

#### 3. Setup your environment variables:
Create a `.env` file in the root of the project and add the following:
```bash
GEMINI_API_KEY=your_api_key_here
```

#### 4. Set up the Google Cloud Vision credentials:
- Download the service account credentials from your Google Cloud console.
- Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to the path of your credentials file:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path_to_your_credentials.json"
```

#### 5. Install the frontend dependencies:
```bash
cd Bot
npm install
```

#### 6. Run the backend server:
In the backend directory, run:
```bash
python server.py
```

#### 7. Run the frontend:
In the frontend directory, run:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000` by default, and the backend will be accessible at `http://localhost:5000`.

## **API Endpoints**

### **1. /login [POST]**
**Description**: Authenticate a user and return a JWT token.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "deepak"
}
```

**Response**:
```json
{
  "token": "your_jwt_token_here"
}
```

### **2. /upload [POST]**
**Description**: Upload a PDF or image file for text extraction and processing.

**Request** (Form Data):
- **file**: The PDF or image file to be uploaded.

**Response**:
```json
{
  "message": "PDF processed and vector DB updated.",
  "success": true
}
```

### **3. / [POST]**
**Description**: Ask a question based on the uploaded document.

**Request**:
```json
{
  "question": "What is the main idea of the document?"
}
```

**Response**:
```json
{
  "answer": "The main idea of the document is...",
  "confidence": 80
}
```

## **How It Works**
1. **Upload PDF/Image**: Users can upload PDF or image files, and the system will extract text from them using either `pdfplumber` (for PDFs) or Google Vision API (for images).
   
2. **Text Vectorization**: The extracted text is split into chunks and vectorized using FAISS for efficient retrieval.

3. **Question Answering**: After processing, users can ask questions, and the system will generate relevant answers based on the extracted text using Google’s Gemini 2.0 Flash model.

4. **Confidence Scoring**: The system returns answers with a confidence score, helping users gauge the reliability of the response.

## **Additional Notes**
- **Google Cloud Vision API**: This is required for image-to-text extraction. Be sure to configure your Google Cloud credentials correctly.
- **JWT Authentication**: Secure your system with JWT tokens to ensure only authorized users can access protected routes.
- **Error Handling**: The system includes comprehensive error handling to ensure robustness, with clear messages in case of failures.

## **Contributing**
If you'd like to contribute, please fork the repository, make your changes, and submit a pull request. Ensure to follow the existing code style and provide detailed commit messages.

## **License**
This project is licensed under the MIT License - see the LICENSE file for details.