// src/utils/socket.ts
import { io } from "socket.io-client";

const SOCKET_URL = `http://192.168.1.12:5000`;

export const socket = io(SOCKET_URL, {
  transports: ["websocket"],
  reconnectionDelay: 1000,
  reconnection: true,
  reconnectionAttempts: 10,
  agent: false,
  upgrade: false,
  rejectUnauthorized: false,
});

export const connectSocket = () => {
  if (!socket.connected) {
    socket.connect();
  }
};

export const disconnectSocket = () => {
  if (socket.connected) {
    socket.disconnect();
  }
};
