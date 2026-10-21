# Görsel Üret

Referans ürün fotoğraflarını Leonardo API ile e-ticaret stüdyo görsellerine dönüştüren Python aracı.

## Gereksinimler

- Python 3.10 veya üzeri
- Leonardo API anahtarı

## Kurulum

1. Depoyu klonlayın ve proje klasörüne geçin.
2. `requirements.txt` içindeki paketleri kurun:

   ```powershell
   py -m pip install -r requirements.txt
   ```

3. Proje klasöründe `.env` dosyası oluşturup API anahtarını ekleyin:

   ```text
   LEONARDO_API_KEY=anahtariniz
   ```

4. Referans görsellerini `referans/` klasörüne koyup `Gorsel-Uret.bat` dosyasını çalıştırın.

Üretilen görseller `cikti/` klasörüne kaydedilir. Bu klasör Git tarafından izlenmez.
