#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YÖK Atlas Üniversite Sayfası Debug
Tek bir üniversite sayfasını detaylı analiz eder
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import re

try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False

def analyze_university_page():
    """Bir üniversite sayfasını analiz et"""
    
    # Test URL - FIRAT ÜNİVERSİTESİ - ADLİ BİLİŞİM MÜHENDİSLİĞİ
    test_url = "https://yokatlas.yok.gov.tr/lisans.php?y=104320299"
    
    print("\n" + "="*70)
    print("🔍 YÖK ATLAS ÜNİVERSİTE SAYFASI ANALİZİ")
    print("="*70)
    print(f"\n📍 Test URL: {test_url}\n")
    
    # Chrome'u başlat
    print("🌐 Tarayıcı başlatılıyor...")
    chrome_options = Options()
    
    try:
        if WEBDRIVER_MANAGER_AVAILABLE:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)
        
        driver.maximize_window()
        print("✅ Tarayıcı başlatıldı\n")
        
        # Sayfaya git
        print(f"📄 Sayfa yükleniyor...")
        driver.get(test_url)
        time.sleep(5)
        
        print(f"✅ Sayfa yüklendi: {driver.title}\n")
        
        # Önce tüm panelleri aç
        print("🔓 Panelleri açıyor...")
        try:
            panels = driver.find_elements(By.XPATH, "//h4[contains(@class, 'panel-title')]")
            print(f"  Bulunan panel: {len(panels)}")
            for idx, panel in enumerate(panels[:5], 1):
                try:
                    panel_text = panel.text[:50]
                    print(f"    Panel {idx}: {panel_text}")
                    if panel.is_displayed():
                        panel.click()
                        time.sleep(1)
                except:
                    pass
        except Exception as e:
            print(f"  Panel açma hatası: {e}")
        
        print()
        
        # Sekmeleri kontrol et
        print("📑 Sekmeleri kontrol ediyor...")
        try:
            tabs = driver.find_elements(By.TAG_NAME, 'a')
            stat_tabs = [t for t in tabs if 'İstatistik' in t.text or 'Kontenjan' in t.text]
            print(f"  İstatistik sekmeleri: {len(stat_tabs)}")
            for tab in stat_tabs[:3]:
                try:
                    print(f"    Sekme: {tab.text[:50]}")
                    if tab.is_displayed():
                        tab.click()
                        time.sleep(2)
                        break
                except:
                    pass
        except Exception as e:
            print(f"  Sekme tıklama hatası: {e}")
        
        time.sleep(2)
        print()
        
        # 1. Puan Türü ara
        print("=" * 70)
        print("1️⃣ PUAN TÜRÜ ARAMA")
        print("=" * 70)
        
        puan_turu_found = []
        
        # Metod 1: Tüm tablolarda ara
        print("\nMetod 1: Tablolarda 'Puan Türü' ara")
        tables = driver.find_elements(By.TAG_NAME, 'table')
        print(f"  Toplam tablo: {len(tables)}")
        
        for table_idx, table in enumerate(tables, 1):
            rows = table.find_elements(By.TAG_NAME, 'tr')
            for row_idx, row in enumerate(rows):
                cells = row.find_elements(By.TAG_NAME, 'td')
                for cell_idx, cell in enumerate(cells):
                    if 'Puan Tür' in cell.text:
                        print(f"\n  ✓ Tablo {table_idx}, Satır {row_idx}, Hücre {cell_idx}")
                        print(f"    Hücre metni: '{cell.text}'")
                        if cell_idx + 1 < len(cells):
                            next_cell = cells[cell_idx + 1]
                            print(f"    Sonraki hücre: '{next_cell.text}'")
                            puan_turu_found.append({
                                'method': 'table',
                                'value': next_cell.text.strip()
                            })
        
        # Metod 2: XPath ile ara
        print("\nMetod 2: XPath ile ara")
        try:
            xpath_elements = driver.find_elements(By.XPATH, 
                "//*[contains(text(), 'Puan Tür')]")
            print(f"  Bulunan element: {len(xpath_elements)}")
            
            for elem in xpath_elements:
                print(f"    Metin: '{elem.text}'")
                try:
                    next_elem = elem.find_element(By.XPATH, './following-sibling::*')
                    print(f"    Sonraki: '{next_elem.text}'")
                    puan_turu_found.append({
                        'method': 'xpath',
                        'value': next_elem.text.strip()
                    })
                except:
                    pass
        except Exception as e:
            print(f"  Hata: {e}")
        
        # 2. Yerleşen ara
        print("\n" + "=" * 70)
        print("2️⃣ YERLEŞEN SAYISI ARAMA")
        print("=" * 70)
        
        yerlesen_found = []
        
        # Metod 1: Tablolarda "Yerleşen" başlığı ara
        print("\nMetod 1: Tablolarda 'Yerleşen' başlığı ara")
        
        for table_idx, table in enumerate(tables, 1):
            headers = table.find_elements(By.TAG_NAME, 'th')
            yerlesen_idx = -1
            
            for h_idx, header in enumerate(headers):
                if 'Yerleşen' in header.text:
                    yerlesen_idx = h_idx
                    print(f"\n  ✓ Tablo {table_idx}, Başlık sütunu {h_idx}")
                    print(f"    Başlık: '{header.text}'")
                    break
            
            if yerlesen_idx >= 0:
                rows = table.find_elements(By.TAG_NAME, 'tr')
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    if len(cells) > yerlesen_idx:
                        cell_text = cells[yerlesen_idx].text.strip()
                        numbers = re.findall(r'\d+', cell_text)
                        if numbers:
                            print(f"    Veri: '{cell_text}' -> Sayı: {numbers[0]}")
                            yerlesen_found.append({
                                'method': 'table-header',
                                'value': int(numbers[0]),
                                'raw': cell_text
                            })
        
        # 3. Tüm sayfa içeriği
        print("\n" + "=" * 70)
        print("3️⃣ SAYFA İÇERİĞİ")
        print("=" * 70)
        
        page_text = driver.page_source
        print(f"Sayfa boyutu: {len(page_text)} karakter")
        print(f"'Puan Türü' geçiş: {page_text.count('Puan Türü')}")
        print(f"'Puan Tür' geçiş: {page_text.count('Puan Tür')}")
        print(f"'Yerleşen' geçiş: {page_text.count('Yerleşen')}")
        
        # 4. Sonuç
        print("\n" + "=" * 70)
        print("📊 SONUÇ")
        print("=" * 70)
        
        print(f"\n🎯 Puan Türü bulunanlar: {len(puan_turu_found)}")
        for pt in puan_turu_found:
            print(f"  • [{pt['method']}] {pt['value']}")
        
        print(f"\n📊 Yerleşen bulunanlar: {len(yerlesen_found)}")
        for yrl in yerlesen_found:
            print(f"  • [{yrl['method']}] {yrl['value']} (raw: {yrl['raw']})")
        
        print("\n💡 Tarayıcı 15 saniye açık kalacak, manuel inceleyebilirsiniz...")
        time.sleep(15)
        
        driver.quit()
        print("\n✅ Analiz tamamlandı!")
        
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_university_page()
