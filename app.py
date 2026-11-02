"""Stone · Paper · Scissor: Streamlit edition.

Run with:  streamlit run app.py
"""

import random
from collections import Counter

import streamlit as st

st.set_page_config(
    page_title="Stone Paper Scissor",
    page_icon="✂️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------ game data
MOVES = {1: "Stone", 2: "Paper", 3: "Scissor"}
BEATS = {1: 3, 2: 1, 3: 2}  # key beats value
COUNTER = {m: next(k for k, v in BEATS.items() if v == m) for m in MOVES}  # what beats m
VERBS = {(1, 3): "crushes", (2, 1): "covers", (3, 2): "cuts"}
TARGETS = {"Endless": None, "Best of 3": 2, "Best of 5": 3}

HEADLINES = {
    "win": ["Point to you", "Clean hit", "Nicely read"],
    "lose": ["Point to CPU", "Outplayed", "It saw that coming"],
    "tie": ["Dead heat", "Mirror match", "Nobody blinks"],
}

# ------------------------------------------------------------------ styling
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,800&family=Space+Mono:wght@400;700&display=swap');

:root{
  --ink:#1E1B18; --paper:#F3ECDC; --card:#FFFBEF; --sand:#EADFC8;
  --teal:#1F8A86; --mustard:#F4B63F; --verm:#E5533D;
  --display:'Bricolage Grotesque','Trebuchet MS',sans-serif;
  --mono:'Space Mono',ui-monospace,Menlo,monospace;
}

/* page */
.stApp{
  background-color:var(--paper);
  background-image:radial-gradient(rgba(30,27,24,.10) 1px, transparent 1.2px);
  background-size:16px 16px;
  color:var(--ink);
  font-family:var(--display);
}
.stApp p, .stApp label, .stApp span, .stApp li{color:var(--ink);}
header[data-testid="stHeader"]{background:transparent;}
[data-testid="stToolbar"], [data-testid="stDecoration"], footer{display:none !important;}
.block-container{max-width:860px; padding-top:2rem; padding-bottom:3rem;}

/* sidebar */
section[data-testid="stSidebar"]{background:var(--sand); border-right:3px solid var(--ink);}
section[data-testid="stSidebar"] *{font-family:var(--display);}
.side-title{font-family:var(--mono); font-size:.75rem; letter-spacing:.2em; text-transform:uppercase; margin:.4rem 0 .2rem;}
.side-note{font-family:var(--mono); font-size:.72rem; line-height:1.5; opacity:.8; margin-top:.4rem;}

/* masthead */
.masthead{margin-bottom:1.4rem;}
.kicker{font-family:var(--mono); font-size:.78rem; letter-spacing:.22em; text-transform:uppercase;}
.masthead h1{
  font-family:var(--display); font-weight:800; font-size:clamp(2.2rem,7vw,3.6rem);
  line-height:1; letter-spacing:-.03em; margin:.35rem 0 0; padding:0;
}
.masthead h1 .dot{color:var(--verm); margin:0 .12em;}
.masthead h1 mark{background:linear-gradient(transparent 58%, var(--mustard) 58%, var(--mustard) 92%, transparent 92%); color:var(--ink); padding:0 .06em;}

/* scoreboard */
.board{display:grid; grid-template-columns:1fr 1fr 1fr; border:3px solid var(--ink); border-radius:18px; overflow:hidden; background:var(--card); box-shadow:6px 6px 0 var(--ink);}
.cell{padding:.8rem 1rem .9rem; text-align:center; display:flex; flex-direction:column; align-items:center; gap:.1rem;}
.cell + .cell{border-left:3px solid var(--ink);}
.cell .k{font-family:var(--mono); font-size:.72rem; letter-spacing:.2em;}
.cell .n{font-weight:800; font-size:2.8rem; line-height:1.05;}
.cell .sub{font-family:var(--mono); font-size:.72rem; min-height:1.1rem;}
.cell.you{background:var(--teal);} .cell.you *{color:var(--paper) !important;}
.cell.cpu{background:var(--verm);} .cell.cpu *{color:var(--paper) !important;}
.pips{display:flex; gap:6px; min-height:14px; margin-top:.2rem;}
.pip{width:14px; height:14px; border-radius:50%; border:2px solid var(--paper); display:inline-block;}
.pip.on{background:var(--paper);}
.streak{display:inline-block; margin-top:.9rem; font-family:var(--mono); font-size:.75rem; font-weight:700; background:var(--mustard); border:2px solid var(--ink); border-radius:999px; padding:.15rem .7rem; transform:rotate(-2deg);}

/* arena */
.arena{display:grid; grid-template-columns:1fr auto 1fr; gap:1rem; align-items:center; margin:2rem 0 1.2rem;}
.side{position:relative; background:var(--card); border:3px solid var(--ink); border-radius:18px; padding:1.5rem 1rem 1rem; text-align:center; box-shadow:6px 6px 0 var(--ink); transition:background .2s;}
.side.won{background:#FBE3A8;}
.side .tag{position:absolute; top:-15px; left:16px; background:var(--ink); color:var(--paper) !important; font-family:var(--mono); font-size:.72rem; letter-spacing:.2em; padding:.2rem .65rem; border-radius:6px;}
.side .tag *{color:var(--paper) !important;}
.hand svg{width:min(150px,28vw); height:auto; display:block; margin:0 auto;}
.hand.goA{animation:throwA .75s cubic-bezier(.2,.8,.3,1.1);}
.hand.goB{animation:throwB .75s cubic-bezier(.2,.8,.3,1.1);}
.side.cpu .hand.goA, .side.cpu .hand.goB{animation-delay:.06s;}
@keyframes throwA{0%{transform:translateY(0) rotate(0)}15%{transform:translateY(-24px) rotate(-10deg)}32%{transform:translateY(8px) rotate(8deg)}48%{transform:translateY(-18px) rotate(-7deg)}64%{transform:translateY(5px) rotate(5deg)}100%{transform:none}}
@keyframes throwB{0%{transform:translateY(0) rotate(0)}15%{transform:translateY(-24px) rotate(-10deg)}32%{transform:translateY(8px) rotate(8deg)}48%{transform:translateY(-18px) rotate(-7deg)}64%{transform:translateY(5px) rotate(5deg)}100%{transform:none}}
.side .label{font-weight:800; font-size:1.15rem; letter-spacing:.06em; text-transform:uppercase; margin-top:.5rem;}
.vs{width:58px; height:58px; border-radius:50%; background:var(--mustard); border:3px solid var(--ink); display:grid; place-items:center; font-weight:800; font-size:1.2rem; transform:rotate(-9deg); box-shadow:3px 3px 0 var(--ink);}

/* result banner */
.result{border:3px solid var(--ink); border-radius:16px; padding:.9rem 1.2rem; box-shadow:6px 6px 0 var(--ink); transform:rotate(-.6deg); animation:pop .35s cubic-bezier(.2,1.4,.4,1) both; animation-delay:.55s;}
.result .big{font-weight:800; font-size:1.7rem; letter-spacing:-.01em; line-height:1.1;}
.result .small{font-family:var(--mono); font-size:.85rem; margin-top:.2rem;}
.result.win{background:var(--teal);} .result.win *{color:var(--paper) !important;}
.result.lose{background:var(--verm);} .result.lose *{color:var(--paper) !important;}
.result.tie{background:var(--mustard);}
.result.idle{background:var(--card); animation:none; transform:none;}
.result.final{background:var(--ink); margin-top:1rem; transform:rotate(.5deg);}
.result.final *{color:var(--paper) !important;}
@keyframes pop{0%{opacity:0; transform:scale(.85) rotate(-3deg)}100%{opacity:1; transform:scale(1) rotate(-.6deg)}}

/* move buttons */
.pick{font-family:var(--mono); font-size:.75rem; letter-spacing:.22em; text-transform:uppercase; margin:1.8rem 0 .6rem;}
.stButton{margin-top:.2rem;}
.stButton button{
  width:100%; border:3px solid var(--ink); border-radius:14px; padding:.85rem .5rem;
  font-family:var(--display); font-weight:800; letter-spacing:.05em; text-transform:uppercase;
  box-shadow:5px 5px 0 var(--ink); transition:transform .08s, box-shadow .08s;
  background:var(--card); color:var(--ink);
}
.stButton button *{color:inherit !important; font-family:var(--display) !important; font-weight:800 !important; font-size:1.05rem !important;}
.stButton button:hover{transform:translate(-2px,-2px); box-shadow:7px 7px 0 var(--ink); border-color:var(--ink);}
.stButton button:active{transform:translate(4px,4px); box-shadow:1px 1px 0 var(--ink);}
.stButton button:focus:not(:active){border-color:var(--ink); box-shadow:5px 5px 0 var(--ink);}
.stButton button:disabled{opacity:.45; transform:none; box-shadow:3px 3px 0 var(--ink); cursor:not-allowed;}
.st-key-b_1 button{background:var(--teal); color:var(--paper);}
.st-key-b_2 button{background:var(--mustard); color:var(--ink);}
.st-key-b_3 button{background:var(--verm); color:var(--paper);}
.st-key-b_new button{background:var(--ink); color:var(--paper);}
.st-key-b_reset button{background:var(--card); color:var(--ink); box-shadow:3px 3px 0 var(--ink);}

/* panels */
.panels{display:grid; grid-template-columns:1fr 1fr; gap:1.2rem; margin-top:2.2rem;}
.panel{background:var(--card); border:3px solid var(--ink); border-radius:16px; padding:1rem 1.1rem 1.1rem;}
.panel h4{font-family:var(--mono); font-size:.75rem; letter-spacing:.2em; text-transform:uppercase; margin:0 0 .8rem; padding:0;}
.bar-row{display:grid; grid-template-columns:70px 1fr 28px; align-items:center; gap:.6rem; margin:.45rem 0; font-size:.9rem; font-weight:500;}
.bar-row .num{font-family:var(--mono); text-align:right; font-size:.8rem;}
.track{height:14px; border:2px solid var(--ink); border-radius:999px; background:var(--sand); overflow:hidden;}
.fill{height:100%; display:block;}
.fill.m1{background:var(--teal);} .fill.m2{background:var(--mustard);} .fill.m3{background:var(--verm);}
.chips{display:flex; flex-wrap:wrap; gap:6px;}
.chip{width:28px; height:28px; border:2px solid var(--ink); border-radius:7px; display:grid; place-items:center; font-family:var(--mono); font-weight:700; font-size:.8rem;}
.chip.win{background:var(--teal); color:var(--paper);} .chip.lose{background:var(--verm); color:var(--paper);} .chip.tie{background:var(--mustard);}
.muted{font-family:var(--mono); font-size:.78rem; opacity:.75; line-height:1.5;}
.winrate{font-family:var(--mono); font-size:.8rem; margin-top:.9rem;}

@media (max-width:640px){
  .arena{gap:.5rem;} .vs{width:42px; height:42px; font-size:.95rem;}
  .panels{grid-template-columns:1fr;} .cell .n{font-size:2.2rem;}
}
</style>
"""


def h(markup: str) -> str:
    """Collapse indented HTML so Markdown never mistakes it for a code block."""
    return "".join(line.strip() for line in markup.strip().splitlines())


# ------------------------------------------------------------------ artwork
def icon(move):
    ink = "#1E1B18"
    s = f'stroke="{ink}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"'
    if move == 1:  # stone
        body = (
            f'<path d="M16 70 L10 46 L30 20 L60 12 L86 30 L92 60 L72 84 L36 88 Z" fill="#8FC1BA" {s}/>'
            f'<path d="M30 20 L44 44 L36 64 M60 12 L56 38 L74 54 M44 44 L56 38" fill="none" {s}/>'
        )
    elif move == 2:  # paper
        body = (
            f'<path d="M24 8 H62 L82 28 V92 H24 Z" fill="#FFF3CF" {s}/>'
            f'<path d="M62 8 V28 H82" fill="none" {s}/>'
            f'<path d="M36 48 H70 M36 62 H70 M36 76 H56" fill="none" {s}/>'
        )
    elif move == 3:  # scissor
        blade = lambda x1, y1, x2, y2: (
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ink}" stroke-width="14" stroke-linecap="round"/>'
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#E6E2D8" stroke-width="6" stroke-linecap="round"/>'
        )
        ring = lambda cx: (
            f'<circle cx="{cx}" cy="80" r="13" fill="#E5533D" {s}/>'
            f'<circle cx="{cx}" cy="80" r="5" fill="#FFFBEF" stroke="{ink}" stroke-width="3"/>'
        )
        body = blade(28, 10, 72, 66) + blade(72, 10, 28, 66) + ring(26) + ring(74) + f'<circle cx="50" cy="38" r="4" fill="{ink}"/>'
    else:  # not thrown yet
        body = (
            f'<circle cx="50" cy="50" r="34" fill="none" stroke="{ink}" stroke-width="4" stroke-dasharray="6 9" stroke-linecap="round"/>'
            f'<text x="50" y="64" text-anchor="middle" font-size="42" font-weight="800" fill="{ink}" font-family="sans-serif">?</text>'
        )
    return f'<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">{body}</svg>'


# ------------------------------------------------------------------ state
def fresh():
    st.session_state.score = {"win": 0, "lose": 0, "tie": 0}
    st.session_state.history = []
    st.session_state.streak = 0
    st.session_state.best = 0
    st.session_state.last = None


def target():
    return TARGETS[st.session_state.mode]


def match_over():
    t = target()
    sc = st.session_state.score
    return t is not None and (sc["win"] >= t or sc["lose"] >= t)


def cpu_pick(difficulty, history):
    """Easy: pure luck. Hard: counters whatever you've leaned on in your last six throws."""
    if difficulty == "Easy" or len(history) < 3:
        return random.choice(list(MOVES))
    recent = [x["p"] for x in history[-6:]]
    favourite = Counter(recent).most_common(1)[0][0]
    if random.random() < 0.55:
        return COUNTER[favourite]
    return random.choice(list(MOVES))


def play(move):
    ss = st.session_state
    if match_over():
        return
    cpu = cpu_pick(ss.difficulty, ss.history)
    res = "tie" if move == cpu else ("win" if BEATS[move] == cpu else "lose")
    ss.score[res] += 1
    ss.history.append({"p": move, "c": cpu, "r": res})
    ss.streak = ss.streak + 1 if res == "win" else 0
    ss.best = max(ss.best, ss.streak)
    ss.last = {**ss.history[-1], "n": len(ss.history)}


if "score" not in st.session_state:
    fresh()

# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.markdown('<div class="side-title">Opponent</div>', unsafe_allow_html=True)
    st.radio("Difficulty", ["Easy", "Hard"], key="difficulty", on_change=fresh, label_visibility="collapsed")
    st.markdown('<div class="side-title">Format</div>', unsafe_allow_html=True)
    st.radio("Mode", list(TARGETS), key="mode", on_change=fresh, label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("Reset scores", key="b_reset", on_click=fresh)
    st.markdown(
        '<div class="side-note">Easy throws at random.<br>Hard studies your last six throws and '
        "leans on the counter. Changing a setting restarts the match.</div>",
        unsafe_allow_html=True,
    )

st.markdown(CSS, unsafe_allow_html=True)

ss = st.session_state
sc, last, t = ss.score, ss.last, target()
over = match_over()
rounds = len(ss.history)

# ------------------------------------------------------------------ masthead
st.markdown(
    h("""
    <div class="masthead">
      <div class="kicker">Three moves &middot; one winner</div>
      <h1>Stone<span class="dot">/</span>Paper<span class="dot">/</span><mark>Scissor</mark></h1>
    </div>
    """),
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------ scoreboard
def pips(n):
    if t is None:
        return '<div class="pips"></div>'
    return '<div class="pips">' + "".join(f'<i class="pip{" on" if i < n else ""}"></i>' for i in range(t)) + "</div>"


sub_mid = "first to %d" % t if t else "endless"
st.markdown(
    h(f"""
    <div class="board">
      <div class="cell you"><span class="k">YOU</span><span class="n">{sc['win']}</span>{pips(sc['win'])}</div>
      <div class="cell"><span class="k">ROUND</span><span class="n">{rounds}</span><span class="sub">{sc['tie']} tie{'s' if sc['tie'] != 1 else ''} &middot; {sub_mid}</span></div>
      <div class="cell cpu"><span class="k">CPU</span><span class="n">{sc['lose']}</span>{pips(sc['lose'])}</div>
    </div>
    """)
    + (f'<span class="streak">STREAK x{ss.streak}</span>' if ss.streak >= 2 else ""),
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------ arena
if last:
    p, c, r, n = last["p"], last["c"], last["r"], last["n"]
    anim = "goA" if n % 2 else "goB"
    you_cls = " won" if r == "win" else ""
    cpu_cls = " won" if r == "lose" else ""
    you_svg, cpu_svg = icon(p), icon(c)
    you_lbl, cpu_lbl = MOVES[p], MOVES[c]
else:
    anim, you_cls, cpu_cls = "", "", ""
    you_svg = cpu_svg = icon(0)
    you_lbl = cpu_lbl = "&hellip;"

st.markdown(
    h(f"""
    <div class="arena">
      <div class="side you{you_cls}"><span class="tag">YOU</span><div class="hand {anim}">{you_svg}</div><div class="label">{you_lbl}</div></div>
      <div class="vs">VS</div>
      <div class="side cpu{cpu_cls}"><span class="tag">CPU</span><div class="hand {anim}">{cpu_svg}</div><div class="label">{cpu_lbl}</div></div>
    </div>
    """),
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------ result
if last:
    if r == "win":
        detail = f"{MOVES[p]} {VERBS[(p, c)]} {MOVES[c]}."
    elif r == "lose":
        detail = f"{MOVES[c]} {VERBS[(c, p)]} {MOVES[p]}."
    else:
        detail = f"Both threw {MOVES[p]}."
    headline = HEADLINES[r][n % 3]
    st.markdown(
        h(f'<div class="result {r}"><div class="big">{headline}</div><div class="small">{detail}</div></div>'),
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        h('<div class="result idle"><div class="big">Your throw.</div><div class="small">Pick a move below to start the match.</div></div>'),
        unsafe_allow_html=True,
    )

if over:
    won = sc["win"] > sc["lose"]
    st.markdown(
        h(
            f'<div class="result final"><div class="big">{"Match is yours" if won else "CPU takes the match"}</div>'
            f'<div class="small">Final score {sc["win"]} &ndash; {sc["lose"]}. Best streak: {ss.best}.</div></div>'
        ),
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------------ controls
if over:
    st.markdown('<div class="pick">Go again?</div>', unsafe_allow_html=True)
    st.button("New match", key="b_new", on_click=fresh)
else:
    st.markdown('<div class="pick">Choose your throw</div>', unsafe_allow_html=True)
    cols = st.columns(3, gap="medium")
    for col, m in zip(cols, MOVES):
        with col:
            st.button(f"{m} · {MOVES[m]}", key=f"b_{m}", on_click=play, args=(m,))

# ------------------------------------------------------------------ insights
counts = Counter(x["p"] for x in ss.history)
total = max(rounds, 1)
bars = "".join(
    f'<div class="bar-row"><span>{MOVES[m]}</span>'
    f'<span class="track"><span class="fill m{m}" style="width:{counts[m] / total * 100:.0f}%"></span></span>'
    f'<span class="num">{counts[m]}</span></div>'
    for m in MOVES
)
if rounds:
    rate = sc["win"] / rounds * 100
    habits = bars + f'<div class="winrate">Win rate {rate:.0f}% &middot; best streak {ss.best}</div>'
    letters = {"win": "W", "lose": "L", "tie": "T"}
    chips = "".join(
        f'<span class="chip {x["r"]}" title="{MOVES[x["p"]]} vs {MOVES[x["c"]]}">{letters[x["r"]]}</span>'
        for x in ss.history[-16:]
    )
    recent = f'<div class="chips">{chips}</div>'
    if ss.difficulty == "Hard":
        recent += '<div class="muted" style="margin-top:.8rem">The CPU is reading your last six throws.</div>'
else:
    habits = '<div class="muted">Play a round and your habits show up here. The Hard CPU is looking at the same numbers.</div>'
    recent = '<div class="muted">Nothing thrown yet.</div>'

st.markdown(
    h(f"""
    <div class="panels">
      <div class="panel"><h4>Your habits</h4>{habits}</div>
      <div class="panel"><h4>Recent rounds</h4>{recent}</div>
    </div>
    """),
    unsafe_allow_html=True,
)
