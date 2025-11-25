# benchmark_subprocess.py - Kurulum ve Kullanım Rehberi

## Hızlı Başlangıç

```bash
cd src/
python benchmark_subprocess.py
```

---

## Ne Yapar?

Senin `bench_runner.py` approach'ı **doğrudan API çağrıları** ile uygulanmıştır:

1. **3 Stratejide GA Eğitimi** yapıyor (Aggressive, Balanced, Conservative)
2. **2 Path'te** her stratejiyyi çalıştırıyor (Convex, Sin)
3. **3 kez tekrarlıyor** her kombinasyonu (toplam 18 eğitim)
4. **4 farklı CSV** raporu üretiyor

---

## Çıktı Dosyaları

`src/results/benchmark/` dizininde:

### 1. **benchmark_detailed_runs_TIMESTAMP.csv**
Her tek tek run'ın **tüm metrikleri** 

```
strategy,path,run_id,fitness_value,total_distance,crashed,success_rate,...
aggressive_exploration,convex,1,0.2456,2340.15,0,1.0,...
aggressive_exploration,convex,2,0.2512,2280.40,0,1.0,...
aggressive_exploration,convex,3,0.2634,2100.60,0,1.0,...
balanced_strategy,convex,1,0.1845,3450.20,0,1.0,...
balanced_strategy,sin,1,0.2450,2156.40,1,0.0,...
...
```

### 2. **benchmark_strategy_comparison_TIMESTAMP.csv**
Stratejiler arasında **karşılaştırma**

```
metric,strategy,convex_avg,sin_avg,convex_better,win_margin
Fitness (lower is better),aggressive_exploration,0.2534,0.3123,Yes,18.83%
Fitness (lower is better),balanced_strategy,0.1845,0.2450,Yes,24.78%
Fitness (lower is better),conservative_exploitation,0.1567,0.1923,Yes,18.52%
Success Rate (%),aggressive_exploration,100.0,66.7,Yes,50.00%
Success Rate (%),balanced_strategy,100.0,100.0,Tie,0.00%
Success Rate (%),conservative_exploitation,100.0,100.0,Tie,0.00%
...
```

**Nasıl Okunur:**
- `convex_avg`: Convex path'te ortalama metrik
- `sin_avg`: Sin path'te ortalama metrik
- `convex_better`: Convex path daha iyi mi?
- `win_margin`: Ne kadar fark?

### 3. **benchmark_path_comparison_TIMESTAMP.csv**
Path'ler arasında **stratejileri karşılaştır**

```
metric,path,aggressive_avg,balanced_avg,conservative_avg,best_strategy
Fitness (lower is better),convex,0.2534,0.1845,0.1567,conservative_exploitation
Fitness (lower is better),sin,0.3123,0.2450,0.1923,conservative_exploitation
Success Rate (%),convex,100.0,100.0,100.0,balanced_strategy
Success Rate (%),sin,66.7,100.0,100.0,balanced_strategy
...
```

**Nasıl Okunur:**
- Hangi stratejinin hangi path'te en iyi?
- Conservative genelde daha iyi fitness (ama daha yavaş)
- Balanced en güvenilir (hiç crash yok)

### 4. **benchmark_summary_statistics_TIMESTAMP.csv**
Her kombinasyon için **özet istatistikler**

```
strategy,path,num_runs,avg_fitness,std_fitness,avg_distance,success_rate_pct,crash_rate_pct
aggressive_exploration,convex,3,0.2534,0.0089,2240.38,100.0,0.0
aggressive_exploration,sin,3,0.3123,0.0245,2179.13,66.7,33.3
balanced_strategy,convex,3,0.1845,0.0056,3450.20,100.0,0.0
balanced_strategy,sin,3,0.2450,0.0134,2894.50,100.0,0.0
conservative_exploitation,convex,3,0.1567,0.0089,3890.60,100.0,0.0
conservative_exploitation,sin,3,0.1923,0.0145,3456.80,100.0,0.0
```

**Özet İstatistikleri:**
- `avg_fitness`: Ortalama fitness (düşük=iyi)
- `std_fitness`: Fitness'in tutarlılığı (düşük=tutarlı)
- `success_rate_pct`: Başarılı run yüzdesi
- `crash_rate_pct`: Çarpışma yüzdesi (düşük=güvenli)

---

## Stratejiler Arasında Farklar

| Stratejisi | Pop | Gen | Mutation | Karakteri |
|-----------|-----|-----|----------|-----------|
| **Aggressive** | 500 | 15 | 0.25 | Exploratory, risky, can crash |
| **Balanced** | 1000 | 20 | 0.10 | Steady, reliable, safe |
| **Conservative** | 1500 | 30 | 0.05 | Quality-focused, best fitness |

---

## Tahmini Çalışma Süresi

- **Aggressive × Convex:** ~15-20 dakika
- **Aggressive × Sin:** ~15-20 dakika
- **Balanced × Convex:** ~25-30 dakika
- **Balanced × Sin:** ~25-30 dakika
- **Conservative × Convex:** ~40-50 dakika
- **Conservative × Sin:** ~40-50 dakika

**Toplam:** ~170-200 dakika (~3-4 saat)

(Sistem performansına bağlı değişir)

---

## CSV Dosyalarını Analiz Etme

### Adım 1: Genel Karşılaştırma
`benchmark_summary_statistics_*.csv` aç
→ Hangi stratejinin en iyi fitness'i?

### Adım 2: Path Zorluk Derecesi
`benchmark_strategy_comparison_*.csv` aç
→ Convex vs Sin'den hangisi daha zor?

### Adım 3: Stratejiye Göre Seçim
`benchmark_path_comparison_*.csv` aç
→ Her path için hangi strateji önerilir?

### Adım 4: Detaylı İnceleme
`benchmark_detailed_runs_*.csv` aç
→ Bireysel run'ları incelemek için

---

## Dikkat Edilecekler

### Fitness Değerleri
- Lower is Better (düşük=iyi)
- Tipik 0.1-0.5 arasında
- Eğer 1.0+ ise path following çok kötü

### Success Rate
- 100.0% = hiç crash yok
- 0.0% = hep crash oldu
- 50-70% = orta, çapraz hatalar mümkün

### Crash Rate
- Aggressive'de daha yüksek olması normal
- Conservative'de 0% olması beklenen
- Balanced genelde 0% (güvenli)

### Distance vs Fitness Trade-off
- Daha uzun distance ≠ daha iyi fitness
- Fitness path following kalitesini ölçüyor
- Distance sadece ilerleyişi ölçüyor

---

## Sorun Giderme

**"Permission denied" hatası?**
- `src/results/benchmark/` klasörü var mı?
- Yazma izni var mı?

**"Import error"?**
- genetic_algorithm.py düzgün üretildi mi?
- Tüm import'lar var mı?

**CSV dosya boş?**
- Python process bitti mi?
- Exception fırladı mı?
- Terminal'de hata mesajı var mı?

**Çok yavaş çalışıyor?**
- Conservative stratejisini skip et (runs=1 olarak değiştir)
- max_iterations'ı azalt
- population_size'ı azalt

---

## Customization

`benchmark_subprocess.py` içinde `GA_STRATEGIES` dictionary'sini düzenleyebilirsin:

```python
GA_STRATEGIES = {
    'aggressive_exploration': {
        'population_size': 500,    # <- Burayı değiştir
        'max_iterations': 15,      # <- Ya da burayı
        'runs': 3,                 # <- Veya run sayısını
        ...
    }
}
```

---

## Çalıştır!

```bash
cd c:\Users\burakdogan\Desktop\BulanıkMantıkProje\Proje\BMProje
python src/benchmark_subprocess.py
```

Çıktı alacaksın. CSV dosyaları Excel/Python ile açabilirsin!

🚀 İyi şanslar!
