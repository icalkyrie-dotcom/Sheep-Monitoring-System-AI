class HealthLogic:
    def __init__(self):
        self.TEMP_MIN = 38.0
        self.TEMP_MAX = 40.0
        self.SENSOR_MIN_VALID = 35.0

    def evaluate(self, current_temp, lying_pct, current_phase):
        """
        Fungsi utama pengambil keputusan (Decision Maker).
        Menerima input fusi sensor (Suhu IR) dan AI (YOLO Behavior).
        Output: "NORMAL", "ABNORMAL", "WAITING DATA", atau "DATA TIDAK VALID".
        """
        if current_temp is None:
            return "WAITING DATA"

        if current_temp < self.SENSOR_MIN_VALID:
            return "DATA TIDAK VALID"
        is_warmup = "PEMANASAN" in current_phase


        temp_abnormal = current_temp < self.TEMP_MIN or current_temp > self.TEMP_MAX

       
        behavior_abnormal = (lying_pct > self.LYING_THRESHOLD) and not is_warmup

      
        if temp_abnormal or behavior_abnormal:
            return "ABNORMAL"
        else:
            return "NORMAL"