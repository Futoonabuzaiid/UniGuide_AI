import { Routes, Route, Navigate } from "react-router-dom";
import ChatPage from "./pages/ChatPage.jsx";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/chat" />} />
      <Route path="/chat" element={<ChatPage />} />
    </Routes>
  );
}

export default App;