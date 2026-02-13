#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
İmam Hatip Liseler Debug Script
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False

def debug_liseler():
    print("\n" + "="*70)
    print("🔍 İMAM HATİP LİSELER DEBUG")
    print("="*70 + "\n")
    
    # Chrome'u başlat
    chrome_options = Options()
    
    try:
        if WEBDRIVER_MANAGER_AVAILABLE:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)
        
        driver.maximize_window()
        
        # Test URL - SELÇUK ÜNİVERSİTESİ - ACİL YARDIM VE AFET YÖNETİMİ
        # Bu üniversitede daha fazla İmam Hatip lisesi var
        test_url = "https://yokatlas.yok.gov.tr/lisans.php?y=108911647"
        
        print(f"📍 Test URL: {test_url}")
        driver.get(test_url)
        time.sleep(5)
        
        print(f"✅ Sayfa yüklendi\n")
        
        # 1. Tüm h4 başlıklarını listele
        print("=" * 70)
        print("1️⃣ TÜM H4 BAŞLIKLARI")
        print("=" * 70)
        
        h4_elements = driver.find_elements(By.TAG_NAME, 'h4')
        print(f"Toplam h4: {len(h4_elements)}\n")
        
        for idx, h4 in enumerate(h4_elements, 1):
            text = h4.text.strip()[:80]
            classes = h4.get_attribute('class')
            print(f"{idx}. [{classes}] {text}")
        
        print()
        
        # 2. "Yerleşenlerin Mezun Oldukları Liseler" başlığını bul (TAM İSİM)
        print("=" * 70)
        print("2️⃣ 'YERLEŞENLER MEZUN OLDUKLARI LİSELER' PANELI")
        print("=" * 70)
        
        target_panel = None
        for h4 in h4_elements:
            text = h4.text.strip()
            # TAM isim kontrolü
            if text == "Yerleşenlerin Mezun Oldukları Liseler":
                target_panel = h4
                print(f"✓ DOĞRU PANEL BULUNDU: {text}")
                break
        
        if not target_panel:
            print("❌ 'Yerleşenlerin Mezun Oldukları Liseler' paneli bulunamadı!")
            return
        
        print()
        
        # 3. Doğru paneli aç
        if target_panel:
            print("=" * 70)
            print("3️⃣ PANELİ AÇIYORUM")
            print("=" * 70)
            
            panel_text = target_panel.text.strip()
            print(f"Panel: {panel_text}")
            
            # Tıkla
            driver.execute_script("arguments[0].click();", target_panel)
            time.sleep(3)
            print("✓ Panel tıklandı, 3 saniye bekleniyor...")
            
            # 4. Tablolardaki verileri kontrol et
            print("\n" + "=" * 70)
            print("4️⃣ PANEL İÇİNDEKİ TABLOLAR")
            print("=" * 70)
            
            tables = driver.find_elements(By.TAG_NAME, 'table')
            print(f"Toplam tablo: {len(tables)}\n")
            
            for table_idx, table in enumerate(tables, 1):
                rows = table.find_elements(By.TAG_NAME, 'tr')
                print(f"Tablo {table_idx}: {len(rows)} satır")
                
                # TÜM satırları göster (sadece ilk 5 değil)
                for row_idx, row in enumerate(rows[:20], 1):  # İlk 20 satır
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    if cells:
                        cell_texts = [c.text.strip()[:80] for c in cells[:3]]
                        print(f"  Satır {row_idx}: {cell_texts}")
                
                if len(rows) > 20:
                    print(f"  ... ve {len(rows) - 20} satır daha")
                
                print()
            
            # 5. İmam Hatip içeren satırları ara
            print("=" * 70)
            print("5️⃣ İMAM HATİP İÇEREN SATIRLAR (TÜM LİSTESİ)")
            print("=" * 70)
            
            found_count = 0
            for table in tables:
                rows = table.find_elements(By.TAG_NAME, 'tr')
                
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    
                    if len(cells) >= 2:
                        lise_adi = cells[0].text.strip()
                        
                        if lise_adi and len(lise_adi) > 5:  # Boş değil ve anlamlı
                            if 'İmam Hatip' in lise_adi or 'IMAM HATIP' in lise_adi.upper() or 'İMAM HATİP' in lise_adi:
                                found_count += 1
                                yerlesen = cells[1].text.strip()
                                print(f"\n{found_count}. LİSE ADI: {lise_adi}")
                                print(f"   Yerleşen: {yerlesen}")
                                print(f"   Karakter sayısı: {len(lise_adi)}")
            
            if found_count == 0:
                print("⚠️  İmam Hatip içeren satır bulunamadı!")
                print("\n💡 İlk 10 satırı kontrol ediyorum:")
                
                for table in tables:
                    rows = table.find_elements(By.TAG_NAME, 'tr')
                    for idx, row in enumerate(rows[:10], 1):
                        cells = row.find_elements(By.TAG_NAME, 'td')
                        if len(cells) >= 2:
                            col1 = cells[0].text.strip()
                            col2 = cells[1].text.strip()
                            if col1:
                                print(f"  {idx}. [{col1[:50]}] -> [{col2}]")
        
        print("\n💡 Tarayıcı 15 saniye açık kalacak, manuel inceleyebilirsiniz...")
        time.sleep(15)
        
        driver.quit()
        print("\n✅ Debug tamamlandı!")
        
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_liseler()
