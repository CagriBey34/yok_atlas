# 🎓 YÖK Atlas Veri Çekici

Tüm lisans programlarının tüm üniversitelerinden **yerleşen öğrenci sayılarını** otomatik olarak çeken web scraper uygulaması.

## 📦 İçerik

1. **flask_scraper.py** - 🌟 Ana uygulama (ÖNERİLEN)
   - Canlı web arayüzü ile veri çekme
   - Gerçek zamanlı takip
   - Excel/CSV export
   - Python Flask backend

2. **yokatlas_scraper.py** - 🔧 Komut satırı scripti
   - Doğrudan Python ile çalışır
   - Terminal üzerinden veri çeker
   - CSV ve JSON export

3. **yokatlas_scraper.html** - 🌐 Demo web arayüzü
   - Sadece görsel demo
   - CORS kısıtlaması nedeniyle gerçek veri çekemez
   - Tasarım referansı

## 🚀 Hızlı Başlangıç

### Yöntem 1: Web Arayüzü ile (ÖNERİLEN)

```bash
# Gerekli kütüphaneleri yükle
pip install flask requests beautifulsoup4

# Uygulamayı başlat
python3 flask_scraper.py

# Tarayıcıda aç
# http://localhost:5000
```

**Kullanım:**
1. Tarayıcınızda `http://localhost:5000` adresini açın
2. "Program Limiti" belirleyin (test için 3-5 yeterli)
3. "🚀 Başlat" butonuna tıklayın
4. Canlı olarak verileri izleyin
5. "📥 CSV İndir" ile verileri kaydedin

### Yöntem 2: Komut Satırı ile

```bash
# Gerekli kütüphaneleri yükle
pip install requests beautifulsoup4

# Scripti çalıştır
python3 yokatlas_scraper.py

# Menüden seçim yapın:
# 1 = Test (3 program)
# 2 = Kısmi (10 program)
# 3 = Tam tarama (TÜM programlar)
```

## 📊 Çıktı Formatı

### CSV Formatı
```csv
Sıra,Bölüm Kodu,Bölüm Adı,Üniversite Kodu,Üniversite Adı,Puan Türü,Yerleşen,Zaman
1,11701,"Bilgisayar Mühendisliği",111490229,"İstanbul Teknik Üniversitesi",SAY,156,2024-02-06T...
2,11702,"İşletme",111490230,"Ankara Üniversitesi",EA,142,2024-02-06T...
3,11703,"Hukuk",111490231,"İstanbul Üniversitesi",SÖZ,98,2024-02-06T...
```

### JSON Formatı
```json
{
  "data": [
    {
      "program_code": "11701",
      "program_name": "Bilgisayar Mühendisliği",
      "university_code": "111490229",
      "university_name": "İstanbul Teknik Üniversitesi",
      "puan_turu": "SAY",
      "yerlesen": 156,
      "timestamp": "2024-02-06T12:30:45"
    }
  ],
  "stats": {
    "programs": 150,
    "universities": 2500,
    "total": 5000
  }
}
```

### Puan Türleri
- **SAY**: Sayısal (Mavi renkle gösterilir)
- **SÖZ**: Sözel (Yeşil renkle gösterilir)
- **EA**: Eşit Ağırlık (Sarı renkle gösterilir)
- **DİL**: Dil (Turkuaz renkle gösterilir)

## ⚙️ Nasıl Çalışır?

1. **Program Listesi**: Ana sayfadan tüm lisans programlarını çeker
2. **Üniversite Listesi**: Her program için üniversiteleri listeler
3. **Veri Çekme**: Her üniversite için:
   - "Genel Bilgiler" bölümünden **Puan Türü** (SAY/SÖZ/EA/DİL)
   - "Kontenjan, Yerleşme ve Kayıt İstatistikleri" bölümünden **Yerleşen** sayısı
4. **Kayıt**: Tüm veriyi CSV/JSON formatında kaydeder

## 🔍 URL Yapısı ve Çekilen Veriler

- Ana Sayfa: `https://yokatlas.yok.gov.tr/lisans-anasayfa.php`
- Bölüm Sayfası: `https://yokatlas.yok.gov.tr/lisans-bolum.php?b={PROGRAM_CODE}`
- Üniversite Sayfası: `https://yokatlas.yok.gov.tr/lisans.php?y={UNIVERSITY_CODE}`

### Her Üniversite için Çekilen Veriler:
1. **Yerleşen Sayısı**: "Kontenjan, Yerleşme ve Kayıt İstatistikleri" tablosundan
2. **Puan Türü**: "Genel Bilgiler" bölümünden (SAY, SÖZ, EA, DİL)

## ⚠️ Önemli Notlar

### 1. Rate Limiting
- Her istek arasında 0.5-1.5 saniye bekleme var
- Sunucuyu yormamak için gerekli
- Değiştirmek isterseniz `delay` parametresini ayarlayın

### 2. Tam Tarama
- **TÜM programları taramak saatler sürebilir!**
- Önerilen: İlk başta test modu ile deneyin (3-5 program)
- Tam tarama için bilgisayarınızın açık kalması gerekir

### 3. CORS Sorunu
- HTML dosyası direkt tarayıcıdan YÖK Atlas'a erişemez
- CORS (Cross-Origin Resource Sharing) politikası bunu engelliyor
- Bu nedenle Python backend kullanılmalı

### 4. Bağlantı Hataları
- Bazı ağlarda YÖK Atlas'a erişim engellenmiş olabilir
- VPN kullanmanız gerekebilir
- Üniversite/kurumsal ağlarda sorun yaşanabilir

## 🛠️ Gereksinimler

```bash
Python 3.7+
requests>=2.31.0
beautifulsoup4>=4.12.0
flask>=3.0.0 (sadece web arayüzü için)
```

## 📈 İstatistikler

Canlı olarak şunları takip edebilirsiniz:
- ✅ Taranan program sayısı
- ✅ Taranan üniversite sayısı
- ✅ Toplam veri sayısı
- ✅ Anlık durum
- ✅ İlerleme çubuğu

## 🎯 Özellikler

### Web Arayüzü (flask_scraper.py)
- ✅ Canlı veri çekme
- ✅ Gerçek zamanlı istatistikler
- ✅ Progress bar
- ✅ Log kayıtları
- ✅ Durdur/Devam et
- ✅ CSV export
- ✅ Veri temizleme
- ✅ Responsive tasarım
- ✅ Güzel arayüz

### Komut Satırı (yokatlas_scraper.py)
- ✅ Terminal üzerinden çalışma
- ✅ 3 farklı mod (test/kısmi/tam)
- ✅ CSV ve JSON export
- ✅ Detaylı log
- ✅ Hata yönetimi

## 🐛 Sorun Giderme

### "ModuleNotFoundError: No module named 'requests'"
```bash
pip install requests beautifulsoup4 flask
```

### "Connection refused" hatası
- YÖK Atlas sitesi erişilebilir mi kontrol edin
- VPN deneyin
- İnternet bağlantınızı kontrol edin

### Veri çekilmiyor
- URL yapısı değişmiş olabilir
- YÖK Atlas sitesi güncellenmiş olabilir
- Script'i güncellemeniz gerekebilir

## 📝 Lisans

Bu proje eğitim amaçlıdır. YÖK Atlas'ın kullanım koşullarına uygun şekilde kullanın.

## 🤝 Katkıda Bulunma

Hata bulursanız veya iyileştirme öneriniz varsa lütfen bildirin!

## 📧 İletişim

Sorularınız için GitHub issue açabilirsiniz.

---

**Not:** Bu araç YÖK Atlas'tan halka açık verileri toplamaktadır. Lütfen sorumlu kullanın ve YÖK Atlas sunucularını yormayın.
# y-k_atlas
