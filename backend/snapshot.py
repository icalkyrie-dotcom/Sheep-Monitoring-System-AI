import cv2
import os
import time

class SnapshotManager:
    def __init__(self, save_dir="snapshots", local_retention_hours=2):
        self.save_dir = save_dir
        self.retention_seconds = local_retention_hours * 3600
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            print(f"[INFO] Folder '{self.save_dir}' telah dikonfigurasi.")

    def save(self, frame, label):
        """
        Menyimpan frame visual secara lokal.
        Melampirkan metadata (watermark) sebagai bukti validasi data untuk Bab 4 Skripsi.
        """
        timestamp_file = time.strftime("%Y%m%d-%H%M%S")
        timestamp_ui = time.strftime("%Y-%m-%d %H:%M:%S")
        filename = f"{self.save_dir}/{timestamp_file}_{label}.jpg"
        annotated_frame = frame.copy()
        cv2.putText(annotated_frame, f"Status: {label} | {timestamp_ui}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        success = cv2.imwrite(filename, annotated_frame)
        if success:
            self.cleanup_local()
            return filename
        return None

    def cleanup_local(self):
        """
        Mekanisme Garbage Collection lokal.
        Memindai direktori dan menghapus file yang umurnya melewati retention_seconds.
        """
        try:
            now = time.time()
            count = 0
            for f in os.listdir(self.save_dir):
                file_path = os.path.join(self.save_dir, f)
                if os.path.isfile(file_path):
                    if os.path.getmtime(file_path) < now - self.retention_seconds: 
                        os.remove(file_path)
                        count += 1
            if count > 0:
                print(f"[SNAPSHOT] Cleanup Lokal: {count} foto lama dihapus dari MicroSD.")
        except Exception as e:
            print(f"[SNAPSHOT ERROR] Gagal menjalankan cleanup lokal: {e}")