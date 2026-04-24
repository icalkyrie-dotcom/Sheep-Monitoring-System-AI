import cv2
from ultralytics import YOLO

class SheepVision:
    def __init__(self, model_path, conf=0.4):
        print(f"Loading YOLO model dari: {model_path}")
        self.model = YOLO(model_path)
        self.conf = conf
        self.cap = self.init_camera()
    def init_camera(self):
        """Inisialisasi hardware kamera dengan konfigurasi efisiensi daya RPi"""
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        return cap

    def reconnect_camera(self):
        """Prosedur auto-recovery jika koneksi kamera terputus secara fisik"""
        print("[VISION] Mencoba menghubungkan ulang kamera...")
        if self.cap:
            self.cap.release()
        self.cap = self.init_camera()

    def read_frame(self):
        """Membaca data visual dari sensor kamera dengan validasi error"""
        if not self.cap or not self.cap.isOpened():
            self.reconnect_camera()
            return None
        ret, frame = self.cap.read()
        if not ret:
            self.reconnect_camera()
            return None
        return frame
    
    def detect_state(self, frame):
        """
        Melakukan inferensi AI menggunakan model YOLO dan pemetaan logika perilaku.
        Output: 'standing' (aktif), 'lying' (istirahat), atau 'unknown'.
        """
        results = self.model(frame, conf=self.conf, verbose=False)
        detected = "unknown"
        for r in results:
            if r.boxes is not None:
                for box in r.boxes: 
                    cls_id = int(box.cls[0])
                    raw_label = self.model.names[cls_id].lower().strip()
                    if raw_label == "resting-sheep":
                        detected = "lying"
                    elif raw_label in ["grazing-sheep", "running-sheep", "walking-sheep"]:
                        detected = "standing"
        return detected

if __name__ == "__main__":
    print("\n--- VALIDASI MODEL bebeee.pt DI KANDANG ---")
    
    try:
        
        tester = SheepVision("models/bebeee.pt", conf=0.50)
        print("[SUKSES] Sistem Visi Aktif.")
        while True:
            frame = tester.read_frame()
            if frame is not None:
                state = tester.detect_state(frame)
                print(f"\r-> Kondisi Domba: {state.upper()}    ", end="")
            else:
                print("\n[ERR] Gagal mendapatkan frame!")

    except KeyboardInterrupt:
        print("\n[INFO] Pengujian dihentikan.")
    
    finally:
        if 'tester' in locals():
            tester.cap.release()