[README.md](https://github.com/user-attachments/files/26565720/README.md)
# 🛡️ Deep-Shield
### Gerçek Zamanlı Ağ Saldırısı Tespit Sistemi

> Makine öğrenmesi tabanlı, gerçek zamanlı ağ trafiği analiz ve saldırı tespit sistemi.

---

## 📸 Ekran Görüntüsü
![WhatsApp Image 2026-04-08 at 12 49 43](https://github.com/user-attachments/assets/ae92e982-3053-41d6-abd3-9c5f9b13cfff)

---

## 🧠 Nasıl Çalışır?

Deep-Shield, ağ trafiğini anlık olarak dinler ve her 2 saniyelik pencerede istatistiksel özellikler çıkararak **Random Forest** modeli ile saldırı tespiti yapar.

```
Ağ Trafiği → Paket Yakalama → Özellik Çıkarma → ML Modeli → Tehdit Skoru
```

**Model Performansı:**
- ✅ Doğruluk: **%81**
- ✅ Çapraz Doğrulama (5-Katlı): **%86.25**
- ✅ Saldırı Tespiti (Recall): **%75**

**Tespit Edilen Özellikler:**
| Özellik | Açıklama |
|--------|----------|
| `std_boyut` | Paket boyutu standart sapması |
| `toplam_boyut` | Saniyedeki toplam veri |
| `hiz` | Saniye başına paket sayısı |
| `port_sayisi` | Benzersiz hedef port sayısı |
| `buyuk_paket_orani` | 500 bayt üzeri paket oranı |

---

## ⚙️ Kurulum (Windows)

### Gereksinimler
- Windows 10/11
- Python 3.10 veya üzeri → [python.org](https://python.org/downloads)
- Npcap (ağ dinlemesi için zorunlu) → [npcap.com](https://npcap.com/#download)

### Adım 1 — Repoyu İndir
```
Code → Download ZIP → ZIP'i çıkart
```

### Adım 2 — Kurulum
`kurulum.bat` dosyasına **sağ tıkla → Yönetici olarak çalıştır**

Bu işlem otomatik olarak:
- Gerekli Python kütüphanelerini kurar
- Npcap'in kurulu olup olmadığını kontrol eder

### Adım 3 — Çalıştır
`deepshield.bat` dosyasına **sağ tıkla → Yönetici olarak çalıştır**

> ⚠️ Ağ trafiği dinlemek için **yönetici yetkisi zorunludur.**

---

## 📁 Proje Yapısı

```
DeepShield/
├── kurulum.bat              ← Önce çalıştır (bir kere yeterli)
├── deepshield.bat           ← Programı başlatır
├── requirements.txt         
├── src/
│   ├── arayuz.py            ← PyQt6 arayüzü
│   ├── ana_calistirici.py   ← Terminal çalıştırıcı
│   ├── asama1_veri_topla.py ← Scapy ile paket yakalama
│   ├── asama2_ozellik_cikar.py ← Özellik mühendisliği
│   ├── asama3_model.py      ← Random Forest eğitimi
│   ├── asama4_gorsellestir.py  ← Görselleştirme
│   └── asama5_gercek_zamanli.py ← Canlı tehdit tespiti
├── data/
│   ├── normal_trafigi.csv   ← Normal trafik verisi
│   └── saldiri_trafigi.csv  ← Saldırı trafik verisi
└── model/
    └── deepshield_model.pkl ← Eğitilmiş model
```

---

## 🚀 Sistem Akışı

| Aşama | Dosya | Açıklama |
|-------|-------|----------|
| 1 | `asama1_veri_topla.py` | 60 sn ağ trafiği dinler, CSV'e kaydeder |
| 2 | `asama2_ozellik_cikar.py` | Ham paketlerden ML özellikleri çıkarır |
| 3 | `asama3_model.py` | Random Forest modelini eğitir |
| 4 | `asama4_gorsellestir.py` | Trafik analiz grafikleri oluşturur |
| 5 | `asama5_gercek_zamanli.py` | Canlı tehdit tespiti yapar |

---

## 🔧 Manuel Kurulum (Terminal)

```bash
pip install -r requirements.txt
python src/arayuz.py
```

> Linux/WSL için `sudo` gerekir:
> ```bash
> sudo python3 src/arayuz.py
> ```

---

## 📦 Kullanılan Teknolojiler

- **Scapy** — Ağ paketi yakalama
- **Scikit-learn** — Random Forest modeli
- **PyQt6** — Masaüstü arayüzü
- **Pandas / NumPy** — Veri işleme
- **Matplotlib / Seaborn** — Görselleştirme

---

## 👥 Ekip

> *(Ekip üyelerinin isimleri buraya)*

---

*Hackathon projesi — 2025*
