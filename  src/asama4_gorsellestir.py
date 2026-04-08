# aşama4_gorsellestir.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
import numpy as np
import os

# DOSYAYI OKU
if not os.path.exists("ozellikler.csv"):
    print("HATA: 'ozellikler.csv' bulunamadı!")
    exit()

df = pd.read_csv("ozellikler.csv")

# Renkler ve Etiket Ayarları (0=Normal, 1=Saldırı)
renkler = {0: "#1D9E75", 1: "#E24B4A"}
etiket_adlari = {0: "Normal", 1: "Saldiri"}

plt.style.use('ggplot') # Grafiklerin daha modern görünmesi için
fig, eksenler = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Deep-Shield: Trafik Analizi ve Anomali Tespiti", fontsize=16, fontweight="bold")

# 1. Paket Hızı Dağılımı (Histogram)
ax = eksenler[0, 0]
for etiket, grup in df.groupby("etiket"):
    ax.hist(grup["hiz"], bins=20, alpha=0.6, 
            label=etiket_adlari[etiket], color=renkler[etiket])
ax.set_title("Saniye Başına Paket Hızı Dağılımı")
ax.set_xlabel("Paket / Saniye")
ax.legend()

# 2. Ortalama Boyut vs. Port Sayısı (Scatter)
ax = eksenler[0, 1]
for etiket, grup in df.groupby("etiket"):
    ax.scatter(grup["ort_boyut"], grup["port_sayisi"], 
               alpha=0.5, label=etiket_adlari[etiket], color=renkler[etiket], s=30)
ax.set_title("Paket Boyutu vs. Port Çeşitliliği")
ax.set_xlabel("Ortalama Paket Boyutu (Bayt)")
ax.set_ylabel("Benzersiz Port Sayısı")
ax.legend()

# 3. Özellikler Arası Korelasyon (Isı Haritas