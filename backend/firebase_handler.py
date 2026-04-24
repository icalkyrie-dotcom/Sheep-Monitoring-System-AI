import firebase_admin
from firebase_admin import credentials, firestore, storage
from datetime import datetime, timedelta, timezone
import os

class FirebaseHandler:
    def __init__(self, key_path):
        try:
            # Mencegah error "App already exists" jika inisialisasi dipanggil lebih dari sekali
            if not firebase_admin._apps:
                # Memuat kredensial Service Account Key (file JSON)
                cred = credentials.Certificate(key_path)
                firebase_admin.initialize_app(cred, {
                    # Alamat bucket Cloud Storage untuk menyimpan foto
                    'storageBucket': 'sheep-monitoring-c9a4d.firebasestorage.app'
                })

            # Klien untuk database NoSQL (Firestore)
            self.db = firestore.client()
            # Klien untuk penyimpanan file (Cloud Storage)
            self.bucket = storage.bucket()
            print("[FIREBASE] Koneksi Cloud Firestore & Storage Berhasil.")
        except Exception as e:
            print(f"[FIREBASE ERROR] Gagal inisialisasi: {e}")

    def update_dashboard(self, phase, temp, lying_pct, health, env_temp, hum, nh3, state):
        """
        Memperbarui data real-time untuk dashboard.
        Menggunakan set() untuk menimpa (overwrite) dokumen tunggal 'status_sekarang'.
        """
        try:
            # Referensi ke dokumen spesifik di dalam collection 'monitoring'
            doc_ref = self.db.collection('monitoring').document('status_sekarang')
            
            # Konversi nilai internal ke format string yang mudah dibaca UI
            status_aktivitas = "Beraktivitas" if state == "standing" else "Istirahat"
            
            # Menyimpan payload data dalam format Dictionary/JSON
            doc_ref.set({
                # SERVER_TIMESTAMP memastikan waktu diambil dari server Google, bukan jam lokal RPi
                'last_update': firestore.SERVER_TIMESTAMP,
                'fase': phase,
                'status_kesehatan': health,
                'data_tubuh': {
                    # Fallback ke 0 jika data bernilai None untuk mencegah error tipe data di Frontend
                    'suhu': round(temp, 2) if temp else 0,
                    'persentase_istirahat': round(lying_pct, 2),
                    'aktivitas_saat_ini': status_aktivitas
                },
                'data_lingkungan': {
                    'suhu_kandang': round(env_temp, 2) if env_temp else 0,
                    'kelembapan': round(hum, 2) if hum else 0,
                    'amonia': round(nh3, 2) if nh3 else 0
                }
            })
        except Exception as e:
            print(f"[FIREBASE ERROR] Gagal update Dashboard: {e}")

    def upload_snapshot_and_log(self, local_path, health, state):
        """
        Mengunggah gambar hasil deteksi YOLO ke Storage dan menyimpan URL-nya di Firestore.
        Digunakan untuk riwayat (History) log.
        """
        try:
            # Validasi keberadaan file fisik di MicroSD
            if not os.path.exists(local_path):
                return None

            # Mengekstrak nama file dari path lokal (misal: 'snapshots/foto.jpg' -> 'foto.jpg')
            file_name = os.path.basename(local_path)
            
            # Membuat referensi objek blob di Firebase Storage
            blob = self.bucket.blob(f"snapshots/{file_name}")
            
            # Eksekusi I/O Jaringan: Mengunggah file
            blob.upload_from_filename(local_path)
            
            # Membuka akses file ke publik agar bisa dirender oleh tag <img> di dashboard web
            blob.make_public()
            image_url = blob.public_url

            # Menambahkan dokumen baru (Auto-ID) ke collection 'history_snapshots'
            self.db.collection('history_snapshots').add({
                'timestamp': firestore.SERVER_TIMESTAMP,
                'image_url': image_url,
                'status_kesehatan': health,
                'aktivitas': "Beraktivitas" if state == "standing" else "Istirahat"
            })
            return image_url
        except Exception as e:
            print(f"[FIREBASE ERROR] Gagal upload: {e}")
            return None

    # --- LOGIKA ROLLING DELETION 3 HARI (72 JAM) ---
    def cleanup_old_data(self, retention_hours=72):
        """
        Menghapus data yang lebih tua dari batas retensi untuk menghemat kuota cloud.
        """
        try:
            # PENTING: Gunakan zona waktu UTC karena firestore.SERVER_TIMESTAMP berbasis UTC
            threshold = datetime.now(timezone.utc) - timedelta(hours=retention_hours)

            # Melakukan query pencarian dokumen yang timestamp-nya lebih kecil (lebih tua) dari threshold
            docs = self.db.collection('history_snapshots') \
                          .where('timestamp', '<', threshold) \
                          .stream()

            deleted_count = 0
            for doc in docs:
                data = doc.to_dict()
                
                # 1. Hapus file fisik di Firebase Storage
                if 'image_url' in data:
                    # Manipulasi string untuk mengekstrak nama file asli dari URL publik Firebase
                    file_name = data['image_url'].split('/')[-1].split('?')[0].replace('snapshots%2F', '')
                    blob = self.bucket.blob(f"snapshots/{file_name}")
                    if blob.exists():
                        blob.delete()

                # 2. Hapus dokumen metadata di Firestore menggunakan ID dokumen
                self.db.collection('history_snapshots').document(doc.id).delete()
                deleted_count += 1

            if deleted_count > 0:
                print(f"[CLEANUP] Berhasil menghapus {deleted_count} data lama (> {retention_hours} jam).")
            return deleted_count
        except Exception as e:
            print(f"[FIREBASE ERROR] Gagal cleanup: {e}")
            return 0