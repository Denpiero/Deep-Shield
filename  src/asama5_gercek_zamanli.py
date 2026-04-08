from scapy.all import sniff, IP, TCP
import pandas as pd
import joblib
import time
from collections import defaultdict
import warnings

warnings.filterwarnings("ignore") # Gereksiz uyarıları kapat

# MODELİ YÜKLE
try:
    model = joblib.load("deepshield_model.pkl")
    # Eğitirken kullandığın sütun isimlerini buraya YAZMALISIN
    sutun_isimleri = ['paket_sayisi', 'ort_boyut', 'std_boyut', 'min_boyut', 'max_boyut', 'toplam_boyut', 'port_sayisi', 'hiz', 'buyuk_paket_orani']
except:
    print("HATA: deepshield_model.pkl bulunamadı! Önce aşama 3'ü çalıştır.")
    exit()

pencere_saniye = 2.0 # 1 saniye çok hızlı olabilir, 2 saniye daha stabil
pencere_paketleri = defaultdict(list)
son_tahmin_zamani = time.time()

def tahmin_et(pencere_verisi):
    if len(pencere_verisi) < 5: return # Çok az paket varsa tahmin yapma
    
    boyutlar = [p["boyut"] for p in pencere_verisi]
    portlar  = set(p.get("hedef_port", 0) for p in pencere_verisi)
    
    # ÖZELLİKLERİ MODELİN ANLAYACAĞI ŞEKLE GETİR (DataFrame)
    veri_ozeti = pd.DataFrame([[
        len(boyutlar),
        sum(boyutlar) / len(boyutlar),
        pd.Series(boyutlar).std() or 0,
        min(boyutlar), 
        max(boyutlar),
        sum(boyutlar),
        len(portlar),
        pencere_saniye / len(boyutlar),
        sum(1 for b in boyutlar if b > 500) / len(boyutlar)
    ]], columns=sutun_isimleri) # <--- BURASI ÇOK KRİTİK
    
    sonuc = model.predict(veri_ozeti)[0]
    olasilik = model.predict_proba(veri_ozeti)[0][1]
    
    if sonuc == 1 or olasilik > 0.7:
        print(f"⚠️  SALDIRI! [%{olasilik*100:.1f}] | Paket: {len(boyutlar)} | Port Çeşitliliği: {len(portlar)}")
    else:
        print(f"✓ Normal [%{olasilik*100:.1f}]")

def paketi_isle(paket):
    global son_tahmin_zamani
    if IP not in paket: return
    
    simdi = time.time()
    kayit = {"boyut": len(paket)}
    if TCP in paket:
        kayit["hedef_port"] = paket[TCP].dport
    
    # Şu anki zaman dilimine ekle
    pencere_anahtari = int(simdi // pencere_saniye)
    pencere_paketleri[pencere_anahtari].append(kayit)
    
    # Eğer 2 saniye geçtiyse eski pencereleri analiz et ve sil
    if simdi - son_tahmin_zamani >= pencere_saniye:
        anahtarlar = list(pencere_paketleri.keys())
        for k in anahtarlar:
            if k < pencere_anahtari:
                tahmin_et(pencere_paketleri.pop(k))
        son_tahmin_zamani = simdi

print("Deep-Shield Aktif! Windows üzerinden trafik dinleniyor...")
# Windows'ta 'iface' belirtmek gerekebilir ama 'sniff' genelde varsayılanı bulur
sniff(filter="ip", prn=paketi_isle, store=0)