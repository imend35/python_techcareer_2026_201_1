"""
Bu dosya terminal üzerinden çalışan gelişmiş bir Quiz / test uygulaması

Amaç:
- Soruları CSV dosaylarında okumak
- Kullanıcı sorularını sormak
- Cevapları karşılaştırmak
- Çıkan sonuçu: txt, csv, Html formatında raporluyoruz

UI ( User Interface)      : Kullanıcının gördüğü kısımlar renk, opacity,
UX ( User eXperisens)     : Kullanıcı Deneyimlerim toplamı. examples: form, error, modal, hızlı,
CX ( Customer eXperisens) : Müşteri Deneyimlerim toplamı.
"""

# csv modülü ==> questions.csv
# csv (Comma Sepatated Values)
import csv

# html modolü => kullanıcının görebileceği ekran
import html

# random modülü => Kurs içindeki soruların her defasında farklı olarak gelmesi
import random

# datetime sınıfı => Tarih ve saat bilgisini kullanmak için
from datetime import datetime

# Path sınıfı:
# Dosya ve klasör yollarından bağımsız ve güvenli olamsı için kullanıyoruz
# Windows, Linux, macOs gibi işletim sistemlerinde dosya yollarını elle birleştirmek yerine nesne yapsın
from pathlib import Path

from pandas.conftest import strict_data_files

# BASE_DIR:
# Python dosyasının bulunduğu klasörünü temsil eder.
# __file__   --> o anda çalışan dosyanın yolunu verir
# resolve()  --> tam/gerçek yolu çözer
# parent     --> dosyanın bulunduğu klasörü alır
# Amaç: CSV ve klasörleri bulunuğu dizine göre oluşturmak
BASE_DIR = Path(__file__).resolve().parent

# CSV_FILE
# soruların olduğu dosyayı almak yani questions.csv
CSV_FILE = BASE_DIR / "questions.csv"

# RESULT_DIR
# Quiz sonuçlarının kaydedildiği klasörü temsil etsin.
# Txt, CSV ve HTML raporlarını bu klasörünü altında olacaktır.
RESULT_DIR = BASE_DIR / "results"


# ensure_results_dir Fonksiyonu
# Sonuçların yazılacğaı klasörün var olup olmadığını kontrol eder
# Eğer klasör yoksa otomatik oluştur
# parents=True  --> gerekirse üst klasörleri de oluşturur.
# exist_ok=True --> klasör zaten varsa hata vermez
def ensure_results_dir():
    RESULT_DIR.mkdir(parents=True, exist_ok=True)


# load_questions fonksiyonu:
# Verilen CSV dosyasını okuyarak quiz sorularını belleğe yükler.
# Geriye liste döner
#
# Beklenen Kolonlar
# question,option_a,option_b,option_c,option_d,answer
#
# Bu fonksiyonları ayrıca veri doğrulama da yapsın
# Dosya var mı ?
# Başlıklar okunabiliyor mu ?
# Kolonlar eksik mi ?
# Cevap: A/B/C/D dışında cevap var mı?
# Soru metni boşmu ?
def load_questions(csv_file):
    # questions listesi, geçerli bulunan tüm soruları alsın
    questions = []

    # Eğer CSV dosyası yoksa kullanıcıya hata gösterebilir ve boş liste döndersin.
    if not csv_file.exists():
        print(f"Hata: CSV dosyası bulunamadı -> {csv_file}")
        return questions

    # CSV dosyasını UTF-8-SIG ile açıyoruz.
    # utf-8-sig seçimini nedeni:
    # Bazı CSV dosyaları başında BOM karakteri içerir.
    # Bu encoding, başlıkların bozulmadan okunmasına yardımcı oluyor.
    # newline:"" parametresi, CSV okuma/yazma sırasında satır sonu sorunları azaltmak içindir
    with open(csv_file, "r", encoding="utf-8-sig", newline="") as file:
        # DictReader, her satırı sözlük(dict) olarak okur
        # Böylece sütunlara index ile değil isimleriyle erişebiliriz.
        reader = csv.DictReader(file)

        # required_columns kümesi:
        # CSV içinde mutlaka gereken başlıkları tanımlayalım.
        required_columns = {
            "question",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "answer",
        }

        # fieldnames eğer boşsa başlıklar okunmamış demektir
        if not reader.fieldnames:
            print("Hata: CSV başlıkları okunamadı")
            return questions

        # missing hesabı:
        # Beklenen kolonlar ile gerçek kolanları karşılaştır
        # Eğer CSV'de eksik olan kolanlar varsa bulsun
        missing = required_columns - set(reader.fieldnames)
        if missing:
            print("Hata CSV içinde eksik kolonlar var: ", ", ".join(sorted(missing)))
            return questions

        # CSV'de veri satırlarını gezelim
        # start=2  nedeni:
        # 1.satır başlık satırıdırn ve gerçek satırlar 2.satırda başlar.
        for row_number, row in enumerate(reader, start=2):
            # answer alanı metne çevrilir, boşluklardan temizleni ve büyük harfe başlanır.
            # Dikkkatttt: Kullanıcı küçük büyük harf girse bile büyük harf
            answer = str(row["answer"]).strip().upper()

            # Eğer cevap yalnızca A,B,C,D dışında ise satır geçersiz sayılır.
            if answer not in {"A","B","C","D"}:
                print(f"Uyarı: {row_number}.satırdaki cevap geçersiz olduğu için soru atlandı")
                continue

            # Soru metni boşluklardan temizlensin
            question_text = str(row["question"]).strip()

            # Sözlük halinde verileri tutalım
            # Sözlük: hem ekrana yazdırmak, hemde sonradan karşılaştırmak için kolaylaşır
            options = {
                "A": str(row["option_a"]).strip(),
                "B": str(row["option_b"]).strip(),
                "C": str(row["option_c"]).strip(),
                "D": str(row["option_d"]).strip(),
            }

            # Soru metni boşsa kullancıya uyarı verilir ve bu satır alınmaz
            if not question_text:
                print(f"Uyarı: {row_number}. satırdaki soru boş olduğu için atlandı.")
                continue

            # question,option_a,option_b,option_c,option_d,answer
            questions.append(
                {
                    "question": question_text,
                    "options": options,
                    "answer": answer,
                }
            )

        # Tüm geçerli sorular yüklendikten sonra geri döndürülür.
        return  questions





#
#
#
#
#


#
#
#
#
#


#
#
#
#
#


#
#
#
#
#


#
#
#
#
#


#
#
#
#
#


#
#
#
#
#


#
#
#
#
#


#
#
#
#
#


#
#
#
#
#


#
#
#
#
#


#
#
#
#
#


#
#
#
#
#


#
#
#
#
#


#
#
#
#
#


#
#
#
#
#


#
#
#
#
#


#
#
#
#
#


#
#
#
#
#


#
#
#
#
#


#
#
#
#
#


#
#
#
#
#


#
#
#
#
#


#
#
#
#
#


#
#
#
#
#
