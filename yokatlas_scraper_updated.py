#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YÖK Atlas Selenium Web Scraper
Gerçek tarayıcı ile otomatik veri çekme - 3 Yıllık + İmam Hatip Analizleri + Şehir + Fakülte
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import json
import time
from datetime import datetime
import os
import re

# Webdriver Manager - Otomatik ChromeDriver yönetimi
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False

class YokAtlasSeleniumScraper:
    def __init__(self, headless=False):
        self.headless = headless
        self.driver = None
        self.data = []
        self.stats = {
            'programs_scanned': 0,
            'universities_scanned': 0,
            'total_records': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
        
    def setup_driver(self):
        print("🌐 Tarayıcı başlatılıyor...")
        
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
            print("   (Headless modda - tarayıcı görünmez)")
        else:
            print("   (Canlı mod - tarayıcıyı izleyebilirsiniz)")
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        try:
            if WEBDRIVER_MANAGER_AVAILABLE:
                print("   ✓ Webdriver Manager ile otomatik ChromeDriver yönetimi")
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                print("   ⚠ Manuel ChromeDriver kullanılıyor")
                self.driver = webdriver.Chrome(options=chrome_options)
            
            self.driver.maximize_window()
            print("✅ Tarayıcı başarıyla başlatıldı\n")
        except Exception as e:
            print(f"❌ Tarayıcı başlatılamadı: {e}")
            raise
    
    def get_all_programs(self):
        print("📚 Tüm lisans programları çekiliyor...")
        
        try:
            print("   → Ana sayfaya gidiliyor...")
            self.driver.get("https://yokatlas.yok.gov.tr/lisans-anasayfa.php")
            time.sleep(3)
            
            print("   → Bölümler listeleniyor...")
            
            programs = []
            
            try:
                bolum_select = self.driver.find_element(By.ID, 'bolum')
                options = bolum_select.find_elements(By.TAG_NAME, 'option')
                
                print(f"   → {len(options)} option bulundu")
                
                for option in options:
                    value = option.get_attribute('value')
                    text = option.text.strip()
                    
                    if value and value.isdigit() and len(value) == 5 and text and text != 'Seç...':
                        programs.append({
                            'code': value,
                            'name': text,
                            'url': f"https://yokatlas.yok.gov.tr/lisans-bolum.php?b={value}"
                        })
                
                print(f"✅ {len(programs)} program bulundu")
                
                # Programlar A'dan Z'ye sırayla taranacak
                print("🔤 Programlar A harfinden başlayarak taranacak!")
                
                if programs:
                    print("\n📋 Bulunan programlardan örnekler (BAŞTAN):")
                    for prog in programs[:5]:
                        print(f"   • {prog['name']} ({prog['code']})")
                    print()
                
                return programs
                
            except Exception as e:
                print(f"   ❌ Bölüm listesi alınamadı: {e}")
                return []
            
        except Exception as e:
            print(f"❌ Program listesi alınırken hata: {e}")
            return []
    
    def get_universities_for_program(self, program, max_retries=3):
        """Program için üniversite listesini çek, retry ile"""
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if retry_count > 0:
                    print(f"  🔄 Yeniden deneme {retry_count}/{max_retries}...")
                    time.sleep(5)
                
                print(f"  🔍 {program['name']} programı açılıyor...")
                
                self.driver.get(program['url'])
                time.sleep(3)
                
                universities = []
                
                univ_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="lisans.php?y="]')
                
                for link in univ_links:
                    href = link.get_attribute('href')
                    name = link.text.strip()
                    
                    if href and 'y=' in href and name:
                        univ_code = href.split('y=')[1].split('&')[0]
                        if univ_code.isdigit():
                            universities.append({
                                'code': univ_code,
                                'name': name,
                                'url': href
                            })
                
                unique_univs = []
                seen_codes = set()
                for univ in universities:
                    if univ['code'] not in seen_codes:
                        unique_univs.append(univ)
                        seen_codes.add(univ['code'])
                
                print(f"     → {len(unique_univs)} üniversite bulundu")
                return unique_univs
                
            except Exception as e:
                retry_count += 1
                
                if retry_count < max_retries:
                    print(f"     ⚠️  Hata: {e}")
                    print(f"     🔄 {max_retries - retry_count} deneme hakkı kaldı...")
                    continue
                else:
                    print(f"     ❌ {max_retries} deneme sonrası başarısız: {e}")
                    return []
        
        return []
    
    def get_university_info_from_page(self):
        """Üniversite sayfasındaki başlıktan üniversite ismi, şehir, tip ve bölüm bilgisini çek"""
        try:
            # Üniversite ismi ve şehir - sol başlık
            university_name = None
            city = None
            h3_left = self.driver.find_elements(By.CSS_SELECTOR, 'h3.panel-title.pull-left')
            for h3 in h3_left:
                text = h3.text.strip()
                match = re.search(r'^(.+?)\s*\(([^)]+)\)$', text)
                if match:
                    university_name = match.group(1).strip()
                    city = match.group(2).strip()
                    break
            
            # Üniversite tipi - sağ başlık
            university_type = None
            h3_right = self.driver.find_elements(By.CSS_SELECTOR, 'h3.panel-title.pull-right')
            for h3 in h3_right:
                text = h3.text.strip()
                if 'Üniversite Türü:' in text:
                    # "Üniversite Türü: Vakıf" -> "Vakıf"
                    university_type = text.replace('Üniversite Türü:', '').strip()
                    break
            
            # Bölüm ismi - h2 başlık
            program_name = None
            h2_elements = self.driver.find_elements(By.CSS_SELECTOR, 'h2.panel-title.pull-left')
            for h2 in h2_elements:
                text = h2.text.strip()
                if 'Program :' in text:
                    # "Program : 201910024 - Amerikan Kültürü ve Edebiyatı (İngilizce) (Burslu)"
                    # -> "Amerikan Kültürü ve Edebiyatı (İngilizce) (Burslu)"
                    match = re.search(r'Program\s*:\s*\d+\s*-\s*(.+)', text)
                    if match:
                        program_name = match.group(1).strip()
                    break
            
            return {
                'university_name': university_name,
                'city': city,
                'university_type': university_type,
                'program_name': program_name
            }
        except:
            pass
        return {'university_name': None, 'city': None, 'university_type': None, 'program_name': None}
    
    def get_year_data(self, year):
        """Belirli bir yıl için veri çek"""
        year_result = {
            'yerlesen': None,
            'puan_turu': None,
            'fakulte': None,  # YENİ: Fakülte bilgisi
            'imam_hatip_lise_tipi': [],
            'imam_hatip_liseler': []
        }
        
        # Genel Bilgiler panelini aç
        try:
            genel_bilgiler = None
            
            try:
                genel_bilgiler = self.driver.find_element(By.XPATH, 
                    "//h4[contains(text(), 'Genel Bilgiler')]")
            except:
                pass
            
            if not genel_bilgiler:
                try:
                    genel_bilgiler = self.driver.find_element(By.XPATH, 
                        "//a[contains(text(), 'Genel Bilgiler')]")
                except:
                    pass
            
            if not genel_bilgiler:
                try:
                    genel_bilgiler = self.driver.find_element(By.XPATH, 
                        "//*[contains(@class, 'panel-title')][contains(., 'Genel Bilgiler')]")
                except:
                    pass
            
            if genel_bilgiler:
                self.driver.execute_script("arguments[0].click();", genel_bilgiler)
                time.sleep(2)
                
        except:
            pass
        
        time.sleep(1)
        
        # Puan Türü, Toplam Yerleşen ve FAKÜLTEYİ çek
        try:
            tables = self.driver.find_elements(By.TAG_NAME, 'table')
            
            for table in tables:
                rows = table.find_elements(By.TAG_NAME, 'tr')
                
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    
                    if len(cells) >= 2:
                        first_cell_text = cells[0].text.strip()
                        second_cell_text = cells[1].text.strip()
                        
                        # Puan Türü
                        if 'Puan Tür' in first_cell_text and not year_result['puan_turu']:
                            year_result['puan_turu'] = second_cell_text
                        
                        # Toplam Yerleşen
                        if 'Toplam Yerleşen' in first_cell_text and not year_result['yerlesen']:
                            numbers = re.findall(r'\d+', second_cell_text)
                            if numbers:
                                year_result['yerlesen'] = int(numbers[0])
                        
                        # YENİ: FAKÜLTE bilgisini çek
                        if 'Fakülte' in first_cell_text and not year_result['fakulte']:
                            year_result['fakulte'] = second_cell_text
                    
                    # Hepsi bulunduysa döngüden çık
                    if year_result['puan_turu'] and year_result['yerlesen'] and year_result['fakulte']:
                        break
                
                if year_result['puan_turu'] and year_result['yerlesen'] and year_result['fakulte']:
                    break
                    
        except:
            pass
        
        # İmam Hatip Lise Tipi
        try:
            lise_tipi_link = None
            try:
                lise_tipi_link = self.driver.find_element(By.XPATH,
                    "//*[contains(text(), 'Yerleşenlerin Mezun Oldukları Lise Grubu')]")
            except:
                try:
                    lise_tipi_link = self.driver.find_element(By.XPATH,
                        "//*[contains(text(), 'Lise Grubu')]")
                except:
                    pass
            
            if lise_tipi_link:
                self.driver.execute_script("arguments[0].click();", lise_tipi_link)
                time.sleep(2)
                
                tables = self.driver.find_elements(By.TAG_NAME, 'table')
                
                for table in tables:
                    rows = table.find_elements(By.TAG_NAME, 'tr')
                    
                    for row in rows:
                        cells = row.find_elements(By.TAG_NAME, 'td')
                        
                        if len(cells) >= 3:
                            lise_tipi = cells[0].text.strip()
                            
                            if 'İmam Hatip' in lise_tipi or 'IMAM HATIP' in lise_tipi.upper():
                                try:
                                    yerlesen_text = cells[1].text.strip()
                                    oran_text = cells[2].text.strip()
                                    
                                    yerlesen = re.findall(r'\d+', yerlesen_text)
                                    oran = re.findall(r'[\d,\.]+', oran_text)
                                    
                                    year_result['imam_hatip_lise_tipi'].append({
                                        'tip': lise_tipi,
                                        'yerlesen': int(yerlesen[0]) if yerlesen else None,
                                        'oran': oran[0] if oran else None
                                    })
                                except:
                                    pass
                
                # Paneli KAPAT
                try:
                    self.driver.execute_script("arguments[0].click();", lise_tipi_link)
                    time.sleep(1)
                except:
                    pass
            
            if year_result['imam_hatip_lise_tipi']:
                print(f"     ✓ {len(year_result['imam_hatip_lise_tipi'])} İmam Hatip lise tipi bulundu")
                
        except:
            pass
        
        # İmam Hatip Liseler verilerini çek
        try:
            time.sleep(1)
            
            liseler_panel = None
            try:
                liseler_panel = self.driver.find_element(By.XPATH,
                    "//h4[contains(@class, 'panel-title') and normalize-space(.)='Yerleşenlerin Mezun Oldukları Liseler']")
            except:
                try:
                    liseler_panel = self.driver.find_element(By.XPATH,
                        "//h4[contains(@class, 'panel-title') and contains(., 'Oldukları Liseler') and not(contains(., 'Grubu'))]")
                except:
                    pass
            
            if liseler_panel:
                self.driver.execute_script("arguments[0].click();", liseler_panel)
                time.sleep(3)
                
                try:
                    panel_parent = liseler_panel.find_element(By.XPATH, "./parent::*/parent::*")
                    panel_body = panel_parent.find_element(By.CLASS_NAME, "panel-collapse")
                    tables = panel_body.find_elements(By.TAG_NAME, 'table')
                except:
                    tables = self.driver.find_elements(By.TAG_NAME, 'table')
                
                for table in tables:
                    rows = table.find_elements(By.TAG_NAME, 'tr')
                    
                    for row in rows:
                        cells = row.find_elements(By.TAG_NAME, 'td')
                        
                        if len(cells) >= 2:
                            lise_adi = cells[0].text.strip()
                            
                            if len(lise_adi) > 10 and ('İmam Hatip' in lise_adi or 'IMAM HATIP' in lise_adi.upper() or 'İMAM HATİP' in lise_adi):
                                try:
                                    yerlesen_text = cells[1].text.strip()
                                    yerlesen = re.findall(r'\d+', yerlesen_text)
                                    
                                    year_result['imam_hatip_liseler'].append({
                                        'lise': lise_adi,
                                        'yerlesen': int(yerlesen[0]) if yerlesen else None
                                    })
                                except:
                                    pass
            
            if year_result['imam_hatip_liseler']:
                print(f"     ✓ {len(year_result['imam_hatip_liseler'])} İmam Hatip lisesi bulundu")
                
        except:
            pass
        
        return year_result
    
    def extract_university_type(self, university_name):
        """Üniversite adından tipini çıkar (Devlet/Vakıf/KKTC)"""
        name_upper = university_name.upper()
        
        # KKTC üniversiteleri
        kktc_keywords = ['KKTC', 'KIBRIS', 'YAKIN DOĞU', 'DOĞU AKDENİZ', 'LEFKE', 
                         'GİRNE', 'ULUSLARARASI KIBRIS']
        for keyword in kktc_keywords:
            if keyword in name_upper:
                return 'KKTC'
        
        # Vakıf üniversiteleri belirteçleri
        vakif_keywords = ['VAKIF', 'ÖZEL', 'ÜCRETLİ', 'BURSLU', 'İNDİRİMLİ']
        for keyword in vakif_keywords:
            if keyword in name_upper:
                return 'Vakıf'
        
        # Bazı bilinen vakıf üniversiteleri
        vakif_univs = ['ALTINBAŞ', 'ANKARA MEDIPOL', 'ANKARA BİLİM', 'ATILIM', 
                       'BAHÇEŞEHİR', 'BAŞKENT', 'BEYKENT', 'BİRUNİ', 'ÇAĞ', 
                       'ÇANKAYA', 'DOĞUŞ', 'FENERBAHÇE', 'HALIÇ', 'İSTANBUL AREL',
                       'İSTANBUL AYDIN', 'İSTANBUL BİLGİ', 'İSTANBUL GELİŞİM',
                       'İSTANBUL KAVRAM', 'İSTANBUL KENT', 'İSTANBUL KÜLTÜR',
                       'İSTANBUL MEDENİYET', 'İSTANBUL MEDIPOL', 'İSTANBUL OKAN',
                       'İSTANBUL RUMELI', 'İSTANBUL SABAHATTİN ZAİM', 'İSTANBUL TİCARET',
                       'İSTANBUL YENİ YÜZYIL', 'İSTİNYE', 'İZMİR EKONOMİ',
                       'KADİR HAS', 'KONYA GIDA', 'KTO KARATAY', 'MALTEPE',
                       'MEF', 'NİŞANTAŞI', 'ÖZYEĞIN', 'PIRI REİS', 'SABANCI',
                       'TED', 'TOBB ETÜ', 'TOROS', 'UFUK', 'UFUK', 'ÜSKÜDAR',
                       'YEDİTEPE', 'YÜKSEK İHTİSAS']
        
        for vakif_univ in vakif_univs:
            if vakif_univ in name_upper:
                return 'Vakıf'
        
        return 'Devlet'
    
    def get_university_data(self, university, max_retries=3):
        """Üniversite sayfasından 3 yıllık veri + İmam Hatip analizleri çek"""
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                years_data = {}
                
                # Önce 2025 sayfasını yükle
                if retry_count > 0:
                    print(f"     🔄 Yeniden deneme {retry_count}/{max_retries}...")
                    time.sleep(5)  # Yeniden denemeden önce biraz bekle
                
                print(f"\n     → 2025 yılı verileri çekiliyor...")
                self.driver.get(university['url'])
                time.sleep(3)
                
                # Üniversite ismi, şehir, tip ve bölüm bilgisini sayfadan çek
                univ_info = self.get_university_info_from_page()
                university_name = univ_info['university_name']
                city = univ_info['city']
                university_type = univ_info['university_type']  # Sayfadan çekilen tip
                program_name_from_page = univ_info['program_name']  # Sayfadan çekilen bölüm ismi
                
                # Eğer sayfadan tip alınamadıysa, fallback olarak tahmin et
                if not university_type:
                    university_type = self.extract_university_type(university_name) if university_name else 'Devlet'
                
                # 2025 verilerini çek
                year_2025_data = self.get_year_data('2025')
                years_data['2025'] = year_2025_data
                
                print(f"     ✓ 2025: Üniversite={university_name}, Şehir={city}, Puan={year_2025_data['puan_turu']}, Yerleşen={year_2025_data['yerlesen']}, Fakülte={year_2025_data['fakulte']}, İH Tip={len(year_2025_data['imam_hatip_lise_tipi'])}, İH Lise={len(year_2025_data['imam_hatip_liseler'])}")
                
                # Şimdi sayfadaki yıl linklerini bul
                year_links = {}
                try:
                    all_links = self.driver.find_elements(By.TAG_NAME, 'a')
                    
                    for link in all_links:
                        try:
                            href = link.get_attribute('href')
                            text = link.text.strip()
                            
                            if href and '/2024/lisans.php' in href and '2024' in text:
                                year_links['2024'] = href
                            
                            if href and '/2023/lisans.php' in href and '2023' in text:
                                year_links['2023'] = href
                        except:
                            continue
                    
                    print(f"     → Yıl linkleri bulundu: {list(year_links.keys())}")
                    
                except Exception as e:
                    print(f"     ⚠️  Yıl linkleri bulunamadı: {e}")
                
                # 2024 ve 2023 verilerini çek
                for year in ['2024', '2023']:
                    if year in year_links:
                        print(f"\n     → {year} yılı verileri çekiliyor...")
                        try:
                            self.driver.get(year_links[year])
                            time.sleep(3)
                            print(f"     ✓ {year} sayfasına geçildi")
                            
                            year_data = self.get_year_data(year)
                            years_data[year] = year_data
                            
                            print(f"     ✓ {year}: Puan={year_data['puan_turu']}, Yerleşen={year_data['yerlesen']}, Fakülte={year_data['fakulte']}, İH Tip={len(year_data['imam_hatip_lise_tipi'])}, İH Lise={len(year_data['imam_hatip_liseler'])}")
                            
                        except Exception as e:
                            print(f"     ⚠️  {year} verisi alınamadı: {e}")
                    else:
                        print(f"\n     → {year} yılı linki bulunamadı, atlanıyor...")
                
                return {
                    'years_data': years_data, 
                    'city': city, 
                    'university_name': university_name, 
                    'university_type': university_type,
                    'program_name': program_name_from_page
                }
                
            except Exception as e:
                last_error = str(e)
                retry_count += 1
                
                if retry_count < max_retries:
                    print(f"     ⚠️  Hata oluştu: {e}")
                    print(f"     🔄 {max_retries - retry_count} deneme hakkı kaldı...")
                    continue
                else:
                    print(f"     ❌ {max_retries} deneme sonrası başarısız: {e}")
                    self.stats['errors'] += 1
                    return None
        
        # Başarısız tüm denemeler
        print(f"     ❌ Tüm denemeler başarısız oldu. Son hata: {last_error}")
        self.stats['errors'] += 1
        return None
    
    def load_existing_data(self, filename='yokatlas_data_temp.json'):
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                self.data = data.get('data', [])
                old_stats = data.get('metadata', {}).get('stats', {})
                
                self.stats['total_records'] = len(self.data)
                
                print(f"\n✅ Önceki veri bulundu!")
                print(f"   📊 {len(self.data)} kayıt yüklendi")
                print(f"   📚 {old_stats.get('programs_scanned', 0)} program taranmıştı")
                print(f"   🏛️  {old_stats.get('universities_scanned', 0)} üniversite taranmıştı\n")
                
                return True
        except Exception as e:
            print(f"⚠️  Önceki veri yüklenemedi: {e}")
            return False
    
    def is_already_scraped(self, program_name, university_code):
        """Belirli bir program-üniversite kombinasyonunun taranıp taranmadığını kontrol et"""
        for record in self.data:
            # university_code ile kontrol (kod hala parametre olarak geliyor)
            if record.get('program_name') == program_name and university_code:
                # Aynı program için bu üniversite kodunu daha önce gördük mü?
                # URL'den university_code çıkararak karşılaştır
                existing_url = record.get('university_url', '')
                if f'y={university_code}' in existing_url:
                    return True
        return False
    
    def save_to_json(self, filename='yokatlas_data.json'):
        output = {
            'metadata': {
                'total_records': len(self.data),
                'stats': self.stats,
                'scraped_at': datetime.now().isoformat()
            },
            'data': self.data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Veriler '{filename}' dosyasına kaydedildi!")
    
    def get_scanned_programs(self):
        """Daha önce taranan programların kodlarını döndür"""
        scanned = set()
        for record in self.data:
            # program_url'den program kodunu çıkar
            url = record.get('program_url', '')
            if 'b=' in url:
                code = url.split('b=')[1].split('&')[0]
                if code:
                    scanned.add(code)
        return scanned
    
    def scrape_all(self, limit_programs=None, limit_universities=None, resume=True):
        print("\n" + "="*70)
        print("🚀 YÖK ATLAS SELENİUM SCRAPER BAŞLATILIYOR")
        print("="*70 + "\n")
        
        self.stats['start_time'] = datetime.now().isoformat()
        
        if resume:
            self.load_existing_data('yokatlas_data_temp.json')
        
        self.setup_driver()
        
        programs = self.get_all_programs()
        
        if not programs:
            print("❌ Program listesi alınamadı!")
            return
        
        # Eksik programları kontrol et
        if resume:
            scanned_program_codes = self.get_scanned_programs()
            missing_programs = [p for p in programs if p['code'] not in scanned_program_codes]
            
            if missing_programs:
                print(f"\n⚠️  {len(missing_programs)} eksik program tespit edildi!")
                print(f"📊 Toplam program: {len(programs)}")
                print(f"✅ Tamamlanan: {len(scanned_program_codes)}")
                print(f"❌ Eksik: {len(missing_programs)}")
                
                retry_missing = input("\nEksik programları taramak ister misiniz? (evet/hayır): ").strip().lower()
                if retry_missing == 'evet':
                    print(f"\n🔄 Sadece {len(missing_programs)} eksik program taranacak!\n")
                    programs = missing_programs
                else:
                    print("\nℹ️  Normal taramaya devam ediliyor...\n")
        
        if limit_programs:
            programs = programs[:limit_programs]
            print(f"ℹ️  İlk {limit_programs} program taranacak\n")
        
        for prog_idx, program in enumerate(programs, 1):
            print(f"\n[{prog_idx}/{len(programs)}] 📖 {program['name']} ({program['code']})")
            
            # Bu programı daha önce taradık mı kontrol et
            if resume and program['code'] in self.get_scanned_programs():
                print(f"   ⏭️  Bu program zaten tamamen tarandı, atlanıyor...")
                continue
            
            self.stats['programs_scanned'] += 1
            
            universities = self.get_universities_for_program(program)
            
            if limit_universities:
                universities = universities[:limit_universities]
            
            for univ_idx, university in enumerate(universities, 1):
                if self.is_already_scraped(program['name'], university['code']):
                    print(f"     [{univ_idx}/{len(universities)}] ⏭️  {university['name'][:50]}... (Zaten tarandı, atlanıyor)")
                    continue
                
                print(f"     [{univ_idx}/{len(universities)}] 🏛️  {university['name'][:50]}...")
                
                result = self.get_university_data(university)
                
                if result:
                    self._save_result(program, university, result)
                    self.stats['universities_scanned'] += 1
                else:
                    print(f"     ⚠️  Veri alınamadı")
                
                time.sleep(1)
        
        self.stats['end_time'] = datetime.now().isoformat()
        
        self.print_summary()
        
        # Eksik program kontrolü
        if not limit_programs:  # Sadece tam taramada kontrol et
            print("\n" + "="*70)
            print("🔍 EKSİK PROGRAM KONTROLÜ")
            print("="*70)
            
            all_programs = self.get_all_programs()
            scanned_program_codes = self.get_scanned_programs()
            missing_programs = [p for p in all_programs if p['code'] not in scanned_program_codes]
            
            if missing_programs:
                print(f"\n⚠️  {len(missing_programs)} eksik program tespit edildi!")
                print(f"\nEksik programlar:")
                for p in missing_programs[:10]:  # İlk 10'unu göster
                    print(f"   • {p['name']} ({p['code']})")
                if len(missing_programs) > 10:
                    print(f"   ... ve {len(missing_programs) - 10} tane daha")
                
                retry = input(f"\nEksik {len(missing_programs)} programı şimdi taramak ister misiniz? (evet/hayır): ").strip().lower()
                if retry == 'evet':
                    print(f"\n🔄 Eksik programlar taranıyor...\n")
                    
                    # Eksik programları tara
                    for prog_idx, program in enumerate(missing_programs, 1):
                        print(f"\n[EKSİK {prog_idx}/{len(missing_programs)}] 📖 {program['name']} ({program['code']})")
                        self.stats['programs_scanned'] += 1
                        
                        universities = self.get_universities_for_program(program)
                        
                        for univ_idx, university in enumerate(universities, 1):
                            if self.is_already_scraped(program['name'], university['code']):
                                print(f"     [{univ_idx}/{len(universities)}] ⏭️  {university['name'][:50]}... (Zaten tarandı)")
                                continue
                            
                            print(f"     [{univ_idx}/{len(universities)}] 🏛️  {university['name'][:50]}...")
                            
                            result = self.get_university_data(university)
                            
                            if result:
                                self._save_result(program, university, result)
                                self.stats['universities_scanned'] += 1
                            
                            time.sleep(1)
                    
                    self.save_to_json('yokatlas_data_final.json')
                    print("\n✅ Eksik programlar tamamlandı!")
            else:
                print("\n✅ Tüm programlar başarıyla tarandı! Eksik yok.")
        
        self.driver.quit()
    
    def _save_result(self, program, university, result):
        """Sonucu kaydet (kod tekrarını önlemek için yardımcı fonksiyon)"""
        years_data = result['years_data']
        city = result['city']
        university_name = result['university_name']
        university_type = result['university_type']
        program_name = result['program_name']
        
        if not university_name:
            university_name = university['name']
        if not university_type:
            university_type = self.extract_university_type(university_name)
        if not program_name:
            program_name = program['name']
        
        for year, data in years_data.items():
            if data['yerlesen'] is not None or data['puan_turu'] is not None:
                record = {
                    'program_name': program_name,
                    'program_url': program['url'],
                    'university_name': university_name,
                    'university_type': university_type,
                    'city': city,
                    'fakulte': data.get('fakulte'),
                    'university_url': university['url'],
                    'year': year,
                    'puan_turu': data['puan_turu'],
                    'toplam_yerlesen': data['yerlesen'],
                    'imam_hatip_lise_tipi': data['imam_hatip_lise_tipi'],
                    'imam_hatip_liseler': data['imam_hatip_liseler']
                }
                
                self.data.append(record)
                self.stats['total_records'] += 1
                self.save_to_json('yokatlas_data_temp.json')
        
        print(f"     ✅ 3 yıllık veri kaydedildi (Üniversite: {university_name}, Şehir: {city})")
    
    def print_summary(self):
        print("\n" + "="*70)
        print("✨ TARAMA TAMAMLANDI!")
        print("="*70)
        print(f"📚 Taranan Program: {self.stats['programs_scanned']}")
        print(f"🏛️  Taranan Üniversite: {self.stats['universities_scanned']}")
        print(f"📊 Toplam Kayıt: {self.stats['total_records']}")
        print(f"❌ Hata Sayısı: {self.stats['errors']}")
        
        if self.stats['start_time'] and self.stats['end_time']:
            start = datetime.fromisoformat(self.stats['start_time'])
            end = datetime.fromisoformat(self.stats['end_time'])
            duration = (end - start).total_seconds()
            print(f"⏱️  Süre: {duration:.1f} saniye ({duration/60:.1f} dakika)")
        
        print("="*70)


def main():
    print("YÖK Atlas Selenium Web Scraper")
    print("-" * 70)
    print("Bu scraper GERÇEK bir tarayıcı açar ve YÖK Atlas'ta gezinir.\n")
    
    resume_available = os.path.exists('yokatlas_data_temp.json')
    resume = False
    
    if resume_available:
        print("⚠️  Önceki tarama verisi bulundu!")
        resume_choice = input("Kaldığı yerden devam etmek ister misiniz? (evet/hayır): ").strip().lower()
        if resume_choice == 'evet':
            resume = True
            print("✅ Kaldığı yerden devam edilecek!\n")
        else:
            print("ℹ️  Sıfırdan başlanacak\n")
    
    print("Tarayıcı modu:")
    print("1. Canlı (Tarayıcıyı görebilirsiniz - ÖNERİLEN)")
    print("2. Headless (Arka planda çalışır)")
    
    mode = input("\nSeçiminiz (1/2): ").strip()
    headless = (mode == '2')
    
    print("\nKaç program taranacak?")
    print("1. Test (İlk 2 program)")
    print("2. Kısmi (İlk 5 program)")
    print("3. Tam (TÜM programlar - saatler sürebilir!)")
    
    choice = input("\nSeçiminiz (1/2/3): ").strip()
    
    if choice == '1':
        limit_prog = 2
        limit_univ = 3
    elif choice == '2':
        limit_prog = 5
        limit_univ = 5
    elif choice == '3':
        limit_prog = None
        limit_univ = None
        print("\n⚠️  UYARI: Tam tarama saatler sürebilir!")
        confirm = input("Devam etmek istediğinizden emin misiniz? (evet/hayır): ")
        if confirm.lower() != 'evet':
            print("İptal edildi.")
            return
    else:
        print("Geçersiz seçim!")
        return
    
    scraper = YokAtlasSeleniumScraper(headless=headless)
    
    try:
        scraper.scrape_all(
            limit_programs=limit_prog,
            limit_universities=limit_univ,
            resume=resume
        )
        
        if scraper.data:
            scraper.save_to_json('yokatlas_data_final.json')
            
            print("\n📁 Dosyalar:")
            print("  - yokatlas_data_final.json (Tüm veriler)")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Kullanıcı tarafından durduruldu!")
        if scraper.data:
            scraper.save_to_json('yokatlas_data_interrupted.json')
            print("💾 Mevcut veriler 'yokatlas_data_interrupted.json' dosyasına kaydedildi")
            print("\n💡 Kaldığı yerden devam etmek için scripti tekrar çalıştırın!")
        if scraper.driver:
            scraper.driver.quit()
    
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")
        import traceback
        traceback.print_exc()
        if scraper.data:
            scraper.save_to_json('yokatlas_data_error.json')
            print("💾 Veriler 'yokatlas_data_error.json' dosyasına kaydedildi")
        if scraper.driver:
            scraper.driver.quit()


if __name__ == "__main__":
    main()