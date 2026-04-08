# aşama2_ozellik_cikar.py
import pandas as pd
import numpy as np
import os

def akis_ozelliklerini_cikar(df, pencere_saniye=1.0):
    """
    Her zaman penceresindeki (1 saniyelik dilimler) paket grubundan 
    istatistiksel özellikler çıkarır.
    """
    # Veriyi zamana göre sırala ve pencere numaralarını ata
    df = df.sort_values("zaman").reset_index(drop=True)
    df["pencere"] = (df["zaman"] // pencere_saniye).astype(int)

    # Temel istatistikleri hesapla
    # Not: Aşama 1'deki 'etiket' sütununu da (0 veya 1) buraya taşıyoruz
    ozellikler = df.groupby("pencere").agg(
        paket_sayisi   = ("boyut", "count"),
        ort_boyut      = ("boyut", "mean"),
        std_boyut      = ("boyut", "std"),
        min_boyut      = ("boyut", "min"),
        max_boyut      = ("boyut", "max"),
        toplam_boyut   = ("boyut", "sum"),
        port_sayisi    = ("hedef_port", "nunique"),
        etiket         = ("etiket", "max") # O pencerede 1 tane bile saldırı varsa 1 sayılır
    ).reset_index()

    # Zamanlama özelliği: saniye başına düşen hız (hız ne kadar yüksekse saldırı ihtimali artar)
    ozellikler["hiz"] = ozellikler["paket_sayisi"] / pencere_saniye

    # Büyük paket oranı (MTU değerine yakın paketlerin oranı)
    # 500 bayttan büyük paketlerin o saniyedeki toplam paketlere oranı
    df["is_large"] = df["boyut"] > 500
    large_counts = df.groupby("pencere")["is_large"].sum()
    ozellikler["buyuk_paket_orani"] = (large_counts.values / ozellikler["paket_sayisi"]).fillna(0)

    # NaN (boş) değerleri 0 ile doldur (özellikle tek paketlik pencerelerdeki std için)
    ozellikler = ozellikler.fillna(0)
    
    # Gereksiz 'pencere' sütununu atalım, yapay zeka bunu görmesin
    return ozellikler.drop(columns=["pencere"])

# --- DOSYALARI OKU VE BİRLEŞTİR ---
try:
    if os.path.exists("normal_trafigi.csv") and os.path.exists("saldiri_trafigi.csv"):
        normal  = pd.read_csv("normal_trafigi.csv")
        saldiri = pd.read_csv("saldiri_trafigi.csv")
        
        # İki veriyi alt alta birleştir
        veri = pd.concat([normal, saldiri], ignore_index=True)
        print(f"[*] Toplam {len(veri)} ham paket işleniyor...")
        
        ozellik_df = akis_ozelliklerini_cikar(veri)
        
        # Sonuçları kaydet
        ozellik_df.to_csv("ozellikler.csv", index=False)
        print("[+] Özellik çıkarma tamamlandı! 'ozellikler.csv' oluşturuldu.")
        print(f"[+] Yeni veri seti boyutu: {ozellik_df.shape}")
        print(ozellik_df.head())
    else:
        print("HATA: CSV dosyaları bulunamadı! Lütfen önce Aşama 1'i çalıştırın.")
except Exception as e:
    print(f"HATA OLUŞTU: {e}")