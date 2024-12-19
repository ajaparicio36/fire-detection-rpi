// src/components/StatusIndicator.tsx
import React from "react";
import { Bell, BellOff, AlertTriangle, AlertOctagon } from "lucide-react";

interface StatusIndicatorProps {
  enabled: boolean;
  active: boolean;
  lastEvent: {
    timestamp: string | null;
    type: string | null;
    source: string | null;
    active: boolean | null;
  };
  onToggle: (enabled: boolean) => void;
  onAlarmControl: (active: boolean) => void;
}

const StatusIndicator = ({
  enabled,
  active,
  lastEvent,
  onToggle,
  onAlarmControl,
}: StatusIndicatorProps) => {
  return (
    <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white">System Status</h2>
        <div className="flex space-x-4">
          <button
            onClick={() => onToggle(!enabled)}
            className={`p-2 rounded-full ${
              enabled
                ? "bg-green-600 hover:bg-green-700"
                : "bg-red-600 hover:bg-red-700"
            }`}
            title={enabled ? "Disable System" : "Enable System"}
          >
            {enabled ? (
              <Bell className="text-white" />
            ) : (
              <BellOff className="text-white" />
            )}
          </button>
          {enabled && (
            <button
              onClick={() => onAlarmControl(!active)}
              className={`p-2 rounded-full ${
                active
                  ? "bg-red-600 hover:bg-red-700"
                  : "bg-yellow-600 hover:bg-yellow-700"
              }`}
              title={active ? "Deactivate Alarm" : "Activate Alarm"}
            >
              {active ? (
                <AlertOctagon className="text-white" />
              ) : (
                <AlertTriangle className="text-white" />
              )}
            </button>
          )}
        </div>
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-gray-300">System Enabled</span>
          <span
            className={`text-sm font-medium ${
              enabled ? "text-green-400" : "text-red-400"
            }`}
          >
            {enabled ? "Yes" : "No"}
          </span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-gray-300">Alarm Status</span>
          <span
            className={`text-sm font-medium ${
              active ? "text-red-400 animate-pulse" : "text-green-400"
            }`}
          >
            {active ? "ACTIVE" : "Inactive"}
          </span>
        </div>

        {lastEvent.timestamp && (
          <div className="mt-4 p-4 bg-gray-700 rounded-lg">
            <h3 className="text-white font-medium mb-2">Last Event</h3>
            <div className="space-y-2 text-sm">
              <p className="text-gray-300">
                Type: <span className="text-white">{lastEvent.type}</span>
              </p>
              <p className="text-gray-300">
                Source: <span className="text-white">{lastEvent.source}</span>
              </p>
              <p className="text-gray-300">
                Time:{" "}
                <span className="text-white">
                  {new Date(lastEvent.timestamp).toLocaleString()}
                </span>
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StatusIndicator;
