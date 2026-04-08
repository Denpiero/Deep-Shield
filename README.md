[README (1).md](https://github.com/user-attachments/files/26569487/README.1.md)
# 🛡️ Deep-Shield
### Yapay Zeka Destekli Gerçek Zamanlı Ağ Anomali Tespit Sistemi

> Ağ trafiğini anlık olarak dinler, makine öğrenmesi ile saldırıları tespit eder.

---

## 🧠 Nasıl Çalışır?

```
Ağ Trafiği → Paket Yakalama → Özellik Çıkarma → Random Forest → Tehdit Skoru
```

Her 2 saniyelik pencerede paketlerin istatistiksel özelliklerini çıkarır ve eğitilmiş model ile **Normal / Saldırı** tahmini yapar.

**Model Performansı:**
| Metrik | Değer |
|--------|-------|
| Doğruluk | %81 |
| Çapraz Doğrulama (5-Katlı) | %86.25 |
| Saldırı Tespiti (Recall) | %75 |

---

## ⚙️ Kurulum

### Gereksinimler
- Windows 10/11
- **Python 3.10+** → [python.org/downloads](https://python.org/downloads)
  - Kurulumda **"Add Python to PATH"** kutusunu işaretle ✅
- **Npcap** (ağ dinlemesi için zorunlu) → [npcap.com/#download](https://npcap.com/#download)
  - Kurulumda **"WinPcap API-compatible Mode"** kutusunu işaretle ✅

### Adım 1 — Repoyu İndir
GitHub'da yeşil **Code** → **Download ZIP** → ZIP'i çıkart

### Adım 2 — Kütüphaneleri Kur
`kurulum.bat` dosyasına **sağ tıkla → Yönetici olarak çalıştır**

### Adım 3 — Programı Başlat
`deepshield.bat` dosyasına **sağ tıkla → Yönetici olarak çalıştır**

> ⚠️ Ağ trafiği dinlemek için **yönetici yetkisi zorunludur.**

---

## 🚀 Kullanım Sırası

Program açıldıktan sonra arayüzdeki butonları sırayla kullan:

| # | Buton | Açıklama | Süre |
|---|-------|----------|------|
| 1 | 🟢 Normal Trafik Topla | 60 saniye normal ağ trafiği kaydeder | ~60 sn |
| 2 | 🔴 Saldırı Trafiği Topla | 60 saniye saldırı trafiği kaydeder (nmap, ping flood vb.) | ~60 sn |
| 3 | ⚙️ Özellik Çıkar | Ham paketlerden ML özellikleri üretir | ~5 sn |
| 4 | 🧠 Modeli Eğit | Random Forest modelini eğitir ve kaydeder | ~10 sn |
| 5 | 📊 Görselleştir | Trafik analiz grafiklerini oluşturur | ~5 sn |
| 6 | 🚀 Canlı Analizi Başlat | Gerçek zamanlı saldırı tespitini başlatır | Sürekli |

> **Not:** Eğer `deepshield_model.pkl` zaten klasörde varsa 1-4. adımları atlayabilirsin, direkt 6'ya geçebilirsin.

---

## 📁 Proje Yapısı

```
Deep-Shield/
├── kurulum.bat          ← Önce çalıştır (bir kere yeterli)
├── deepshield.bat       ← Programı başlatır
├── requirements.txt
├── src/
│   └── deep_shield.py   ← Ana program (tek dosya)
├── data/
│   ├── normal_trafigi.csv
│   └── saldiri_trafigi.csv
└── model/
    └── deepshield_model.pkl
```

---

## 🔧 Manuel Kurulum (Terminal)

```bash
pip install -r requirements.txt
python src/deep_shield.py
```

> Linux/Mac için `sudo` gerekir:
> ```bash
> sudo python3 src/deep_shield.py
> ```

---

## 📦 Kullanılan Teknolojiler

| Kütüphane | Kullanım |
|-----------|----------|
| Scapy | Ağ paketi yakalama |
| Scikit-learn | Random Forest modeli |
| PyQt6 | Masaüstü arayüzü |
| Pandas / NumPy | Veri işleme |
| Matplotlib / Seaborn | Görselleştirme |

---

## ❓ Sık Karşılaşılan Sorunlar

**"Operation not permitted" hatası**
→ Programı yönetici olarak çalıştırın (sağ tık → Yönetici olarak çalıştır)

**"Npcap bulunamadı" hatası**
→ [npcap.com](https://npcap.com/#download) adresinden Npcap'i kurun, "WinPcap API-compatible Mode"u işaretleyin

**"Python bulunamadı" hatası**
→ Python kurulumunda "Add Python to PATH" seçeneğini işaretleyip tekrar kurun

---

*Hackathon 2025 — Deep-Shield Ekibi*
