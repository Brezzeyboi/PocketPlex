from flask import Flask, render_template, jsonify
import os
import json

app = Flask(__name__)

# Define paths relative to the app's location
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
VIDEOS_DIR = os.path.join(APP_ROOT, 'static/videos')
STATUS_FILE = os.path.join(APP_ROOT, 'status.json')

@app.route('/')
def index():
    """Serves the main library page."""
    return render_template('index.html')

@app.route('/video/<movie_id>')
def video_player(movie_id):
    """Serves the video player page."""
    return render_template('video.html', movie_id=movie_id)

@app.route('/api/movies')
def get_movies_list():
    """API endpoint that scans the videos directory and returns a list of all movies."""
    movies = []
    if not os.path.exists(VIDEOS_DIR):
        return jsonify([])

    for movie_id in sorted(os.listdir(VIDEOS_DIR), reverse=True): 
        movie_path = os.path.join(VIDEOS_DIR, movie_id)
        if os.path.isdir(movie_path):
            thumbnail = os.path.join(movie_id, 'thumbnail.jpg')
            stream = os.path.join(movie_id, 'stream.m3u8')
            

            if os.path.exists(os.path.join(VIDEOS_DIR, thumbnail)) and os.path.exists(os.path.join(VIDEOS_DIR, stream)):
                title = movie_id.replace('-', ' ').title()
                movies.append({
                    'id': movie_id,
                    'title': title,
                    'category': 'Recently Added',
                    'backdrop': f'/static/videos/{thumbnail}',
                    'stream_url': f'/static/videos/{stream}',
                    'year': 2025,
                    'director': 'Unknown',
                    'description': f'Description for {title}.'
                })
    return jsonify(movies)

@app.route('/api/status')
def get_status():
    """API endpoint to check the current processing status."""
    try:
        with open(STATUS_FILE, 'r') as f:
            return jsonify(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify({"status": "idle", "filename": "", "progress": 0})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)