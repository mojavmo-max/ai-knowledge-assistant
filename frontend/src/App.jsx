import {Routes, Route} from 'react-router-dom';
import Home from "./pages/Home";
import Invoice from "./pages/Invoice";
import Knowledge from "./pages/Knowledge";

function App() {
  return(
    <Routes>
        <Route path="/" element={<Home />}/>
        <Route path="/knowledge" element={<Knowledge />}/>
        <Route path="/invoice" element={<Invoice />}/>
      </Routes>
  )
}

export default App
