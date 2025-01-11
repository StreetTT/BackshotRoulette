import { useState, useEffect } from 'react';
import GunInfo from "../components/GunInfo";
import PlayerInfo from "../components/PlayerInfo";
import useWebSocket from "../hooks/useWebSocket";

const Game = () => {
  const ITEMS = [
    "knife", "glass", "drugs", "cuffs", "voddy", "twist", 
    "spike", "8ball", "pluck", "null"
  ];
  const { messages, sendMessage } = useWebSocket('ws://localhost:5050');
  const [player1Info, setPlayer1Info] = useState(null);
  const [player2Info, setPlayer2Info] = useState(null);
  const [gunInfo, setGunInfo] = useState(null);

  const signalsToIgnore = ['heartbeat', 'ping', 'heartbeat_ack', null];

  useEffect(() => {
    console.log(messages)
    if (messages.length > 0) {
      let latestMessage = null;

      // Skip over ignored signals
      for (let i = messages.length - 1; i >= 0; i--) {
        if (messages[i] && !signalsToIgnore.includes(messages[i].type)) {
          latestMessage = messages[i];
          break;
        }
      }

      if (latestMessage && latestMessage.type === 'startInfo') {
        setPlayer1Info(latestMessage.players[0]);
        setPlayer2Info(latestMessage.players[1]);
        setGunInfo(latestMessage.gun);
      }
    }
  }, [messages]);


  return (
    <main>
      {player1Info && <PlayerInfo opponent={true} playerInfo={player1Info} />}
      {gunInfo && <GunInfo crit={gunInfo.crit} chamber={gunInfo.chamber} />}
      {player2Info && <PlayerInfo opponent={false} playerInfo={player2Info} />}
    </main>
  );
};

export default Game;
