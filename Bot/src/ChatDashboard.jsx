import React, { useState, useEffect, useRef } from 'react';
import { MdFace } from "react-icons/md";
import { FiSend } from "react-icons/fi";
import ScrollToBottom from 'react-scroll-to-bottom';
import axios from 'axios';
import UploadForm from './components/UploadForm'; // Ensure this component is implemented correctly
import './index.css';

const ChatDashboard = ({ onLogout }) => {
    const [messages, setMessages] = useState([]);
    const [message, setMessage] = useState('');
    const [pdfUploaded, setPdfUploaded] = useState(false);
    const bottomRef = useRef(null);
    const token = localStorage.getItem('token');

    const handleSend = async (e) => {
        e.preventDefault();

        if (!pdfUploaded) {
            alert("Please upload a PDF first.");
            return;
        }

        if (!message.trim()) {
            alert("Please enter a message.");
            return;
        }

        setMessages(prev => [...prev, { text: message, user: true }]);

        try {
            const response = await axios.post(
                'http://localhost:5000/',  // Make sure this is the correct endpoint for sending questions
                { question: message },
                { headers: { Authorization: `Bearer ${token}` } }
            );

            if (response.data.answer) {
                setMessages(prev => [...prev, { text: response.data.answer, user: false }]);
            } else {
                setMessages(prev => [...prev, { text: 'Failed to get answer from the backend.', user: false }]);
            }
        } catch (error) {
            setMessages(prev => [...prev, { text: `Backend error: ${error.message}`, user: false }]);
        }

        setMessage('');
    };

    const handleFileUpload = async (file) => {
        const formData = new FormData();
        formData.append('file', file); // Append the file to FormData

        try {
            const response = await axios.post(
                'http://localhost:5000/upload',
                formData,
                { headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'multipart/form-data' } }
            );

            if (response.status === 200) {
                setMessages(prev => [...prev, { text: 'File uploaded successfully!', user: false }]);
                setPdfUploaded(true);
            } else {
                setMessages(prev => [...prev, { text: 'File upload failed.', user: false }]);
            }
        } catch (error) {
            setMessages(prev => [...prev, { text: 'Error uploading file.', user: false }]);
        }
    };


    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    return (
        <div className="flex justify-center w-full h-screen py-5 bg-gray-50">
            <div className="flex flex-col w-11/12 h-full overflow-hidden bg-white rounded-lg md:w-8/12 lg:w-6/12">
                {/* Header */}
                <header className="flex items-center justify-between p-4 text-black border-b">
                    <div className="text-xl font-semibold">MasterBot</div>
                    <div className="flex items-center gap-4">
                        <MdFace className="text-2xl" />
                        <button
                            onClick={onLogout}
                            className="px-3 py-1 text-sm text-white bg-red-500 rounded-md hover:bg-red-600"
                        >
                            Logout
                        </button>
                    </div>
                </header>

                {/* Chat Messages */}
                <div className="flex-1 p-4 overflow-y-auto">
                    <ScrollToBottom className="flex-1">
                        {messages.map((msg, index) => (
                            <div key={index} className={`mb-4 flex ${msg.user ? 'justify-end' : 'justify-start'}`}>
                                <span className={`inline-block max-w-lg break-words px-4 py-2 rounded-lg ${msg.user ? 'bg-blue-100 text-right' : 'bg-gray-100 text-left'}`}>
                                    {msg.text}
                                </span>
                            </div>
                        ))}
                        <div ref={bottomRef} />
                    </ScrollToBottom>
                </div>

                {/* Input + Upload */}
                <form className="flex p-4 space-x-2 border-t" onSubmit={handleSend}>
                    <input
                        type="text"
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        placeholder="Type a message..."
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg outline-none"
                    />
                    {/* Pass file upload handler to UploadForm */}
                    <UploadForm onFileUpload={handleFileUpload} />
                    <button
                        type="submit"
                        className="flex items-center justify-center px-3 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <FiSend className="text-xl" />
                    </button>
                </form>
            </div>
        </div>
    );
};

export default ChatDashboard;
