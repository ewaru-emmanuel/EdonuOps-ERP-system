// frontend/src/components/Sidebar.jsx

import React from 'react';
import { Link } from 'react-router-dom';
import { useModuleAccess } from '../hooks/useModuleAccess';

function Sidebar() {
  const { hasAccess } = useModuleAccess();

  return (
    <aside className="bg-gray-900 text-white w-64 min-h-screen p-4">
      <nav>
        <ul>
          <li className="mb-2">
            <Link to="/" className="block py-2 px-4 rounded hover:bg-gray-700">Dashboard</Link>
          </li>
          {hasAccess('core_setup') && (
            <li className="mb-2">
              <Link to="/core-setup" className="block py-2 px-4 rounded hover:bg-gray-700">Core Setup</Link>
            </li>
          )}
          {hasAccess('inventory_wms') && (
            <li className="mb-2">
              <Link to="/inventory-wms" className="block py-2 px-4 rounded hover:bg-gray-700">Inventory + WMS</Link>
            </li>
          )}
          {hasAccess('procurement') && (
            <li className="mb-2">
              <Link to="/procurement" className="block py-2 px-4 rounded hover:bg-gray-700">Procurement</Link>
            </li>
          )}
          {hasAccess('dashboard_ai') && (
            <li className="mb-2">
              <Link to="/dashboard-ai" className="block py-2 px-4 rounded hover:bg-gray-700">Dashboard & AI Copilot</Link>
            </li>
          )}
          {hasAccess('admin_settings') && (
            <li className="mb-2">
              <Link to="/admin-settings" className="block py-2 px-4 rounded hover:bg-gray-700">Admin & Settings</Link>
            </li>
          )}
        </ul>
      </nav>
    </aside>
  );
}

export default Sidebar;
