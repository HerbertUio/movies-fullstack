// src/App.jsx
import React, { useContext } from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import AppContent from './AppContent';
import Login from './components/Login';
import { AuthContext } from './context/AuthContext';

function App() {
  const { auth } = useContext(AuthContext);

  if (!auth) {
    return <Login />;
  }

  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
