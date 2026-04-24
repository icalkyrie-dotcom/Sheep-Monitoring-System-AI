import time
import sys
import csv
import os

from vision import SheepVision
from state_manager import StateManager
from snapshot import SnapshotManager
from mqtt_handler import MQTTHandler
from health_logic import HealthLogic
from firebase_handler import FirebaseHandler
from profiler import SystemProfiler

MODEL_PATH      = "models/bebeee.pt"   
CONF_THRESHOLD  = 0.50                
SAMPLE_INTERVAL = 1                   
FIREBASE_DELAY  = 10                  

CLEANUP_DELAY   = 3600                
RETENTION_HOURS = 72                  

BROKER_IP       = "YOUR_MQTT_BROKER_IP"   
LOG_FILE        = "data_monitoring.csv"
FB_KEY          = "firebase_key.json"

class SheepMonitoringSystem:
    def __init__(self):
        try:
            self.vision        = SheepVision(MODEL_PATH, CONF_THRESHOLD)
            self.state_manager = StateManager()
            self.snapshot      = SnapshotManager()
            self.logic         = HealthLogic()
            self.profiler      = SystemProfiler()
            self.mqtt_node     = MQTTHandler(broker=BROKER_IP)
            self.fb_node       = FirebaseHandler(FB_KEY)
            self.mqtt_node.start()
            self.last_sample_time = 0
            self.last_fb_time     = 0
            self.last_cleanup_time = time.time() 
            print("\n" + "="*55)
            print(" [SISTEM MONITORING DEPLOYMENT - INTERVAL 10S] ".center(55, "="))
            print("="*55 + "\n")
        except Exception as e:
            print(f"[ERROR KRITIKAL] Gagal memulai sistem: {e}")
            sys.exit(1)

    def save_research_log(self, data):
        """Menyimpan data mentah ke CSV lokal untuk analisis Bab 4"""
        file_exists = os.path.isfile(LOG_FILE)
        with open(LOG_FILE, mode='a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            if not file_exists: writer.writeheader()
            writer.writerow(data)

    def run(self):
        try:
            while True:
                now = time.time()

                if now - self.last_sample_time < SAMPLE_INTERVAL:
                    time.sleep(0.05)
                    continue
                self.last_sample_time = now

                start_inf = time.time()
                frame = self.vision.read_frame()
                if frame is None: continue

                detected = self.vision.detect_state(frame)
                state_changed = self.state_manager.update(detected)
                
                inf_time = time.time() - start_inf
                current_fps = 1.0 / inf_time if inf_time > 0 else 0
                self.profiler.log_performance(current_fps, inf_time)

                t_body  = self.mqtt_node.body_temp
                t_env   = self.mqtt_node.env_temp
                h_env   = self.mqtt_node.humidity
                nh3_val = self.mqtt_node.nh3
                curr_state = self.state_manager.current_state
                t_sensor = self.mqtt_node.last_update_time or now 
                sync_delay_ms = (now - t_sensor) * 1000

                s_pct, l_pct = self.state_manager.get_percentages()
                fase         = self.state_manager.get_monitoring_phase()
                health_status = self.logic.evaluate(t_body, l_pct, fase)

                time_to_sync = (now - self.last_fb_time >= FIREBASE_DELAY)
                
                if time_to_sync or state_changed or health_status == "ABNORMAL":
                    self.fb_node.update_dashboard(
                        fase, t_body, l_pct, health_status, 
                        t_env, h_env, nh3_val, curr_state
                    )
                    
                    path_lokal = self.snapshot.save(frame, f"{health_status}_{curr_state}")
                    if path_lokal:
                        self.fb_node.upload_snapshot_and_log(path_lokal, health_status, curr_state)
                    
                    self.last_fb_time = now

                if now - self.last_cleanup_time >= CLEANUP_DELAY:
                    print(f"\n[SYSTEM] {time.strftime('%H:%M:%S')} - Menjalankan Rolling Deletion 72 Jam...")
                    self.fb_node.cleanup_old_data(retention_hours=RETENTION_HOURS)
                    self.last_cleanup_time = now
                self.save_research_log({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "ai_state": curr_state,
                    "sync_delay_ms": round(sync_delay_ms, 2),
                    "t_body": t_body if t_body else 0,
                    "nh3": nh3_val if nh3_val else 0,
                    "status": "SINKRON" if sync_delay_ms < 1000 else "DELAY"
                })

                self.update_terminal(fase, current_fps, t_body, health_status, curr_state)

        except KeyboardInterrupt:
            print("\n[STOP] Mematikan sistem secara aman...")
        except Exception as e:
            print(f"\n[FATAL ERROR] Sistem berhenti: {e}")
        finally:
            self.mqtt_node.stop()
            self.vision.cap.release()

    def update_terminal(self, fase, fps, t_body, health, state):
        """Mencetak status sebaris di terminal secara dinamis (tanpa spam baris baru)"""
        sys.stdout.write("\033[K") 
        t_str = f"{t_body:.1f}C" if t_body else "WAIT"
        act_str = "BERAKTIVITAS" if state == "standing" else "ISTIRAHAT"
        output = f"\r[{fase}] | FPS: {fps:.1f} | Body: {t_str} | Act: {act_str} | Health: {health}"
        sys.stdout.write(output)
        sys.stdout.flush()

if __name__ == "__main__":
    monitor = SheepMonitoringSystem()
    monitor.run()