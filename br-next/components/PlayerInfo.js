import { useGameContext } from '../Contexts/GameContext';
import { toTitleCase } from "../hooks/useTitleCase";



const PlayerInfo = ({ opponent, playerInfo: { health, cuffed, gallery } }) => {
  const personText = opponent ? "Opps" : "Self"
  const floatDir = opponent ? "left" : "right"
  const { currentTurn, setInfoBoxItem } = useGameContext();


  return (
    <div className={`player-info ${opponent ? "top" : "bottom"}`}>
      {!opponent && (
        <div className="player-status">
         <div className="trigger" style={{float: floatDir}}>
            <button onClick={() => {
              if (currentTurn){
                console.log(personText + " Shot")
              }
            }}> Shoot {personText}</button>
          </div>
          {currentTurn && <div className="turn" style={{float: floatDir}}>Your Turn</div> }
          <div className="cuffs" style={{float: floatDir}}>{cuffed ? "🔒" : " "}</div>
          <div className="hearts" style={{float: floatDir}}>{"❤️".repeat(health)}</div>
        </div>
      )}

      <div className="gallery">
        {gallery.map((item, idx) => (
          <div
            key={idx}
            className={`item ${item === "8ball" ? "ball" : item}`}
            onClick={() => {
              if (!currentTurn){
                return
              }
              console.log(`${opponent ? "Opponent's" : "Player's"} item ${idx}: ${item}`);
              // if (opponent && item !== "null") {
              //   setInfoBoxItem(item);
              // }
              // IDK if I like this functionality
            }}
            onContextMenu={(e) => {
              e.preventDefault();
              if (item !== "null") setInfoBoxItem(item);
            }}
          >
            <p>{item === "null" ? "" : toTitleCase(item)}</p>
          </div>
        ))}
      </div>

      {opponent && (
        <div className="player-status">
         <div className="trigger" style={{float: floatDir}}>
            <button onClick={() => {
              if (!currentTurn){
                console.log(personText + " Shot")
              }
            }}> Shoot {personText}</button>
          </div>
          <div className="hearts" style={{float: floatDir}}>{"❤️".repeat(health)}</div>
          <div className="cuffs" style={{float: floatDir}}>{cuffed ? "🔒" : " "}</div>
          {!currentTurn && <div className="turn" style={{float: floatDir}}>Their Turn</div> }
        </div>
      )}
    </div>

    
  );
};

export default PlayerInfo;
