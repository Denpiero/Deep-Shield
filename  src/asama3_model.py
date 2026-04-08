# aşama3_model.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

# DOSYAYI OKU
if not os.path.exists("ozellikler.csv"):
    print("HATA: 'ozellikler.csv' bulunamadı! Önce Aşama 2'yi çalıştırın.")
    exit()

df = pd.read_csv("ozellikler.csv")

# ÖZELLİK SÜTUNLARI (Aşama 2 ile birebir aynı olmalı)
ozellik_sutunlari = [
    "paket_sayisi", "ort_boyut", "std_boyut", 
    "min_boyut", "max_boyut", "toplam_boyut", 
    "port_sayisi", "hiz", "buyuk_paket_orani"
]

# Veri setinde eksik değer varsa 0 ile doldur
df = df.fillna(0)

X = df[ozellik_sutunlari]
y = df["etiket"] # Aşama 2'de zaten 0 ve 1 yapmıştık

# EĞİTİM VE TEST AYRIMI
# stratify=y komutu, normal ve saldırı verisinin eşit dağılmasını sağlar
X_egitim, X_test, y_egitim, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"[*] Model eğitiliyor... (Eğitim seti: {len(X_egitim)} örnek)")

# RANDOM FOREST — Sınıflandırma için en güçlü algoritmalardan biri
rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
rf.fit(X_egitim, y_egitim)

# TEST SONUÇLARI
tahminler = rf.predict(X_test)
print("\n=== MODEL PERFORMANS RAPORU ===")
print(classification_report(y_test, tahminler, target_names=["Normal", "Saldırı"]))

# ÇAPRAZ DOĞRULAMA (Jüriye güvenilirlik kanıtı)
cv_skorlar = cross_val_score(rf, X, y, cv=5)
print(f"\n[+] Çapraz Doğrulama Skoru (5-Katlı): %{cv_skorlar.mean()*100:.2f}")

# ÖZELLİK ÖNEMLERİ (Hangi veri saldırıyı daha iyi ele veriyor?)
onem = pd.Series(rf.feature_importances_, index=ozellik_sutunlari).sort_values(ascending=False)
print("\n=== HANGİ ÖZELLİKLER DAHA ÖNEMLİ? ===")
print(onem)

# MODELİ KAYDET (Aşama 5 bu dosyayı kullanacak)
joblib.dump(rf, "deepshield_model.pkl")
print("\n[OK] Model başarıyla kaydedildi: deepshield_model.pkl")