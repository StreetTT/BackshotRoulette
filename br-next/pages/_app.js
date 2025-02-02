import '../styles/globals.css'; 
import '../styles/App.css';
import { WebSocketProvider } from '../Contexts/WebSocketContext';
import { GameContextProvider } from '../Contexts/GameContext';

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