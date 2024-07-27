import {BrowserRouter as Router, Route, Routes} from 'react-router-dom'
import Game from './Game';
import Landing from './Landing';

function App() {
  return (
    <Router>
      <div className="App" onContextMenu={(e) => e.preventDefault()}>
        <Routes>
          <Route exact path='/' element={<Landing />} />
          <Route exact path='/play' element={<Game />} />
          {/* <Route path='*' element={<NotFound />} /> */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;
