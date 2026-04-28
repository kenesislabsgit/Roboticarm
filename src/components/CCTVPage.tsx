import React, { useState } from 'react';
import { Camera } from '../types';
import { Camera as CameraIcon, Plus, Maximize, Activity, Info } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

const INITIAL_CAMERAS: Camera[] = [
  { id: '1', name: 'Robotic Arm Area 1', status: 'online', region: 'Factory Floor' },
  { id: '2', name: 'Inventory Gate B', status: 'alert', region: 'Warehouse' },
  { id: '3', name: 'Main Assembly Line', status: 'online', region: 'Factory Floor' },
  { id: '4', name: 'Server Rack Room', status: 'online', region: 'IT Office' },
];

export default function CCTVPage() {
  const [cameras, setCameras] = useState<Camera[]>(INITIAL_CAMERAS);
  const [selectedCamera, setSelectedCamera] = useState<Camera>(cameras[0]);

  const addCamera = () => {
    const newId = (cameras.length + 1).toString();
    const newCamera: Camera = {
      id: newId,
      name: `New Camera ${newId}`,
      status: 'online',
      region: 'Unknown',
    };
    setCameras([...cameras, newCamera]);
  };

  return (
    <div className="flex bg-white h-full">
      {/* Camera List Sidebar (Internal) */}
      <div className="w-80 border-r border-gray-100 flex flex-col h-full overflow-hidden">
        <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
          <h2 className="font-bold flex items-center gap-2">
            <CameraIcon size={18} className="text-primary" />
            Active Sources
          </h2>
          <button 
            onClick={addCamera}
            className="p-1.5 rounded-full bg-primary text-white hover:bg-primary-dark transition-colors"
            title="Add Camera"
          >
            <Plus size={16} />
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto">
          {cameras.map((camera) => (
            <button
              key={camera.id}
              onClick={() => setSelectedCamera(camera)}
              className={`w-full text-left p-5 border-b border-gray-50 transition-all ${
                selectedCamera.id === camera.id 
                  ? 'bg-orange-50 border-l-4 border-l-primary' 
                  : 'hover:bg-gray-50 border-l-4 border-l-transparent'
              }`}
            >
              <div className="flex justify-between items-start mb-1">
                <span className={`text-xs font-bold uppercase tracking-wider ${
                  selectedCamera.id === camera.id ? 'text-primary' : 'text-gray-400'
                }`}>
                  {camera.region}
                </span>
                <span className={`w-2 h-2 rounded-full ${
                  camera.status === 'online' ? 'bg-green-500' : 'bg-red-500 animate-pulse'
                }`} />
              </div>
              <p className={`font-semibold ${selectedCamera.id === camera.id ? 'text-gray-900' : 'text-gray-600'}`}>
                {camera.name}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Main Feed Area */}
      <div className="flex-1 p-8 bg-[#f8f9fa] flex flex-col overflow-hidden">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-3">
              {selectedCamera.name}
              {selectedCamera.status === 'alert' && (
                <span className="bg-red-100 text-red-600 text-[10px] uppercase px-2 py-1 rounded-full font-bold animate-bounce">
                  Active Alert
                </span>
              )}
            </h1>
            <p className="text-gray-500 text-sm">Real-time stream from {selectedCamera.region}</p>
          </div>
          <div className="flex gap-2">
            <button className="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-lg text-sm bg-white hover:bg-gray-50 font-medium">
              <Activity size={16} className="text-primary" />
              Diagnostics
            </button>
            <button className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg text-sm hover:bg-primary-dark font-medium shadow-sm transition-all">
              <Maximize size={16} />
              Full Screen
            </button>
          </div>
        </div>

        {/* Video Canvas Simulator */}
        <div className="flex-1 relative rounded-2xl overflow-hidden bg-black shadow-2xl border-4 border-white group">
          <div className="absolute inset-0 opacity-20 pointer-events-none bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')]"></div>
          
          {/* Mock Video Content */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-full h-full relative">
              <img 
                src={`https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&q=80&w=1200&h=800`} 
                className="w-full h-full object-cover opacity-60 grayscale-[0.5]"
                alt="Feed"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
            </div>
          </div>

          {/* Overlays */}
          <div className="absolute top-6 left-6 flex flex-col gap-2">
            <div className="bg-black/50 backdrop-blur-md text-white text-[10px] font-mono px-3 py-1 bg rounded uppercase tracking-widest flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
              Live Feed
            </div>
            <div className="bg-black/50 backdrop-blur-md text-white text-[10px] font-mono px-3 py-1 rounded">
              0.45s Latency • 4K UHD
            </div>
          </div>

          <div className="absolute bottom-6 left-6 text-white font-mono">
            <p className="text-sm font-bold">{selectedCamera.id.padStart(3, '0')}-CAM-{selectedCamera.region.split(' ')[0].toUpperCase()}</p>
            <p className="text-[10px] opacity-70">2026-04-28 08:30:45.12</p>
          </div>

          <div className="absolute bottom-6 right-6 flex gap-3">
             <button className="w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 backdrop-blur-md flex items-center justify-center text-white transition-all">
                <Info size={18} />
             </button>
          </div>

          {/* Alert Overlay if needed */}
          {selectedCamera.status === 'alert' && (
            <div className="absolute inset-0 ring-[12px] ring-red-500/30 animate-pulse pointer-events-none"></div>
          )}
        </div>

        <div className="mt-6 grid grid-cols-4 gap-4">
            {cameras.slice(0, 4).map(cam => (
              <div key={cam.id} className="h-24 bg-gray-200 rounded-xl overflow-hidden relative cursor-pointer hover:ring-2 hover:ring-primary transition-all">
                  <img 
                    src={`https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&q=80&w=300&h=200&sig=${cam.id}`} 
                    className="w-full h-full object-cover grayscale brightness-50"
                    alt="Preview"
                  />
                  <div className="absolute inset-0 flex items-center justify-center text-white font-bold text-[10px] uppercase tracking-tighter text-center px-2">
                    {cam.name}
                  </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}
