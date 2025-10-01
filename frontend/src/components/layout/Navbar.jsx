// frontend/src/components/Navbar.jsx

import React from 'react';
import { useAuth } from '../context/AuthContext';

function Navbar() {
  const { isAuthenticated, logout, user } = useAuth();

  return (
    <header className="bg-white shadow-md p-4 flex justify-between items-center">
      <div className="text-xl font-bold">EdonuOps</div>
      <nav>
        {isAuthenticated ? (
          <div className="flex items-center">
            <span className="mr-4">Hello, {user?.username}</span>
            <button onClick={logout} className="bg-red-500 text-white px-4 py-2 rounded">Logout</button>
          </div>
        ) : (
          <a href="/login" className="bg-blue-500 text-white px-4 py-2 rounded">Login</a>
        )}
      </nav>
    </header>
  );
}

export default Navbar;