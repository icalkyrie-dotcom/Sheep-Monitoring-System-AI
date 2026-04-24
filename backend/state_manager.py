import time

class StateManager:
    def __init__(self):

        self.current_state = "unknown"
        self.start_monitoring_time = time.time() 
        self.state_start_time = time.time()
        self.standing_duration = 0
        self.lying_duration = 0

    def update(self, detected_state):
        """
        Dipanggil setiap kali frame diproses oleh YOLO.
        Fungsinya menghitung rentang waktu (elapsed) dari frame sebelumnya ke frame saat ini,
        lalu menambahkannya ke state yang sedang aktif.
        """
        now = time.time()
        elapsed = now - self.state_start_time
        if self.current_state == "standing":
            self.standing_duration += elapsed
        elif self.current_state == "lying":
            self.lying_duration += elapsed

        state_changed = False
        
      
        if detected_state != self.current_state and detected_state != "unknown":
            self.current_state = detected_state
            state_changed = True
        self.state_start_time = now
        return state_changed

    def get_monitoring_phase(self):
        """
        Klasifikasi fase pemantauan berdasarkan total uptime sistem.
        Membantu menentukan validitas data (data di bawah 4 jam dianggap belum stabil/representatif).
        """
        total_elapsed_hours = (time.time() - self.start_monitoring_time) / 3600
        if total_elapsed_hours < 4:
            return "PEMANASAN (Data Belum Stabil)"
        elif total_elapsed_hours < 12:
            return "MONITORING SEMENTARA"
        elif total_elapsed_hours < 24:
            return "MONITORING AKTIF"
        else:
            return "DATA HARIAN FINAL (24 JAM)"

    def get_totals(self):
        """Mengembalikan akumulasi metrik mentah (raw data) dalam bentuk integer (detik)"""
        return {
            "standing": int(self.standing_duration),
            "lying": int(self.lying_duration),
            "uptime_seconds": int(time.time() - self.start_monitoring_time)
        }

    def get_percentages(self):
        """
        Mengonversi total detik aktivitas menjadi persentase.
        Ini adalah metrik utama yang akan masuk ke health_logic (sistem pakar kesehatan).
        """
        total = self.standing_duration + self.lying_duration
        if total == 0:
            return 0.0, 0.0
        standing_pct = (self.standing_duration / total) * 100
        lying_pct = (self.lying_duration / total) * 100
        
        return standing_pct, lying_pct