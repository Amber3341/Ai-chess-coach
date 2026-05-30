"""
Auto-generated chess theory passages for RAG.
Created by: scripts/generate_theory.py (hand-authored for accuracy and consistency)
Total passages: 57

DO NOT EDIT MANUALLY — re-run scripts/generate_theory.py to regenerate,
or add new passages directly to this list.
After updating this file, re-run scripts/ingest_theory.py to push to Qdrant.
"""

CHESS_THEORY_GENERATED: list[str] = [

    # ── DEFENSIVE TECHNIQUE ───────────────────────────────────────────────────

    "A fortress is a defensive setup where the weaker side builds an impregnable position "
    "that the opponent cannot penetrate despite being ahead in material. When you are a piece "
    "down in the endgame, your job is to lock the pawn structure, place your remaining pieces "
    "on their best defensive squares, and keep your king in the corner the opponent's bishop "
    "cannot reach. For example, with a wrong-colored bishop on g2 and your king fixed on h8, "
    "White cannot make progress even with extra material. Recognizing the fortress early and "
    "steering toward it is the key defensive skill.",

    "Perpetual check is your last resort when you are losing and cannot hold the position "
    "materially. The idea is simple: find a sequence of checks that the opponent's king cannot "
    "escape, forcing a draw by repetition. Your queen is the main tool — look for a checking "
    "route that covers two or three squares the king must cycle between. Before resigning in a "
    "queen endgame, always scan for a queen check on h5, g6, or f7 that starts a perpetual "
    "sequence. Even a rook can deliver perpetual check if the king is confined to the back rank "
    "with Rg8+ and Rh8+ alternating.",

    "When the opponent launches a pawn storm against your castled king — typically h4-h5-h6 or "
    "g4-g5-g6 in opposite-side castling positions — your best defense is usually counterattack, "
    "not pure defense. Advance your own queenside pawns aggressively with a5-b4-b3 or a4-b5 "
    "to create threats of your own. If you only defend, your opponent's attack will arrive "
    "first. When the position is truly defended, use prophylactic moves like h6 to give your "
    "king a flight square and slow the pawn advance. The side whose attack lands first wins — "
    "so make your counterplay as fast as possible.",

    "Stalemate is a powerful defensive weapon when you are losing. Look for positions where "
    "your king has no legal move and your other pieces are also restricted. To engineer a "
    "stalemate trap, sacrifice material to strip away your own pawns and leave your king with "
    "no escape squares. A common pattern is queen vs rook-pawn on the seventh rank: the losing "
    "side sacrifices the rook so the king is stalemated in the corner. Always calculate whether "
    "your opponent can safely capture a piece you offer — if taking it leaves your king with "
    "no moves and no pawns to push, you have earned your draw.",

    "In rook endgames when you are defending, your rook must stay active — a passive rook "
    "always loses. The Philidor method teaches you to place your rook on the sixth rank, "
    "cutting off the attacking king, and only switch to checking from behind once the pawn "
    "reaches the sixth rank. Never let your rook be pushed to the edge passively. If your "
    "rook is on a1 blocking the a-pawn, switch to checking from the side on a8, b8, or c8 "
    "immediately. Active rook checks force the king to shield the pawn, giving you drawing "
    "resources that a passive rook can never create.",

    "Active defense means counterattacking rather than just absorbing blows. When your opponent "
    "attacks on one wing, look for counterplay in the center or on the opposite flank rather "
    "than passively shuffling defensive pieces. For example, if White attacks on the kingside, "
    "Black can often respond with c5 or d5 breaks in the center, forcing White to defend and "
    "abandon the attack. The principle is: threats from both sides are harder to handle than "
    "a threat from one side. Your defensive move should ideally contain a counter-threat — "
    "that is what separates active defense from passive suffering.",

    "In a bad bishop endgame where your bishop is blocked by its own pawns, your main drawing "
    "technique is to fix all your pawns on the opposite color of the bishop and keep your king "
    "actively placed. For example, with a dark-squared bishop and pawns on e4, d3, and c4 "
    "(all light squares), the bishop is nearly useless. Your king must do all the work — "
    "centralize it on d4 or e5 to compensate. The drawing idea is to blockade the opponent's "
    "passed pawn with your king and use your bishop only to guard the squares your king cannot "
    "reach. Correct king placement saves many of these positions.",

    # ── PIECE TRADING DECISIONS ───────────────────────────────────────────────

    "Knowing when to trade pieces is one of the most important middlegame skills. Trade pieces "
    "when: (1) your pieces are passive and the opponent's are active — swap off the active "
    "ones, (2) you have a material advantage and want to simplify into a won endgame, (3) "
    "trading relieves pressure on a weak square or pawn. Do not trade when: you have the "
    "initiative and trading gives the opponent time to consolidate, or when your remaining "
    "pieces are better coordinated than the opponent's. Ask yourself after every trade: 'Is "
    "my remaining position improved or worsened?' That question alone will prevent most bad "
    "exchanges.",

    "Trading your bad bishop for the opponent's active knight is a classic positional weapon. "
    "A bishop blocked by its own pawns on e6, d5, and c6 — all the same color — is worth far "
    "less than a centralized knight on d4 or e5. When you can swap Bxd4 or ...Bxf3 to "
    "eliminate the dominant knight, do it even if you hand over the bishop pair, because "
    "the resulting pawn structure with a freed bishop or a more mobile position fully "
    "compensates. The resulting simplification typically converts your structural advantage "
    "into an endgame where the opponent's remaining bishop is permanently bad.",

    "Do not trade queens when you have the attacking initiative, even if the material balance "
    "is equal. Queens are the engine of attacking play — the moment queens leave the board, "
    "your attacking threats evaporate and the position often becomes a technical endgame where "
    "structural factors dominate. If your opponent offers a queen trade in a position where "
    "your pieces are pointing at their king, decline it and find a move that maintains the "
    "tension. The exception is when trading queens enters a clearly won pawn endgame. "
    "Otherwise, keep the queens on and keep the pressure alive.",

    "Rook trades are powerful when they enter a won pawn endgame. Before trading rooks, "
    "calculate the resulting king-and-pawn endgame precisely: if your king is closer to the "
    "key squares and your pawn majority can create a passed pawn, the rook trade wins. The "
    "formula is: count your king's distance to the key squares, use the square-of-the-pawn "
    "rule, and verify your passed pawn reaches promotion. Only then trade on the open file. "
    "A common mistake is trading rooks 'automatically' when ahead in material without checking "
    "that the pawn endgame is actually won — sometimes a rook endgame with an extra pawn is "
    "only drawn, while the rook endgame with active pieces would win.",

    "Trading into an opposite-colored bishop endgame when you are a pawn or two ahead is "
    "extremely risky — these endgames are notorious for being drawn even with a large material "
    "advantage. The defending side's bishop guards all the squares the attacking bishop can "
    "never reach, making a fortress trivial to build. Before you enter this structure, verify "
    "that your pawns are advanced enough to force promotion without king support, or that your "
    "king can force the defending king away from the critical squares. If you cannot see a "
    "clear winning method, avoid trading into opposite-colored bishops and keep other pieces "
    "on the board.",

    "Simplifying into an endgame when you have the initiative trades your most valuable asset "
    "— dynamic pressure — for a static material or positional advantage that may not be "
    "decisive. Initiative means your opponent must react to your threats every move; once "
    "simplified, they can consolidate and use their own strengths. When your pieces are "
    "actively attacking, keep the tension and look for concrete winning continuations. Only "
    "trade down when your advantage is so clear that the endgame is technically won by force. "
    "The principle: dynamic advantages (attack, initiative) must be used immediately; static "
    "advantages (extra pawn, better structure) can afford to be converted later.",

    # ── OPENING TO MIDDLEGAME TRANSITION ─────────────────────────────────────

    "After completing development — both knights developed, both bishops active, king castled, "
    "rooks connected — your opening phase is done and the middlegame begins. Your first task "
    "is to identify the pawn structure and ask three questions: Where is my space advantage? "
    "Which of my pieces is worst placed? What is my opponent's best plan? The answers give "
    "you your middlegame plan. A common mistake is continuing to make 'development moves' "
    "after development is complete — at that point, you need a concrete plan based on pawn "
    "breaks, piece improvements, or creating weaknesses in the opponent's position.",

    "The pawn structure after the opening defines your middlegame plan. In a French structure "
    "(pawns on e6 and d5 vs e5 and d4), Black attacks the base of White's chain with c5 "
    "while White attacks with f4-f5. In a Sicilian Dragon structure, White's plan is always "
    "h4-h5 on the kingside while Black plays on the c-file. Before making a move, look at "
    "your pawns and ask: which pawn break opens lines for my pieces? Pawn breaks — c5, d5, "
    "f5, or e5 depending on the structure — are often the most important moves in the "
    "transition from opening to middlegame.",

    "When your opponent deviates from the opening moves you know, do not panic — apply "
    "general principles instead. Ask: does the deviation develop a piece, fight for the "
    "center, or create a threat? If it does none of these, it is probably a mistake you "
    "can punish by continuing your own development and seizing the initiative. The principle "
    "is: respond to threats, but otherwise keep developing and castling. Only calculate "
    "deeply when the opponent's move creates a concrete tactical threat. Against passive or "
    "off-beat moves, simply play the best principled move — develop, centralize, castle — "
    "and your position will be fine.",

    "Premature attacks — launching before all pieces are developed — almost always fail "
    "because the opponent can counterattack in the center. The classic example is the "
    "Scholar's Mate attempt: White brings the queen to h5 and the bishop to c4 while Black "
    "simply plays Nf6 attacking the queen, then completes development freely. The principle "
    "is: every piece must join the fight before you attack. If you are attacking with queen "
    "and two pieces while four of your pieces sit undeveloped, your opponent's counterattack "
    "in the center will land before your attack on the king. Finish development first, then "
    "attack.",

    "When facing a gambit, you have three options: accept and return the pawn at the right "
    "moment, accept and try to hold it, or decline and play solidly. Accepting is fine if "
    "you can complete development before the opponent's attack gathers speed — count the "
    "tempos. If the gambit gives the opponent three development tempos for one pawn, return "
    "the pawn immediately to catch up. Declining with a solid move like d3 or Nf6 is often "
    "the safest choice against dangerous gambits — you avoid all preparation and play a "
    "normal position. Never hold a gambit pawn at the cost of your development and king "
    "safety.",

    # ── MIDDLEGAME PLANNING ────────────────────────────────────────────────────

    "When you do not know what to do in the middlegame, use the three-step method: (1) Find "
    "your worst-placed piece and ask how to improve it. (2) Identify any weaknesses in the "
    "opponent's position — a backward pawn, an outpost square, an exposed king. (3) Ask what "
    "your opponent wants to do next and whether you must stop it. These three questions almost "
    "always produce a useful move. Avoid random pawn pushes or 'waiting moves' — every move "
    "should either improve a piece, create a weakness, or prevent the opponent's plan. This "
    "systematic approach prevents the aimless shuffling that characterizes lower-level play.",

    "The principle of the worst-placed piece: in any position, identify the piece that "
    "contributes least to your position and make a plan to improve it. A bishop on a1 behind "
    "your own pawns, a knight on h3 with no good squares, or a rook on f1 with no open file "
    "— these are your priority. Move the worst piece to its ideal square before launching "
    "any attack, because attacking with one passive piece is always less effective than "
    "attacking with all pieces coordinated. Grandmasters win by improving pieces one by one "
    "until all pieces work together, then striking when the position is optimized.",

    "To create a target to attack in the middlegame, you must first provoke a pawn weakness "
    "in the opponent's position. Use piece pressure to force the opponent to advance a pawn "
    "(creating a backward pawn) or exchange a defender (creating a hole). For example, place "
    "a bishop on b3 or a knight on d5 to pressure f7 or e6, forcing the opponent to weaken "
    "their pawn structure with f6 or f5. Once a weakness exists — a weak pawn on d6, a hole "
    "on f5 — concentrate all your pieces on it. The opponent must use pieces to defend the "
    "weakness, which restricts their activity and lets you seize control elsewhere.",

    "Open the position when your pieces are more active; keep it closed when the opponent's "
    "pieces are more active. If you have the bishop pair and open files, play e4-e5 or d4-d5 "
    "to break open diagonals. If you have a knight vs bad bishop, keep the pawns fixed and "
    "closed — the knight needs stable outposts that closed positions provide. The practical "
    "trigger: if you can open a file your rooks will dominate, open it. If opening lines "
    "gives the opponent's bishop pair targets, keep the center closed. Always ask 'Who "
    "benefits most from open lines?' before pushing a central pawn.",

    "Space advantage should be exploited by keeping all your pieces on the board and avoiding "
    "exchanges. When you have more space — say, pawns on e5 and d5 vs e6 and d6 — your pieces "
    "have more room to maneuver while the opponent's are cramped. Do not trade pieces; let the "
    "opponent suffocate. Advance your space advantage further with f4-f5 or a4-a5 to squeeze "
    "the position. Only attack once all your pieces are on their ideal squares. The opponent's "
    "best hope is to trade pieces to free their position — deny them that by keeping as many "
    "pieces on as possible while improving each one in turn.",

    "When your position is cramped — your pieces have little space, your pawns are on the "
    "back half of the board — your priority is to free your position with pawn exchanges. "
    "Look for the key pawn break: in a French-type structure, c5xd4 or f6xe5 frees pieces "
    "immediately. Offer piece exchanges too — trading one or two pieces relieves the cramping "
    "pressure significantly. Avoid the mistake of passively defending every pawn; sometimes "
    "sacrificing a pawn with d5 or e5 opens lines and gives your pieces activity worth more "
    "than the pawn. A cramped but active position is far better than a cramped and passive one.",

    # ── STALEMATE AVOIDANCE ───────────────────────────────────────────────────

    "In queen vs pawn endgames, stalemate is an ever-present danger on the a-file, c-file, "
    "f-file, and h-file (especially rook and bishop pawns). Before capturing or checkmating, "
    "always check whether the move leaves the opponent's king with at least one legal square. "
    "The technique is to use your queen to cut off the king without stalemating it — give "
    "check from a distance to maneuver the king away from the stalemate corner, then bring "
    "your own king in to help. With a rook pawn on h2 and a king on h1, the solution is "
    "to check the king to g1, then play your king to f3 before winning the pawn.",

    "The classic stalemate trap in rook endgames occurs when the defending side sacrifices "
    "their rook on the promotion square. If White has a pawn on a7 and a rook, and Black "
    "plays Ra1 intending Rxa8 when the pawn promotes, White must be careful not to take the "
    "rook if it results in stalemate. Before advancing the pawn to a8=Q or a8=R, verify that "
    "the Black king has at least one legal move. The solution: use your rook to drive the "
    "enemy king away from the corner before promoting, or choose an underpromotion to a "
    "rook to avoid the stalemate pattern entirely.",

    "Advancing pawns too quickly in a winning endgame can accidentally stalemate the opponent. "
    "The most common version: you push your h-pawn to h7 with the opponent's king trapped on "
    "h8, and suddenly all of Black's pieces have no legal moves — stalemate. Before every "
    "pawn advance in a winning endgame, ask: does this pawn move leave the opponent with at "
    "least one legal move? If the answer is no, stop and use a tempo move with your king or "
    "rook first to give the opponent a waiting move. This small check — does my opponent have "
    "a legal move? — prevents one of the most embarrassing mistakes in chess.",

    "The bishop-pawn stalemate on a7 or h7 (or a2/h2) is one of the most famous drawn "
    "endgames. When a rook pawn reaches the seventh rank and the defending king reaches the "
    "corner square the bishop does not control, the position is always a draw regardless of "
    "material. If you are winning with a light-squared bishop and an a-pawn, and the opponent's "
    "king reaches a8, you cannot force checkmate — the bishop cannot cover b8 and the corner "
    "is a stalemate refuge. Recognize this draw early and either advance a different pawn, "
    "sacrifice the bishop to create a new passer, or accept the draw.",

    # ── BLUNDER PREVENTION ────────────────────────────────────────────────────

    "Hanging pieces — leaving a piece unprotected where the opponent can simply capture it — "
    "are the most common cause of lost games below 1600 ELO. Before every move, run the "
    "LPDO check: Look at all your pieces and ask 'Is this piece Loose (unprotected)? Does "
    "the opponent's next move attack it?' Scan your pieces one by one: queen, rooks, bishops, "
    "knights. If any piece is loose after your intended move, either protect it, move it, or "
    "calculate whether the opponent can actually win it. This 10-second habit eliminates "
    "the majority of one-move blunders from your game.",

    "The back-rank checkmate is one of the most common tactical themes at club level. It "
    "occurs when your king is trapped on the back rank by its own pawns, and a rook or queen "
    "delivers checkmate on e1, d1, or f1. The solution is simple: create a 'luft' square by "
    "playing h3, g3, or h6, g6 — a pawn move that gives your king an escape square. Make "
    "this prophylactic move as soon as your king is castled and you have no other urgent tasks. "
    "When you see a back-rank threat, always ask: can my rook interpose? Can my king escape? "
    "If both answers are no, you are in serious danger.",

    "Moving your king into the center during the middlegame is one of the most dangerous "
    "decisions you can make. An exposed king in the center is a target for sacrifices on e6, "
    "d6, or f6, discovered checks, and direct queen attacks. If you have not castled by move "
    "12-14, your opponent can open the center with d5, e5, or c5 to expose your king to "
    "attack from every direction. Always castle before the center opens. If you cannot castle, "
    "keep the center closed with e5 or d5 pawn advances — a closed center protects a king "
    "stuck in the middle.",

    "Moving a pinned piece is one of the most dangerous mistakes in chess. When your knight "
    "on f6 is pinned by a bishop on b2 or g5 — meaning moving it exposes your queen or king "
    "to capture — any move of that knight loses material immediately. Before moving any piece, "
    "ask: is this piece pinned? If yes, verify that moving it does not leave a more valuable "
    "piece hanging behind it. An absolute pin (pinned to the king) means the pinned piece "
    "legally cannot move at all. A relative pin (pinned to the queen) can be broken but at "
    "the cost of the queen — almost always losing.",

    "Under time pressure, the most important habit is to spend five seconds on a blunder check "
    "before every move, even if you are almost out of time. The checklist: (1) Does my move "
    "leave any piece undefended? (2) Does my move expose my king? (3) Can the opponent deliver "
    "check or a fork on their next move? This three-point check takes five seconds and catches "
    "90% of time-pressure blunders. When the clock is critical, play simple, solid moves that "
    "do not create new tactical problems. Avoid complex sacrifices or pawn breaks under time "
    "pressure — the risk of a calculation error is too high.",

    "Before every capture, count the number of attackers and defenders on the square you are "
    "capturing. If you have two attackers and the opponent has two defenders, and the piece "
    "on the square is worth less than your capturing piece, the exchange likely loses material. "
    "Always perform the attacker-defender count: list every piece that can take on the square, "
    "assign material values (pawn=1, knight=3, bishop=3, rook=5, queen=9), and calculate the "
    "net gain or loss. This simple arithmetic, done before every capture, prevents the majority "
    "of material-losing exchanges in club-level games.",

    # ── TACTICAL VISION ────────────────────────────────────────────────────────

    "Before making your move, scan for tactics using the BAIT checklist: Bxh7+ sacrifice "
    "patterns, Attacks on undefended pieces, In-between moves (zwischenzug), Threats the "
    "opponent can create. Specifically: look at every check you can give, every capture you "
    "can make, and every piece the opponent has left undefended. This scan takes 15-20 seconds "
    "and surfaces the tactical shots that time pressure or positional focus causes you to miss. "
    "If you see a potential combination, calculate it fully before playing it — a combination "
    "that almost works but fails on move three loses the game.",

    "The decision to calculate deeply vs play a positional move depends on whether the position "
    "contains forcing elements. If there are checks, captures, or threats that limit both "
    "sides' options significantly, you must calculate — the position is tactical and intuition "
    "alone will fail. If the position is quiet with no forcing moves, positional judgment "
    "based on pawn structure, piece activity, and long-term plans is the right approach. "
    "The mistake most players make is calculating deeply in quiet positions (wasting time) "
    "and playing intuitively in tactical positions (missing combinations). Learn to read "
    "which mode the position demands.",

    "A combination is a forcing sequence — checks, captures, and threats — that leads to a "
    "concrete advantage. To spot a combination, look for: an exposed king, an overloaded "
    "defender, a piece on an unprotected square, or a back-rank weakness. When you see one "
    "of these signals, ask: what is the most forcing move I can make? Start with checks and "
    "captures because they limit the opponent's responses most severely. Calculate checks "
    "first, captures second, threats third. If a sequence of forcing moves leads to material "
    "gain, checkmate, or a clearly winning position, you have found your combination.",

    "A sacrifice is correct when the compensation is concrete and calculable, not just "
    "intuitive. Before sacrificing a piece, verify at least one of these: (1) the sacrifice "
    "leads to forced checkmate in a calculated number of moves, (2) the sacrifice wins back "
    "more material by force within three to five moves, or (3) the sacrifice permanently "
    "destroys the opponent's king safety with lasting attacking compensation. The Greek Gift "
    "sacrifice Bxh7+ is a classic example that requires the opponent's king on g8, a knight "
    "on f3 ready to hop to g5, and a queen available to come to h5. Verify all conditions "
    "before sacrificing.",

    # ── ENDGAME: KING AND PAWN ────────────────────────────────────────────────

    "Key squares are the squares that, if your king reaches them, guarantee the pawn will "
    "promote regardless of where the opponent's king is. For a pawn on d5, the key squares "
    "are c7, d7, and e7 — one rank ahead of where the pawn would become a queen. For a pawn "
    "on d4, the key squares are c6, d6, and e6. Your job in a king-and-pawn ending is to "
    "march your king to one of these key squares while the opponent's king tries to prevent "
    "it. If your king reaches a key square, play the pawn forward — it will promote by force. "
    "Use the opposition and triangulation to outmaneuver the defending king.",

    "The square of the pawn is a visual tool to judge pawn races without calculation. Draw "
    "an imaginary square from the pawn's current square to the promotion square — the side "
    "of the square equals the number of squares the pawn needs to promote. If the defending "
    "king can step into that square on their turn, they catch the pawn; if they cannot, the "
    "pawn promotes freely. For example, a pawn on a5 with five squares to go: the square is "
    "a5-a1-e1-e5. If the Black king on f6 can step into that square by moving to e6 (inside "
    "the square), the king catches the pawn. This mental shortcut saves crucial calculation "
    "time in time pressure.",

    "Rook pawn (a- or h-pawn) endgames are the most common drawn positions in practical chess, "
    "even when the stronger side has an extra piece. The reason is simple: the defending king "
    "runs to the corner (a8 or h8), and once there, the opponent cannot dislodge it without "
    "causing stalemate. If you are trying to win with a rook pawn and king, verify that your "
    "king can reach b6 (or g6) to shoulder aside the defending king before it reaches the "
    "corner. If the defending king arrives at the corner first, accept the draw and look for "
    "a different winning plan in the earlier position.",

    "Converting a king and two connected pawns versus a lone king is usually straightforward "
    "but stalemate must be avoided. The key is to keep the opponent's king active — never let "
    "it be reduced to zero legal moves. Advance your pawns together, one square at a time, "
    "with your king supporting from behind. When the pawns reach the sixth rank, use your "
    "king actively to cut off the defending king's approach. If the defending king retreats "
    "to the corner, advance the pawn to the seventh rank and use the other pawn or king to "
    "prevent stalemate. The f-pawn and h-pawn together are the trickiest — always verify "
    "the opponent has a legal move before capturing or advancing.",

    "The wrong-colored bishop and rook pawn draw is one of the most important theoretical "
    "endgames to know. When you have a bishop that does not control the promotion square of "
    "your only remaining pawn (e.g., a light-squared bishop with an a-pawn that promotes on "
    "a8, a dark square), the endgame is a forced draw if the opponent's king reaches the "
    "corner. The defending king simply shuffles between a8 and b8 — the bishop can never "
    "force it out, and advancing the pawn to a7 is met by Ka8 with stalemate looming. "
    "Recognize this pattern early and avoid it by keeping another pawn on the board.",

    # ── ENDGAME: ROOK TECHNIQUE ───────────────────────────────────────────────

    "Cutting off the enemy king with your rook is the most powerful technique in rook "
    "endgames. Place your rook on a rank or file that separates the defending king from "
    "the key area — for example, Rf5 cuts the king off from crossing the fifth rank while "
    "your own king marches to support the passed pawn. The further you cut the king off, "
    "the more powerful the restriction. A rook on the fifth rank keeping the king on the "
    "last three ranks combined with an active king on d5 often wins by force even without "
    "a direct passed pawn. Always check if a lateral cutoff (rook on the 5th, 6th, or 7th "
    "rank) is available before spending moves on other plans.",

    "The seventh rank is the most powerful square for a rook in the endgame. A rook on e7 "
    "or d7 attacks all unprotected pawns on that rank, boxes in the enemy king to the back "
    "rank, and supports your own pawns advancing to promotion. To reach the seventh rank, "
    "look for an open file that gives your rook access — often Re1-e7 or Rd1-d7 after a "
    "central file opens. Two rooks on the seventh rank win in virtually any non-fortress "
    "position. Even a single rook on the seventh is often decisive. Prioritize getting your "
    "rook to the seventh rank as soon as queens are exchanged.",

    "Rook vs two connected passed pawns is one of the most dynamically balanced endgame "
    "positions. The rook wins if it can pick off one pawn while keeping the second under "
    "control — typically by attacking from behind or the side. The pawns win if they are "
    "advanced enough to promote before the rook can stop both. The general rule: two pawns "
    "on the fifth rank beat the rook; two pawns on the fourth rank or behind usually lose "
    "to the rook with correct play. Your job with the rook is to attack the rear pawn first "
    "from behind, forcing the front pawn to stop and defend, then collect the rear pawn.",

    # ── ADVANCED STRATEGY ──────────────────────────────────────────────────────

    "To exploit a good knight vs bad bishop advantage, follow these steps: First, fix the "
    "opponent's pawns on the same color as their bishop — if they have a dark-squared bishop, "
    "advance your pawns to d5, e4, and f5 (all dark squares) to block it permanently. Second, "
    "establish your knight on a strong central outpost — d6 or e5 — where it cannot be "
    "attacked by pawns. Third, create a passed pawn on the side opposite to the bishop's "
    "activity. The knight can support pawn advances on both wings; the bad bishop can only "
    "patrol one color. This positional advantage converts slowly but reliably in the endgame.",

    "Prophylaxis is the habit of thinking about what your opponent wants to do before deciding "
    "on your own plan. Before every move, ask: 'What would my opponent play if it were their "
    "turn right now?' If the answer is dangerous — a knight invasion on f4, a pawn break with "
    "d5, or a rook doubling on the c-file — stop it first with a move like h3 (preventing "
    "Ng4), e4 (preventing d5), or Re1 (contesting the c-file). This proactive prevention "
    "is what separates strong positional players from reactive ones. A move that improves "
    "your position while also stopping the opponent's plan is almost always the best move "
    "available.",

    "The initiative — the ability to make threats your opponent must respond to — is worth "
    "tempo, space, and sometimes material. To maintain the initiative, every one of your moves "
    "should contain a threat, even if it is a positional one. If your opponent never gets a "
    "free move to improve their pieces, they cannot consolidate. When you have the initiative, "
    "avoid trades that allow consolidation — each exchange that 'simplifies' the position "
    "gives the opponent a free move. The correct approach: keep making threats with new pieces, "
    "advance pawns to open lines, and force the opponent to react until a decisive material "
    "or positional concession is made.",

    "The decision to push forward or consolidate depends on a simple principle: push when "
    "your position will deteriorate if you wait; consolidate when time is on your side. If "
    "your advantage is dynamic — an attack, an exposed king, a time-sensitive pawn storm — "
    "you must act immediately, because dynamic advantages evaporate. If your advantage is "
    "static — a better pawn structure, a good knight vs bad bishop, an extra pawn — you can "
    "take time to improve your position before converting. A common mistake is rushing to "
    "attack in a position where patient consolidation would convert the advantage more "
    "reliably. Read the type of advantage before deciding on the pace.",

    "Converting small advantages requires the technique of the two weaknesses. If your "
    "opponent has one weakness — say, a backward pawn on d6 — they can often defend it "
    "perfectly. Your job is to create a second weakness on the other side of the board. "
    "Advance your kingside pawns to h5, g5, creating pressure there while maintaining "
    "pressure on d6. The opponent cannot defend both weaknesses with limited pieces — "
    "defending one allows you to advance on the other. This technique is the foundation "
    "of converting a slight positional edge into a won endgame and is used in virtually "
    "every high-level positional game.",

    "Strategic piece exchange — trading your passive piece for the opponent's active one — "
    "is one of the most powerful positional weapons available. If the opponent has a dominant "
    "knight on d5 that you cannot attack with pawns, trade your bishop for it even at the "
    "cost of the bishop pair. If the opponent's rook is dominating an open file while yours "
    "is passive, offer an exchange of rooks to neutralize the file. The principle: do not "
    "measure the trade by whether you keep the bishop pair or some abstract positional rule; "
    "measure it by whether your position improves. Eliminating the opponent's best piece is "
    "often worth conceding a small material or positional cost.",

    # ── OPENING ERRORS ─────────────────────────────────────────────────────────

    "Developing a knight to the rim — Na3, Nh3, Na6, or Nh6 — in the opening is almost always "
    "a mistake. A knight on a3 has only four squares it can move to and zero central influence; "
    "a knight on h3 is even more limited and typically blocks the g-pawn advance. The rule 'a "
    "knight on the rim is dim' captures the practical reality: edge knights take several moves "
    "to reach useful squares (Na3-c2-e3 or Nh3-f4 takes two moves), and those tempos are "
    "development tempos you cannot afford. Always develop knights to c3, f3, c6, or f6 — "
    "squares where they immediately fight for the center and have maximum mobility.",

    "Pushing the f-pawn in the opening — f4 before castling — is one of the most dangerous "
    "decisions a player can make. The f-pawn is the primary shield of the king's castled "
    "position, and advancing it creates a permanent weakness on f4 and e4. If you play f4 "
    "before castling and the center opens, your king is stuck in the middle facing open "
    "diagonals and files. The exception is specific systems like the King's Gambit or Dutch "
    "Defense where f4 is the correct thematic move from the start. Outside these lines, "
    "castle first and only push f4 when your king is safe and your pieces are coordinated "
    "to support the advance.",

    "Bringing your queen out early — Qh5 on move three, Qf3 on move two, or Qe2 before "
    "development — hands the opponent free tempo. Every move the opponent spends attacking "
    "your queen with Nc6, Nf6, or g6 is simultaneously a useful developing move for them. "
    "After three or four queen retreats, the opponent has a fully developed position with "
    "tempo while your pieces sit undeveloped. The queen is strongest when all other pieces "
    "are developed and coordinated — only then does the queen's power multiply. Keep the "
    "queen back, develop your minor pieces and castle, and bring the queen to an active "
    "square only when it serves a concrete purpose.",

    "Failing to castle by move 12-14 is a serious danger signal. Every move your king spends "
    "in the center is a move the opponent can use to open files with d5, e5, or c5 pawn "
    "breaks targeting your exposed king. An uncastled king in an open or semi-open position "
    "faces threats from bishops on long diagonals, rooks on central files, and queen "
    "maneuvers to attacking squares. If you realize you have not castled by move 10 and the "
    "center is opening, prioritize castling above all else — even at the cost of a tempo or "
    "a small positional concession. A king in the center is a liability that the opponent "
    "will exploit.",

    "When your opponent plays an early h6 or a6 — passive moves that do not develop pieces "
    "or fight for the center — you gain a free tempo to improve your position. Do not waste "
    "this gift by playing an equally passive move. Instead, develop with purpose: bring a "
    "new piece to its best square, advance a central pawn to claim more space, or prepare "
    "castling. After 1.e4 e5 2.Nf3 h6, for example, White should simply play 3.Bc4 or 3.d4 "
    "continuing normal development. By the time the opponent's 'prophylactic' move turns out "
    "to be useful, you will have built a significant development lead and spatial advantage.",
]
