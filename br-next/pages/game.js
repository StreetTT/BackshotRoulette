import GunInfo from "../components/GunInfo";
import PlayerInfo from "../components/PlayerInfo";
import HelpBox from "../components/HelpBox";
import { useGameContext } from '../contexts/GameContext';

const Game = () => {
  const ITEMS = [
    "knife", "glass", "drugs", "cuffs", "voddy", "twist", 
    "spike", "8ball", "pluck", "null"
  ];
  const { player1Info, player2Info, gunInfo, loading } = useGameContext();

  return (
    <main>
      {loading && (
        <div className={`loading-screen ${!loading ? 'fade-out' : ''}`}>
          <div className="loading-text">Loading...</div>
        </div>
      )}
      {player1Info && <PlayerInfo opponent={true} playerInfo={player1Info} />}
      {gunInfo && <GunInfo crit={gunInfo.crit} chamber={gunInfo.chamber} />}
      {<HelpBox />}
      {player2Info && <PlayerInfo opponent={false} playerInfo={player2Info} />}
    </main>
  );
};

export default Game;
