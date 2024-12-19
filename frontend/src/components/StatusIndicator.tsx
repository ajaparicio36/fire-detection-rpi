import React from "react";
import {
  Bell,
  BellOff,
  AlertTriangle,
  AlertOctagon,
  Clock,
} from "lucide-react";

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

const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  enabled,
  active,
  lastEvent,
  onToggle,
  onAlarmControl,
}) => {
  return (
    <div className="bg-gray-800 rounded-lg p-6 shadow-lg border border-gray-700 hover:border-blue-500 transition-all duration-300">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600">
          System Status
        </h2>
        <div className="flex space-x-4">
          <button
            onClick={() => onToggle(!enabled)}
            className={`p-3 rounded-full transition-colors duration-300 ${
              enabled
                ? "bg-green-600 hover:bg-green-700"
                : "bg-red-600 hover:bg-red-700"
            }`}
            title={enabled ? "Disable System" : "Enable System"}
          >
            {enabled ? (
              <Bell className="text-white" size={24} />
            ) : (
              <BellOff className="text-white" size={24} />
            )}
          </button>
          {enabled && (
            <button
              onClick={() => onAlarmControl(!active)}
              className={`p-3 rounded-full transition-colors duration-300 ${
                active
                  ? "bg-red-600 hover:bg-red-700"
                  : "bg-yellow-600 hover:bg-yellow-700"
              }`}
              title={active ? "Deactivate Alarm" : "Activate Alarm"}
            >
              {active ? (
                <AlertOctagon className="text-white" size={24} />
              ) : (
                <AlertTriangle className="text-white" size={24} />
              )}
            </button>
          )}
        </div>
      </div>
      <div className="space-y-6">
        <div className="flex items-center justify-between bg-gray-700 p-4 rounded-lg hover:bg-gray-600 transition-colors duration-300">
          <span className="text-gray-300">System Enabled</span>
          <span
            className={`text-lg font-bold ${
              enabled ? "text-green-400" : "text-red-400"
            }`}
          >
            {enabled ? "YES" : "NO"}
          </span>
        </div>
        <div className="flex items-center justify-between bg-gray-700 p-4 rounded-lg hover:bg-gray-600 transition-colors duration-300">
          <span className="text-gray-300">Alarm Status</span>
          <span
            className={`text-lg font-bold ${
              active ? "text-red-400 animate-pulse" : "text-green-400"
            }`}
          >
            {active ? "ACTIVE" : "Inactive"}
          </span>
        </div>
        {lastEvent.timestamp && (
          <div className="mt-6 p-4 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors duration-300">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center">
              <Clock className="mr-2" size={20} />
              Last Event
            </h3>
            <div className="space-y-3 text-sm">
              <p className="text-gray-300 flex justify-between">
                Type:{" "}
                <span className="text-white font-medium">{lastEvent.type}</span>
              </p>
              <p className="text-gray-300 flex justify-between">
                Source:{" "}
                <span className="text-white font-medium">
                  {lastEvent.source}
                </span>
              </p>
              <p className="text-gray-300 flex justify-between">
                Time:{" "}
                <span className="text-white font-medium">
                  {lastEvent.timestamp
                    ? new Date(lastEvent.timestamp).toLocaleString()
                    : "N/A"}
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
