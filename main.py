"""
Bu dosya ile projenin giriş noktası olacak.
main.py Çalıştırdığımızda;
1-) CSV verisini okur, analiz eder, garfikleri üretir
2-) Tek sayfalık HTML raporunu yorumlar
3-) Window 64bit Pro -> Google Chrome Varsayılan tararcıda otomatik olarka açar
"""

# 1) Gerekli modülleri içe aktarıyoruz.
from pathlib import Path
import webbrowser

from analyzer import (
    build_html_report,
    calculate_metrics,
    create_category_revenue_chart,
    create_daily_revenue_chart,
    load_sales_data,
    prepare_sales_data,
    summarize_by_category,
    summarize_by_day,
)


# 2) Ana çalışma fonksiyonunu tanımlıyoruz.
# Bu yapı kodun okunmasını ve ileride büyütülmesini kolaylaştırır.
def main() -> None:
    project_root = Path(__file__).resolve().parent
    data_file = project_root / "data" / "sample_sales.csv"
    output_dir = project_root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 3) Veriyi yükleyip temizliyoruz.
    raw_dataframe = load_sales_data(data_file)
    clean_dataframe = prepare_sales_data(raw_dataframe)

    # 4) Özet verileri ve KPI sonuçlarını hesaplıyoruz.
    daily_summary = summarize_by_day(clean_dataframe)
    category_summary = summarize_by_category(clean_dataframe)
    metrics = calculate_metrics(clean_dataframe)

    # 5) Grafik dosyalarını üretiyoruz.
    daily_chart_path = create_daily_revenue_chart(daily_summary, output_dir / "daily_revenue.png")
    category_chart_path = create_category_revenue_chart(category_summary, output_dir / "category_revenue.png")

    # 6) Tek sayfalık HTML raporunu oluşturuyoruz.
    report_path = build_html_report(
        metrics=metrics,
        category_summary=category_summary,
        daily_summary=daily_summary,
        preview_data=clean_dataframe,
        daily_chart_path=daily_chart_path,
        category_chart_path=category_chart_path,
        output_html_path=output_dir / "report.html",
    )

    # 7) Kullanıcıya çıktı bilgisini terminalden veriyoruz.
    print("Rapor başarıyla oluşturuldu.")
    print(f"HTML raporu: {report_path}")
    print(f"Günlük grafik: {daily_chart_path}")
    print(f"Kategori grafik: {category_chart_path}")

    # 8) Raporu varsayılan tarayıcıda otomatik açıyoruz.
    try:
        report_uri = report_path.resolve().as_uri()
        opened = webbrowser.open(report_uri)
        if opened:
            print("Rapor varsayılan tarayıcıda açıldı.")
        else:
            print("Tarayıcı otomatik açılamadı. report.html dosyasını manuel açabilirsin.")
    except Exception as error:
        print(f"Tarayıcı açılırken hata oluştu: {error}")
        print("report.html dosyasını manuel açabilirsin.")


