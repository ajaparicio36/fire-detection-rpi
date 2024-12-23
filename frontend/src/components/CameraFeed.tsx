import React, { useState, useEffect } from "react";
import { Camera, CameraOff, Eye, EyeOff } from "lucide-react";

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

const CameraFeed: React.FC<CameraFeedProps> = ({
  cameraStatus,
  frame,
  processedFrame,
}) => {
  const [showProcessed, setShowProcessed] = useState(true);
  const [imageLoadError, setImageLoadError] = useState(false);

  // Reset image load error when frames change
  useEffect(() => {
    setImageLoadError(false);
  }, [frame, processedFrame]);

  // Helper to determine if we have valid frame data
  const hasValidFrame = (frame: string | null): boolean => {
    return Boolean(frame && frame.length > 0);
  };

  // Handle image load errors
  const handleImageError = () => {
    setImageLoadError(true);
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 shadow-lg border border-gray-700 hover:border-blue-500 transition-all duration-300">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600">
          Camera Feed
        </h2>
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setShowProcessed(!showProcessed)}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-md text-white text-sm flex items-center space-x-2 transition-colors duration-300"
            disabled={!cameraStatus.running}
          >
            {showProcessed ? <Eye size={16} /> : <EyeOff size={16} />}
            <span>
              {showProcessed ? "Show Raw Feed" : "Show Processed Feed"}
            </span>
          </button>
          <span
            className={`flex items-center ${
              cameraStatus.running ? "text-green-400" : "text-red-400"
            }`}
            title={cameraStatus.running ? "Camera Active" : "Camera Inactive"}
          >
            {cameraStatus.running ? (
              <Camera size={24} className="animate-pulse" />
            ) : (
              <CameraOff size={24} />
            )}
          </span>
        </div>
      </div>

      <div className="relative aspect-video bg-gray-900 rounded-lg overflow-hidden border-2 border-gray-700">
        {cameraStatus.running &&
        !imageLoadError &&
        hasValidFrame(showProcessed ? processedFrame : frame) ? (
          <img
            src={`data:image/jpeg;base64,${
              showProcessed ? processedFrame : frame
            }`}
            alt="Camera feed"
            className="w-full h-full object-contain"
            onError={handleImageError}
          />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500 flex-col">
            <CameraOff size={48} className="mb-2" />
            <p>
              {!cameraStatus.running
                ? "Camera is not running"
                : imageLoadError
                ? "Error loading camera feed"
                : "No feed available"}
            </p>
          </div>
        )}
      </div>

      <div className="mt-6 grid grid-cols-2 gap-4 text-sm">
        <div className="bg-gray-700 p-4 rounded-lg hover:bg-gray-600 transition-colors duration-300">
          <p className="text-gray-300 mb-1">FPS</p>
          <p className="text-2xl font-bold text-white">
            {cameraStatus.running ? cameraStatus.fps.toFixed(1) : "0.0"}
          </p>
        </div>
        <div className="bg-gray-700 p-4 rounded-lg hover:bg-gray-600 transition-colors duration-300">
          <p className="text-gray-300 mb-1">Detections</p>
          <p className="text-2xl font-bold text-white">
            {cameraStatus.detections_count}
          </p>
        </div>
        <div className="bg-gray-700 p-4 rounded-lg col-span-2 hover:bg-gray-600 transition-colors duration-300">
          <p className="text-gray-300 mb-1">Resolution</p>
          <p className="text-2xl font-bold text-white">
            {cameraStatus.resolution.width} x {cameraStatus.resolution.height}
          </p>
        </div>
      </div>
    </div>
  );
};

export default CameraFeed;
