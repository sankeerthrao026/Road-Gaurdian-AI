import React from 'react';
import { AlertTriangle, MapPin, ChevronRight, Flame, RotateCw, Car, ShieldAlert, CheckCircle, Eye } from 'lucide-react';
import type { Incident } from '../types';

interface PriorityListProps {
  incidents: Incident[];
  selectedIncidentId: string | null;
  onSelectIncident: (incident: Incident) => void;
  processingState: string;
}

export const PriorityList: React.FC<PriorityListProps> = ({
  incidents,
  selectedIncidentId,
  onSelectIncident,
  processingState,
}) => {
  const getSeverityStyle = (label?: string) => {
    switch (label?.toLowerCase()) {
      case 'critical':
      case 'high':
        return 'text-[#D9534F] border-[#D9534F]/40 bg-[#1A1516]';
      case 'medium':
        return 'text-[#C98255] border-[#C98255]/40 bg-[#1B1714]';
      default:
        return 'text-[#55C98A] border-[#55C98A]/40 bg-[#141A16]';
    }
  };

  const getIcon = (type: string) => {
    const t = type.toLowerCase();
    if (t.includes('fire')) return <Flame className="w-3.5 h-3.5 text-[#D9534F]" />;
    if (t.includes('rollover')) return <RotateCw className="w-3.5 h-3.5 text-[#C98255]" />;
    return <Car className="w-3.5 h-3.5 text-[#C98255]" />;
  };

  // ── Empty states ──────────────────────────────────────────────────────────
  const emptyContent = () => {
    if (processingState === 'COMPLETE') {
      return (
        <div className="p-5 text-center font-mono text-xs border border-dashed border-[#394047] rounded">
          <CheckCircle className="w-5 h-5 mx-auto mb-2 text-[#55C98A]" />
          <p className="text-[#999EA5] font-semibold">NO INCIDENT DETECTED</p>
          <p className="text-[#798690] mt-1">All pipeline stages completed above threshold.</p>
        </div>
      );
    }
    if (processingState === 'FINAL_ANALYSIS') {
      return (
        <div className="p-5 text-center font-mono text-xs border border-dashed border-[#C98255]/40 rounded bg-[#1B1714]">
          <AlertTriangle className="w-5 h-5 mx-auto mb-2 text-[#C98255]" />
          <p className="text-[#C98255] font-semibold">FINAL ANALYSIS IN PROGRESS</p>
          <p className="text-[#798690] mt-1">ML severity scoring and classification running…</p>
        </div>
      );
    }
    return (
      <div className="p-5 text-center font-mono text-xs border border-dashed border-[#394047] rounded">
        <Eye className="w-5 h-5 mx-auto mb-2 text-[#394047]" />
        <p className="text-[#999EA5] font-semibold">MONITORING CCTV FEED</p>
        <p className="text-[#798690] mt-1">
          YOLOv8 + ByteTrack active. Incident queue populates after video completes.
        </p>
      </div>
    );
  };

  return (
    <div className="bg-[#141517] border border-[#394047] rounded-md flex flex-col">
      {/* Header */}
      <div className="bg-[#1B1D20] border-b border-[#394047] px-4 py-2.5 flex justify-between items-center">
        <div className="flex items-center gap-2 font-mono text-xs font-bold text-[#C98255] tracking-wider uppercase">
          <ShieldAlert className="w-4 h-4 text-[#C98255]" />
          <span>PRIORITY QUEUE</span>
        </div>
        <span className="font-mono text-xs text-[#999EA5] bg-[#0D0E10] px-2 py-0.5 border border-[#394047] rounded">
          {incidents.length} ACTIVE
        </span>
      </div>

      <div className="p-3 space-y-2.5">
        {incidents.length === 0 ? (
          emptyContent()
        ) : (
          incidents.map((inc, idx) => {
            const isSelected = selectedIncidentId === inc.incident_id;
            const rank = inc.priority_rank ?? idx + 1;

            return (
              <div
                key={inc.incident_id}
                onClick={() => onSelectIncident(inc)}
                className={`p-3 border rounded-md cursor-pointer transition-all ${
                  isSelected
                    ? 'bg-[#1B1714] border-[#C98255]'
                    : 'bg-[#0D0E10] border-[#394047] hover:border-[#798690]'
                }`}
              >
                <div className="flex justify-between items-start mb-2 gap-2 flex-wrap">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-[#C98255] bg-[#141517] px-2 py-0.5 border border-[#394047] rounded">
                      #{rank}
                    </span>
                    <div className="flex items-center gap-1.5 font-bold text-sm text-[#D4D9DF]">
                      {getIcon(inc.type)}
                      <span>{inc.type?.toUpperCase()}</span>
                    </div>
                  </div>
                  <span className={`font-mono text-xs font-bold px-2 py-0.5 border rounded ${getSeverityStyle(inc.severity_label)}`}>
                    {inc.severity_label?.toUpperCase()} {inc.severity_score}/100
                  </span>
                </div>

                <div className="flex items-center justify-between text-xs font-mono text-[#999EA5]">
                  <div className="flex items-center gap-1">
                    <MapPin className="w-3 h-3 text-[#798690]" />
                    <span>{inc.location?.road_name || 'Highway'} ({inc.camera_id})</span>
                  </div>
                  <ChevronRight className={`w-4 h-4 ${isSelected ? 'text-[#C98255]' : 'text-[#394047]'}`} />
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
