let socket;

export const connectToServer = () => {
  const SERVER_URL = "ws://localhost:5050"; 

  socket = new WebSocket(SERVER_URL);

  socket.onopen = () => {
    console.log("Connected to server:", url);
  };

  socket.onclose = () => {
    console.log("Disconnected from server");
  };

  socket.onerror = (error) => {
    console.error("Socket Error:", error);
  };
};

export const sendMessage = (message) => {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(message);
  } else {
    console.error("Socket is not connected.");
  }
};

export const receiveMessage = (callback) => {
  if (socket) {
    socket.onmessage = (event) => {
      callback(event.data);
    };
  } else {
    console.error("Socket is not initialized.");
  }
};