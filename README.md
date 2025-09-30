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

<div style="background:#f5f5f5; border-radius:12px; padding:20px; margin:20px 0;">
<h2>📋 Table of Contents</h2>
<ul>
<li>About The Project</li>
<li>✨ Key Features</li>
<li>🛠️ Tech Stack</li>
<li>🚀 Getting Started
  <ul>
    <li>Prerequisites</li>
    <li>Installation & Configuration</li>
    <li>Running 24/7</li>
  </ul>
</li>
<li>🏗️ How It Works</li>
<li>📄 License</li>
</ul>
</div>

<div style="background:#e0f7fa; border-radius:12px; padding:20px; margin:20px 0;">
<h2>About The Project</h2>
<p>PocketPlex transforms a standard Android phone into a powerful, low-energy media server. It runs 24/7, automatically fetching new video files from a network source (like a router's USB drive), processing them into web-friendly streaming formats, and serving them through a clean, modern web interface accessible from any device on your network.</p>
<p>This project solves the problem of wanting a personal media library like Plex or Jellyfin without needing dedicated server hardware.</p>
</div>

<div style="background:#fff3e0; border-radius:12px; padding:20px; margin:20px 0;">
<h2>✨ Key Features</h2>
<ul>
<li><strong>Fully Automated Pipeline:</strong> Automatically finds, downloads, and processes new media.</li>
<li><strong>Efficient HLS Transcoding:</strong> Converts videos to HTTP Live Streaming (HLS) format for fast startups, smooth seeking, and reduced buffering.</li>
<li><strong>Dynamic Web UI:</strong> Beautiful and responsive frontend built with Flask and Tailwind CSS.</li>
<li><strong>Live Progress Monitoring:</strong> UI shows real-time download and encoding status.</li>
<li><strong>Smart Storage Management:</strong> Processes files one-by-one and cleans up original files to save space.</li>
<li><strong>Energy Efficient:</strong> Low-power ARM processor usage keeps your server always-on without high electricity costs.</li>
</ul>
</div>

<div style="background:#e8f5e9; border-radius:12px; padding:20px; margin:20px 0;">
<h2>🛠️ Tech Stack</h2>
<table>
<tr><td><strong>Backend</strong></td><td><img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white">  <img src="https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white"></td></tr>
<tr><td><strong>Frontend</strong></td><td><img src="https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white"> <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?logo=tailwind-css&logoColor=white"> <img src="https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black"></td></tr>
<tr><td><strong>Core Tools</strong></td><td><img src="https://img.shields.io/badge/Termux-black"> <img src="https://img.shields.io/badge/Rclone-blue"> <img src="https://img.shields.io/badge/FFmeg-green"></td></tr>
</table>
</div>

<div style="background:#fce4ec; border-radius:12px; padding:20px; margin:20px 0;">
<h2>🚀 Getting Started</h2>

<h3>Prerequisites</h3>
<ul>
<li>Android phone with Termux installed</li>
<li>Network-accessible file source (router with FTP + USB)</li>
<li>Basic command line familiarity</li>
</ul>

<h3>Installation & Configuration</h3>
<pre>
git clone https://github.com/Brezzeyboi/PocketPlex.git
cd PocketPlex

pkg update && pkg upgrade -y
pkg install python ffmpeg rclone root-repo
pkg install libfuse

pip install Flask

rclone config

 <strong>Create a remote (e.g., routerftp) and connect to your router USB</stronge>
</pre>

<h3>Running 24/7</h3>
<p>To make PocketPlex run all the time:</p>
<ol>
<li><strong>Wake the device:</strong> <code>termux-wake-lock</code></li>
<li><strong>Start the web server:</strong> <code>python app.py</code> (access via browser: <code>http://&lt;your-phone-ip&gt;:8000</code>)</li>
<li><strong>Start media processor:</strong> Swipe left → New session → <code>cd PocketPlex</code> → <code>python media_processor.py</code></li>
<li><strong>Upload new movies:</strong> Use CX File Explorer (phone) or WinSCP (PC). Connect using router IP, username, password, port 21. Drop movies in the folder you set in <code>REMOTE_PATH</code>.</li>
</ol>
</div>

<div style="background:#fffde7; border-radius:12px; padding:20px; margin:20px 0;">
<h2>🏗️ How It Works</h2>
<p>[Router with New Movie] → [media_processor.py (rclone sync)] → [Phone Temp Storage] → [ffmpeg (transcode)] → [static/videos] → [app.py (Flask API)] → [Web Browser]</p>

<ul>
<li><strong>Check:</strong> media_processor.py reads config.json and lists files</li>
<li><strong>Download:</strong> First new file → temp directory</li>
<li><strong>Process:</strong> ffmpeg generates thumbnail + HLS, updates status.json</li>
<li><strong>Serve:</strong> app.py serves processed files, live UI updates</li>
<li><strong>Clean Up:</strong> Deletes original from router and temp from phone</li>
</ul>
</div>

<div style="background:#e1f5fe; border-radius:12px; padding:20px; margin:20px 0;">
<h2>📄 License</h2>
<p>Distributed under the MIT License.</p>
</div>
