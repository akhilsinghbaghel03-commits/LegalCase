import threading
import time
import datetime
import cv2
import mss
import numpy as np
import subprocess
import sys

def screen_recorder(stop_event, filename):
    with mss.MSS() as sct:
        monitor = sct.monitors[1]
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(filename, fourcc, 10.0, (monitor["width"], monitor["height"]))
        
        while not stop_event.is_set():
            try:
                img = np.array(sct.grab(monitor))
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                out.write(frame)
            except Exception:
                pass
            time.sleep(0.1)
            
        out.release()

if __name__ == "__main__":
    stop_recording = threading.Event()
    video_filename = f"full_execution_record_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.mp4"
    recording_thread = threading.Thread(target=screen_recorder, args=(stop_recording, video_filename))
    
    print(f"Starting global screen recording to {video_filename}...")
    recording_thread.start()
    
    try:
        # Run run_signup.py
        print("\n\n=== RUNNING: run_signup.py ===")
        subprocess.run([sys.executable, "test/run_signup.py"], check=False)
        
        # Run pytest files in exact sequence requested, generating reports
        print("\n\n=== RUNNING: pytest sequence ===")
        pytest_cmd = [
            sys.executable, "-m", "pytest", 
            "test/test_registration.py", 
            "test/test_forgot_password.py", 
            "test/test_login_scenarios.py", 
            "-v", "-s", 
            "--html=report.html", 
            "--excelreport=report.xlsx"
        ]
        subprocess.run(pytest_cmd, check=False)
        
    finally:
        print(f"\nStopping screen recording...")
        stop_recording.set()
        recording_thread.join()
        print(f"Saved full recording to {video_filename}")
        print("Done!")
