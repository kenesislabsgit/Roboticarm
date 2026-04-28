import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import CCTVPage from './components/CCTVPage';
import IncidentsPage from './components/IncidentsPage';

export default function App() {
  return (
    <Router>
      <div className="flex min-h-screen bg-white">
        <Sidebar />
        <main className="flex-1 ml-64 overflow-auto">
          <Routes>
            <Route path="/" element={<CCTVPage />} />
            <Route path="/incidents" element={<IncidentsPage />} />
            <Route path="/settings" element={
              <div className="p-12 text-center">
                <h1 className="text-2xl font-bold">Settings</h1>
                <p className="text-gray-500">Service configuration panel.</p>
              </div>
            } />
          </Routes>
        </main>
      </div>
    </Router>
  );
}
