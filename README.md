<div align="center">
  <h1 style="font-size: 3em; font-weight: bold;">📱 PocketPlex</h1>
  <p><strong>Your personal, automated media server, powered by your Android phone.</strong></p>
  <p>
    <img src="https://img.shields.io/badge/Platform-Termux-brightgreen" alt="Platform: Termux">
    <img src="https://img.shields.io/badge/Python-3.11%2B-blue.svg" alt="Python Version">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
  </p>
</div>

<p align="center">
  <img src="img/Screenshot 2025-09-28 135826.png" alt="PocketPlex Interface" width="800">
</p>
<p align="center">
  <img src="img/Screenshot 2025-09-28 135900.png" alt="PocketPlex Interface" width="800">
</p>
<p align="center">
  <img src="img/Screenshot 2025-09-28 140036.png" alt="PocketPlex Interface" width="800">
</p>

## 📋 Table of Contents
- [About The Project](#about-the-project)
- [✨ Key Features](#-key-features)
- [🛠️ Tech Stack](#️-tech-stack)
- [🚀 Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation & Configuration](#installation--configuration)
- [🏗️ How It Works](#-how-it-works)
- [📄 License](#-license)

---

## About The Project
PocketPlex transforms a standard Android phone into a powerful, low-energy media server. It runs 24/7, automatically fetching new video files from a network source (like a router's USB drive), processing them into web-friendly streaming formats, and serving them through a clean, modern web interface accessible from any device on your network.

This project solves the problem of wanting a personal media library like Plex or Jellyfin without needing dedicated server hardware.

---

## ✨ Key Features
- **Fully Automated Pipeline:** Automatically finds, downloads, and processes new media.
- **Efficient HLS Transcoding:** Converts videos to HTTP Live Streaming (HLS) format for fast startups, smooth seeking, and reduced buffering.
- **Dynamic Web UI:** Beautiful and responsive frontend built with Flask and Tailwind CSS.
- **Live Progress Monitoring:** UI shows real-time download and encoding status.
- **Smart Storage Management:** Processes files one-by-one and cleans up original files to save space.
- **Energy Efficient:** Low-power ARM processor usage keeps your server always-on without high electricity costs.

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| Backend  | ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white) |
| Frontend | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white) ![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?logo=tailwind-css&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black) |
| Core Tools | Termux (Android Environment), rclone (File Sync), ffmpeg (Video Processing) |

---

## 🚀 Getting Started

### Prerequisites
- Android phone with Termux installed.
- Network-accessible file source (e.g., router with FTP server and USB drive).
- Basic familiarity with command line.

### Installation & Configuration

1. **Clone the repository**
```bash
git clone https://github.com/Brezzeyboi/PocketPlex.git
cd PocketPlex
```

2. **Install Termux dependencies**
```bash
pkg update && pkg upgrade -y
pkg install python ffmpeg rclone root-repo
pkg install libfuse
```

3. **Install Python libraries**
```bash
pip install Flask
```

4. **Configure rclone**
```bash
rclone config
```
- Create a new remote (name it `routerftp` or similar).
- Select FTP type and enter your router's IP, username, and password.

5. **Configure the Media Processor**
- Open `media_processor.py` and set `REMOTE_PATH` to your rclone remote:
```python
REMOTE_PATH = "routerftp:/usb1_1/movies"  # IMPORTANT: Change this path:
# for example name you kept for the connection in roclone:/ -> this if
# the movies are present in to root if in a folder then name:/folder .