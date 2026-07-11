"""
Chess Platform - ~1000 ELO Bot + Multiplayer + Admin
Run: streamlit run app.py
"""
import streamlit as st
import streamlit.components.v1 as components
import chess
import random, time, json, hashlib, uuid
from datetime import datetime
from pathlib import Path

DATA_DIR   = Path("data")
USERS_FILE = DATA_DIR / "users.json"
GAMES_FILE = DATA_DIR / "games.json"
DATA_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="Chess", page_icon="♟", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=JetBrains+Mono&display=swap');
html,body,[class*="css"]{font-family:'Syne',sans-serif;background:#0d0d10;color:#e6e2db;}
.stApp{background:#0d0d10;}
div.stButton>button{background:#e6b84a!important;color:#0d0d10!important;
  font-family:'Syne',sans-serif!important;font-weight:800!important;border:none!important;
  border-radius:5px!important;padding:.4rem 1rem!important;transition:opacity .15s!important;}
div.stButton>button:hover{opacity:.78!important;}
div[data-baseweb="input"] input{background:#1e1e28!important;color:#e6e2db!important;
  border:1px solid #2a2a35!important;border-radius:5px!important;}
div[data-baseweb="tab-list"]{background:#17171d!important;border-radius:8px!important;padding:4px!important;}
button[data-baseweb="tab"]{background:transparent!important;color:#888!important;border-radius:6px!important;font-weight:600!important;}
button[data-baseweb="tab"][aria-selected="true"]{background:#e6b84a!important;color:#0d0d10!important;}
section[data-testid="stSidebar"]{background:#111116!important;}
section[data-testid="stSidebar"] *{color:#e6e2db!important;}
.pill{display:block;background:#1e1e28;border-left:3px solid #e6b84a;border-radius:4px;
  padding:.35rem .9rem;font-family:'JetBrains Mono',monospace;font-size:.8rem;color:#e6b84a;margin:.4rem 0 .7rem;}
.card{background:#17171d;border:1px solid #2a2a35;border-radius:10px;padding:1.2rem 1.5rem;margin-bottom:.8rem;}
.ct{font-size:.85rem;font-weight:800;letter-spacing:.07em;text-transform:uppercase;color:#e6b84a;margin-bottom:.5rem;}
.logo{font-size:2.2rem;font-weight:800;}.logo span{color:#e6b84a;}
.badge{background:#2a2a35;border-radius:20px;padding:2px 10px;font-size:.74rem;color:#e6b84a;}
.badge-admin{background:#e6b84a22;border:1px solid #e6b84a55;}
.mlist{font-family:'JetBrains Mono',monospace;font-size:.75rem;color:#888;
  max-height:180px;overflow-y:auto;background:#0d0d10;border-radius:6px;padding:.5rem .8rem;line-height:1.9;}
.mlist span{color:#e6e2db;}
#MainMenu,footer,header{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ── user store ────────────────────────────────────────────────────────────────
def _hash(pw): return hashlib.sha256(pw.encode()).hexdigest()

def load_users():
    if USERS_FILE.exists(): return json.loads(USERS_FILE.read_text())
    u = {"admin": {"password": _hash("admin123"), "role": "admin",
                   "created": datetime.now().isoformat(), "wins":0,"losses":0,"draws":0}}
    USERS_FILE.write_text(json.dumps(u, indent=2)); return u

def save_users(u): USERS_FILE.write_text(json.dumps(u, indent=2))
def load_games(): return json.loads(GAMES_FILE.read_text()) if GAMES_FILE.exists() else {}
def save_games(g): GAMES_FILE.write_text(json.dumps(g, indent=2))

# ── engine ────────────────────────────────────────────────────────────────────
PST = {
    chess.PAWN:   [0,0,0,0,0,0,0,0,50,50,50,50,50,50,50,50,10,10,20,30,30,20,10,10,
                   5,5,10,25,25,10,5,5,0,0,0,20,20,0,0,0,5,-5,-10,0,0,-10,-5,5,
                   5,10,10,-20,-20,10,10,5,0,0,0,0,0,0,0,0],
    chess.KNIGHT: [-50,-40,-30,-30,-30,-30,-40,-50,-40,-20,0,0,0,0,-20,-40,
                   -30,0,10,15,15,10,0,-30,-30,5,15,20,20,15,5,-30,
                   -30,0,15,20,20,15,0,-30,-30,5,10,15,15,10,5,-30,
                   -40,-20,0,5,5,0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50],
    chess.BISHOP: [-20,-10,-10,-10,-10,-10,-10,-20,-10,0,0,0,0,0,0,-10,
                   -10,0,5,10,10,5,0,-10,-10,5,5,10,10,5,5,-10,
                   -10,0,10,10,10,10,0,-10,-10,10,10,10,10,10,10,-10,
                   -10,5,0,0,0,0,5,-10,-20,-10,-10,-10,-10,-10,-10,-20],
    chess.ROOK:   [0,0,0,0,0,0,0,0,5,10,10,10,10,10,10,5,-5,0,0,0,0,0,0,-5,
                   -5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,
                   -5,0,0,0,0,0,0,-5,0,0,0,5,5,0,0,0],
    chess.QUEEN:  [-20,-10,-10,-5,-5,-10,-10,-20,-10,0,0,0,0,0,0,-10,
                   -10,0,5,5,5,5,0,-10,-5,0,5,5,5,5,0,-5,
                   0,0,5,5,5,5,0,-5,-10,5,5,5,5,5,0,-10,
                   -10,0,5,0,0,0,0,-10,-20,-10,-10,-5,-5,-10,-10,-20],
    chess.KING:   [-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,
                   -30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,
                   -20,-30,-30,-40,-40,-30,-30,-20,-10,-20,-20,-20,-20,-20,-20,-10,
                   20,20,0,0,0,0,20,20,20,30,10,0,0,10,30,20],
}
PV = {chess.PAWN:100,chess.KNIGHT:320,chess.BISHOP:330,chess.ROOK:500,chess.QUEEN:900,chess.KING:20000}

def evaluate(b):
    if b.is_checkmate(): return -99999 if b.turn==chess.WHITE else 99999
    if b.is_stalemate() or b.is_insufficient_material(): return 0
    s=0
    for sq in chess.SQUARES:
        p=b.piece_at(sq)
        if p:
            idx=sq if p.color==chess.WHITE else chess.square_mirror(sq)
            v=PV[p.piece_type]+PST.get(p.piece_type,[0]*64)[idx]
            s+=v if p.color==chess.WHITE else -v
    return s

def minimax(b,d,a,be,mx):
    if d==0 or b.is_game_over(): return evaluate(b)
    if mx:
        best=-999999
        for m in b.legal_moves:
            b.push(m); best=max(best,minimax(b,d-1,a,be,False)); b.pop()
            a=max(a,best)
            if be<=a: break
        return best
    else:
        best=999999
        for m in b.legal_moves:
            b.push(m); best=min(best,minimax(b,d-1,a,be,True)); b.pop()
            be=min(be,best)
            if be<=a: break
        return best

def get_bot_move(b):
    legal=list(b.legal_moves)
    if not legal: return None
    if random.random()<0.25: return random.choice(legal)
    best,bv=None,-999999
    for m in legal:
        b.push(m); v=minimax(b,1,-999999,999999,b.turn==chess.WHITE); b.pop()
        if v>bv: bv,best=v,m
    return best or random.choice(legal)

# ── session ───────────────────────────────────────────────────────────────────
def init():
    defs = dict(
        logged_in=False,
        username=None,
        role=None,
        page="auth",
        fen=chess.STARTING_FEN,
        my_color=chess.WHITE,
        history=[],
        sel=None,
        status="Your move",
        game_over=False,
        last_uci="",
        mode="bot",
        gid=None,
        opponent=None,
        clicked_sq=None,
    )
    for k, v in defs.items():
        st.session_state.setdefault(k, v)
init()

# ── move logic ────────────────────────────────────────────────────────────────
def push_move(board, move):
    board.push(move)
    st.session_state.fen      = board.fen()
    st.session_state.history.append(move.uci())
    st.session_state.last_uci = move.uci()
    st.session_state.sel      = None
    st.session_state.clicked_sq = None
    if board.is_game_over():
        st.session_state.game_over=True
        st.session_state.status="Game over: "+board.result()
        end_game(board.result())
    elif st.session_state.mode=="bot":
        st.session_state.status="Bot thinking..."
    else:
        mp_push(st.session_state.gid,move.uci())
        st.session_state.status="Opponent's turn"

def sq_click(sq):
    board=chess.Board(st.session_state.fen)
    pc=st.session_state.my_color
    sel=st.session_state.sel
    if sel is None:
        p=board.piece_at(sq)
        if p and p.color==pc and board.turn==pc:
            st.session_state.sel=sq
        return
    sp=board.piece_at(sel)
    promo=chess.QUEEN if (sp and sp.piece_type==chess.PAWN and chess.square_rank(sq) in (0,7)) else None
    mv=chess.Move(sel,sq,promotion=promo)
    if mv not in board.legal_moves: mv=chess.Move(sel,sq)
    if mv in board.legal_moves:
        push_move(board,mv)
    else:
        p=board.piece_at(sq)
        st.session_state.sel=sq if (p and p.color==pc and board.turn==pc) else None

PROMO_MAP = {"q": chess.QUEEN, "r": chess.ROOK, "b": chess.BISHOP, "n": chess.KNIGHT}

def apply_move(frm_name, to_name, promo=None):
    """Apply a move given as algebraic square names (e.g. 'e2','e4'), used by the new HTML/JS board."""
    board = chess.Board(st.session_state.fen)
    pc = st.session_state.my_color
    if board.turn != pc or st.session_state.game_over:
        return
    try:
        frm = chess.parse_square(frm_name)
        to  = chess.parse_square(to_name)
    except ValueError:
        return
    sp = board.piece_at(frm)
    promo_type = PROMO_MAP.get(promo) if promo else (
        chess.QUEEN if (sp and sp.piece_type == chess.PAWN and chess.square_rank(to) in (0, 7)) else None
    )
    mv = chess.Move(frm, to, promotion=promo_type)
    if mv not in board.legal_moves:
        mv = chess.Move(frm, to)
    if mv in board.legal_moves:
        push_move(board, mv)

def uci_move(text):
    board=chess.Board(st.session_state.fen)
    pc=st.session_state.my_color
    if board.turn!=pc or st.session_state.game_over: return "Not your turn"
    try:
        try:    mv=board.parse_uci(text.strip())
        except: mv=board.parse_san(text.strip())
        if mv in board.legal_moves: push_move(board,mv); return ""
        return "Illegal move"
    except: return "Invalid notation"

# ── board renderer (interactive HTML/JS board with drag&drop + arrows) ────────
PSYM = {
    (chess.PAWN,  chess.WHITE):"♙",(chess.PAWN,  chess.BLACK):"♟",
    (chess.KNIGHT,chess.WHITE):"♘",(chess.KNIGHT,chess.BLACK):"♞",
    (chess.BISHOP,chess.WHITE):"♗",(chess.BISHOP,chess.BLACK):"♝",
    (chess.ROOK,  chess.WHITE):"♖",(chess.ROOK,  chess.BLACK):"♜",
    (chess.QUEEN, chess.WHITE):"♕",(chess.QUEEN, chess.BLACK):"♛",
    (chess.KING,  chess.WHITE):"♔",(chess.KING,  chess.BLACK):"♚",
}

BOARD_HTML = r"""<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  * { box-sizing: border-box; }
  html,body { margin:0; padding:0; background:transparent; font-family:'Syne',Arial,sans-serif; }
  .wrap { display:flex; flex-direction:column; align-items:center; gap:8px; padding:4px 0; }
  .toolbar { display:flex; gap:8px; flex-wrap:wrap; justify-content:center; }
  .toolbar button {
    background:#e6b84a; color:#0d0d10; border:none; border-radius:6px;
    font-weight:800; padding:.4rem .9rem; cursor:pointer; font-size:13px;
    font-family:'Syne',Arial,sans-serif;
  }
  .toolbar button.active { background:#5fc8ee; color:#0d0d10; }
  .board-shell { position:relative; width:min(560px,94vw); height:min(560px,94vw); }
  .board {
    width:100%; height:100%; display:grid;
    grid-template-columns:repeat(8,1fr); grid-template-rows:repeat(8,1fr);
    border:3px solid #3a3a45; border-radius:4px; overflow:hidden;
    box-shadow:0 8px 32px rgba(0,0,0,.55);
  }
  .square { position:relative; display:flex; align-items:center; justify-content:center;
            font-size:min(7vw,42px); user-select:none; }
  .light { background:#f0d9b5; }
  .dark  { background:#b58863; }
  .last-move { box-shadow: inset 0 0 0 1000px rgba(255,235,59,.32); }
  .check-sq  { background:#e53935 !important; }
  .selected  { outline:3px solid #5fc8ee; outline-offset:-3px; z-index:2; }
  .legal-dot::after {
    content:""; position:absolute; width:26%; height:26%; border-radius:50%;
    background:rgba(30,160,70,.55); z-index:1;
  }
  .legal-capture::after {
    content:""; position:absolute; width:82%; height:82%; border-radius:50%;
    border:5px solid rgba(200,60,60,.55); box-sizing:border-box; z-index:1;
  }
  .piece { cursor:grab; z-index:3; line-height:1; }
  .piece.disabled { cursor:default; }
  .coord { position:absolute; font-size:10px; font-weight:700; font-family:'JetBrains Mono',monospace;
           color:rgba(0,0,0,.4); z-index:4; }
  .coord-rank { top:2px; left:3px; }
  .coord-file { bottom:2px; right:3px; }
  .board-overlay { position:absolute; inset:0; pointer-events:none; z-index:5; }
  .promo-overlay {
    position:absolute; inset:0; display:none; align-items:center; justify-content:center;
    background:rgba(0,0,0,.55); z-index:20; border-radius:4px;
  }
  .promo-dialog { background:#17171d; border:1px solid #2a2a35; border-radius:10px;
                  padding:14px 16px; text-align:center; }
  .promo-dialog h4 { margin:0 0 8px; color:#e6e2db; font-size:14px; font-family:'Syne',Arial,sans-serif; }
  .promo-row { display:flex; gap:6px; }
  .promo-btn { border:none; border-radius:6px; padding:8px 10px; font-size:22px;
               cursor:pointer; background:#2a2a35; color:#e6e2db; }
  .promo-btn:hover { background:#e6b84a; color:#0d0d10; }
  @media (max-width:480px) {
    .toolbar button { font-size:12px; padding:.35rem .7rem; }
  }
</style>
</head>
<body>
<div class="wrap">
  <div class="toolbar">
    <button id="arrowBtn" onclick="toggleArrowMode()">✏ Draw Arrows</button>
    <button onclick="clearArrows()">🧹 Clear Arrows</button>
  </div>
  <div class="board-shell">
    <div id="board" class="board"></div>
    <svg id="arrowLayer" class="board-overlay" viewBox="0 0 640 640" preserveAspectRatio="none"></svg>
    <div id="promoOverlay" class="promo-overlay">
      <div class="promo-dialog">
        <h4>Promote to</h4>
        <div class="promo-row">
          <button class="promo-btn" data-p="q">♕</button>
          <button class="promo-btn" data-p="r">♖</button>
          <button class="promo-btn" data-p="b">♗</button>
          <button class="promo-btn" data-p="n">♘</button>
        </div>
      </div>
    </div>
  </div>
</div>
<script>
const DATA = __DATA__;
const FILES = ["a","b","c","d","e","f","g","h"];
const boardEl = document.getElementById("board");

let arrowMode = false;
let arrowStart = null;
let arrows = [];
let selected = null;
let pendingPromo = null;

function squareColor(fileIdx, rank){ return ((fileIdx + rank) % 2 === 0) ? "light" : "dark"; }

function buildBoard(){
  boardEl.innerHTML = "";
  const ranks = DATA.flip ? [1,2,3,4,5,6,7,8] : [8,7,6,5,4,3,2,1];
  const dfiles = DATA.flip ? FILES.slice().reverse() : FILES;

  ranks.forEach(rank => {
    dfiles.forEach(file => {
      const name = file + rank;
      const fIdx = FILES.indexOf(file);
      const sq = document.createElement("div");
      sq.className = "square " + squareColor(fIdx, rank);
      sq.dataset.sq = name;

      if (DATA.last && DATA.last.includes(name)) sq.classList.add("last-move");
      if (DATA.check === name) sq.classList.add("check-sq");
      if (selected === name) sq.classList.add("selected");

      const targets = (selected && DATA.legal && DATA.legal[selected]) || [];
      if (targets.includes(name)) {
        sq.classList.add(DATA.squares[name] ? "legal-capture" : "legal-dot");
      }

      if (fIdx === (DATA.flip ? 7 : 0)) {
        const r = document.createElement("div");
        r.className = "coord coord-rank"; r.innerText = rank;
        sq.appendChild(r);
      }
      if (rank === (DATA.flip ? 8 : 1)) {
        const f = document.createElement("div");
        f.className = "coord coord-file"; f.innerText = file;
        sq.appendChild(f);
      }

      const sym = DATA.squares[name];
      if (sym) {
        const span = document.createElement("span");
        span.className = "piece";
        span.innerText = sym;
        const mine = DATA.interactive && DATA.myPieces.includes(name);
        span.draggable = !!mine;
        if (!mine) span.classList.add("disabled");
        span.addEventListener("dragstart", (e) => {
          if (arrowMode || !mine) { e.preventDefault(); return; }
          selected = name;
          e.dataTransfer.setData("text/plain", name);
          buildBoard();
        });
        sq.appendChild(span);
      }

      sq.addEventListener("dragover", (e) => e.preventDefault());
      sq.addEventListener("drop", (e) => {
        e.preventDefault();
        const frm = e.dataTransfer.getData("text/plain");
        if (frm) attemptMove(frm, name);
      });
      sq.addEventListener("click", () => onSquareClick(name));

      boardEl.appendChild(sq);
    });
  });
  drawArrows();
}

function onSquareClick(name){
  if (arrowMode) {
    if (!arrowStart) { arrowStart = name; }
    else if (arrowStart === name) { arrowStart = null; }
    else { arrows.push({from: arrowStart, to: name}); arrowStart = null; }
    buildBoard();
    return;
  }
  if (!DATA.interactive) return;

  if (selected) {
    if (selected === name) { selected = null; buildBoard(); return; }
    const legalTo = (DATA.legal && DATA.legal[selected]) || [];
    if (legalTo.includes(name)) { attemptMove(selected, name); return; }
    if (DATA.myPieces.includes(name)) { selected = name; buildBoard(); return; }
    selected = null; buildBoard();
    return;
  }
  if (DATA.myPieces.includes(name)) { selected = name; buildBoard(); }
}

function isPromotion(frm, to){
  const sym = DATA.squares[frm];
  if (!sym) return false;
  const isPawn = (sym === "♙" || sym === "♟");
  if (!isPawn) return false;
  const rank = parseInt(to[1], 10);
  return (rank === 1 || rank === 8);
}

function attemptMove(frm, to){
  if (!DATA.interactive) return;
  const legalTo = (DATA.legal && DATA.legal[frm]) || [];
  if (!legalTo.includes(to)) { selected = null; buildBoard(); return; }
  if (isPromotion(frm, to)) {
    pendingPromo = {frm, to};
    document.getElementById("promoOverlay").style.display = "flex";
    return;
  }
  sendMove(frm, to, null);
}

document.querySelectorAll(".promo-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    if (!pendingPromo) return;
    sendMove(pendingPromo.frm, pendingPromo.to, btn.dataset.p);
    pendingPromo = null;
    document.getElementById("promoOverlay").style.display = "none";
  });
});

function sendMove(frm, to, promo){
  const url = new URL(window.top.location.href);
  url.searchParams.set("frm", frm);
  url.searchParams.set("to", to);
  if (promo) url.searchParams.set("promo", promo); else url.searchParams.delete("promo");
  window.top.history.pushState({}, "", url);
  window.top.dispatchEvent(new PopStateEvent("popstate"));
}

function toggleArrowMode(){
  arrowMode = !arrowMode;
  arrowStart = null;
  document.getElementById("arrowBtn").classList.toggle("active", arrowMode);
  buildBoard();
}
function clearArrows(){ arrows = []; arrowStart = null; buildBoard(); }

function squareCenter(name){
  const file = FILES.indexOf(name[0]);
  const rank = parseInt(name[1], 10);
  const df = DATA.flip ? 7 - file : file;
  const dr = DATA.flip ? rank - 1 : 8 - rank;
  return { x: df*80 + 40, y: dr*80 + 40 };
}

function drawArrows(){
  const svg = document.getElementById("arrowLayer");
  svg.innerHTML = "";
  if (arrows.length === 0 && !arrowStart) return;
  const ns = "http://www.w3.org/2000/svg";
  const marker = document.createElementNS(ns, "marker");
  marker.setAttribute("id", "arrowhead");
  marker.setAttribute("markerWidth", "8"); marker.setAttribute("markerHeight", "8");
  marker.setAttribute("refX", "6"); marker.setAttribute("refY", "3"); marker.setAttribute("orient", "auto");
  const poly = document.createElementNS(ns, "polygon");
  poly.setAttribute("points", "0 0, 7 3, 0 6"); poly.setAttribute("fill", "#2563eb");
  marker.appendChild(poly); svg.appendChild(marker);
  arrows.forEach(a => {
    const f = squareCenter(a.from), t = squareCenter(a.to);
    const line = document.createElementNS(ns, "line");
    line.setAttribute("x1", f.x); line.setAttribute("y1", f.y);
    line.setAttribute("x2", t.x); line.setAttribute("y2", t.y);
    line.setAttribute("stroke", "#2563eb"); line.setAttribute("stroke-width", "6");
    line.setAttribute("stroke-linecap", "round"); line.setAttribute("marker-end", "url(#arrowhead)");
    line.setAttribute("opacity", "0.95");
    svg.appendChild(line);
  });
}

buildBoard();
</script>
</body>
</html>"""


def render_board():
    board = chess.Board(st.session_state.fen)
    flip  = st.session_state.my_color == chess.BLACK
    pc    = st.session_state.my_color
    is_my_turn = board.turn == pc and not st.session_state.game_over

    squares, my_pieces = {}, []
    for sq in chess.SQUARES:
        p = board.piece_at(sq)
        if p:
            name = chess.square_name(sq)
            squares[name] = PSYM[(p.piece_type, p.color)]
            if is_my_turn and p.color == pc:
                my_pieces.append(name)

    legal_map = {}
    if is_my_turn:
        for m in board.legal_moves:
            legal_map.setdefault(chess.square_name(m.from_square), []).append(chess.square_name(m.to_square))

    last_sqs = []
    if st.session_state.last_uci:
        try:
            lm = chess.Move.from_uci(st.session_state.last_uci)
            last_sqs = [chess.square_name(lm.from_square), chess.square_name(lm.to_square)]
        except ValueError:
            pass

    check_name = None
    if board.is_check():
        ksq = board.king(board.turn)
        if ksq is not None:
            check_name = chess.square_name(ksq)

    payload = {
        "squares": squares,
        "legal": legal_map,
        "last": last_sqs,
        "check": check_name,
        "flip": flip,
        "interactive": is_my_turn,
        "myPieces": my_pieces,
    }

    html = BOARD_HTML.replace("__DATA__", json.dumps(payload))
    components.html(html, height=700, scrolling=False)

# ── multiplayer ───────────────────────────────────────────────────────────────
def mp_push(gid,uci):
    games=load_games(); g=games.get(gid)
    if not g: return
    b=chess.Board(g["fen"])
    try:
        m=chess.Move.from_uci(uci)
        if m in b.legal_moves:
            b.push(m); g["fen"]=b.fen(); g["moves"].append(uci)
            if b.is_game_over(): g["status"]="finished"; g["result"]=b.result()
            save_games(games)
    except: pass

def end_game(result):
    me=st.session_state.username; opp=st.session_state.opponent; pc=st.session_state.my_color
    users=load_users()
    def bump(u,f):
        if u and u in users: users[u][f]=users[u].get(f,0)+1
    if result=="1/2-1/2": bump(me,"draws"); bump(opp,"draws")
    elif (result=="1-0" and pc==chess.WHITE) or (result=="0-1" and pc==chess.BLACK):
        bump(me,"wins"); bump(opp,"losses")
    else: bump(me,"losses"); bump(opp,"wins")
    save_users(users)

def new_bot_game(color):
    st.session_state.update(fen=chess.STARTING_FEN,
        my_color=chess.WHITE if color=="White" else chess.BLACK,
        history=[],sel=None,status="Your move",game_over=False,
        last_uci="",mode="bot",gid=None,opponent="Bot (~1000 ELO)",page="game",
        clicked_sq=None)

def do_login(u,p):
    users=load_users(); ud=users.get(u)
    if ud and ud["password"]==_hash(p):
        st.session_state.update(logged_in=True,username=u,role=ud["role"],page="lobby"); return True
    return False

def do_register(u,p):
    users=load_users()
    if u in users:  return False,"Username taken."
    if len(u)<3:    return False,"Username must be 3+ chars."
    if len(p)<6:    return False,"Password must be 6+ chars."
    users[u]={"password":_hash(p),"role":"player","created":datetime.now().isoformat(),
              "wins":0,"losses":0,"draws":0}
    save_users(users); return True,"Account created — log in now."

def do_logout():
    for k in list(st.session_state.keys()): del st.session_state[k]
    init()

# ── pages ─────────────────────────────────────────────────────────────────────
def page_auth():
    _,col,_=st.columns([1,1.4,1])
    with col:
        st.markdown('<div class="logo">♟ Chess<span>.</span></div>',unsafe_allow_html=True)
        st.markdown("<p style='color:#555;margin:-4px 0 1.2rem'>Bot · Multiplayer · Admin</p>",unsafe_allow_html=True)
        t1,t2=st.tabs(["Log in","Create account"])
        with t1:
            u=st.text_input("Username",key="liu"); p=st.text_input("Password",type="password",key="lip")
            if st.button("Log in",key="libtn"):
                if do_login(u,p): st.rerun()
                else: st.error("Wrong credentials.")
            st.caption("Default admin: `admin` / `admin123`")
        with t2:
            nu=st.text_input("Username",key="rgu"); np=st.text_input("Password",type="password",key="rgp")
            nc=st.text_input("Confirm",type="password",key="rgc")
            if st.button("Register",key="rgbtn"):
                if np!=nc: st.error("Passwords don't match.")
                else:
                    ok,msg=do_register(nu,np)
                    st.success(msg) if ok else st.error(msg)

def page_lobby():
    users=load_users(); u=users.get(st.session_state.username,{})
    st.markdown(f"## Welcome, **{st.session_state.username}** 👋")
    c1,c2,c3=st.columns(3)
    c1.metric("Wins",u.get("wins",0)); c2.metric("Losses",u.get("losses",0)); c3.metric("Draws",u.get("draws",0))
    st.markdown("---")
    L,R=st.columns(2,gap="large")
    with L:
        st.markdown('<div class="card"><div class="ct">🤖 vs Bot (~1000 ELO)</div>',unsafe_allow_html=True)
        cp=st.selectbox("Play as",["White","Black"],key="lbc")
        if st.button("Start",key="lsb"): new_bot_game(cp); st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)
    with R:
        st.markdown('<div class="card"><div class="ct">👥 Multiplayer</div>',unsafe_allow_html=True)
        if st.button("Create game",key="lcg"):
            games=load_games(); gid=str(uuid.uuid4())[:8]
            games[gid]={"white":st.session_state.username,"black":None,
                        "fen":chess.STARTING_FEN,"moves":[],"status":"waiting",
                        "result":None,"created":datetime.now().isoformat()}
            save_games(games)
            st.session_state.update(gid=gid,my_color=chess.WHITE,opponent="Waiting...",
                mode="multiplayer",fen=chess.STARTING_FEN,history=[],last_uci="",
                status="Waiting for opponent...",game_over=False,page="game",clicked_sq=None)
            st.rerun()
        jid=st.text_input("Game ID to join",key="ljid",placeholder="e.g. a3f7b2c1")
        if st.button("Join",key="ljbtn"):
            games=load_games(); g=games.get(jid)
            if not g or g["status"]!="waiting": st.error("Game not found or already started.")
            elif g["white"]==st.session_state.username: st.error("You created this game.")
            else:
                g["black"]=st.session_state.username; g["status"]="active"; save_games(games)
                mv=g["moves"]
                st.session_state.update(gid=jid,my_color=chess.BLACK,opponent=g["white"],
                    mode="multiplayer",fen=g["fen"],history=mv,last_uci=mv[-1] if mv else "",
                    status="Your move" if chess.Board(g["fen"]).turn==chess.BLACK else "Opponent's turn",
                    game_over=False,page="game",clicked_sq=None)
                st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)
    games=load_games()
    og=[(gid,d) for gid,d in games.items() if d["status"]=="waiting" and d["white"]!=st.session_state.username]
    if og:
        st.markdown("### Open games")
        for gid,g in og[:8]:
            ca,cb=st.columns([3,1])
            ca.markdown(f"**{g['white']}** · {g['created'][:10]}")
            if cb.button("Join",key="oj_"+gid):
                g["black"]=st.session_state.username; g["status"]="active"; games[gid]=g; save_games(games)
                st.session_state.update(gid=gid,my_color=chess.BLACK,opponent=g["white"],
                    mode="multiplayer",fen=g["fen"],history=[],last_uci="",
                    status="Opponent's turn",game_over=False,page="game",clicked_sq=None)
                st.rerun()

def page_game():
    board=chess.Board(st.session_state.fen)
    pc=st.session_state.my_color
    is_my_turn=(board.turn==pc and not st.session_state.game_over)

    with st.sidebar:
        st.markdown(f"**{st.session_state.username}** vs **{st.session_state.opponent}**")
        st.markdown("---")
        if st.button("Back to Lobby",key="sl"): st.session_state.page="lobby"; st.rerun()
        if st.button("Resign",key="sr"):        st.session_state.page="lobby"; st.rerun()
        st.markdown("---")
        mi=st.text_input("Move (UCI or SAN)",placeholder="e2e4 or Nf3",key="mi")
        if st.button("Submit move",key="sm"):
            if is_my_turn:
                err=uci_move(mi)
                if err: st.session_state.status=err
            st.rerun()
        st.markdown("---")
        hist=st.session_state.history
        if hist:
            rows=[]
            for i in range(0,len(hist),2):
                w=hist[i]; b=hist[i+1] if i+1<len(hist) else "..."
                rows.append(f"{i//2+1}. <span>{w}</span> <span>{b}</span>")
            st.markdown('<div class="mlist">'+"<br>".join(rows)+"</div>",unsafe_allow_html=True)

    col_board,col_info=st.columns([1.9,1],gap="large")

    with col_board:
        whose="Your turn ✅" if is_my_turn else "Opponent's turn ⏳"
        if st.session_state.game_over: whose=st.session_state.status
        st.markdown(f'<div class="pill">⚡ {whose}</div>',unsafe_allow_html=True)
        render_board()

    with col_info:
        st.markdown('<div class="card">',unsafe_allow_html=True)
        st.markdown('<div class="ct">Game info</div>',unsafe_allow_html=True)
        st.markdown(f"**Mode:** {'vs Bot' if st.session_state.mode=='bot' else 'Multiplayer'}")
        st.markdown(f"**You:** {'⬜ White' if pc==chess.WHITE else '⬛ Black'}")
        st.markdown(f"**Opponent:** {st.session_state.opponent}")
        if st.session_state.mode=="multiplayer" and st.session_state.gid:
            st.markdown(f"**Game ID:** `{st.session_state.gid}`")
        st.markdown("</div>",unsafe_allow_html=True)
        if board.is_check() and not board.is_checkmate(): st.warning("♚ Check!")
        if st.session_state.game_over:
            r=board.result()
            st.success({"1-0":"⬜ White wins!","0-1":"⬛ Black wins!","1/2-1/2":"Draw"}.get(r,r))
            if st.button("Back to Lobby",key="btl"): st.session_state.page="lobby"; st.rerun()
        PU={"P":"♙","p":"♟","N":"♘","n":"♞","B":"♗","b":"♝","R":"♖","r":"♜","Q":"♕","q":"♛"}
        S={"P":8,"N":2,"B":2,"R":2,"Q":1,"p":8,"n":2,"b":2,"r":2,"q":1}
        cur={}
        for sq in chess.SQUARES:
            p=board.piece_at(sq)
            if p: cur[p.symbol()]=cur.get(p.symbol(),0)+1
        wc,bc=[],[]
        for sym,n in S.items():
            for _ in range(n-cur.get(sym,0)):
                (bc if sym.isupper() else wc).append(PU[sym])
        st.markdown(f"**White captured:** {''.join(bc) or '–'}")
        st.markdown(f"**Black captured:** {''.join(wc) or '–'}")
        if st.session_state.mode=="multiplayer" and not st.session_state.game_over and not is_my_turn:
            g=load_games().get(st.session_state.gid)
            if g and len(g["moves"])>len(st.session_state.history):
                mv=g["moves"]
                st.session_state.history=mv; st.session_state.fen=g["fen"]
                st.session_state.last_uci=mv[-1] if mv else ""
                if g["status"]=="finished":
                    st.session_state.game_over=True; st.session_state.status="Game over: "+g["result"]
                else: st.session_state.status="Your move"
                st.rerun()
            if st.button("Refresh",key="poll"): st.rerun()

    if (st.session_state.mode=="bot" and not st.session_state.game_over
            and board.turn!=pc and st.session_state.status=="Bot thinking..."):
        with st.spinner("Bot thinking..."):
            time.sleep(0.3)
            bm=get_bot_move(board)
            if bm: push_move(board,bm)
        st.rerun()

def page_admin():
    st.markdown("## 🛡 Admin Panel")
    users=load_users(); games=load_games()
    t1,t2=st.tabs(["👤 Users","🎮 Games"])
    with t1:
        for uname,ud in users.items():
            c1,c2,c3,c4=st.columns([2,1.4,1.2,.8])
            b='<span class="badge badge-admin">admin</span>' if ud["role"]=="admin" else '<span class="badge">player</span>'
            c1.markdown(f"**{uname}** {b}",unsafe_allow_html=True)
            c2.markdown(f"W{ud.get('wins',0)} L{ud.get('losses',0)} D{ud.get('draws',0)}")
            c3.markdown(f"<small style='color:#555'>{ud.get('created','')[:10]}</small>",unsafe_allow_html=True)
            if uname!="admin" and c4.button("🗑",key="del_"+uname):
                del users[uname]; save_users(users); st.rerun()
        st.markdown("---"); st.markdown("### ➕ Add user")
        a1,a2,a3=st.columns(3)
        an=a1.text_input("Username",key="an"); ap=a2.text_input("Password",type="password",key="ap")
        ar=a3.selectbox("Role",["player","admin"],key="ar")
        if st.button("Add user",key="au"):
            if an in users: st.error("Taken.")
            elif len(an)<3 or len(ap)<6: st.error("Too short.")
            else:
                users[an]={"password":_hash(ap),"role":ar,"created":datetime.now().isoformat(),
                           "wins":0,"losses":0,"draws":0}
                save_users(users); st.success(f"Added {an}."); st.rerun()
    with t2:
        for gid,g in list(games.items())[-20:]:
            st.markdown(f"`{gid}` {g['white']} vs {g['black'] or '?'} · {g['status']} · {g.get('result','–')}")
        if games and st.button("Clear finished",key="cf"):
            save_games({k:v for k,v in games.items() if v["status"]!="finished"}); st.rerun()

# ── board move bridge (JS board posts moves via URL query params) ─────────────
_qp = st.query_params
_frm, _to, _promo = _qp.get("frm"), _qp.get("to"), _qp.get("promo")
if _frm and _to and st.session_state.get("logged_in") and st.session_state.page == "game":
    apply_move(_frm, _to, _promo)
    st.query_params.clear()
    st.rerun()
elif _frm or _to or _promo:
    st.query_params.clear()

# ── nav + router ──────────────────────────────────────────────────────────────
if st.session_state.logged_in:
    with st.sidebar:
        st.markdown("### ♟ Chess")
        st.markdown(f"**{st.session_state.username}**")
        if st.session_state.role=="admin":
            st.markdown('<span class="badge badge-admin">admin</span>',unsafe_allow_html=True)
        st.markdown("---")
        if st.button("🏠 Lobby",key="nl"):  st.session_state.page="lobby"; st.rerun()
        if st.session_state.role=="admin":
            if st.button("🛡 Admin",key="na"): st.session_state.page="admin"; st.rerun()
        st.markdown("---")
        if st.button("🚪 Log out",key="nlo"): do_logout(); st.rerun()

pg=st.session_state.page
if   not st.session_state.logged_in: page_auth()
elif pg=="lobby":  page_lobby()
elif pg=="game":   page_game()
elif pg=="admin":
    if st.session_state.role=="admin": page_admin()
    else: st.session_state.page="lobby"; st.rerun()
else: page_lobby()
