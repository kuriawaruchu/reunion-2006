import pandas as pd
import streamlit as st

st.set_page_config(page_title="Class of 2006 Reunion", page_icon="🥂", layout="centered")

# ---- Settings ----
GOAL = 150
PER_PERSON = 4000
try:
    SHEET_URL = st.secrets["SHEET_URL"]
except Exception:
    SHEET_URL = "https://docs.google.com/spreadsheets/d/1W-lEoDnSvkkfysm0wbxO0QRkIyyJ5h7NMHvRbOHpbrA/edit?usp=sharing"

COLORS = {"W": "#4A0404", "X": "#800020", "Y": "#722F37", "Z": "#8E3A59"}
FALLBACK = "#C9A0A8"
RED, OXBLOOD, MULBERRY, BERRY = "#D62839", "#4A0404", "#8E3A59", "#C9A0A8"


# ---- Data (refreshes every 5 minutes) ----
@st.cache_data(ttl=300)
def load(url: str) -> pd.DataFrame:
    sheet_id = url.split("/d/")[1].split("/")[0]
    gid = url.split("gid=")[1].split("&")[0].split("#")[0] if "gid=" in url else "0"
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    df = pd.read_csv(csv_url).rename(columns={"Class Stream": "Stream"})
    if "Status" in df.columns:                      # optional: count only confirmed payments
        df = df[df["Status"].astype(str).str.strip().str.lower() == "paid"]
    df = df[["Stream", "Amount"]].dropna()
    df["Stream"] = df["Stream"].astype(str).str.strip().str.upper()
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0).astype(int)
    return df


df = load(SHEET_URL)
paid = len(df)
raised = int(df["Amount"].sum())
pct = min(paid / GOAL, 1) * 100

summary = (df.groupby("Stream")
             .agg(People=("Amount", "size"), Total=("Amount", "sum"))
             .sort_values("People", ascending=False)
             .reset_index())
order = [s for s, n in zip(summary["Stream"], summary["People"]) for _ in range(n)]

# ---- Styling ----
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,800&display=swap');
.block-container {{ max-width: 760px; padding-top: 1.5rem; }}
header[data-testid="stHeader"] {{ background: transparent; }}
.band {{ background:{OXBLOOD}; color:#FBF3F4; padding:32px 26px 26px; border-radius:18px; margin-bottom:26px; }}
.band h1 {{ font-family:Fraunces,Georgia,serif; font-weight:800; font-size:clamp(2rem,7vw,3.4rem);
           line-height:1.05; margin:0 0 10px; color:#FBF3F4; padding:0; }}
.band p {{ color:{BERRY}; margin:0 0 18px; font-size:1.05rem; }}
.band b {{ color:#FBF3F4; }}
.prog {{ height:14px; border-radius:99px; background:rgba(201,160,168,.3); overflow:hidden; }}
.prog i {{ display:block; height:100%; width:{pct}%; background:{RED}; border-radius:99px; }}
.progl {{ display:flex; justify-content:space-between; margin-top:7px; font-size:.9rem; color:{BERRY}; }}
.seats {{ display:grid; grid-template-columns:repeat(10,1fr); gap:8px; margin:6px 0 28px; }}
.seat {{ aspect-ratio:1; border-radius:50%; border:2px dashed {BERRY}; }}
.seat.on {{ border:0; }}
.row {{ display:grid; grid-template-columns:5.5rem 1fr; gap:4px 14px; align-items:center;
        background:#fff; border:1px solid #E6CDD2; border-radius:14px; padding:12px 16px; margin-bottom:10px; }}
.nm {{ font-family:Fraunces,Georgia,serif; font-weight:600; font-size:1.1rem; color:{OXBLOOD}; }}
.bar {{ height:13px; border-radius:99px; background:#EEDDE0; overflow:hidden; }}
.bar i {{ display:block; height:100%; border-radius:99px; }}
.meta {{ grid-column:2; font-size:.92rem; color:#6E4B55; }}
.facts {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin:24px 0; }}
.fact {{ background:#fff; border:1px solid #E6CDD2; border-radius:14px; padding:16px; }}
.fact strong {{ display:block; font-family:Fraunces,Georgia,serif; font-weight:800; font-size:1.7rem; color:{OXBLOOD}; }}
.fact.hot strong {{ color:{RED}; }}
.fact span {{ color:#6E4B55; font-size:.92rem; }}
.cta {{ font-family:Fraunces,Georgia,serif; font-weight:600; font-size:1.25rem; color:{OXBLOOD}; }}
h2.sec {{ font-family:Fraunces,Georgia,serif; font-weight:600; color:{OXBLOOD}; font-size:1.5rem; margin:0 0 10px; padding:0; }}
</style>
""", unsafe_allow_html=True)

# ---- Header with progress ----
st.markdown(f"""
<div class="band">
<h1>Class of 2006</h1>
<h2>20 Year Reunion</h1> 
<p><b>{paid} of {GOAL}</b> classmates will be attending.</p>
<div class="prog"><i></i></div>
<div class="progl"><span>{paid} claimed</span><span>Goal: {GOAL} attendees</span></div>
</div>
""", unsafe_allow_html=True)

# ---- Seat grid ----
seats = "".join(
    f'<div class="seat on" style="background:{COLORS.get(order[i], FALLBACK)}" title="Stream {order[i]}"></div>'
    if i < paid else '<div class="seat"></div>'
    for i in range(max(GOAL, paid))
)
st.markdown(f'<h2 class="sec">Every coloured circle is a classmate you will meet</h2><div class="seats">{seats}</div>',
            unsafe_allow_html=True)

# ---- Stream rows ----
top = max(summary["People"].max(), 1) if len(summary) else 1
rows = "".join(
    f'<div class="row"><span class="nm">Stream {r.Stream}</span>'
    f'<span class="bar"><i style="width:{r.People / top * 100}%;background:{COLORS.get(r.Stream, FALLBACK)}"></i></span>'
    f'<span class="meta"><b>{r.People} classmates</b> &middot; KES {r.Total:,}</span></div>'
    for r in summary.itertuples()
)
st.markdown(rows, unsafe_allow_html=True)

# ---- Facts and call to action ----
st.markdown(f"""
<div class="facts">
<div class="fact hot"><strong>KES {raised:,}</strong><span>raised so far</span></div>
<div class="fact"><strong>KES {PER_PERSON:,}</strong><span>per classmate</span></div>
</div>
<p class="cta">Book your space with KES {PER_PERSON:,}.</p>
""", unsafe_allow_html=True)

if st.button("Refresh now"):
    st.cache_data.clear()
    st.rerun()
