import React, { useState, useEffect } from 'react';
import { Incident } from '../types';
import { AlertCircle, Clock, MapPin, Eye, Filter, Download, X, Maximize2 } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

const BACKEND_URL = 'http://localhost:5000';

export default function IncidentsPage() {
  const [selectedEvidence, setSelectedEvidence] = useState<string | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);

  useEffect(() => {
    const fetchIncidents = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/api/incidents`);
        const data = await response.json();
        setIncidents(data);
      } catch (error) {
        console.error('Failed to fetch incidents:', error);
      }
    };

    fetchIncidents();
    const interval = setInterval(fetchIncidents, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-8 bg-white min-h-screen">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-end mb-10">
          <div>
            <h1 className="text-3xl font-bold tracking-tight mb-2">Incident Repository</h1>
            <p className="text-gray-500">Historical log of all detected security and operational alarms.</p>
          </div>
          <div className="flex gap-3">
            <button className="flex items-center gap-2 px-4 py-2 border border-blue-100 bg-blue-50/30 text-blue-600 rounded-lg text-sm font-semibold hover:bg-blue-50 transition-colors">
              <Filter size={16} />
              Filter Logs
            </button>
            <button className="flex items-center gap-2 px-4 py-2 bg-[#0a0a0a] text-white rounded-lg text-sm font-semibold hover:bg-black shadow-lg transition-all">
              <Download size={16} />
              Export CSV
            </button>
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50/50 border-b border-gray-100">
                <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Evidence</th>
                <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Incident Details</th>
                <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Source</th>
                <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Severity</th>
                <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {incidents.map((incident) => (
                <tr key={incident.id} className="hover:bg-gray-50/50 transition-colors group">
                  <td className="px-6 py-6">
                    <button
                      onClick={() => setSelectedEvidence(incident.evidenceUrl)}
                      className="w-24 h-16 rounded-xl overflow-hidden border border-gray-100 relative group-hover:scale-105 transition-transform cursor-zoom-in"
                    >
                      <img src={`${BACKEND_URL}${incident.evidenceUrl}`} alt="Evidence" className="w-full h-full object-cover" />
                      <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                        <Maximize2 size={16} className="text-white" />
                      </div>
                    </button>
                  </td>
                  <td className="px-6 py-6">
                    <div className="flex flex-col gap-1">
                      <span className="text-xs font-mono font-bold text-primary">{incident.id}</span>
                      <p className="font-bold text-gray-900">{incident.type}</p>
                      <div className="flex items-center gap-2 text-gray-400 text-xs">
                        <Clock size={12} />
                        {incident.timestamp}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-6">
                    <div className="flex items-center gap-2">
                       <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-500">
                         <MapPin size={14} />
                       </div>
                       <div>
                         <p className="text-sm font-semibold">{incident.cameraName}</p>
                         <p className="text-[10px] text-gray-400 uppercase font-bold tracking-tighter">Sensor ID: {incident.cameraId}</p>
                       </div>
                    </div>
                  </td>
                  <td className="px-6 py-6">
                    <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                      incident.severity === 'high' ? 'bg-red-100 text-red-600' :
                      incident.severity === 'medium' ? 'bg-orange-100 text-orange-600' :
                      'bg-blue-100 text-blue-600'
                    }`}>
                      <AlertCircle size={10} />
                      {incident.severity}
                    </div>
                  </td>
                  <td className="px-6 py-6">
                    <button 
                      onClick={() => setSelectedEvidence(incident.evidenceUrl)}
                      className="px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-lg text-xs font-bold hover:border-primary hover:text-primary transition-all shadow-sm"
                    >
                      View Snapshot
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          <div className="p-6 bg-gray-50/50 border-t border-gray-100 flex justify-between items-center">
            <p className="text-sm text-gray-500 font-medium">Showing 1-{incidents.length} of {incidents.length} incidents</p>
            <div className="flex gap-2">
               <button className="px-4 py-2 border border-gray-200 rounded-lg text-xs font-bold opacity-50 cursor-not-allowed">Previous</button>
               <button className="px-4 py-2 border border-gray-200 rounded-lg text-xs font-bold hover:border-gray-900 hover:bg-white transition-all">Next</button>
            </div>
          </div>
        </div>
      </div>

      {/* Evidence Lightbox Modal */}
      <AnimatePresence>
        {selectedEvidence && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedEvidence(null)}
            className="fixed inset-0 z-50 bg-black/90 backdrop-blur-sm flex items-center justify-center p-4 md:p-12 cursor-zoom-out"
          >
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="relative max-w-5xl w-full bg-[#0a0a0a] rounded-3xl overflow-hidden shadow-2xl border border-gray-800"
            >
              <div className="absolute top-6 right-6 z-10">
                <button 
                  onClick={() => setSelectedEvidence(null)}
                  className="p-2 bg-black/50 hover:bg-black text-white rounded-full backdrop-blur-md transition-colors"
                >
                  <X size={24} />
                </button>
              </div>

              <div className="p-6 border-b border-gray-800 flex items-center justify-between">
                <div>
                   <h3 className="text-white font-bold text-lg">Evidence Analysis</h3>
                   <p className="text-gray-500 text-sm">Industrial Vision Snap-Archive #428</p>
                </div>
                <div className="flex gap-2">
                   <span className="px-3 py-1 bg-primary/20 text-primary text-[10px] font-bold uppercase rounded-full">AI Verified</span>
                   <span className="px-3 py-1 bg-white/5 text-gray-400 text-[10px] font-bold uppercase rounded-full">RAW Capture</span>
                </div>
              </div>

              <div className="aspect-video bg-black flex items-center justify-center overflow-hidden">
                <img
                  src={selectedEvidence?.startsWith('http') ? selectedEvidence : `${BACKEND_URL}${selectedEvidence}`}
                  alt="Full Evidence"
                  className="w-full h-full object-contain"
                />
              </div>

              <div className="p-6 bg-[#0f0f0f] flex justify-between items-center">
                 <div className="flex gap-6">
                    <div className="flex flex-col">
                      <span className="text-[10px] text-gray-500 font-bold uppercase">Exposure</span>
                      <span className="text-white text-sm font-mono">+0.5 EV</span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-[10px] text-gray-500 font-bold uppercase">Sensor</span>
                      <span className="text-white text-sm font-mono">Sony IMX415</span>
                    </div>
                 </div>
                 <button className="px-6 py-2 bg-primary text-white rounded-xl font-bold text-sm shadow-lg hover:bg-primary-dark transition-all">
                    Download RAW
                 </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
