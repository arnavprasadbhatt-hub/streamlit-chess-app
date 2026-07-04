"""
♟️  Chess Platform  –  ~1000 ELO Bot  +  Multiplayer  +  Admin
=================================================================
Single unified interactive canvas board — no secondary grid.
Run:  streamlit run app.py
"""

import streamlit as st
import streamlit.components.v1 as components
import chess
import random, time, json, hashlib, uuid
from datetime import datetime
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_DIR   = Path("data")
USERS_FILE = DATA_DIR / "users.json"
GAMES_FILE = DATA_DIR / "games.json"
DATA_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="♟️ Chess Platform", page_icon="♟️", layout="wide")

# ══════════════════════════════════════════════════════════════════════════════
#  GLOBAL CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;800&family=JetBrains+Mono:wght@400;600&display=swap');
html,body,[class*="css"]{font-family:'Syne',sans-serif;background:#0d0d10;color:#e6e2db;}
.stApp{background:#0d0d10;}
.card{background:#17171d;border:1px solid #2a2a35;border-radius:10px;padding:1.4rem 1.8rem;margin-bottom:1rem;}
.card-title{font-size:1rem;font-weight:800;letter-spacing:.07em;text-transform:uppercase;color:#e6b84a;margin-bottom:.7rem;}
.status-pill{display:block;background:#1e1e28;border-left:3px solid #e6b84a;border-radius:4px;padding:.4rem .9rem;font-family:'JetBrains Mono',monospace;font-size:.82rem;color:#e6b84a;margin:.5rem 0 .9rem;}
div.stButton>button{background:#e6b84a!important;color:#0d0d10!important;font-family:'Syne',sans-serif!important;font-weight:800!important;border:none!important;border-radius:5px!important;padding:.45rem 1.2rem!important;letter-spacing:.04em!important;transition:opacity .15s!important;}
div.stButton>button:hover{opacity:.78!important;}
div[data-baseweb="input"] input{background:#1e1e28!important;color:#e6e2db!important;border:1px solid #2a2a35!important;border-radius:5px!important;font-family:'Syne',sans-serif!important;}
div[data-baseweb="tab-list"]{background:#17171d!important;border-radius:8px!important;padding:4px!important;gap:4px!important;}
button[data-baseweb="tab"]{background:transparent!important;color:#888!important;border-radius:6px!important;font-family:'Syne',sans-serif!important;font-weight:600!important;}
button[data-baseweb="tab"][aria-selected="true"]{background:#e6b84a!important;color:#0d0d10!important;}
section[data-testid="stSidebar"]{background:#111116!important;}
section[data-testid="stSidebar"] *{color:#e6e2db!important;}
.move-list{font-family:'JetBrains Mono',monospace;font-size:.76rem;color:#888;max-height:200px;overflow-y:auto;background:#0d0d10;border-radius:6px;padding:.5rem .8rem;line-height:1.9;}
.move-list span{color:#e6e2db;}
.logo{font-size:2.2rem;font-weight:800;letter-spacing:-.02em;}
.logo span{color:#e6b84a;}
.badge{background:#2a2a35;border-radius:20px;padding:2px 10px;font-size:.74rem;color:#e6b84a;}
.badge-admin{background:#e6b84a22;border:1px solid #e6b84a55;}
#MainMenu,footer,header{visibility:hidden;}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  USER STORE
# ══════════════════════════════════════════════════════════════════════════════
def _hash(pw): return hashlib.sha256(pw.encode()).hexdigest()

def load_users():
    if USERS_FILE.exists(): return json.loads(USERS_FILE.read_text())
    u = {"admin":{"password":_hash("admin123"),"role":"admin","created":datetime.now().isoformat(),"wins":0,"losses":0,"draws":0}}
    save_users(u); return u

def save_users(u): USERS_FILE.write_text(json.dumps(u, indent=2))

def load_games():
    return json.loads(GAMES_FILE.read_text()) if GAMES_FILE.exists() else {}

def save_games(g): GAMES_FILE.write_text(json.dumps(g, indent=2))


# ══════════════════════════════════════════════════════════════════════════════
#  CHESS ENGINE  (~1000 ELO)
# ══════════════════════════════════════════════════════════════════════════════
PST = {
    chess.PAWN:   [ 0, 0, 0, 0, 0, 0, 0, 0,50,50,50,50,50,50,50,50,10,10,20,30,30,20,10,10,
                    5, 5,10,25,25,10, 5, 5, 0, 0, 0,20,20, 0, 0, 0, 5,-5,-10,0,0,-10,-5,5,
                    5,10,10,-20,-20,10,10,5, 0, 0, 0, 0, 0, 0, 0, 0],
    chess.KNIGHT: [-50,-40,-30,-30,-30,-30,-40,-50,-40,-20,0,0,0,0,-20,-40,-30,0,10,15,15,10,0,-30,
                   -30,5,15,20,20,15,5,-30,-30,0,15,20,20,15,0,-30,-30,5,10,15,15,10,5,-30,
                   -40,-20,0,5,5,0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50],
    chess.BISHOP: [-20,-10,-10,-10,-10,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,10,10,5,0,-10,
                   -10,5,5,10,10,5,5,-10,-10,0,10,10,10,10,0,-10,-10,10,10,10,10,10,10,-10,
                   -10,5,0,0,0,0,5,-10,-20,-10,-10,-10,-10,-10,-10,-20],
    chess.ROOK:   [0,0,0,0,0,0,0,0,5,10,10,10,10,10,10,5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,
                   -5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,0,0,0,5,5,0,0,0],
    chess.QUEEN:  [-20,-10,-10,-5,-5,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,5,5,5,0,-10,-5,0,5,5,5,5,0,-5,
                    0,0,5,5,5,5,0,-5,-10,5,5,5,5,5,0,-10,-10,0,5,0,0,0,0,-10,-20,-10,-10,-5,-5,-10,-10,-20],
    chess.KING:   [-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,
                   -30,-40,-40,-50,-50,-40,-40,-30,-20,-30,-30,-40,-40,-30,-30,-20,-10,-20,-20,-20,-20,-20,-20,-10,
                    20,20,0,0,0,0,20,20,20,30,10,0,0,10,30,20],
}
PV = {chess.PAWN:100,chess.KNIGHT:320,chess.BISHOP:330,chess.ROOK:500,chess.QUEEN:900,chess.KING:20000}

def pst_score(pt,sq,color):
    t=PST.get(pt,[0]*64)
    return t[sq if color==chess.WHITE else chess.square_mirror(sq)]

def evaluate(board):
    if board.is_checkmate(): return -99999 if board.turn==chess.WHITE else 99999
    if board.is_stalemate() or board.is_insufficient_material(): return 0
    s=0
    for sq in chess.SQUARES:
        p=board.piece_at(sq)
        if p:
            v=PV[p.piece_type]+pst_score(p.piece_type,sq,p.color)
            s+=v if p.color==chess.WHITE else -v
    return s

def order_moves(board):
    def pri(m):
        if board.is_capture(m):
            vic=board.piece_at(m.to_square); att=board.piece_at(m.from_square)
            return (PV[vic.piece_type]-PV[att.piece_type]//10) if vic and att else 100
        board.push(m); c=board.is_check(); board.pop()
        return 50 if c else 0
    return sorted(board.legal_moves,key=pri,reverse=True)

def minimax(board,depth,alpha,beta,maxi):
    if depth==0 or board.is_game_over(): return evaluate(board)
    if maxi:
        best=-999999
        for m in order_moves(board):
            board.push(m); best=max(best,minimax(board,depth-1,alpha,beta,False)); board.pop()
            alpha=max(alpha,best)
            if beta<=alpha: break
        return best
    else:
        best=999999
        for m in order_moves(board):
            board.push(m); best=min(best,minimax(board,depth-1,alpha,beta,True)); board.pop()
            beta=min(beta,best)
            if beta<=alpha: break
        return best

def get_bot_move(board,depth=2,blunder_rate=0.25):
    legal=list(board.legal_moves)
    if not legal: return None
    if random.random()<blunder_rate: return random.choice(legal)
    best_move,best_val=None,-999999
    for m in order_moves(board):
        board.push(m)
        v=minimax(board,depth-1,-999999,999999,board.turn==chess.WHITE)
        board.pop()
        if v>best_val: best_val,best_move=v,m
    return best_move or random.choice(legal)


# ══════════════════════════════════════════════════════════════════════════════
#  SINGLE UNIFIED CANVAS BOARD
#  Renders entirely in HTML5 Canvas — click fires postMessage → query_param
# ══════════════════════════════════════════════════════════════════════════════
def build_board_component(fen, flipped, selected_sq, legal_dests, last_move_uci, is_my_turn, game_over):
    board = chess.Board(fen)

    # Serialize board state for JS
    pieces_js = []
    PIECE_CHARS = {
        (chess.PAWN,   chess.WHITE):"P",(chess.PAWN,   chess.BLACK):"p",
        (chess.KNIGHT, chess.WHITE):"N",(chess.KNIGHT, chess.BLACK):"n",
        (chess.BISHOP, chess.WHITE):"B",(chess.BISHOP, chess.BLACK):"b",
        (chess.ROOK,   chess.WHITE):"R",(chess.ROOK,   chess.BLACK):"r",
        (chess.QUEEN,  chess.WHITE):"Q",(chess.QUEEN,  chess.BLACK):"q",
        (chess.KING,   chess.WHITE):"K",(chess.KING,   chess.BLACK):"k",
    }
    for sq in chess.SQUARES:
        p = board.piece_at(sq)
        if p:
            pieces_js.append({"sq": sq, "sym": PIECE_CHARS[(p.piece_type, p.color)]})

    in_check = board.is_check()
    king_sq = board.king(board.turn) if in_check else -1

    last_from, last_to = -1, -1
    if last_move_uci and len(last_move_uci) >= 4:
        try:
            lm = chess.Move.from_uci(last_move_uci)
            last_from, last_to = lm.from_square, lm.to_square
        except: pass

    pieces_json   = json.dumps(pieces_js)
    legal_json    = json.dumps(list(legal_dests))
    sel           = selected_sq if selected_sq is not None else -1
    flipped_js    = "true" if flipped else "false"
    my_turn_js    = "true" if is_my_turn and not game_over else "false"

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  *{{margin:0;padding:0;box-sizing:border-box;}}
  body{{background:#0d0d10;display:flex;justify-content:center;align-items:flex-start;padding:8px;}}
  #wrap{{position:relative;user-select:none;}}
  canvas{{display:block;border-radius:6px;}}
  #overlay{{position:absolute;top:0;left:0;cursor:pointer;}}
  #promo-modal{{display:none;position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
    background:#1e1e28;border:2px solid #e6b84a;border-radius:10px;padding:14px 20px;
    z-index:10;text-align:center;font-family:'Syne',sans-serif;}}
  #promo-modal p{{color:#e6b84a;font-weight:700;font-size:.9rem;margin-bottom:10px;}}
  .promo-btn{{font-size:2rem;background:none;border:2px solid #2a2a35;border-radius:6px;
    cursor:pointer;margin:3px;padding:4px 10px;color:#e6e2db;transition:border-color .2s;}}
  .promo-btn:hover{{border-color:#e6b84a;}}
</style>
</head>
<body>
<div id="wrap">
  <canvas id="board"></canvas>
  <canvas id="overlay"></canvas>
  <div id="promo-modal">
    <p>Choose promotion piece</p>
    <button class="promo-btn" data-piece="q">♛</button>
    <button class="promo-btn" data-piece="r">♜</button>
    <button class="promo-btn" data-piece="b">♝</button>
    <button class="promo-btn" data-piece="n">♞</button>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/streamlit-component-lib@1.4.0/streamlit.js"></script>
<script>
// ── Config ────────────────────────────────────────────────────────────────────
const FLIPPED    = {flipped_js};
const MY_TURN    = {my_turn_js};
const SEL_SQ     = {sel};
const LAST_FROM  = {last_from};
const LAST_TO    = {last_to};
const KING_SQ    = {king_sq};   // -1 if not in check
const PIECES     = {pieces_json};
const LEGAL_DESTS= new Set({legal_json});

// Responsive sizing
const MAX_SIZE = Math.min(window.innerWidth - 20, 560);
const SZ = Math.floor(MAX_SIZE / 8) * 8;   // board px (multiple of 8)
const SQ = SZ / 8;                          // square px
const COORD_PAD = Math.round(SQ * 0.22);   // space for rank/file labels

// ── Canvas setup ──────────────────────────────────────────────────────────────
const wrap = document.getElementById('wrap');
wrap.style.width  = (SZ + COORD_PAD) + 'px';
wrap.style.height = (SZ + COORD_PAD) + 'px';

const bc = document.getElementById('board');
bc.width = bc.height = SZ + COORD_PAD;

const oc = document.getElementById('overlay');
oc.width = oc.height = SZ + COORD_PAD;
oc.style.width  = (SZ + COORD_PAD) + 'px';
oc.style.height = (SZ + COORD_PAD) + 'px';

const ctx  = bc.getContext('2d');
const octx = oc.getContext('2d');

// ── Piece images (Unicode on canvas) ─────────────────────────────────────────
const PIECE_UNICODE = {{
  'P':'♙','p':'♟','N':'♘','n':'♞','B':'♗','b':'♝',
  'R':'♖','r':'♜','Q':'♕','q':'♛','K':'♔','k':'♚'
}};

// ── Coordinate helpers ────────────────────────────────────────────────────────
function sqToXY(sq) {{
  const file = sq % 8;
  const rank = Math.floor(sq / 8);
  const col  = FLIPPED ? 7 - file : file;
  const row  = FLIPPED ? rank     : 7 - rank;
  return {{ x: COORD_PAD + col * SQ, y: row * SQ }};
}}

function xyToSq(px, py) {{
  const col = Math.floor((px - COORD_PAD) / SQ);
  const row = Math.floor(py / SQ);
  if (col < 0 || col > 7 || row < 0 || row > 7) return -1;
  const file = FLIPPED ? 7 - col : col;
  const rank = FLIPPED ? row     : 7 - row;
  return rank * 8 + file;
}}

// ── Draw board ────────────────────────────────────────────────────────────────
function drawBoard() {{
  ctx.clearRect(0, 0, bc.width, bc.height);

  // Coordinates background strip
  ctx.fillStyle = '#17171d';
  ctx.fillRect(0, 0, bc.width, bc.height);

  for (let row = 0; row < 8; row++) {{
    for (let col = 0; col < 8; col++) {{
      const file = FLIPPED ? 7 - col : col;
      const rank = FLIPPED ? row     : 7 - row;
      const sq   = rank * 8 + file;
      const x    = COORD_PAD + col * SQ;
      const y    = row * SQ;
      const light = (file + rank) % 2 === 0;

      // Base square color
      let color = light ? '#f0d9b5' : '#b58863';

      // Last move highlight
      if (sq === LAST_FROM || sq === LAST_TO) {{
        color = light ? '#cdd26a' : '#aaa23a';
      }}

      // Selected square
      if (sq === SEL_SQ) {{
        color = '#4fc3f7';
      }}

      // Check highlight
      if (sq === KING_SQ) {{
        color = '#e53935';
      }}

      ctx.fillStyle = color;
      ctx.fillRect(x, y, SQ, SQ);

      // Legal destination dots / rings
      if (LEGAL_DESTS.has(sq)) {{
        const piece = PIECES.find(p => p.sq === sq);
        ctx.save();
        if (piece) {{
          // Capture ring
          ctx.strokeStyle = 'rgba(76,195,247,0.55)';
          ctx.lineWidth   = SQ * 0.1;
          ctx.beginPath();
          ctx.arc(x + SQ/2, y + SQ/2, SQ * 0.42, 0, Math.PI*2);
          ctx.stroke();
        }} else {{
          // Move dot
          ctx.fillStyle = 'rgba(76,195,247,0.45)';
          ctx.beginPath();
          ctx.arc(x + SQ/2, y + SQ/2, SQ * 0.16, 0, Math.PI*2);
          ctx.fill();
        }}
        ctx.restore();
      }}

      // Rank labels (left edge)
      if (col === 0) {{
        ctx.fillStyle = light ? '#b58863' : '#f0d9b5';
        ctx.font      = `bold ${{Math.round(SQ*0.22)}}px 'JetBrains Mono', monospace`;
        ctx.textAlign = 'left';
        ctx.textBaseline = 'top';
        const rankLabel = rank + 1;
        ctx.fillText(rankLabel, 3, y + 3);
      }}

      // File labels (bottom edge)
      if (row === 7) {{
        ctx.fillStyle = light ? '#b58863' : '#f0d9b5';
        ctx.font      = `bold ${{Math.round(SQ*0.22)}}px 'JetBrains Mono', monospace`;
        ctx.textAlign = 'right';
        ctx.textBaseline = 'bottom';
        const fileLabel = String.fromCharCode(97 + (FLIPPED ? 7 - col : col));
        ctx.fillText(fileLabel, x + SQ - 3, y + SQ - 2);
      }}
    }}
  }}

  // Draw pieces
  ctx.textAlign    = 'center';
  ctx.textBaseline = 'middle';
  const pieceFontSize = Math.round(SQ * 0.72);
  ctx.font = `${{pieceFontSize}}px serif`;

  for (const {{sq, sym}} of PIECES) {{
    if (sq === SEL_SQ) continue; // draw selected piece last (dragged feel)
    const {{x, y}} = sqToXY(sq);
    const isWhite = sym === sym.toUpperCase();

    // Drop shadow for depth
    ctx.save();
    ctx.shadowColor   = 'rgba(0,0,0,0.45)';
    ctx.shadowBlur    = SQ * 0.12;
    ctx.shadowOffsetX = SQ * 0.03;
    ctx.shadowOffsetY = SQ * 0.05;
    ctx.fillStyle = isWhite ? '#fff8f0' : '#1a1008';
    ctx.fillText(PIECE_UNICODE[sym], x + SQ/2, y + SQ/2 + SQ*0.03);
    ctx.restore();

    // Crisp outline for contrast
    ctx.save();
    ctx.strokeStyle = isWhite ? '#8b6914' : '#e6d4b0';
    ctx.lineWidth   = SQ * 0.025;
    ctx.font        = `${{pieceFontSize}}px serif`;
    ctx.strokeText(PIECE_UNICODE[sym], x + SQ/2, y + SQ/2 + SQ*0.03);
    ctx.restore();
  }}

  // Draw selected piece on top with glow
  if (SEL_SQ >= 0) {{
    const selPiece = PIECES.find(p => p.sq === SEL_SQ);
    if (selPiece) {{
      const {{x, y}} = sqToXY(SEL_SQ);
      const isWhite = selPiece.sym === selPiece.sym.toUpperCase();
      ctx.save();
      ctx.shadowColor = '#4fc3f7';
      ctx.shadowBlur  = SQ * 0.35;
      ctx.fillStyle   = isWhite ? '#fff8f0' : '#1a1008';
      ctx.font        = `${{pieceFontSize}}px serif`;
      ctx.fillText(PIECE_UNICODE[selPiece.sym], x + SQ/2, y + SQ/2 + SQ*0.03);
      ctx.restore();
    }}
  }}

  // Arrow for last move
  if (LAST_FROM >= 0 && LAST_TO >= 0) {{
    drawArrow(LAST_FROM, LAST_TO, 'rgba(230,184,74,0.55)');
  }}
}}

function drawArrow(fromSq, toSq, color) {{
  const f = sqToXY(fromSq);
  const t = sqToXY(toSq);
  const fx = f.x + SQ/2, fy = f.y + SQ/2;
  const tx = t.x + SQ/2, ty = t.y + SQ/2;

  const angle   = Math.atan2(ty - fy, tx - fx);
  const headLen = SQ * 0.28;
  const tailEnd = {{x: tx - Math.cos(angle)*SQ*0.38, y: ty - Math.sin(angle)*SQ*0.38}};

  ctx.save();
  ctx.strokeStyle = color;
  ctx.fillStyle   = color;
  ctx.lineWidth   = SQ * 0.10;
  ctx.lineCap     = 'round';

  ctx.beginPath();
  ctx.moveTo(fx, fy);
  ctx.lineTo(tailEnd.x, tailEnd.y);
  ctx.stroke();

  // Arrowhead
  ctx.beginPath();
  ctx.moveTo(tx - Math.cos(angle - 0.4)*headLen, ty - Math.sin(angle - 0.4)*headLen);
  ctx.lineTo(tx, ty);
  ctx.lineTo(tx - Math.cos(angle + 0.4)*headLen, ty - Math.sin(angle + 0.4)*headLen);
  ctx.closePath();
  ctx.fill();
  ctx.restore();
}}

// ── Hover effect on overlay canvas ───────────────────────────────────────────
oc.addEventListener('mousemove', function(e) {{
  if (!MY_TURN) return;
  const r   = oc.getBoundingClientRect();
  const sq  = xyToSq(e.clientX - r.left, e.clientY - r.top);
  octx.clearRect(0, 0, oc.width, oc.height);
  if (sq >= 0) {{
    const piece = PIECES.find(p => p.sq === sq);
    if (piece || LEGAL_DESTS.has(sq)) {{
      const {{x, y}} = sqToXY(sq);
      octx.fillStyle = 'rgba(255,255,255,0.08)';
      octx.fillRect(x, y, SQ, SQ);
    }}
  }}
}});

oc.addEventListener('mouseleave', () => octx.clearRect(0, 0, oc.width, oc.height));

// ── Click → send square index to Streamlit via query param ───────────────────
let pendingPromoMove = null;  // [fromSq, toSq]

oc.addEventListener('click', function(e) {{
  if (!MY_TURN) return;
  const r  = oc.getBoundingClientRect();
  const sq = xyToSq(e.clientX - r.left, e.clientY - r.top);
  if (sq < 0) return;

  // Check if this is a pawn promotion move
  if (SEL_SQ >= 0 && LEGAL_DESTS.has(sq)) {{
    const selPiece = PIECES.find(p => p.sq === SEL_SQ);
    if (selPiece && selPiece.sym.toLowerCase() === 'p') {{
      const destRank = Math.floor(sq / 8);
      if (destRank === 0 || destRank === 7) {{
        pendingPromoMove = [SEL_SQ, sq];
        document.getElementById('promo-modal').style.display = 'block';
        return;
      }}
    }}
  }}

  sendMove(sq, null);
}});

document.querySelectorAll('.promo-btn').forEach(btn => {{
  btn.addEventListener('click', function() {{
    const piece = this.dataset.piece;
    document.getElementById('promo-modal').style.display = 'none';
    if (pendingPromoMove) {{
      const toSq = pendingPromoMove[1];
      pendingPromoMove = null;
      sendMove(toSq, piece);
    }}
  }});
}});

function sendMove(sq, promoChar) {{
  // Send move via Streamlit component API
  const moveData = sq + '|' + (promoChar || '') + '|' + Date.now();
  try {{
    if (window.Streamlit) {{
      Streamlit.setComponentValue(moveData);
    }} else {{
      console.error('Streamlit component API not loaded');
    }}
  }} catch (err) {{
    console.error('Could not deliver move:', err);
  }}
}}

// ── Initial draw ──────────────────────────────────────────────────────────────
drawBoard();
</script>
</body>
</html>"""
    return html


# ══════════════════════════════════════════════════════════════════════════════
#  SESSION DEFAULTS
# ══════════════════════════════════════════════════════════════════════════════
def session_defaults():
    defaults = dict(
        logged_in=False, username=None, role=None, page="auth",
        board_fen=chess.STARTING_FEN, player_color=chess.WHITE,
        move_history=[], selected_sq=None, status="Your move",
        game_over=False, last_move_uci="", game_mode="bot",
        game_id=None, opponent=None,
    )
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

session_defaults()


# ══════════════════════════════════════════════════════════════════════════════
#  CLICK HANDLER
# ══════════════════════════════════════════════════════════════════════════════
def handle_square_click(sq, promo_char=None):
    board = chess.Board(st.session_state.board_fen)
    pc    = st.session_state.player_color
    selected = st.session_state.selected_sq

    if selected is None:
        piece = board.piece_at(sq)
        if piece and piece.color == pc and board.turn == pc:
            st.session_state.selected_sq = sq
        return

    # Build move
    promo = None
    if promo_char:
        promo = {"q":chess.QUEEN,"r":chess.ROOK,"b":chess.BISHOP,"n":chess.KNIGHT}.get(promo_char, chess.QUEEN)
    else:
        sel_piece = board.piece_at(selected)
        if sel_piece and sel_piece.piece_type == chess.PAWN and chess.square_rank(sq) in (0,7):
            promo = chess.QUEEN  # auto-queen if no dialog answer yet

    move = chess.Move(selected, sq, promotion=promo)
    if move not in board.legal_moves:
        move = chess.Move(selected, sq)

    if move in board.legal_moves:
        board.push(move)
        st.session_state.board_fen     = board.fen()
        st.session_state.move_history.append(move.uci())
        st.session_state.last_move_uci = move.uci()
        st.session_state.selected_sq   = None

        if board.is_game_over():
            st.session_state.game_over = True
            st.session_state.status    = "Game over · " + board.result()
            _handle_game_end(board.result())
        elif st.session_state.game_mode == "bot":
            st.session_state.status = "Bot thinking…"
        else:
            push_mp_move(st.session_state.game_id, move.uci())
            st.session_state.status = "Opponent's turn"
    else:
        # Re-select own piece
        piece = board.piece_at(sq)
        if piece and piece.color == pc:
            st.session_state.selected_sq = sq
        else:
            st.session_state.selected_sq = None

# ══════════════════════════════════════════════════════════════════════════════
#  AUTH / GAME HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def login(username, password):
    users = load_users()
    u = users.get(username)
    if u and u["password"] == _hash(password):
        st.session_state.logged_in = True
        st.session_state.username  = username
        st.session_state.role      = u["role"]
        st.session_state.page      = "lobby"
        return True
    return False

def register(username, password):
    users = load_users()
    if username in users:        return False, "Username already taken."
    if len(username) < 3:        return False, "Username must be ≥ 3 characters."
    if len(password) < 6:        return False, "Password must be ≥ 6 characters."
    users[username] = {"password":_hash(password),"role":"player",
                       "created":datetime.now().isoformat(),"wins":0,"losses":0,"draws":0}
    save_users(users)
    return True, "Account created — please log in."

def logout():
    for k in list(st.session_state.keys()): del st.session_state[k]
    session_defaults()

def start_bot_game(color_choice):
    st.session_state.update(board_fen=chess.STARTING_FEN,
        player_color=chess.WHITE if color_choice=="White" else chess.BLACK,
        move_history=[],selected_sq=None,status="Your move",
        game_over=False,last_move_uci="",game_mode="bot",
        game_id=None,opponent="Bot (~1000 ELO)",page="game")

def create_multiplayer_game():
    games = load_games(); gid = str(uuid.uuid4())[:8]
    games[gid] = {"white":st.session_state.username,"black":None,
                  "fen":chess.STARTING_FEN,"moves":[],"status":"waiting",
                  "result":None,"created":datetime.now().isoformat()}
    save_games(games); return gid

def join_multiplayer_game(gid):
    games = load_games(); g = games.get(gid)
    if not g:                                  return False, "Game not found."
    if g["status"] != "waiting":               return False, "Game already started or finished."
    if g["white"] == st.session_state.username:return False, "You created this game — share the ID with a friend."
    g["black"] = st.session_state.username; g["status"] = "active"
    save_games(games); return True, g

def load_mp_game(gid):
    return load_games().get(gid)

def push_mp_move(gid, move_uci):
    games = load_games(); g = games.get(gid)
    if not g: return
    board = chess.Board(g["fen"])
    try:
        move = chess.Move.from_uci(move_uci)
        if move in board.legal_moves:
            board.push(move); g["fen"] = board.fen(); g["moves"].append(move_uci)
            if board.is_game_over(): g["status"]="finished"; g["result"]=board.result()
            save_games(games); return True
    except: pass

def _handle_game_end(result):
    me=st.session_state.username; opp=st.session_state.opponent; pc=st.session_state.player_color
    users=load_users()
    def bump(u,field):
        if u in users: users[u][field]=users[u].get(field,0)+1
    if result=="1/2-1/2":
        bump(me,"draws")
        if opp in users: bump(opp,"draws")
    elif (result=="1-0" and pc==chess.WHITE) or (result=="0-1" and pc==chess.BLACK):
        bump(me,"wins")
        if opp in users: bump(opp,"losses")
    else:
        bump(me,"losses")
        if opp in users: bump(opp,"wins")
    save_users(users)

def update_stats_admin(winner,loser,draw=False):
    users=load_users()
    if draw:
        for u in [winner,loser]:
            if u in users: users[u]["draws"]=users[u].get("draws",0)+1
    else:
        if winner in users: users[winner]["wins"]=users[winner].get("wins",0)+1
        if loser  in users: users[loser]["losses"]=users[loser].get("losses",0)+1
    save_users(users)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: AUTH
# ══════════════════════════════════════════════════════════════════════════════
def page_auth():
    _, col, _ = st.columns([1,1.5,1])
    with col:
        st.markdown('<div class="logo">♟ Chess<span>.</span></div>', unsafe_allow_html=True)
        st.markdown("<p style='color:#555;margin:-4px 0 1.4rem'>Play vs Bot · Challenge a friend</p>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["Log in","Create account"])
        with t1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            u = st.text_input("Username", key="li_u")
            p = st.text_input("Password", type="password", key="li_p")
            if st.button("Log in", key="btn_li"):
                if login(u, p): st.rerun()
                else: st.error("Wrong username or password.")
            st.markdown('</div>', unsafe_allow_html=True)
            st.caption("Default admin → `admin` / `admin123`")
        with t2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            nu=st.text_input("Username",key="ru"); np=st.text_input("Password",type="password",key="rp")
            nc=st.text_input("Confirm password",type="password",key="rc")
            if st.button("Create account",key="btn_reg"):
                if np!=nc: st.error("Passwords don't match.")
                else:
                    ok,msg=register(nu,np)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
            st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: LOBBY
# ══════════════════════════════════════════════════════════════════════════════
def page_lobby():
    users = load_users(); u = users.get(st.session_state.username, {})
    st.markdown(f"## Welcome, **{st.session_state.username}** 👋")
    c1,c2,c3=st.columns(3)
    c1.metric("Wins",u.get("wins",0)); c2.metric("Losses",u.get("losses",0)); c3.metric("Draws",u.get("draws",0))
    st.markdown("---")
    left,right=st.columns(2,gap="large")
    with left:
        st.markdown('<div class="card"><div class="card-title">🤖 vs Bot  (~1000 ELO)</div>',unsafe_allow_html=True)
        cp=st.selectbox("Play as",["White","Black"],key="bc")
        if st.button("Start game",key="sb"): start_bot_game(cp); st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
    with right:
        st.markdown('<div class="card"><div class="card-title">👥 Multiplayer</div>',unsafe_allow_html=True)
        if st.button("Create new game",key="cng"):
            gid=create_multiplayer_game()
            st.session_state.update(game_id=gid,player_color=chess.WHITE,opponent="Waiting for opponent…",
                game_mode="multiplayer",board_fen=chess.STARTING_FEN,move_history=[],
                last_move_uci="",status="Waiting for opponent…",game_over=False,page="game")
            st.rerun()
        st.markdown("<p style='font-size:.83rem;color:#666;margin:.6rem 0 .2rem'>Join with a Game ID:</p>",unsafe_allow_html=True)
        jid=st.text_input("Game ID",key="jid",placeholder="e.g. a3f7b2c1")
        if st.button("Join",key="jbtn"):
            ok,res=join_multiplayer_game(jid)
            if ok:
                mv=res["moves"]
                st.session_state.update(game_id=jid,player_color=chess.BLACK,opponent=res["white"],
                    game_mode="multiplayer",board_fen=res["fen"],move_history=mv,
                    last_move_uci=mv[-1] if mv else "",
                    status="Your move" if chess.Board(res["fen"]).turn==chess.BLACK else "Opponent's turn",
                    game_over=False,page="game")
                st.rerun()
            else: st.error(res)
        st.markdown('</div>',unsafe_allow_html=True)

    games=load_games()
    waiting=[(g,d) for g,d in games.items() if d["status"]=="waiting" and d["white"]!=st.session_state.username]
    if waiting:
        st.markdown("### Open games")
        for gid,g in waiting[:8]:
            ca,cb=st.columns([3,1])
            ca.markdown(f"**{g['white']}** · {g['created'][:10]}")
            if cb.button("Join",key=f"qj_{gid}"):
                ok,res=join_multiplayer_game(gid)
                if ok:
                    st.session_state.update(game_id=gid,player_color=chess.BLACK,opponent=res["white"],
                        game_mode="multiplayer",board_fen=res["fen"],move_history=[],
                        last_move_uci="",status="Opponent's turn",game_over=False,page="game")
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: GAME  (clickable board grid)
# ══════════════════════════════════════════════════════════════════════════════
def render_clickable_board():
    board = chess.Board(st.session_state.board_fen)
    pc = st.session_state.player_color
    is_my_turn = (board.turn == pc)
    selected_sq = st.session_state.selected_sq

    legal_dests = set()
    if selected_sq is not None:
        for move in board.legal_moves:
            if move.from_square == selected_sq:
                legal_dests.add(move.to_square)

    ranks = list(range(7, -1, -1)) if pc == chess.WHITE else list(range(8))
    files = list(range(8)) if pc == chess.WHITE else list(range(7, -1, -1))

    st.markdown(
        """
        <style>
        div[data-testid="stBaseButton-secondary"] > button {
            min-height: 76px !important;
            min-width: 76px !important;
            height: 76px !important;
            width: 76px !important;
            padding: 0 !important;
            font-size: 2.3rem !important;
            line-height: 1 !important;
            border-radius: 8px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.caption("Click a piece, then click a destination square.")
    for rank in ranks:
        cols = st.columns(8, gap="small")
        for idx, file in enumerate(files):
            sq = rank * 8 + file
            piece = board.piece_at(sq)
            label = piece.unicode_symbol() if piece else ""
            if sq == selected_sq:
                label = "●"
            elif sq in legal_dests:
                label = "•"

            square_color = "#f0d9b5" if (file + rank) % 2 == 0 else "#b58863"
            if sq == selected_sq:
                square_color = "#4fc3f7"
            elif sq in legal_dests:
                square_color = "#7ec8e3"

            with cols[idx]:
                if st.button(
                    label,
                    key=f"board_{sq}",
                    use_container_width=True,
                    disabled=st.session_state.game_over or not is_my_turn,
                ):
                    handle_square_click(sq)

                st.markdown(
                    f"<div style='height:0.28rem;background:{square_color};border-radius:0.2rem;margin-top:0.2rem;'></div>",
                    unsafe_allow_html=True,
                )


def page_game():
    board  = chess.Board(st.session_state.board_fen)
    pc     = st.session_state.player_color
    st.session_state.setdefault("board_flipped", False)
    flipped = (pc == chess.BLACK) != st.session_state.board_flipped
    is_my_turn = (board.turn == pc)

    # Sidebar
    with st.sidebar:
        st.markdown(f"### ♟️ {st.session_state.username}")
        st.markdown(f"vs **{st.session_state.opponent}**")
        st.markdown("---")
        if st.button("⬅ Lobby"): st.session_state.page="lobby"; st.rerun()
        if st.button("🏳 Resign"): st.session_state.page="lobby"; st.rerun()
        if st.button("🔄 Flip board"): 
            st.session_state.setdefault("board_flipped", False)
            st.session_state.board_flipped = not st.session_state.board_flipped
            st.rerun()
        st.markdown("---")
        st.markdown("**Keyboard move** *(UCI or SAN)*")
        mi=st.text_input("",placeholder="e.g. e2e4 or Nf3",key="kmi",label_visibility="collapsed")
        if st.button("Submit",key="ksub"):
            if not st.session_state.game_over and is_my_turn:
                try:
                    try:    mv=board.parse_uci(mi)
                    except: mv=board.parse_san(mi)
                    if mv in board.legal_moves:
                        board.push(mv)
                        st.session_state.board_fen=board.fen()
                        st.session_state.move_history.append(mv.uci())
                        st.session_state.last_move_uci=mv.uci()
                        st.session_state.selected_sq=None
                        if board.is_game_over():
                            st.session_state.game_over=True
                            st.session_state.status="Game over · "+board.result()
                            _handle_game_end(board.result())
                        elif st.session_state.game_mode=="bot":
                            st.session_state.status="Bot thinking…"
                        else:
                            push_mp_move(st.session_state.game_id,mv.uci())
                            st.session_state.status="Opponent's turn"
                    else: st.session_state.status="Illegal move"
                except: st.session_state.status="Invalid move"
            st.rerun()
        st.markdown("---")
        st.markdown("**Move history**")
        hist=st.session_state.move_history
        if hist:
            rows=[]
            for i in range(0,len(hist),2):
                w=hist[i]; b=hist[i+1] if i+1<len(hist) else "…"
                rows.append(f"{i//2+1}. <span>{w}</span>&nbsp;&nbsp;<span>{b}</span>")
            st.markdown('<div class="move-list">'+"<br>".join(rows)+"</div>",unsafe_allow_html=True)
        else:
            st.caption("No moves yet.")

    # Main columns
    col_board, col_info = st.columns([2.6, 1], gap="large")

    with col_board:
        legal_dests = set()
        if st.session_state.selected_sq is not None:
            for m in board.legal_moves:
                if m.from_square == st.session_state.selected_sq:
                    legal_dests.add(m.to_square)

        html = build_board_component(
            fen=st.session_state.board_fen,
            flipped=flipped,
            selected_sq=st.session_state.selected_sq,
            legal_dests=legal_dests,
            last_move_uci=st.session_state.last_move_uci,
            is_my_turn=is_my_turn,
            game_over=st.session_state.game_over,
        )
        board_click = components.html(html, height=600, scrolling=False)

        if board_click:
            parts = str(board_click).split("|")
            if len(parts) >= 2:
                try:
                    sq = int(parts[0])
                    promo_char = parts[1] if parts[1] else None
                    handle_square_click(sq, promo_char)
                    st.rerun()
                except Exception:
                    pass

    with col_info:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Game info</div>', unsafe_allow_html=True)
        mode = "vs Bot" if st.session_state.game_mode=="bot" else "Multiplayer"
        st.markdown(f"**Mode:** {mode}")
        st.markdown(f"**You:** {'⬜ White' if pc==chess.WHITE else '⬛ Black'}")
        st.markdown(f"**Opponent:** {st.session_state.opponent}")
        if st.session_state.game_mode=="multiplayer" and st.session_state.game_id:
            st.markdown(f"**Game ID:** `{st.session_state.game_id}`")
            st.caption("Share with your opponent.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="status-pill">⚡ {st.session_state.status}</div>', unsafe_allow_html=True)

        if board.is_check() and not board.is_checkmate():
            st.warning("♚ Check!")
        if st.session_state.game_over:
            r=board.result()
            msgs={"1-0":"⬜ White wins!","0-1":"⬛ Black wins!","1/2-1/2":"½–½ Draw"}
            st.success(f"**{msgs.get(r,r)}**")
            if st.button("Play again",key="pa"): st.session_state.page="lobby"; st.rerun()

        # Multiplayer: poll for opponent's move
        if st.session_state.game_mode=="multiplayer" and not st.session_state.game_over and not is_my_turn:
            g=load_mp_game(st.session_state.game_id)
            if g:
                new_mv=g["moves"]
                if len(new_mv)>len(st.session_state.move_history):
                    st.session_state.move_history=new_mv
                    st.session_state.board_fen=g["fen"]
                    st.session_state.last_move_uci=new_mv[-1] if new_mv else ""
                    if g["status"]=="finished":
                        st.session_state.game_over=True
                        st.session_state.status="Game over · "+g["result"]
                    else:
                        st.session_state.status="Your move"
                    st.rerun()
            if st.button("🔃 Refresh",key="poll"): st.rerun()

        # Captured material display
        st.markdown('<div class="card" style="margin-top:.8rem">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Material</div>', unsafe_allow_html=True)
        PU={"P":"♙","p":"♟","N":"♘","n":"♞","B":"♗","b":"♝","R":"♖","r":"♜","Q":"♕","q":"♛"}
        START_COUNTS={"P":8,"N":2,"B":2,"R":2,"Q":1,"p":8,"n":2,"b":2,"r":2,"q":1}
        current={}
        for sq in chess.SQUARES:
            p=board.piece_at(sq)
            if p:
                sym=p.symbol()
                current[sym]=current.get(sym,0)+1
        white_cap=[]; black_cap=[]
        for sym,start in START_COUNTS.items():
            diff=start-current.get(sym,0)
            for _ in range(diff):
                (black_cap if sym.isupper() else white_cap).append(PU[sym])
        st.markdown(f"White captured: {''.join(black_cap) or '–'}")
        st.markdown(f"Black captured: {''.join(white_cap) or '–'}")
        st.markdown('</div>', unsafe_allow_html=True)

    # Bot move
    if (st.session_state.game_mode=="bot"
            and not st.session_state.game_over
            and board.turn != pc
            and st.session_state.status=="Bot thinking…"):
        with st.spinner("Bot thinking…"):
            time.sleep(0.35)
            bot_mv=get_bot_move(board)
            if bot_mv:
                board.push(bot_mv)
                st.session_state.board_fen=board.fen()
                st.session_state.move_history.append(bot_mv.uci())
                st.session_state.last_move_uci=bot_mv.uci()
                if board.is_game_over():
                    st.session_state.game_over=True
                    st.session_state.status="Game over · "+board.result()
                    _handle_game_end(board.result())
                else:
                    st.session_state.status="Your move"
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: ADMIN
# ══════════════════════════════════════════════════════════════════════════════
def page_admin():
    st.markdown("## 🛡️ Admin Panel")
    users=load_users(); games=load_games()
    t1,t2=st.tabs(["👤 Users","🎮 Games"])
    with t1:
        st.markdown(f"**{len(users)} registered accounts**")
        for uname,ud in users.items():
            c1,c2,c3,c4=st.columns([2,1.4,1.2,0.8])
            badge='<span class="badge badge-admin">admin</span>' if ud["role"]=="admin" else '<span class="badge">player</span>'
            c1.markdown(f"**{uname}** {badge}",unsafe_allow_html=True)
            c2.markdown(f"W{ud.get('wins',0)} L{ud.get('losses',0)} D{ud.get('draws',0)}")
            c3.markdown(f"<span style='font-size:.75rem;color:#555'>{ud.get('created','')[:10]}</span>",unsafe_allow_html=True)
            if uname!="admin":
                if c4.button("🗑",key=f"del_{uname}",help=f"Delete {uname}"):
                    del users[uname]; save_users(users); st.rerun()
            else: c4.markdown("🔒")
        st.markdown("---")
        st.markdown("### ➕ Add user")
        a1,a2,a3=st.columns(3)
        an=a1.text_input("Username",key="an"); ap=a2.text_input("Password",type="password",key="ap")
        ar=a3.selectbox("Role",["player","admin"],key="ar")
        if st.button("Add",key="adm_add"):
            if an in users: st.error("Username taken.")
            elif len(an)<3 or len(ap)<6: st.error("Username ≥3, password ≥6 chars.")
            else:
                users[an]={"password":_hash(ap),"role":ar,"created":datetime.now().isoformat(),"wins":0,"losses":0,"draws":0}
                save_users(users); st.success(f"Added {an} as {ar}."); st.rerun()
    with t2:
        st.markdown(f"**{len(games)} total games**")
        for gid,g in list(games.items())[-25:]:
            st.markdown(f"`{gid}` · **{g['white']}** vs **{g['black'] or '(open)'}** · {g['status']} · {g.get('result','–')} · {g.get('created','')[:10]}")
        if games and st.button("🗑 Clear finished games",key="clfin"):
            save_games({k:v for k,v in games.items() if v["status"]!="finished"})
            st.success("Cleared."); st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR NAV
# ══════════════════════════════════════════════════════════════════════════════
def top_nav():
    if not st.session_state.logged_in: return
    with st.sidebar:
        st.markdown("### ♟ Chess Platform")
        st.markdown(f"**{st.session_state.username}**")
        if st.session_state.role=="admin":
            st.markdown('<span class="badge badge-admin">admin</span>',unsafe_allow_html=True)
        st.markdown("---")
        if st.button("🏠 Lobby",key="nl"): st.session_state.page="lobby"; st.rerun()
        if st.session_state.role=="admin":
            if st.button("🛡 Admin",key="na"): st.session_state.page="admin"; st.rerun()
        st.markdown("---")
        if st.button("🚪 Log out",key="nlo"): logout(); st.rerun()

top_nav()

# ══════════════════════════════════════════════════════════════════════════════
#  ROUTER
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    page_auth()
elif st.session_state.page=="lobby":
    page_lobby()
elif st.session_state.page=="game":
    page_game()
elif st.session_state.page=="admin":
    if st.session_state.role=="admin": page_admin()
    else: st.error("Access denied."); st.session_state.page="lobby"; st.rerun()
else:
    page_lobby()