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


# 4-) Bu fonksiyonun amacı:
# Veriyi günlük bazda özetlemek.
# Her gün için toplam gelir, toplam adet ve sipariş sayısı üretir.
# sample_sales.csv => date,category,product,quantity,unit_price
@beartype
def summarize_by_day(dataframe: pd.DataFrame) -> pd.DataFrame:
    # Orijinal veriyi bozmamak için kopyasını alıyoruz.
    working_df = dataframe.copy()

    # Datetime içindeki sadece tarih parçasını alıyoruz.
    working_df["report_date"] = working_df["date"].dt.date

    # Günlük groupby yapıyoruz.
    # total_revenue: revenue toplamı
    # total_quantity: quantity toplamı
    # order_count: ürün satır sayısı
    daily_summary = (
        working_df.groupby("report_date", as_index=False)
        .agg(
            total_revenue=("revenue", "sum"),
            total_quantity=("quantity", "sum"),
            order_count=("product", "count"),
        )
        .sort_values("report_date")
        .reset_index(drop=True)
        .rename(columns={"report_date": "date"})
    )

    return daily_summary


# 5-) Bu fonksiyonun amacı:
# Veriyi kategori bazlı özetlemek.
# Her kategori için gelir, adet, sipariş sayısı ve ortalama performans puanı çıkarır.
# sample_sales.csv => date,category,product,quantity,unit_price
@beartype
def summarize_by_category(dataframe: pd.DataFrame) -> pd.DataFrame:
    # category kolonuna göre gruplayıp özet hesaplıyoruz.
    category_summary = (
        dataframe.groupby("category", as_index=False)
        .agg(
            total_revenue=("revenue", "sum"),
            total_quantity=("quantity", "sum"),
            order_count=("product", "count"),
            average_score=("performance_score", "mean"),
        )
        .sort_values("total_revenue", ascending=False)
        .reset_index(drop=True)
    )

    # Ortalama puanı daha okunabilir olsun diye 2 basamağa yuvarlıyoruz.
    category_summary["average_score"] = category_summary["average_score"].round(2)

    return category_summary


# 6-) Bu fonksiyonun amacı:
# Dashboard veya HTML raporda göstereceğimiz KPI metriklerini tek yerde toplamak.
@beartype
def calculate_metrics(dataframe: pd.DataFrame) -> dict[str, Any]:
    # Günlük özet veriyi alıyoruz.
    daily_summary = summarize_by_day(dataframe)

    # Kategori özet veriyi alıyoruz.
    category_summary = summarize_by_category(dataframe)

    # Toplam geliri hesaplıyoruz.
    total_revenue = float(dataframe["revenue"].sum())

    # Toplam ürün adedini hesaplıyoruz.
    total_quantity = int(dataframe["quantity"].sum())

    # Toplam sipariş sayısını hesaplıyoruz.
    total_orders = int(len(dataframe))

    # Ortalama sipariş tutarı hesaplıyoruz.
    average_order_value = float(total_revenue / total_orders) if total_orders else 0.0

    # Trend hesabı:
    # x ekseni 0,1,2,3... gibi günlük index dizisi olur.
    x_axis = np.arange(len(daily_summary))

    # polyfit ile günlük gelir trend eğimini hesaplıyoruz.
    # Eğer 1'den fazla gün yoksa eğim 0 kabul edilir.
    slope = float(np.polyfit(x_axis, daily_summary["total_revenue"], 1)[0]) if len(daily_summary) > 1 else 0.0

    # Eğim değerine göre yorum metni oluşturuyoruz.
    if slope > 5:
        trend_message = "Gelir trendi yükseliş yönünde."
    elif slope < -5:
        trend_message = "Gelir trendi düşüş yönünde."
    else:
        trend_message = "Gelir trendi dengeli görünüyor."

    # En iyi kategoriyi, kategori özet tablosunun ilk satırından alıyoruz.
    best_category = str(category_summary.iloc[0]["category"]) if not category_summary.empty else "-"

    # En güçlü günü, günlük gelir en yüksek olan tarihten alıyoruz.
    best_day = str(daily_summary.sort_values("total_revenue", ascending=False).iloc[0]["date"]) if not daily_summary.empty else "-"

    # Tüm KPI sonuçlarını tek sözlük halinde döndürüyoruz.
    return {
        "total_revenue": round(total_revenue, 2),
        "total_quantity": total_quantity,
        "total_orders": total_orders,
        "average_order_value": round(average_order_value, 2),
        "best_category": best_category,
        "best_day": best_day,
        "trend_message": trend_message,
    }



# 7-) Bu fonksiyonun amacı:
# Günlük toplam gelir grafiğini oluştursun ve PNG dosyasını oalrak diske kaydetsin.
@beartype
def create_daily_revenue_chart(daily_summary: pd.DataFrame,output_path: str|Path) -> Path:
    # Çıktı yolunu PAth nesnesine çevirelim.
    output= Path(output_path)

    # Klasör yoksa otomatik olarak oluştursun
    output.parent.mkdir(parents=True, exist_ok=True)

    # Grafik boyutunu belirliyoruz
    plt.figure(figsize=(10,4.5))

    # Çizgi grafik oluşturalım
    plt.plot(daily_summary["date"].astype(str), daily_summary["total_revenue"], marker="o")

    # Başlık ve Eksen isimlerini ekliyoruz
    plt.title("Günlük Toplam Gelir")
    plt.xlabel("Tarih")
    plt.ylabel("Gelir")

    # Tarih etiketlerini döndürerek okunabilir hale getirmek
    plt.xticks(rotation=45, ha="right")

    # Görsel taşmaları önlemek
    plt.tight_layout()

    # Grafigi PNG olarak kaydediliyor
    plt.savefig(output, dpi=120, bbox_inches="tight")

    # Belleğimizi temizlemek için grafiği kapatıyoruz
    plt.close()

    return output



# 8-) Bu fonksiyonun amacı:
# Kategorilerine göre toplam gelir grafiğini oluştursun Çubuk grafik ve PNG dosyasını oalrak diske kaydetsin.
@beartype
def create_category_revenue_chart(category_summary: pd.DataFrame,output_path: str|Path) -> Path:
    # Çıktı yolunu PAth nesnesine çevirelim.
    output= Path(output_path)

    # Klasör yoksa otomatik olarak oluştursun
    output.parent.mkdir(parents=True, exist_ok=True)

    # Grafik boyutunu belirliyoruz
    plt.figure(figsize=(8,4.5))

    # Çizgi grafik oluşturalım
    plt.bar(category_summary["category"], category_summary["total_revenue"])

    # Başlık ve Eksen isimlerini ekliyoruz
    plt.title("Kategori Göre Toplam Gelir")
    plt.xlabel("Kategori")
    plt.ylabel("Gelir")

    # X ekseni etiketlerini döndürerek okunabilir hale getirmek
    plt.xticks(rotation=20, ha="right")

    # Görsel taşmaları önlemek
    plt.tight_layout()

    # Grafigi PNG olarak kaydediliyor
    plt.savefig(output, dpi=120, bbox_inches="tight")

    # Belleğimizi temizlemek için grafiği kapatıyoruz
    plt.close()

    return output


# 9-) Bu fonksiyonun amacı:
# Pandas DataFrame'i HTML tablo string'e çevirmek
# Böylece rapor içine doğrudan gömülü bir şekilde dönüştürmek
@beartype
def dataframe_to_html_table(dataframe: pd.DataFrame, max_rows:int = 10) ->str:
    # Sadece ilk max_rows'a kadar satırı tabloya çeviriyoruz.
    return dataframe.head(max_rows).to_html(index=False, classes="table",border=0)




