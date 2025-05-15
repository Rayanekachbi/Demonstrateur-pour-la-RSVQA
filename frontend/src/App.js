// src/App.js
import Home from "./Home";
import Datasets from "./Datasets";
import "./App.css";
import { BrowserRouter as Router} from "react-router-dom";

function App() {
  return (
    <Router>
      <div>
        <div>
          <section id="homepage">
            <Home />
          </section>
          <section id="datasets">
            <Datasets />
          </section>
        </div>
      </div>
    </Router>
  );
}

export default App;



