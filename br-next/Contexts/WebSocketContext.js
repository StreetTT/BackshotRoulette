import { createContext, useContext, useEffect, useState, useRef } from 'react';

const WebSocketContext = createContext(null);

export const WebSocketProvider = ({ children }) => {
    const ws = useRef(null);
	const [isConnected, setIsConnected] = useState(false);
	const [messages, setMessages] = useState([]); // Store received messages
	const [retryInterval, setRetryInterval] = useState(500); // Start with 1s retry
	const clientID = useRef(`client-${Math.random().toString(36).substr(2, 9)}`);

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
            setRetryInterval(1000); // Reset retry interval on success

            // Send an identification message to the server
            ws.current.send(JSON.stringify({
                type: "ReconnectAttempt",
                clientID: clientID.current
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
                setRetryInterval(newRetryInterval); // Max out at 30s
                initializeWebSocket();
            }, retryInterval);
        };
    };

	const sendMessage = (message) => {
        if (isConnected) {
            ws.current.send(JSON.stringify(message));
        } else {
            console.warn("WebSocket is not open. Message not sent.");
        }
    };

    useEffect(() => {
        initializeWebSocket();
        return () => ws.current?.close();
    }, []);

    return (
        <WebSocketContext.Provider value={{ ws: ws.current, messages, sendMessage }}>
            {children}
        </WebSocketContext.Provider>
    );
};

export const useWebSocketContext = () => useContext(WebSocketContext);