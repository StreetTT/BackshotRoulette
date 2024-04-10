import { useState } from 'react';

const PlayerInfo = ({opponent, playerInfo: {health, cuffed, gallery}}) => {
    const toTitleCase = (str) => {
        return str.toLowerCase().split(' ').map(function(word) {
            return word.charAt(0).toUpperCase() + word.slice(1);
        }).join(' ');
    }
    const personText = opponent ? "Opps" : "Self"
    const items = {
        "knife": "The Gun will become 'Crit' and deal double damage for the next shot",
        "glass": "The user will see what type of round the next shot is ",
        "drugs": "The user will gain one heart",
        "cuffs": "The opposing player will skip their next turn",
        "voddy": "The user will eject the current shell without firing it",
        "twist": "The polarity of the next shot will be flipped; a dead shell becomes live, and a live shell becomes dead",
        "spike": "The user has a 50% chance of regaining two hearts and a 50% chance of losing one",
        "8ball": "The user will be told the location and type of a random bullet in the gun",
        "pluck": "The user will be able to steal one item from the opposing player's side and use it immediately"
      };
    const [showInfoBox, setShowInfoBox] = useState(false);
    const [infoBoxTitle, setInfoBoxTitle] = useState('');
    const [infoBoxContent, setInfoBoxContent] = useState('');

    const itemInfoBox = (item) => {
        setShowInfoBox(true);
        setInfoBoxTitle(item);
        setInfoBoxContent(items[item]);
        
        setTimeout(() => {
            setShowInfoBox(false);
            setInfoBoxContent('');
            setInfoBoxTitle('');
        }, 4000);
    };

    return ( 
        <div className={`player-info ${opponent ? "top" : "bottom"}`}>
            {!opponent && (<div className="player-status">
                <div className="trigger" style={{float: opponent ? "left" : "right"}}>
                    <button onClick={() => console.log(personText + " Shot")}> Shoot {personText}</button>
                </div>

                <div className="cuffs" style={{float: opponent ? "left" : "right"}}>{cuffed ? "🔒" : " "}</div>
                <div className="hearts" style={{float: opponent ? "left" : "right"}}>{(() => {
                    let message = "";
                    for (let index = 0; index < health; index++) {
                        message += "❤️";
                    }
                    return message;
                })()}</div>
            </div>)}

            <div className="gallery">
                {gallery.map((item) => <div 
                    className={`item ${item === "8ball" ? "ball" : item }`}
                    onContextMenu={(e) => { 
                        e.preventDefault();
                        if (item != "null"){
                            itemInfoBox(item)
                        }  
                    }} 
                    onClick={(e) => { 
                        e.preventDefault();
                        if (item != "null" ){
                            if (opponent){
                                itemInfoBox(item)
                            } else {
                                console.log(item)
                            }
                        }  
                    }}
                    style={{cursor : opponent ? "" : "pointer"}}>
                        <p>{item === "null" ? "" : toTitleCase(item)}</p>
                </div>)}
            </div>

            {showInfoBox && (
                <div className="info-box">
                    <h4>{toTitleCase(infoBoxTitle)}</h4>
                    <p>{infoBoxContent}</p>
                </div>
            )}

            {opponent && (<div className="player-status">
                <div className="trigger" style={{float: opponent ? "left" : "right"}}>
                    <button onClick={() => console.log(personText + " Shot")}> Shoot {personText}</button>
                </div>

                <div className="hearts" style={{ float: opponent ? "left" : "right"}}>{(() => {
                    let message = "";
                    for (let index = 0; index < health; index++) {
                        message += "❤️";
                    }
                    return message;
                })()}</div>
                <div className="cuffs" style={{ float: opponent ? "left" : "right"}}>{cuffed ? "🔒" : " "}</div>
            </div>)}

        </div>
     ); 
}
 
export default PlayerInfo;