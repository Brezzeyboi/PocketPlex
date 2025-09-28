import os
import subprocess
import time
import json

# --- CONFIGURATION ---
REMOTE_PATH = "routerftp:/usb1_1/movies"
DOWNLOAD_DIR = os.path.expanduser("~/temp_downloads")
OUTPUT_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static/videos")
STATUS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "status.json")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)

def get_video_duration(file_path):
    """Gets the duration of a video file in seconds."""
    cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', file_path
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, check=True)
        return float(result.stdout)
    except (subprocess.CalledProcessError, ValueError):
        return 0

def update_status(status, filename, progress=0):
    """Writes the current status to the status file."""
    status_data = {"status": status, "filename": filename, "progress": progress}
    with open(STATUS_FILE, 'w') as f:
        json.dump(status_data, f)

def process_video(local_file_path):
    """Processes a single, locally downloaded video file."""
    filename = os.path.basename(local_file_path)
    update_status("processing", filename, 0)
    try:
        print(f"Processing: {filename}")
        total_duration = get_video_duration(local_file_path)
        name_without_ext = os.path.splitext(filename)[0]
        clean_name = name_without_ext.lower().replace(' ', '-').replace('.', '-')
        movie_output_dir = os.path.join(OUTPUT_DIRECTORY, clean_name)
        os.makedirs(movie_output_dir, exist_ok=True)

        print("Generating thumbnail...")
        subprocess.run([
            'ffmpeg', '-i', local_file_path, '-ss', '00:00:10.000',
            '-vframes', '1', '-y', os.path.join(movie_output_dir, "thumbnail.jpg")
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print("Converting to HLS...")
        hls_playlist_path = os.path.join(movie_output_dir, "stream.m3u8")
        hls_command = [
            'ffmpeg', '-i', local_file_path, '-y', '-c:v', 'copy', '-c:a', 'aac',
            '-hls_time', '10', '-hls_list_size', '0', '-f', 'hls',
            '-progress', 'pipe:1', hls_playlist_path
        ]
        process = subprocess.Popen(hls_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        
        for line in process.stdout:
            if 'out_time_ms' in line:
                time_str = line.split('=')[1].strip()
                try:
                    current_time_ms = int(time_str)
                    if total_duration > 0:
                        progress = (current_time_ms / (total_duration * 1000000)) * 100
                        update_status("processing", filename, int(progress))
                except ValueError:
                    pass
        process.wait()
        
        if process.returncode != 0:
            print(f"FFmpeg failed with return code {process.returncode}")
            return False

        print(f"Successfully processed {filename}.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during thumbnail generation for {filename}: {e}")
        return False
    finally:
        print(f"Cleaning up local file: {local_file_path}")
        if os.path.exists(local_file_path):
            os.remove(local_file_path)

def main():
    """Main loop to check for and process new videos one by one."""
    if os.path.exists(STATUS_FILE):
        os.remove(STATUS_FILE)

    while True:
        print(f"[{time.ctime()}] Checking for new movies on the router...")
        update_status("idle", "Checking for new files...", 0)

        try:
            result = subprocess.run(
                ['rclone', 'lsf', REMOTE_PATH, '--files-only'],
                capture_output=True, text=True, check=True
            )
            files_on_remote = result.stdout.strip().split('\n')
            if not files_on_remote or files_on_remote == ['']:
                 files_on_remote = []
        except subprocess.CalledProcessError as e:
            print(f"Error listing files on remote: {e.stderr}")
            files_on_remote = []
        
        if not files_on_remote:
            print("No new files to process.")
        else:
            filename_to_process = files_on_remote[0]
            print(f"Found new file to process: {filename_to_process}")
            
            update_status("downloading", filename_to_process, 0)
            remote_file_path = os.path.join(REMOTE_PATH, filename_to_process)
            local_file_path = os.path.join(DOWNLOAD_DIR, filename_to_process)
            
            print(f"Downloading {filename_to_process}...")
            subprocess.run(['rclone', 'copyto', remote_file_path, local_file_path, '--progress'])
            
            if os.path.exists(local_file_path):
                if process_video(local_file_path):
                    print(f"Deleting original file from router: {remote_file_path}")
                    subprocess.run(['rclone', 'delete', remote_file_path])
            else:
                print(f"Download failed for {filename_to_process}, file not found locally.")

        update_status("idle", "", 0)
        print(f"Check complete. Sleeping for 30 seconds...")
        time.sleep(30)

if __name__ == "__main__":
    main()
