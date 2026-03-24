# 📊 WEEKLY REPORT TEMPLATE

**Use this template EVERY FRIDAY at 21:00 GMT+1**
**Owner:** CHAT 4 (Monitoring & Reporting)
**Distribution:** MASTER + all CHATs

---

## 📋 HEADER

```
WEEKLY REPORT — Week of [MON DD.MM.YYYY to FRI DD.MM.YYYY]
Reporting Week: Week [N] of 13 (Paper Trading Period)
Days Trading: [X] / 7
Report Generated: 2026-03-24 21:00 GMT+1
```

---

## 📈 KEY METRICS (High-level summary)

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Win Rate %** | 62% | ≥60% | ✅ |
| **Profit Factor** | 1.87 | >1.5 | ✅ |
| **Weekly PnL** | +$234.56 | >0 | ✅ |
| **PnL %** | +2.35% | >0 | ✅ |
| **Max Drawdown** | -2.1% | <5% | ✅ |
| **Uptime** | 99.2% | ≥99% | ✅ |
| **Cumulative PnL** | +$456.78 | >+$100 | ✅ |

---

## 📊 DETAILED BREAKDOWN

### Trades Summary
```
Period: [MON-FRI]
Total Trades: 67
Winning Trades: 42 (62%)
Losing Trades: 25 (38%)

Average Win: $45.23
Average Loss: -$28.15
Largest Win: +$123.45 (BTCUSDT)
Largest Loss: -$89.20 (ETHUSDT)
```

### Daily Breakdown
```
MON: 11 trades, 64% win, +$145.23
TUE: 15 trades, 67% win, +$289.45
WED: 18 trades, 72% win, +$456.78 ← BEST DAY
THU: 12 trades, 58% win, +$123.45
FRI: 11 trades, 63% win, +$219.65
```

### Pair Performance
```
Rank | Pair     | Trades | Win% | PnL      | Status
-----|----------|--------|------|----------|--------
1    | BTCUSDT  | 26     | 68%  | +$234.45 | 🟢 Strong
2    | ETHUSDT  | 25     | 64%  | +$156.78 | 🟢 Good
3    | BNBUSDT  | 22     | 59%  | +$98.12  | 🟡 Weak
...
25   | RNDRUSDT | 10     | 48%  | -$15.34  | 🔴 Poor
```

---

## ⚡ INCIDENTS & ALERTS

### Critical Issues
```
- None this week ✅
```

### Warnings (Monitor)
```
- RNDRUSDT: 48% win (below 50% threshold) → Consider removing
- Thu 15:30 UTC: 3 consecutive losses → Normal variance
```

### SL Audit
```
- Total trades: 67
- SL placed at entry: 67/67 ✅ (100%)
- SL triggered when hit: 67/67 ✅ (100%)
- SL failures: 0 ✅
- Accuracy: 100% ✅
```

### Risk Rule Compliance
```
- Position sizing (≤1% risk): 67/67 ✅ (100%)
- Exposure limit (<5%): Always ✅ (Max: 3.8%)
- Daily loss limit (-1.5%): Never exceeded ✅ (Max: -0.45%)
- ATR-based SL: 67/67 ✅ (All ATR×2.0)
- Compliance: 100% ✅
```

---

## 🎯 DECISIONS MADE THIS WEEK

| Date | Decision | Outcome |
|------|----------|---------|
| MON | Tested ATR×1.8 vs 2.0 on BTCUSDT | 1.8 = higher SL hits, keep 2.0 |
| WED | Reduced position size Wed-Thu | Improved win rate +4% |
| FRI | Approved TP 0.65% for next week test | Ready to deploy Mon |

---

## 📈 TRENDS & PATTERNS

### Win Rate Trend
```
Mon: 64% ↗
Tue: 67% ↗ PEAK
Wed: 72% ↗ PEAK
Thu: 58% ↘ dip
Fri: 63% ↗ recovering

7-day avg: 65% → Target 60% ✅
Trend: Stable / Strong
```

### PnL Trend
```
Daily:  +145 → +289 → +456 → +123 → +219
Weekly: +$1,234.56 ✅
MTD:    +$1,234.56 (first week)
Trend:  Strong start
```

### Time-of-Day Performance
```
00-08 UTC (Asia): 58% win, 12 trades
08-16 UTC (Europe): 68% win, 35 trades ← BEST
16-24 UTC (Americas): 61% win, 20 trades

Insight: Peak performance 08-16 UTC
→ Consider focusing orders in this window next week
```

### Pair Correlation
```
BTCUSDT / ETHUSDT correlation: 0.87 (high)
→ When one trades, other likely trades too
→ Consider reducing overlap (trade fewer alts when BTC moves)

Best performing pairs: BTC, ETH, BNB
Worst performing pairs: RND, SEI, FIL
→ Consider pair-specific TP/SL next week
```

---

## 💾 ACCOUNT STATUS

```
Starting Balance (Week 1): $10,000.00
Week PnL:                 +$1,234.56
Current Balance:          $11,234.56
Week Return:              +12.35% ✅

Cumulative (since 2026-03-17):
Starting: $10,000.00
Current:  $10,456.78
Total PnL: +$456.78
Return: +4.57% ✅

Exposure (EOD Fri): 3.2% (OK, <5% limit)
Daily Loss: -0.45% (OK, <-1.5% limit)
```

---

## 📊 CHARTS / GRAPHS

### Weekly Equity Curve (ASCII)
```
$11,300 |                    
$11,200 |              /  \  
$11,100 |            /      
$11,000 |          /        
$10,500 |        /          
$10,200 |      /            
$10,000 |____/_______________
        Mon Tue Wed Thu Fri
```

### Win Rate by Day
```
75% |
70% |        ■        ■
65% |    ■   ■   ■   ■
60% |
55% |                ■
50% |_________________
    Mon Tue Wed Thu Fri
```

---

## 🎓 LEARNINGS & NEXT WEEK

### This Week's Wins
✅ Baseline validated: 62% backtest ≈ 65% live (good match)
✅ SL working perfectly: 100% accuracy
✅ Time-of-day filter idea: 08-16 UTC = 68% win
✅ Strong start: +12% in one week

### This Week's Challenges
⚠️ RNDRUSDT underperforming: Only 48% win
⚠️ Thu drawdown: -2.1% (within limit, but monitor)
⚠️ Pair correlation: BTC/ETH high (reduce overlap?)

### Hypotheses for Next Week
1. **Time-of-day filter:** Trade only 08-16 UTC → should improve win%
2. **Pair selection:** Remove RND, FIL, SEI → focus top 15 pairs
3. **TP optimization:** Test 0.65% vs 0.70% → could increase PF
4. **Dynamic SL:** Try ATR×1.8 when vol<2%, 2.0 when vol>2%

---

## 📋 RECOMMENDATIONS FOR NEXT WEEK

### Level 1 (Auto-Deploy)
- [ ] Remove RNDRUSDT, FIL, SEI from trading (underperforming)
- [ ] Test time-of-day filter: 08-16 UTC only
- [ ] Continue TP 0.65% (baseline)

### Level 2 (Discuss with MASTER)
- [ ] TP test: 0.65% vs 0.70% vs 0.75% (propose backtest)
- [ ] Dynamic SL: Adjust ATR multiple based on volatility
- [ ] Correlation filter: Skip pairs >0.85 corr to BTCUSDT

### Level 3 (Strategic)
- [ ] Consider early live (Bybit) if win% reaches 65%+ by 2026-04-07?
- [ ] Or stay paper trading full 90 days (safer)?

---

## 📞 CHAT STATUS

| Chat | Status | Key Output |
|------|--------|-----------|
| CHAT 1 | ✅ Active | Backtest baseline confirmed, TP testing ready |
| CHAT 2 | ✅ Active | SL 100%, risk rules enforced, no incidents |
| CHAT 3 | ✅ Active | Pair ranking, time-of-day analysis ready |
| CHAT 4 | ✅ This report | Daily metrics tracked, weekly summary |
| MASTER | ✅ Decision hub | Authorized Level 1-2 changes, reviewing |

---

## ✅ CHECKLIST FOR NEXT FRIDAY

- [ ] CHAT 4: Daily metrics logged (every 21:00)
- [ ] CHAT 2: Risk compliance check (daily)
- [ ] CHAT 1: Backtest TP optimization (if requested)
- [ ] CHAT 3: Time-of-day / pair analysis (if requested)
- [ ] MASTER: Weekly decisions logged (Friday)
- [ ] Report: Next Friday 21:00 GMT+1

---

## 🎯 TARGET FOR NEXT WEEK

| Metric | This Week | Next Week Target | Stretch Goal |
|--------|-----------|-----------------|--------------|
| Win Rate | 65% | 64% (stable) | 66%+ |
| PF | 1.87 | >1.5 (maintain) | 2.0+ |
| PnL | +$1,234 | +$1,500+ | +$2,000+ |
| Drawdown | -2.1% | <3% | <2% |
| Trades | 67 | 70-80 | 100+ |

---

**Report Version:** 1.0
**Template Last Updated:** 2026-03-24
**Next Report:** 2026-03-31 21:00 GMT+1
**Owner:** CHAT 4 (Monitoring & Reporting)
**Approver:** MASTER (Robert)
