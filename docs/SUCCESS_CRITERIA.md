# ✅ SUCCESS CRITERIA — GO/NO-GO DECISION

**Decision Date:** 2026-06-17
**Trading Period:** 2026-03-17 to 2026-06-17 (3 months, ~90 days)
**Target Trades:** 300+ for statistical significance

---

## 🎯 PRIMARY CRITERIA (ALL must be ✅)

### **Criterion 1: Win Rate ≥ 60%**

**Definition:** (Winning trades / Total trades) × 100 ≥ 60%

**Why:** Strategy must win more than it loses to be profitable long-term.

**Measurement:**
- Count: Trades with PnL > 0 (winners)
- Denominator: Total trades executed
- Sample size: Minimum 300 trades for statistical confidence

**Acceptable Range:** 60% - 75%
- 60%+: GO ✅
- 55-59%: MARGINAL (review, possibly extend)
- <55%: NO-GO ❌

**Validation Method:**
- Weekly reports: CHAT 4 calculates daily
- Trend analysis: 7-day rolling average
- Per-pair breakdown: Ensure not skewed by 1-2 pairs

---

### **Criterion 2: Profit Factor > 1.5**

**Definition:** Gross profit / Gross loss > 1.5

**Why:** Even at 55% win rate, PF tells us if winners are bigger than losers.

**Measurement:**
- Gross profit: Sum of all winning trades
- Gross loss: Sum of all losing trades (absolute value)
- Ratio: Profit / Loss

**Example:**
```
Gross profit:  $1,500 (from 165 winners)
Gross loss:    $900 (from 135 losers)
PF = 1,500 / 900 = 1.67 ✅
```

**Acceptable Range:** 1.5 - 3.0
- >1.5: GO ✅
- 1.3-1.5: MARGINAL (review TP settings)
- <1.3: NO-GO ❌

**Validation Method:**
- Trade log: Every trade logged with entry/exit/PnL
- Weekly aggregation: CHAT 4 calculates
- Per-pair: Identify if some pairs pulling down ratio

---

### **Criterion 3: Cumulative PnL > +$100**

**Definition:** Total P&L (wins - losses) > $100 USD

**Why:** Must be profitable in absolute terms, not just win rate.

**Measurement:**
- Account balance start: $10,000
- Account balance end (2026-06-17): $10,100+
- Or: Cumulative trades P&L > +$100

**Acceptable Range:** +$100 to +$5,000+
- >+$100: GO ✅
- $0 to +$100: MARGINAL (barely profitable)
- <$0: NO-GO ❌

**Validation Method:**
- Live account statement
- CHAT 4 daily aggregation
- Trade log: Sum of all PnL

---

### **Criterion 4: Max Drawdown < 5%**

**Definition:** Largest peak-to-trough decline < 5% of starting capital

**Why:** Risk management. Can't tolerate large drawdowns even if profitable.

**Measurement:**
- Peak: Highest equity reached
- Trough: Lowest equity after peak
- Drawdown %: (Trough - Peak) / Peak × 100

**Example:**
```
Peak equity: $10,500
Trough: $10,200
DD = (10,200 - 10,500) / 10,500 = -2.86% ✅
```

**Acceptable Range:** -0.5% to -5%
- <-5%: NO-GO ❌
- -2% to -5%: GO (acceptable risk)
- <-2%: EXCELLENT ✅

**Validation Method:**
- Daily equity tracking: CHAT 4
- Real-time monitoring: Dashboard
- Weekly report: Max DD by week

---

### **Criterion 5: Uptime ≥ 99%**

**Definition:** Bot running / Total time × 100 ≥ 99%

**Why:** Bot must be reliable. 99% = 21.6 hours/day average (acceptable downtime: 14.4 min/day)

**Measurement:**
- Running time: Process alive + trading
- Down time: Crashes, manual stops, infrastructure issues
- % Uptime: (Running / Total) × 100

**Acceptable Range:** 99% - 100%
- ≥99%: GO ✅
- 95-99%: MARGINAL (investigate crashes)
- <95%: NO-GO ❌

**Validation Method:**
- VPS monitoring: systemd service logs
- CHAT 2: Daily uptime check
- CHAT 4: Report in weekly summary

---

### **Criterion 6: SL Accuracy = 100%**

**Definition:** All trades have SL placed at order creation. SL triggered when hit.

**Why:** Non-negotiable. SL failure = uncontrolled loss.

**Measurement:**
- Check every trade log:
  - SL order placed same time as entry? ✅
  - SL triggered when price hit? ✅
  - No manual overrides? ✅

**Acceptable Range:** 100% (no tolerance)
- 100%: GO ✅
- 99.5-99.9%: MARGINAL (1 miss in 200 trades = investigate)
- <99%: NO-GO ❌

**Validation Method:**
- Trade log audit: CHAT 2 weekly
- Order history: Check Bybit API
- Real-time monitoring: SL placement at entry

---

### **Criterion 7: Risk Rules Enforced ✅**

**Definition:** All risk rules followed without exception:
1. Every trade ≤ 1% risk
2. Exposure never > 5%
3. Daily loss cutoff -1.5% enforced
4. ATR-based SL (not fixed %)

**Why:** Risk management is the foundation.

**Measurement:**
- Position sizing: Check each trade (1% of capital)
- Exposure: Sum open positions < 5%
- Daily P&L: Stop at -1.5% (auto-enforced)
- SL distance: Verify ATR × multiplier

**Acceptable Range:** 100% compliance (no exceptions)
- 100%: GO ✅
- 99.5-99.9%: MARGINAL (1 miss = investigate)
- <99%: NO-GO ❌

**Validation Method:**
- CHAT 2 daily: Risk rule audit
- Trade log: Position size check
- Dashboard: Exposure real-time

---

## 🚨 SECONDARY CRITERIA (helpful, not mandatory)

### **Sharpe Ratio > 1.0**
- Measures risk-adjusted returns
- >1.0: Good, 1.5+: Excellent
- If <1.0 but other criteria met: Still GO (but monitor)

### **Consistency (Win% daily)**
- 7-day rolling average should be ≥58%
- If trending down: Investigate
- If stable: Confidence high

### **Per-Pair Performance**
- No pair should have <45% win rate (outlier)
- If one pair problematic: Consider removing
- Best 10 pairs should drive 70%+ of PnL

---

## 📊 DECISION MATRIX

```
Criterion               Target    Acceptable   NO-GO
────────────────────────────────────────────────────
Win Rate               ≥60%      58-59%       <55%
Profit Factor          >1.5      1.3-1.5      <1.3
PnL                    >+$100    $0-$100      <$0
Max Drawdown           <5%       <5% OK       >5%
Uptime                 ≥99%      95-99%       <95%
SL Accuracy            100%      99%+         <99%
Risk Rules Enforced    100%      100%         <100%
────────────────────────────────────────────────────

GO LIVE IF:
✅ Win Rate ≥ 60%
✅ PF > 1.5
✅ PnL > +$100
✅ Drawdown < 5%
✅ Uptime ≥ 99%
✅ SL 100%
✅ Risk rules 100%

NO-GO IF:
❌ Any PRIMARY criterion fails
```

---

## 🎯 CONTINGENCY PLANS

### **If Win% < 55% on 2026-05-17 (halfway point):**
1. PAUSE trading (go SL-only mode)
2. Analyze: Which pairs failing? Which times?
3. Root cause: Strategy issue? Market regime change?
4. Fix: Adjust parameters (TP, SL, filters)
5. Resume: Test for 7 days before deciding

### **If PF dropping (trending <1.5):**
1. Check: Are winners shrinking or losers growing?
2. If winners small: Increase TP (test 0.7% vs 0.8%)
3. If losers large: Tighten SL (test ATR×1.8)
4. Backtest: Verify change improves historical PF

### **If Drawdown > 3%:**
1. Reduce position size (0.8% per trade instead of 1%)
2. Tighten daily cutoff to -1% (from -1.5%)
3. Increase SL buffer (ATR×2.2 vs 2.0)
4. Monitor for 7 days, then decide

### **If Uptime < 99%:**
1. Check: Crashes? Network? VPS issues?
2. CHAT 2: Debug + restart bot
3. If persistent: Migrate to new VPS
4. Add monitoring: Slack alerts on down

### **If SL fails (even once):**
1. EMERGENCY: Manual fix (close position)
2. Root cause analysis (within 1h)
3. Code review: Why didn't SL trigger?
4. Restart bot with fix
5. CHAT 2: Post-mortem report to MASTER

---

## 📅 CHECKPOINT REVIEWS

| Date | Milestone | Action |
|------|-----------|--------|
| 2026-03-31 | Week 1 complete | Review baseline, adjust if needed |
| 2026-04-14 | Week 3 complete | Mid-point evaluation, major pivots allowed |
| 2026-05-17 | Day 62 (halfway) | MUST show ≥55% win%, decide continue or extend |
| 2026-06-10 | Week 12 almost done | Final validation, prepare for GO/NO-GO |
| 2026-06-17 | DECISION DAY | All criteria measured, GO LIVE or EXTEND |

---

## 💰 FINANCIAL IMPACT (if GO LIVE)

```
Paper Trading: $10,000 test account
Live Trading: $1,000-$10,000 (decide after success)

Monthly Expected Return (60% win rate):
$1,000 → ~$100-200/month (10-20%)
$10,000 → ~$1,000-2,000/month (10-20%)

Annual (if consistent 60% win, 1.87 PF):
$10,000 → ~$96,000 (900% return) — OPTIMISTIC
Realistic: $10,000 → ~$20,000-40,000/year (100-300%)
```

---

## ✅ FINAL GO/NO-GO CHECKLIST (2026-06-17)

- [ ] Win Rate ≥ 60%? (CHAT 4 report)
- [ ] PF > 1.5? (CHAT 1 confirms)
- [ ] PnL > +$100? (Account balance)
- [ ] Drawdown < 5%? (Dashboard)
- [ ] Uptime ≥ 99%? (Logs)
- [ ] SL 100%? (Trade audit)
- [ ] Risk rules 100%? (Compliance check)
- [ ] Zero critical errors? (Incident log)
- [ ] All 200+ trades analyzed? (CHAT 3 deep-dive)
- [ ] Live account ready? (CHAT 2 infrastructure)

If ALL ✅ → **GO LIVE**
If ANY ❌ → **EXTEND PAPER TRADING**

---

**Document Version:** 1.0
**Last Updated:** 2026-03-24
**Reviewed by:** MASTER CHAT (Robert)
**Next Review:** 2026-03-31
