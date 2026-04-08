# =============================================================================
#  DEEP-SHIELD | Yapay Zeka Destekli Ağ Güvenlik Sistemi
#  Tek Dosya Sürümü — Tüm aşamalar bu dosyada birleştirilmiştir.
#  Kullanım: python deep_shield.py
# =============================================================================

import sys, os, time, threading, warnings, subprocess
from collections import defaultdict

# ─── BAĞIMLILIK KONTROLÜ ───────────────────────────────────────────────────
GEREKLI = ["scapy", "pandas", "numpy", "sklearn", "joblib", "matplotlib",
           "seaborn", "PyQt6"]
eksik = []
for lib in GEREKLI:
    try:
        __import__(lib if lib != "sklearn" else "sklearn.ensemble")
    except ImportError:
        eksik.append(lib)

if eksik:
    print(f"[!] Eksik kütüphaneler: {', '.join(eksik)}")
    print("[!] Lütfen 'pip install -r gereksinimler.txt' komutunu çalıştırın.")
    sys.exit(1)

# ─── KÜTÜPHANELER ──────────────────────────────────────────────────────────
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import joblib
import matplotlib
matplotlib.use("Agg")  # GUI olmadan render — görsel kaydetme için
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report
from sklearn.decomposition import PCA
from scapy.all import sniff, IP, TCP, UDP

from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout,
                              QHBoxLayout, QPushButton, QWidget, QLabel,
                              QTabWidget, QProgressBar, QFrame)
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QPixmap

PYTHON = sys.executable

# Tüm veri dosyaları her zaman bu scriptin yanına kaydedilir
DIZIN = os.path.dirname(os.path.abspath(__file__))

def yol(dosya_adi):
    """Verilen dosya adını scriptin bulunduğu klasörle birleştirir."""
    return os.path.join(DIZIN, dosya_adi)

# =============================================================================
#  AŞAMA 1 — VERİ TOPLAMA
# =============================================================================
def asama1_veri_topla(mod="normal", sure=60, log_fn=print):
    dosya_adi = yol(f"{mod}_trafigi.csv")
    paketler  = []

    def paketi_isle(paket):
        if IP not in paket:
            return
        kayit = {
            "zaman":      time.time(),
            "boyut":      len(paket),
            "kaynak_ip":  paket[IP].src,
            "hedef_ip":   paket[IP].dst,
            "protokol":   paket[IP].proto,
            "ttl":        paket[IP].ttl,
            "etiket":     1 if mod == "saldiri" else 0,
        }
        if TCP in paket:
            kayit.update({"kaynak_port": paket[TCP].sport,
                          "hedef_port":  paket[TCP].dport,
                          "bayraklar":   str(paket[TCP].flags)})
        elif UDP in paket:
            kayit.update({"kaynak_port": paket[UDP].sport,
                          "hedef_port":  paket[UDP].dport,
                          "bayraklar":   "UDP"})
        else:
            kayit.update({"kaynak_port": 0, "hedef_port": 0, "bayraklar": "None"})

        paketler.append(kayit)
        if len(paketler) % 100 == 0:
            log_fn(f"[*] Toplanan paket sayısı: {len(paketler)}")

    log_fn(f"--- [{mod.upper()}] Veri Toplama Başladı ({sure} sn) ---")
    try:
        sniff(filter="ip", prn=paketi_isle, timeout=sure, store=0)
    except Exception as e:
        log_fn(f"HATA: {e}")

    if paketler:
        df = pd.DataFrame(paketler)
        if os.path.exists(dosya_adi):
            df.to_csv(dosya_adi, mode="a", header=False, index=False)
        else:
            df.to_csv(dosya_adi, index=False)
        log_fn(f"[+] {len(df)} paket kaydedildi → {dosya_adi}")
    else:
        log_fn("HATA: Hiç paket toplanamadı!")


# =============================================================================
#  AŞAMA 2 — ÖZELLİK ÇIKARMA
# =============================================================================
def akis_ozelliklerini_cikar(df, pencere_saniye=1.0):
    df = df.sort_values("zaman").reset_index(drop=True)
    df["pencere"] = (df["zaman"] // pencere_saniye).astype(int)

    ozellikler = df.groupby("pencere").agg(
        paket_sayisi  = ("boyut", "count"),
        ort_boyut     = ("boyut", "mean"),
        std_boyut     = ("boyut", "std"),
        min_boyut     = ("boyut", "min"),
        max_boyut     = ("boyut", "max"),
        toplam_boyut  = ("boyut", "sum"),
        port_sayisi   = ("hedef_port", "nunique"),
        etiket        = ("etiket", "max"),
    ).reset_index()

    ozellikler["hiz"] = ozellikler["paket_sayisi"] / pencere_saniye

    df["is_large"] = df["boyut"] > 500
    large_counts   = df.groupby("pencere")["is_large"].sum()
    ozellikler["buyuk_paket_orani"] = (
        large_counts.values / ozellikler["paket_sayisi"]
    ).fillna(0)

    return ozellikler.fillna(0).drop(columns=["pencere"])


def asama2_ozellik_cikar(log_fn=print):
    normal_csv  = yol("normal_trafigi.csv")
    saldiri_csv = yol("saldiri_trafigi.csv")
    cikti_csv   = yol("ozellikler.csv")

    if not (os.path.exists(normal_csv) and os.path.exists(saldiri_csv)):
        log_fn("HATA: CSV dosyaları bulunamadı! Önce Aşama 1'i çalıştırın.")
        log_fn(f"      Aranan konum: {DIZIN}")
        return False
    try:
        veri = pd.concat([
            pd.read_csv(normal_csv),
            pd.read_csv(saldiri_csv),
        ], ignore_index=True)
        log_fn(f"[*] Toplam {len(veri)} ham paket işleniyor...")
        ozellik_df = akis_ozelliklerini_cikar(veri)
        ozellik_df.to_csv(cikti_csv, index=False)
        log_fn(f"[+] Özellik çıkarma tamamlandı! Boyut: {ozellik_df.shape}")
        log_fn(f"    Kaydedildi → {cikti_csv}")
        return True
    except Exception as e:
        log_fn(f"HATA: {e}")
        return False


# =============================================================================
#  AŞAMA 3 — MODEL EĞİTİMİ
# =============================================================================
OZELLIK_SUTUNLARI = [
    "paket_sayisi", "ort_boyut", "std_boyut",
    "min_boyut", "max_boyut", "toplam_boyut",
    "port_sayisi", "hiz", "buyuk_paket_orani",
]

def asama3_model(log_fn=print):
    ozellikler_csv = yol("ozellikler.csv")
    model_pkl      = yol("deepshield_model.pkl")

    if not os.path.exists(ozellikler_csv):
        log_fn("HATA: 'ozellikler.csv' bulunamadı! Önce Aşama 2'yi çalıştırın.")
        log_fn(f"      Aranan konum: {ozellikler_csv}")
        return False
    try:
        df = pd.read_csv(ozellikler_csv).fillna(0)
        X, y = df[OZELLIK_SUTUNLARI], df["etiket"]

        X_eg, X_te, y_eg, y_te = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        log_fn(f"[*] Model eğitiliyor... (Eğitim seti: {len(X_eg)} örnek)")
        rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(X_eg, y_eg)

        rapor = classification_report(y_te, rf.predict(X_te),
                                      target_names=["Normal", "Saldırı"])
        log_fn("\n=== PERFORMANS RAPORU ===\n" + rapor)

        cv = cross_val_score(rf, X, y, cv=5)
        log_fn(f"[+] Çapraz Doğrulama: %{cv.mean()*100:.2f}")

        joblib.dump(rf, model_pkl)
        log_fn(f"[OK] Model kaydedildi → {model_pkl}")
        return True
    except Exception as e:
        log_fn(f"HATA: {e}")
        return False


# =============================================================================
#  AŞAMA 4 — GÖRSELLEŞTİRME
# =============================================================================
def asama4_gorsellestir(log_fn=print):
    ozellikler_csv = yol("ozellikler.csv")
    gorsel_png     = yol("deepshield_analiz.png")

    if not os.path.exists(ozellikler_csv):
        log_fn("HATA: 'ozellikler.csv' bulunamadı! Önce Aşama 2'yi çalıştırın.")
        return
    try:
        df = pd.read_csv(ozellikler_csv)
        renkler      = {0: "#1D9E75", 1: "#E24B4A"}
        etiket_adlari= {0: "Normal",  1: "Saldırı"}

        plt.style.use("ggplot")
        fig, eksenler = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("Deep-Shield: Trafik Analizi", fontsize=16, fontweight="bold")

        # 1 — Hız Dağılımı
        ax = eksenler[0, 0]
        for et, grp in df.groupby("etiket"):
            ax.hist(grp["hiz"], bins=20, alpha=0.6,
                    label=etiket_adlari[et], color=renkler[et])
        ax.set_title("Saniye Başına Paket Hızı")
        ax.set_xlabel("Paket / Saniye")
        ax.legend()

        # 2 — Boyut vs Port
        ax = eksenler[0, 1]
        for et, grp in df.groupby("etiket"):
            ax.scatter(grp["ort_boyut"], grp["port_sayisi"],
                       alpha=0.5, label=etiket_adlari[et], color=renkler[et], s=30)
        ax.set_title("Paket Boyutu vs. Port Çeşitliliği")
        ax.set_xlabel("Ortalama Paket Boyutu (Bayt)")
        ax.set_ylabel("Benzersiz Port Sayısı")
        ax.legend()

        # 3 — Korelasyon Isı Haritası
        ax = eksenler[1, 0]
        sayisal = df[OZELLIK_SUTUNLARI + ["etiket"]]
        sns.heatmap(sayisal.corr(), ax=ax, cmap="coolwarm", annot=True, fmt=".1f",
                    linewidths=0.5, annot_kws={"size": 7})
        ax.set_title("Özellik Korelasyon Matrisi")

        # 4 — PCA 2D
        ax = eksenler[1, 1]
        X_pca_in = df[OZELLIK_SUTUNLARI].fillna(0)
        pca = PCA(n_components=2)
        coords = pca.fit_transform(X_pca_in)
        for et, nom in etiket_adlari.items():
            mask = df["etiket"] == et
            ax.scatter(coords[mask, 0], coords[mask, 1],
                       alpha=0.5, label=nom, color=renkler[et], s=20)
        ax.set_title("PCA — 2 Boyutlu Uzayda Ayrışım")
        ax.legend()

        plt.tight_layout()
        plt.savefig(gorsel_png, dpi=120, bbox_inches="tight")
        log_fn(f"[+] Grafik kaydedildi → {gorsel_png}")
        plt.close()
    except Exception as e:
        log_fn(f"HATA: {e}")


# =============================================================================
#  AŞAMA 5 — GERÇEK ZAMANLI TAHMİN
# =============================================================================
def asama5_gercek_zamanli(log_fn=print, dur_olay=None):
    model_pkl = yol("deepshield_model.pkl")
    try:
        model = joblib.load(model_pkl)
    except:
        log_fn(f"HATA: Model bulunamadı → {model_pkl}")
        log_fn("Önce Aşama 3'ü (Modeli Eğit) çalıştırın.")
        return

    pencere_saniye   = 2.0
    pencere_paketleri= defaultdict(list)
    son_tahmin_zamani= [time.time()]

    def tahmin_et(pencere_verisi):
        if len(pencere_verisi) < 5:
            return
        boyutlar = [p["boyut"] for p in pencere_verisi]
        portlar  = set(p.get("hedef_port", 0) for p in pencere_verisi)
        n        = len(boyutlar)
        veri     = pd.DataFrame([[
            n, sum(boyutlar)/n,
            pd.Series(boyutlar).std() or 0,
            min(boyutlar), max(boyutlar), sum(boyutlar),
            len(portlar),
            pencere_saniye / n,
            sum(1 for b in boyutlar if b > 500) / n,
        ]], columns=OZELLIK_SUTUNLARI)
        sonuc    = model.predict(veri)[0]
        olasilik = model.predict_proba(veri)[0][1]
        if sonuc == 1 or olasilik > 0.7:
            log_fn(f"⚠️  SALDIRI! [%{olasilik*100:.1f}] | "
                   f"Paket: {n} | Port Çeşitliliği: {len(portlar)}")
        else:
            log_fn(f"✓ Normal [%{olasilik*100:.1f}]")

    def paketi_isle(paket):
        if IP not in paket:
            return
        simdi = time.time()
        kayit = {"boyut": len(paket)}
        if TCP in paket:
            kayit["hedef_port"] = paket[TCP].dport
        anahtar = int(simdi // pencere_saniye)
        pencere_paketleri[anahtar].append(kayit)
        if simdi - son_tahmin_zamani[0] >= pencere_saniye:
            for k in list(pencere_paketleri.keys()):
                if k < anahtar:
                    tahmin_et(pencere_paketleri.pop(k))
            son_tahmin_zamani[0] = simdi

    log_fn("Deep-Shield Aktif! Trafik dinleniyor... (Durdurmak için arayüzden kapatın)")
    sniff(filter="ip", prn=paketi_isle, store=0,
          stop_filter=lambda _: dur_olay and dur_olay.is_set())


# =============================================================================
#  PyQt6 ARAYÜZÜ
# =============================================================================
class Logger(QObject):
    log_signal = pyqtSignal(str)

class IsciThread(QThread):
    """Her aşamayı arka planda çalıştırır."""
    log_signal   = pyqtSignal(str)
    bitti_signal = pyqtSignal()

    def __init__(self, gorev, parent=None):
        super().__init__(parent)
        self.gorev    = gorev   # çağrılacak fonksiyon
        self.dur_olay = threading.Event()

    def run(self):
        self.gorev(log_fn=self.log_signal.emit, dur_olay=self.dur_olay)
        self.bitti_signal.emit()

    def durdur(self):
        self.dur_olay.set()


class DeepShieldGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Deep-Shield | Siber Güvenlik Paneli")
        self.setGeometry(100, 100, 860, 620)
        self.setStyleSheet("""
            QMainWindow { background-color: #0d1117; }
            QWidget     { background-color: #0d1117; color: #c9d1d9; font-family: 'Consolas'; }
            QLabel      { color: #c9d1d9; }
            QTextEdit   { background-color: #161b22; color: #00ff88;
                          border: 1px solid #30363d; border-radius: 6px;
                          font-family: 'Consolas'; font-size: 12px; padding: 6px; }
            QPushButton { background-color: #21262d; color: #c9d1d9;
                          border: 1px solid #30363d; border-radius: 6px;
                          padding: 8px 18px; font-size: 13px; font-weight: bold; }
            QPushButton:hover   { background-color: #30363d; border-color: #8b949e; }
            QPushButton:disabled{ background-color: #161b22; color: #484f58; }
            QProgressBar { border: 1px solid #30363d; border-radius: 4px;
                           background-color: #161b22; height: 8px; text-align: center; }
            QProgressBar::chunk { background-color: #238636; border-radius: 4px; }
            QTabWidget::pane    { border: 1px solid #30363d; border-radius: 6px; }
            QTabBar::tab        { background-color: #161b22; color: #8b949e;
                                  padding: 8px 18px; border-radius: 4px; margin-right: 2px; }
            QTabBar::tab:selected { background-color: #21262d; color: #58a6ff; }
        """)

        self.aktif_thread = None
        self._arayuz_kur()

    def _arayuz_kur(self):
        merkez = QWidget()
        self.setCentralWidget(merkez)
        ana_duzen = QVBoxLayout(merkez)
        ana_duzen.setContentsMargins(20, 16, 20, 16)
        ana_duzen.setSpacing(12)

        # Başlık
        baslik = QLabel("🛡️  DEEP-SHIELD")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setStyleSheet("font-size: 22px; font-weight: bold; "
                             "color: #58a6ff; letter-spacing: 4px; padding: 8px;")
        alt_baslik = QLabel("Yapay Zeka Destekli Ağ Anomali Tespit Sistemi")
        alt_baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        alt_baslik.setStyleSheet("font-size: 11px; color: #8b949e; margin-bottom: 6px;")
        ana_duzen.addWidget(baslik)
        ana_duzen.addWidget(alt_baslik)

        # İlerleme çubuğu
        self.ilerleme = QProgressBar()
        self.ilerleme.setRange(0, 5)
        self.ilerleme.setValue(0)
        self.ilerleme.setFormat("Hazır")
        ana_duzen.addWidget(self.ilerleme)

        # Log alanı
        self.log_alani = QTextEdit()
        self.log_alani.setReadOnly(True)
        self.log_alani.setMinimumHeight(320)
        self.log_alani.setPlaceholderText("Sistem çıktıları burada görünecek...")
        ana_duzen.addWidget(self.log_alani)

        # Ayırıcı
        cizgi = QFrame()
        cizgi.setFrameShape(QFrame.Shape.HLine)
        cizgi.setStyleSheet("color: #30363d;")
        ana_duzen.addWidget(cizgi)

        # Butonlar
        buton_satiri = QHBoxLayout()
        self.btn_normal  = self._buton("🟢 Normal Trafik Topla (60s)",  "#238636", self._normal_topla)
        self.btn_saldiri = self._buton("🔴 Saldırı Trafiği Topla (60s)", "#b91c1c", self._saldiri_topla)
        self.btn_cikar   = self._buton("⚙️  Özellik Çıkar",              "#9333ea", self._ozellik_cikar)
        self.btn_model   = self._buton("🧠 Modeli Eğit",                 "#0284c7", self._model_egit)
        self.btn_gorsel  = self._buton("📊 Görselleştir",                "#b45309", self._gorsellestir)
        self.btn_canli   = self._buton("🚀 Canlı Analizi Başlat",        "#0f766e", self._canli_baslat)
        self.btn_durdur  = self._buton("⏹  Durdur",                     "#374151", self._durdur)
        self.btn_durdur.setEnabled(False)

        for btn in [self.btn_normal, self.btn_saldiri, self.btn_cikar,
                    self.btn_model, self.btn_gorsel, self.btn_canli, self.btn_durdur]:
            buton_satiri.addWidget(btn)

        ana_duzen.addLayout(buton_satiri)

        # Durum çubuğu
        self.durum = QLabel("● Sistem bekleniyor")
        self.durum.setStyleSheet("color: #8b949e; font-size: 11px; padding-top: 4px;")
        ana_duzen.addWidget(self.durum)

    def _buton(self, metin, renk, slot):
        btn = QPushButton(metin)
        btn.setStyleSheet(btn.styleSheet() +
                          f"QPushButton {{ border-left: 3px solid {renk}; }}")
        btn.clicked.connect(slot)
        return btn

    def _log(self, metin):
        self.log_alani.append(metin)
        self.log_alani.verticalScrollBar().setValue(
            self.log_alani.verticalScrollBar().maximum())

    def _durum_guncelle(self, metin, renk="#58a6ff"):
        self.durum.setStyleSheet(f"color: {renk}; font-size: 11px; padding-top: 4px;")
        self.durum.setText(f"● {metin}")

    def _thread_baslat(self, gorev_fn, ilerleme_adim=None):
        if self.aktif_thread and self.aktif_thread.isRunning():
            self._log("[!] Zaten çalışan bir işlem var.")
            return
        t = IsciThread(lambda **kw: gorev_fn(**kw))
        t.log_signal.connect(self._log)
        t.bitti_signal.connect(lambda: self._bitti(ilerleme_adim))
        self.aktif_thread = t
        self.btn_durdur.setEnabled(True)
        t.start()

    def _bitti(self, adim=None):
        self.btn_durdur.setEnabled(False)
        if adim is not None:
            self.ilerleme.setValue(adim)
            self.ilerleme.setFormat(f"Aşama {adim}/5 tamamlandı")
        self._durum_guncelle("Hazır", "#238636")

    def _durdur(self):
        if self.aktif_thread:
            self.aktif_thread.durdur()
            self._log("[SİSTEM] Durdurma isteği gönderildi...")

    # ── Aşama bağlantıları ──
    def _normal_topla(self):
        self._durum_guncelle("Normal trafik toplanıyor...")
        self._thread_baslat(
            lambda log_fn, **_: asama1_veri_topla("normal", 60, log_fn), 1)

    def _saldiri_topla(self):
        self._durum_guncelle("Saldırı trafiği toplanıyor...")
        self._thread_baslat(
            lambda log_fn, **_: asama1_veri_topla("saldiri", 60, log_fn), 1)

    def _ozellik_cikar(self):
        self._durum_guncelle("Özellikler çıkarılıyor...")
        self._thread_baslat(
            lambda log_fn, **_: asama2_ozellik_cikar(log_fn), 2)

    def _model_egit(self):
        self._durum_guncelle("Model eğitiliyor...")
        self._thread_baslat(
            lambda log_fn, **_: asama3_model(log_fn), 3)

    def _gorsellestir(self):
        self._durum_guncelle("Grafikler oluşturuluyor...")
        self._thread_baslat(
            lambda log_fn, **_: asama4_gorsellestir(log_fn), 4)

    def _canli_baslat(self):
        self._durum_guncelle("Canlı analiz aktif!", "#00ff88")
        self.ilerleme.setValue(5)
        self.ilerleme.setFormat("Canlı İzleme")

        def _canli_sarici(log_fn, dur_olay=None, **kw):
            asama5_gercek_zamanli(log_fn, dur_olay)

        if self.aktif_thread and self.aktif_thread.isRunning():
            self._log("[!] Zaten çalışan bir işlem var.")
            return
        t = IsciThread(_canli_sarici)
        t.log_signal.connect(self._log)
        t.bitti_signal.connect(lambda: self._bitti(5))
        self.aktif_thread = t
        self.btn_durdur.setEnabled(True)
        t.start()


# =============================================================================
#  GİRİŞ NOKTASI
# =============================================================================
if __name__ == "__main__":
    app    = QApplication(sys.argv)
    window = DeepShieldGUI()
    window.show()
    sys.exit(app.exec())
