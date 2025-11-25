# BENCHMARK_SUBPROCESS.PY - QUICK REFERENCE

## BAŞLA
```bash
cd src && python benchmark_subprocess.py
```

## ÇIKIŞ DOSYALARI (src/results/benchmark/)

### 1. benchmark_detailed_runs_*.csv
- **İçerik:** Tüm 18 run'ın tüm metrikleri
- **Kullanım:** Bireysel run'ları incelemek
- **Satırlar:** 18 tane (3 strateji × 2 path × 3 run)
- **Kolonnlar:** fitness, distance, crashed, success_rate, ...

### 2. benchmark_strategy_comparison_*.csv  
- **İçerik:** Stratejileri path'lere karşı karşılaştır
- **Kullanım:** Hangi strateji hangi path'te iyi?
- **Yapı:** Her metrik için 3 satır (3 strateji)
- **Örnek:** Aggressive convex fitness=0.25, sin fitness=0.31

### 3. benchmark_path_comparison_*.csv
- **İçerik:** Path'leri stratejilere karşı karşılaştır  
- **Kullanım:** Hangi path hangi stratejiyle daha iyi?
- **Yapı:** Her metrik için 2 satır (2 path)
- **Örnek:** Convex aggressive=0.25, balanced=0.18, conservative=0.16

### 4. benchmark_summary_statistics_*.csv
- **İçerik:** Özet istatistikler her kombinasyon için
- **Kullanım:** Hızlı görünüm
- **Satırlar:** 6 tane (3 strateji × 2 path)
- **Kolonnlar:** avg_fitness, std_fitness, success_rate, crash_rate, ...

---

## KÖKEYMETRİKLER

| Metrik | Anlamı | İyi Değer |
|--------|--------|-----------|
| fitness | Path takip kalitesi (düşük=iyi) | 0.1-0.3 |
| distance | Araç kaç piksel ilerlemişi | Yüksek |
| success_rate | % başarılı run | 100% |
| crash_rate | % çarpışan run | 0% |
| iterations | Kaç adım ileri gitti | Yüksek |
| efficiency | distance/fitness | Yüksek |

---

## STRATEJİLER

| | **Aggressive** | **Balanced** | **Conservative** |
|---|---|---|---|
| **Pop** | 500 | 1000 | 1500 |
| **Gen** | 15 | 20 | 30 |
| **Mutation** | 0.25 | 0.10 | 0.05 |
| **Crash Risk** | Yüksek | Düşük | Çok Düşük |
| **Fitness Quality** | Orta | İyi | Çok İyi |
| **Süre** | Hızlı | Orta | Yavaş |

---

## OKUMA TALIMATATI

### "Convex path daha kolay mi?"
1. `benchmark_strategy_comparison_*.csv` aç
2. Tüm satırlar'da convex_avg < sin_avg mı bak?
3. Evet = Convex daha kolay

### "Hangi strateji tercih?"  
1. `benchmark_summary_statistics_*.csv` aç
2. Düşük avg_fitness'i bul = O strateji tercih
3. Conservative genelde kazanır (daha iyi fitness)

### "Güvenilir strateji hangisi?"
1. `benchmark_summary_statistics_*.csv` aç
2. Yüksek success_rate_pct'i bul = O strateji güvenilir
3. Düşük crash_rate_pct'i bul = O strateji crash yapmıyor

---

## CSV OKUMA ÖRNEKLERİ

### Örnek 1: benchmark_summary_statistics
```
strategy,path,avg_fitness,success_rate_pct,crash_rate_pct
aggressive_exploration,convex,0.2534,100.0,0.0         <- Convex safe
aggressive_exploration,sin,0.3123,66.7,33.3            <- Sin risky!
balanced_strategy,convex,0.1845,100.0,0.0              <- Better fitness
conservative_exploitation,convex,0.1567,100.0,0.0      <- Best fitness!
```

**Sonuç:** Conservative = en iyi fitness. Balanced = güvenli. Aggressive = risky on Sin.

### Örnek 2: benchmark_strategy_comparison
```
metric,strategy,convex_avg,sin_avg,convex_better,win_margin
Fitness,aggressive,0.25,0.31,Yes,19.4%
Fitness,balanced,0.18,0.24,Yes,25.0%
Fitness,conservative,0.16,0.19,Yes,15.8%
```

**Sonuç:** Conservative çok fazla fark yok (daha robust). Others bigger gap (less robust).

---

## TİPİK BULGULAR

✓ Conservative > Balanced > Aggressive (fitness kalitesi)  
✓ Convex < Sin (path zorluk derecesi)  
✓ Balanced = Most reliable (crash yok)  
✓ Conservative = Best quality (yavaş ama iyi)  
✓ Aggressive = Fast but risky (crash olabilir)

---

## EĞİTİM SÜRESİ

```
Aggressive:   3 runs × 2 paths = 6 run    ≈ 30 min
Balanced:     3 runs × 2 paths = 6 run    ≈ 60 min
Conservative: 3 runs × 2 paths = 6 run    ≈ 100 min
─────────────────────────────────────────────────
TOPLAM:       3 strategies × 2 paths × 3 = ≈ 3-4 saat
```

---

## EXCEL'DE AÇMA

1. `src/results/benchmark/` klas açmış
2. `benchmark_summary_statistics_*.csv` dosya sağ tıkla
3. "Open with" → Excel seç
4. Kolonlar otomatik görünecek ✓

---

## PYTHON'DA ANALİZ

```python
import pandas as pd

# Özet istatistikler oku
df = pd.read_csv('benchmark_summary_statistics_20251125_143045.csv')

# En iyi stratejyi bul
best = df.loc[df['avg_fitness'].idxmin()]
print(f"Best: {best['strategy']} on {best['path']}")
print(f"Fitness: {best['avg_fitness']:.4f}")

# Convex vs Sin karşılaştır
convex = df[df['path'] == 'convex']
sin = df[df['path'] == 'sin']
print(f"Convex avg fitness: {convex['avg_fitness'].mean():.4f}")
print(f"Sin avg fitness: {sin['avg_fitness'].mean():.4f}")
```

---

## HATA YÖNETİMİ

| Hata | Çözüm |
|------|-------|
| Import error | genetic_algorithm.py var mı? |
| Permission error | `src/results/benchmark/` yazılabilir mi? |
| Empty CSV | Process tamamlandı mı? Terminal'de error var mı? |
| Timeout | Conservative skip et, daha hızlı çalış |

---

## SONUÇ

**4 CSV = Complete Picture:**
1. Detailed: Mikro görünüş (her run)
2. Strategy: Strateji karşılaştırması
3. Path: Path karşılaştırması  
4. Summary: Makro görünüş (özet)

🎯 Run et, CSV'leri aç, analiz et!
