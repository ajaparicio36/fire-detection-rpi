# 🔥 Smart Fire Detection System 🚨

A distributed fire detection system using Raspberry Pi, YOLOv5, and React. Features real-time fire detection through computer vision and hardware smoke detection.

## 🌟 Features

- 🎥 Real-time fire detection using YOLOv5
- 💨 Hardware smoke detection
- 🚨 Configurable alarm system
- 📱 Web dashboard for monitoring and control
- 🔄 Real-time updates using Socket.IO
- 🛡️ Distributed architecture for better performance

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌────────────────┐
│   AI Service    │◄───┤   RPi Server     │◄───┤    Frontend    │
│  (YOLOv5 Model) │    │  (GPIO + Camera) │    │  (React + UI)  │
└─────────────────┘    └──────────────────┘    └────────────────┘
```

## 🛠️ Prerequisites

- Raspberry Pi 3B or better
- Python 3.8+
- Node.js 16+
- Web camera
- Smoke detector (GPIO compatible)
- Alarm bell/buzzer
- High-performance computer for AI service

## 📥 Installation

### 1️⃣ AI Service Setup

```bash
# Clone repository
git clone <repository-url>
cd fire-detection-system/ai-service

# Create and activate virtual environment
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Start AI service
python model_server.py
```

### 2️⃣ RPi Server Setup

```bash
cd fire-detection-system/rpi-server

# Create and activate virtual environment
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Start server
python server.py
```

### 3️⃣ Frontend Setup

```bash
cd fire-detection-system/frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## 🌐 Static IP Configuration

### Windows

1. Open Network Settings:
   ```
   Windows Key + R -> ncpa.cpl
   ```
2. Right-click your network adapter -> Properties
3. Select "Internet Protocol Version 4 (TCP/IPv4)" -> Properties
4. Use these settings:
   ```
   IP address: 192.168.1.10
   Subnet mask: 255.255.255.0
   Default gateway: 192.168.1.1
   DNS: 8.8.8.8, 8.8.4.4
   ```

### Raspberry Pi OS (Linux)

#### Method 1: For newer versions (using dhcpcd)
1. Edit dhcpcd configuration:
   ```bash
   sudo nano /etc/dhcpcd.conf
   ```

2. Add these lines:
   ```bash
   interface eth0  # or wlan0 for WiFi
   static ip_address=192.168.1.11/24
   static routers=192.168.1.1
   static domain_name_servers=8.8.8.8 8.8.4.4
   ```

3. Restart networking:
   ```bash
   sudo service dhcpcd restart
   ```

#### Method 2: For older versions (using interfaces)
1. Edit the interfaces file:
   ```bash
   sudo nano /etc/network/interfaces
   ```

2. Add these lines for Ethernet (eth0):
   ```bash
   auto eth0
   iface eth0 inet static
       address 192.168.1.11
       netmask 255.255.255.0
       gateway 192.168.1.1
       dns-nameservers 8.8.8.8 8.8.4.4
   ```

   Or for WiFi (wlan0):
   ```bash
   auto wlan0
   iface wlan0 inet static
       address 192.168.1.11
       netmask 255.255.255.0
       gateway 192.168.1.1
       dns-nameservers 8.8.8.8 8.8.4.4
       wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf
   ```

3. Restart networking:
   ```bash
   sudo /etc/init.d/networking restart
   ```

4. If using WiFi, make sure your WiFi credentials are in `/etc/wpa_supplicant/wpa_supplicant.conf`:
   ```bash
   sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
   ```
   Add:
   ```
   network={
       ssid="Your_WiFi_Name"
       psk="Your_WiFi_Password"
   }
   ```

## 📌 GPIO Pin Configuration

- Smoke Detector: GPIO 17 (Physical Pin 11)
- Alarm Bell: GPIO 18 (Physical Pin 12)

## 🚀 Usage

1. Start AI Service on your high-performance computer
2. Start RPi Server on your Raspberry Pi
3. Start Frontend application
4. Access the dashboard at `http://localhost:5173`

## 🔧 Configuration

Default ports:
- AI Service: 5001
- RPi Server: 5000
- Frontend: 5173

Update the connection settings in:
- `ai-service/config.py`
- `rpi-server/config.py`
- `frontend/src/config.ts`

## 🔍 System Monitoring

Access the dashboard to:
- 👀 View real-time camera feed
- 📊 Monitor smoke detector status
- 🔄 Check system uptime
- 🎛️ Control alarm system
- 📝 View event logs

## ⚠️ Troubleshooting

1. **Camera not detected**
   ```bash
   # Check camera
   v4l2-ctl --list-devices
   ```

2. **GPIO Permission Issues**
   ```bash
   # Add user to gpio group
   sudo usermod -a -G gpio $USER
   ```

3. **Network Connectivity**
   ```bash
   # Test connections
   ping 192.168.1.10
   ping 192.168.1.11
   ```

## 🛟 Support

For issues and feature requests, please open an issue in the repository.

## 📜 License

MIT License - feel free to use in your projects!