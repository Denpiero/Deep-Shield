import sys
PYTHON = sys.executable
import threading
import subprocess
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QPushButton, QWidget, QLabel
from PyQt6.QtCore import Qt, QObject, pyqtSignal

# Çıktıları arayüze güvenli aktarmak için bir sinyal sınıfı
class Logger(QObject):
    log_signal = pyqtSignal(str)

class DeepShieldGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Deep-Shield | Siber Güvenlik Paneli")
        self.setGeometry(100, 100, 700, 550)
        self.logger = Logger()
        self.logger.log_signal.connect(self.update_log)

        # Arayüz Düzeni
        self.layout = QVBoxLayout()
        self.label = QLabel("Deep-Shield Ağ Analiz ve Savunma Sistemi")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin: 10px;")
        
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: Consolas; font-size: 12px;")
        
        self.start_btn = QPushButton("SİSTEMİ BAŞLAT")
        self.start_btn.setStyleSheet("""
            QPushButton { background-color: #27ae60; color: white; padding: 12px; font-weight: bold; border-radius: 5px; }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        self.start_btn.clicked.connect(self.start_process_thread)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.log_area)
        self.layout.addWidget(self.start_btn)
        
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def update_log(self, text):
        self.log_area.append(text)
        # Otomatik aşağı kaydır
        self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())

    def start_process_thread(self):
        self.start_btn.setEnabled(False)
        self.update_log(">>> [SİSTEM] Deep-Shield başlatılıyor...")
        thread = threading.Thread(target=self.run_deep_shield)
        thread.daemon = True
        thread.start()

    def run_deep_shield(self):
        # Sırasıyla çalıştırılacak dosyalar (Senin gönderdiğin liste)
        dosyalar = [
            ('aşama1_veri_topla.py', 60),
            ('aşama2_ozellik_cikar.py', None),
            ('aşama3_model.py', None),
            ('aşama4_gorsellestir.py', None),
            ('aşama5_gercek_zamanli.py', None)
        ]

        for dosya, sure in dosyalar:
            if not os.path.exists(dosya):
                self.logger.log_signal.emit(f"[HATA] {dosya} bulunamadı!")
                continue

            self.logger.log_signal.emit(f"\n>>> {dosya} çalıştırılıyor...")
            
            # Subprocess ile terminal çıktılarını yakalıyoruz
            islem = subprocess.Popen(
                [PYTHON, dosya],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                encoding='utf-8',
                errors='replace'
            )

            # Çıktıları anlık oku ve arayüze gönder
            if sure:
                # Süreli çalışan (aşama 1) için zamanlayıcı
                import time
                start_time = time.time()
                while islem.poll() is None:
                    line = islem.stdout.readline()
                    if line: self.logger.log_signal.emit(line.strip())
                    if time.time() - start_time > sure:
                        islem.terminate()
                        break
            else:
                # Normal bitene kadar çalışanlar için
                for line in iter(islem.stdout.readline, ''):
                    if line: self.logger.log_signal.emit(line.strip())
                islem.wait()

            self.logger.log_signal.emit(f"--- {dosya} tamamlandı. ---")

        self.logger.log_signal.emit("\n[TAMAMLANDI] Deep-Shield tam kapasite çalışıyor.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DeepShieldGUI()
    window.show()
    sys.exit(app.exec())