import subprocess
import time
import os

def calistir(dosya_adi, sure=None):
    print(f">>> {dosya_adi} baslatiliyor...")
    # Windows'ta python3 yerine 'python' komutu kullanılır genelde
    islem = subprocess.Popen(['python', dosya_adi])
    
    if sure:
        time.sleep(sure)
        islem.terminate()
        print(f"--- {dosya_adi} {sure} saniye sonra durduruldu. ---")
    else:
        islem.wait()
        print(f"--- {dosya_adi} tamamlandi. ---")

if __name__ == "__main__":
    calistir('aşama1_veri_topla.py', sure=60)
    calistir('aşama2_ozellik_cikar.py')
    calistir('aşama3_model.py')
    calistir('aşama4_gorsellestir.py')
    calistir('aşama5_gercek_zamanli.py')
    print("ISLEM TAMAMLANDI!")