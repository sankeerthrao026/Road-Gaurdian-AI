import React from 'react';
import { MapPin, Navigation, Radio } from 'lucide-react';

interface DigitalTwinMapProps {
  cameraId: string;
  roadName: string;
}

export const DigitalTwinMap: React.FC<DigitalTwinMapProps> = ({ cameraId, roadName }) => {
  return (
    <div className="bg-[#141517] border border-[#394047] rounded-md flex flex-col h-full">
      <div className="bg-[#1B1D20] border-b border-[#394047] px-4 py-2.5 flex justify-between items-center font-mono text-xs font-bold text-[#C98255] uppercase">
        <div className="flex items-center gap-2">
          <Navigation className="w-4 h-4 text-[#C98255]" />
          <span>DIGITAL TWIN GIS MONITOR</span>
        </div>
        <span className="flex items-center gap-1 text-[10px] text-[#55C98A]">
          <Radio className="w-3 h-3 animate-pulse" /> LIVE TELEMETRY
        </span>
      </div>

      <div className="p-4 font-mono text-xs text-[#999EA5] space-y-3">
        <div className="bg-[#0D0E10] border border-[#394047] p-3 rounded flex items-center justify-between">
          <div className="flex items-center gap-2">
            <MapPin className="w-4 h-4 text-[#C98255]" />
            <div>
              <div className="text-[10px] text-[#798690]">CAMERA NODE</div>
              <div className="text-[#D4D9DF] font-bold">{cameraId} — {roadName}</div>
            </div>
          </div>
          <span className="text-[10px] bg-[#1B1D20] border border-[#394047] px-2 py-1 rounded text-[#D4D9DF]">
            GPS: 37.7749° N, 122.4194° W
          </span>
        </div>

        {/* Tactical Simulated GIS Radar Display */}
        <div className="relative bg-[#090A0C] border border-[#394047] rounded h-32 flex items-center justify-center overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(#394047_1px,transparent_1px)] [background-size:16px_16px] opacity-30" />
          <div className="w-20 h-20 rounded-full border border-[#394047] flex items-center justify-center relative">
            <div className="w-10 h-10 rounded-full border border-[#C98255]/40 animate-ping" />
            <div className="w-2 h-2 rounded-full bg-[#C98255] absolute" />
          </div>
          <div className="absolute bottom-2 left-3 text-[10px] text-[#798690]">
            CORRIDOR SENSORS ACTIVE
          </div>
        </div>
      </div>
    </div>
  );
};
