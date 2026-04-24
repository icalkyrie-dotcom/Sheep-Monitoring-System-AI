import psutil
import time
import csv
import os

class SystemProfiler:
    def __init__(self, base_folder="logs/performance"):
        self.folder = base_folder
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        timestamp_str = time.strftime("%Y%m%d_%H%M%S")
        self.filename = f"{self.folder}/perf_log_{timestamp_str}.csv"
        self.start_time = time.time()
        self.headers = [
            "timestamp", "uptime_sec", "fps",
            "inference_ms", "cpu_usage_pct",
            "ram_usage_mb", "cpu_temp_c"
        ]
        self._init_csv()
    def _init_csv(self):
        """Fungsi internal untuk menyiapkan struktur file CSV kosong"""
        with open(self.filename, mode='w', newline='') as f:
            
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writeheader()
    def get_cpu_temp(self):
        """
        Membaca suhu prosesor langsung dari sensor termal hardware Raspberry Pi.
        Penting untuk membuktikan sistem tidak mengalami thermal throttling selama 72 jam.
        """
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp = int(f.read()) / 1000.0
                return round(temp, 2)
        except:
            return 0.0
    def log_performance(self, fps, inference_time_sec):
        """
        Pencatatan data performa sistem. 
        Mengekstraksi metrik komputasi dan menyimpannya ke memori fisik (MicroSD).
        """
        try:
            data = {
                "timestamp": time.strftime("%H:%M:%S"),
                "uptime_sec": round(time.time() - self.start_time, 2),
                "fps": round(fps, 2),
                "inference_ms": round(inference_time_sec * 1000, 2),
                "cpu_usage_pct": psutil.cpu_percent(interval=None),
                "ram_usage_mb": round(psutil.Process().memory_info().rss / (1024 * 1024), 2),
                "cpu_temp_c": self.get_cpu_temp()
            }
            with open(self.filename, mode='a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.headers)
                writer.writerow(data)       
        except Exception as e:
            pass