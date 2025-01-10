import { useState, useEffect } from 'react';
import { connectToServer, sendMessage, receiveMessage } from '../lib/websocketService';

const Landing = () => {
  const [name, setName] = useState('');
  const [receivedMessage, setReceivedMessage] = useState('');

  useEffect(() => {
    // Establish WebSocket connection
    connectToServer();

    // Handle incoming messages
    const unsubscribe = receiveMessage((message) => {
      setReceivedMessage(message);
    });

    // Cleanup WebSocket on unmount
    return () => {
      unsubscribe();
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
