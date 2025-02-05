import { createContext, useContext, useState, useEffect } from 'react';
import { useWebSocketContext } from './WebSocketContext';


const GameContext = createContext(null);


export const GameContextProvider = ({ children }) => {
    const { latestMessage, clientID } = useWebSocketContext();
    const [player1Info, setPlayer1Info] = useState(null);
    const [player2Info, setPlayer2Info] = useState(null);
    const [gunInfo, setGunInfo] = useState(null);
    const [loading, setLoading] = useState(true);
    const [currentTurn, setCurrentTurn] = useState(false);
    const [infoBoxItem, setInfoBoxItem] = useState(false);

    const ParseGameInfo = (gameInfo) => {
        setCurrentTurn(gameInfo.currentTurn === clientID);

        const [player1, player2] = gameInfo.players[0].ID === clientID 
            ? [gameInfo.players[1], gameInfo.players[0]] 
            : [gameInfo.players[0], gameInfo.players[1]];

        setPlayer1Info(player1);
        setPlayer2Info(player2);

        setGunInfo(gameInfo.gun);
        setLoading(false);
    };

    useEffect(() => {
        if (latestMessage) {
          if (latestMessage.type === 'gameInfo') {
            ParseGameInfo(latestMessage);
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