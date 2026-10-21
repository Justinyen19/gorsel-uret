import os
import sys
import requests
import json
import time
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()
API_KEY = os.getenv("LEONARDO_API_KEY")

# Kullanıcı tarafından istenen yollar
REF_DIR = Path(__file__).resolve().parent / "referans"
OUT_DIR = Path(__file__).resolve().parent / "cikti"

# -- AYARLAR --
DEFAULT_PROMPT = """GÖREV:

Verilen referans ürün görselini profesyonel bir sanal market / e-ticaret stüdyo ürün fotoğrafına dönüştür.

ÖNCE REFERANS GÖRSELİ DİKKATLİCE ANALİZ ET, SONRA DÖNÜŞTÜR.

Bu işlem yeni bir ürün görseli tasarlama görevi değildir.

Referans görseldeki GERÇEK ÜRÜN korunacaktır. Yalnızca ürünün sunumu, fiziksel düzgünlüğü, hizalaması, arka planı ve stüdyo çekim kalitesi profesyonelleştirilecektir.


━━━━━━━━━━━━━━━━━━━━━━
1. ÖNCE REFERANS ÜRÜNÜ ANALİZ ET
━━━━━━━━━━━━━━━━━━━━━━

Görsel oluşturmadan önce referans ürünü dikkatlice analiz et.

Şunları tespit et ve KİLİTLE:

- Ürünün gerçek şekli
- Ürünün gerçek en-boy oranı
- Ambalaj tipi
- Ambalaj formu
- Marka
- Logo
- Ürün adı
- Tüm görünür yazılar
- Yazıların konumları
- Tipografi görünümü
- Renkler
- Grafikler
- Desenler
- Ürün görselleri
- Etiketler
- Kapak veya ambalaj detayları
- Barkod görünüyorsa barkod
- Paket içerisindeki ürün sayısı
- Ürünün ön yüzü
- Ambalajın genel geometrisi

Bunları üretim sırasında değiştirme.


━━━━━━━━━━━━━━━━━━━━━━
2. REFERANSA MUTLAK SADAKAT
━━━━━━━━━━━━━━━━━━━━━━

Çıktıdaki ürün referans görseldeki ürünün AYNISI olmalıdır.

ÜRÜNÜ YENİDEN TASARLAMA.

ÜRÜNÜ FARKLI BİR VERSİYON OLARAK YENİDEN OLUŞTURMA.

Aşağıdaki unsurlar birebir korunmalıdır:

- Ambalaj
- Logo
- Marka adı
- Ürün adı
- Yazılar
- Yazıların konumları
- Renkler
- Grafikler
- Desenler
- Etiketler
- Ürün üzerindeki görseller
- Kapak
- Paket yapısı
- Ürün adedi
- Barkod
- Ürünün gerçek oranları

Referansta bulunmayan hiçbir logo, yazı, grafik, desen, etiket veya tasarım öğesi ekleme.

Mevcut yazıları yeniden yazma, değiştirme, düzeltme veya farklı bir tipografiyle oluşturma.

Ambalaj tasarımını "iyileştirmeye" çalışma.

TASARIMI DEĞİL, FOTOĞRAFIN SUNUMUNU İYİLEŞTİR.


━━━━━━━━━━━━━━━━━━━━━━
3. ÜRÜN YÖNÜ VE POZİSYONU — KRİTİK
━━━━━━━━━━━━━━━━━━━━━━

Ürün görselin TAM MERKEZİNDE bulunmalıdır.

Ürün DİMDİK durmalıdır.

Ürünün merkezi, tuvalin merkeziyle çakışmalıdır.

Ürünün dikey ekseni görselin dikey eksenine paralel olmalıdır.

Ürünün ÖN YÜZÜ kameraya TAM KARŞIDAN bakmalıdır.

Ön yüz görüntü düzlemine mümkün olduğunca paralel olmalıdır.

Kamera ürünün tam merkezinin karşısında bulunmalıdır.

Kamera açısı nötr ve düz olmalıdır.

KESİNLİKLE YAPMA:

- Ürünü sağa döndürme
- Ürünü sola döndürme
- Ürünü yana çevirme
- Ürünü eğme
- Ürünü yatırma
- Ürünü çapraz yerleştirme
- 3/4 açı kullanma
- Dinamik kamera açısı kullanma
- Ürünü yukarıdan çekme
- Ürünü aşağıdan çekme
- Gereksiz perspektif oluşturma
- Ürünü sağa veya sola kaydırma

Ürün profesyonel e-ticaret katalog fotoğrafındaki gibi düz, nötr, simetrik ve merkezlenmiş görünmelidir.


━━━━━━━━━━━━━━━━━━━━━━
4. KADRAJ VE ÜRÜN BOYUTU — ÇOK KRİTİK
━━━━━━━━━━━━━━━━━━━━━━

Çıktı:

1000 × 1000 piksel
1:1 kare format.

CLOSE-UP ÇEKİM YAPMA.

ÜRÜN KADRAJI DOLDURMAMALIDIR.

Kamerayı üründen yeterince uzakta konumlandır.

Ürün beyaz tuval içerisinde küçük, dengeli ve ferah görünmelidir.


ÖLÇEK KURALI:

Önce ürünün hangi boyutunun daha uzun olduğunu belirle:

- Ürün yatay ise GENİŞLİĞİ esas al.
- Ürün dikey ise YÜKSEKLİĞİ esas al.

Ürünün EN UZUN BOYUTU, 1000 × 1000 tuvalin yaklaşık %60–65'ini kaplamalıdır.

%65'İ GEÇMEMELİDİR.

ÖRNEK:

Yatay ve geniş bir ürünse:
Ürün genişliği yaklaşık 600–650 piksel olmalıdır.

Dikey ve uzun bir ürünse:
Ürün yüksekliği yaklaşık 600–650 piksel olmalıdır.

Ürünün diğer boyutu kendi doğal en-boy oranına göre otomatik olarak belirlenmelidir.

ÜRÜNÜ ESNETME.

ÜRÜNÜ SIKIŞTIRMA.

ÜRÜNÜN EN-BOY ORANINI DEĞİŞTİRME.


━━━━━━━━━━━━━━━━━━━━━━
5. ZORUNLU BEYAZ BOŞLUK
━━━━━━━━━━━━━━━━━━━━━━

Ürünün çevresinde dört tarafta da BELİRGİN ve GENİŞ beyaz boşluk bulunmalıdır.

Ürün:

- Üst kenara yaklaşmamalı
- Alt kenara yaklaşmamalı
- Sol kenara yaklaşmamalı
- Sağ kenara yaklaşmamalı

Hiçbir ürün parçası görüntünün kenarına temas etmemelidir.

Ürünün çevresindeki boş beyaz alan kompozisyonun önemli bir parçasıdır.

Beyaz boşlukları kırpmaya çalışma.

Ürünü boş alanı doldurmak amacıyla büyütme.

"Ürünü mümkün olduğunca büyük göster" yaklaşımını KULLANMA.

Bunun yerine:

"Ürünü merkezde, kontrollü ölçekte ve çevresinde geniş negatif alan olacak şekilde göster."

Ürün ilk bakışta kadraja göre büyük görünüyorsa:
KAMERAYI UZAKLAŞTIR VE ÜRÜNÜ KÜÇÜLT.


━━━━━━━━━━━━━━━━━━━━━━
6. ARKA PLAN
━━━━━━━━━━━━━━━━━━━━━━

Arka plan tamamen SAF BEYAZ olmalıdır.

HEX:

#FFFFFF

Arka planda kesinlikle:

- Gradient olmasın
- Gri ton olmasın
- Doku olmasın
- Zemin olmasın
- Zemin çizgisi olmasın
- Horizon çizgisi olmasın
- Dekor olmasın
- Başka obje olmasın
- Yansıma olmasın

Sadece ürün + saf beyaz arka plan.


━━━━━━━━━━━━━━━━━━━━━━
7. GÖLGE
━━━━━━━━━━━━━━━━━━━━━━

TAMAMEN GÖLGESİZ.

Ürünün:

- Altında
- Arkasında
- Sağında
- Solunda

gölge oluşturma.

Drop shadow kullanma.

Temas gölgesi kullanma.

Zemin gölgesi kullanma.

Ürün saf beyaz arka plan üzerinde temiz şekilde izole edilmiş görünmelidir.


━━━━━━━━━━━━━━━━━━━━━━
8. PROFESYONEL STÜDYO IŞIKLANDIRMASI
━━━━━━━━━━━━━━━━━━━━━━

Aydınlık, profesyonel high-key e-ticaret ürün fotoğrafçılığı kullan.

Büyük ve yumuşak softbox aydınlatma görünümü oluştur.

Işık ürünün tamamına dengeli dağılmalıdır.

Hedef:

- Temiz
- Aydınlık
- Net
- Dengeli pozlanmış
- Profesyonel
- Gerçekçi ürün fotoğrafı

Sert ışık kullanma.

Sert highlight oluşturma.

Aşırı parlama oluşturma.

Renkleri soldurma.

Ürünün gerçek renklerini değiştirme.

Ambalaj üzerindeki yansımaları kontrollü ve doğal tut.


━━━━━━━━━━━━━━━━━━━━━━
9. FİZİKSEL AMBALAJ DÜZELTMELERİ
━━━━━━━━━━━━━━━━━━━━━━

Referans üründe fotoğraf çekiminden veya fiziksel ambalaj durumundan kaynaklanan küçük kusurlar düzeltilebilir.

Örneğin:

- Hafif kırışıklıkları azalt
- Küçük ezilmeleri düzelt
- Paketi daha düzgün göster
- Ambalaj deformasyonlarını azalt
- Ürünün dik durmasını sağla
- Gereksiz fiziksel yamuklukları düzelt

ANCAK:

Bu düzeltmeler ambalaj tasarımını değiştirmemelidir.

Logo değişmemeli.

Yazılar değişmemeli.

Grafikler değişmemeli.

Ürün geometrisi farklılaştırılmamalı.

Paket içerisindeki ürün sayısı değişmemeli.

FİZİKSEL KUSURLARI DÜZELT,
TASARIMI DEĞİŞTİRME.


━━━━━━━━━━━━━━━━━━━━━━
10. SON KONTROL — ÜRETMEDEN ÖNCE
━━━━━━━━━━━━━━━━━━━━━━

Final görseli oluşturmadan önce sonucu kontrol et:

1. Referanstaki ürünün aynısı mı?

2. Ambalaj tasarımı aynı mı?

3. Logo, marka ve ürün adı korunmuş mu?

4. Yazılar ve yazı konumları korunmuş mu?

5. Renkler, desenler ve grafikler korunmuş mu?

6. Ürün sayısı aynı mı?

7. Ürünün gerçek en-boy oranı korunmuş mu?

8. Ürün TAM MERKEZDE mi?

9. Ürün DİMDİK mi?

10. Ürün kameraya TAM KARŞIDAN mı bakıyor?

11. Üründe sağa veya sola dönüş var mı?
Varsa düzelt.

12. Perspektif veya 3/4 açı var mı?
Varsa düzelt.

13. Ürünün EN UZUN BOYUTU tuvalin %65'inden büyük mü?
Büyükse ÜRÜNÜ KÜÇÜLT.

14. Dört tarafta geniş beyaz boşluk açıkça görünüyor mu?
Görünmüyorsa ÜRÜNÜ KÜÇÜLT.

15. Ürün herhangi bir kenara çok yakın mı?
Yakınsa ÜRÜNÜ KÜÇÜLT.

16. Arka plan tam #FFFFFF mı?

17. Herhangi bir gölge var mı?
Varsa kaldır.

18. Görsel 1000 × 1000 ve 1:1 mi?

Tüm koşullar sağlanmadan final görseli oluşturma.


━━━━━━━━━━━━━━━━━━━━━━
EN ÖNEMLİ 5 KURAL
━━━━━━━━━━━━━━━━━━━━━━

1. REFERANS ÜRÜNÜ VE AMBALAJ TASARIMINI DEĞİŞTİRME.

2. ÜRÜNÜ TAM MERKEZDE, DİK VE KAMERAYA TAM KARŞIDAN GÖSTER.

3. ÜRÜNÜN EN UZUN BOYUTU TUVALİN %60–65'İ OLMALI VE %65'İ GEÇMEMELİ.

4. DÖRT TARAFTA BELİRGİN, GENİŞ VE TEMİZ BEYAZ BOŞLUK BIRAK.

5. ARKA PLAN SAF #FFFFFF VE TAMAMEN GÖLGESİZ OLMALI.


SON TALİMAT:

Referans ürünü yeniden oluşturulacak bir tasarım olarak değil, korunması gereken gerçek ürün olarak ele al.

Referans = ürün kimliği.
Dönüşüm = yalnızca profesyonel stüdyo sunumu.

Ürünün tasarımına dokunma.

Ürünü kadrajı dolduracak şekilde büyütme.

Şüphe durumunda ürünü büyütmek yerine KÜÇÜLT.

Şüphe durumunda açı vermek yerine TAM KARŞIDAN göster.

Şüphe durumunda yeniden tasarlamak yerine REFERANSA SADIK KAL."""
PROMPT_PATH = Path(__file__).resolve().parent / "prompt.txt"
PROMPT = PROMPT_PATH.read_text(encoding="utf-8").strip() if PROMPT_PATH.exists() else DEFAULT_PROMPT
NEGATIVE_PROMPT = "Zoom, crop, close-up, distortion, background objects, props, gradients, textures, floor shadows, drop shadows, cast shadows, reflections, frames, borders, picture frames, surface, table, pedestal, stand, backdrop, watermark, text."
REFERENCE_STRENGTH = "MID"  # LOW, MID, HIGH
MODEL_ID = "nano-banana-2"  # Buradan modeli değiştirebilirsiniz (Örn: "leonardo-diffusion-xl")
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "10"))  # Leonardo varsayılan eşzamanlılık sınırı
POLL_INITIAL_INTERVAL = 1
POLL_MAX_INTERVAL = 3
REQUEST_TIMEOUT = (10, 60)  # (bağlantı, yanıt)
UPLOAD_TIMEOUT = (15, 300)  # Büyük/yavaş referans yüklemelerinde 5 dakikaya kadar bekle
UPLOAD_ATTEMPTS = 3

_thread_local = threading.local()

HEADERS = {
    "accept": "application/json",
    "authorization": f"Bearer {API_KEY}",
    "content-type": "application/json"
}

def get_session():
    """Her worker için bağlantıları yeniden kullanan bir HTTP oturumu döndür."""
    if not hasattr(_thread_local, "session"):
        _thread_local.session = requests.Session()
        _thread_local.session.headers.update(HEADERS)
        retry = Retry(
            total=3,
            connect=3,
            status=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(("GET",)),
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=2, pool_maxsize=2)
        _thread_local.session.mount("https://", adapter)
    return _thread_local.session

def upload_init_image(img_path):
    ext = img_path.split('.')[-1]
    session = get_session()
    res = session.post(
        "https://cloud.leonardo.ai/api/rest/v1/init-image",
        json={"extension": ext},
        timeout=REQUEST_TIMEOUT,
    )
    data = res.json().get('uploadInitImage')
    if not data:
        print(f"  [{os.path.basename(img_path)}] Yükleme izni alınamadı: {res.text}")
        return None

    upload_url = data['url']
    fields = json.loads(data['fields'])
    img_id = data['id']

    for attempt in range(1, UPLOAD_ATTEMPTS + 1):
        try:
            with open(img_path, 'rb') as f:
                # Bu imzalı depolama URL'sine Leonardo API anahtarını göndermemek için
                # oturumdaki kimlik doğrulama başlığını kullanma.
                r = requests.post(upload_url, data=fields, files={'file': f}, timeout=UPLOAD_TIMEOUT)
            if r.status_code == 204:
                return img_id
            if r.status_code not in (429, 500, 502, 503, 504):
                print(f"  [{os.path.basename(img_path)}] S3 yükleme hatası: {r.status_code}")
                return None
            print(f"  [{os.path.basename(img_path)}] Yükleme yanıtı {r.status_code}; tekrar deneniyor ({attempt}/{UPLOAD_ATTEMPTS})...")
        except requests.RequestException as exc:
            print(f"  [{os.path.basename(img_path)}] Yükleme zaman aşımı/ağ hatası; tekrar deneniyor ({attempt}/{UPLOAD_ATTEMPTS}): {exc}")

        if attempt < UPLOAD_ATTEMPTS:
            time.sleep(min(2 ** attempt, 5))

    print(f"  [{os.path.basename(img_path)}] Yükleme {UPLOAD_ATTEMPTS} denemede tamamlanamadı.")
    return None

def generate_image(init_img_id):
    payload = {
        "model": MODEL_ID,
        "parameters": {
            "prompt": PROMPT,
            "negative_prompt": NEGATIVE_PROMPT,
            "width": 1024,
            "height": 1024,
            "quantity": 1,
            "guidances": {
                "image_reference": [
                    {
                        "image": {
                            "id": init_img_id,
                            "type": "UPLOADED"
                        },
                        "strength": REFERENCE_STRENGTH
                    }
                ]
            }
        },
        "public": False
    }

    res = get_session().post(
        "https://cloud.leonardo.ai/api/rest/v2/generations",
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )
    res_json = res.json()

    # Hata kontrolü: API bazen list döner (hata), bazen dict döner (başarı)
    if isinstance(res_json, list):
        print(f"  Üretim hatası (API list döndü): {json.dumps(res_json, indent=2)[:300]}")
        return None

    if res.status_code != 200:
        print(f"  Üretim hatası ({res.status_code}): {json.dumps(res_json, indent=2)[:300]}")
        return None

    gen_id = (
        res_json.get('generate', {}).get('generationId') or
        res_json.get('sdGenerationJob', {}).get('generationId') or
        res_json.get('generationId') or
        res_json.get('id')
    )

    return gen_id

def download_image(gen_id, out_path, img_name):
    # İlk sonucu 1 saniye içinde kontrol et; uzun işler için sorgu sıklığını azalt.
    session = get_session()
    poll_interval = POLL_INITIAL_INTERVAL
    while True:
        res = session.get(
            f"https://cloud.leonardo.ai/api/rest/v1/generations/{gen_id}",
            timeout=REQUEST_TIMEOUT,
        )
        res.raise_for_status()
        data = res.json()
        gen_info = data.get('generations_by_pk', {})
        status = gen_info.get('status')

        if status == 'COMPLETE':
            images = gen_info.get('generated_images', [])
            if not images:
                print(f"  [{img_name}] Görsel linki bulunamadı.")
                return False
            img_url = images[0]['url']
            # Görsel CDN'sine de Leonardo API anahtarı göndermeden indir.
            img_res = requests.get(img_url, timeout=REQUEST_TIMEOUT, stream=True)
            img_res.raise_for_status()
            with open(out_path, 'wb') as f:
                for chunk in img_res.iter_content(chunk_size=1024 * 64):
                    if chunk:
                        f.write(chunk)
            print(f"  [{img_name}] Kaydedildi: {os.path.basename(out_path)}")
            return True
        elif status in ('FAILED', 'ERROR'):
            print(f"  [{img_name}] Üretim başarısız: {gen_id}")
            with open("error_response.json", "w", encoding="utf-8") as err_f:
                json.dump(data, err_f, indent=2, ensure_ascii=False)
            return False

        time.sleep(poll_interval)
        poll_interval = min(poll_interval + 1, POLL_MAX_INTERVAL)

def process_image(img):
    try:
        path = os.path.join(REF_DIR, img)
        # Üzerine yazmaması için dosya adına zaman damgası ekliyoruz
        timestamp = str(int(time.time()))
        out_path = os.path.join(OUT_DIR, f"output_{timestamp}_{img}")

        print(f"[{img}] Yükleniyor...")
        init_id = upload_init_image(path)
        if not init_id:
            return img, False

        print(f"[{img}] Üretim başlatılıyor...")
        gen_id = generate_image(init_id)
        if not gen_id:
            print(f"[{img}] Üretim ID bulunamadı.")
            return img, False

        print(f"[{img}] Bekleniyor (ID: {gen_id[:8]}...)")
        success = download_image(gen_id, out_path, img)
        return img, success
    except requests.RequestException as exc:
        print(f"[{img}] Ağ/API hatası: {exc}")
        return img, False

def main():
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)

    requested_imgs = {
        name.strip()
        for name in os.getenv("IMAGE_FILES", "").split("|")
        if name.strip()
    }
    imgs = [
        f for f in os.listdir(REF_DIR)
        if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        and not f.startswith('output_')
        and (not requested_imgs or f in requested_imgs)
    ]
    if not imgs:
        print(f"Klasör boş: {REF_DIR}")
        return

    print(f"{len(imgs)} görsel bulundu. {MAX_WORKERS} eş zamanlı işlemle başlıyor...\n")
    t_start = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_image, img): img for img in imgs}
        ok, fail = 0, 0
        for future in as_completed(futures):
            img_name, success = future.result()
            if success:
                ok += 1
            else:
                fail += 1

    elapsed = time.time() - t_start
    print(f"\nTamamlandı: {ok} başarılı, {fail} başarısız — {elapsed:.0f}s")
    if fail > 0 and ok == 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
