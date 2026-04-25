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
            if answer not in {"A", "B", "C", "D"}:
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
        return questions


# prompt_menu fonskiyonu
# Kulalnıcıya ana menü gösterilir ve seçim yapılır
# Geçersiz giriş yapılırsa kullancıya yeniden yönlendişrilir
def prompt_menu():
    print("\n" + "=" * 70)
    print("Python Quiz / Test uygulaması")
    print("=" * 70)
    print("1-) Quiz Başlat")
    print("2-) Quiz Soru sayısı")
    print("3-) Quiz Çıkış")

    # strip() ==> baştaki, sonradaki boşlukları temizlensin
    choise = input("Seçiminiz: ").strip()

    # While döngüsü, geçerli bir menü seçimi yapılana kadar tekrar ister
    while choise not in {"1", "2", "3"}:
        choise = input("Geçersiz seçim, Lütfen 1,2 veya 3 girin: ").strip()
    return choise

# ask_question fonskiyonu:
# Tek bir soruyu kullanıcıya gösterir, cevabı alır ve doğru/yanlış kontrolü yapar.
# Parametreler:
#   - index: Kaçıncı soru olduğu
#   - total: Toplam soru sayısı
#   - question_Data: Soru metni, şıklar doğru cevap içeren sözlük
# Geriye, bu soruya ait kullanıcı sonucunu içeren bir sözlük döndürür.
def ask_question(index, total, question_data):
    print("\n" + "=" * 70)
    print(f"Soru {index}/{total}")
    print("-" * 70)
    print(question_data["question"])
    print("-" * 70)

    # options sözlüğündeki tüm şıkları sırayla ekrana basar.
    for key, value in question_data["options"].items():
        print(f"{key}) {value}")

    # Kullanıcıdan cevap alınır.
    # upper() kullanımı sayesinde küçük harf girilse bile büyük harfe çevrilir.
    user_answer = input("\nCevabınız (A/B/C/D): ").strip().upper()

    # Geçerli bir cevap girilene kadar kullanıcı tekrar yönlendirilir.
    while user_answer not in {"A", "B", "C", "D"}:
        user_answer = input("Geçersiz giriş. Lütfen A, B, C veya D girin: ").strip().upper()

    # Soru verisindeki doğru cevap alınır.
    correct_answer = question_data["answer"]

    # Kullanıcının cevabı ile doğru cevap karşılaştırılır.
    is_correct = user_answer == correct_answer

    # Kullanıcıya anlık geri bildirim verilir.
    if is_correct:
        print("Sonuç: Doğru")
    else:
        print(
            f"Sonuç: Yanlış | Doğru cevap: {correct_answer}) "
            f"{question_data['options'][correct_answer]}"
        )

    # Sonuçlar standart yapıda döndürülür.
    return {
        "question": question_data["question"],
        "options": question_data["options"],
        "correct_answer": correct_answer,
        "user_answer": user_answer,
        "is_correct": is_correct,
    }

# run_quiz fonksiyonu
# Quize akışının ana çalıştıma fonskiyonu olacaktır.
# Tüm sorular rastgele karıştırsın, her bir soruda sırayla kullanıcıya sorsun
# Paunları hesaplama 100/soru sayısı= 1 adet soru için puan sayısı hesaplansın ve sonuç listesini döndersin
def run_quiz(questions):
    # Original soru listesini bozmamak için kopyasını alıyoruz.
    randomized_questions = questions[:]

    # Soruları rastgele karıştırır
    # Yani her quiz aynı sırada gelmeyecektir.
    random.shuffle(randomized_questions)

    print("\nQuiz başladı. Sorular rastgele karıştırıldı.")

    # Toplam soru sayısı hesaplansın
    total = len(randomized_questions)

    # Score değişkeni doğru cevap sayısını tutar
    score = 0

    # user_results listesi, her soruya ilişkin kullanıcı sonucu saklar.
    user_results = []

    # Soru numaralandırılması 1'den başlatılır.
    for index, question_data in enumerate(randomized_questions, start=1):
        result = ask_question(index, total, question_data)
        user_results.append(result)

        # Eğer sorı doğru ise skor'u 1 artırır.
        if result["is_correct"]:
            ##score=score+1
            score += 1
    return score, total, user_results

# create_result_base_names fonskiyonu:
# Sonuç dosyalarına ortak temel isim üretir.
# ÖRneğin: results/quiz_result_20260425_143945
# Sopnra buna .txt, .csv, .html uzantıları ekler
def create_result_base_names():
    # Önce sonuç klasörünün var olup olmadığını test ediyoruz
    ensure_results_dir()

    # Zaman damgası tarih-saat
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Path nesnesi olarak temel dosya adını oluşturulsun
    base_name = RESULT_DIR / f"quiz_result_{timestamp}"
    return base_name

# save_results_txt fonskiyonu:
# Quiz sonucu okunabilir bir metin raporu oluştursun ".txt" dosyasınıa kaydeder.
# txt dosyası insan gözüyle daha okuanbilirdir
def save_results_txt(base_name, score, total, percent, user_results):
    txt_path = base_name.with_suffix(".txt")

    # Dosya yazma modunda açılır
    with open(txt_path, "w", encoding="utf-8") as file:
        file.write("PYTHON QUIZ SONUÇ RAPORU\n")
        file.write("=" * 70 + "\n")
        file.write(f"Tarih          : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        file.write(f"Doğru Sayısı   : {score}\n")
        file.write(f"Yanlış Sayısı  : {total - score}\n")
        file.write(f"Toplam Soru    : {total}\n")
        file.write(f"Başarı Oranı   : %{percent:.2f}\n")
        file.write("=" * 70 + "\n\n")

        # Her soru tek tek raporu detaylı bir şekilde yazılır.
        for index, item in enumerate(user_results, start=1):
            file.write(f"Soru {index}: {item['question']}\n")
            file.write(f"İşaretlenen Cevap : {item['user_answer']}) {item['options'][item['user_answer']]}\n")
            file.write(f"Doğru Cevap       : {item['correct_answer']}) {item['options'][item['correct_answer']]}\n")
            file.write(f"Durum             : {'Doğru' if item['is_correct'] else 'Yanlış'}\n")
            file.write("-" * 70 + "\n")

    return txt_path

# save_results_txt fonskiyonu:
# Quiz sonucu okunabilir bir metin raporu oluştursun ".txt" dosyasınıa kaydeder.
# txt dosyası insan gözüyle daha okuanbilirdir
def save_results_csv(base_name, score, total, percent, user_results):
    csv_path = base_name.with_suffix(".csv")

    # Dosya yazma modunda açılır
    with open(csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(["summary_type", "value"])
        file.write(["date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        file.write(["score", score])
        file.write(["wrong", total - score])
        file.write(["total", total])
        file.write(["percent", f"{percent:.2f}"])
        file.write([])

        # Ardından detay verisi başlıklarını yazılır
        writer.writerow([
            "question_no",
            "question",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "user_answer",
            "correct_answer",
            "result",
        ])

        # Her soru tek tek raporu detaylı bir şekilde yazılır.
        for index, item in enumerate(user_results, start=1):
            writer.writerow([
                index,
                item["question"],
                item["question"]["A"],
                item["question"]["B"],
                item["question"]["C"],
                item["question"]["D"],
                item["question"]["A"],
                item["user_answer"],
                item["correct_answer"],
                "Doğru" if item["is_correct"] else "Yanlış",
            ])

    return csv_path


# get_option_css_class(key, item["user_answer"], item["correct_answer"])
def get_option_css_class(option_key, user_answer, correct_answer):
    if option_key == correct_answer and option_key == user_answer:
        return "option option-correct-selected"

    # Doğru cevap
    if option_key == correct_answer:
        return "option option-correct"

    # Hatalı cevap
    if option_key ==user_answer and user_answer != correct_answer:
        return "option option-wrong-selected"

    return "option"


# save_results_html fonksiyonu:
# Sonuçları görsel açıdan daha zengin bir HTML raporu olarak kaydeder.
# Kullanıcı hangi şıkkı işaretledi, doğru cevap neydi, hangi soru doğru/yanlıştı
# gibi bilgiler renkli kutular ve rozetlerle gösterilir.
def save_results_html(base_name, score, total, percent, user_results):
    html_path = base_name.with_suffix(".html")

    # Her soru kartını HTML içinde bir bölüm olarak biriktireceğiz.
    sections = []

    # Tüm kullanıcı sonuçlarını geziyoruz.
    for index, item in enumerate(user_results, start=1):
        options_html = []

        # Her şık için ayrı HTML satırı üretilir.
        for key, value in item["options"].items():
            # Şıkkın hangi görsel sınıfa sahip olacağı hesaplanır.
            css_class = get_option_css_class(key, item["user_answer"], item["correct_answer"])

            # html.escape ile içerik güvenli hale getirilir.
            label_parts = [f"<strong>{key})</strong> {html.escape(value)}"]

            # Kullanıcının seçtiği şık ise rozet eklenir.
            if key == item["user_answer"]:
                label_parts.append('<span class="badge badge-user">İşaretlediğin</span>')

            # Doğru cevap olan şık ise rozet eklenir.
            if key == item["correct_answer"]:
                label_parts.append('<span class="badge badge-correct">Doğru Cevap</span>')

            # Tek bir şık satırı HTML listesi elemanı olarak oluşturulur.
            option_line = f'<li class="{css_class}">{" ".join(label_parts)}</li>'
            options_html.append(option_line)

        # Soru doğru mu yanlış mı bilgisi hem metin hem CSS sınıfı olarak hazırlanır.
        question_status = "Doğru" if item["is_correct"] else "Yanlış"
        question_status_class = "status-correct" if item["is_correct"] else "status-wrong"

        # Tek bir soru kartının HTML içeriği hazırlanır.
        section = f"""
        <div class="question-card">
            <div class="question-header">
                <h2>Soru {index}</h2>
                <span class="status {question_status_class}">{question_status}</span>
            </div>
            <p class="question-text">{html.escape(item["question"])}</p>
            <ul class="options">
                {''.join(options_html)}
            </ul>
            <div class="answer-summary">
                <p><strong>İşaretlediğin:</strong> {item["user_answer"]}) {html.escape(item["options"][item["user_answer"]])}</p>
                <p><strong>Doğru cevap:</strong> {item["correct_answer"]}) {html.escape(item["options"][item["correct_answer"]])}</p>
            </div>
        </div>
        """
        sections.append(section)

    # Tüm raporun ana HTML iskeleti hazırlanır.
    # İçinde CSS stilleri de gömülü olduğu için tek dosya halinde açılabilir.
    html_content = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Quiz Sonuç Raporu</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            color: #1f2937;
            margin: 0;
            padding: 24px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        .summary {{
            background: #ffffff;
            border-radius: 14px;
            padding: 20px;
            margin-bottom: 24px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }}
        .summary h1 {{
            margin-top: 0;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 12px;
            margin-top: 16px;
        }}
        .summary-box {{
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 14px;
        }}
        .question-card {{
            background: #ffffff;
            border-radius: 14px;
            padding: 20px;
            margin-bottom: 18px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }}
        .question-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
        }}
        .question-text {{
            font-size: 18px;
            font-weight: bold;
        }}
        .status {{
            padding: 8px 12px;
            border-radius: 999px;
            font-weight: bold;
            font-size: 14px;
        }}
        .status-correct {{
            background: #dcfce7;
            color: #166534;
        }}
        .status-wrong {{
            background: #fee2e2;
            color: #991b1b;
        }}
        .options {{
            list-style: none;
            padding: 0;
            margin: 16px 0;
        }}
        .option {{
            background: #f9fafb;
            border: 1px solid #d1d5db;
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 10px;
        }}
        .option-correct {{
            background: #dcfce7;
            border-color: #22c55e;
        }}
        .option-correct-selected {{
            background: #bbf7d0;
            border: 2px solid #15803d;
        }}
        .option-wrong-selected {{
            background: #fee2e2;
            border-color: #ef4444;
        }}
        .badge {{
            display: inline-block;
            margin-left: 8px;
            padding: 4px 8px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: bold;
        }}
        .badge-user {{
            background: #dbeafe;
            color: #1d4ed8;
        }}
        .badge-correct {{
            background: #dcfce7;
            color: #166534;
        }}
        .answer-summary {{
            background: #f9fafb;
            border-radius: 10px;
            padding: 12px;
            border: 1px solid #e5e7eb;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="summary">
            <h1>Quiz Sonuç Raporu</h1>
            <p><strong>Tarih:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <div class="summary-grid">
                <div class="summary-box"><strong>Doğru Sayısı</strong><br>{score}</div>
                <div class="summary-box"><strong>Yanlış Sayısı</strong><br>{total - score}</div>
                <div class="summary-box"><strong>Toplam Soru</strong><br>{total}</div>
                <div class="summary-box"><strong>Başarı Oranı</strong><br>%{percent:.2f}</div>
            </div>
        </div>

        {''.join(sections)}
    </div>
    
    <button 
    type="button" 
    id="button_click_me_id"
    style="background-color:blue; color:fff; cursor:pointer;" > 
    Click Me </button>
    
    <script>
        let user_data= document.getElementById("button_click_me_id")
        alert(user_data)
    </script>
</body>
</html>
"""

    # Hazırlanan HTML metni dosyaya UTF-8 ile yazılır.
    html_path.write_text(html_content, encoding="utf-8")
    return html_path


# save_all_results fonksiyonu:
# Quiz tamamlandıktan sonra tüm rapor dosyalarını tek noktadan üretir.
# TXT, CSV ve HTML dosyalarını oluşturur ve bunların yolunu döndürür.
def save_all_results(score, total, user_results):
    # Başarı oranı yüzde olarak hesaplanır.
    # total sıfır olursa hata olmaması için güvenli kontrol vardır.
    percent = (score / total) * 100 if total else 0

    # Tüm dosyalarda kullanılacak ortak temel isim üretilir.
    base_name = create_result_base_names()

    # Üç farklı formatta rapor oluşturulur.
    txt_file = save_results_txt(base_name, score, total, percent, user_results)
    csv_file = save_results_csv(base_name, score, total, percent, user_results)
    html_file = save_results_html(base_name, score, total, percent, user_results)

    return txt_file, csv_file, html_file, percent


# show_final_summary(score, total, percent)
def show_final_summary(score, total, percent):
    print("\n"+ "="*70)
    print("Quiz tamamlandı")
    print("="*70)
    print(f"Doğru sayısı: {score}")
    print(f"Yanlış sayısı: {total-score}")
    print(f"Toplam sayısı: {total}")
    print(f"Başarı oranı: {percent:.2f}")

    # Başarı oranına göre seviye değerlendirsin
    if percent==100:
        print("Değerlendirme Mükemmel")
    elif percent>=80:
        print("Değerlendirme Çok iyi")
    elif percent>=60:
        print("Değerlendirme İyi")
    elif percent>=40:
        print("Değerlendirme Orta")
    else:
        print("Çok kötü çok çalışmalısınız.")

# main fonksiyonu:
# Programın giriş noktasıdır.
# Genel akış burada yönetilir:
# 1) Soruları yükle
# 2) Menü göster
# 3) Kullanıcı seçimine göre quiz başlat / soru sayısını göster / çıkış yap
def main():
    # Önce CSV dosyasındaki sorular yüklenir.
    questions = load_questions(CSV_FILE)

    # Eğer soru listesi boşsa program devam etmez.
    if not questions:
        print("Program sonlandırıldı. Soru listesi boş veya CSV hatalı.")
        return

    # Sonsuz döngü ile menü sürekli gösterilir.
    # Kullanıcı '3' ile çıkış yapana kadar program açık kalır.
    while True:
        choice = prompt_menu()

        # 1 seçildiyse quiz başlatılır.
        if choice == "1":
            score, total, user_results = run_quiz(questions)
            txt_file, csv_file, html_file, percent = save_all_results(score, total, user_results)

            show_final_summary(score, total, percent)
            print("\nSonuç dosyaları oluşturuldu:")
            print(f"TXT  : {txt_file}")
            print(f"CSV  : {csv_file}")
            print(f"HTML : {html_file}")

        # 2 seçildiyse toplam soru sayısı gösterilir.
        elif choice == "2":
            print(f"\nToplam soru sayısı: {len(questions)}")

        # 3 seçildiyse program sonlandırılır.
        elif choice == "3":
            print("Program kapatıldı.")
            break


# Bu koşulun anlamı:
# Dosya doğrudan çalıştırılırsa main() fonksiyonu devreye girsin.
# Ancak bu dosya başka bir Python dosyası içinde import edilirse
# otomatik olarak çalışmasın.
if __name__ == "__main__":
    main()
