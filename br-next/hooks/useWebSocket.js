import { useState, useEffect, useRef } from 'react';

const useWebSocket = (url) => {
  const socketRef = useRef(null);
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const connect = () => {
      // Establish WebSocket connection
      socketRef.current = new WebSocket(url);

      socketRef.current.onopen = () => {
        console.log('WebSocket connection established');
        setIsConnected(true);
      };

      socketRef.current.onmessage = (event) => {
        const message = JSON.parse(event.data);
        setMessages((prevMessages) => [...prevMessages, message]);
      };

      socketRef.current.onclose = (event) => {
        console.log('WebSocket connection closed', event);
        setIsConnected(false);
        // Attempt to reconnect after a delay
        setTimeout(connect, 1000);
      };

      socketRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      // Heartbeat mechanism to keep the connection alive
      const interval = setInterval(() => {
        if (socketRef.current.readyState === WebSocket.OPEN) {
          socketRef.current.send(JSON.stringify({ type: 'heartbeat' }));
        }
      }, 30000); // Send a heartbeat every 30 seconds

      return () => {
        clearInterval(interval);
        if (socketRef.current) {
          socketRef.current.close();
        }
      };
    };

    connect();

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [url]);

  const sendMessage = (message) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(message));
    }
  };

  return { messages, sendMessage, isConnected };
};

export default useWebSocket;