import os
import subprocess
import time
import json
import shutil
import re

# --- CONFIGURATION ---
REMOTE_PATH = "routerftp:/usb1_1/movies"
DOWNLOAD_DIR = os.path.expanduser("~/temp_downloads")
OUTPUT_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static/videos")
STATUS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "status.json")
DELETE_ORIGINAL_FROM_ROUTER = True
STABILITY_COOLDOWN = 50 
CHECK_INTERVAL = 10 

# --- NEW: Only process these file types ---
VIDEO_EXTENSIONS = ('.mkv', '.mp4', '.avi', '.mov', '.flv', '.wmv')

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)

def get_video_duration(file_path):
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, check=True)
        return float(result.stdout)
    except (subprocess.CalledProcessError, ValueError): return 0

def update_status(status, filename, progress=0):
    status_data = {"status": status, "filename": filename, "progress": progress}
    with open(STATUS_FILE, 'w') as f: json.dump(status_data, f)

def process_video(local_file_path):
    filename = os.path.basename(local_file_path)
    update_status("processing", filename, 0)
    try:
        total_duration = get_video_duration(local_file_path)
        name_without_ext = os.path.splitext(filename)[0]
        clean_name = name_without_ext.lower().replace(' ', '-').replace('.', '-')
        movie_output_dir = os.path.join(OUTPUT_DIRECTORY, clean_name)
        os.makedirs(movie_output_dir, exist_ok=True)
        
        shutil.copy(local_file_path, movie_output_dir)
        print("Generating thumbnail...")
        subprocess.run(['ffmpeg', '-i', local_file_path, '-ss', '00:00:10.000', '-vframes', '1', '-y', os.path.join(movie_output_dir, "thumbnail.jpg")], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print("Converting to HLS...")
        hls_playlist_path = os.path.join(movie_output_dir, "stream.m3u8")
        hls_command = [
            'ffmpeg', '-i', local_file_path, '-y', '-map', '0:v:0', '-map', '0:a:0?', 
            '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', 
            '-ac', '2',
            '-hls_time', '10', 
            '-hls_list_size', '0', '-f', 'hls', '-progress', 'pipe:1', hls_playlist_path
        ]
        process = subprocess.Popen(hls_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        
        for line in process.stdout:
            if 'out_time_ms' in line:
                time_str = line.split('=')[1].strip()
                if time_str != "N/A":
                    current_time_ms = int(time_str)
                    progress = int((current_time_ms / (total_duration * 1000000)) * 100 if total_duration > 0 else 0)
                    print(f"\rEncoding Progress: {progress}%", end="")
                    update_status("processing", filename, progress)
        process.wait()
        print() 

        if process.returncode != 0:
             print(f"FFmpeg failed for {filename} with code {process.returncode}")
             return False

        print(f"Successfully processed {filename}.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error processing {filename}: {e}")
        return False
    finally:
        if os.path.exists(local_file_path):
            os.remove(local_file_path)

def main():
    if os.path.exists(STATUS_FILE): os.remove(STATUS_FILE)
    upload_tracker = {}
    while True:
        current_files_on_remote = {}
        try:
            result = subprocess.run(['rclone', 'lsjson', REMOTE_PATH, '--files-only'], capture_output=True, text=True, check=True)
            remote_files_list = json.loads(result.stdout)
            # --- NEW: Filter for video files only ---
            for item in remote_files_list:
                if item['Path'].lower().endswith(VIDEO_EXTENSIONS):
                    current_files_on_remote[item['Path']] = item['Size']
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            print(f"[{time.ctime()}] Error connecting to router. Retrying...")
            time.sleep(CHECK_INTERVAL)
            continue

        is_upload_active = False
        active_upload_filename = ""
        for filename, size in current_files_on_remote.items():
            if filename not in upload_tracker:
                print(f"\n[{time.ctime()}] New video detected: '{filename}'. Starting to monitor.")
                upload_tracker[filename] = {"size": size, "last_updated": time.time()}
                is_upload_active = True
                active_upload_filename = filename
            elif size > upload_tracker[filename]["size"]:
                print(f"[{time.ctime()}] '{filename}' size gained! Restarting timer.")
                upload_tracker[filename].update({"size": size, "last_updated": time.time()})
                is_upload_active = True
                active_upload_filename = filename
        
        for filename in list(upload_tracker):
            if filename not in current_files_on_remote: del upload_tracker[filename]

        file_to_process = None
        for filename, data in upload_tracker.items():
            if time.time() - data["last_updated"] > STABILITY_COOLDOWN:
                file_to_process = filename
                break
        
        if file_to_process:
            print(f"'{file_to_process}' is stable. Starting download.")
            update_status("downloading", file_to_process, 0)
            remote_path = os.path.join(REMOTE_PATH, file_to_process)
            local_path = os.path.join(DOWNLOAD_DIR, file_to_process)
            
            download_command = ['rclone', 'copyto', remote_path, local_path, '--progress']
            download_process = subprocess.Popen(download_command, stderr=subprocess.PIPE, text=True, encoding='utf-8')
            
            percentage_re = re.compile(r'(\d+)%')
            for line in iter(download_process.stderr.readline, ''):
                match = percentage_re.search(line)
                if match:
                    progress = int(match.group(1))
                    update_status("downloading", file_to_process, progress)
                    print(f"\rDownloading Progress: {progress}%", end="")
            
            download_process.wait()
            print() 

            if os.path.exists(local_path):
                process_success = process_video(local_path)
                del upload_tracker[file_to_process] 
                if process_success and DELETE_ORIGINAL_FROM_ROUTER:
                    print(f"Deleting from router: {remote_path}")
                    subprocess.run(['rclone', 'delete', remote_path])
            else:
                print(f"Download failed for {file_to_process}.")
                del upload_tracker[file_to_process]
        
        elif is_upload_active:
            print(f"Upload in progress for '{active_upload_filename}'. Monitoring...")
            update_status("monitoring", active_upload_filename, 0)
        else:
            print(f"\n[{time.ctime()}] No new activity detected.")
            update_status("idle", "", 0)
            
        print(f"Next check in {CHECK_INTERVAL} seconds...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()

