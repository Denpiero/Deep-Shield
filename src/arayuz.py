
import sys
import threading
import subprocess
import os
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QPushButton, QWidget, QLabel
from PyQt6.QtCore import Qt, QObject, pyqtSignal
 
PYTHON = sys.executable
 
class Logger(QObject):
    log_signal = pyqtSignal(str)
 
class DeepShieldGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Deep-Shield | Siber Güvenlik Paneli")
        self.setGeometry(100, 100, 700, 550)
        self.logger = Logger()
        self.logger.log_signal.connect(self.update_log)
 
        self.layout = QVBoxLayout()
        self.label = QLabel("Deep-Shield Ag Analiz ve Savunma Sistemi")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin: 10px;")
 
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: Consolas; font-size: 12px;")
 
        self.start_btn = QPushButton("SISTEMI BASLAT")
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
        self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())
 
    def start_process_thread(self):
        self.start_btn.setEnabled(False)
        self.update_log(">>> [SISTEM] Deep-Shield baslatiliyor...")
        thread = threading.Thread(target=self.run_deep_shield)
        thread.daemon = True
        thread.start()
 
    def run_deep_shield(self):
        BASE = os.path.dirname(os.path.abspath(__file__))
 
        dosyalar = [
            (os.path.join(BASE, 'asama1_veri_topla.py'), 60),
            (os.path.join(BASE, 'asama2_ozellik_cikar.py'), None),
            (os.path.join(BASE, 'asama3_model.py'), None),
            (os.path.join(BASE, 'asama4_gorsellestir.py'), None),
            (os.path.join(BASE, 'asama5_gercek_zamanli.py'), None),
        ]
 
        for dosya, sure in dosyalar:
            if not os.path.exists(dosya):
                self.logger.log_signal.emit(f"[HATA] {dosya} bulunamadi!")
                continue
 
            self.logger.log_signal.emit(f"\n>>> {dosya} calistiriliyor...")
 
            islem = subprocess.Popen(
                [PYTHON, dosya],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                encoding='utf-8',
                errors='replace'
            )
 
            if sure:
                start_time = time.time()
                while islem.poll() is None:
                    line = islem.stdout.readline()
                    if line:
                        self.logger.log_signal.emit(line.strip())
                    if time.time() - start_time > sure:
                        islem.terminate()
                        break
            else:
                for line in iter(islem.stdout.readline, ''):
                    if line:
                        self.logger.log_signal.emit(line.strip())
                islem.wait()
 
            self.logger.log_signal.emit(f"--- {dosya} tamamlandi. ---")
 
        self.logger.log_signal.emit("\n[TAMAMLANDI] Deep-Shield tam kapasite calisiyor.")
 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DeepShieldGUI()
    window.show()
    sys.exit(app.exec())