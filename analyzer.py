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
def create_daily_revenue_chart(daily_summary: pd.DataFrame, output_path: str|Path) -> Path:
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


# 10-) Bu fonksiyonun amacı:
# PNG gibi görsel dosyasını base64 string haline çevirmek
# Böylece HTML içinde ayrı dosya çağırmadan direk olarak gömübilsin
@beartype
def image_to_base64(image_path: str|Path) ->str:
    # Dosyayı binary modda açıyoruz.
    with open(image_path, "rb") as image_file:
        # Dosyayı okuyup base64'e çeviriyoruz
        encoded= base64.b64decode(image_file.read()).decode("utf-8")

    return encoded

# 11-) Bu fonksiyonun amacı:
# Tek sayfalık HTML raporunu üretmek
# Tablolar, yorumlar, grafik bu alanda göster ve birleştir
@beartype
def build_html_report(
        metrics: dict[str,Any],
        category_summary:pd.DataFrame,
        daily_summary:pd.DataFrame,
        preview_data:pd.DataFrame,
        daily_chart_path: str | Path,
        category_chart_path: str | Path,
        output_html_path:str | Path,
) ->Path:
    # HTML dosyasının yazılacağı yolu Path nesnesine çeviriyoruz.
    output_path = Path(output_html_path)

    # Gerekirse klasörü oluşturuyoruz.
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Günlük gelir grafiğini base64 string haline getiriyoruz.
    daily_chart_base64 = image_to_base64(daily_chart_path)

    # Kategori gelir grafiğini base64 string haline getiriyoruz.
    category_chart_base64 = image_to_base64(category_chart_path)

    # Kategori özet tablosunu HTML tabloya çeviriyoruz.
    category_table_html = dataframe_to_html_table(category_summary, max_rows=10)

    # Günlük özet tablosunu HTML tabloya çeviriyoruz.
    daily_table_html = dataframe_to_html_table(daily_summary, max_rows=10)

    # Ham veri önizlemesini HTML tabloya çeviriyoruz.
    preview_html = dataframe_to_html_table(preview_data, max_rows=12)

    # Tüm rapor içeriğini tek HTML string olarak oluşturuyoruz.
    html_content = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Tek Sayfalık Satış Analiz Raporu</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #f5f7fb;
            margin: 0;
            padding: 0;
            color: #1f2937;
        }}
        .container {{
            width: min(1200px, 92%);
            margin: 30px auto;
        }}
        .header {{
            background: white;
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.06);
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
        }}
        .header p {{
            margin: 0;
            line-height: 1.6;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }}
        .card {{
            background: white;
            border-radius: 16px;
            padding: 18px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.05);
        }}
        .card h3 {{
            margin-top: 0;
            font-size: 15px;
            color: #4b5563;
        }}
        .metric {{
            font-size: 28px;
            font-weight: bold;
            margin: 8px 0;
        }}
        .section {{
            background: white;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }}
        .section h2 {{
            margin-top: 0;
        }}
        .chart-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 16px;
        }}
        .chart-box img {{
            width: 100%;
            border-radius: 12px;
            border: 1px solid #e5e7eb;
        }}
        .table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 12px;
            font-size: 14px;
            overflow: hidden;
        }}
        .table th, .table td {{
            border: 1px solid #e5e7eb;
            padding: 10px;
            text-align: left;
        }}
        .table th {{
            background: #eef2ff;
        }}
        .footer-note {{
            font-size: 13px;
            color: #6b7280;
            margin-top: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Tek Sayfalık Satış Analiz Raporu</h1>
            <p>
                Bu rapor; <strong>pandas</strong> ile veri işleme,
                <strong>numpy</strong> ile sayısal hesaplama,
                <strong>matplotlib</strong> ile grafik üretimi ve
                <strong>beartype</strong> ile tip kontrollü fonksiyon yapısını göstermek için hazırlanmıştır.
            </p>
        </div>

        <div class="grid">
            <div class="card">
                <h3>Toplam Gelir</h3>
                <div class="metric">{metrics['total_revenue']}</div>
            </div>
            <div class="card">
                <h3>Toplam Ürün Adedi</h3>
                <div class="metric">{metrics['total_quantity']}</div>
            </div>
            <div class="card">
                <h3>Toplam Sipariş</h3>
                <div class="metric">{metrics['total_orders']}</div>
            </div>
            <div class="card">
                <h3>Ortalama Sipariş Tutarı</h3>
                <div class="metric">{metrics['average_order_value']}</div>
            </div>
            <div class="card">
                <h3>En İyi Kategori</h3>
                <div class="metric">{metrics['best_category']}</div>
            </div>
            <div class="card">
                <h3>En Güçlü Gün</h3>
                <div class="metric">{metrics['best_day']}</div>
            </div>
        </div>

        <div class="section">
            <h2>Trend Yorumu</h2>
            <p>{metrics['trend_message']}</p>
            <p class="footer-note">Bu yorum, günlük gelir verisi üzerinden numpy ile hesaplanan eğim değerine göre oluşturulmuştur.</p>
        </div>

        <div class="section">
            <h2>Grafikler</h2>
            <div class="chart-grid">
                <div class="chart-box">
                    <h3>Günlük Gelir Grafiği</h3>
                    <img src="data:image/png;base64,{daily_chart_base64}" alt="Günlük gelir grafiği" />
                </div>
                <div class="chart-box">
                    <h3>Kategori Gelir Grafiği</h3>
                    <img src="data:image/png;base64,{category_chart_base64}" alt="Kategori gelir grafiği" />
                </div>
            </div>
        </div>

        <div class="section">
            <h2>Kategori Özeti</h2>
            {category_table_html}
        </div>

        <div class="section">
            <h2>Günlük Özet</h2>
            {daily_table_html}
        </div>

        <div class="section">
            <h2>Ham Veri Önizleme</h2>
            {preview_html}
            <p class="footer-note">Bu tablo, temizlenmiş veri setinin ilk 15 satırını göstermektedir.</p>
        </div>
    </div>
</body>
</html>
"""

    # Oluşturduğumuz HTML içeriğini dosyaya yazıyoruz.
    output_path.write_text(html_content, encoding="utf-8")

    # Sonuç olarak HTML dosya yolunu geri döndürüyoruz.
    return output_path