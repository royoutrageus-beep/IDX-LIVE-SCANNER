"""
╔══════════════════════════════════════════════════════════╗
║         IDX RUNNING TRADE SCANNER  v3.0                  ║
║         Auto-scan | Live Log | Telegram Notify TOP 10    ║
╚══════════════════════════════════════════════════════════╝
Usage:
    pip install streamlit yfinance pandas numpy ta requests
    streamlit run idx_running_trade_v3.py

Telegram Setup:
    1. Chat @BotFather → /newbot → copy token
    2. Chat @userinfobot → copy chat_id
    3. Masukkan di sidebar app
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import requests
from datetime import datetime
import pytz
WIB = pytz.timezone("Asia/Jakarta")
import warnings
warnings.filterwarnings("ignore")

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IDX Running Trade Scanner v3",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── BLOOMBERG DARK THEME ──────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&display=swap');

  html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace;
    background-color: #0a0a0f;
    color: #e0e0e0;
  }
  .stApp { background-color: #0a0a0f; }

  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d18 0%, #0a0a14 100%);
    border-right: 1px solid #1a2a3a;
  }

  .metric-card {
    background: linear-gradient(135deg, #0d1a26 0%, #0a1220 100%);
    border: 1px solid #1e3a5f;
    border-radius: 6px;
    padding: 14px 18px;
    margin: 4px 0;
  }
  .metric-val   { font-size: 22px; font-weight: 700; color: #00d4ff; }
  .metric-label { font-size: 10px; color: #607080; letter-spacing: 1px; text-transform: uppercase; }

  .scanner-header {
    background: linear-gradient(90deg, #0d1a26, #091520);
    border: 1px solid #1e3a5f;
    border-left: 4px solid #ff6600;
    border-radius: 4px;
    padding: 14px 20px;
    margin-bottom: 16px;
  }
  .scanner-title { font-size: 20px; font-weight: 700; color: #ff6600; letter-spacing: 2px; }
  .scanner-sub   { font-size: 11px; color: #607080; margin-top: 2px; }

  .log-box {
    background: #05080d;
    border: 1px solid #1a2a3a;
    border-radius: 4px;
    padding: 10px 14px;
    font-size: 11px;
    color: #607080;
    max-height: 200px;
    overflow-y: auto;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1.8;
  }
  .log-hot  { color: #ff4444; font-weight: 700; }
  .log-buy  { color: #ff9900; font-weight: 700; }
  .log-ok   { color: #00ff88; }
  .log-skip { color: #304050; }
  .log-scan { color: #00aaff; }

  .tele-preview {
    background: #17212b;
    border: 1px solid #2a3f55;
    border-radius: 12px;
    padding: 16px 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #d0d0d0;
    line-height: 1.9;
    white-space: pre-wrap;
    word-break: break-word;
  }
  .tele-header {
    background: #0d1a26;
    border: 1px solid #1e3a5f;
    border-radius: 8px 8px 0 0;
    padding: 10px 16px;
    font-size: 11px;
    color: #607080;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .stButton > button {
    background: linear-gradient(135deg, #0d2a45, #091a2e);
    color: #00d4ff;
    border: 1px solid #1e5a8f;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    letter-spacing: 1px;
    transition: all 0.2s;
    width: 100%;
  }
  .stButton > button:hover {
    background: linear-gradient(135deg, #1a3a55, #0d2a3e);
    border-color: #00d4ff;
    color: #fff;
  }
  .btn-tele > button {
    background: linear-gradient(135deg, #0a2a1a, #052010) !important;
    color: #00cc66 !important;
    border: 1px solid #00aa44 !important;
  }
  .btn-tele > button:hover {
    background: linear-gradient(135deg, #0d3a22, #072a14) !important;
    border-color: #00ff88 !important;
    color: #00ff88 !important;
  }

  hr { border-color: #1e3a5f !important; }
  .up   { color: #00ff88; font-weight: 700; }
  .down { color: #ff4444; font-weight: 700; }
  .neu  { color: #aaaaaa; }

  .stProgress > div > div > div > div {
    background: linear-gradient(90deg, #ff6600, #ff9900) !important;
  }

  .stTextInput > div > div > input,
  .stTextInput > div > div > input:focus {
    background: #0d1a26 !important;
    border: 1px solid #1e3a5f !important;
    color: #e0e0e0 !important;
    font-family: 'JetBrains Mono', monospace;
  }
</style>
""", unsafe_allow_html=True)

# ── STOCK UNIVERSE ────────────────────────────────────────────────────────────
IDX_UNIVERSE = {
    "LQ45 Blue Chips": [
        "BBCA", "BBRI", "BMRI", "TLKM", "ASII", "GOTO", "BYAN", "MDKA",
        "UNVR", "ICBP", "INDF", "KLBF", "SIDO", "MNCN", "EXCL",
        "TOWR", "PGAS", "PTBA", "ADRO", "ITMG", "INCO", "HRUM",
        "JSMR", "SMGR", "WIKA", "WSKT", "ANTM", "PTPP", "TBIG",
    ],
    "Mid Cap Aktif": [
    "AADI", "AALI", "ABBA", "ABDA", "ABMM", "ACES", "ACRO", "ACST", "ADCP", "ADES", 
    "ADHI", "ADMF", "ADMG", "ADMR", "ADRO", "AEGS", "AGAR", "AGII", "AGRO", "AGRS", 
    "AHAP", "AIMS", "AISA", "AKKU", "AKPI", "AKRA", "AKSI", "ALDO", "ALII", "ALKA", 
    "ALMI", "ALTO", "AMAG", "AMAN", "AMAR", "AMFG", "AMIN", "AMMN", "AMMS", "AMOR", 
    "AMRT", "ANDI", "ANJT", "ANTM", "APEX", "APIC", "APII", "APLI", "APLN", "ARCI", 
    "AREA", "ARGO", "ARII", "ARKA", "ARKO", "ARMY", "ARNA", "ARTA", "ARTI", "ARTO", 
    "ASBI", "ASDM", "ASGR", "ASHA", "ASII", "ASJT", "ASLI", "ASLC", "ASMI", "ASPI", 
    "ASPR", "ASRI", "ASRM", "ASSA", "ATAP", "ATIC", "ATLA", "AUTO", "AVIA", "AWAN", 
    "AXIO", "AYAM", "AYLS", "BABA", "BABP", "BABY", "BACA", "BAIK", "BAJA", "BALI", 
    "BANK", "BAPA", "BAPI", "BATA", "BATR", "BAUT", "BAYU", "BBCA", "BBHI", "BBKP", 
    "BBLD", "BBMD", "BBNI", "BBRI", "BBRM", "BBSI", "BBSS", "BBTN", "BBYB", "BCAP", 
    "BCIC", "BCIP", "BDKR", "BDMN", "BEBS", "BEEF", "BEER", "BEKS", "BELI", "BELL", 
    "BESS", "BEST", "BFIN", "BGTG", "BHAT", "BHIT", "BIAS", "BIKA", "BIKE", "BIMA", 
    "BINA", "BINO", "BIPI", "BIPP", "BIRD", "BISI", "BIWA", "BJBR", "BJTM", "BKDP", 
    "BKSL", "BKSW", "BLES", "BLOG", "BLTA", "BLTZ", "BLUE", "BMAS", "BMBL", "BMHS", 
    "BMRI", "BMSR", "BMTR", "BNBA", "BNBR", "BNGA", "BNII", "BNLI", "BOAT", "BOBA", 
    "BOGA", "BOLA", "BOLT", "BOSS", "BPFI", "BPII", "BPTR", "BRAM", "BREN", "BRIS", 
    "BRMS", "BRNA", "BRPT", "BRRC", "BSBK", "BSDE", "BSIM", "BSML", "BSSR", "BSWD", 
    "BTEK", "BTEL", "BTON", "BTPN", "BTPS", "BUAH", "BUDI", "BUKA", "BUKK", "BULL", 
    "BUMI", "BUVA", "BVIC", "BWPT", "BYAN", "CAKK", "CAMP", "CANI", "CARE", "CARS", 
    "CASA", "CASH", "CASS", "CBDK", "CBPE", "CBRE", "CBUT", "CBMF", "CCSI", "CDIA", 
    "CEKA", "CENT", "CFIN", "CGAS", "CHEK", "CHEM", "CHIP", "CINT", "CITA", "CITY", 
    "CLAY", "CLEO", "CLPI", "CMNP", "CMNT", "CMPP", "CMRY", "CNKO", "CNMA", "CNTX", 
    "COAL", "COCO", "COIN", "COWL", "CPIN", "CPRI", "CPRO", "CRAB", "CRSN", "CSAP", 
    "CSIS", "CSMI", "CSRA", "CTBN", "CTRA", "CTTH", "CUAN", "CYBR", "DAAZ", "DADA", 
    "DART", "DATA", "DAYA", "DCII", "DEAL", "DEFI", "DEPO", "DEWA", "DEWI", "DFAM", 
    "DGNS", "DGWG", "DGIK", "DIGI", "DILD", "DIVA", "DKFT", "DKHH", "DLTA", "DMAS", 
    "DMMX", "DMND", "DNAR", "DNET", "DOID", "DOOH", "DOSS", "DPNS", "DPUM", "DRMA", 
    "DSFI", "DSNG", "DSSA", "DUCK", "DUTI", "DVLA", "DWGL", "DYAN", "EAST", "ECII", 
    "EDGE", "EKAD", "ELIT", "ELPI", "ELSA", "ELTY", "EMAS", "EMDE", "EMTK", "ENAK", 
    "ENRG", "ENVY", "ENZO", "EPAC", "EPMT", "ERAL", "ERAA", "ERTX", "ESIP", "ESSA", 
    "ESTA", "ESTI", "ETWA", "EURO", "EXCL", "FAPA", "FAST", "FASW", "FILM", "FIMP", 
    "FIRE", "FISH", "FITT", "FLMC", "FOLK", "FOOD", "FORE", "FORU", "FPNI", "FUJI", 
    "FUTR", "FWCT", "GAMA", "GDST", "GDYR", "GEMA", "GEMS", "GGRP", "GGRM", "GHON", 
    "GIAA", "GJTL", "GLOB", "GLVA", "GMFI", "GMTD", "GOLF", "GOLD", "GOLL", "GOOD", 
    "GOTO", "GPRA", "GPSO", "GRIA", "GRPH", "GRPM", "GRII", "GSMF", "GTBO", "GTRA", 
    "GTSI", "GULA", "GUNA", "GWSA", "GZCO", "HADE", "HAIS", "HAJJ", "HALO", "HATM", 
    "HBAT", "HDFA", "HDIT", "HEAL", "HELI", "HERO", "HEXA", "HGII", "HILL", "HITS", 
    "HKMU", "HMSP", "HOKI", "HOME", "HOMI", "HOPE", "HOTL", "HRME", "HRTA", "HRUM", 
    "HUMI", "HYGN", "IATA", "IBFN", "IBOS", "IBST", "ICBP", "ICON", "IDEA", "IDPR", 
    "IFII", "IFSH", "IGAR", "IIKP", "IKAI", "IKAN", "IKBI", "IKPM", "IMAS", "IMJS", 
    "IMPC", "INAF", "INAI", "INCF", "INCI", "INCO", "INDF", "INDO", "INDR", "INDS", 
    "INDX", "INDY", "INET", "INKP", "INOV", "INPC", "INPP", "INPS", "INRU", "INTA", 
    "INTD", "INTP", "IOTF", "IPAC", "IPCC", "IPCM", "IPOL", "IPPE", "IPTV", "IRRA", 
    "IRSX", "ISAP", "ISAT", "ISEA", "ISSP", "ITIC", "ITMA", "ITMG", "JAAS", "JARR", 
    "JAST", "JATI", "JAVA", "JAYA", "JECC", "JGLE", "JIHD", "JKON", "JMAS", "JPFA", 
    "JRPT", "JSKY", "JSMR", "JSPT", "JTPE", "KAEF", "KAQI", "KARW", "KARY", "KAST", 
    "KAYU", "KBAG", "KBLI", "KBLM", "KBLV", "KBRI", "KDSI", "KDTN", "KEEN", "KEJU", 
    "KETR", "KIAS", "KICI", "KIJA", "KING", "KINO", "KIOS", "KJEN", "KKES", "KKGI", 
    "KLAS", "KLBF", "KLIN", "KMDS", "KMTR", "KOBX", "KOCI", "KOIN", "KOKA", "KONI", 
    "KOPI", "KOTA", "KPIG", "KRAH", "KRAS", "KREN", "KSIX", "KUAS", "LABA", "LABS", 
    "LAJU", "LAND", "LAPD", "LCGP", "LCKM", "LEAD", "LFLO", "LIFE", "LINK", "LION", 
    "LIVE", "LMAS", "LMPI", "LMSH", "LOPI", "LPCK", "LPGI", "LPIN", "LPKR", "LPLI", 
    "LPPF", "LPPS", "LRNA", "LSIP", "LTLS", "LUCK", "LUCY", "MAAS", "MABA", "MADA", 
    "MAGP", "MAHA", "MAIN", "MANG", "MAPA", "MAPB", "MAPI", "MARI", "MARK", "MASA", 
    "MASB", "MAYA", "MBAP", "MBMA", "MBSS", "MBTO", "MCAS", "MCOL", "MCOR", "MDIA", 
    "MDKA", "MDKI", "MDLA", "MDLN", "MDRN", "MEDC", "MEDS", "MEGA", "MEJA", "MENN", 
    "MERI", "MERK", "META", "MFMI", "MGNA", "MGRO", "MHKI", "MICE", "MIDI", "MIKA", 
    "MINA", "MINE", "MIRA", "MITI", "MKAP", "MKPI", "MKTR", "MLBI", "MLIA", "MLPL", 
    "MLPT", "MMLP", "MMIX", "MNCN", "MOLI", "MORA", "MPOW", "MPMX", "MPPA", "MPRO", 
    "MPXL", "MRAT", "MREI", "MSIE", "MSIN", "MSJA", "MSKY", "MSTI", "MTDL", "MTEL", 
    "MTFN", "MTLA", "MTMH", "MTPS", "MTRA", "MTRN", "MTSM", "MTWI", "MUTU", "MYOH", 
    "MYOR", "MYTX", "NAIK", "NANO", "NASA", "NASI", "NATO", "NAYZ", "NCKL", "NELY", 
    "NEST", "NETV", "NICE", "NICK", "NICL", "NIKL", "NINE", "NIRO", "NISP", "NOBU", 
    "NPGF", "NRCA", "NSSS", "NTBK", "NUSA", "NZIA", "OASA", "OBAT", "OBMD", "OCAP", 
    "OILS", "OKAS", "OLIV", "OMED", "OMRE", "OPMS", "PACK", "PADA", "PADI", "PALM", 
    "PAMG", "PANI", "PANR", "PANS", "PART", "PBID", "PBSA", "PBRX", "PCAR", "PDES", 
    "PDPP", "PEGE", "PEHA", "PELI", "PENT", "PERW", "PEVE", "PGAS", "PGEO", "PGJO", 
    "PGLI", "PGUN", "PICO", "PIPA", "PJAA", "PJHB", "PKPK", "PLAN", "PLAS", "PLIN", 
    "PMJS", "PMMP", "PMUI", "PNBN", "PNBS", "PNGO", "PNIN", "PNLF", "PNSE", "POLA", 
    "POLI", "POLL", "POLU", "POLY", "POOL", "PORT", "POSA", "POWR", "PPGL", "PPRI", 
    "PPRE", "PPRO", "PRAY", "PRDA", "PRIM", "PSAB", "PSAT", "PSDN", "PSGO", "PSKT", 
    "PSSI", "PTBA", "PTDU", "PTIS", "PTMP", "PTMR", "PTPP", "PTPS", "PTPW", "PTRO", 
    "PTSN", "PTSP", "PUDP", "PURA", "PURE", "PURI", "PWON", "PYFA", "PZZA", "RAAM", 
    "RAFI", "RAJA", "RALS", "RANC", "RATU", "RBMS", "RCCC", "RDTX", "REAL", "RELF", 
    "RELI", "REPP", "RGAS", "RICY", "RIGS", "RIMO", "RISE", "RLCO", "RMBA", "RMKE", 
    "RMKO", "RMLP", "ROCK", "RODA", "ROLI", "RONY", "ROTI", "RSCH", "RSGK", "RUIS", 
    "RUNS", "SAFE", "SAGE", "SAGI", "SAME", "SAMF", "SAMR", "SAMP", "SANO", "SAPX", 
    "SATU", "SBAT", "SBMA", "SCCO", "SCMA", "SCNP", "SCPI", "SDMU", "SDPC", "SDRA", 
    "SEMA", "SFAN", "SGER", "SGGH", "SGJL", "SGRO", "SHID", "SHIP", "SICO", "SIDO", 
    "SIER", "SILO", "SIMA", "SIMP", "SINI", "SIPD", "SKBM", "SKLT", "SKRN", "SKYB", 
    "SLIS", "SMAR", "SMDM", "SMDR", "SMGA", "SMGR", "SMKM", "SMKL", "SMLE", "SMMA", 
    "SMMT", "SMRA", "SMRU", "SMSM", "SNLK", "SOCI", "SOFA", "SOHO", "SOLA", "SONA", 
    "SOSS", "SOTS", "SOUL", "SPMA", "SPRE", "SPTO", "SQMI", "SRAJ", "SREI", "SRIL", 
    "SRSN", "SRTG", "SSIA", "SSMS", "SSTM", "STAA", "STAR", "STRK", "STTP", "SUGI", 
    "SULI", "SUNI", "SUPA", "SUPR", "SURE", "SWAT", "SWID", "SYAI", "TALF", "TAMA", 
    "TAMU", "TAPG", "TARA", "TAXI", "TAYS", "TBIG", "TBLA", "TBMS", "TCID", "TCPI", 
    "TDPM", "TEBE", "TECH", "TELE", "TFAS", "TFCO", "TGKA", "TGRA", "TGUK", "TIFA", 
    "TINS", "TIRA", "TIRT", "TKIM", "TLDN", "TLKM", "TMAS", "TMPO", "TNCA", "TOBA", 
    "TOOL", "TOPS", "TOSK", "TOTL", "TOTO", "TOWR", "TOYS", "TPAI", "TPIA", "TPMA", 
    "TRAM", "TRGU", "TRIL", "TRIM", "TRIN", "TRIO", "TRIS", "TRJA", "TRON", "TRST", 
    "TRUE", "TRUK", "TRUS", "TSPC", "TUGU", "TULT", "TYRE", "UANG", "UCID", "UDNG", 
    "UFOE", "ULTJ", "UNIC", "UNIQ", "UNIT", "UNSP", "UNTR", "UNVR", "URBN", "UVCR", 
    "VAST", "VATE", "VCOK", "VERN", "VICI", "VICO", "VINS", "VISA", "VISI", "VIVA", 
    "VKTR", "VOKS", "VOSS", "VRNA", "VTNY", "WAPO", "WBSA", "WEGE", "WEHA", "WGSH", 
    "WICO", "WIDI", "WIFI", "WIIM", "WIKA", "WINE", "WINR", "WINS", "WIRG", "WITA", 
    "WMPP", "WMUU", "WOMF", "WONS", "WOOD", "WOWS", "WPOW", "WSBP", "WSKT", "WTON", 
    "YELO", "YOII", "YPAS", "YULE", "YUPI", "ZATA", "ZBRA", "ZENI", "ZINC", "ZONE", 
    "ZYRX", "KRYA",
    ],
    "High Volatility": [
        "BRIS", "ADMR", "MBMA", "CUAN", "AMMN", "SBMA", "SRTG",
        "BRPT", "FILM", "RATU", "CGAS", "CSMI", "NICL",
    ],
}

ALL_STOCKS = sorted(set(t for g in IDX_UNIVERSE.values() for t in g))

# ── HELPERS ───────────────────────────────────────────────────────────────────
def yf_ticker(code): return f"{code}.JK"

def color_change(val):
    if val > 0:   return f'<span class="up">▲ {val:.2f}%</span>'
    elif val < 0: return f'<span class="down">▼ {abs(val):.2f}%</span>'
    return f'<span class="neu">  {val:.2f}%</span>'

# ── TELEGRAM FORMATTER ────────────────────────────────────────────────────────
def build_telegram_message(df_top10: pd.DataFrame) -> str:
    now = datetime.now(WIB)
    ts    = now.strftime("%d %b %Y  %H:%M WIB")
    day   = now.strftime("%A")

    # Header
    lines = [
        "⚡ *IDX RUNNING TRADE SCANNER*",
        f"📅 `{day}, {ts}`",
        "━━━━━━━━━━━━━━━━━━━━━━━",
        "🏆 *TOP 10 CANDIDATES*",
        "",
    ]

    signal_emoji = {
        "STRONG": "🔥",
        "BUY":    "⚡",
        "WATCH":  "👀",
        "SKIP":   "❄",
    }

    for i, row in df_top10.reset_index(drop=True).iterrows():
        rank    = i + 1
        ticker  = row["Ticker"]
        price   = row["Price"]
        chg1d   = row["Chg 1D %"]
        vol     = row["Vol Ratio"]
        rsi     = row["RSI"]
        score   = row["Score"]
        signal  = row["Signal"]
        macd    = row["MACD ✓"]
        ema20   = row["EMA20 ✓"]
        ema50   = row["EMA50 ✓"]
        bb      = row["BB%"]
        chg3d   = row["Chg 3D %"]

        # Determine emoji
        if "STRONG" in signal:   sig_icon = "🔥"
        elif "BUY" in signal:    sig_icon = "⚡"
        elif "WATCH" in signal:  sig_icon = "👀"
        else:                     sig_icon = "❄"

        # Change arrow
        chg_arrow = "▲" if chg1d >= 0 else "▼"
        chg_str   = f"{chg_arrow}{abs(chg1d):.2f}%"

        # Score bar (visual)
        filled = int(score / 10)
        bar    = "█" * filled + "░" * (10 - filled)

        # RSI zone label
        if rsi < 30:        rsi_zone = "oversold"
        elif rsi <= 50:     rsi_zone = "recovery"
        elif rsi <= 65:     rsi_zone = "running ✅"
        elif rsi <= 70:     rsi_zone = "hot zone"
        else:               rsi_zone = "overbought ⚠️"

        lines += [
            f"{'━'*23}",
            f"{sig_icon} *#{rank} {ticker}.JK*   {signal}",
            f"💰 `Rp {price:,.0f}`   {chg_str} (1D)  |  3D: {chg3d:+.2f}%",
            f"📊 Score: `{score:.0f}/100`  [{bar}]",
            f"📈 Vol Ratio : `{vol:.2f}x`",
            f"📉 RSI       : `{rsi:.1f}` — {rsi_zone}",
            f"🔀 MACD      : {macd}   EMA20: {ema20}   EMA50: {ema50}",
            f"📐 BB%       : `{bb:.2f}` {'✅' if bb < 0.8 else '⚠️ near top'}",
            "",
        ]

    # Footer
    lines += [
        "━━━━━━━━━━━━━━━━━━━━━━━",
        "⚠️ _Bukan financial advice_",
        "🤖 _IDX Running Trade Scanner v3.0_",
    ]

    return "\n".join(lines)

# ── SEND TELEGRAM ─────────────────────────────────────────────────────────────
def send_telegram(token: str, chat_id: str, message: str) -> tuple[bool, str]:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id":    chat_id,
        "text":       message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            return True, "✅ Pesan berhasil dikirim ke Telegram!"
        else:
            return False, f"❌ Error {r.status_code}: {r.json().get('description', 'Unknown error')}"
    except Exception as e:
        return False, f"❌ Exception: {str(e)}"

# ── SCORE ONE TICKER ──────────────────────────────────────────────────────────
def score_ticker(code: str):
    try:
        df = yf.download(yf_ticker(code), period="3mo",
                         interval="1d", progress=False, auto_adjust=True)
        if df is None or len(df) < 20:
            return None

        close  = df["Close"].squeeze()
        volume = df["Volume"].squeeze()

        chg_1d = (close.iloc[-1] / close.iloc[-2] - 1) * 100
        chg_3d = (close.iloc[-1] / close.iloc[-4] - 1) * 100
        chg_5d = (close.iloc[-1] / close.iloc[-6] - 1) * 100

        vol_avg20 = volume.iloc[-21:-1].mean()
        vol_ratio = float(volume.iloc[-1] / vol_avg20) if vol_avg20 > 0 else 1.0

        rsi = float(ta.momentum.RSIIndicator(close, 14).rsi().iloc[-1])

        macd_obj   = ta.trend.MACD(close)
        macd_val   = float(macd_obj.macd().iloc[-1])
        macd_sig   = float(macd_obj.macd_signal().iloc[-1])
        macd_hist  = float(macd_obj.macd_diff().iloc[-1])
        macd_cross = macd_val > macd_sig

        bb     = ta.volatility.BollingerBands(close, 20, 2)
        bb_pct = float(bb.bollinger_pband().iloc[-1])

        ema20      = float(ta.trend.EMAIndicator(close, 20).ema_indicator().iloc[-1])
        ema50      = float(ta.trend.EMAIndicator(close, 50).ema_indicator().iloc[-1])
        price_last = float(close.iloc[-1])
        above_ema20 = price_last > ema20
        above_ema50 = price_last > ema50

        atr = float(ta.volatility.AverageTrueRange(
            df["High"].squeeze(), df["Low"].squeeze(), close, 14
        ).average_true_range().iloc[-1])
        atr_pct = (atr / price_last) * 100

        score = 0.0
        score += min(float(chg_1d) * 5, 20) if chg_1d > 0 else 0
        score += min(float(chg_3d) * 2, 10) if chg_3d > 0 else 0
        score += min(float(chg_5d) * 1,  5) if chg_5d > 0 else 0
        score += min((vol_ratio - 1) * 10, 25) if vol_ratio > 1 else 0
        if 40 <= rsi <= 65:   score += 15
        elif 65 < rsi <= 70:  score += 8
        elif 30 <= rsi < 40:  score += 5
        if macd_cross:        score += 10
        if macd_hist > 0:     score += 5
        if above_ema20:       score += 5
        if above_ema50:       score += 5
        if bb_pct < 0.8:      score += 5
        score = min(score, 100)

        if score >= 70 and vol_ratio >= 2.0: signal = "🔥 STRONG BUY"
        elif score >= 55:                    signal = "⚡ BUY"
        elif score >= 40:                    signal = "👀 WATCH"
        else:                                signal = "❄ SKIP"

        return {
            "Ticker":    code,
            "Price":     round(price_last, 0),
            "Chg 1D %":  round(float(chg_1d), 2),
            "Chg 3D %":  round(float(chg_3d), 2),
            "Chg 5D %":  round(float(chg_5d), 2),
            "Vol Ratio": round(vol_ratio, 2),
            "RSI":       round(rsi, 1),
            "MACD ✓":    "✅" if macd_cross else "❌",
            "BB%":       round(bb_pct, 2),
            "ATR%":      round(atr_pct, 2),
            "EMA20 ✓":   "✅" if above_ema20 else "❌",
            "EMA50 ✓":   "✅" if above_ema50 else "❌",
            "Score":     round(score, 1),
            "Signal":    signal,
        }
    except Exception:
        return None

# ── LIVE SCAN ─────────────────────────────────────────────────────────────────
def run_live_scan(pool: list):
    total     = len(pool)
    results   = []
    log_lines = []

    status_ph   = st.empty()
    prog_ph     = st.progress(0)
    log_ph      = st.empty()
    live_tbl_ph = st.empty()

    status_ph.markdown(
        f"<div style='color:#ff9900;font-size:13px;font-family:JetBrains Mono'>"
        f"🔍 SCANNING {total} SAHAM — HARAP TUNGGU...</div>",
        unsafe_allow_html=True
    )

    for i, code in enumerate(pool):
        prog_ph.progress((i + 1) / total)
        ts = datetime.now(WIB).strftime("%H:%M:%S.%f")[:-3]

        log_lines.append(
            f'<span class="log-scan">[{ts}]</span> → scanning <b>{code}.JK</b>...'
        )
        log_ph.markdown(
            f'<div class="log-box">{"<br>".join(log_lines[-14:])}</div>',
            unsafe_allow_html=True
        )

        result = score_ticker(code)

        if result:
            s, sig = result["Score"], result["Signal"]
            chg, vr = result["Chg 1D %"], result["Vol Ratio"]
            cls  = "log-hot" if "STRONG" in sig else "log-buy" if "BUY" in sig else "log-ok" if "WATCH" in sig else "log-skip"
            icon = "🔥" if "STRONG" in sig else "⚡" if "BUY" in sig else "👀" if "WATCH" in sig else "❄"
            log_lines[-1] = (
                f'<span class="log-scan">[{ts}]</span> '
                f'<span class="{cls}">{icon} {code} &nbsp;|&nbsp; '
                f'Score:{s:.0f} &nbsp;|&nbsp; Chg:{chg:+.2f}% &nbsp;|&nbsp; '
                f'Vol:{vr:.1f}x &nbsp;|&nbsp; {sig}</span>'
            )
            results.append(result)
        else:
            log_lines[-1] = (
                f'<span class="log-scan">[{ts}]</span> '
                f'<span class="log-skip">— {code} &nbsp;|&nbsp; no data / skip</span>'
            )

        log_ph.markdown(
            f'<div class="log-box">{"<br>".join(log_lines[-14:])}</div>',
            unsafe_allow_html=True
        )

        if results and (i % 5 == 0 or i == total - 1):
            df_live = pd.DataFrame(results).sort_values("Score", ascending=False)
            df_live.index = range(1, len(df_live) + 1)
            live_tbl_ph.dataframe(
                df_live[["Ticker", "Price", "Chg 1D %", "Vol Ratio",
                          "RSI", "MACD ✓", "Score", "Signal"]],
                use_container_width=True, height=260
            )

    done_ts = datetime.now(WIB).strftime("%H:%M:%S")
    prog_ph.progress(1.0)
    status_ph.markdown(
        f"<div style='color:#00ff88;font-size:13px;font-family:JetBrains Mono'>"
        f"✅ SCAN SELESAI [{done_ts}] — {len(results)}/{total} saham berhasil</div>",
        unsafe_allow_html=True
    )
    live_tbl_ph.empty()
    log_ph.empty()

    if not results:
        return pd.DataFrame()

    df_out = pd.DataFrame(results).sort_values("Score", ascending=False)
    df_out.reset_index(drop=True, inplace=True)
    df_out.index += 1
    return df_out

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚡ SCANNER CONFIG")
    st.markdown("---")

    universe_choice = st.multiselect(
        "Universe Saham",
        options=list(IDX_UNIVERSE.keys()),
        default=list(IDX_UNIVERSE.keys())[:2],
    )
    selected_pool = sorted(set(
        t for grp in universe_choice for t in IDX_UNIVERSE.get(grp, [])
    )) if universe_choice else ALL_STOCKS

    custom_input = st.text_input("➕ Custom ticker (pisah koma)", placeholder="BKSL, ACES, HRUM")
    if custom_input:
        extras = [x.strip().upper() for x in custom_input.split(",") if x.strip()]
        selected_pool = sorted(set(selected_pool + extras))

    st.markdown(f"**{len(selected_pool)} saham** dalam queue")
    st.markdown("---")

    min_score     = st.slider("Min Score",        0,   100, 40, 5)
    min_vol_ratio = st.slider("Min Volume Ratio", 1.0, 10.0, 1.5, 0.5)
    max_rsi       = st.slider("Max RSI",          50,  85,  72, 1)

    st.markdown("---")

    # ── Telegram Config ───────────────────────────────────────────────────────
    st.markdown("### 📲 TELEGRAM CONFIG")
    tele_token   = st.secrets.get("TELEGRAM_TOKEN", "")
    tele_chat_id = st.secrets.get("TELEGRAM_CHAT_ID", "")
    auto_notify  = st.checkbox("Auto kirim setelah scan", value=False)

    st.markdown("""
    <div style='font-size:10px;color:#405060;line-height:1.8;margin-top:4px'>
    💡 Cara dapat token:<br>
    &nbsp;&nbsp;→ Chat <b>@BotFather</b> → /newbot<br>
    💡 Cara dapat chat_id:<br>
    &nbsp;&nbsp;→ Chat <b>@userinfobot</b>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    rescan_btn = st.button("🔄 RE-SCAN", use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:10px;color:#405060;line-height:1.8'>
    📡 Data: yFinance (delayed)<br>
    ⚡ Auto-scan saat buka app<br>
    ⚠️ Bukan financial advice
    </div>
    """, unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="scanner-header">
  <div class="scanner-title">⚡ IDX RUNNING TRADE SCANNER v3</div>
  <div class="scanner-sub">Auto-scan on startup · Live log · Momentum · Volume · RSI · MACD · EMA · Telegram Notify</div>
</div>
""", unsafe_allow_html=True)

# ── AUTO-SCAN ─────────────────────────────────────────────────────────────────
pool_key  = ",".join(selected_pool)
first_run = "df_result" not in st.session_state

if first_run or rescan_btn or st.session_state.get("pool_key") != pool_key:
    st.session_state.pool_key  = pool_key
    st.session_state.df_result = run_live_scan(selected_pool)
    st.session_state.scan_time = datetime.now(WIB).strftime("%H:%M:%S")

    # Auto notify after scan
    if auto_notify and tele_token and tele_chat_id:
        df_top = st.session_state.df_result.head(10)
        if not df_top.empty:
            msg = build_telegram_message(df_top)
            ok, info = send_telegram(tele_token, tele_chat_id, msg)
            st.session_state.tele_status = info

df = st.session_state.df_result

if df is None or df.empty:
    st.warning("Tidak ada data. Cek koneksi atau kurangi filter.")
    st.stop()

# ── FILTER ────────────────────────────────────────────────────────────────────
df_filtered = df[
    (df["Score"]     >= min_score)     &
    (df["Vol Ratio"] >= min_vol_ratio) &
    (df["RSI"]       <= max_rsi)
].copy()

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
hot   = len(df_filtered[df_filtered["Signal"].str.contains("STRONG")])
buy   = len(df_filtered[df_filtered["Signal"].str.contains("⚡ BUY")])
watch = len(df_filtered[df_filtered["Signal"].str.contains("WATCH")])

c1, c2, c3, c4 = st.columns(4)
for col, label, val, clr in [
    (c1, "🔥 STRONG BUY", hot,   "#ff4444"),
    (c2, "⚡ BUY",        buy,   "#ff9900"),
    (c3, "👀 WATCH",      watch, "#00aaff"),
    (c4, "⏱ LAST SCAN",  st.session_state.get("scan_time","--"), "#00d4ff"),
]:
    with col:
        sz = "22px" if isinstance(val, int) else "15px"
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-label">{label}</div>
          <div class="metric-val" style="color:{clr};font-size:{sz}">{val}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("---")

# ── RESULTS TABLE ─────────────────────────────────────────────────────────────
st.markdown("### 🏆 TOP RUNNING TRADE CANDIDATES")

col_l, col_r = st.columns([3, 1])
with col_l:
    top_n = st.selectbox("Tampilkan top", [10, 20, 30, 50], index=0)
with col_r:
    sig_filter = st.selectbox("Filter signal", ["Semua", "🔥 STRONG BUY", "⚡ BUY", "👀 WATCH"])

df_show = df_filtered.copy()
if sig_filter != "Semua":
    kw = sig_filter.split(" ", 1)[-1]
    df_show = df_show[df_show["Signal"].str.contains(kw)]
df_show = df_show.head(top_n).copy()

if df_show.empty:
    st.info("Tidak ada yang lolos filter. Longgarkan parameter di sidebar.")
else:
    def c_chg(v):
        if isinstance(v, (int, float)):
            return f"color:{'#00ff88' if v>0 else '#ff4444' if v<0 else '#aaa'};font-weight:bold"
        return ""
    def c_score(v):
        if isinstance(v, (int, float)):
            if v >= 70:   return "color:#ff4444;font-weight:bold"
            elif v >= 45: return "color:#ff9900;font-weight:bold"
            return "color:#00aaff"
        return ""
    def c_vol(v):
        if isinstance(v, (int, float)):
            if v >= 3.0:   return "color:#ff4444;font-weight:bold"
            elif v >= 2.0: return "color:#ff9900;font-weight:bold"
        return ""

    styled = (
        df_show.style
        .map(c_chg,   subset=["Chg 1D %", "Chg 3D %", "Chg 5D %"])
        .map(c_score, subset=["Score"])
        .map(c_vol,   subset=["Vol Ratio"])
        .format({
            "Price":     "{:,.0f}",
            "Chg 1D %":  "{:+.2f}%",
            "Chg 3D %":  "{:+.2f}%",
            "Chg 5D %":  "{:+.2f}%",
            "Vol Ratio": "{:.2f}x",
            "RSI":       "{:.1f}",
            "BB%":       "{:.2f}",
            "ATR%":      "{:.2f}%",
            "Score":     "{:.1f}",
        })
    )
    st.dataframe(styled, use_container_width=True, height=420)

st.markdown("---")

# ── TELEGRAM SECTION ──────────────────────────────────────────────────────────
st.markdown("### 📲 TELEGRAM NOTIFICATION")

df_top10  = df_filtered.head(10).copy()
tele_msg  = build_telegram_message(df_top10) if not df_top10.empty else ""

col_prev, col_send = st.columns([3, 1])

with col_prev:
    st.markdown("**📋 Preview Pesan Telegram (Top 10)**")
    if tele_msg:
        # Render preview styled like Telegram dark
        st.markdown(f"""
        <div class="tele-header">
          <span>🤖</span>
          <span style='color:#00d4ff;font-weight:700'>IDX Running Trade Bot</span>
          <span style='margin-left:auto;font-size:10px'>{datetime.now(WIB).strftime("%H:%M")}</span>
        </div>
        <div class="tele-preview">{tele_msg.replace("*","").replace("`","").replace("_","")}</div>
        """, unsafe_allow_html=True)
    else:
        st.info("Tidak ada kandidat untuk dikirim.")

with col_send:
    st.markdown("**📤 Kirim Sekarang**")

    if "tele_status" in st.session_state:
        st.markdown(f"""
        <div style='font-size:12px;padding:8px;background:#0d1a26;border:1px solid #1e3a5f;border-radius:4px;margin-bottom:8px'>
        {st.session_state.tele_status}
        </div>""", unsafe_allow_html=True)

    tele_ok = bool(tele_token and tele_chat_id)

    if not tele_ok:
        st.markdown("""
        <div style='font-size:11px;color:#607080;padding:8px;background:#0d1a26;
                    border:1px solid #1e3a5f;border-radius:4px'>
        ⚠️ Isi Bot Token &<br>Chat ID di sidebar<br>untuk aktifkan notif
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="btn-tele">', unsafe_allow_html=True)
    send_btn = st.button(
        "📲 KIRIM KE TELEGRAM",
        disabled=not tele_ok or df_top10.empty,
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if send_btn and tele_ok and not df_top10.empty:
        with st.spinner("Mengirim..."):
            ok, info = send_telegram(tele_token, tele_chat_id, tele_msg)
            st.session_state.tele_status = info
            st.rerun()

    # Copy raw message
    if tele_msg:
        with st.expander("📋 Raw text"):
            st.code(tele_msg, language="markdown")

# ── DETAIL VIEW ───────────────────────────────────────────────────────────────
if not df_show.empty:
    st.markdown("---")
    st.markdown("### 🔬 DETAIL TICKER")
    detail_ticker = st.selectbox("Pilih saham", df_show["Ticker"].tolist())

    if detail_ticker:
        row = df_show[df_show["Ticker"] == detail_ticker].iloc[0]
        col1, col2 = st.columns([1, 2])
        score_color = "#ff4444" if row["Score"] >= 70 else "#ff9900" if row["Score"] >= 45 else "#00aaff"

        with col1:
            st.markdown(f"""
            <div class="metric-card">
              <div style='font-size:22px;font-weight:700;color:#ff6600'>{row['Ticker']}.JK</div>
              <div style='font-size:26px;font-weight:700;color:#00d4ff'>Rp {row['Price']:,.0f}</div>
              <div style='margin-top:10px;font-size:15px'>{row['Signal']}</div>
              <div style='margin-top:6px;font-size:22px;font-weight:700;color:{score_color}'>Score: {row['Score']:.1f}</div>
            </div>
            <div class="metric-card" style='margin-top:8px'>
              <div class="metric-label">RSI (14)</div>
              <div class="metric-val">{row['RSI']}</div>
            </div>
            <div class="metric-card" style='margin-top:8px'>
              <div class="metric-label">Volume Ratio</div>
              <div class="metric-val" style="color:#ff9900">{row['Vol Ratio']:.2f}x</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-label">PERFORMANCE</div>
              <table style='width:100%;font-size:13px;margin-top:8px'>
                <tr><td style='color:#607080;padding:4px 0'>1 Day</td><td>{color_change(row['Chg 1D %'])}</td></tr>
                <tr><td style='color:#607080;padding:4px 0'>3 Days</td><td>{color_change(row['Chg 3D %'])}</td></tr>
                <tr><td style='color:#607080;padding:4px 0'>5 Days</td><td>{color_change(row['Chg 5D %'])}</td></tr>
              </table>
            </div>
            <div class="metric-card" style='margin-top:8px'>
              <div class="metric-label">TECHNICAL CHECKLIST</div>
              <table style='width:100%;font-size:12px;margin-top:8px'>
                <tr><td style='color:#607080;padding:3px 0'>MACD Bullish</td><td>{row['MACD ✓']}</td></tr>
                <tr><td style='color:#607080;padding:3px 0'>Above EMA20</td><td>{row['EMA20 ✓']}</td></tr>
                <tr><td style='color:#607080;padding:3px 0'>Above EMA50</td><td>{row['EMA50 ✓']}</td></tr>
                <tr><td style='color:#607080;padding:3px 0'>Bollinger %</td><td style='color:#00d4ff'>{row['BB%']:.2f} {"✅" if row['BB%']<0.8 else "⚠️"}</td></tr>
                <tr><td style='color:#607080;padding:3px 0'>ATR%</td><td style='color:#00aaff'>{row['ATR%']:.2f}%</td></tr>
              </table>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        with st.spinner(f"Loading chart {detail_ticker}..."):
            df_c = yf.download(yf_ticker(detail_ticker), period="3mo",
                               interval="1d", progress=False, auto_adjust=True)
            if df_c is not None and not df_c.empty:
                cl  = df_c["Close"].squeeze()
                e20 = ta.trend.EMAIndicator(cl, 20).ema_indicator()
                e50 = ta.trend.EMAIndicator(cl, 50).ema_indicator()
                st.line_chart(
                    pd.DataFrame({"Price": cl.values, "EMA20": e20.values, "EMA50": e50.values},
                                 index=df_c.index),
                    height=220, use_container_width=True
                )
                st.bar_chart(
                    pd.DataFrame({"Volume": df_c["Volume"].squeeze().values}, index=df_c.index),
                    height=90, use_container_width=True
                )

# ── LEGEND ────────────────────────────────────────────────────────────────────
with st.expander("📖 Scoring & Metodologi"):
    st.markdown("""
    | Komponen | Max | Keterangan |
    |----------|-----|-----------|
    | Chg 1D % | 20 | Momentum harian |
    | Chg 3D % | 10 | Momentum 3 hari |
    | Chg 5D % | 5  | Trend 1 minggu |
    | Volume Surge | 25 | Vol hari ini ÷ avg 20 hari |
    | RSI 40–65 | 15 | Running zone |
    | MACD bullish | 15 | Cross + histogram positif |
    | EMA Alignment | 10 | Di atas EMA20 + EMA50 |
    | Bollinger < 0.8 | 5 | Ada ruang naik |

    **Signal**: 🔥 ≥70+vol≥2x · ⚡ ≥55 · 👀 ≥40 · ❄ <40

    > ⚠️ Bukan financial advice. Selalu pakai manajemen risiko.
    """)

st.markdown("""
<div style='text-align:center;color:#304050;font-size:10px;margin-top:20px'>
IDX RUNNING TRADE SCANNER v3.0 | Auto-scan | Telegram Notify | yFinance data
</div>
""", unsafe_allow_html=True)
