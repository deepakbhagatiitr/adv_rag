import React, { useState, useEffect } from 'react';
import ChatDashboard from './components/ChatDashboard';
import axios from 'axios';

const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  // Check login state on load
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) setIsLoggedIn(true);
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post('https://rag-backend-463375822200.us-central1.run.app/login', { email, password });
      const token = response.data.token;

      if (token) {
        localStorage.setItem('token', token);   // Store token in localStorage
        setIsLoggedIn(true);
      } else {
        alert('Login failed. No token received.');
      }
    } catch (err) {
      alert('Invalid email or password');
    }
  };

  if (isLoggedIn) {
    return <ChatDashboard onLogout={() => {
      localStorage.removeItem('token');
      setIsLoggedIn(false);
    }} />;
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-sm p-8 space-y-6 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-center text-gray-800">Login to MasterBot</h2>
        <form className="space-y-4" onSubmit={handleLogin}>
          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input
              type="email"
              className="w-full px-4 py-2 mt-1 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Password</label>
            <input
              type="password"
              className="w-full px-4 py-2 mt-1 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="********"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700"
          >
            Login
          </button>
        </form>
      </div>
    </div>
  );
};

export default App;
