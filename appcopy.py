"""
♟️  Chess Platform  –  ~1000 ELO Bot + Multiplayer + Admin
Run:  streamlit run app.py
"""
import streamlit as st
import chess, chess.svg
import random, time, json, hashlib, uuid
from datetime import datetime
from pathlib import Path

# ── paths ──────────────────────────────────────────────────────────────────────
DATA_DIR   = Path("data")
USERS_FILE = DATA_DIR / "users.json"
GAMES_FILE = DATA_DIR / "games.json"
DATA_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="♟️ Chess", page_icon="♟️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=JetBrains+Mono&display=swap');
html,body,[class*="css"]{font-family:'Syne',sans-serif;background:#0d0d10;color:#e6e2db;}
.stApp{background:#0d0d10;}
/* kill all column padding so board squares touch */
div[data-testid="column"]{padding:0!important;min-width:0!important;}
div[data-testid="stHorizontalBlock"]{gap:0!important;}
/* square buttons */
div[data-testid="stButton"] button{
  width:58px!important;height:58px!important;min-width:0!important;
  padding:0!important;margin:0!important;border:none!important;
  border-radius:0!important;font-size:32px!important;line-height:1!important;
  transition:filter .1s!important;box-shadow:none!important;
}
div[data-testid="stButton"] button:hover{filter:brightness(1.3)!important;z-index:2!important;}
/* nav/action buttons override */
button[data-testid="baseButton-secondary"]{
  background:#e6b84a!important;color:#0d0d10!important;
  font-family:'Syne',sans-serif!important;font-weight:800!important;
  border-radius:5px!important;padding:.4rem 1rem!important;
}
div[data-baseweb="input"] input{background:#1e1e28!important;color:#e6e2db!important;
  border:1px solid #2a2a35!important;border-radius:5px!important;}
div[data-baseweb="tab-list"]{background:#17171d!important;border-radius:8px!important;padding:4px!important;}
button[data-baseweb="tab"]{background:transparent!important;color:#888!important;
  border-radius:6px!important;font-weight:600!important;}
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

# ══════════════════════════════════════════════════════════════════════════════
#  USER STORE
# ══════════════════════════════════════════════════════════════════════════════
def _hash(pw): return hashlib.sha256(pw.encode()).hexdigest()

def load_users():
    if USERS_FILE.exists(): return json.loads(USERS_FILE.read_text())
    u={"admin":{"password":_hash("admin123"),"role":"admin",
                "created":datetime.now().isoformat(),"wins":0,"losses":0,"draws":0}}
    USERS_FILE.write_text(json.dumps(u,indent=2)); return u

def save_users(u): USERS_FILE.write_text(json.dumps(u,indent=2))
def load_games(): return json.loads(GAMES_FILE.read_text()) if GAMES_FILE.exists() else {}
def save_games(g): GAMES_FILE.write_text(json.dumps(g,indent=2))

# ══════════════════════════════════════════════════════════════════════════════
#  ENGINE
# ══════════════════════════════════════════════════════════════════════════════
PST={chess.PAWN:[0,0,0,0,0,0,0,0,50,50,50,50,50,50,50,50,10,10,20,30,30,20,10,10,
                 5,5,10,25,25,10,5,5,0,0,0,20,20,0,0,0,5,-5,-10,0,0,-10,-5,5,
                 5,10,10,-20,-20,10,10,5,0,0,0,0,0,0,0,0],
     chess.KNIGHT:[-50,-40,-30,-30,-30,-30,-40,-50,-40,-20,0,0,0,0,-20,-40,
                   -30,0,10,15,15,10,0,-30,-30,5,15,20,20,15,5,-30,
                   -30,0,15,20,20,15,0,-30,-30,5,10,15,15,10,5,-30,
                   -40,-20,0,5,5,0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50],
     chess.BISHOP:[-20,-10,-10,-10,-10,-10,-10,-20,-10,0,0,0,0,0,0,-10,
                   -10,0,5,10,10,5,0,-10,-10,5,5,10,10,5,5,-10,
                   -10,0,10,10,10,10,0,-10,-10,10,10,10,10,10,10,-10,
                   -10,5,0,0,0,0,5,-10,-20,-10,-10,-10,-10,-10,-10,-20],
     chess.ROOK:[0,0,0,0,0,0,0,0,5,10,10,10,10,10,10,5,-5,0,0,0,0,0,0,-5,
                 -5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,
                 -5,0,0,0,0,0,0,-5,0,0,0,5,5,0,0,0],
     chess.QUEEN:[-20,-10,-10,-5,-5,-10,-10,-20,-10,0,0,0,0,0,0,-10,
                  -10,0,5,5,5,5,0,-10,-5,0,5,5,5,5,0,-5,
                  0,0,5,5,5,5,0,-5,-10,5,5,5,5,5,0,-10,
                  -10,0,5,0,0,0,0,-10,-20,-10,-10,-5,-5,-10,-10,-20],
     chess.KING:[-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,
                 -30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,
                 -20,-30,-30,-40,-40,-30,-30,-20,-10,-20,-20,-20,-20,-20,-20,-10,
                 20,20,0,0,0,0,20,20,20,30,10,0,0,10,30,20]}
PV={chess.PAWN:100,chess.KNIGHT:320,chess.BISHOP:330,chess.ROOK:500,chess.QUEEN:900,chess.KING:20000}

def evaluate(b):
    if b.is_checkmate(): return -99999 if b.turn==chess.WHITE else 99999
    if b.is_stalemate() or b.is_insufficient_material(): return 0
    s=0
    for sq in chess.SQUARES:
        p=b.piece_at(sq)
        if p:
            t=PST.get(p.piece_type,[0]*64)
            idx=sq if p.color==chess.WHITE else chess.square_mirror(sq)
            v=PV[p.piece_type]+t[idx]
            s+=v if p.color==chess.WHITE else -v
    return s

def minimax(b,depth,alpha,beta,maxi):
    if depth==0 or b.is_game_over(): return evaluate(b)
    if maxi:
        best=-999999
        for m in b.legal_moves:
            b.push(m); best=max(best,minimax(b,depth-1,alpha,beta,False)); b.pop()
            alpha=max(alpha,best)
            if beta<=alpha: break
        return best
    else:
        best=999999
        for m in b.legal_moves:
            b.push(m); best=min(best,minimax(b,depth-1,alpha,beta,True)); b.pop()
            beta=min(beta,best)
            if beta<=alpha: break
        return best

def get_bot_move(b):
    legal=list(b.legal_moves)
    if not legal: return None
    if random.random()<0.25: return random.choice(legal)
    best,bval=None,-999999
    for m in legal:
        b.push(m); v=minimax(b,1,-999999,999999,b.turn==chess.WHITE); b.pop()
        if v>bval: bval,best=v,m
    return best or random.choice(legal)

# ══════════════════════════════════════════════════════════════════════════════
#  SESSION
# ══════════════════════════════════════════════════════════════════════════════
def init():
    defs=dict(logged_in=False,username=None,role=None,page="auth",
              fen=chess.STARTING_FEN,my_color=chess.WHITE,history=[],
              sel=None,status="Your move",game_over=False,last_uci="",
              mode="bot",gid=None,opponent=None,move_count=0)
    for k,v in defs.items():
        if k not in st.session_state: st.session_state[k]=v
init()

# ══════════════════════════════════════════════════════════════════════════════
#  MOVE LOGIC
# ══════════════════════════════════════════════════════════════════════════════
def push_move(board, move):
    board.push(move)
    st.session_state.fen=board.fen()
    st.session_state.history.append(move.uci())
    st.session_state.last_uci=move.uci()
    st.session_state.sel=None
    st.session_state.move_count+=1          # key change → forces button re-render
    if board.is_game_over():
        st.session_state.game_over=True
        st.session_state.status="Game over · "+board.result()
        end_game(board.result())
    elif st.session_state.mode=="bot":
        st.session_state.status="Bot thinking…"
    else:
        mp_push(st.session_state.gid, move.uci())
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

    # build move (auto-queen promo)
    sp=board.piece_at(sel)
    promo=chess.QUEEN if (sp and sp.piece_type==chess.PAWN and chess.square_rank(sq) in (0,7)) else None
    mv=chess.Move(sel,sq,promotion=promo)
    if mv not in board.legal_moves:
        mv=chess.Move(sel,sq)

    if mv in board.legal_moves:
        push_move(board,mv)
    else:
        p=board.piece_at(sq)
        st.session_state.sel=sq if (p and p.color==pc and board.turn==pc) else None

def uci_move(text):
    board=chess.Board(st.session_state.fen)
    pc=st.session_state.my_color
    if board.turn!=pc or st.session_state.game_over:
        return "Not your turn"
    try:
        try:    mv=board.parse_uci(text.strip())
        except: mv=board.parse_san(text.strip())
        if mv in board.legal_moves:
            push_move(board,mv); return ""
        return "Illegal move"
    except: return "Invalid notation"

# ══════════════════════════════════════════════════════════════════════════════
#  BOARD RENDER  — pure Streamlit buttons, keyed by move_count so they are
#  always fresh widgets and Streamlit never ignores the click
# ══════════════════════════════════════════════════════════════════════════════
SQ_COLORS={
    "light":"#f0d9b5","dark":"#b58863",
    "light_last":"#cdd26a","dark_last":"#aaa23a",
    "sel":"#5fc8ee","legal":"#90d8a0","cap":"#e88080","check":"#e53935"
}
PIECES={(chess.PAWN,chess.WHITE):"♙",(chess.PAWN,chess.BLACK):"♟",
        (chess.KNIGHT,chess.WHITE):"♘",(chess.KNIGHT,chess.BLACK):"♞",
        (chess.BISHOP,chess.WHITE):"♗",(chess.BISHOP,chess.BLACK):"♝",
        (chess.ROOK,chess.WHITE):"♖",(chess.ROOK,chess.BLACK):"♜",
        (chess.QUEEN,chess.WHITE):"♕",(chess.QUEEN,chess.BLACK):"♛",
        (chess.KING,chess.WHITE):"♔",(chess.KING,chess.BLACK):"♚"}

def render_board():
    board  = chess.Board(st.session_state.fen)
    flip   = st.session_state.my_color==chess.BLACK
    sel    = st.session_state.sel
    mc     = st.session_state.move_count   # changes every move → fresh keys

    # legal destinations of selected piece
    legal=set()
    if sel is not None:
        for m in board.legal_moves:
            if m.from_square==sel: legal.add(m.to_square)

    # last-move squares
    last_sqs=set()
    if st.session_state.last_uci:
        try:
            lm=chess.Move.from_uci(st.session_state.last_uci)
            last_sqs={lm.from_square,lm.to_square}
        except: pass

    # check square
    check_sq=-1
    if board.is_check():
        ksq=board.king(board.turn)
        if ksq is not None: check_sq=ksq

    ranks=range(7,-1,-1) if not flip else range(0,8)
    files=range(0,8)     if not flip else range(7,-1,-1)

    for rank in ranks:
        cols=st.columns(8,gap="small")
        for ci,file in enumerate(files):
            sq=chess.square(file,rank)
            piece=board.piece_at(sq)
            light=(file+rank)%2==0

            # background colour
            if sq==check_sq:       bg=SQ_COLORS["check"]
            elif sq==sel:          bg=SQ_COLORS["sel"]
            elif sq in legal:      bg=SQ_COLORS["cap"] if piece else SQ_COLORS["legal"]
            elif sq in last_sqs:   bg=SQ_COLORS["light_last"] if light else SQ_COLORS["dark_last"]
            else:                  bg=SQ_COLORS["light"] if light else SQ_COLORS["dark"]

            label=PIECES.get((piece.piece_type,piece.color),"") if piece else ("·" if sq in legal else " ")
            txt_color="#111" if light else "#eee"

            # Inject per-button style via a unique class tied to sq+mc
            cls=f"sqb_{sq}_{mc}"
            st.markdown(
                f"<style>.{cls}>div>button{{background:{bg}!important;"
                f"color:{txt_color}!important;}}</style>",
                unsafe_allow_html=True
            )
            with cols[ci]:
                st.markdown(f'<div class="{cls}">',unsafe_allow_html=True)
                clicked=st.button(label, key=f"sq_{sq}_{mc}")
                st.markdown("</div>",unsafe_allow_html=True)
                if clicked:
                    sq_click(sq)
                    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  MULTIPLAYER HELPERS
# ══════════════════════════════════════════════════════════════════════════════
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
        if u in users: users[u][f]=users[u].get(f,0)+1
    if result=="1/2-1/2":
        bump(me,"draws")
        if opp in users: bump(opp,"draws")
    elif (result=="1-0" and pc==chess.WHITE) or (result=="0-1" and pc==chess.BLACK):
        bump(me,"wins"); (lambda: bump(opp,"losses") if opp in users else None)()
    else:
        bump(me,"losses"); (lambda: bump(opp,"wins") if opp in users else None)()
    save_users(users)

def new_bot_game(color):
    st.session_state.update(fen=chess.STARTING_FEN,
        my_color=chess.WHITE if color=="White" else chess.BLACK,
        history=[],sel=None,status="Your move",game_over=False,
        last_uci="",mode="bot",gid=None,opponent="Bot (~1000 ELO)",
        page="game",move_count=0)

# ══════════════════════════════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════════════════════════════
def do_login(u,p):
    users=load_users(); ud=users.get(u)
    if ud and ud["password"]==_hash(p):
        st.session_state.update(logged_in=True,username=u,role=ud["role"],page="lobby")
        return True
    return False

def do_register(u,p):
    users=load_users()
    if u in users:      return False,"Username taken."
    if len(u)<3:        return False,"Username ≥3 chars."
    if len(p)<6:        return False,"Password ≥6 chars."
    users[u]={"password":_hash(p),"role":"player","created":datetime.now().isoformat(),
              "wins":0,"losses":0,"draws":0}
    save_users(users); return True,"Account created — log in now."

def do_logout():
    for k in list(st.session_state.keys()): del st.session_state[k]
    init()

# ══════════════════════════════════════════════════════════════════════════════
#  PAGES
# ══════════════════════════════════════════════════════════════════════════════
def page_auth():
    _,col,_=st.columns([1,1.4,1])
    with col:
        st.markdown('<div class="logo">♟ Chess<span>.</span></div>',unsafe_allow_html=True)
        st.markdown("<p style='color:#555;margin:-4px 0 1.2rem'>vs Bot · Multiplayer · Admin</p>",unsafe_allow_html=True)
        t1,t2=st.tabs(["Log in","Create account"])
        with t1:
            u=st.text_input("Username",key="liu"); p=st.text_input("Password",type="password",key="lip")
            if st.button("Log in",key="libtn"):
                if do_login(u,p): st.rerun()
                else: st.error("Wrong credentials.")
            st.caption("Default admin → `admin` / `admin123`")
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
            st.session_state.update(gid=gid,my_color=chess.WHITE,opponent="Waiting…",
                mode="multiplayer",fen=chess.STARTING_FEN,history=[],last_uci="",
                status="Waiting for opponent…",game_over=False,page="game",move_count=0)
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
                    mode="multiplayer",fen=g["fen"],history=mv,
                    last_uci=mv[-1] if mv else "",
                    status="Your move" if chess.Board(g["fen"]).turn==chess.BLACK else "Opponent's turn",
                    game_over=False,page="game",move_count=len(mv))
                st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)

    games=load_games()
    open_games=[(g,d) for g,d in games.items()
                if d["status"]=="waiting" and d["white"]!=st.session_state.username]
    if open_games:
        st.markdown("### Open games")
        for gid,g in open_games[:8]:
            ca,cb=st.columns([3,1])
            ca.markdown(f"**{g['white']}** · {g['created'][:10]}")
            if cb.button("Join",key=f"oj_{gid}"):
                g["black"]=st.session_state.username; g["status"]="active"
                games[gid]=g; save_games(games)
                st.session_state.update(gid=gid,my_color=chess.BLACK,opponent=g["white"],
                    mode="multiplayer",fen=g["fen"],history=[],last_uci="",
                    status="Opponent's turn",game_over=False,page="game",move_count=0)
                st.rerun()

def page_game():
    board=chess.Board(st.session_state.fen)
    pc=st.session_state.my_color
    is_my_turn=(board.turn==pc and not st.session_state.game_over)

    # ── sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"**{st.session_state.username}** vs **{st.session_state.opponent}**")
        st.markdown("---")
        if st.button("⬅ Lobby",key="sl"):  st.session_state.page="lobby"; st.rerun()
        if st.button("🏳 Resign",key="sr"): st.session_state.page="lobby"; st.rerun()
        st.markdown("---")
        mi=st.text_input("Move (UCI/SAN)",placeholder="e2e4 or Nf3",key="mi")
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
                w=hist[i]; b=hist[i+1] if i+1<len(hist) else "…"
                rows.append(f"{i//2+1}. <span>{w}</span> <span>{b}</span>")
            st.markdown('<div class="mlist">'+"<br>".join(rows)+"</div>",unsafe_allow_html=True)

    # ── main ──────────────────────────────────────────────────────────────────
    col_board, col_info = st.columns([1.8,1], gap="large")

    with col_board:
        # turn / status indicator above board
        whose = "Your turn ✅" if is_my_turn else "Opponent's turn ⏳"
        if st.session_state.game_over: whose = st.session_state.status
        st.markdown(f'<div class="pill">⚡ {whose}</div>', unsafe_allow_html=True)
        render_board()

    with col_info:
        st.markdown('<div class="card">',unsafe_allow_html=True)
        st.markdown('<div class="ct">Game info</div>',unsafe_allow_html=True)
        st.markdown(f"**Mode:** {'vs Bot' if st.session_state.mode=='bot' else 'Multiplayer'}")
        st.markdown(f"**You:** {'⬜ White' if pc==chess.WHITE else '⬛ Black'}")
        st.markdown(f"**Opp:** {st.session_state.opponent}")
        if st.session_state.mode=="multiplayer" and st.session_state.gid:
            st.markdown(f"**ID:** `{st.session_state.gid}`")
        st.markdown("</div>",unsafe_allow_html=True)

        if board.is_check() and not board.is_checkmate():
            st.warning("♚ Check!")
        if st.session_state.game_over:
            r=board.result()
            st.success({"1-0":"⬜ White wins!","0-1":"⬛ Black wins!","1/2-1/2":"½–½ Draw"}.get(r,r))
            if st.button("🏠 Back to lobby",key="btl"): st.session_state.page="lobby"; st.rerun()

        # material
        PU={"P":"♙","p":"♟","N":"♘","n":"♞","B":"♗","b":"♝","R":"♖","r":"♜","Q":"♕","q":"♛"}
        S={"P":8,"N":2,"B":2,"R":2,"Q":1,"p":8,"n":2,"b":2,"r":2,"q":1}
        cur={}
        for sq in chess.SQUARES:
            p=board.piece_at(sq)
            if p: cur[p.symbol()]=cur.get(p.symbol(),0)+1
        wc=[]; bc=[]
        for s,n in S.items():
            for _ in range(n-cur.get(s,0)):
                (bc if s.isupper() else wc).append(PU[s])
        st.markdown(f"**White captured:** {''.join(bc) or '–'}")
        st.markdown(f"**Black captured:** {''.join(wc) or '–'}")

        # multiplayer poll
        if st.session_state.mode=="multiplayer" and not st.session_state.game_over and not is_my_turn:
            g=load_games().get(st.session_state.gid)
            if g and len(g["moves"])>len(st.session_state.history):
                mv=g["moves"]
                st.session_state.history=mv; st.session_state.fen=g["fen"]
                st.session_state.last_uci=mv[-1] if mv else ""
                st.session_state.move_count=len(mv)
                if g["status"]=="finished":
                    st.session_state.game_over=True; st.session_state.status="Game over · "+g["result"]
                else: st.session_state.status="Your move"
                st.rerun()
            if st.button("🔃 Refresh",key="poll"): st.rerun()

    # ── bot reply ─────────────────────────────────────────────────────────────
    if (st.session_state.mode=="bot" and not st.session_state.game_over
            and board.turn!=pc and st.session_state.status=="Bot thinking…"):
        with st.spinner("Bot thinking…"):
            time.sleep(0.3)
            bm=get_bot_move(board)
            if bm: push_move(board,bm)
        st.rerun()

def page_admin():
    st.markdown("## 🛡️ Admin Panel")
    users=load_users(); games=load_games()
    t1,t2=st.tabs(["👤 Users","🎮 Games"])
    with t1:
        for uname,ud in users.items():
            c1,c2,c3,c4=st.columns([2,1.4,1.2,.8])
            b='<span class="badge badge-admin">admin</span>' if ud["role"]=="admin" else '<span class="badge">player</span>'
            c1.markdown(f"**{uname}** {b}",unsafe_allow_html=True)
            c2.markdown(f"W{ud.get('wins',0)} L{ud.get('losses',0)} D{ud.get('draws',0)}")
            c3.markdown(f"<small style='color:#555'>{ud.get('created','')[:10]}</small>",unsafe_allow_html=True)
            if uname!="admin" and c4.button("🗑",key=f"del_{uname}"):
                del users[uname]; save_users(users); st.rerun()
        st.markdown("---"); st.markdown("### ➕ Add user")
        a1,a2,a3=st.columns(3)
        an=a1.text_input("Username",key="an"); ap=a2.text_input("Password",type="password",key="ap")
        ar=a3.selectbox("Role",["player","admin"],key="ar")
        if st.button("Add user",key="au"):
            if an in users: st.error("Taken.")
            elif len(an)<3 or len(ap)<6: st.error("Too short.")
            else:
                users[an]={"password":_hash(ap),"role":ar,
                           "created":datetime.now().isoformat(),"wins":0,"losses":0,"draws":0}
                save_users(users); st.success(f"Added {an}."); st.rerun()
    with t2:
        for gid,g in list(games.items())[-20:]:
            st.markdown(f"`{gid}` {g['white']} vs {g['black'] or '?'} · {g['status']} · {g.get('result','–')}")
        if games and st.button("Clear finished",key="cf"):
            save_games({k:v for k,v in games.items() if v["status"]!="finished"}); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  NAV + ROUTER
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.logged_in:
    with st.sidebar:
        st.markdown("### ♟ Chess")
        st.markdown(f"**{st.session_state.username}**")
        if st.session_state.role=="admin":
            st.markdown('<span class="badge badge-admin">admin</span>',unsafe_allow_html=True)
        st.markdown("---")
        if st.button("🏠 Lobby",key="nl"): st.session_state.page="lobby"; st.rerun()
        if st.session_state.role=="admin":
            if st.button("🛡 Admin",key="na"): st.session_state.page="admin"; st.rerun()
        st.markdown("---")
        if st.button("🚪 Log out",key="nlo"): do_logout(); st.rerun()

pg=st.session_state.page
if not st.session_state.logged_in: page_auth()
elif pg=="lobby":  page_lobby()
elif pg=="game":   page_game()
elif pg=="admin":
    if st.session_state.role=="admin": page_admin()
    else: st.session_state.page="lobby"; st.rerun()
else: page_lobby()