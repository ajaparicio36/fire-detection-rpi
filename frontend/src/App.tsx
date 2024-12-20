import React, { useEffect, useState } from "react";
import { socket } from "./utils/socket";
import StatusIndicator from "./components/StatusIndicator";
import CameraFeed from "./components/CameraFeed";
import { Sparkles } from "lucide-react";

interface Status {
  enabled: boolean;
  active: boolean;
  last_event: {
    timestamp: string | null;
    type: string | null;
    source: string | null;
    active: boolean | null;
  };
  camera: {
    running: boolean;
    fps: number;
    resolution: {
      width: number;
      height: number;
    };
    detections_count: number;
  };
}

const App = () => {
  const [status, setStatus] = useState<Status>({
    enabled: false,
    active: false,
    last_event: {
      timestamp: null,
      type: null,
      source: null,
      active: null,
    },
    camera: {
      running: false,
      fps: 0,
      resolution: {
        width: 0,
        height: 0,
      },
      detections_count: 0,
    },
  });
  const [frame, setFrame] = useState<string | null>(null);
  const [processedFrame, setProcessedFrame] = useState<string | null>(null);

  useEffect(() => {
    socket.on("status_update", (newStatus: Status) => {
      setStatus(newStatus);
    });
    socket.on(
      "frame_update",
      (data: { frame: string; processed_frame: string }) => {
        setFrame(data.frame);
        setProcessedFrame(data.processed_frame);
      }
    );

    return () => {
      socket.off("status_update");
      socket.off("frame_update");
    };
  }, []);

  const handleToggleEnabled = (enabled: boolean) => {
    socket.emit("set_enabled", enabled);
  };

  const handleAlarmControl = (active: boolean) => {
    socket.emit("control_alarm", active);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 p-6 text-white">
      <div className="max-w-7xl mx-auto space-y-8">
        <header className="flex items-center justify-between">
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600">
            Fire Monitoring System
          </h1>
          <Sparkles className="text-yellow-400 animate-pulse" size={32} />
        </header>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <StatusIndicator
            enabled={status.enabled}
            active={status.active}
            lastEvent={status.last_event}
            onToggle={handleToggleEnabled}
            onAlarmControl={handleAlarmControl}
          />
          <CameraFeed
            frame={frame}
            processedFrame={processedFrame}
            cameraStatus={status.camera}
          />
        </div>
      </div>
    </div>
  );
};

export default App;
