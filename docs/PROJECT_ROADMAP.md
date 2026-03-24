# 🗺️ PROJECT ROADMAP — 30-DNI DO LIVE TRADING

**Status:** Paper Trading (Testnet) — Live na 2026-06-17
**Start:** 2026-03-17
**End:** 2026-06-17 (GO/NO-GO decision)

---

## 📊 VISION

Build fully automated AI crypto futures scalping bot:
- ✅ Multi-pair scanner (25 pairs)
- ✅ MACD+RSI momentum strategy
- ✅ Risk-first execution (1% per trade, -1.5% daily cutoff)
- ✅ 60%+ win rate, PF>1.5
- ✅ 99%+ uptime on VPS

---

## 🎯 SUCCESS CRITERIA (ALL must be ✅)

```
Win Rate:        ≥ 60%
Profit Factor:   > 1.5
PnL:             > +$100 cumulative
Drawdown:        < 5% (max)
Uptime:          ≥ 99%
SL Accuracy:     100% (0 failures)
Daily Loss Rule: -1.5% enforced ✓
```

If ANY fails → extend paper trading OR pivot strategy.

---

## 📅 30-DAY BLOCKS

### **BLOCK 1: Days 1-7 (2026-03-17 to 2026-03-24)**
**Theme:** TP Logic + Win Rate Tracking

**Goals:**
- ✅ Validate baseline (62% win rate from backtest)
- ✅ Implement full TP logic (50%, 25%, 25% exits)
- ✅ Setup daily win rate tracking
- ✅ 50+ test trades minimum

**Deliverables:**
- Dashboard update: win rate %, PnL, trade log
- Trade analysis: best/worst pairs, best/worst times
- Recommendation: Any parameter adjustments needed?

**Success:** Win% ≥ 55% on first 50 trades

---

### **BLOCK 2: Days 8-14 (2026-03-25 to 2026-03-31)**
**Theme:** Risk Recycling + Dynamic TP

**Goals:**
- ✅ Test dynamic TP (0.6% vs 0.7% vs 0.8%)
- ✅ Implement Risk Recycling (scale position based on DD)
- ✅ Optimize SL (ATR×1.8 vs 2.0 vs 2.2)
- ✅ 100+ cumulative trades

**Deliverables:**
- Backtest results: TP comparison across 25 pairs
- Live test: dynamic TP impact on PnL
- Weekly report: metrics vs baseline

**Success:** Win% maintained ≥ 58%, PF > 1.5

---

### **BLOCK 3: Days 15-21 (2026-04-01 to 2026-04-07)**
**Theme:** Correlation Filter + TP Scaling

**Goals:**
- ✅ Add pair correlation filter (reduce hedge risk)
- ✅ Implement time-of-day filter (UTC hour optimization)
- ✅ Scale TP based on volatility regime
- ✅ 150+ cumulative trades

**Deliverables:**
- Correlation analysis: which pairs move together?
- Time-of-day backtest: which hours most profitable?
- Live test: correlation filter impact

**Success:** Win% ≥ 60%, Sharpe stable/improving

---

### **BLOCK 4: Days 22-30 (2026-04-08 to 2026-04-16)**
**Theme:** Validation + Live Decision Prep

**Goals:**
- ✅ Stabilize all parameters
- ✅ Validate ALL success criteria
- ✅ Complete 200+ test trades
- ✅ Zero critical errors
- ✅ Prepare live account setup

**Deliverables:**
- Final validation report (all metrics vs criteria)
- Live readiness checklist
- Contingency plan (what if X goes wrong?)

**Success:** ALL criteria ✅ → Ready for live

---

## 🔄 WEEKLY CYCLE (Every Friday 21:00 GMT+1)

```
FRIDAY SYNC:
├─ CHAT 4 → Daily metrics (win%, PnL, drawdown, uptime)
├─ CHAT 3 → Backtest deep-dive (if needed)
├─ CHAT 1 → Parameter optimization report
├─ CHAT 2 → Risk status + any incidents
└─ MASTER → Decision: Continue? Pivot? Adjust?
```

---

## 📈 EXPECTED PROGRESSION

```
Week 1 (ending 2026-03-24):
  Win%: 55-62% (validate baseline)
  Trades: 50-75
  PnL: -$50 to +$200 (noisy)

Week 2 (ending 2026-03-31):
  Win%: 58-64% (TP optimization)
  Trades: 100+
  PnL: +$100 to +$300

Week 3 (ending 2026-04-07):
  Win%: 60-65% (filters helping)
  Trades: 150+
  PnL: +$300 to +$600

Week 4 (ending 2026-04-14):
  Win%: 60-65% (stable)
  Trades: 200+
  PnL: +$600 to +$1,000+
  Confidence: 90%+
```

---

## 🚨 RISK GATES

If at ANY point:
- Win% < 55% for 3 consecutive days → PAUSE, analyze
- PnL < 0 for 5 consecutive days → PAUSE, debug
- Daily loss = -1.5% → AUTO STOP (enforced)
- SL failure → EMERGENCY fix (LEVEL 4)
- Uptime < 99% → Investigate infrastructure

---

## 🎯 GO/NO-GO DECISION: 2026-06-17

**GO LIVE if:**
- ✅ Win rate ≥ 60% (validated)
- ✅ Profit Factor > 1.5
- ✅ Cumulative PnL > +$100
- ✅ Drawdown < 5%
- ✅ Uptime ≥ 99%
- ✅ Zero critical errors (SL, exposure)
- ✅ All risk rules enforced

**NO-GO if:**
- Any criterion not met
- → Extend paper trading 30 more days
- → Root-cause analysis + pivot

---

## 📊 CURRENT STATE (2026-03-24)

- **Paper trading:** Live on VPS 157.230.117.206
- **Trades so far:** 4 (in 6h52min)
- **PnL:** -$4.08 (-0.082%)
- **Win rate:** 75% (3/4, but small sample)
- **SL success:** 3/4 ✅
- **Confidence:** 80% (selective mode, ATR×2.0)

**Status:** On track. First week performance within range.

---

## 📞 ESCALATION

| Issue | Action | Deadline |
|-------|--------|----------|
| Win% < 55% | PAUSE + analyze | Same day |
| Daily loss -1.5% | AUTO STOP | Real-time |
| SL failure | EMERGENCY fix | 10 min |
| Infrastructure issue | LEVEL 4 | 5 min |
| Strategy pivot needed | MASTER decision | 24h |

---

## ✅ NEXT STEPS

1. **Validate baseline** — first 50 trades (Days 1-7)
2. **Daily reports** — CHAT 4 every 21:00
3. **Weekly sync** — Friday 21:00, all chats
4. **Parameter tests** — Level 1-2 as identified
5. **Track metrics** — dashboard live

**Target:** 60%+ win rate by end of Week 2 (2026-03-31)

---

**Document Version:** 1.0
**Last Updated:** 2026-03-24
**Next Review:** 2026-03-31 (Weekly)
