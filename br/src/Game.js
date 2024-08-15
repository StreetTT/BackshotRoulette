import GunInfo from "./GunInfo";
import PlayerInfo from "./PlayerInfo";

const Game = () => {
  const ITEMS = ["knife", "glass", "drugs", "cuffs", "voddy", "twist", "spike", "8ball", "pluck", "null"]

  const genPlayerInfo = () => (
    {
      "health" : Math.floor(Math.random() * 4) + 1,
      "cuffed" : Math.random() < 0.5,
      "gallery": Array.from({ length: 8 }, () => ITEMS[Math.floor(Math.random() * ITEMS.length)])
    }
  )
  
  function genChamber() {
    const boolList = [true, false, ...Array.from({ length: Math.floor(Math.random() * 7) }, () => Math.random() < 0.5)];
      for (let i = boolList.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [boolList[i], boolList[j]] = [boolList[j], boolList[i]];
      }
      return boolList
  }

  return ( 
        <main>
            <PlayerInfo opponent={true}  playerInfo={genPlayerInfo()} />
            <GunInfo crit={Math.random() < 0.5} chamber={genChamber()} />
            <PlayerInfo opponent={false} playerInfo={genPlayerInfo()} />
        </main>
     ); 
}
 
export default Game;