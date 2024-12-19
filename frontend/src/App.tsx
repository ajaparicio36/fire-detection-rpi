import React, { useEffect, useState } from "react";
import { socket } from "./utils/socket";
import StatusIndicator from "./components/StatusIndicator";
import CameraFeed from "./components/CameraFeed";

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
    socket.on("status_update", (newStatus) => {
      setStatus(newStatus);
    });

    socket.on("frame_update", (data) => {
      setFrame(data.frame);
      setProcessedFrame(data.processed_frame);
    });

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
    // Added proper Tailwind classes for dark theme
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold text-white">
          Security Monitoring System
        </h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
