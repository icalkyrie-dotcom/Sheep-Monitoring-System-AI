# 🐑 Smart Sheep Monitoring System with Edge AI & Cloud Integration

An integrated **Edge AI and IoT** solution for real-time livestock health monitoring. This system classifies sheep behaviors and tracks environmental & physiological metrics to ensure animal welfare through precision agriculture.

---

### 🖥️ Live Research Dashboard
<img width="1398" height="591" alt="Screenshot 2026-04-14 184318" src="https://github.com/user-attachments/assets/a635cd71-b564-4779-8596-b7164952cdcc" />
*Real-time visualization of health status, behavior classification, and environmental metrics.*

---

## 🚀 Overview
Traditional livestock monitoring is labor-intensive and prone to human error. This project automates the surveillance process using **Computer Vision** at the edge and **Sensor Fusion** for health assessment, providing a centralized cloud-backed dashboard for remote monitoring.

### 🛠️ Tech Stack
| Category | Technology |
|---|---|
| **AI Architecture** | YOLOv8/v11 (Custom Trained) |
| **Edge Computing** | Raspberry Pi 4 |
| **Sensors & IoT** | DS18B20 (Contact Temp), MQ137 (Ammonia), DHT22 |
| **Cloud & Database** | Firebase Realtime Database, Firestore |
| **Connectivity** | MQTT Protocol (Local), Firebase Admin SDK (Cloud) |
| **Software** | Python 3.11, HTML5/CSS3/JavaScript |

## 📂 Repository Structure
* `backend/`: Modular Python scripts for vision processing and data handling.
* `dashboard/`: Firebase-deployed web interface for data visualization.
* `models/`: Pre-trained YOLO weights optimized for livestock detection.
* `snapshot/`: Curated evidence of behavioral classification (Standing vs. Lying).
* `logs/`: Performance profiling data (System stability logs).
* `data_monitoring.csv`: Raw dataset from 72+ hours of continuous field testing.

## ✨ Key Features
* **Behavioral AI Classification:** Real-time detection of activities such as **Grazing, Walking, and Resting** with high confidence.
* **Precision Health Logic:** Automated status assessment using sensor fusion, specifically monitoring body temperature via **DS18B20 contact sensors**.
* **System Profiling:** Integrated profiler to monitor CPU, RAM, and thermals to ensure 24/7 reliability in pen environments.
* **Dual-Layer Data Sync:** Simultaneous data transmission via local MQTT broker and Cloud Firebase for data redundancy.

## 📊 Research & Validation
This system was deployed and validated in a real livestock pen environment, successfully processing over **26,000 data points** and visual snapshots. This extensive dataset ensures the reliability of the behavior classification model and health logic.

## ⚙️ Installation & Setup
1.  **Clone the Repo:**
    ```bash
    git clone [https://github.com/icalkyrie-dotcom/Sheep-Monitoring-System-AI.git](https://github.com/icalkyrie-dotcom/Sheep-Monitoring-System-AI.git)
    ```
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Credentials:**
    * Place your `firebase_key.json` in the `backend/` directory.
    * Update `firebaseConfig` in `dashboard/public/index.html`.
4.  **Run System:**
    ```bash
    python backend/Main.py
    ```

---
**Developed by Faisal Atmaja** *Electrical Engineering - Focus on AI* [LinkedIn Profile](www.linkedin.com/in/faisal-atmaja-b38330356) 
