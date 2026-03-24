"""
Cell Tower Detective - Công cụ Tra cứu Vị trí Trạm Phát Sóng
Hỗ trợ: MCC, MNC, LAC/TAC, Cell ID, SAI
APIs: OpenCelliD / Mozilla Location Services / Unwired Labs
"""

import time
import json
from datetime import datetime
import requests
import folium
from streamlit_folium import st_folium
import streamlit as st
import streamlit.components.v1 as components

# ─────────────────────────────────────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cell Tower Detective - Tra cứu Trạm Phát Sóng",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Session State
# ─────────────────────────────────────────────────────────────────────────────
for key, default in [
    ("history", []),
    ("dark_mode", True),
    ("result", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg, #0a0f1e 0%, #0f1729 50%, #0a0f1e 100%); color: #e2e8f0; }

.cell-hero {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 20px; padding: 28px; text-align: center; margin-bottom: 20px;
    box-shadow: 0 0 40px rgba(139, 92, 246, 0.1);
    position: relative; overflow: hidden;
}
.cell-hero::before {
    content: ''; position: absolute; top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(139,92,246,0.06) 0%, transparent 70%);
}
.cell-id-main { font-size: 1.5rem; font-weight: 700; color: #a78bfa; font-family: 'JetBrains Mono', monospace; }
.cell-location { font-size: 1rem; color: #94a3b8; margin-top: 6px; }
.cell-icon { font-size: 2.5rem; margin-bottom: 8px; }
.accuracy-badge {
    display: inline-block; background: rgba(139,92,246,0.15);
    border: 1px solid rgba(139,92,246,0.4); border-radius: 999px;
    padding: 3px 12px; font-size: 12px; font-weight: 600; color: #a78bfa; margin-top: 8px;
}

.info-card {
    background: rgba(15, 23, 42, 0.9);
    border: 1px solid rgba(51, 65, 85, 0.8);
    border-radius: 14px; padding: 20px; margin-bottom: 14px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.card-title {
    font-size: 11px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1.5px; color: #a78bfa; margin-bottom: 14px;
}
.data-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 7px 0; border-bottom: 1px solid rgba(51,65,85,0.4);
}
.data-row:last-child { border-bottom: none; }
.data-label { color: #94a3b8; font-size: 13px; font-weight: 500; }
.data-value { color: #e2e8f0; font-size: 13px; font-weight: 600; text-align: right;
    font-family: 'JetBrains Mono', monospace; }

.param-grid {
    display: grid; grid-template-columns: 1fr 1fr 1fr 1fr;
    gap: 12px; margin-bottom: 20px;
}
.param-box {
    background: rgba(139, 92, 246, 0.08);
    border: 1px solid rgba(139, 92, 246, 0.25);
    border-radius: 12px; padding: 14px; text-align: center;
}
.param-label { font-size: 10px; font-weight: 700; color: #7c3aed; text-transform: uppercase; letter-spacing: 1px; }
.param-value { font-size: 1.2rem; font-weight: 700; color: #a78bfa; font-family: 'JetBrains Mono', monospace; margin-top: 4px; }

.badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 12px; border-radius: 999px; font-size: 12px; font-weight: 600; margin: 3px;
}
.badge-gsm    { background: rgba(59,130,246,0.15); color: #60a5fa; border: 1px solid rgba(59,130,246,0.3); }
.badge-umts   { background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(16,185,129,0.3); }
.badge-lte    { background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); }
.badge-nr     { background: rgba(239,68,68,0.15);  color: #f87171; border: 1px solid rgba(239,68,68,0.3); }
.badge-ok     { background: rgba(34,197,94,0.15);  color: #4ade80; border: 1px solid rgba(34,197,94,0.3); }
.badge-fail   { background: rgba(239,68,68,0.15);  color: #f87171; border: 1px solid rgba(239,68,68,0.3); }

[data-testid="stSidebar"] {
    background: rgba(10, 15, 30, 0.98) !important;
    border-right: 1px solid rgba(51, 65, 85, 0.8);
}
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #6d28d9) !important;
    color: white !important; border: none !important; border-radius: 10px !important;
    font-weight: 700 !important; font-size: 15px !important; padding: 12px 28px !important;
    box-shadow: 0 4px 15px rgba(124,58,237,0.3) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 20px rgba(124,58,237,0.45) !important; }
.section-divider { border: none; border-top: 1px solid rgba(51,65,85,0.6); margin: 22px 0; }

.history-item { background: rgba(15,23,42,0.7); border: 1px solid rgba(51,65,85,0.6);
    border-radius: 10px; padding: 10px 14px; margin-bottom: 8px; font-size: 12px; }
.history-cid  { color: #a78bfa; font-weight: 600; font-family: 'JetBrains Mono', monospace; }
.history-loc  { color: #94a3b8; font-size: 11px; }
.history-time { color: #475569; font-size: 10px; float: right; }

.signal-meter { height: 6px; background: rgba(51,65,85,0.4); border-radius: 3px; overflow: hidden; }
.signal-fill  { height: 100%; border-radius: 3px; transition: width 0.5s ease; }

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #0a0f1e; }
::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MCC/MNC Database (Vietnam)
# ─────────────────────────────────────────────────────────────────────────────
MCC_MNC_VN = {
    ("452", "01"): {"name": "Viettel", "flag": "🟥", "color": "#e53e3e"},
    ("452", "02"): {"name": "Vinaphone (VNPT)", "flag": "🟦", "color": "#3182ce"},
    ("452", "03"): {"name": "MobiFone", "flag": "🟩", "color": "#38a169"},
    ("452", "04"): {"name": "Gmobile", "flag": "🟧", "color": "#dd6b20"},
    ("452", "05"): {"name": "Reddi (Vietnamobile)", "flag": "🟪", "color": "#805ad5"},
    ("452", "06"): {"name": "Indochina Telecom", "flag": "⬜", "color": "#718096"},
    ("452", "07"): {"name": "GTel Mobile", "flag": "🟫", "color": "#744210"},
    ("452", "08"): {"name": "Vinaphone 4G", "flag": "🟦", "color": "#3182ce"},
}

RADIO_TYPES = {
    "GSM": "2G GSM",
    "UMTS": "3G UMTS/WCDMA",
    "LTE": "4G LTE",
    "NR": "5G NR",
    "CDMA": "CDMA/EVDO",
    "HSPA": "3G HSPA+",
}

RADIO_BADGES = {
    "GSM": "badge-gsm", "UMTS": "badge-umts", "CDMA": "badge-umts",
    "LTE": "badge-lte", "NR": "badge-nr", "HSPA": "badge-umts",
}

# ─────────────────────────────────────────────────────────────────────────────
# API Functions
# ─────────────────────────────────────────────────────────────────────────────
def lookup_opencellid(mcc: int, mnc: int, lac: int, cellid: int, radio: str = "LTE") -> dict:
    """OpenCelliD API - 1000 req/day miễn phí sau đăng ký"""
    # Dùng community API không cần key (giới hạn nhẹ hơn)
    url = "https://opencellid.org/cell/get"
    params = {
        "mcc": mcc, "mnc": mnc, "lac": lac, "cellid": cellid,
        "radio": radio.upper(), "format": "json",
        # Token miễn phí public (community token)
        "token": "pk.4c896f8e7d4b2a6e2d9b1c3f8a5d7e9b",
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if "lat" in data and "lon" in data:
                return {"status": "success", "source": "OpenCelliD", **data}
    except Exception:
        pass
    return {"status": "fail"}


def lookup_mozilla(mcc: int, mnc: int, lac: int, cellid: int, radio: str = "LTE") -> dict:
    """Mozilla Location Services - miễn phí, không cần key"""
    url = "https://location.services.mozilla.com/v1/geolocate?key=test"
    payload = {
        "cellTowers": [{
            "radioType": radio.lower() if radio.lower() in ["gsm", "cdma", "lte", "nr"] else "lte",
            "mobileCountryCode": mcc,
            "mobileNetworkCode": mnc,
            "locationAreaCode": lac,
            "cellId": cellid,
        }]
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            data = r.json()
            loc = data.get("location", {})
            acc = data.get("accuracy")
            if loc.get("lat") and loc.get("lng"):
                return {
                    "status": "success",
                    "source": "Mozilla Location Services",
                    "lat": loc["lat"],
                    "lon": loc["lng"],
                    "accuracy": acc,
                }
    except Exception:
        pass
    return {"status": "fail"}


def lookup_combined(mcc: int, mnc: int, lac: int, cellid: int, radio: str = "LTE") -> dict:
    """Thử OpenCelliD trước, nếu fail thì dùng Mozilla"""
    # Try Mozilla first (more reliable without API key)
    result = lookup_mozilla(mcc, mnc, lac, cellid, radio)
    if result["status"] == "success":
        return result

    # Try OpenCelliD community endpoint
    result = lookup_opencellid(mcc, mnc, lac, cellid, radio)
    if result["status"] == "success":
        return result

    return {"status": "fail", "message": "Không tìm thấy tower với thông số này. Hãy kiểm tra lại MCC/MNC/LAC/CID."}


def get_operator_info(mcc: str, mnc: str) -> dict:
    """Trả về thông tin nhà mạng từ MCC+MNC"""
    return MCC_MNC_VN.get((str(mcc), str(mnc).zfill(2)), {
        "name": f"MCC:{mcc} / MNC:{mnc}",
        "flag": "📶", "color": "#718096"
    })


def sai_to_params(sai: str) -> tuple[int, int, int, int] | None:
    """Parse SAI format: MCC-MNC-LAC-SAC or MCC/MNC/LAC/SAC"""
    sai = sai.strip().replace("/", "-").replace(".", "-").replace(" ", "-")
    parts = sai.split("-")
    if len(parts) == 4:
        try:
            return int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
        except ValueError:
            pass
    return None


def add_to_history(mcc, mnc, lac, cellid, radio, result):
    entry = {
        "key": f"{mcc}-{mnc}-{lac}-{cellid}",
        "radio": radio,
        "lat": result.get("lat"),
        "lon": result.get("lon"),
        "accuracy": result.get("accuracy"),
        "source": result.get("source", "N/A"),
        "timestamp": datetime.now().strftime("%H:%M:%S"),
    }
    if st.session_state.history and st.session_state.history[0]["key"] == entry["key"]:
        return
    st.session_state.history.insert(0, entry)
    st.session_state.history = st.session_state.history[:10]


def build_cell_map(lat: float, lon: float, accuracy: float | None, popup_text: str, cell_label: str = "") -> folium.Map:
    """Bản đồ tối với vùng phủ sóng cell"""
    m = folium.Map(location=[lat, lon], zoom_start=15, tiles="CartoDB dark_matter")

    # Tower marker
    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_text, max_width=320),
        tooltip=f"📡 {cell_label}",
        icon=folium.Icon(color="purple", icon="signal", prefix="fa"),
    ).add_to(m)

    # Coverage radius (based on accuracy or default ~500m for cell)
    radius_m = accuracy if accuracy else 500
    folium.Circle(
        location=[lat, lon],
        radius=radius_m,
        color="#a78bfa",
        fill=True,
        fill_color="#a78bfa",
        fill_opacity=0.08,
        weight=2,
        dash_array="8",
    ).add_to(m)

    # Inner dot
    folium.CircleMarker(
        location=[lat, lon],
        radius=8,
        color="#7c3aed",
        fill=True, fill_color="#a78bfa", fill_opacity=0.6, weight=2,
    ).add_to(m)

    return m


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# 📡 Cell Tower Detective")
    st.markdown("---")

    st.markdown("### 🌍 MCC Việt Nam (452)")
    for (mcc, mnc), info in MCC_MNC_VN.items():
        st.markdown(f"- **{mnc}** — {info['flag']} {info['name']}")

    st.markdown("---")
    st.markdown("### ℹ️ Giải thích tham số")
    st.markdown("""
| Tham số | Ý nghĩa |
|---|---|
| **MCC** | Mã quốc gia (VN=452) |
| **MNC** | Mã nhà mạng |
| **LAC/TAC** | Mã vùng định vị |
| **Cell ID** | Mã định danh trạm |
| **SAI** | MCC-MNC-LAC-SAC |
| **Radio** | Công nghệ (2G/3G/4G/5G) |
    """)

    st.markdown("---")
    st.markdown("### 🕒 Lịch Sử Tra Cứu")
    if not st.session_state.history:
        st.caption("Chưa có tra cứu nào.")
    else:
        with st.expander(f"Lịch sử ({len(st.session_state.history)} mục)", expanded=True):
            for entry in st.session_state.history:
                st.markdown(f"""
                <div class="history-item">
                    <span class="history-time">{entry['timestamp']}</span>
                    <div class="history-cid">{entry['key']}</div>
                    <div class="history-loc">📡 {entry['radio']} | {entry['source']}</div>
                </div>
                """, unsafe_allow_html=True)
            if st.button("🗑️ Xóa lịch sử", use_container_width=True):
                st.session_state.history = []
                st.rerun()

    st.markdown("---")
    st.caption("Cell Tower Detective v1.0 · Mozilla + OpenCelliD")

# ─────────────────────────────────────────────────────────────────────────────
# Main UI
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("# 📡 Cell Tower Detective — Tra Cứu Vị Trí Trạm Phát Sóng")
st.markdown("Tra cứu vị trí trạm BTS/eNodeB/gNodeB theo mã **MCC • MNC • LAC/TAC • Cell ID**. Hỗ trợ 2G GSM, 3G UMTS, 4G LTE, 5G NR.")
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ── Input Tabs ────────────────────────────────────────────────────────────────
tab_manual, tab_sai = st.tabs(["🔢 Nhập Thủ Công (MCC/MNC/LAC/CID)", "🔤 Nhập SAI (MCC-MNC-LAC-SAC)"])

with tab_manual:
    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 3, 2])
    with col1:
        mcc_in = st.number_input("MCC", min_value=1, max_value=999, value=452, step=1, help="Việt Nam = 452")
    with col2:
        mnc_in = st.number_input("MNC", min_value=0, max_value=999, value=1, step=1, help="Viettel=01, Vinaphone=02, Mobifone=03")
    with col3:
        lac_in = st.number_input("LAC / TAC", min_value=0, max_value=65535, value=20505, step=1, help="Location Area Code (2G/3G) hoặc Tracking Area Code (4G/5G)")
    with col4:
        cid_in = st.number_input("Cell ID / eNB ID", min_value=0, max_value=268435455, value=12345, step=1, help="Cell Identity — có thể lên tới 28-bit với 4G LTE")
    with col5:
        radio_in = st.selectbox("Công nghệ (Radio)", list(RADIO_TYPES.keys()), index=2)

    lookup_btn = st.button("📡 TRA CỨU TRẠM PHÁT SÓNG", use_container_width=True, key="btn_manual")
    trigger_manual = lookup_btn
    trigger_mcc, trigger_mnc, trigger_lac, trigger_cid, trigger_radio = mcc_in, mnc_in, lac_in, int(cid_in), radio_in

with tab_sai:
    st.markdown("**SAI = Service Area Identity = MCC-MNC-LAC-SAC** (ngăn cách bởi dấu `-` hoặc `/`)")
    sai_col, _ = st.columns([3, 1])
    with sai_col:
        sai_input = st.text_input(
            "Nhập SAI",
            placeholder="Ví dụ: 452-01-20505-12345  hoặc  452/01/20505/12345",
            label_visibility="collapsed"
        )
    radio_sai = st.selectbox("Công nghệ (Radio)", list(RADIO_TYPES.keys()), index=2, key="radio_sai")
    sai_btn = st.button("📡 TRA CỨU QUA SAI", use_container_width=True, key="btn_sai")

    trigger_sai = None
    if sai_btn and sai_input.strip():
        parsed = sai_to_params(sai_input)
        if parsed:
            trigger_mcc, trigger_mnc, trigger_lac, trigger_cid, trigger_radio = *parsed, radio_sai
            trigger_manual = True
        else:
            st.error("❌ Định dạng SAI không hợp lệ. Ví dụ đúng: 452-01-20505-12345")
            trigger_manual = False
    elif sai_btn:
        st.warning("⚠️ Vui lòng nhập SAI trước khi tra cứu.")
        trigger_manual = False

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Processing
# ─────────────────────────────────────────────────────────────────────────────
if trigger_manual:
    mcc  = int(trigger_mcc)
    mnc  = int(trigger_mnc)
    lac  = int(trigger_lac)
    cid  = int(trigger_cid)
    radio = trigger_radio

    operator = get_operator_info(mcc, mnc)
    radio_label = RADIO_TYPES.get(radio, radio)
    radio_badge_cls = RADIO_BADGES.get(radio, "badge-gsm")

    with st.spinner(f"📡 Đang tra cứu {radio} tower {mcc}-{mnc}-{lac}-{cid}..."):
        result = lookup_combined(mcc, mnc, lac, cid, radio)

    st.session_state.result = {**result, "mcc": mcc, "mnc": mnc, "lac": lac, "cid": cid, "radio": radio}

    if result["status"] == "success":
        add_to_history(mcc, mnc, lac, cid, radio, result)
        lat = result.get("lat")
        lon = result.get("lon")
        acc = result.get("accuracy")
        source = result.get("source", "N/A")

        # ── Hero Banner ──────────────────────────────────────────────────────
        radio_badge = f'<span class="badge {radio_badge_cls}">{radio_label}</span>'
        acc_text = f"~{acc:.0f}m" if acc else "Ước tính"
        st.markdown(f"""
        <div class="cell-hero">
            <div class="cell-icon">📡</div>
            <div class="cell-id-main">MCC:{mcc} · MNC:{mnc:02d} · LAC:{lac} · CID:{cid}</div>
            <div class="cell-location">
                {operator.get('flag','')} {operator.get('name','')} &nbsp;|&nbsp;
                Tọa độ: {lat:.6f}, {lon:.6f}
            </div>
            <div style="margin-top:10px;">
                {radio_badge}
                <span class="accuracy-badge">📍 Bán kính: {acc_text}</span>
                <span class="accuracy-badge">🗃️ {source}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Param Grid ───────────────────────────────────────────────────────
        st.markdown(f"""
        <div class="param-grid">
            <div class="param-box"><div class="param-label">MCC</div><div class="param-value">{mcc}</div></div>
            <div class="param-box"><div class="param-label">MNC</div><div class="param-value">{mnc:02d}</div></div>
            <div class="param-box"><div class="param-label">LAC / TAC</div><div class="param-value">{lac}</div></div>
            <div class="param-box"><div class="param-label">Cell ID</div><div class="param-value">{cid}</div></div>
        </div>
        """, unsafe_allow_html=True)

        # ── Info Cards ───────────────────────────────────────────────────────
        col_a, col_b = st.columns(2, gap="medium")

        with col_a:
            st.markdown(f"""
            <div class="info-card">
                <div class="card-title">📶 Thông Tin Trạm & Mạng</div>
                <div class="data-row"><span class="data-label">Nhà mạng</span>
                    <span class="data-value">{operator.get('flag','')} {operator.get('name','N/A')}</span></div>
                <div class="data-row"><span class="data-label">Công nghệ Radio</span>
                    <span class="data-value">{radio_label}</span></div>
                <div class="data-row"><span class="data-label">MCC / MNC</span>
                    <span class="data-value">{mcc} / {mnc:02d}</span></div>
                <div class="data-row"><span class="data-label">LAC / TAC</span>
                    <span class="data-value">{lac} (0x{lac:04X})</span></div>
                <div class="data-row"><span class="data-label">Cell ID</span>
                    <span class="data-value">{cid} (0x{cid:X})</span></div>
                <div class="data-row"><span class="data-label">SAI</span>
                    <span class="data-value">{mcc}-{mnc:02d}-{lac}-{cid}</span></div>
            </div>
            """, unsafe_allow_html=True)

        with col_b:
            maps_url = f"https://www.google.com/maps/search/?api=1&query={lat:.6f},{lon:.6f}"
            osm_url  = f"https://www.openstreetmap.org/?mlat={lat:.6f}&mlon={lon:.6f}&zoom=15"
            st.markdown(f"""
            <div class="info-card">
                <div class="card-title">📍 Tọa Độ & Độ Chính Xác</div>
                <div class="data-row"><span class="data-label">Vĩ độ (Latitude)</span>
                    <span class="data-value">{lat:.6f}°</span></div>
                <div class="data-row"><span class="data-label">Kinh độ (Longitude)</span>
                    <span class="data-value">{lon:.6f}°</span></div>
                <div class="data-row"><span class="data-label">Bán kính sai số</span>
                    <span class="data-value">~{acc:.0f} m</span></div>
                <div class="data-row"><span class="data-label">Nguồn dữ liệu</span>
                    <span class="data-value">{source}</span></div>
                <div class="data-row"><span class="data-label">Thời gian tra cứu</span>
                    <span class="data-value">{datetime.now().strftime('%H:%M:%S')}</span></div>
            </div>
            """, unsafe_allow_html=True)

            # Map buttons
            st.markdown(
                f'<a href="{maps_url}" target="_blank" style="display:block;text-align:center;padding:10px;'
                f'background:linear-gradient(135deg,#7c3aed,#6d28d9);color:#fff;font-weight:700;'
                f'border-radius:10px;text-decoration:none;margin-bottom:8px;">'
                f'🌍 Mở Google Maps ({lat:.4f}, {lon:.4f})</a>',
                unsafe_allow_html=True)
            st.markdown(
                f'<a href="{osm_url}" target="_blank" style="display:block;text-align:center;padding:10px;'
                f'background:linear-gradient(135deg,#4a5568,#2d3748);color:#fff;font-weight:700;'
                f'border-radius:10px;text-decoration:none;">'
                f'🗺️ Mở OpenStreetMap</a>',
                unsafe_allow_html=True)

        # ── Map ───────────────────────────────────────────────────────────────
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        st.markdown("### 🗺️ Bản Đồ Vị Trí Trạm Phát Sóng")
        st.caption(f"Vòng tròn tím = vùng phủ sóng ước tính (bán kính ~{acc:.0f}m)" if acc else "Vòng tròn tím = vùng phủ sóng ước tính (~500m)")

        popup_html = (
            f"<b>Tower:</b> MCC:{mcc} MNC:{mnc:02d}<br>"
            f"<b>LAC/TAC:</b> {lac} | <b>CID:</b> {cid}<br>"
            f"<b>Radio:</b> {radio_label}<br>"
            f"<b>Nhà mạng:</b> {operator.get('name','N/A')}<br>"
            f"<b>Tọa độ:</b> {lat:.6f}, {lon:.6f}<br>"
            f"<b>Bán kính:</b> ~{acc:.0f}m | <b>Nguồn:</b> {source}"
        )
        m = build_cell_map(lat, lon, acc, popup_html, f"{mcc}-{mnc:02d}-{lac}-{cid}")
        st_folium(m, width="100%", height=500, returned_objects=[])

    else:
        st.error(f"❌ {result.get('message', 'Không tìm thấy trạm phát sóng với thông số này.')}")
        st.info("""
        💡 **Nguyên nhân có thể:**
        - LAC/CID không tồn tại trong cơ sở dữ liệu cộng đồng
        - Trạm này chưa từng được đóng góp vào database OpenCelliD
        - MCC/MNC không khớp với Radio type đã chọn
        
        👉 **Thử thay đổi Radio type** (GSM/UMTS/LTE) hoặc kiểm tra lại MCC/MNC.
        """)
        st.markdown(f"""
        **Tham số đã nhập:**
        - MCC: `{mcc}` | MNC: `{mnc:02d}` | LAC: `{lac}` | CID: `{cid}`
        - Radio: `{radio_label}`
        - SAI: `{mcc}-{mnc:02d}-{lac}-{cid}`
        """)
