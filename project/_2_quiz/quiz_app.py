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
















