import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { connectToServer, sendMessage, receiveMessage } from '../lib/websocketService';

const Landing = () => {
  const [name, setName] = useState('');
  const [receivedMessage, setReceivedMessage] = useState('');
  const router = useRouter();


  // useEffect(() => {
  //   // Establish WebSocket connection
  //   connectToServer();

  //   // Handle incoming messages
  //   const unsubscribe = receiveMessage((message) => {
  //     setReceivedMessage(message);
  //   });

  //   // Cleanup WebSocket on unmount
  //   return () => {
  //     unsubscribe();
  //   };
  // }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (name) {
      console.log(name);
      router.push('/game');
    }
  };

  return (
    <div className='welcomeContainer'>
      <div className='welcome'>
        <h1>Name: </h1>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Your name"
          />
          <button type="submit">Enter</button>
        </form>
        {/* {receivedMessage && (
          <div>
            <h2>Message from server:</h2>
            <p>{receivedMessage}</p>
          </div>
        )} */}
      </div>
    </div>
  );
};

export default Landing;
