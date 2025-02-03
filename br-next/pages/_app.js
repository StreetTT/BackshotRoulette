import '../styles/globals.css'; 
import '../styles/App.css';
import { WebSocketProvider } from '../contexts/WebSocketContext';
import { GameContextProvider } from '../contexts/GameContext';

function MyApp({ Component, pageProps }) {
  return (
    <WebSocketProvider>
      <GameContextProvider>
        <Component {...pageProps} />
      </GameContextProvider>
    </WebSocketProvider>
  );
}

export default MyApp;