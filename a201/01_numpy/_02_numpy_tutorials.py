import numpy as npm


print("Numpy  Sürümü : ", npm.__version__)

# Not: Liste benzerdir ancak iç yapı farklıdır
# NOTTTTT: Numpy array, sayısal işelmler için daha uygundur

# Liste
normal_liste= [20,10,30,40,50]
print(normal_liste)

# Numpy Liste
numpy_liste =npm.array([20,10,30,40,50])
print(numpy_liste)

dizi = npm.array([20,10,30,40,50])
print(dizi[0])  # ilk eleman
print(dizi[1])  # ikinci eleman
print(dizi[-1])  # son eleman
print(dizi[-2])  # son eleman bir önceki

# Toplu işlemler
print(dizi+15)
print(dizi*15)
print(dizi/15)


# Temel İstatistik (Math)
print("Toplam: ", npm.sum(dizi))
print("Ortalama: ", npm.mean(dizi))
print("En küçük: ", npm.min(dizi))
print("En büyük: ", npm.max(dizi))
print("Standart Sapma: ", npm.std(dizi))

# Belirli aralıkta sayı üretme
print(npm.arange(0,10,3))  # 0<=SAYI<=10-1

print(npm.linspace(0,1,6)) # 0 <= SAYI/4 <=1

# Sayı üretme (0 ve 1)
print(npm.zeros(3))
print(npm.ones(4))

# Rastgele sayı üretme
print(npm.random.randint(1,2,3)) # 1<=SAYI<=2-1  , 3= adet sayısı

# Matrix
# saymaya sıfırdan başla
matrix= npm.array([
    [1,2,3],
    [4,5,6]
])
print(matrix)
print("satır sayısı: ", matrix.shape[0])
print("sütun sayısı: ", matrix.shape[1])
print("şekili sayısı: ", matrix.shape)


# Matrix
matrix_data= npm.array([
    [10,20,30],
    [40,50,60],
    [70,80,90],
])
print("İlk satır:", matrix_data[0])
print("İlk sütun:", matrix_data[:,0])
print("ikinci sütun:", matrix_data[:,1])
print("İkinci satır üçüncü eleman:", matrix_data[1,2])

# Koşullu filtreleme
sayilar= npm.array([5,9,3,2,11,12,20])
print(sayilar[sayilar>11])
print(sayilar[sayilar>=11])