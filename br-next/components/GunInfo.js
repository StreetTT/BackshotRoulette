import { useState, useEffect } from "react";

const GunInfo = ({ crit, chamber }) => {
  const [visibleStatus, setVisibleStatus] = useState("hide");
  const [setup, setSetup] = useState(true);

  useEffect(() => {
    const handleMouseEnter = (event) => {
      const screenWidth = window.innerWidth;
      const screenHeight = window.innerHeight;
      const { clientX: x, clientY: y } = event;

      // Check if the mouse enters the specified areas and update visibility status accordingly
      if (screenHeight / 3 < y && y <= (2 * screenHeight) / 3) {
        if (screenWidth / 8 > x) {
          setVisibleStatus("show");
        } else if (screenWidth / 4 > x) {
          setVisibleStatus("poke");
        } else {
          setVisibleStatus("hide");
        }
      } else {
        setVisibleStatus("hide");
      }
    };

    document.addEventListener("mousemove", handleMouseEnter);

    return () => {
      document.removeEventListener("mousemove", handleMouseEnter);
    };
  }, []);

  return (
    <div className={`gun ${visibleStatus}`}>
      <h4>Gun Information</h4>
      <span className={crit ? "crit" : ""}>
        {crit ? "CRITICAL DAMAGE" : "Normal Damage"}
      </span>
      <div className="chamber">
        {setup && <div className="bullets">
          {chamber.map((bullet, index) => (
            <div key={index} className={`bullet ${bullet ? "live" : "dead"}`} />
          ))}
        </div>}
        <p>
          Dead: {chamber.filter((item) => !item).length}, Live:
          {chamber.filter((item) => item).length}
        </p>
      </div>
    </div>
  ); // <div className="bullets"> needs to be able to hide
};

export default GunInfo;
