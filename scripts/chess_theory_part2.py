"""
Expanded chess theory corpus — Part 2
Covers: Pawn Structure, Endgame Technique, King Safety, Rooks, Advanced Strategy
"""

CHESS_THEORY_PART2 = [

    # ── PAWN STRUCTURE: ISOLATED PAWN ────────────────────────────────────────
    "An isolated queen's pawn (IQP) on d4 or d5 is a permanent structural weakness. It cannot be defended by adjacent pawns and must be protected by pieces. The enemy should blockade it with a knight on d5 (or d4) and attack it with rooks.",
    "The side with the IQP gets full compensation in the form of active piece play, open files for rooks, and a space advantage. The IQP side must attack before the opponent simplifies into an endgame where the pawn is just a weakness.",
    "To fight against the IQP: blockade the pawn with a knight (Ne5 or Nd5), trade off the active pieces, and then win the endgame with the extra pawn structure advantage.",
    "With an IQP, launch an attack before trading pieces. The IQP gives central control and the d5 square for a knight. Use these assets aggressively — if you trade into an endgame, the pawn becomes a decisive weakness.",

    # ── PAWN STRUCTURE: DOUBLED PAWNS ────────────────────────────────────────
    "Doubled pawns are two pawns of the same color on the same file. They are generally a structural weakness — the rear pawn cannot advance until the front pawn moves. However, they can also open files for rooks.",
    "Doubled pawns on the c-file (doubled c-pawns) often arise in the Nimzo-Indian and Ruy Lopez. They restrict the opponent's queenside but limit pawn mobility. The side with doubled pawns must use dynamic piece play to compensate.",
    "When you give the opponent doubled pawns, ensure the positional compensation is real. Simply creating doubled pawns is not enough — you must have a concrete plan to exploit them (blockade, open a file toward them, exchange all pieces to enter the endgame).",
    "Doubled isolated pawns are almost always a decisive weakness. Two pawns on the same file, each undefended by adjacent pawns, require constant piece protection and are very difficult to defend in the endgame.",

    # ── PAWN STRUCTURE: BACKWARD AND HANGING PAWNS ───────────────────────────
    "A backward pawn is one that cannot advance because the adjacent pawns have gone further and the square in front is controlled by the opponent. It is a chronic weakness that ties defending pieces down.",
    "A backward pawn on a semi-open file is especially dangerous. The opponent can place a rook on the open file, attacking the backward pawn. The pawn cannot advance (the square in front is controlled) and cannot be defended by adjacent pawns.",
    "Hanging pawns (two adjacent pawns without neighboring pawns) on c5 and d5 (or c4 and d4) are dynamic but potentially weak. They control important central squares but become targets in the endgame. The side with hanging pawns must keep the position complex.",
    "To exploit hanging pawns: blockade one of them (usually with a knight), then attack the other. Once you force ...c4 or ...d4 (or c5/d5 advance), the pawn structure fragments and weaknesses multiply.",

    # ── PAWN STRUCTURE: PASSED PAWNS ─────────────────────────────────────────
    "A passed pawn has no opposing pawns on its file or adjacent files to stop it from promoting. In the endgame, a passed pawn is usually a winning advantage. The further advanced, the more dangerous.",
    "The principle of the passed pawn: advance it! A passed pawn must be pushed to tie down the opponent's pieces. A passed pawn that sits still gives the opponent time to blockade and neutralize it.",
    "The best blockader of a passed pawn is a knight. A knight on d4 (blocking a d3 passer) is rock-solid and cannot be easily dislodged. A bishop can only blockade from one color and can be attacked by pawns.",
    "Connected passed pawns on the 6th rank (or 5th rank) often win by themselves, even without piece support. Two pawns connected and advanced can outrun a single rook or require sacrificing material to stop them.",
    "A protected passed pawn (backed by another pawn) is the most dangerous type. The opponent cannot capture it without losing material. It is the most powerful positional trump in chess.",
    "In rook endgames, always place your rook behind your passed pawn. A rook behind the passed pawn gains power as the pawn advances. An opponent's rook in front of the pawn is passive and defensive.",

    # ── PAWN STRUCTURE: PAWN CHAINS AND BREAKS ───────────────────────────────
    "A pawn chain is a diagonal line of pawns protecting each other. The base of the chain (the rearmost pawn) is the weakest point — attack the base to undermine the whole structure.",
    "In the French Defense, White has a pawn chain e5-d4. Black should attack the base (d4) with ...c5. White counterattacks by pushing f4-f5. Each side attacks the base of the opponent's chain.",
    "A pawn break is an advance that challenges and disrupts the opponent's pawn structure. Identifying the correct pawn break is often the key to unlocking a seemingly blocked position.",
    "In the King's Indian, Black's main pawn break is ...f5 (attacking White's e4 pawn) or ...c5 (attacking White's d4 pawn). White's break is usually f4-f5 or d5 (closing the center and attacking queenside).",
    "In the Sicilian Dragon, White's pawn break is h4-h5 (if Black plays g6) or g4-g5 (dislodging the knight on f6). Black's break is ...b5-b4 attacking the c3 knight and opening the b-file.",
    "A minority attack uses fewer pawns to create a majority attack on the opponent. In the QGD Exchange structure, White pushes b4-b5-bxc6 with three pawns against Black's two, creating a weak isolated c-pawn on c6.",

    # ── ENDGAME: KING AND PAWN ENDINGS ───────────────────────────────────────
    "In king and pawn endgames, the king is a powerful fighting piece. Activate it immediately. The side that centralizes the king first usually wins.",
    "The opposition: two kings facing each other with an odd number of squares between them. The player NOT to move has the opposition and restricts the other king. Mastering the opposition is essential in pawn endgames.",
    "Direct opposition: kings two squares apart on the same rank or file. Diagonal opposition: kings two squares apart diagonally. Distant opposition: kings separated by three or five squares in a line.",
    "Triangulation: a king gains a tempo by taking a triangular path to reach the same square, forcing the opponent into a zugzwang. It works when one side has extra squares to maneuver and the other does not.",
    "The key square concept: for each pawn, there are key squares that, if the king reaches, guarantee promotion. For a d4 pawn, the key squares are c6, d6, and e6. If the attacking king gets to any of these, the pawn promotes regardless of the defender's king position.",
    "The square of the pawn: draw a square from the pawn's current position to the promotion square. If the defending king can step into this square on their turn, they can catch the pawn. Used to quickly judge king-and-pawn races.",
    "Pawn endgames with one extra pawn are often won but require precise king play. The attacking king must get in front of the pawn (using the key square) before the defending king can set up the opposition.",
    "Corresponding squares (reciprocal zugzwang) is an advanced concept where both kings are in mutual zugzwang — whoever moves loses. Mastering corresponding squares unlocks the deepest pawn endgame ideas.",

    # ── ENDGAME: ROOK ENDGAMES ───────────────────────────────────────────────
    "The Lucena Position is the fundamental winning technique in rook endgames with a pawn. The winning method is 'building a bridge': the attacking king shelters on the 5th rank file while the rook cuts off the defending king, then the pawn advances to promote.",
    "The Philidor Defense (not the opening) is the fundamental drawing technique in rook endgames one pawn down. Place the rook on the 6th rank (cutting off the attacking king), wait for the pawn to advance to the 6th, then switch to checking from behind.",
    "Rook endgames are the most common endgame type. Key principles: (1) activate your rook immediately, (2) place it behind passed pawns (yours or the opponent's), (3) cut off the enemy king with your rook, (4) don't allow a Lucena position.",
    "In rook endgames, the rook's activity is more important than material. An active rook that checks the king continuously can save a lost position. A passive rook loses even with equal material.",
    "Rook vs. rook + pawn on the 7th rank: the defending rook must immediately go active (checking from behind or the side). Passive rook defense always loses. The Philidor method must be applied precisely.",
    "The 'lawnmower' technique: in a king and two rooks vs. king endgame, the rooks take turns checking the king down the board, cutting off escape squares rank by rank until checkmate on the edge.",
    "When you have an extra passed pawn in a rook endgame, do not rush to trade rooks. Rook trades often lead to lost pawn endgames if the position is not accurately calculated. Keep the rooks on to increase pressure.",

    # ── ENDGAME: MINOR PIECE ENDINGS ─────────────────────────────────────────
    "Bishop vs. knight endgames: bishops favor open positions with pawns on both wings; knights favor closed positions with fixed pawn structures. A knight's outpost in a closed position is worth as much as a rook.",
    "Opposite-colored bishop endgames are notorious for being drawn even with two or three extra pawns. The defending side's bishop controls squares the attacking bishop can never reach. Draw fortress positions are common.",
    "Same-colored bishop endgames: the stronger side should put pawns on the opposite color of the bishop (so the bishop can attack them) and the weaker side should put pawns on the same color as the bishop (so the bishop defends them).",
    "Knight endgames are similar to king and pawn endgames in their sensitivity to zugzwang. Knights cannot lose a tempo (they always change square color), so zugzwang patterns behave differently from bishop or king endgames.",
    "Bishop vs. rook endgame: generally a draw if the weaker side plays correctly. The defending king and bishop must stay together to avoid the rook forking or skewering them. The corner the bishop cannot control is the key concept.",
    "Two bishops vs. knight and bishop (or two knights): the bishop pair usually wins in open positions because they cover more ground and work well together. In closed positions, the knights can hold.",

    # ── ENDGAME: QUEEN ENDINGS ────────────────────────────────────────────────
    "Queen and pawn endgames are generally won if the pawn is advanced, but queen vs. queen + pawn is drawish if the defending queen can perpetually check. The attacking side must shepherd the pawn carefully.",
    "Queen vs. rook is theoretically won for the queen but practically complex. The queen must force the rook away from the king and deliver checkmate in specific patterns (Philidor position). It requires many moves with no pawn.",
    "Stalemate is a constant danger in queen endgames. When the opponent is reduced to king + pawn (especially rook pawn or bishop pawn on the 7th), always check for stalemate traps before winning 'automatically'.",
    "Queen vs. passed pawn on the 7th rank: the queen wins against all pawns except the rook pawn or bishop pawn that promotes to a stalemate square. Even then, the queen wins if the attacking king is close enough to help.",

    # ── KING SAFETY ───────────────────────────────────────────────────────────
    "Never leave your king in the center if the position is open or semi-open. Open files and diagonals pointing toward an uncastled king are extremely dangerous. Castle before the position opens up.",
    "The fianchettoed king (kingside castle + g3 + Bg2 or g6 + Bg7) is well-protected. The bishop on g2 (or g7) is a powerful shield. Trading that bishop away weakens the king dramatically ('weakening the dragon diagonal').",
    "A pawn storm against a castled king: if you have castled on opposite wings, launch a pawn storm against the opponent's king immediately. The race is won by the side whose attack arrives first.",
    "Pawn advances in front of your own castled king (h3, g4) are double-edged. They can prevent piece invasions (g4 stops ...Nf4) but weaken the king's shelter. Judge carefully based on whether your opponent can open lines quickly.",
    "The h3 prophylaxis move (or ...h6) is one of the most common moves in chess. It prevents Bg5 (or ...Bg4) pins and gives the king a flight square. It slightly weakens the g3 square but is often worth it.",
    "An exposed king in the center is often the deciding factor in tactics. Before calculating a complex combination, check if the opponent's king is exposed. Exposed kings invite sacrifices.",
    "King safety in the endgame: once queens are off, the king should rush to the center. The king becomes a powerful attacking piece. 'A king in the center is an endgame king' — centralize it aggressively.",
    "If you have castled on the same side as your opponent, king attacks are less common (you'd expose your own king too). Positional play and pawn structure become the key factors.",
    "A knight invasion on f4 (or ...f5) near the castled king is very dangerous. The knight on f4 can jump to h5 (threatening Nxg7 or Nf6+) or g6 (attacking h8 and creating mating threats). Drive away invading knights immediately.",

    # ── ROOK ACTIVITY AND ROOK ENDINGS ───────────────────────────────────────
    "Open files are the rook's natural habitat. Place your rooks on open or semi-open files early. If no files are open, identify which pawns are most likely to be exchanged and pre-position your rook there.",
    "Doubling rooks on an open file (both rooks stacked) is a very powerful battery. It is difficult to contest and creates enormous pressure. The opponent usually has to give up one of their own rooks or concede material.",
    "A rook on the 7th rank attacks all unprotected pawns on the 7th rank and boxes in the enemy king. Achieving this is often a major advantage. Two rooks on the 7th rank win in virtually any position.",
    "The 'pig' (rook on the 7th rank that grabs pawns freely): a rook on the 7th that has nothing opposing it sweeps across the rank. Even if it only wins one or two pawns, the activity gained is worth it.",
    "In rook endgames, king activity is crucial. The side with the more active king and rook almost always wins. Do not keep your king passive while your rook fights alone.",
    "Do not rush rook endgames. Take time to activate your pieces, cut off the enemy king, and centralize your own king before advancing passed pawns. Precise king positioning often determines the outcome.",

    # ── ADVANCED POSITIONAL CONCEPTS ─────────────────────────────────────────
    "An outpost is a square that cannot be attacked by the opponent's pawns and is within the opponent's half of the board. A knight on an outpost is a long-term positional trump — it is hard to dislodge and exerts great influence.",
    "Creating an outpost: trade the pawn that would attack the outpost square. After ...d5 cxd5 or c5 bxc5, a square like d6 or c4 may become permanently available for your knight.",
    "Dynamic vs. static advantages: static advantages (pawn structure, outposts, bishop pair) persist through exchanges. Dynamic advantages (active pieces, king attack, initiative) must be exploited immediately before they dissipate.",
    "The Steinitz principle: accumulate small advantages. Every small positional plus (better pawn structure, more active piece, a slight lead in development) adds up. Do not try to force a win from a minimal edge — build it gradually.",
    "Imbalances: Silman's concept of imbalances identifies the factors that differ between the two sides: pawn structure, minor piece type, space, material, king safety, initiative, and piece activity. The player who better uses their imbalances wins.",
    "A restriction strategy: when the opponent has a bad bishop, advance pawns to the same color as that bishop. Fix the pawns so the bishop is permanently bad, then use your pieces to dominate.",
    "Good knight vs. bad bishop: a knight that is established on a solid outpost in front of a blocked bishop is a classic positional theme. The bishop cannot attack the knight and the knight dominates the position indefinitely.",
    "Space advantage: when you have more space, keep pieces on and avoid exchanges. Piece exchanges give the cramped side freedom. Attack only after all your pieces are optimally placed.",
    "The minority attack: use fewer pawns to create weaknesses in the opponent's majority. Classic example: in the QGD Exchange structure, White advances b4-b5-bxc6, creating an isolated or backward pawn in Black's structure.",
    "Prophylaxis in practice: before your move, always ask 'What does my opponent want to do next turn?' If the answer is dangerous, stop it first. Prophylaxis is the hallmark of positional mastery.",
    "Strategic exchanges: exchanging a good piece for a bad one is a powerful strategic weapon. Trading your knight for the opponent's dominating bishop (or vice versa) can relieve pressure or lock in a structural advantage.",
    "Piece coordination: pieces working together are stronger than the sum of their parts. A bishop-rook battery on a diagonal and file, a queen-rook battery, or a knight-bishop pair targeting the same weaknesses multiply their effectiveness.",
    "Zugzwang in practical play: positions where the player to move is forced to worsen their position. Zugzwang is not just an endgame concept — it can occur in middlegame positions with locked pawn structures.",
    "The initiative: the side with the initiative dictates the tempo and forces the opponent to react. Maintaining the initiative is worth a pawn in many positions. Giving up the initiative allows the opponent to seize the agenda.",
    "Converting an advantage in the endgame requires: (1) activating the king, (2) creating and advancing passed pawns, (3) restricting the opponent's king, (4) trading into a won endgame type. Do not rush — be methodical.",
]
