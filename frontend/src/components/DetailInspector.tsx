import React, { useState } from 'react';
import {
  FileText,
  BarChart2,
  Shield,
  Clock,
  Database,
  Cpu,
  Trophy,
  AlertCircle,
  Siren,
  Flame,
  RotateCw,
  User,
  Car,
  CheckCircle,
  Loader,
} from 'lucide-react';
import type { Incident, Dispatch, ModelComparisonResponse } from '../types';
import { SeverityGauge } from './SeverityGauge';
import { ShapChart } from './ShapChart';

interface DetailInspectorProps {
  incident: Incident | null;
  dispatches: Dispatch[];
  modelComparison: ModelComparisonResponse | null;
  processingState: string;
  videoFps?: number;
  aiFps?: number;
  displayFps?: number;
  framesProcessed?: number;
  framesSkipped?: number;
  totalFrames?: number;
  videoDuration?: number;
  processingDuration?: number;
}

type TabKey = 'overview' | 'severity' | 'dispatches' | 'report' | 'rag' | 'performance';

const TABS: { key: TabKey; label: string; icon: React.ReactNode }[] = [
  { key: 'overview',    label: 'OVERVIEW',       icon: <Shield className="w-3.5 h-3.5" /> },
  { key: 'severity',   label: 'SEVERITY',        icon: <BarChart2 className="w-3.5 h-3.5" /> },
  { key: 'dispatches', label: 'RESPONSE',        icon: <Siren className="w-3.5 h-3.5" /> },
  { key: 'report',     label: 'FINAL REPORT',    icon: <FileText className="w-3.5 h-3.5" /> },
  { key: 'rag',        label: 'RAG CONTEXT',     icon: <Database className="w-3.5 h-3.5" /> },
  { key: 'performance',label: 'PERFORMANCE',     icon: <Cpu className="w-3.5 h-3.5" /> },
];

export const DetailInspector: React.FC<DetailInspectorProps> = ({
  incident,
  dispatches,
  modelComparison,
  processingState,
  videoFps,
  aiFps,
  displayFps,
  framesProcessed,
  framesSkipped,
  totalFrames,
  videoDuration,
  processingDuration,
}) => {
  const [activeTab, setActiveTab] = useState<TabKey>('overview');

  // ── State-aware empty state ──────────────────────────────────────────────────
  if (!incident) {
    return (
      <div className="bg-[#141517] border border-[#394047] rounded-md p-6 font-mono text-xs">
        {processingState === 'FINAL_ANALYSIS' ? (
          <div className="text-center space-y-3">
            <Loader className="w-8 h-8 text-[#C98255] mx-auto animate-spin" />
            <h3 className="text-sm font-bold text-[#D4D9DF]">FINAL ANALYSIS IN PROGRESS</h3>
            <p className="text-[#798690] max-w-lg mx-auto leading-relaxed">
              Executing ML severity scoring → SHAP attribution → RAG context recall → LangGraph Agentic AI → Emergency dispatch → Report generation.
            </p>
            <div className="flex justify-center gap-6 mt-3 text-[10px] text-[#798690]">
              {['XGBoost Severity', 'SHAP Explainability', 'ChromaDB RAG', 'LangGraph Agent', 'Dispatch', 'Report'].map((step) => (
                <div key={step} className="flex items-center gap-1">
                  <Loader className="w-3 h-3 animate-spin text-[#C98255]" /> {step}
                </div>
              ))}
            </div>
          </div>
        ) : processingState === 'ANALYZING' ? (
          <div className="text-center space-y-2">
            <AlertCircle className="w-8 h-8 text-[#394047] mx-auto" />
            <h3 className="text-sm font-bold text-[#D4D9DF]">MONITORING CCTV FEED</h3>
            <p className="text-[#798690] max-w-lg mx-auto leading-relaxed">
              YOLOv8 + ByteTrack active. Final incident classification, ML severity scoring, SHAP, RAG recall, LangGraph agent, and emergency dispatch will trigger upon video completion.
            </p>
          </div>
        ) : (
          <div className="text-center space-y-2">
            <CheckCircle className="w-8 h-8 text-[#55C98A] mx-auto" />
            <h3 className="text-sm font-bold text-[#D4D9DF]">NO INCIDENT DETECTED</h3>
            <p className="text-[#798690]">All pipeline stages completed. No incident was classified above threshold.</p>
          </div>
        )}
      </div>
    );
  }

  const inc = incident;
  const shapEntries = Object.entries(inc.shap_values ?? {});
  const incIcon =
    inc.type?.toLowerCase().includes('fire') ? '🔥' :
    inc.type?.toLowerCase().includes('rollover') ? '🔄' :
    inc.type?.toLowerCase().includes('collision') ? '💥' : '🛑';

  // Dispatches matched to this incident
  const matchedDispatches = dispatches.filter(
    (d) => !d.target_incident || d.target_incident === inc.incident_id
  );

  return (
    <div className="bg-[#141517] border border-[#394047] rounded-md flex flex-col">
      {/* ── COMPLETE Banner ──────────────────────────────────────────────────── */}
      {processingState === 'COMPLETE' && (
        <div className="bg-[#141A16] border-b border-[#55C98A]/30 px-4 py-2 flex items-center gap-2 font-mono text-xs font-bold text-[#55C98A]">
          <CheckCircle className="w-4 h-4" />
          FINAL ANALYSIS COMPLETE — {inc.type?.toUpperCase()} | Severity {inc.severity_score}/100 | {inc.incident_id}
        </div>
      )}

      {/* ── Tab Bar ──────────────────────────────────────────────────────────── */}
      <div className="bg-[#1B1D20] border-b border-[#394047] px-4 py-2 flex flex-wrap gap-1 overflow-x-auto">
        {TABS.map(({ key, label, icon }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key)}
            className={`flex items-center gap-1.5 px-3 py-1.5 font-mono text-xs font-semibold rounded border transition cursor-pointer ${
              activeTab === key
                ? 'bg-[#141517] border-[#C98255] text-[#C98255]'
                : 'border-transparent text-[#798690] hover:text-[#D4D9DF] hover:border-[#394047]'
            }`}
          >
            {icon} {label}
          </button>
        ))}
      </div>

      {/* ── Tab Content ──────────────────────────────────────────────────────── */}
      <div className="p-4">

        {/* OVERVIEW ─────────────────────────────────────────────────────────── */}
        {activeTab === 'overview' && (
          <div className="space-y-4">
            {/* Incident Confirmation Card */}
            <div className="bg-[#0D0E10] border border-[#394047] border-l-4 border-l-[#C98255] rounded p-4">
              <div className="flex justify-between items-start mb-2 flex-wrap gap-2">
                <div className="flex items-center gap-2">
                  <span className="text-lg">{incIcon}</span>
                  <span className="font-sans font-bold text-base text-[#D4D9DF]">
                    INCIDENT CONFIRMED — {inc.type?.toUpperCase()}
                  </span>
                  <span className="font-mono text-[10px] text-[#999EA5] bg-[#141517] border border-[#394047] px-2 py-0.5 rounded">
                    [{inc.incident_id}]
                  </span>
                </div>
                <span
                  className={`font-mono text-xs font-bold px-2 py-1 border rounded uppercase ${
                    inc.severity_label?.toLowerCase() === 'critical' || inc.severity_label?.toLowerCase() === 'high'
                      ? 'text-[#D9534F] border-[#D9534F]/40 bg-[#1A1516]'
                      : inc.severity_label?.toLowerCase() === 'medium'
                      ? 'text-[#C98255] border-[#C98255]/40 bg-[#1B1714]'
                      : 'text-[#55C98A] border-[#55C98A]/40 bg-[#141A16]'
                  }`}
                >
                  {inc.severity_label?.toUpperCase()} ({inc.severity_score}/100)
                </span>
              </div>
              <p className="font-mono text-xs text-[#999EA5]">
                📍 <strong className="text-[#D4D9DF]">{inc.location?.road_name || 'Highway Corridor'}</strong> ({inc.camera_id})
              </p>
            </div>

            {/* Feature Flags Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 font-mono text-xs">
              {[
                { icon: <Car className="w-4 h-4 text-[#C98255]" />, label: 'VEHICLES', value: String(inc.features?.vehicle_count ?? 0) },
                { icon: <User className="w-4 h-4 text-[#55C98A]" />, label: 'PEDESTRIAN', value: inc.features?.person_on_road ? 'YES' : 'NO', alert: inc.features?.person_on_road },
                { icon: <Flame className="w-4 h-4 text-[#D9534F]" />, label: 'FIRE / SMOKE', value: inc.features?.fire_smoke ? 'YES' : 'NO', alert: inc.features?.fire_smoke },
                { icon: <RotateCw className="w-4 h-4 text-[#C98255]" />, label: 'ROLLOVER', value: inc.features?.rollover ? 'YES' : 'NO', alert: inc.features?.rollover },
              ].map(({ icon, label, value, alert }) => (
                <div
                  key={label}
                  className={`bg-[#0D0E10] border rounded p-3 flex items-center gap-2 ${alert ? 'border-[#D9534F]/40' : 'border-[#394047]'}`}
                >
                  {icon}
                  <div>
                    <div className="text-[10px] text-[#798690]">{label}</div>
                    <div className={`font-bold ${alert ? 'text-[#D9534F]' : 'text-[#D4D9DF]'}`}>{value}</div>
                  </div>
                </div>
              ))}
            </div>

            {/* Evidence Timeline */}
            {inc.evidence && (
              <div className="bg-[#0D0E10] border border-[#394047] p-4 rounded">
                <h4 className="font-mono text-xs font-bold text-[#C98255] uppercase mb-2 flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5" /> EVIDENCE TIMELINE
                </h4>
                <p className="font-mono text-xs text-[#D4D9DF] mb-3">{inc.evidence.summary}</p>
                {inc.evidence.timeline?.length > 0 && (
                  <div className="space-y-1.5 pl-3 border-l-2 border-[#394047]">
                    {inc.evidence.timeline.map((ev, idx) => (
                      <div key={idx} className="font-mono text-xs text-[#999EA5] flex items-start gap-2">
                        <span className="text-[#C98255] font-bold shrink-0">{ev.timestamp}</span>
                        <span>— {ev.event}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* SEVERITY & SHAP ─────────────────────────────────────────────────── */}
        {activeTab === 'severity' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Severity Gauge */}
            <div className="bg-[#0D0E10] border border-[#394047] rounded p-4 flex flex-col items-center gap-4">
              <div className="font-mono text-[10px] font-bold text-[#999EA5] uppercase tracking-wider self-start">ML Severity Score</div>
              <SeverityGauge score={inc.severity_score} label={inc.severity_label ?? 'High'} />
              <div className="text-xs font-mono text-[#798690] text-center">
                XGBoost Regression Model • Trained on Historical Incident Data
              </div>
            </div>

            {/* SHAP Chart */}
            <div className="bg-[#0D0E10] border border-[#394047] rounded p-4">
              {shapEntries.length > 0 ? (
                <ShapChart shapValues={inc.shap_values!} />
              ) : (
                <div className="text-xs font-mono text-[#798690] text-center mt-8">SHAP values not available</div>
              )}
            </div>
          </div>
        )}

        {/* EMERGENCY RESPONSE ──────────────────────────────────────────────── */}
        {activeTab === 'dispatches' && (
          <div className="space-y-3 font-mono text-xs">
            {matchedDispatches.length === 0 ? (
              <div className="text-center text-[#798690] py-6">
                <Siren className="w-6 h-6 mx-auto mb-2 text-[#394047]" />
                <p>No dispatch records yet.</p>
              </div>
            ) : (
              matchedDispatches.map((d, idx) => (
                <div
                  key={idx}
                  className="bg-[#0D0E10] border border-[#394047] border-l-4 border-l-[#C98255] p-3.5 rounded"
                >
                  <div className="flex justify-between items-center mb-1 flex-wrap gap-2">
                    <span className="font-bold text-[#D4D9DF] text-sm">{d.service}</span>
                    <span className="px-2 py-0.5 bg-[#1B1714] text-[#C98255] border border-[#C98255]/30 rounded text-[10px] font-bold uppercase">
                      {d.badge || 'SIMULATED DISPATCH'}
                    </span>
                  </div>
                  <p className="text-[#999EA5] leading-relaxed">{d.message}</p>
                </div>
              ))
            )}
          </div>
        )}

        {/* FINAL REPORT ───────────────────────────────────────────────────── */}
        {activeTab === 'report' && (
          <div
            className="bg-[#0D0E10] border border-[#394047] border-t-2 border-t-[#C98255] rounded p-4 font-mono text-xs text-[#D4D9DF] whitespace-pre-wrap leading-relaxed overflow-y-auto"
            style={{ maxHeight: '420px' }}
          >
            {inc.report_text || 'GenAI structured incident report will appear here after final analysis.'}
          </div>
        )}

        {/* RAG CONTEXT ────────────────────────────────────────────────────── */}
        {activeTab === 'rag' && (
          <div className="space-y-3 font-mono text-xs">
            {!inc.similar_incidents || inc.similar_incidents.length === 0 ? (
              <div className="text-center text-[#798690] py-6">
                <Database className="w-6 h-6 mx-auto mb-2 text-[#394047]" />
                <p>ChromaDB RAG context not available for this incident.</p>
              </div>
            ) : (
              inc.similar_incidents.map((sim) => (
                <div key={sim.incident_id} className="bg-[#0D0E10] border border-[#394047] p-3.5 rounded">
                  <div className="flex justify-between font-bold text-[#C98255] mb-1 flex-wrap gap-1">
                    <span>#{sim.incident_id} — {sim.type?.toUpperCase()}</span>
                    <span className="text-[#999EA5] font-normal">
                      Severity: {sim.severity} ({sim.severity_score}/100)
                    </span>
                  </div>
                  <div className="text-[11px] text-[#798690] mb-2">📍 {sim.location} | {sim.timestamp}</div>
                  <p className="text-[#D4D9DF] leading-relaxed">{sim.summary}</p>
                </div>
              ))
            )}
          </div>
        )}

        {/* PERFORMANCE & MLFLOW ────────────────────────────────────────────── */}
        {activeTab === 'performance' && (
          <div className="space-y-4 font-mono text-xs">
            {/* System Benchmarks */}
            <div className="bg-[#0D0E10] border border-[#394047] rounded p-4">
              <div className="text-[#C98255] font-bold uppercase mb-3 text-[10px] tracking-wider">System Benchmarks</div>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {[
                  { label: 'Video Duration',    value: `${videoDuration ?? 0}s` },
                  { label: 'Processing Time',   value: `${processingDuration ?? 0}s` },
                  { label: 'Inference FPS',     value: `${aiFps ?? 0} FPS`, highlight: true },
                  { label: 'Display FPS',       value: `${displayFps ?? 0} FPS`, highlight: true },
                  { label: 'Frames Inferred',   value: String(framesProcessed ?? 0) },
                  { label: 'Frames Skipped',    value: String(framesSkipped ?? 0) },
                  { label: 'Total Frames',      value: String(totalFrames ?? 0) },
                  { label: 'Video FPS',         value: String(videoFps ?? 0) },
                  { label: 'Engine',            value: 'YOLOv8n + ByteTrack' },
                ].map(({ label, value, highlight }) => (
                  <div key={label} className="bg-[#141517] border border-[#394047] rounded p-2.5">
                    <div className="text-[10px] text-[#798690] mb-0.5">{label}</div>
                    <div className={`font-bold ${highlight ? 'text-[#C98255]' : 'text-[#D4D9DF]'}`}>{value}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* MLflow Model Comparison */}
            {modelComparison && (
              <div className="bg-[#0D0E10] border border-[#394047] rounded p-4">
                <div className="flex items-center gap-2 mb-3">
                  <Trophy className="w-4 h-4 text-[#55C98A]" />
                  <span className="font-bold text-[#55C98A] text-[10px] uppercase tracking-wider">
                    MLflow Winning Model: {modelComparison.winner}
                  </span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-[11px]">
                    <thead>
                      <tr className="border-b border-[#394047]">
                        {['Model', 'R² Score', 'RMSE', 'Accuracy', 'F1'].map((h) => (
                          <th key={h} className="text-left py-1.5 pr-4 text-[#798690] font-semibold">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(modelComparison.models).map(([name, m]) => (
                        <tr
                          key={name}
                          className={`border-b border-[#1B1D20] ${name === modelComparison.winner ? 'text-[#55C98A]' : 'text-[#999EA5]'}`}
                        >
                          <td className="py-1.5 pr-4 font-bold">{name}</td>
                          <td className="py-1.5 pr-4">{m.r2_score?.toFixed(3)}</td>
                          <td className="py-1.5 pr-4">{m.rmse?.toFixed(3)}</td>
                          <td className="py-1.5 pr-4">{((m.accuracy ?? 0) * 100).toFixed(1)}%</td>
                          <td className="py-1.5 pr-4">{m.f1_weighted?.toFixed(3)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
};
