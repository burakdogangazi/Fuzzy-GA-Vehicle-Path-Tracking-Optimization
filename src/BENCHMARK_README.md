# Benchmark Script - Strateji & Yol Karşılaştırması

## Genel Bakış

Bu script, **3 farklı Genetik Algoritma stratejisini** iki farklı yol üzerinde karşılaştırır:

### GA Stratejileri:
1. **Aggressive Exploration** - Yüksek mutasyon, geniş arama
2. **Balanced Strategy** - Dengeli keşif-sömürü
3. **Conservative Exploitation** - Düşük mutasyon, güçlü yakınsama

### Yollar:
- **Convex Path** (Dışbükey yol)
- **Sin Path** (Sinüs dalgalı yol)

## Nasıl Kullanılır?

```bash
cd src/
python benchmark.py
```

## Strateji Parametreleri

| Parametre | Aggressive | Balanced | Conservative |
|-----------|-----------|----------|--------------|
| **Pop. Size** | 500 | 1000 | 1500 |
| **Generations** | 15 | 20 | 30 |
| **Elitism Ratio** | 0.02 | 0.05 | 0.15 |
| **Mutation Rate** | 0.25 | 0.1 | 0.05 |
| **Mutation Span** | 3 | 2 | 1 |
| **Tournament Size** | 3 | 5 | 7 |

### Strateji Özellikleri:

#### 🔴 Aggressive Exploration
```
Hedef: Geniş çözüm uzayını keşfet
Avantaj: Farklı çözümler bulur, lokal optimumdan kaçar
Dezavantaj: Hızlı yakınsama yapamaz, istikrarsız
Kullanım: İlk keşif, bilinmeyen problemler
```

#### 🟡 Balanced Strategy
```
Hedef: Keşif ve sömürü dengesini sağla
Avantaj: Hem iyi çözüm kalitesi hem de istikrarlılık
Dezavantaj: En hızlı olmayabilir
Kullanım: Genel amaçlı kullanım, tavsiye edilen
```

#### 🟢 Conservative Exploitation
```
Hedef: İyi çözümü derinlemesine iyileştir
Avantaj: Yüksek kaliteli çözümler, hızlı yakınsama
Dezavantaj: Lokal optimumda takılabilir
Kullanım: Çözüm tanındığında iyileştirme
```

## Ne Yapıyor?

### 1. **Eğitim (Training)**
```
For each strategy in [aggressive, balanced, conservative]:
    For each path in [convex, sin]:
        Run 3 independent GA trainings
```

**Total eğitim sayısı:** 3 strateji × 2 yol × 3 eğitim = **18 eğitim**

### 2. **Değerlendirme (Evaluation)**
Her eğitim sonucu şu metrikleri hesaplar:

| Metrik | Açıklama | Formül |
|--------|----------|--------|
| **Fitness Value** | GA uygunluğu (düşük iyidir) | Sol-sağ dengesizlik + ceza |
| **Left-Right Balance** | Araç dengesi | `Σ\|left_sensor - right_sensor\| / iter` |
| **Total Distance** | Toplam hareket | `Σ ds` |
| **Iterations Completed** | Adım sayısı | Sayac |
| **Collision Penalty** | Çarpışma cezası | 0, 50 (idle), 150 (crash) |
| **Success Rate** | Başarı oranı | 1.0 (başarı), 0.0 (başarısızlık) |
| **Efficiency Score** | Verimlilik | `distance / (fitness + 0.0001)` |

### 3. **Karşılaştırma**
Üç CSV dosyası oluşturur:

#### `benchmark_detailed_[timestamp].csv`
Tüm eğitimler için detaylı metrikleri içerir.

```
Path,Strategy,Training_ID,Fitness_Value,Total_Distance,Success_Rate
convex,aggressive,1,2.54,450.23,1.0
convex,aggressive,2,2.34,420.15,1.0
convex,aggressive,3,2.09,480.45,1.0
convex,balanced,1,2.15,450.23,1.0
...
sin,conservative,3,1.89,530.20,1.0
```

#### `benchmark_strategies_[timestamp].csv`
Her strateji için yol karşılaştırması:

```
Metric,Strategy,Convex Path,Sin Path,Difference,Winner
Avg Fitness (lower is better),aggressive,2.3233,2.1098,0.2135,Sin
Avg Fitness (lower is better),balanced,2.1984,1.8967,0.3017,Sin
Avg Fitness (lower is better),conservative,1.9876,2.0234,-0.0358,Convex
Success Rate,aggressive,1.0,1.0,0.0,Tie
Success Rate,balanced,1.0,1.0,0.0,Tie
```

#### `benchmark_paths_[timestamp].csv`
Her yol için strateji karşılaştırması:

```
Metric,Path,Aggressive,Balanced,Conservative,Best
Avg Fitness (lower is better) (CONVEX),convex,2.3233,2.1984,1.9876,Conservative
Avg Fitness (lower is better) (SIN),sin,2.1098,1.8967,2.0234,Balanced
Success Rate (CONVEX),convex,1.0,1.0,1.0,Tie
Success Rate (SIN),sin,1.0,1.0,1.0,Tie
```

### 4. **Konsol Çıktısı**
Eğitim ve karşılaştırma sonuçlarını konsola yazdırır:

```
================================================================================
FUZZY LOGIC VEHICLE BENCHMARK - PATH & STRATEGY COMPARISON
================================================================================

Configuration:
  - Strategies: ['aggressive', 'balanced', 'conservative']
  - Paths: convex, sin
  - Total combinations: 6

################################################################################
# STRATEGY: AGGRESSIVE EXPLORATION
# High mutation, high diversity - explores solution space aggressively
################################################################################

********************************************************************************
* PATH: CONVEX | STRATEGY: AGGRESSIVE
********************************************************************************

  Training 1/3 for convex path...
    Gen  5/15: Best=2.5431 Avg=3.1234
    Gen 10/15: Best=2.3421 Avg=3.0145
    Gen 15/15: Best=2.3233 Avg=2.9876
  ✓ Training 1 completed! Fitness: 2.3233

...

================================================================================
EVALUATION & COMPARISON
================================================================================

Evaluating aggressive strategy on convex path...
  Training 1: Fitness=2.3233 Dist=450 Iter=450 Success=✓
  Training 2: Fitness=2.3421 Dist=420 Iter=420 Success=✓
  Training 3: Fitness=2.0987 Dist=480 Iter=480 Success=✓

...

================================================================================
BENCHMARK SUMMARY - STRATEGIES & PATHS COMPARISON
================================================================================

AGGRESSIVE STRATEGY - Aggressive Exploration
--------------------------------------------------------------------------------

  CONVEX PATH:
    Avg Fitness:      2.3233 ± 0.1224
    Fitness Range:    [2.0987, 2.5431]
    Avg Distance:     450.13 pixels
    Success Rate:     100.0%
    Efficiency Score: 193.87

  SIN PATH:
    Avg Fitness:      2.1098 ± 0.0876
    Fitness Range:    [2.0120, 2.2145]
    Avg Distance:     520.45 pixels
    Success Rate:     100.0%
    Efficiency Score: 246.52

BALANCED STRATEGY - Balanced Strategy
...

================================================================================
CONCLUSION: STRATEGY IMPACT ON PATH PERFORMANCE
================================================================================

CONVEX PATH - Best Strategy:
  🏆 Winner: CONSERVATIVE
     Average Fitness: 1.9876

SIN PATH - Best Strategy:
  🏆 Winner: BALANCED
     Average Fitness: 1.8967

OVERALL - Best Path per Strategy:
  AGGRESSIVE: SIN path (9.16% better)
  BALANCED: SIN path (13.71% better)
  CONSERVATIVE: CONVEX path (2.55% better)
```

## Çıktı Dosyaları

Tüm sonuçlar `results/benchmark/` klasöründe kaydedilir:

```
results/
└── benchmark/
    ├── benchmark_detailed_20251125_143022.csv    # Tüm metrikleri
    ├── benchmark_strategies_20251125_143022.csv  # Strateji karşılaştırması
    └── benchmark_paths_20251125_143022.csv       # Yol karşılaştırması
```

## Akademik Yorumlama

### Sonuç Analizi Örneği:

**"Conservative strateji Convex yolda daha iyi performans gösteriyor"**

Bu sonuç şu anlamı taşır:
- Convex yolunun **basit yapısı**, düşük mutasyonla bulunabilir (Conservative özelliği)
- Sin yolu daha karmaşık olduğu için **daha fazla keşif** gerekiyor (Balanced tercih)
- GA parametrelerinin yol türüne **uyarlanması** başarı için önemli

### İlgili Araştırma Soruları:

1. **Strateji-Yol İlişkisi:** Hangi strateji hangi yol tipinde daha etkili?
2. **Yakınsama Hızı:** Conservative neden daha hızlı yakınsıyor?
3. **Çeşitlilik:** Aggressive neden farklı sonuçlar veriyor?
4. **İstikrarlılık:** Hangi strateji en kararlı (düşük std)?

## İlgili Dosyalar

- `genetic_algorithm.py` - Temel GA implementasyonu
- `ga_fitness.py` - Fitness fonksiyonu
- `fuzzy_generator.py` - Fuzzy sistem generator
- `vehicle.py` - Araç simülasyonu
- `decoder.py` - Fuzzy çıktısı → hareket parametresi

## Notlar

- Script **non-invasive** olarak tasarlanmıştır
- Mevcut `genetic_algorithm.py`'yi değiştirmez
- Global değişkenler geçici olarak ayarlanır
- Her eğitim bitmesinde bellek temizlenir

