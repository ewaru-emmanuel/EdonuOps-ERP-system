import React from 'react';
import { Link } from 'react-router-dom';

const Dashboard = () => {
    const modules = [
        {
            name: 'Core Setup',
            path: '/core-setup',
            description: 'Company, locale, roles, and plugin settings.'
        },
        {
            name: 'Finance',
            path: '/finance',
            description: 'Manage accounts, ledgers, and financial reports.'
        },
        {
            name: 'Inventory + WMS',
            path: '/inventory-wms',
            description: 'Stock, QR scanning, and warehouse logistics.'
        },
        {
            name: 'Procurement',
            path: '/procurement',
            description: 'Purchase orders, vendor scoring, and invoice matching.'
        },
        {
            name: 'Dashboard & AI Copilot',
            path: '/dashboard-ai',
            description: 'Modular dashboards, analytics, and AI agent.'
        },
        {
            name: 'Admin & Settings',
            path: '/admin-settings',
            description: 'User roles, theming, logs, and plugins.'
        }
    ];

    return (
        <div className="p-6 bg-gray-100 min-h-screen space-y-10">
            <header className="text-center mb-12">
                <h1 className="text-4xl font-extrabold text-gray-800 tracking-tight">Welcome to EdonuOps</h1>
                <p className="mt-2 text-gray-600 text-lg">Your centralized dashboard for operational excellence.</p>
            </header>

            <section className="mb-16">
                <h2 className="text-2xl font-semibold text-gray-700 mb-6">Core Modules</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {modules.map((mod) => (
                        <Link
                            key={mod.name}
                            to={mod.path}
                            className="bg-white border border-gray-200 hover:border-blue-500 hover:bg-blue-50 p-6 rounded-xl shadow-md transition duration-200 hover:shadow-lg"
                        >
                            <h3 className="text-xl font-semibold text-blue-700 mb-1">{mod.name}</h3>
                            <p className="text-sm text-gray-600">{mod.description}</p>
                        </Link>
                    ))}
                </div>
            </section>

            <section>
                <h2 className="text-2xl font-semibold text-gray-700 mb-6">Quick Stats</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                    <div className="bg-white border border-gray-200 p-6 rounded-xl shadow-md text-center">
                        <p className="text-3xl font-bold text-blue-600">12</p>
                        <p className="text-sm text-gray-600 mt-1">New Leads</p>
                    </div>
                    <div className="bg-white border border-gray-200 p-6 rounded-xl shadow-md text-center">
                        <p className="text-3xl font-bold text-green-600">$24K</p>
                        <p className="text-sm text-gray-600 mt-1">Monthly Revenue</p>
                    </div>
                    <div className="bg-white border border-gray-200 p-6 rounded-xl shadow-md text-center">
                        <p className="text-3xl font-bold text-yellow-600">4</p>
                        <p className="text-sm text-gray-600 mt-1">Pending Orders</p>
                    </div>
                    <div className="bg-white border border-gray-200 p-6 rounded-xl shadow-md text-center">
                        <p className="text-3xl font-bold text-red-600">3</p>
                        <p className="text-sm text-gray-600 mt-1">Overdue Invoices</p>
                    </div>
                </div>
            </section>
        </div>
    );
};

export default Dashboard;
