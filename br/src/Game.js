import GunInfo from "./GunInfo";
import PlayerInfo from "./PlayerInfo";

const Game = () => {
  const ITEMS = ["knife", "glass", "drugs", "cuffs", "voddy", "twist", "spike", "8ball", "pluck", "null"]

  const genPlayerInfo = () => {
    const output = {
      "health" : Math.floor(Math.random() * 4) + 1,
      "cuffed" : Math.random() < 0.5,
      "gallery": Array.from({ length: 8 }, () => ITEMS[Math.floor(Math.random() * ITEMS.length)])
    }
    return output
  }

    return ( 
        <main>
            <PlayerInfo opponent={true}  playerInfo={genPlayerInfo()} />
            <PlayerInfo opponent={false} playerInfo={genPlayerInfo()} />
        </main>
     ); 
}
 
export default Game;