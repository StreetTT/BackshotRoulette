import {BrowserRouter as Router, Route, Routes} from 'react-router-dom'
import Game from './Game';

function App() {
  return (
    <Router>
      <div className="App" onContextMenu={(e) => e.preventDefault()}>
        <Routes>
          <Route exact path='/' element={<Game />} />
          {/* <Route path='*' element={<NotFound />} /> */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;
