import paho.mqtt.client as mqtt
import time

class MQTTHandler:
    def __init__(self, broker="YOUR_MQTT_BROKER_IP", port=1883):
        # Menginisialisasi objek klien MQTT
        self.client = mqtt.Client()
        
        # Alamat IP statis broker MQTT (biasanya Mosquitto di Raspberry Pi)
        self.broker = broker
        # Port standar MQTT tanpa enkripsi SSL/TLS
        self.port = port

        # --- BUFFER DATA SENSOR ---
        # Variabel ini menampung nilai terakhir yang dikirim oleh node sensor (Wemos/ESP)
        self.body_temp = None  # Suhu tubuh domba (Inframerah)
        self.env_temp = None   # Suhu lingkungan kandang (DHT/SHT)
        self.humidity = None   # Kelembaban kandang
        self.nh3 = None        # Kadar gas amonia (MQ137)

        # --- MANAJEMEN WAKTU & KONEKSI ---
        self.last_update_str = None    # Waktu operasional dari Wemos dalam format string (HH:MM:SS)
        self.last_update_time = None   # Timestamp absolut (UNIX time) saat paket data terakhir diterima
        self.is_connected = False      # Status koneksi jaringan ke broker

        # Mendaftarkan fungsi callback untuk menangani event dari protokol MQTT
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, rc):
        """Callback yang dieksekusi saat klien berhasil (atau gagal) menyentuh broker"""
        # rc (Return Code) 0 berarti koneksi sukses
        if rc == 0:
            self.is_connected = True
            print("\n[MQTT] Terhubung! Mendengarkan transmisi data kandang...")
            # Subscribe ke semua sub-topik di bawah 'kandang/sheep/' menggunakan wildcard '#'
            self.client.subscribe("kandang/sheep/#")
        else:
            print(f"\n[MQTT ERROR] Koneksi Gagal, Kode Error: {rc}")

    def on_disconnect(self, client, userdata, rc):
        """Callback saat koneksi TCP terputus secara tidak wajar"""
        self.is_connected = False
        if rc != 0:
            print("\n[MQTT WARN] Koneksi terputus! Mencoba auto-reconnect...")

    def on_message(self, client, userdata, msg):
        """
        Fungsi krusial: Memproses setiap paket (message) yang masuk dari broker.
        Berjalan secara asinkron (di-trigger oleh network loop).
        """
        try:
            # Memperbarui waktu kedatangan data terbaru (Penting untuk deteksi sensor mati)
            self.last_update_time = time.time()

            topic = msg.topic
            # Mendekode payload dari byte ke string dan membersihkan spasi/newline
            payload_str = msg.payload.decode().strip()

            if not payload_str: return

            # Demultiplexing data berdasarkan topik MQTT
            if topic == "kandang/sheep/last_update":
                self.last_update_str = payload_str
                print(f"[MQTT] Update Waktu: {self.last_update_str}")
                
            else:
                try:
                    # Konversi tipe data dari string jaringan ke float untuk komputasi
                    payload = float(payload_str)

                    # Pemetaan data ke variabel buffer internal
                    if topic == "kandang/sheep/temp":
                        self.body_temp = payload
                    elif topic == "kandang/sheep/suhu":
                        self.env_temp = payload
                    elif topic == "kandang/sheep/hum":
                        self.humidity = payload
                    elif topic == "kandang/sheep/nh3":
                        self.nh3 = payload

                except ValueError:
                    # Proteksi tipe data: Mengabaikan payload rusak (misal: "NaN" atau karakter aneh)
                    pass

        except Exception as e:
            print(f"\n[MQTT ERROR] Gagal proses data pada {msg.topic}: {e}")

    def start(self):
        """Memulai thread jaringan MQTT secara non-blocking"""
        try:
            # Timeout keepalive diset 60 detik
            self.client.connect(self.broker, self.port, 60)
            # Menjalankan thread terpisah untuk menangani I/O jaringan MQTT
            self.client.loop_start()
        except Exception as e: 
            print(f"[MQTT FATAL] Broker {self.broker} offline: {e}")

    def stop(self):
        """Prosedur shutdown bersih untuk mencegah port menggantung (zombie connection)"""
        self.client.loop_stop()
        self.client.disconnect()
        print("[MQTT] Shutdown aman.")