from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

# Ensure we can import from local package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from RedLight.api import (
    GetStatistics,
    GetDownloadHistory,
    GetActiveDownloads,
    StartResumableDownload,
    GetVideoInfo
)

app = Flask(__name__) # Initialize first to access helpers if needed, but we'll override static config

def get_static_folder():
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the PyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app 
        # path into variable _MEIPASS.
        # For 'onedir' mode, we expect assets in the same dir as executable/script
        base_path = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(os.path.abspath(__file__))
        
        # When using --add-data, folders are preserved. 
        # We mapped "gui/client/dist" -> "gui/client/dist"
        return os.path.join(base_path, 'gui', 'client', 'dist')
    else:
        # Normal python execution
        return '../gui/client/dist'

static_folder = get_static_folder()
app = Flask(__name__, static_folder=static_folder, static_url_path='/')
CORS(app)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        stats = GetStatistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/downloads/history', methods=['GET'])
def get_history():
    try:
        limit = int(request.args.get('limit', 10))
        history = GetDownloadHistory(limit=limit)
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/downloads/active', methods=['GET'])
def get_active():
    try:
        active = GetActiveDownloads()
        return jsonify(active)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/download', methods=['POST'])
def start_download():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    try:
        # Start async/resumable download
        download_id = StartResumableDownload(url)
        return jsonify({"success": True, "id": download_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/info', methods=['GET'])
def get_info():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400
    try:
        info = GetVideoInfo(url)
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting RedLight API Server on port 5000...")
    app.run(host='127.0.0.1', port=5000, debug=True)
