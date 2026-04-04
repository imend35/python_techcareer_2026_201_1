"""
Bu dosya: projenin veri analizi ve rapor üretim mantığını taşır.
Bizim amacımız: kodu parçalara bölmek ve her bir parçayı SOLID(Single Responsibility) göre yönetmek  ==> Yani Modüler olmasını sağlamak
"""
from jinja2.utils import missing

# 1-) Gerekli kütüphaneleri içe aktarıyoruz.
"""
    Pandas     => Veri işleme
    Numpy      => Sayısal Hesaplama
    Matplotlib => Grafik üretimi
    Beartype   => Fonksiyonlara tip kontrolü için
"""
# Bu import sayesinde Python tip ipuçlarını daha güvenli ve esnek bir şekilde kullanabiliyoruz.
# Özellikle Python sürümlerinde tiplerin ileri referanslarını desteklemek için faydalıdır.
from __future__ import annotations

# Path
# Dosya ve klasör yollarını işletim sistemlerinden bağımsız bir şekilde yönetmek içindir.
from pathlib import Path

# Any:
# Dönüş tiplerinde veya karışık veri yapılarında esnek tip tanımı yapmak için kullanıyoruz
from typing import Any

#base64:
#Grafik PNG dosyalarını HTML içine gömebilmek için base64 string'e çevirmede kullanılır
import base64

# io: Veri akışını veya bellek içi byte işlem işlemlerini
import io

#numpy:
# Sayısal hesaplamala, median, mea,std,polyfit etc
import numpy as np

# pandas
# csv okuma, tablo işlemleri, dönüşüm, özet çıkarma
import pandas as pd

# matplotlib
# Grafik çizmek veya PNG üretmek
import matplotlib.pyplot as plt

# beartype: decorator yazalım.
"""
Eğer beartype kurulu ise gerçek decorator kullansın
Eğer beartype kurulu değilse sistemi bozmasın pasif bir yani yedek(pasif) bir decorator devreye girsin
"""
try:
    from beartype import beartype
except ImportError:
    # Bu yedek yapı sayesinde beartype yoksa bu fonksiyon normal bir çalışmaya devam eder.
    def beartype(func):
        return func

# 2-) CSV Dosyasını okusun /data/sample_sales.csv
# Kullanıcının verdiği CSV dosyasını okumak ve DataFrame oalrak geri döndürmek
@beartype
def load_sales_data(csv_path: str|Path) -> pd.DataFrame:
    # Gelen yolu Path nesnesine çeviriyoruz ki dosya sistemi işlemleri daha güvenli olsun
    path = Path(csv_path)

    # Eğer dosya fiziksel oalrak yoksa direk kata versin
    if not path.exists():
        raise FileNotFoundError(f"CSV dosyasını bulamadı: {path}")

    # CSV dosyasını panda  DataFrame olarak okunsun
    dataframe= pd.read_csv(path)

    # Eğer dosya var ama içi boşsa uyarı verelim
    if dataframe.empty:
        raise ValueError("CSV dosyası boş geldi, Lütfen bu dosyaya veri ekleyiniz")

    # Eğer başarılı ise veriyi geri dönder.
    return dataframe


# 3-) Bu fonksiyon ham(raw) veriyi temizlenir(Cleaner) ve analiz için hazır hale getirecek
# Tarih, sayısal, hesaplamalar vs
# Ham veriyi (raw) analiz yapmak
# Eksik kolon, tip dönüşü, bozuk satır, etiketleme
"""
Std: Standart deviation (Standart Sapma): Sayıların ortalaması 
Veriler birbirine ne akdar yakın ? : Veriler ortalamaya ne kadar yakın duruyor, veya ne kadar uzağa saçılıyor Ortalama: 50
Örnek: [48,49,50,51,52] => Bunlar birbirine yakın
Örnek: [10,30,50,70,90] => Bunlar birbirine yakın değil
Mean: Merkez nerede
"""
@beartype
def prepate_sales_data(dataframe:pd.DataFrame) -> pd.DataFrame:
    # Original veriyi bozmamak için kopyasını oluştururuz.
    df = dataframe.copy()

    # Projede zorunluı olan kolonları tanımlıyoruz
    required_columns ={"date","category","product","quantity","unit_price"}

    # Eksik kolonlar var mı diye kontrol ediyoruz
    missing_columns= required_columns.difference(df.columns)

    # Eğer eksik kolon varsa işlemi durduruyoruz
    if missing_columns:
        raise ValueError(f"Eksik kolonlar bulundu. {sorted(missing_columns)} ")

    # Cast -> Dönüşümler (Date, Numerics)
    # Tarih  => datetime
    # coerce => Date     NaT => Hatalı değer
    # coerce => Sayısal  NaN => Hatalı değer
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")

    # Bozuk satırları temizleyelim
    df= df.dropna(subset=["date","category","product","quantity","unit_price"]).copy()

    # Sayısal değerlerde Sıfır(0) veya Eksi (-) varsa dahil etme
    df= df[(df["quantity"]>0) & (df["unit_price"]>0)].copy()

    # Toplam gelir hesabı
    # revenue= quantity * unit_price
    # gelir  = miktar   * birim fiyat
    df["revenue"] = df["quantity"] * df["unit_price"]

    # numpy ile sipariş büyüklüğünü göstermek (Label)
    # Sipariş büyklüğünü ayırmak için quantity median değerini kullanıyoruz.
    quantity_median= float(np.median(df["quantity"]))

    # quantity median'dan byüük/eşitse Büyük sipariş değilse Standart Sipariş etiketine
    df["order_size_label"] =np.where(
        df["quantity"] >= quantity_median,
        "Büyük Sipariş",
        "Standart Sipariş"
    )

    # Performans puanı oluşturuyoruz (Score)
    # revenue: ortalamasını hesaplıyoruz.
    revenue_mean = float(np.mean(df["revenue"]))

    # revenue: Standart sapmasını hesaplıyoruz.
    revenue_std  = float(np.std(df["revenue"]))

    # Eğer std 0 ise tüm satırlar aynı revenue sahiptir
    # Böylece sabit performans puanını veriyoruz.
    if revenue_std==0:
        df["performance_score"] = 50.0
    else:
        # Z-score ile her kaydın ortalamadan sapmasını hesaplıyoruz
        z_scores = (df["revenue"]-revenue_mean)/revenue_std

        # Skoru 0-100
        # Z-score daha okuanbilir olması 0-100 benzeri bir skala taşıyoruz
        df["performance_score"] = np.clip(50 + (z_scores*10), 0,100).round(2)

    # Veriyi tarihe göre sıralayıp index'i sıfırlıyoruz.
    return df.sort_values("date").reset_index(drop=True)




