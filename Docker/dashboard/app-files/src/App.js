import { BrowserRouter, Route, Routes } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import DataPage from "./pages/DataPage";
import ConfigPage from "./pages/ConfigPage"
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/iot-platform/login"
          exact
          element={<LoginPage />}
        ></Route>
        <Route path="/iot-platform/dashboard" exact element={<DataPage />}></Route>
        <Route path="/iot-platform/config" exact element={<ConfigPage />}></Route>
        <Route path="*" element={<LoginPage />}></Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
