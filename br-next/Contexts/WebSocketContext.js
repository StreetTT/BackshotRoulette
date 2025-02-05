import { createContext, useContext, useEffect, useState, useRef } from 'react';

const WebSocketContext = createContext(null);

export const WebSocketProvider = ({ children }) => {
    const ws = useRef(null);
	const [isConnected, setIsConnected] = useState(false);
	const [messages, setMessages] = useState([]);
	const [retryInterval, setRetryInterval] = useState(500);
    const [clientID, setClientID] = useState(null);

	const initializeWebSocket = () => {
        if(isConnected || (ws.current && ws.current.readyState === WebSocket.OPEN)) {
            console.log("WebSocket already connected.");
			setIsConnected(true);
            return;
        }

        ws.current = new WebSocket("ws://localhost:5050");

        ws.current.onopen = () => {
            console.log("WebSocket connection opened.");
            setIsConnected(true);
            setRetryInterval(500);

            // Retrieve or generate a client ID
            let storedClientID = localStorage.getItem('clientID');
            if (!storedClientID) {
                storedClientID = `client-${Math.random().toString(36).substr(2, 9)}`;
                localStorage.setItem('clientID', storedClientID);
            }
            setClientID(storedClientID);

            // Send an identification message to the server
            ws.current.send(JSON.stringify({
                type: "ReconnectAttempt",
                clientID: storedClientID
            }));
        };

        ws.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log("Message from server:", data);

            // Add new message to the array
            setMessages((prevMessages) => [...prevMessages, data]);
        };

        ws.current.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        ws.current.onclose = (event) => {
            console.warn(`WebSocket closed: Code ${event.code}, Reason: ${event.reason}`);
            setIsConnected(false);

            // Reconnect with exponential backoff
            setTimeout(() => {
                const newRetryInterval = Math.min(retryInterval * 2, 30000); // Max out at 30s
                console.log(`Reconnecting in ${newRetryInterval / 1000} seconds...`);
                setRetryInterval(newRetryInterval);
                initializeWebSocket();
            }, retryInterval);
        };
    };

	const sendMessage = (message) => {
        if (isConnected) {
            const messageWithClientID = { ...message, clientID: clientID };
            ws.current.send(JSON.stringify(messageWithClientID));
        } else {
            console.warn("WebSocket is not open. Message not sent.");
        }
    };

    useEffect(() => {
        initializeWebSocket();
        return () => ws.current?.close();
    }, []);

    return (
        <WebSocketContext.Provider value={{ clientID, messages, sendMessage, latestMessage: messages[messages.length - 1] }}>
            {children}
        </WebSocketContext.Provider>
    );
};

export const useWebSocketContext = () => useContext(WebSocketContext);