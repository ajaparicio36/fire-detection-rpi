// src/components/CameraFeed.tsx
import React, { useState } from "react";
import { Camera, CameraOff } from "lucide-react";

interface CameraFeedProps {
  frame: string | null;
  processedFrame: string | null;
  cameraStatus: {
    running: boolean;
    fps: number;
    resolution: {
      width: number;
      height: number;
    };
    detections_count: number;
  };
}

const CameraFeed = ({
  frame,
  processedFrame,
  cameraStatus,
}: CameraFeedProps) => {
  const [showProcessed, setShowProcessed] = useState(false);

  return (
    <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white">Camera Feed</h2>
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setShowProcessed(!showProcessed)}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-md text-white text-sm"
          >
            {showProcessed ? "Show Raw Feed" : "Show Processed Feed"}
          </button>
          <span
            className={`flex items-center ${
              cameraStatus.running ? "text-green-400" : "text-red-400"
            }`}
          >
            {cameraStatus.running ? (
              <Camera size={20} />
            ) : (
              <CameraOff size={20} />
            )}
          </span>
        </div>
      </div>

      <div className="relative aspect-video bg-gray-900 rounded-lg overflow-hidden">
        {(showProcessed ? processedFrame : frame) ? (
          <img
            src={`data:image/jpeg;base64,${
              showProcessed ? processedFrame : frame
            }`}
            alt="Camera feed"
            className="w-full h-full object-contain"
          />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            No feed available
          </div>
        )}
      </div>

      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
        <div className="bg-gray-700 p-3 rounded-lg">
          <p className="text-gray-300">FPS</p>
          <p className="text-white font-medium">
            {cameraStatus.fps.toFixed(1)}
          </p>
        </div>
        <div className="bg-gray-700 p-3 rounded-lg">
          <p className="text-gray-300">Detections</p>
          <p className="text-white font-medium">
            {cameraStatus.detections_count}
          </p>
        </div>
        <div className="bg-gray-700 p-3 rounded-lg col-span-2">
          <p className="text-gray-300">Resolution</p>
          <p className="text-white font-medium">
            {cameraStatus.resolution.width} x {cameraStatus.resolution.height}
          </p>
        </div>
      </div>
    </div>
  );
};

export default CameraFeed;
