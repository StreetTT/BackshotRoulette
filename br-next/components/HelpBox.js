import { useState, useEffect } from "react";
import { toTitleCase } from "../hooks/useTitleCase";
import { useGameContext } from '../Contexts/GameContext';


const HelpBox = ({ }) => {
    const items = {
        "knife": "The Gun will become 'Crit' and deal double damage for the next shot",
        "glass": "The user will see what type of round the next shot is",
        "drugs": "The user will gain one heart",
        "cuffs": "The opposing player will skip their next turn",
        "voddy": "The user will eject the current shell without firing it",
        "twist": "The polarity of the next shot will be flipped; a dead shell becomes live, and a live shell becomes dead",
        "spike": "The user has a 50% chance of regaining two hearts and a 50% chance of losing one",
        "8ball": "The user will be told the location and type of a random bullet in the gun",
        "pluck": "The user will be able to steal one item from the opposing player's side and use it immediately",
        };
    const [showInfoBox, setShowInfoBox] = useState(false);
    const [hideInfoBox, setHideInfoBox] = useState(false);
    const [infoBoxTitle, setInfoBoxTitle] = useState("");
    const [infoBoxContent, setInfoBoxContent] = useState("");
    const { infoBoxItem } = useGameContext();

    const displayInfoBox = (item) => {
        setShowInfoBox(true);
        setInfoBoxTitle(toTitleCase(item));
        setInfoBoxContent(items[item.toLowerCase()]);

        setTimeout(() => {
        setHideInfoBox(true);
        setTimeout(() => {
            setInfoBoxContent("");
            setInfoBoxTitle("");
            setShowInfoBox(false);
            setHideInfoBox(false);
        }, 500);
        }, 4000);
    };

    useEffect(() => {
        console.log("Right click", infoBoxItem);
        if (infoBoxItem) {
          displayInfoBox(infoBoxItem);
        }
      }, [infoBoxItem]);


    return (
        <>
        {showInfoBox && (
            <div className={`info-box ${hideInfoBox ? "slide-out" : ""}`}>
                <h4>{toTitleCase(infoBoxTitle)}</h4>
                <p>{infoBoxContent}</p>
            </div>
        )}
        </>
    );
};

export default HelpBox;



