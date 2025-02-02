import React, { createContext, useContext, useEffect, useState } from 'react';
import useWebSocket from '../hooks/useWebSocket';


const WebSocketContext = createContext(null);

export const WebSocketProvider = ({ children }) => {
  const { messages, sendMessage } = useWebSocket('ws://localhost:5050');
  const [latestMessage, setLatestMessage] = useState(null);
  const signalsToIgnore = ['ping', 'heartbeat_ack', "", null];

  useEffect(() => {
    if (messages.length > 0 && !signalsToIgnore.includes(messages[messages.length - 1].type)) {
      setLatestMessage(messages[messages.length - 1]);
      console.log("Message:", messages[messages.length - 1]);
    }
  }, [messages]);

  return (
    <WebSocketContext.Provider value={{ latestMessage, sendMessage }}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocketContext = () => useContext(WebSocketContext);