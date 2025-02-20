// src/components/Sidebar.jsx
import React from 'react';
import { Link } from 'react-router-dom';

function Sidebar({ isOpen, toggleSidebar, isAdmin }) {
  return (
    <>
      {/* Overlay */}
      <div
        className={`fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity duration-300 ${
          isOpen ? 'opacity-100 visible' : 'opacity-0 invisible'
        }`}
        onClick={toggleSidebar}
      ></div>
      {/* Sidebar */}
      <div
        className={`fixed top-0 left-0 h-full w-64 bg-gray-800 text-white shadow-lg z-50 transform transition-transform duration-300 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="p-6">
          <h2 className="text-2xl font-bold mb-6">Menú</h2>
          <ul className="space-y-4">
            {isAdmin && (
              <li>
                <Link to="/gestion-categorias" className="hover:text-blue-400" onClick={toggleSidebar}>
                  Gestión de Categorías
                </Link>
              </li>
            )}
            {/* Puedes agregar más opciones aquí */}
          </ul>
        </div>
      </div>
    </>
  );
}

export default Sidebar;
