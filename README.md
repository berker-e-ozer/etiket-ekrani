# Ürün Etiket Ekranı (`etiket_ekrani`)

Raf fiyat etiketi basmak için Flask modülü. Akış:

1. **Ürün seçimi:** Sistemdeki ürünler listelenir, aranır, seçilir.
2. **Fiyat ve birim:** Sistemde fiyat/birim varsa dolu gelir, istenirse değiştirilir ("Sisteme dön" ile geri alınır). Fiyatı olmayan ürüne elle girilir. Birim listeden seçilir ya da yazılır (TL/kg, TL/250g, TL/Paket…).
3. **Önizleme ve ayarlar:** Etiket boyutu, boşluklar ve her alan için yazı tipi / boyut / kalınlık ayarlanır, önizleme anında güncellenir. Tarayıcıdan yazdırılır ya da yazıcıya gönderilir.

Etiket içeriği: ürün adı (üstte), fiyat + birim aynı satırda (ortada), altta sola hizalı "Üretim Yeri" ve "Fiyat Değişiklik Tarihi".
Tarih kuralı: fiyat sistemdekiyle aynıysa sistemdeki fiyat değişiklik tarihi, değiştirildiyse ya da sistemde fiyat yoksa bugünün tarihi.

## Dosyalar

```
services/etiket_ekrani_service.py   # iş mantığı ve SQL
routes_etiket_ekrani.py             # Blueprint: bp = Blueprint("etiket_ekrani", __name__)
templates/etiket_ekrani.html        # {% extends "base.html" %}, yalnızca {% block content %}
static/etiket_ekrani.js             # düz JavaScript + fetch
tests/test_etiket_ekrani.py         # sahte veriyle testler
sahte_veri.json                     # geliştirme ürün verisi
dev_run.py                          # yalnızca yerel geliştirme
dev/base.html                       # yalnızca yerel geliştirme (ana sisteme taşınmaz)
```

## Yerelde çalıştırma

```bash
python -m pip install flask
python dev_run.py
```

Tarayıcıda `http://localhost:5000/etiket-ekrani`.

Testler:

```bash
python -m unittest tests.test_etiket_ekrani -v
```

## Ana sisteme alma (Alp için)

Taşınacaklar: `services/etiket_ekrani_service.py`, `routes_etiket_ekrani.py`, `templates/etiket_ekrani.html`, `static/etiket_ekrani.js`.
Taşınmayacaklar: `dev_run.py`, `dev/`, `sahte_veri.json` (gerçek kaynağa bağlandıktan sonra).

```python
from routes_etiket_ekrani import bp as etiket_ekrani_bp
from services.etiket_ekrani_service import init_schema as etiket_ekrani_init_schema

app.register_blueprint(etiket_ekrani_bp)
etiket_ekrani_init_schema()   # açılışta; 3 işçi aynı anda çalıştırsa da güvenli
```

Veritabanı yolu `ETIKET_DB_YOLU` ortam değişkeninden okunur (varsayılan `etiket_ekrani.db`). Ana sistemin SQLite dosyasına yönlendirilmeli.

Şablon `base.html`'den şunları bekler: Tailwind (CDN), Phosphor Icons, `showLoading(mesaj)` / `hideLoading()`.

### Bağlanacak fonksiyonlar

| Fonksiyon | Şu an | Bağlanacak |
|---|---|---|
| `urunleri_getir()` | `sahte_veri.json` okur | Sistemdeki ürün listesi |
| `etiket_bas(urun_id, urun_adi, fiyat, birim, fiyat_tarihi)` | `etiket_basim_log`'a yazar, `{"ok": True}` döner | Gerçek yazıcı |
| Kullanıcı | Sabit `"test"` | Oturumdaki kullanıcı |

`urunleri_getir()` şu biçimde liste döndürmeli:

```json
{"id": "urun-001", "ad": "MOR İSOT ORTA ACI", "birim": "TL/kg", "uretim_yeri": "Türkiye", "fiyat": 650.0, "fiyat_tarihi": "2026-05-02"}
```

`fiyat` sayı ya da `null`, `fiyat_tarihi` `YYYY-AA-GG` ya da `null`.

### Veritabanı (yalnızca yeni tablolar)

- `etiket_ayarlari`: kullanıcı başına etiket görünüm ayarları (JSON), `kullanici`, `zaman`
- `etiket_basim_log`: basım geçmişi (`urun_id`, `urun_adi`, `fiyat`, `birim`, `fiyat_tarihi`, `kullanici`, `durum`, `zaman`)

Tümü `init_schema()` içinde `CREATE TABLE IF NOT EXISTS`; sonradan eklenen kolonlar `ALTER TABLE … ADD COLUMN` + "duplicate column" yutulur. Mevcut tablolara dokunulmaz.

## API

| Yol | Metot | Açıklama |
|---|---|---|
| `/etiket-ekrani` | GET | Sayfa |
| `/api/etiket-ekrani/urunler` | GET | Ürün listesi |
| `/api/etiket-ekrani/ayarlar` | GET | Kayıtlı ayarlar (yoksa varsayılan) |
| `/api/etiket-ekrani/ayarlar` | POST | Ayar kaydet (yalnızca bilinen anahtarlar) |
| `/api/etiket-ekrani/bas` | POST | `{"etiketler": [{"id", "ad", "fiyat", "birim", "fiyat_tarihi"}]}` |

Hatalarda `{"error": "Türkçe mesaj"}` ve uygun HTTP kodu (400 / 500) döner; teknik ayrıntı sunucu loguna yazılır.
