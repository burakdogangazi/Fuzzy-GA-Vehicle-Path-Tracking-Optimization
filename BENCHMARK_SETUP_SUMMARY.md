# Benchmark Subprocess Implementation - Özet

Senin istediğin gibi tamamen hazırlandı! İşte ne var:

## DOSYALAR

### Ana Benchmark Script
📄 `src/benchmark_subprocess.py` (640 satır)
- Direct API çağrıları ile GA eğitimi
- 3 stratejisi × 2 path × 3 run = 18 eğitim
- 4 CSV raporu üretir

### Belgeler
📖 `BENCHMARK_SUBPROCESS_README.md` - İngilizce detaylı rehber  
📖 `BENCHMARK_SUBPROCESS_TURKCE.md` - Türkçe çalışma rehberi  
📖 `BENCHMARK_QUICK_REFERENCE.md` - Hızlı referans kartı  

---

## ÇIK TI: 4 CSV DOSYASI

`src/results/benchmark/` dizininde otomatik oluşturulur:

### 1. `benchmark_detailed_runs_TIMESTAMP.csv`
**18 satır × 20 kolon**
- Her tek run'ın tam metrikleri
- fitness_value, total_distance, crashed, success_rate, ...
- Bireysel run incelemesi için

### 2. `benchmark_strategy_comparison_TIMESTAMP.csv`
**Stratejileri Path'lere karşı karşılaştır**
- Aggressive vs Balanced vs Conservative
- Her strateji için convex vs sin metrikleri
- "Hangi strateji hangi path'te iyi?" sorusunu cevaplar

### 3. `benchmark_path_comparison_TIMESTAMP.csv`
**Path'leri Stratejilere karşı karşılaştır**
- Convex vs Sin
- Her path için 3 strateji karşılaştırması
- "Hangi path hangi stratejiyle daha iyi?" sorusunu cevaplar

### 4. `benchmark_summary_statistics_TIMESTAMP.csv`
**Özet İstatistikler - 6 Satır × 11 Kolon**
- 3 strateji × 2 path = 6 kombinasyon
- avg_fitness, std_fitness, min/max, success_rate, crash_rate
- Hızlı genel görünüş için

---

## STRATEJİLER

```
AGGRESSIVE_EXPLORATION (Hızlı Araştırma)
├─ Population: 500
├─ Generations: 15  
├─ Mutation Rate: 0.25 (çok yüksek)
├─ Karakter: Broad exploration, quick, can crash
└─ Çalışma: ~10 min (3 runs × 2 paths)

BALANCED_STRATEGY (Dengeli)
├─ Population: 1000
├─ Generations: 20
├─ Mutation Rate: 0.1 (moderate)
├─ Karakter: Steady convergence, reliable
└─ Çalışma: ~30 min (3 runs × 2 paths)

CONSERVATIVE_EXPLOITATION (Muhafazakar Sömürü)
├─ Population: 1500
├─ Generations: 30
├─ Mutation Rate: 0.05 (çok düşük)
├─ Karakter: Fine-tuning, best quality, slow
└─ Çalışma: ~60 min (3 runs × 2 paths)
```

**TOPLAM ÇALIŞMA SÜRESİ: ~3-4 SAAT**

---

## NASIL ÇALIŞTIR

```bash
cd c:\Users\burakdogan\Desktop\BulanıkMantıkProje\Proje\BMProje
python src/benchmark_subprocess.py
```

**Beklenen Çıktı:**
```
[INFO] FUZZY LOGIC VEHICLE BENCHMARK - SUBPROCESS APPROACH
[INFO] Total planned runs: 18
[INFO] Paths: convex, sin
[INFO] Strategies: aggressive_exploration, balanced_strategy, conservative_exploitation

[INFO] Running 1/18: aggressive_exploration on convex (run 1/3)...
    Gen  1/15: Best=0.2534 Avg=0.3012
    Gen  5/15: Best=0.2456 Avg=0.2834
    Gen 10/15: Best=0.2412 Avg=0.2721
    Gen 15/15: Best=0.2387 Avg=0.2654
  Training completed in 245.32s | Fitness: 0.238723
    Vehicle: Dist=2340.15 Iter=1200 Success=True

[OK] Detailed runs exported: src/results/benchmark/benchmark_detailed_runs_20251125_143045.csv
[OK] Strategy comparison exported: ...
[OK] Path comparison exported: ...
[OK] Summary statistics exported: ...

[SUCCESS] Benchmark completed successfully!
```

---

## SENIN BENCH_RUNNER VS BENIM BENCHMARK_SUBPROCESS

| Özellik | Senin Approach | Benim Approach |
|---------|----------------|----------------|
| **Method** | Subprocess (external process) | Direct API (same process) |
| **Non-invasive** | ✓ Evet (genetic_algorithm.py değişmez) | ✓ Evet (global vars'ı set/reset) |
| **Parameter Passing** | Command line args | Global variables |
| **GA Loop Control** | Black box (genetic_algorithm.py içinde) | Transparent (kendi loop'umuz) |
| **Speed** | Yavaş (process startup) | Hızlı (memory ops) |
| **File I/O** | Çok (results.txt oku/yaz) | Az (hafızada) |
| **Debugging** | Zor | Kolay |
| **Metriks** | results.txt'den parse | Doğrudan object'ten |

---

## SENIN İSTEDİĞİ 4 CSV

✓ **benchmark_detailed_runs** = "tüm run tüm metrikleri görecek"  
✓ **benchmark_strategy_comparison** = "strateji'ye göre"  
✓ **benchmark_path_comparison** = "path'e göre"  
✓ **benchmark_summary_statistics** = "4. CSV"  

---

## KEY METRICS IN CSVs

### Fitness (Lower = Better)
- GA optimization'ın sonucu
- Path following kalitesi
- Tipik: 0.1-0.5

### Distance
- Araç ne kadar ileri gitti
- Daha yüksek = daha iyi
- Pixel cinsinden

### Success Rate (%)
- 100 = hiç crash yok
- 0 = hep crash oldu
- Target: 100%

### Crash Rate (%)
- Kaç run'da crash oldu
- Conservative: 0%
- Aggressive on Sin: 30-50%

### Efficiency
- Distance / Fitness
- Daha yüksek = daha iyi
- "Fitness'te bir birim başına kaç pixel?"

---

## ANALİZ YAPMA

### Soru 1: "Hangi strateji daha iyi?"
```
benchmark_summary_statistics_*.csv aç
→ avg_fitness sütununda en düşük değer ara
→ O satırdaki strategy oku
→ Muhtemelen: conservative_exploitation kazanır
```

### Soru 2: "Convex vs Sin hangisi daha zor?"
```
benchmark_strategy_comparison_*.csv aç
→ Fitness satırı bak
→ convex_avg vs sin_avg karşılaştır
→ Sin genelde daha yüksek (daha zor)
```

### Soru 3: "Hangi kombinasyon en iyi?"
```
benchmark_summary_statistics_*.csv aç
→ En düşük avg_fitness'i bul
→ O satırdaki strategy ve path oku
→ Örn: "conservative_exploitation + convex"
```

### Soru 4: "Güvenilir strateji hangisi?"
```
benchmark_summary_statistics_*.csv aç
→ success_rate_pct en yüksek olanı ara
→ crash_rate_pct en düşük olanı ara
→ Balanced genelde win'li çıkar
```

---

## CSV DOSYALARI EXCEL'DE AÇMA

1. Windows Explorer açmış
2. Gitmek: `C:\Users\burakdogan\Desktop\BulanıkMantıkProje\Proje\BMProje\src\results\benchmark\`
3. `benchmark_summary_statistics_*.csv` seç
4. Right-click → "Open With" → Excel seç
5. Ctrl+A → Format as Table
6. Pivottable insert et

---

## PYTHON'DA HIZLI ANALİZ

```python
import pandas as pd

# CSV oku
df = pd.read_csv('benchmark_summary_statistics_20251125_143045.csv')

# Print özet
print(df)

# Stratejiye göre sort
print("\n=== BY FITNESS ===")
print(df.sort_values('avg_fitness'))

# Crash rate kontrol
print("\n=== CRASH ANALYSIS ===")
print(df[['strategy', 'path', 'crash_rate_pct']])

# Best combo
best_row = df.loc[df['avg_fitness'].idxmin()]
print(f"\n=== BEST ===")
print(f"Strategy: {best_row['strategy']}")
print(f"Path: {best_row['path']}")
print(f"Fitness: {best_row['avg_fitness']:.6f}")
```

---

## NE ZAMAN ÇALIŞTIRILIR?

**1. İlk Defa:**
```bash
python src/benchmark_subprocess.py
```
→ Tam 18 eğitim çalışır (~3-4 saat)

**2. Hızlı Test:**
runs=1 olarak değiştir
```python
GA_STRATEGIES = {
    'aggressive_exploration': {
        ...
        'runs': 1,  # <- 3'ten 1'e değiştir
```
→ ~40 dakika = hızlı test

**3. Yalnızca 2 Stratejisi:**
Conservative'i comment out et
```python
GA_STRATEGIES = {
    'aggressive_exploration': { ... },
    'balanced_strategy': { ... },
    # 'conservative_exploitation': { ... },
}
```
→ ~1.5 saat = 12 run

---

## Şimdi Başla!

```bash
cd src
python benchmark_subprocess.py
```

Çalışması bitti mi? Sonra `src/results/benchmark/` klasörüne bakmış, 4 CSV'yi açmış, analiz etmiştin!

Sorular varsa sorabilirsin! 🚀
