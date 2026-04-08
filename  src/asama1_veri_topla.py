# aşama1_veri_topla.py
from scapy.all import sniff, IP, TCP, UDP
import pandas as pd
import time
import os

# --- AYARLAR ---
SURE = 60  # Kaç saniye dinlenecek?
# MOD SEÇİMİ: 'normal' verisi toplarken 'normal', saldırı yaparken 'saldiri' yazın
MOD = "saldırı" 
DOSYA_ADI = f"{MOD}_trafigi.csv"
# ---------------

paketler = []

def paketi_isle(paket):
    if IP in paket:
        kayit = {
            "zaman":      time.time(),
            "boyut":      len(paket),
            "kaynak_ip":  paket[IP].src,
            "hedef_ip":   paket[IP].dst,
            "protokol":   paket[IP].proto, # 6=TCP, 17=UDP
            "ttl":        paket[IP].ttl,
            "etiket":     1 if MOD == "saldiri" else 0  # Yapay zeka için sayısal etiket (1=Saldırı, 0=Normal)
        }
        
        # TCP veya UDP port bilgilerini güvenli bir şekilde al
        if TCP in paket:
            kayit["kaynak_port"] = paket[TCP].sport
            kayit["hedef_port"]  = paket[TCP].dport
            kayit["bayraklar"]   = str(paket[TCP].flags)
        elif UDP in paket:
            kayit["kaynak_port"] = paket[UDP].sport
            kayit["hedef_port"]  = paket[UDP].dport
            kayit["bayraklar"]   = "UDP"
        else:
            kayit["kaynak_port"] = 0
            kayit["hedef_port"]  = 0
            kayit["bayraklar"]   = "None"
            
        paketler.append(kayit)
        if len(paketler) % 100 == 0:
            print(f"[*] Toplanan paket sayısı: {len(paketler)}")

print(f"--- [{MOD.upper()}] Veri Toplama Başladı ({SURE} sn) ---")
print("Lütfen bu sırada ağda trafik oluşturun (Siteye girin veya saldırı başlatın)...")

# Windows'ta yönetici olarak çalıştırıldığından emin olun
try:
    sniff(filter="ip", prn=paketi_isle, timeout=SURE, store=0)
except Exception as e:
    print(f"HATA: Trafik dinlenemedi. Npcap yüklü mü? Yönetici misiniz? \nDetay: {e}")

if paketler:
    df = pd.DataFrame(paketler)
    # Eğer dosya varsa üzerine ekleme yap, yoksa yeni oluştur
    if os.path.exists(DOSYA_ADI):
        df.to_csv(DOSYA_ADI, mode='a', header=False, index=False)
    else:
        df.to_csv(DOSYA_ADI, index=False)
    print(f"İŞLEM TAMAM: {len(df)} adet [{MOD}] paketi '{DOSYA_ADI}' dosyasına kaydedildi.")
else:
    print("HATA: Hiç paket toplanamadı!")