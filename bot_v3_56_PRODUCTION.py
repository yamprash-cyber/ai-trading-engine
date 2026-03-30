"""
+======================================================================+
|   FAST CAPITALIZATION SNIPER V3.56 PRODUCTION — DUAL-LOOP            |
|   Bybit V5 Mainnet | MACD(12,26,9) + RSI(14) + ATR(14)              |
|   LOOP1: market scanner (15s) | LOOP2: position monitor (2s)         |
|   50 pairs | 1m klines | Partial close TP | Trailing SL              |
+======================================================================+

ARCHITECTURE:
  LOOP1 — market_scanner_loop() every 15s
    Scans 50 pairs, MACD+RSI on 1min candles, max 3 positions
  LOOP2 — position_monitor_loop() every 2s
    Only runs when len(open_positions) > 0
    Handles TP1/TP2 partial closes and trailing SL

AFTER FILL:
  set_position_sl() via /v5/position/trading-stop — SL=ATR×1.5
  ONE call, ONLY stopLoss, TP via partial close instead
  TP is handled by partial market close in LOOP2

LOOP2 STAGES:
  stage 0: watching for TP1
  stage 1: TP1 hit (50% closed), SL moved to breakeven
  stage 2: TP2 hit (40% closed), trailing SL active

RISK:
  1% capital/trade, max 3 positions, max 5% exposure
  Daily cutoff -1.5% stops LOOP1 (LOOP2 continues)
"""

import os
import sys
import time
import json
import hmac
import hashlib
import logging
import sqlite3
import urllib.parse
import math
import threading
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional

import requests
import numpy as np
from dotenv import load_dotenv

load_dotenv("/home/bot/.env")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONFIG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

API_KEY    = os.environ["BYBIT_API_KEY"]
API_SECRET = os.environ["BYBIT_API_SECRET"]
BASE_URL   = os.environ.get("BYBIT_BASE_URL", "https://api.bybit.com")
CATEGORY   = "linear"
INTERVAL   = "1"
KLINE_LIMIT = 200

# ── Top 50 pairs ───────────────────────────────────────────────
PAIRS = [
    "BTCUSDT",   "ETHUSDT",   "SOLUSDT",   "BNBUSDT",   "XRPUSDT",
    "ADAUSDT",   "DOGEUSDT",  "AVAXUSDT",  "LINKUSDT",  "MATICUSDT",
    "LTCUSDT",   "TRXUSDT",   "AAVEUSDT",  "UNIUSDT",   "SUSHIUSDT",
    "OPUSDT",    "ARBUSDT",   "GMXUSDT",   "MAGICUSDT", "DYDXUSDT",
    "SUIUSDT",   "MANAUSDT",  "SANDUSDT",  "AXSUSDT",   "ENJUSDT",
    "CHZUSDT",   "ENAUSDT",   "GALAUSDT",  "FLOWUSDT",  "IMXUSDT",
    "LRCUSDT",   "GMTUSDT",   "MASKUSDT",  "ALICEUSDT", "ANKRUSDT",
    "ANTUSDT",   "APEUSDT",   "APTUSDT",   "ARKUSDT",   "DOTUSDT",
    "ATOMUSDT",  "NEARUSDT",  "FTMUSDT",   "INJUSDT",   "LDOUSDT",
    "WLDUSDT",   "SEIUSDT",   "TIAUSDT",   "JUPUSDT",   "PYTHUSDT",
]

# ── Qty step per pair (fallback) ──────────────────────────────
STEP_MAP = {
    "BTCUSDT":   0.001, "ETHUSDT":  0.01,  "SOLUSDT":   0.1,
    "BNBUSDT":   0.01,  "XRPUSDT":  1.0,   "ADAUSDT":   1.0,
    "DOGEUSDT":  1.0,   "AVAXUSDT": 0.1,   "LINKUSDT":  0.1,
    "MATICUSDT": 1.0,   "LTCUSDT":  0.01,  "TRXUSDT":   1.0,
    "AAVEUSDT":  0.01,  "UNIUSDT":  0.1,   "SUSHIUSDT": 0.1,
    "OPUSDT":    0.1,   "ARBUSDT":  1.0,   "GMXUSDT":   0.01,
    "MAGICUSDT": 1.0,   "DYDXUSDT": 0.1,   "SUIUSDT":   1.0,
    "MANAUSDT":  1.0,   "SANDUSDT": 1.0,   "AXSUSDT":   0.1,
    "ENJUSDT":   1.0,   "CHZUSDT":  1.0,   "ENAUSDT":   1.0,
    "GALAUSDT":  10.0,  "FLOWUSDT": 0.1,   "IMXUSDT":   0.1,
    "LRCUSDT":   1.0,   "GMTUSDT":  1.0,   "MASKUSDT":  0.1,
    "ALICEUSDT": 0.1,   "ANKRUSDT": 10.0,  "ANTUSDT":   0.1,
    "APEUSDT":   0.1,   "APTUSDT":  0.1,   "ARKUSDT":   0.1,
    "DOTUSDT":   0.1,   "ATOMUSDT": 0.1,   "NEARUSDT":  0.1,
    "FTMUSDT":   1.0,   "INJUSDT":  0.01,  "LDOUSDT":   0.1,
    "WLDUSDT":   0.1,   "SEIUSDT":  1.0,   "TIAUSDT":   0.1,
    "JUPUSDT":   1.0,   "PYTHUSDT": 1.0,
}

# ── Risk params ────────────────────────────────────────────────
ATR_SL_MULT         = 1.5
TP1_PCT             = 0.004     # +0.4%
TP2_PCT             = 0.008     # +0.8%
TP1_CLOSE_FRAC      = 0.50      # close 50% at TP1
TP2_CLOSE_FRAC      = 0.40      # close 40% at TP2
TRAIL_ATR_MULT      = 0.5       # trailing SL = price - ATR*0.5
MIN_NOTIONAL_USD    = 5.0
VOL_FLOOR_PCT       = 0.003

# ── Risk guards ────────────────────────────────────────────────
DAILY_LOSS_CUTOFF   = -0.015
MAX_POSITIONS       = 3
MAX_EXPOSURE_PCT    = 0.05
RISK_PER_TRADE      = 0.01

# ── Dynamic risk scaling ──────────────────────────────────────
RISK_TIER_1_PCT     = 0.010
RISK_TIER_2_PCT     = 0.005
RISK_TIER_3_PCT     = 0.0025

# ── Operational params ────────────────────────────────────────
SCAN_INTERVAL_S     = 10
MONITOR_INTERVAL_S  = 2
MAX_RETRIES         = 3
RETRY_DELAY_S       = 2
FILL_POLL_INTERVAL  = 0.5
FILL_POLL_TIMEOUT   = 20
FILL_MAX_CHECKS     = int(FILL_POLL_TIMEOUT / FILL_POLL_INTERVAL)

# ── Paths ─────────────────────────────────────────────────────
DB_PATH  = os.environ.get("BOT_DB_PATH",  "/home/bot/trades_v3_56.db")
LOG_PATH = os.environ.get("BOT_LOG_PATH", "/home/bot/bot_v3_56.log")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LOGGING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def setup_logging() -> logging.Logger:
    fmt = "%(asctime)s  %(levelname)-8s  %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    handlers = [logging.StreamHandler(sys.stdout)]
    try:
        handlers.append(logging.FileHandler(LOG_PATH))
    except Exception as e:
        print(f"[WARN] Cannot open log file {LOG_PATH}: {e}")
    logging.basicConfig(level=logging.INFO, format=fmt, datefmt=datefmt,
                        handlers=handlers)
    return logging.getLogger("sniper356")

log = setup_logging()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SQLITE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_db_lock = threading.Lock()

def setup_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            pair          TEXT    NOT NULL,
            side          TEXT    NOT NULL,
            qty           REAL    NOT NULL,
            entry_price   REAL    NOT NULL,
            entry_time    TEXT    NOT NULL,
            sl_price      REAL    NOT NULL,
            atr           REAL    NOT NULL DEFAULT 0,
            order_id      TEXT,
            stage         INTEGER DEFAULT 0,
            status        TEXT    DEFAULT 'ACTIVE',
            pnl           REAL    DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS risk_log (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            ts       TEXT    NOT NULL,
            event    TEXT    NOT NULL,
            balance  REAL,
            details  TEXT
        )
    """)
    conn.commit()

    existing = {row[1] for row in conn.execute("PRAGMA table_info(trades)")}
    for col, definition in [
        ("atr",   "REAL DEFAULT 0"),
        ("stage", "INTEGER DEFAULT 0"),
    ]:
        if col not in existing:
            conn.execute(f"ALTER TABLE trades ADD COLUMN {col} {definition}")
            log.info(f"[DB] Migrated: added column '{col}' to trades")
    conn.commit()
    return conn


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PRECISION HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _floor_to_step(value: float, step: float) -> float:
    if step <= 0:
        return value
    return math.floor(value / step) * step

def _round_to_tick(price: float, tick: float) -> float:
    if tick <= 0:
        return price
    return round(round(price / tick) * tick, 10)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# IN-MEMORY POSITION TRACKING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class OpenPosition:
    symbol: str
    side: str           # "LONG" or "SHORT"
    entry_price: float
    qty: float          # original total qty
    remaining_qty: float
    atr: float
    sl_price: float
    stage: int = 0      # 0=watching, 1=TP1 hit, 2=TP2 hit (trailing)
    db_id: int = 0

open_positions: dict[str, OpenPosition] = {}
positions_lock = threading.Lock()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BYBIT V5 CLIENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class BybitClient:
    RECV_WINDOW = "5000"

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})
        self._instruments: dict[str, dict] = {}

    def _ts(self) -> str:
        return str(int(time.time() * 1000))

    def _sign(self, ts: str, payload_str: str) -> str:
        raw = f"{ts}{API_KEY}{self.RECV_WINDOW}{payload_str}"
        return hmac.new(
            API_SECRET.encode("utf-8"),
            raw.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _auth_headers(self, ts: str, sig: str) -> dict:
        return {
            "X-BAPI-API-KEY":     API_KEY,
            "X-BAPI-TIMESTAMP":   ts,
            "X-BAPI-RECV-WINDOW": self.RECV_WINDOW,
            "X-BAPI-SIGN":        sig,
        }

    def _get(self, path: str, params: dict) -> dict:
        qs = urllib.parse.urlencode(params)
        ts = self._ts()
        sig = self._sign(ts, qs)
        url = f"{BASE_URL}{path}"
        r = self._session.get(
            url, params=params,
            headers=self._auth_headers(ts, sig),
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        if data.get("retCode") != 0:
            raise RuntimeError(f"GET {path} retCode={data['retCode']}: {data['retMsg']}")
        return data["result"]

    def _post(self, path: str, body: dict) -> dict:
        body_str = json.dumps(body, separators=(",", ":"))
        ts = self._ts()
        sig = self._sign(ts, body_str)
        url = f"{BASE_URL}{path}"
        r = self._session.post(
            url, data=body_str,
            headers=self._auth_headers(ts, sig),
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        if data.get("retCode") != 0:
            raise RuntimeError(f"POST {path} retCode={data['retCode']}: {data['retMsg']}")
        return data["result"]

    # ── Market data ────────────────────────────────────────────

    def get_klines(self, symbol: str, interval: str = INTERVAL,
                   limit: int = KLINE_LIMIT) -> list:
        result = self._get("/v5/market/kline", {
            "category": CATEGORY, "symbol": symbol,
            "interval": interval, "limit": limit,
        })
        return list(reversed(result.get("list", [])))

    def get_instrument_info(self, symbol: str) -> dict:
        if symbol not in self._instruments:
            try:
                result = self._get("/v5/market/instruments-info", {
                    "category": CATEGORY, "symbol": symbol,
                })
                items = result.get("list", [])
                if not items:
                    raise ValueError(f"{symbol} not found")
                info = items[0]
                lot_f  = info.get("lotSizeFilter", {})
                price_f = info.get("priceFilter", {})
                self._instruments[symbol] = {
                    "qty_step":   float(lot_f.get("qtyStep", "0.01")),
                    "min_qty":    float(lot_f.get("minOrderQty", "0.01")),
                    "price_tick": float(price_f.get("tickSize", "0.01")),
                }
            except Exception:
                step = STEP_MAP.get(symbol, 0.01)
                self._instruments[symbol] = {
                    "qty_step": step, "min_qty": step, "price_tick": 0.01,
                }
        return self._instruments[symbol]

    def get_ticker_price(self, symbol: str) -> float:
        result = self._get("/v5/market/tickers", {
            "category": CATEGORY, "symbol": symbol,
        })
        items = result.get("list", [])
        if not items:
            raise RuntimeError(f"No ticker for {symbol}")
        return float(items[0].get("lastPrice", 0))

    def get_all_tickers(self) -> dict[str, float]:
        """Batch call: GET /v5/market/tickers?category=linear — all pairs at once."""
        result = self._get("/v5/market/tickers", {"category": CATEGORY})
        tickers = {}
        for item in result.get("list", []):
            sym = item.get("symbol", "")
            price = float(item.get("lastPrice", 0))
            if sym and price > 0:
                tickers[sym] = price
        return tickers

    # ── Account ────────────────────────────────────────────────

    def get_wallet_balance(self) -> float:
        result = self._get("/v5/account/wallet-balance", {
            "accountType": "UNIFIED",
        })
        accounts = result.get("list", [])
        if not accounts:
            raise RuntimeError("No wallet data returned")
        return float(accounts[0].get("totalEquity", 0))

    def get_positions(self) -> list:
        result = self._get("/v5/position/list", {
            "category": CATEGORY, "settleCoin": "USDT",
        })
        return [p for p in result.get("list", [])
                if float(p.get("size", 0)) > 0]

    # ── Orders ─────────────────────────────────────────────────

    def place_market_order(self, symbol: str, side: str, qty: float) -> dict:
        info = self.get_instrument_info(symbol)
        qty = _floor_to_step(qty, info["qty_step"])
        body = {
            "category":    CATEGORY,
            "symbol":      symbol,
            "side":        side,
            "orderType":   "Market",
            "qty":         str(qty),
            "timeInForce": "GTC",
            "positionIdx": 0,
        }
        return self._post("/v5/order/create", body)

    def place_limit_order(self, symbol: str, side: str, qty: float,
                          price: float) -> dict:
        info = self.get_instrument_info(symbol)
        qty   = _floor_to_step(qty, info["qty_step"])
        price = _round_to_tick(price, info["price_tick"])
        body = {
            "category":    CATEGORY,
            "symbol":      symbol,
            "side":        side,
            "orderType":   "Limit",
            "qty":         str(qty),
            "price":       str(price),
            "timeInForce": "GTC",
            "positionIdx": 0,
        }
        return self._post("/v5/order/create", body)

    def get_order_status(self, symbol: str, order_id: str) -> dict:
        result = self._get("/v5/order/realtime", {
            "category": CATEGORY, "symbol": symbol, "orderId": order_id,
        })
        orders = result.get("list", [])
        return orders[0] if orders else {}

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # POSITION-LEVEL SL via /v5/position/trading-stop
    # ONLY stopLoss — TP handled by partial market close
    # TP is handled by partial market close in LOOP2
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def set_position_sl(self, symbol: str, sl_price: float) -> dict:
        """
        Set SL ONLY via /v5/position/trading-stop.
        ONE call, ONLY stopLoss field. TP via partial close.
        """
        info = self.get_instrument_info(symbol)
        sl_price = _round_to_tick(sl_price, info["price_tick"])
        body = {
            "category":    CATEGORY,
            "symbol":      symbol,
            "positionIdx": 0,
            "stopLoss":    str(sl_price),
            "slTriggerBy": "LastPrice",
        }
        result = self._post("/v5/position/trading-stop", body)
        log.info(f"[SL] {symbol} SL=${sl_price} via trading-stop")
        return result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# INDICATORS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _ema(data: np.ndarray, period: int) -> np.ndarray:
    alpha = 2.0 / (period + 1)
    result = np.empty_like(data)
    result[0] = data[0]
    for i in range(1, len(data)):
        result[i] = alpha * data[i] + (1 - alpha) * result[i - 1]
    return result

def calc_macd(closes: np.ndarray, fast=12, slow=26, signal=9):
    ema_fast    = _ema(closes, fast)
    ema_slow    = _ema(closes, slow)
    macd_line   = ema_fast - ema_slow
    signal_line = _ema(macd_line, signal)
    histogram   = macd_line - signal_line
    return macd_line, signal_line, histogram

def calc_rsi(closes: np.ndarray, period=14) -> np.ndarray:
    deltas = np.diff(closes)
    gains  = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)
    avg_gain = np.empty(len(deltas))
    avg_loss = np.empty(len(deltas))
    avg_gain[0] = np.mean(gains[:period]) if period <= len(gains) else 0.0
    avg_loss[0] = np.mean(losses[:period]) if period <= len(losses) else 0.0
    for i in range(1, len(deltas)):
        avg_gain[i] = (avg_gain[i-1] * (period - 1) + gains[i]) / period
        avg_loss[i] = (avg_loss[i-1] * (period - 1) + losses[i]) / period
    rs  = np.where(avg_loss > 0, avg_gain / avg_loss, 100.0)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    full_rsi = np.empty(len(closes))
    full_rsi[0] = 50.0
    full_rsi[1:] = rsi
    return full_rsi

def calc_atr(highs: np.ndarray, lows: np.ndarray, closes: np.ndarray,
             period=14) -> np.ndarray:
    tr = np.empty(len(closes))
    tr[0] = highs[0] - lows[0]
    for i in range(1, len(closes)):
        hl = highs[i] - lows[i]
        hc = abs(highs[i] - closes[i-1])
        lc = abs(lows[i] - closes[i-1])
        tr[i] = max(hl, hc, lc)
    atr = np.empty(len(closes))
    atr[:period] = np.mean(tr[:period])
    for i in range(period, len(closes)):
        atr[i] = (atr[i-1] * (period - 1) + tr[i]) / period
    return atr


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SIGNAL DETECTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class Signal:
    symbol:     str
    side:       str
    price:      float
    atr:        float
    atr_pct:    float
    rsi:        float
    macd_val:   float
    signal_val: float

def detect_signal(symbol: str, klines: list) -> Optional[Signal]:
    if len(klines) < KLINE_LIMIT - 10:
        return None
    closes = np.array([float(k[4]) for k in klines])
    highs  = np.array([float(k[2]) for k in klines])
    lows   = np.array([float(k[3]) for k in klines])

    macd_line, signal_line, hist = calc_macd(closes)
    rsi = calc_rsi(closes)
    atr = calc_atr(highs, lows, closes)

    price     = closes[-1]
    atr_val   = atr[-1]
    atr_pct   = (atr_val / price) * 100 if price > 0 else 0
    rsi_val   = rsi[-1]
    macd_val  = macd_line[-1]
    sig_val   = signal_line[-1]
    hist_val  = hist[-1]
    hist_prev = hist[-2] if len(hist) > 1 else 0

    # LONG: MACD > Signal AND RSI > 50 AND histogram turning positive
    if macd_val > sig_val and rsi_val > 50 and hist_val > 0 and hist_prev <= 0:
        return Signal(symbol, "LONG", price, atr_val, atr_pct, rsi_val, macd_val, sig_val)
    # SHORT: MACD < Signal AND RSI < 50 AND histogram turning negative
    if macd_val < sig_val and rsi_val < 50 and hist_val < 0 and hist_prev >= 0:
        return Signal(symbol, "SHORT", price, atr_val, atr_pct, rsi_val, macd_val, sig_val)
    return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RISK MANAGER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class RiskManager:
    def __init__(self):
        self._start_balance: Optional[float] = None

    def set_start_balance(self, balance: float):
        if self._start_balance is None:
            self._start_balance = balance

    def daily_pnl(self, current_balance: float) -> float:
        if self._start_balance is None or self._start_balance == 0:
            return 0.0
        return (current_balance - self._start_balance) / self._start_balance

    def get_risk_pct(self, daily_pnl_pct: float) -> float:
        if daily_pnl_pct >= 0.04:
            return RISK_TIER_3_PCT
        elif daily_pnl_pct >= 0.02:
            return RISK_TIER_2_PCT
        return RISK_TIER_1_PCT

    def calc_position_size(self, balance: float, price: float,
                           sl_price: float, daily_pnl_pct: float) -> float:
        risk_pct = self.get_risk_pct(daily_pnl_pct)
        risk_amount = balance * risk_pct
        sl_distance = abs(price - sl_price)
        if sl_distance <= 0:
            return 0.0
        qty = risk_amount / sl_distance
        max_notional = balance * MAX_EXPOSURE_PCT
        max_qty = max_notional / price if price > 0 else 0
        return min(qty, max_qty)

    def can_open(self, current_balance: float,
                 open_count: int) -> tuple[bool, str]:
        if open_count >= MAX_POSITIONS:
            return False, f"max positions ({MAX_POSITIONS})"
        dpnl = self.daily_pnl(current_balance)
        if dpnl <= DAILY_LOSS_CUTOFF:
            return False, f"daily loss cutoff ({dpnl:.2%})"
        return True, "OK"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TRADING ENGINE — DUAL-LOOP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TradingEngine:
    def __init__(self):
        self.client = BybitClient()
        self.db     = setup_db()
        self.risk   = RiskManager()
        self._running = True
        self._load_open_positions()

    def _load_open_positions(self):
        """Restore open_positions from DB on startup."""
        rows = self.db.execute(
            "SELECT id, pair, side, qty, entry_price, sl_price, atr, stage "
            "FROM trades WHERE status='ACTIVE'"
        ).fetchall()
        with positions_lock:
            for row in rows:
                db_id, pair, side, qty, entry, sl, atr_val, stage = row
                # Get current position size from exchange
                remaining = qty
                try:
                    positions = self.client.get_positions()
                    for p in positions:
                        if p.get("symbol") == pair:
                            remaining = float(p.get("size", qty))
                            break
                except Exception:
                    pass
                open_positions[pair] = OpenPosition(
                    symbol=pair, side=side, entry_price=entry,
                    qty=qty, remaining_qty=remaining,
                    atr=atr_val, sl_price=sl,
                    stage=stage or 0, db_id=db_id,
                )
        log.info(f"[STARTUP] Restored {len(open_positions)} open positions from DB")

    # ── Poll for entry fill ────────────────────────────────────

    def _poll_for_fill(self, symbol: str, order_id: str,
                       expected_price: float) -> tuple[bool, float, str]:
        for check in range(1, FILL_MAX_CHECKS + 1):
            time.sleep(FILL_POLL_INTERVAL)
            try:
                order = self.client.get_order_status(symbol, order_id)
                status = order.get("orderStatus", "")
                if status == "Filled":
                    fill_price = float(order.get("avgPrice", expected_price))
                    log.info(f"[FILL] {symbol} filled @ ${fill_price:.4f} (check #{check})")
                    return True, fill_price, "Filled"
                elif status in ("Cancelled", "Rejected", "Deactivated"):
                    log.error(f"[{symbol}] Entry {status}")
                    return False, 0.0, status
            except Exception as e:
                log.warning(f"[{symbol}] Fill check #{check}: {e}")
        log.error(f"[{symbol}] Entry NOT filled after {FILL_POLL_TIMEOUT}s")
        return False, 0.0, "TIMEOUT"

    # ── Execute signal ─────────────────────────────────────────

    def execute_signal(self, signal: Signal, balance: float) -> bool:
        sym   = signal.symbol
        side  = signal.side
        price = signal.price
        atr   = signal.atr

        with positions_lock:
            if sym in open_positions:
                return False

        if signal.atr_pct < VOL_FLOOR_PCT:
            return False

        # SL calculation
        if side == "LONG":
            sl_price = price - atr * ATR_SL_MULT
            api_side = "Buy"
            limit_price = price * 1.0005
        else:
            sl_price = price + atr * ATR_SL_MULT
            api_side = "Sell"
            limit_price = price * 0.9995

        # Position sizing
        daily_pnl_val = self.risk.daily_pnl(balance)
        qty = self.risk.calc_position_size(balance, price, sl_price, daily_pnl_val)

        info = self.client.get_instrument_info(sym)
        qty_step = info["qty_step"]
        min_qty  = info["min_qty"]

        qty = _floor_to_step(qty, qty_step)
        if qty < min_qty:
            return False

        max_qty = _floor_to_step((balance * 0.30) / price, qty_step)
        if max_qty < qty_step:
            return False
        if qty > max_qty:
            qty = max_qty

        if qty * price < MIN_NOTIONAL_USD:
            return False

        # Place limit entry with retry
        order_id = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                result = self.client.place_limit_order(sym, api_side, qty, limit_price)
                order_id = result.get("orderId", "")
                break
            except Exception as e:
                log.error(f"[ERROR] entry {sym} attempt {attempt}: {e}")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY_S)

        if order_id is None:
            log.error(f"[{sym}] All entry attempts failed")
            return False

        log.info(
            f"[ENTRY] {sym} {side} qty={qty} @ ${price:.4f} "
            f"SL=${sl_price:.4f} (orderID={order_id})"
        )

        # Poll for fill
        filled, fill_price, fill_status = self._poll_for_fill(sym, order_id, price)
        if not filled:
            log.error(f"[{sym}] Entry not filled ({fill_status})")
            return False

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # POST-FILL: set SL via trading-stop (ONLY stopLoss)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        try:
            self.client.set_position_sl(sym, sl_price)
        except Exception as e:
            log.error(f"[CRITICAL] {sym} SL FAILED: {e} — POSITION UNPROTECTED!")

        # Save to open_positions dict and SQLite
        with _db_lock:
            cursor = self.db.execute(
                """INSERT INTO trades
                   (pair,side,qty,entry_price,entry_time,sl_price,atr,order_id,stage,status)
                   VALUES (?,?,?,?,?,?,?,?,0,'ACTIVE')""",
                (sym, side, qty, fill_price,
                 datetime.now(timezone.utc).isoformat(),
                 sl_price, atr, order_id),
            )
            self.db.commit()
            db_id = cursor.lastrowid

        pos = OpenPosition(
            symbol=sym, side=side, entry_price=fill_price,
            qty=qty, remaining_qty=qty,
            atr=atr, sl_price=sl_price,
            stage=0, db_id=db_id,
        )
        with positions_lock:
            open_positions[sym] = pos

        log.info(f"[ACTIVE] {sym} {side} qty={qty} entry=${fill_price:.4f} SL=${sl_price:.4f}")
        return True

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # LOOP1: market_scanner_loop — every 10s
    # Uses batch ticker call for all pairs at once
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def market_scanner_loop(self):
        log.info("[LOOP1] Market scanner started (every 10s, batch tickers)")
        while self._running:
            cycle_start = time.time()
            try:
                balance = self.client.get_wallet_balance()
                self.risk.set_start_balance(balance)
                daily_pnl = self.risk.daily_pnl(balance)

                with positions_lock:
                    open_count = len(open_positions)

                log.info(
                    f"[SCAN] Balance=${balance:.2f} PnL={daily_pnl:.2%} "
                    f"Positions={open_count}/{MAX_POSITIONS}"
                )

                can_trade, reason = self.risk.can_open(balance, open_count)
                if not can_trade:
                    log.info(f"[RISK] {reason}")
                else:
                    # Batch ticker: one call for all linear pairs
                    try:
                        all_tickers = self.client.get_all_tickers()
                    except Exception as e:
                        log.error(f"[ERROR] batch tickers: {e}")
                        all_tickers = {}

                    for sym in PAIRS:
                        with positions_lock:
                            if sym in open_positions:
                                continue
                            if len(open_positions) >= MAX_POSITIONS:
                                break

                        try:
                            klines = self.client.get_klines(sym)
                            signal = detect_signal(sym, klines)
                            if signal:
                                # Override signal price with batch ticker
                                if sym in all_tickers:
                                    signal.price = all_tickers[sym]
                                log.info(
                                    f"[SIGNAL] {sym} {signal.side} "
                                    f"RSI={signal.rsi:.1f} MACD={signal.macd_val:.6f}"
                                )
                                self.execute_signal(signal, balance)
                        except Exception as e:
                            log.error(f"[ERROR] scan {sym}: {e}")
                        time.sleep(0.1)

            except Exception as e:
                log.error(f"[ERROR] scanner cycle: {e}")

            elapsed = time.time() - cycle_start
            sleep_for = max(0, SCAN_INTERVAL_S - elapsed)
            time.sleep(sleep_for)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # LOOP2: position_monitor_loop — every 2s
    # ONLY runs when len(open_positions) > 0
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def position_monitor_loop(self):
        log.info("[LOOP2] Position monitor started (every 2s)")
        while self._running:
            with positions_lock:
                if not open_positions:
                    time.sleep(MONITOR_INTERVAL_S)
                    continue
                snapshot = list(open_positions.values())

            for pos in snapshot:
                try:
                    self._check_position(pos)
                except Exception as e:
                    log.error(f"[LOOP2] {pos.symbol} error: {e}")

            # Cleanup: remove positions that are fully closed on exchange
            self._sync_closed_positions()

            time.sleep(MONITOR_INTERVAL_S)

    def _check_position(self, pos: OpenPosition):
        """Check TP levels and manage trailing SL for one position."""
        price = self.client.get_ticker_price(pos.symbol)
        info = self.client.get_instrument_info(pos.symbol)
        qty_step = info["qty_step"]

        is_long = (pos.side == "LONG")

        # Compute TP thresholds
        if is_long:
            tp1_price = pos.entry_price * (1 + TP1_PCT)
            tp2_price = pos.entry_price * (1 + TP2_PCT)
            hit_tp1 = price >= tp1_price
            hit_tp2 = price >= tp2_price
        else:
            tp1_price = pos.entry_price * (1 - TP1_PCT)
            tp2_price = pos.entry_price * (1 - TP2_PCT)
            hit_tp1 = price <= tp1_price
            hit_tp2 = price <= tp2_price

        # ── STAGE 0 → 1: TP1 hit — close 50%, move SL to breakeven ──
        if pos.stage == 0 and hit_tp1:
            close_qty = _floor_to_step(pos.qty * TP1_CLOSE_FRAC, qty_step)
            if close_qty >= info["min_qty"]:
                close_side = "Sell" if is_long else "Buy"
                try:
                    self.client.place_market_order(pos.symbol, close_side, close_qty)
                    log.info(
                        f"[TP1] {pos.symbol} closed {close_qty} @ ${price:.4f} "
                        f"(50% partial close)"
                    )
                except Exception as e:
                    log.error(f"[TP1] {pos.symbol} close failed: {e}")
                    return

                # Move SL to breakeven via trading-stop
                try:
                    self.client.set_position_sl(pos.symbol, pos.entry_price)
                    log.info(f"[SL→BE] {pos.symbol} SL moved to breakeven ${pos.entry_price:.4f}")
                except Exception as e:
                    log.error(f"[SL→BE] {pos.symbol} failed: {e}")

                with positions_lock:
                    pos.stage = 1
                    pos.remaining_qty -= close_qty
                    pos.sl_price = pos.entry_price

                with _db_lock:
                    self.db.execute(
                        "UPDATE trades SET stage=1, sl_price=? WHERE id=?",
                        (pos.entry_price, pos.db_id),
                    )
                    self.db.commit()

        # ── STAGE 1 → 2: TP2 hit — close 40%, activate trailing ──
        elif pos.stage == 1 and hit_tp2:
            close_qty = _floor_to_step(pos.qty * TP2_CLOSE_FRAC, qty_step)
            if close_qty >= info["min_qty"]:
                close_side = "Sell" if is_long else "Buy"
                try:
                    self.client.place_market_order(pos.symbol, close_side, close_qty)
                    log.info(
                        f"[TP2] {pos.symbol} closed {close_qty} @ ${price:.4f} "
                        f"(40% partial close)"
                    )
                except Exception as e:
                    log.error(f"[TP2] {pos.symbol} close failed: {e}")
                    return

                with positions_lock:
                    pos.stage = 2
                    pos.remaining_qty -= close_qty

                with _db_lock:
                    self.db.execute(
                        "UPDATE trades SET stage=2 WHERE id=?",
                        (pos.db_id,),
                    )
                    self.db.commit()

                log.info(f"[TRAIL] {pos.symbol} trailing SL activated (stage 2)")

        # ── STAGE 2: trailing SL — update every 2s ──
        elif pos.stage == 2:
            trail_distance = pos.atr * TRAIL_ATR_MULT
            if is_long:
                new_sl = price - trail_distance
            else:
                new_sl = price + trail_distance

            # Only ratchet SL in favorable direction
            if is_long:
                new_sl = max(pos.sl_price, new_sl)
            else:
                new_sl = min(pos.sl_price, new_sl)

            if new_sl != pos.sl_price:
                try:
                    self.client.set_position_sl(pos.symbol, new_sl)
                    log.info(
                        f"[TRAIL] {pos.symbol} SL updated "
                        f"${pos.sl_price:.4f} → ${new_sl:.4f}"
                    )
                    with positions_lock:
                        pos.sl_price = new_sl
                    with _db_lock:
                        self.db.execute(
                            "UPDATE trades SET sl_price=? WHERE id=?",
                            (new_sl, pos.db_id),
                        )
                        self.db.commit()
                except Exception as e:
                    log.error(f"[TRAIL] {pos.symbol} SL update failed: {e}")

    def _sync_closed_positions(self):
        """Remove from open_positions if no longer on exchange."""
        try:
            exchange_positions = self.client.get_positions()
        except Exception:
            return

        open_symbols = {p.get("symbol") for p in exchange_positions}

        with positions_lock:
            to_remove = [sym for sym in open_positions if sym not in open_symbols]

        for sym in to_remove:
            with positions_lock:
                pos = open_positions.pop(sym, None)
            if pos:
                with _db_lock:
                    self.db.execute(
                        "UPDATE trades SET status='CLOSED' WHERE id=?",
                        (pos.db_id,),
                    )
                    self.db.commit()
                log.info(f"[CLOSED] {sym} position no longer on exchange")

    # ── Main entry point ───────────────────────────────────────

    def run(self):
        log.info("=" * 60)
        log.info("  FAST CAPITALIZATION SNIPER V3.56 — DUAL-LOOP")
        log.info("  SL: EXCLUSIVELY via /v5/position/trading-stop")
        log.info("  TP: partial market close in position_monitor_loop")
        log.info("=" * 60)
        log.info(f"  Pairs          : {len(PAIRS)}")
        log.info(f"  Interval       : {INTERVAL}m candles")
        log.info(f"  LOOP1 interval : {SCAN_INTERVAL_S}s (scanner, batch tickers)")
        log.info(f"  LOOP2 interval : {MONITOR_INTERVAL_S}s (monitor)")
        log.info(f"  Max positions  : {MAX_POSITIONS}")
        log.info(f"  Risk/trade     : {RISK_PER_TRADE*100:.1f}%")
        log.info(f"  SL             : ATR x {ATR_SL_MULT}")
        log.info(f"  TP1            : +{TP1_PCT*100:.1f}% close {TP1_CLOSE_FRAC*100:.0f}%")
        log.info(f"  TP2            : +{TP2_PCT*100:.1f}% close {TP2_CLOSE_FRAC*100:.0f}%")
        log.info(f"  Trailing       : ATR x {TRAIL_ATR_MULT} (stage 2)")
        log.info(f"  Daily cutoff   : {DAILY_LOSS_CUTOFF*100:.1f}%")
        log.info(f"  Base URL       : {BASE_URL}")
        log.info("=" * 60)

        t1 = threading.Thread(target=self.market_scanner_loop,
                              name="LOOP1-scanner", daemon=True)
        t2 = threading.Thread(target=self.position_monitor_loop,
                              name="LOOP2-monitor", daemon=True)
        t1.start()
        t2.start()

        try:
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            log.info("Bot stopped by user (Ctrl+C)")
            self._running = False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    log.info("Starting bot...")
    try:
        engine = TradingEngine()
        engine.run()
    except KeyboardInterrupt:
        log.info("Bot stopped by user (Ctrl+C)")
    except Exception as e:
        log.error(f"[FATAL] Bot crashed: {e}")
        raise
