import { createContext, useContext, useState, useEffect } from 'react';
import { useWebSocketContext } from './WebSocketContext';


const GameContext = createContext(null);


export const GameContextProvider = ({ children }) => {
    const { latestMessage } = useWebSocketContext();
    const [player1Info, setPlayer1Info] = useState(null);
    const [player2Info, setPlayer2Info] = useState(null);
    const [gunInfo, setGunInfo] = useState(null);
    const [loading, setLoading] = useState(true);
    const [currentTurn, setCurrentTurn] = useState(false);
    const [infoBoxItem, setInfoBoxItem] = useState(false);

    useEffect(() => {
        if (latestMessage) {
          if (latestMessage.type === 'startInfo') {
            setPlayer1Info(latestMessage.players[0]);
            setPlayer2Info(latestMessage.players[1]);
            setGunInfo(latestMessage.gun);
            setLoading(false); 
          } else if (latestMessage.type === 'currentTurn') {
            setCurrentTurn(latestMessage.currentTurn)
          }
        }
      }, [latestMessage]);

      
return (
    <GameContext.Provider value={{ player1Info, player2Info, gunInfo, loading, currentTurn, infoBoxItem, setInfoBoxItem }}>
        {children}
    </GameContext.Provider>
    );
};

export const useGameContext = () => useContext(GameContext);