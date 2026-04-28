import React from 'react';
import { Camera, Incident } from '../types';
import { Camera as CameraIcon, ShieldAlert, Settings, LayoutDashboard, LogOut } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

export default function Sidebar() {
  const location = useLocation();

  const menuItems = [
    { icon: LayoutDashboard, label: 'Live CCTV', path: '/' },
    { icon: ShieldAlert, label: 'Incidents', path: '/incidents' },
    { icon: Settings, label: 'Settings', path: '/settings' },
  ];

  return (
    <div id="sidebar" className="w-64 bg-[#0a0a0a] text-white flex flex-col h-screen fixed left-0 top-0">
      <div className="p-6 flex items-center gap-3">
        <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
          <ShieldAlert size={20} className="text-white" />
        </div>
        <h1 className="text-xl font-bold tracking-tight">Kenesis <span className="text-primary">Vision</span></h1>
      </div>

      <nav className="flex-1 mt-6">
        <p className="px-6 text-xs font-semibold text-gray-500 uppercase tracking-widest mb-4">Menu</p>
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-6 py-4 transition-all border-r-4 ${
                isActive 
                  ? 'bg-gray-900 border-primary text-primary' 
                  : 'border-transparent text-gray-400 hover:text-white hover:bg-gray-900'
              }`}
            >
              <item.icon size={20} />
              <span className="font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-6 border-t border-gray-800">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-full bg-gray-800 border border-gray-700 overflow-hidden">
            <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="User" />
          </div>
          <div>
            <p className="text-sm font-medium">Aswin</p>
            <p className="text-xs text-gray-500">Security Head</p>
          </div>
        </div>
        <button className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors text-sm">
          <LogOut size={16} />
          Logout
        </button>
      </div>
    </div>
  );
}
