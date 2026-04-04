"""
Bu dosya: projenin veri analizi ve rapor üretim mantığını taşır.
Bizim amacımız: kodu parçalara bölmek ve her bir parçayı SOLID(Single Responsibility) göre yönetmek  ==> Yani Modüler olmasını sağlamak
"""

# 1-) Gerekli kütüphaneleri içe aktarıyoruz.
"""
    Pandas     => Veri işleme
    Numpy      => Sayısal Hesaplama
    Matplotlib => Grafik üretimi
    Beartype   => Fonksiyonlara tip kontrolü için
"""

from __future__ import annotations
from pathlib import Path
from typing import Any
import base64
import io

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# beartype: decorator yazalım.

