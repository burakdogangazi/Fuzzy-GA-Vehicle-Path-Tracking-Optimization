# Timing Summary - Hızlı Referans

## Tek Cümlelik Sonuç

**benchmark_subprocess.py:** 3-5 saat (KULLAN!)  
**benchmark.py:** 150-200 saat (Kullanma!)

---

## Saatlik Breakdown

### benchmark_subprocess.py (TERCIH ET)

```
Aggressive (6 run)  ..... 1 saat
Balanced (6 run)    ..... 1.7 saat  
Conservative (6 run) .... 2.2 saat
Export/Summary ...... 0.1 saat
────────────────────────────────
TOPLAM: ~5 saat
```

### benchmark.py (KAÇIN)

```
Aggressive (6 run)  ..... 31 saat
Balanced (6 run)    ..... 83 saat
Conservative (6 run) .... 188 saat
────────────────────────────────
TOPLAM: ~302 saat (12.6 gün!)
```

---

## Kısaca

| Metric | benchmark.py | subprocess |
|--------|--------------|-----------|
| Total Time | **150-200h** | **3-5h** |
| Faster | - | **40-50x** ⚡ |
| Practical | ❌ | ✅ |

**Sonuç: benchmark_subprocess.py'ı kullan!**
