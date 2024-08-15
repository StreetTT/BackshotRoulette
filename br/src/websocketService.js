import net from 'net';

export let socket;

export const connectToServer = () => {
  const HOST = '192.168.1.176';
  const PORT = 5050;
  socket = new net.Socket();

  socket.connect(PORT, HOST, () => {
    console.log('Connected to server\n[localhost:5050]');
  });

  socket.on('close', () => {
    console.log('Disconnected from server');
  });

  socket.on('error', (error) => {
    console.log('Socket Error:', error);
  });
};

export const sendMessage = (message) => {
  // Format the message with its size prefixed and padded
  const messageSize = message.length.toString().padEnd(1024, ' ');
  socket.write(messageSize);
  socket.write(message);
};

export const receiveMessage = (callback) => {
  let buffer = '';
  let expectedMessageSize = null;

  socket.on('data', (data) => {
    buffer += data.toString();

    if (expectedMessageSize === null && buffer.length >= 1024) {
      // Extract the message size from the first 1024 characters
      expectedMessageSize = parseInt(buffer.slice(0, 1024).trimEnd(), 10);
      buffer = buffer.slice(1024);
    }

    if (expectedMessageSize !== null && buffer.length >= expectedMessageSize) {
      // Extract the actual message based on the expected size
      const message = buffer.slice(0, expectedMessageSize);
      buffer = buffer.slice(expectedMessageSize);
      expectedMessageSize = null;

      callback(message); // Use callback to handle the received message
    }
  });
};
