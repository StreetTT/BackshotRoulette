import React, { useState, useEffect } from 'react';
import { connectToServer, sendMessage, receiveMessage } from './websocketService';

const Landing = () => {
  const [name, setName] = useState('');
  const [receivedMessage, setReceivedMessage] = useState('');

  useEffect(() => {
    connectToServer();

    receiveMessage((message) => {
      setReceivedMessage(message);
    });

    return () => {
      if (socket) {
        socket.end();
      }
    };
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (name) {
      sendMessage(name);
    }
  };

  return (
    <div>
      <h1>Enter your name</h1>
      <form onSubmit={handleSubmit}>
        <input 
          type="text" 
          value={name} 
          onChange={(e) => setName(e.target.value)} 
          placeholder="Your name" 
        />
        <button type="submit">Send</button>
      </form>
      {receivedMessage && (
        <div>
          <h2>Message from server:</h2>
          <p>{receivedMessage}</p>
        </div>
      )}
    </div>
  );
};

export default Landing;
