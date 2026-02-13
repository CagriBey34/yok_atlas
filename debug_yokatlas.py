#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YÖK Atlas Sayfa Analiz Scripti
Sayfanın yapısını analiz eder ve doğru elementleri bulur
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

def analyze_page():
    """YÖK Atlas ana sayfasını analiz et"""
    
    print("\n" + "="*70)
    print("🔍 YÖK ATLAS SAYFA ANALİZİ")
    print("="*70 + "\n")
    
    # Chrome'u başlat
    print("🌐 Tarayıcı başlatılıyor...")
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    try:
        if WEBDRIVER_MANAGER_AVAILABLE:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)
        
        driver.maximize_window()
        print("✅ Tarayıcı başlatıldı\n")
        
        # Ana sayfaya git
        url = "https://yokatlas.yok.gov.tr/lisans-anasayfa.php"
        print(f"📍 Sayfaya gidiliyor: {url}")
        driver.get(url)
        time.sleep(5)
        
        print(f"✅ Sayfa yüklendi: {driver.title}\n")
        
        # 1. SELECT elementlerini analiz et
        print("=" * 70)
        print("1️⃣ SELECT ELEMENTLERİ ANALİZİ")
        print("=" * 70)
        
        selects = driver.find_elements(By.TAG_NAME, 'select')
        print(f"Toplam select elementi: {len(selects)}\n")
        
        for idx, select in enumerate(selects, 1):
            select_id = select.get_attribute('id')
            select_name = select.get_attribute('name')
            select_class = select.get_attribute('class')
            options = select.find_elements(By.TAG_NAME, 'option')
            
            print(f"Select #{idx}:")
            print(f"  ID: {select_id}")
            print(f"  Name: {select_name}")
            print(f"  Class: {select_class}")
            print(f"  Option sayısı: {len(options)}")
            
            # İlk 5 option'ı göster
            print(f"  İlk 5 option:")
            for i, opt in enumerate(options[:5], 1):
                value = opt.get_attribute('value')
                text = opt.text[:50]
                print(f"    {i}. value='{value}' text='{text}'")
            print()
        
        # 2. Program linklerini analiz et
        print("=" * 70)
        print("2️⃣ PROGRAM LİNKLERİ ANALİZİ")
        print("=" * 70)
        
        all_links = driver.find_elements(By.TAG_NAME, 'a')
        program_links = [l for l in all_links if 'lisans-bolum.php?b=' in (l.get_attribute('href') or '')]
        
        print(f"Toplam link: {len(all_links)}")
        print(f"Program linkleri: {len(program_links)}\n")
        
        if program_links:
            print("İlk 10 program linki:")
            for idx, link in enumerate(program_links[:10], 1):
                href = link.get_attribute('href')
                text = link.text.strip()[:50]
                
                # Kod çıkar
                if 'b=' in href:
                    code = href.split('b=')[1].split('&')[0].split('#')[0]
                    print(f"  {idx}. [{code}] {text}")
                    print(f"      URL: {href}")
        else:
            print("⚠️  Program linki bulunamadı!")
        
        print()
        
        # 3. JavaScript ile veri çek
        print("=" * 70)
        print("3️⃣ JAVASCRIPT İLE VERİ ÇEKME")
        print("=" * 70)
        
        js_script = """
        var data = {
            selects: [],
            links: [],
            divs: []
        };
        
        // SELECT elementleri
        document.querySelectorAll('select').forEach(function(sel, idx) {
            data.selects.push({
                id: sel.id,
                name: sel.name,
                optionCount: sel.options.length
            });
        });
        
        // Program linkleri
        document.querySelectorAll('a[href*="lisans-bolum.php?b="]').forEach(function(link) {
            var match = link.href.match(/b=(\\d+)/);
            if (match) {
                data.links.push({
                    code: match[1],
                    text: link.textContent.trim().substring(0, 50)
                });
            }
        });
        
        // Ana div'ler
        document.querySelectorAll('div[id], div[class]').forEach(function(div, idx) {
            if (idx < 10) {
                data.divs.push({
                    id: div.id,
                    class: div.className
                });
            }
        });
        
        return data;
        """
        
        js_data = driver.execute_script(js_script)
        
        print(f"JavaScript ile bulunan:")
        print(f"  SELECT: {len(js_data['selects'])}")
        print(f"  Program linkleri: {len(js_data['links'])}")
        print(f"  Ana div'ler: {len(js_data['divs'])}\n")
        
        if js_data['links']:
            print("JavaScript ile bulunan ilk 10 program:")
            for idx, link in enumerate(js_data['links'][:10], 1):
                print(f"  {idx}. [{link['code']}] {link['text']}")
        
        print()
        
        # 4. Sayfa kaynağını kontrol et
        print("=" * 70)
        print("4️⃣ SAYFA KAYNAĞI ANALİZİ")
        print("=" * 70)
        
        page_source = driver.page_source
        print(f"Sayfa boyutu: {len(page_source)} karakter")
        print(f"'lisans-bolum.php?b=' geçiş sayısı: {page_source.count('lisans-bolum.php?b=')}")
        print(f"'<select' geçiş sayısı: {page_source.count('<select')}")
        print(f"'<option' geçiş sayısı: {page_source.count('<option')}")
        
        print()
        
        # 5. Sonuç
        print("=" * 70)
        print("📊 SONUÇ VE ÖNERİLER")
        print("=" * 70)
        
        if len(program_links) > 0:
            print(f"✅ {len(program_links)} program linki bulundu!")
            print("   Script çalışmalı.")
        elif len(js_data['links']) > 0:
            print(f"✅ JavaScript ile {len(js_data['links'])} program bulundu!")
            print("   JavaScript metodunu kullanın.")
        elif len(selects) > 0:
            print(f"⚠️  {len(selects)} select bulundu ama programlar çıkarılamadı.")
            print("   Select içindeki option'ları kontrol edin.")
        else:
            print("❌ Hiçbir metod çalışmadı!")
            print("   Sayfa yapısı değişmiş olabilir.")
        
        print("\n💡 Tarayıcı 10 saniye açık kalacak, sayfayı manuel inceleyebilirsiniz...")
        time.sleep(10)
        
        driver.quit()
        print("\n✅ Analiz tamamlandı!")
        
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_page()
