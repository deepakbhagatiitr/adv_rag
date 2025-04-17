Thanks for sharing the repo link and clarifying the project structure. Based on this, here's an updated version of the `README.md`, taking into account the actual folder structure and your provided information:

---

# **RAGGaze - Intelligent Question Answering System**

RAGGaze is an AI-powered web application that enables users to upload PDF documents and ask questions about the content. It extracts text from the PDF documents using the Google Cloud Vision API, and answers queries using machine learning models.

## **Table of Contents**

1. [Project Overview](#project-overview)
2. [Technologies](#technologies)
3. [Frontend Setup (React)](#frontend-setup-react)
4. [Backend Setup (Flask)](#backend-setup-flask)
5. [Running the Application](#running-the-application)
6. [Docker Setup](#docker-setup)
7. [Environment Variables](#environment-variables)
8. [Dependencies](#dependencies)
9. [Troubleshooting](#troubleshooting)
10. [License](#license)

---

## **Project Overview**

RAGGaze is a full-stack web application where users can upload a PDF document, and then ask questions about its contents. The system uses Flask as the backend, React.js for the frontend, and integrates Google Cloud Vision API for extracting text from the PDFs. The intelligent question-answering model processes the query and returns relevant answers.

### **Project Structure**
```
.
├── RAG/                    # Backend - RAG (Flask)
│   ├── app.py              # Main Flask app file
│   ├── requirements.txt    # Python dependencies
│   └── server.py           # Flask server for handling API requests
│
└── bot/                    # Frontend - React
    ├── public/             # Static assets
    ├── src/                # React components and pages
    ├── package.json        # Frontend dependencies
    └── .env                # Environment variables for frontend
```

---

## **Technologies**

- **Frontend (React & Tailwind CSS)**:
  - **React.js** for building the user interface.
  - **Tailwind CSS** for utility-first CSS styling.
  - **Axios** for making HTTP requests to the backend.

- **Backend (Flask)**:
  - **Flask** for handling HTTP requests and serving APIs.
  - **Google Cloud Vision API** for text extraction from PDF files.
  - **TensorFlow** for question-answering machine learning models.

- **Docker**:
  - Docker for containerizing the application for easy deployment.

---

## **Frontend Setup (React)**

### 1. **Clone the Repository**
   Clone the repository to your local machine:
   ```bash
   git clone https://github.com/deepakbhagatiitr/adv_rag.git
   cd adv_rag
   ```

### 2. **Install Dependencies**
   Navigate to the `bot` directory and install the required packages:
   ```bash
   cd bot
   npm install
   ```

### 3. **Run the React Development Server**
   Start the React development server:
   ```bash
   npm start
   ```
   The frontend will be available at [http://localhost:3000](http://localhost:3000).

### 4. **Configure Axios**
   Make sure Axios is configured to communicate with your backend by setting the base URL:
   ```js
   axios.defaults.baseURL = "http://localhost:5000";  // Set to Flask backend URL
   ```

---

## **Backend Setup (Flask)**

### 1. **Create a Virtual Environment**
   Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

### 2. **Install Dependencies**
   Navigate to the `RAG` directory and install the Python dependencies:
   ```bash
   cd RAG
   pip install -r requirements.txt
   ```

### 3. **Set Up Google Cloud Credentials**
   Make sure you have the Google Cloud Vision API credentials. Download the credentials JSON file and set the environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials-file.json"
   ```

### 4. **Run the Flask Server**
   Start the Flask server:
   ```bash
   python server.py
   ```
   The backend will be available at [http://localhost:5000](http://localhost:5000).

---

## **Running the Application Locally**

To run the full application locally:

1. **Start the Backend (Flask)**:
   Navigate to the `RAG` directory and run the Flask server:
   ```bash
   python server.py
   ```

2. **Start the Frontend (React)**:
   Navigate to the `bot` directory and run the React app:
   ```bash
   npm start
   ```

This will make the backend available at [http://localhost:5000](http://localhost:5000) and the frontend at [http://localhost:3000](http://localhost:3000).

---

## **Docker Setup**

To deploy the application using Docker, follow these steps:

### 1. **Build Docker Images**

- **Backend (Flask)**:
   In the root project directory, build the Docker image for the backend:
   ```bash
   docker build -t python-server ./RAG
   ```

- **Frontend (React)**:
   Build the Docker image for the frontend:
   ```bash
   cd bot
   docker build -t react-frontend .
   ```

### 2. **Run Backend with Docker**

Mount the Google Cloud Vision credentials file and set the environment variable in Docker:

```bash
docker run -p 5000:5000 \
  -v /path/to/your/credentials/iprc-456620-6454ff816526.json:/app/credentials/iprc-456620-6454ff816526.json \
  -e GOOGLE_APPLICATION_CREDENTIALS="/app/credentials/iprc-456620-6454ff816526.json" \
  python-server
```

### 3. **Run Frontend with Docker (Optional)**

If you choose to containerize the frontend, run it in a similar manner:
```bash
docker run -p 3000:3000 react-frontend
```

---

## **Environment Variables**

Make sure to set up the following environment variables:

- **`GOOGLE_APPLICATION_CREDENTIALS`**: Path to your Google Cloud credentials JSON file.

In the backend, you can specify this environment variable directly, as shown in the Docker setup:
```bash
-e GOOGLE_APPLICATION_CREDENTIALS="/app/credentials/iprc-456620-6454ff816526.json"
```

---

## **Dependencies**

### Backend (Flask)

- **Flask**: A micro web framework for Python.
- **google-cloud-vision**: Google Cloud Vision API client.
- **pdfplumber**: Extracts content from PDF documents.
- **FAISS**: Library for efficient similarity search.
- **TensorFlow**: Deep learning framework for question-answering models.

### Frontend (React)

- **React**: JavaScript library for building user interfaces.
- **Tailwind CSS**: A utility-first CSS framework for styling.
- **Axios**: HTTP client for making API requests.

To install the dependencies, run the following:

```bash
pip install -r requirements.txt  # Backend
npm install                     # Frontend
```

---

## **Troubleshooting**

1. **CORS Issue (Cross-Origin Resource Sharing)**:
   To fix CORS issues between React and Flask, make sure `flask-cors` is installed and configured in the backend:
   ```bash
   pip install flask-cors
   ```

   In `server.py`, enable CORS for all routes:
   ```python
   from flask_cors import CORS
   CORS(app)
   ```

2. **Google Cloud Vision API Credentials Not Found**:
   Ensure that the `GOOGLE_APPLICATION_CREDENTIALS` variable points to the correct path of your Google Cloud credentials JSON file.

3. **Connection Reset (ERR_CONNECTION_RESET)**:
   If the frontend works locally but not inside Docker, ensure the Flask server is bound to `0.0.0.0` (not just `localhost`):
   ```python
   app.run(host='0.0.0.0', port=5000)
   ```

4. **Missing Modules**:
   If you see errors related to missing modules, make sure to run:
   ```bash
   pip install -r requirements.txt  # For backend
   npm install                     # For frontend
   ```

---

## **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

This README should provide a clear and detailed guide for setting up and running your project. Let me know if you need any additional changes or clarifications!