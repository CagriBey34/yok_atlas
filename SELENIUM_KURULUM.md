# 🌐 YÖK Atlas Selenium Scraper Kurulum Kılavuzu

## 🎯 Bu Scraper Ne Yapar?

**GERÇEK BİR TARAYICI AÇAR** ve sizin yerinize YÖK Atlas sitesinde:
1. ✅ Her programa tıklar
2. ✅ Her üniversiteye girer
3. ✅ "Genel Bilgiler" panelini açar → Puan Türü'nü okur
4. ✅ "Kontenjan, Yerleşme ve Kayıt İstatistikleri" sekmesine tıklar → Yerleşen sayısını okur
5. ✅ Her veriyi **JSON dosyasına** kaydeder

**CANLI İZLEYEBİLİRSİNİZ!** Tarayıcı açık olur, ne yaptığını görebilirsiniz.

---

## 📦 Kurulum

### 1️⃣ Selenium Kütüphanesini Yükleyin

```bash
pip3 install selenium
```

### 2️⃣ Chrome Driver'ı Yükleyin

**macOS (Homebrew ile):**
```bash
brew install chromedriver
```

**veya Manuel:**
1. [ChromeDriver İndir](https://chromedriver.chromium.org/downloads)
2. Chrome sürümünüze uygun olanı indirin
3. `/usr/local/bin/` klasörüne kopyalayın

**Test edin:**
```bash
chromedriver --version
```

---

## 🚀 Kullanım

```bash
python3 selenium_scraper.py
```

### Karşınıza Çıkacak Seçenekler:

**1. Tarayıcı Modu:**
- **Canlı (Önerilen)**: Tarayıcıyı görebilirsiniz, ne yaptığını izlersiniz
- **Headless**: Arka planda çalışır, görmezsiniz

**2. Tarama Miktarı:**
- **Test (2 program)**: Hızlı test için
- **Kısmi (5 program)**: Orta seviye
- **Tam (TÜM programlar)**: Saatler sürer!

---

## 📊 Çıktı Formatı

### JSON Dosyası: `yokatlas_data_final.json`

```json
{
  "metadata": {
    "total_records": 150,
    "stats": {
      "programs_scanned": 10,
      "universities_scanned": 145,
      "total_records": 150,
      "errors": 5,
      "start_time": "2024-02-06T10:30:00",
      "end_time": "2024-02-06T10:45:00"
    },
    "scraped_at": "2024-02-06T10:45:00"
  },
  "data": [
    {
      "program_code": "11701",
      "program_name": "Bilgisayar Mühendisliği",
      "university_code": "111490229",
      "university_name": "İstanbul Teknik Üniversitesi",
      "puan_turu": "SAY",
      "yerlesen": 156,
      "timestamp": "2024-02-06T10:30:15"
    },
    {
      "program_code": "11702",
      "program_name": "İşletme",
      "university_code": "111490230",
      "university_name": "Ankara Üniversitesi",
      "puan_turu": "EA",
      "yerlesen": 142,
      "timestamp": "2024-02-06T10:30:18"
    }
  ]
}
```

---

## ⚙️ Özellikler

### ✅ Otomatik Kaydetme
- Her 10 kayıtta bir geçici dosyaya yazar (`yokatlas_data_temp.json`)
- Kesinti olursa veri kaybı olmaz

### ✅ Hata Yönetimi
- Bir üniversitede hata olursa diğerine geçer
- Hata sayısını loglar

### ✅ Canlı İzleme
- Terminal'de her adımı görebilirsiniz:
  ```
  [2/10] 📖 Bilgisayar Mühendisliği (11701)
    → 45 üniversite bulundu
    [1/45] 🏛️  İstanbul Teknik Üniversitesi... ✅ Yerleşen: 156, Puan: SAY
    [2/45] 🏛️  Orta Doğu Teknik Üniversitesi... ✅ Yerleşen: 142, Puan: SAY
  ```

### ✅ Güvenli Durdurma
- Ctrl+C ile durdurduğunuzda mevcut verileri kaydeder

---

## 🎮 Örnek Kullanım

### Test Modu (Hızlı Deneme):
```bash
python3 selenium_scraper.py

# Seçimler:
# 1. Canlı mod
# 1. Test (2 program)

# Sonuç: ~5 dakikada 10-20 kayıt
```

### Tam Tarama:
```bash
python3 selenium_scraper.py

# Seçimler:
# 1. Canlı mod (veya 2. Headless)
# 3. Tam

# Sonuç: Saatler sonra binlerce kayıt
```

---

## 🐛 Sorun Giderme

### "chromedriver not found"
```bash
# macOS:
brew install chromedriver

# veya manuel indirin:
# https://chromedriver.chromium.org/downloads
```

### "This version of ChromeDriver only supports Chrome version X"
Chrome sürümünüze uygun ChromeDriver indirin:
1. Chrome sürümünüzü öğrenin: chrome://version
2. Uygun driver'ı indirin: https://chromedriver.chromium.org/downloads

### Tarayıcı açılmıyor
```bash
# ChromeDriver'ın çalıştırılabilir olduğundan emin olun:
chmod +x /usr/local/bin/chromedriver

# Güvenlik ayarlarından izin verin (macOS):
xattr -d com.apple.quarantine /usr/local/bin/chromedriver
```

### "selenium module not found"
```bash
pip3 install selenium
```

---

## 💡 İpuçları

1. **İlk önce TEST modunda deneyin** - Sistemin çalıştığından emin olun
2. **Canlı modda izleyin** - İlk birkaç taramada ne yaptığını görün
3. **Veri kaybı yok** - Kesinti olursa temp dosyasından devam edebilirsiniz
4. **JSON'u Excel'e çevirin**:
   ```python
   import json
   import pandas as pd
   
   with open('yokatlas_data_final.json') as f:
       data = json.load(f)
   
   df = pd.DataFrame(data['data'])
   df.to_excel('yokatlas_data.xlsx', index=False)
   ```

---

## 🆚 Diğer Scraper'lardan Farkı

| Özellik | BeautifulSoup | Selenium |
|---------|---------------|----------|
| Tarayıcı açar | ❌ | ✅ |
| JavaScript çalışır | ❌ | ✅ |
| Tıklama yapabilir | ❌ | ✅ |
| Dinamik içerik | ❌ | ✅ |
| CORS sorunu | ✅ Var | ❌ Yok |
| Hız | Hızlı | Yavaş |
| İzleyebilirsiniz | ❌ | ✅ |

**Sonuç:** Selenium daha yavaş ama %100 çalışır!

---

## 📞 Yardım

Sorun yaşarsanız:
1. Terminal'deki hata mesajlarını okuyun
2. ChromeDriver sürümünü kontrol edin
3. Test moduyla başlayın
4. Canlı modda ne yaptığını izleyin

İyi taramalar! 🚀
