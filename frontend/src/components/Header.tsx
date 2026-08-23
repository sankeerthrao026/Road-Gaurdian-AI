import React from 'react';
import { Shield, Camera as CameraIcon, Activity } from 'lucide-react';
import type { Camera } from '../types';

interface HeaderProps {
  cameras: Camera[];
  activeCameraId: string;
  onSelectCamera: (id: string) => void;
  status: string;
  processingState: string;
}

export const Header: React.FC<HeaderProps> = ({
  cameras,
  activeCameraId,
  onSelectCamera,
  status,
  processingState
}) => {
  return (
    <header className="bg-[#141517] border-b border-[#394047] px-6 py-3 flex flex-wrap justify-between items-center gap-4">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-[#1B1D20] border border-[#394047] rounded-md">
          <Shield className="w-6 h-6 text-[#C98255]" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-sans font-bold text-lg text-[#D4D9DF] tracking-wider uppercase">
              ROADGUARDIAN AI
            </h1>
            <span className="px-2 py-0.5 text-[10px] font-mono font-semibold bg-[#1B1D20] text-[#999EA5] border border-[#394047] rounded">
              v2.0
            </span>
          </div>
          <p className="font-mono text-xs text-[#798690] uppercase tracking-wide">
            AI Road Incident Intelligence & Emergency Orchestration
          </p>
        </div>
      </div>

      <div className="flex items-center gap-4 flex-wrap">
        {/* Camera Selector */}
        <div className="flex items-center gap-2 bg-[#0D0E10] border border-[#394047] rounded-md px-3 py-1.5">
          <CameraIcon className="w-4 h-4 text-[#C98255]" />
          <span className="font-mono text-xs text-[#798690] uppercase font-semibold">FEED:</span>
          <select
            value={activeCameraId}
            onChange={(e) => onSelectCamera(e.target.value)}
            className="bg-transparent font-mono text-xs text-[#D4D9DF] font-semibold focus:outline-none cursor-pointer"
          >
            {cameras.map((cam) => (
              <option key={cam.id} value={cam.id} className="bg-[#141517] text-[#D4D9DF]">
                {cam.id}: {cam.name}
              </option>
            ))}
          </select>
        </div>

        {/* System Status Pills */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 bg-[#0D0E10] border border-[#394047] px-3 py-1.5 rounded-md font-mono text-xs font-semibold text-[#999EA5]">
            <span className={`w-2 h-2 rounded-full ${status === 'PLAYING' ? 'bg-[#55C98A]' : 'bg-[#C98255]'}`} />
            <span>SYSTEM {status === 'PLAYING' ? 'ONLINE' : status}</span>
          </div>

          <div className="flex items-center gap-1.5 bg-[#0D0E10] border border-[#394047] px-3 py-1.5 rounded-md font-mono text-xs font-semibold text-[#C98255]">
            <Activity className="w-3.5 h-3.5" />
            <span>{processingState}</span>
          </div>
        </div>
      </div>
    </header>
  );
};
