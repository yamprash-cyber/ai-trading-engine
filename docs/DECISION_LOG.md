# 📋 DECISION LOG — Project Decisions & Outcomes

**Purpose:** Record every decision, rationale, and outcome. Archive of "why we did X".

**Format:**
```
DATE: YYYY-MM-DD
DECISION: [Clear 1-line summary]
CONTEXT: [What triggered the decision]
OPTIONS: [What we considered]
CHOSEN: [Which option + why]
APPROVED_BY: [Robert / CHAT1 / CHAT2 etc]
IMPLEMENTED: [What happened]
OUTCOME: [Results so far]
STATUS: [In Progress / Completed / Reversed]
NEXT_REVIEW: [When to check if this still works]
```

---

## 📝 ACTIVE DECISIONS

### Decision #1
**DATE:** 2026-03-15
**DECISION:** Start paper trading on Binance Testnet (not Bybit immediately)
**CONTEXT:** Wanted to validate bot before live capital. Testnet = free, no real money risk.
**OPTIONS:**
- A: Start live on Bybit with $1,000 → Risk real money now
- B: Paper trade Binance Testnet 3 months → Risk-free validation
- C: Backtest only, no live trading → No real data
**CHOSEN:** B (Paper trade Testnet)
**REASON:** Risk-first approach. Validate strategy with real market conditions before live capital.
**APPROVED_BY:** Robert (MASTER decision)
**IMPLEMENTED:** VPS deployed, bot trading since 2026-03-17
**OUTCOME:** 
- 4 trades in first 6h52min
- -$4.08 PnL (-0.082%) 
- 3/4 SL success ✅
- Win rate: 75% (but small sample)
**STATUS:** In Progress
**NEXT_REVIEW:** 2026-03-31 (end of Week 1)

---

### Decision #2
**DATE:** 2026-03-17
**DECISION:** Set ATR multiple = 2.0 for SL (vs 1.8 or 2.2)
**CONTEXT:** Risk Engine needed SL multiplier. Backtest showed 62% win rate at 2.0.
**OPTIONS:**
- A: ATR × 1.5 → Tight SL, more hits
- B: ATR × 1.8 → Medium SL
- C: ATR × 2.0 → Wider SL, fewer hits
- D: ATR × 2.2 → Very wide SL, risk too large
**CHOSEN:** C (ATR × 2.0)
**REASON:** Backtest baseline. Good balance: 62% win rate, manageable drawdown.
**APPROVED_BY:** Robert + CHAT 2 (Risk decision)
**IMPLEMENTED:** Bot deployed with SL = ATR × 2.0
**OUTCOME:** First trades: 3/4 SL triggered correctly ✅
**STATUS:** In Progress
**MONITORING:** Will test 1.8 in Week 2 if win rate drops
**NEXT_REVIEW:** 2026-03-31 (check if SL too wide/tight)

---

### Decision #3
**DATE:** 2026-03-17
**DECISION:** Daily loss cutoff = -1.5% (auto-stop trading)
**CONTEXT:** Risk rule needed. How much daily loss acceptable before stopping?
**OPTIONS:**
- A: -1% → Conservative, stops too often
- B: -1.5% → Balanced (original spec)
- C: -2% → Aggressive, allows more losses
**CHOSEN:** B (-1.5%)
**REASON:** Original spec. Protects capital while allowing recovery days.
**APPROVED_BY:** Robert + CHAT 2
**IMPLEMENTED:** Daily loss tracker in Risk Manager
**OUTCOME:** Not yet triggered (too early, few trades)
**STATUS:** In Progress
**IMMUTABLE:** Yes (risk rule, can't change without approval)
**NEXT_REVIEW:** Weekly check (CHAT 4 reports)

---

### Decision #4
**DATE:** 2026-03-24
**DECISION:** Setup hierarchical chat system (4 subordinate chats + MASTER)
**CONTEXT:** Main chat was overloaded. Needed structure for 90-day intensive project.
**OPTIONS:**
- A: Continue in single chat (chaos)
- B: Create 4 specialized chats (CHAT 1-4) + MASTER hierarchy
- C: Use separate Claude projects per topic
**CHOSEN:** B (4-chat hierarchy)
**REASON:** Clear separation of concerns. CHAT 1=backtest, CHAT 2=live ops, CHAT 3=history, CHAT 4=reporting.
**APPROVED_BY:** Robert (MASTER decision)
**IMPLEMENTED:** 5 instruction docs created + loaded into chats
**OUTCOME:** Structure ready, organizing workflow
**STATUS:** In Progress (just deployed)
**NEXT_REVIEW:** 2026-03-31 (check if hierarchy working)

---

### Decision #5
**DATE:** 2026-03-24
**DECISION:** GitHub as Single Source of Truth (sync PC/Mac/VPS)
**CONTEXT:** Working from PC + Mac + VPS. Needed central repo + auto-sync.
**OPTIONS:**
- A: Local sync (USB, manual copy) → Error-prone
- B: GitHub + Git sync (auto) → Professional
- C: Google Drive (not code-friendly)
**CHOSEN:** B (GitHub + Git)
**REASON:** Git is industry standard. Auto-sync keeps everything in sync. 4-hour cron on VPS.
**APPROVED_BY:** Robert
**IMPLEMENTED:** 
- Repo created: yamprash-cyber/ai-trading-engine
- PC cloned, pushed 5 docs
- VPS auto-pull every 4h
- Mac setup plan (execute wieczorem)
**OUTCOME:** Repo live, PC synced ✅
**STATUS:** In Progress (Mac setup pending)
**NEXT_REVIEW:** 2026-03-25 (after Mac setup)

---

## 🔄 DECISIONS PENDING

### Decision #P1
**TOPIC:** Which parameter to optimize first in Week 1?
**OPTIONS:**
- A: TP (0.5% vs 0.6% vs 0.7%) — affects winners
- B: SL multiple (1.8 vs 2.0 vs 2.2) — affects SL hits
- C: Volatility filter (skip low-vol pairs) — affects opportunities
**STATUS:** Awaiting CHAT 1 backtest results
**DECISION_DATE:** 2026-03-31
**OWNER:** MASTER (Robert)

---

### Decision #P2
**TOPIC:** When to test live (Bybit real account)?
**OPTIONS:**
- A: Immediately after Day 62 (2026-05-17) if criteria met
- B: Wait until Day 90 (2026-06-17) = full 3 months
- C: Extend paper trading to 6 months
**STATUS:** Pending daily performance data
**DECISION_DATE:** 2026-05-17 (halfway point)
**OWNER:** MASTER (Robert)

---

### Decision #P3
**TOPIC:** How many pairs to trade live?
**OPTIONS:**
- A: Start with 5 best pairs (lowest risk)
- B: Trade all 25 pairs (higher volume)
- C: Trade top 10 pairs (balanced)
**STATUS:** Pending pair-performance analysis (CHAT 3)
**DECISION_DATE:** 2026-06-10 (pre-live)
**OWNER:** MASTER + CHAT 1

---

## 📊 DECISION OUTCOMES (Past)

### Outcome #1: Block A (Cowork autonomous work)
**DECISION:** Give Cowork 20h solo to build 5 core modules
**DATE:** 2026-03-12
**RESULT:** ✅ Success
- 2000+ lines production code
- 5 modules complete (Market Scanner, Feature Engine, Strategy Engine, Risk Manager, Execution Engine)
- Integration tests passed (223 signals)
**LESSON:** Autonomous blocks work well if task is clear

---

### Outcome #2: Block B (Full backtest framework)
**DECISION:** Run full backtest vs 25 pairs, 2019-2024 data
**DATE:** 2026-03-14
**RESULT:** ✅ Success
- Backtest completed
- Baseline metrics: 62% win, 1.87 PF, 1.34 Sharpe, -4.2% DD
- Ready for paper trading
**LESSON:** 4.9GB dataset is manageable, backtest framework scales

---

### Outcome #3: Claude 20h autonomous work
**DECISION:** Claude (me) spends 20h on dashboard + demo automation
**DATE:** 2026-03-15
**RESULT:** ✅ Success
- Dashboard: Live trade tracking, PnL, win rate, Sharpe
- Orchestrator: Auto-manage demo account
- Logger: Trade history
- Docs: Setup guides
**LESSON:** AI collaboration works. Clear tasks = quality output

---

## 🎯 LESSONS LEARNED

1. **Risk-first approach works:** SL validation + daily cutoff working as designed
2. **Backtest ≠ live:** 62% backtest vs 75% early live (but 4 trades = noise)
3. **Hierarchy reduces chaos:** 4 chats > 1 overloaded chat
4. **GitHub sync essential:** Multi-machine work needs central repo
5. **Autonomous blocks scale:** Cowork + Claude can work in parallel

---

## 🚨 RISKS & MITIGATIONS

| Risk | Mitigation | Owner |
|------|-----------|-------|
| Win% drops <55% | Auto-pause, analyze pairs | CHAT 1 |
| SL fails | Manual close, emergency fix | CHAT 2 |
| Drawdown >5% | Reduce position size | CHAT 2 |
| VPS downtime | Monitoring + restart | CHAT 2 |
| Strategy drift | Weekly backtest validation | CHAT 1 |
| Data quality | Verify OHLC candles daily | CHAT 3 |

---

## 📅 DECISION REVIEW SCHEDULE

**Weekly:** Every Friday 21:00 GMT+1
- CHAT 4: Report metrics (win%, PnL, DD, uptime)
- CHAT 1-3: Quick status
- MASTER: Any pivots needed?

**Checkpoints:**
- 2026-03-31: End Week 1 (Decision review #1)
- 2026-04-14: End Week 3 (Decision review #2 — mid-point)
- 2026-05-17: Day 62 (Halfway — major decision point)
- 2026-06-10: Pre-live (Final decisions)
- 2026-06-17: GO/NO-GO decision

---

**Document Version:** 1.0
**Last Updated:** 2026-03-24
**Maintained by:** MASTER CHAT (Robert)
**Reviewed:** Weekly (every Friday)
