"""
Expanded chess theory corpus for RAG — Part 1
Covers: Opening Principles, Major Openings (e4 and d4 systems), Tactical Motifs
"""

CHESS_THEORY_PART1 = [

    # ── OPENING PRINCIPLES ──────────────────────────────────────────────────
    "Control the center with pawns. The four central squares (e4, d4, e5, d5) are the most important on the board. Pieces placed near the center influence more squares and have greater mobility.",
    "Develop your minor pieces early. Knights and bishops should come out in the first several moves. Aim to develop a new piece every turn in the opening rather than moving the same piece twice.",
    "Castle early to protect your king. Castling connects the rooks and moves the king to safety behind a pawn shield. Delay it only when you have a very concrete reason.",
    "Do not bring the queen out early. The queen can be harassed by cheaper pieces, costing you tempo. The exception is specific lines where the queen actively helps development or grabs a pawn safely.",
    "Avoid moving the same piece twice in the opening unless forced. Every extra move on one piece is a development tempo wasted. Tempo is crucial in the opening.",
    "Connect your rooks before launching an attack. A rook connected to another rook means both can support each other instantly. Complete development first.",
    "Do not make unnecessary pawn moves in the opening. Each pawn move creates weaknesses and takes a tempo away from development. Only advance pawns that open lines or fight for the center.",
    "Always ask 'why?' before accepting a gambit. Many gambits give a pawn for fast development and king attack. Count tempos before grabbing material.",
    "The bishop pair is a long-term advantage. Two bishops control all squares and dominate open positions. Try to preserve your bishop pair in the early game.",
    "Knights are better in closed positions; bishops in open ones. If the pawn structure is fixed and closed, knights can find stable outposts. If lines are open, bishops can dominate.",

    # ── RUY LOPEZ (SPANISH GAME) ─────────────────────────────────────────────
    "The Ruy Lopez begins 1.e4 e5 2.Nf3 Nc6 3.Bb5. White pins the knight defending e5, aiming to win the center pawn. It is one of the most studied and principled openings in chess history.",
    "In the Ruy Lopez, White's long-term plan is to control d4 and e5 with pawns, dominate the center, and press on the queenside with a4-b4. Black must find counterplay or White's advantage grows.",
    "The Closed Ruy Lopez (3...a6 4.Ba4 Nf6 5.0-0 Be7 6.Re1 b5 7.Bb3 d6 8.c3 0-0) is a rich positional system. Black solidifies the center while planning the Breyer (...Nb8-d7) or Chigorin (...Na5) maneuvers.",
    "The Marshall Attack (3...a6 4.Ba4 Nf6 5.0-0 Be7 6.Re1 b5 7.Bb3 0-0 8.c3 d5) is Black's most aggressive choice. Black sacrifices a pawn for long-term piece activity and king attack. The Anti-Marshall (8.a4 or 8.h3) avoids it.",
    "The Berlin Defense (3...Nf6) is an ultra-solid choice for Black. After 4.0-0 Nxe4 5.d4 Nd6 the queens often come off, leading to a solid but slightly passive endgame for Black. It became famous for being a drawing weapon at the highest level.",
    "In the Ruy Lopez, Black should never exchange too many pieces without getting something in return. Passive defense in a slightly worse endgame is often preferable to desperate counterattacks.",

    # ── ITALIAN GAME ─────────────────────────────────────────────────────────
    "The Italian Game begins 1.e4 e5 2.Nf3 Nc6 3.Bc4, targeting the f7 square. White typically follows with d3 and c3 for a slow positional buildup or d4 for sharp play.",
    "The Giuoco Piano (3.Bc4 Bc5 4.c3 Nf6 5.d4) leads to sharp central play. White challenges for the center immediately. Black must be precise to equalize — the key is not to give White a dominant center for free.",
    "The Two Knights Defense (3.Bc4 Nf6) invites White to attack with 4.Ng5 or play solidly with 4.d4. After 4.Ng5 d5 5.exd5 Na5, Black sacrifices a pawn for active piece play — the Fried Liver Attack after ...Nxf7 is dangerous if Black is unprepared.",
    "The Evan's Gambit (3.Bc4 Bc5 4.b4) sacrifices a pawn for rapid development and central control. White gets enormous pressure. Black must return the pawn at the right moment to equalize.",

    # ── SICILIAN DEFENSE ─────────────────────────────────────────────────────
    "The Sicilian Defense (1.e4 c5) is Black's most popular and combative response to e4. It fights for the center asymmetrically — Black gets the semi-open c-file and dynamic counterplay at the cost of giving White a space advantage.",
    "In the Open Sicilian (1.e4 c5 2.Nf3 followed by 3.d4), White gets central control and an open d-file for pieces. Black gets a semi-open c-file and aims for queenside counterplay while White attacks the kingside.",
    "The Najdorf Sicilian (2...d6 3.d4 cxd4 4.Nxd4 Nf6 5.Nc3 a6) is Black's sharpest option. The move ...a6 prevents Bb5 and prepares ...e5 or ...b5. White typically plays 6.Be3, 6.Bg5, or 6.Be2. Theory is extremely deep.",
    "The Dragon Sicilian (2...d6 3.d4 cxd4 4.Nxd4 Nf6 5.Nc3 g6) features Black's fianchettoed dragon bishop on g7. White usually plays the Yugoslav Attack (Be3, Qd2, 0-0-0) with a massive kingside pawn storm. Black counterattacks on the queenside.",
    "The Scheveningen Sicilian (...e6 with ...d6) is a solid, flexible system. Black keeps all options open and avoids early commitments. The pawn on e6 limits Black's bishop but gives a solid pawn structure.",
    "The Kan (Paulsen) Sicilian (...a6 with ...e6) gives maximum flexibility. Black avoids early commitments and can choose structures based on White's setup. A solid and underrated system.",
    "In the Sicilian, Black should launch counterplay before White's attack becomes unstoppable. If Black just defends, White will eventually crash through on the kingside. Active counterplay on the c-file or queenside is essential.",
    "Against the Sicilian, White's typical plan is to castle queenside and attack with g4-g5, h4-h5 pawn storms. Black simultaneously attacks down the c-file with Rc8, Nc4, b5-b4. It is a race where both sides attack the opposing king.",

    # ── FRENCH DEFENSE ───────────────────────────────────────────────────────
    "The French Defense (1.e4 e6) is a solid choice. Black plans ...d5 to challenge the center. The drawback is the light-squared bishop on c8, which often becomes a 'bad bishop' blocked by its own pawns on e6 and d5.",
    "In the French Defense Exchange Variation (3.exd5 exd5), positions become symmetrical and drawish. White gives up the center but Black's bad bishop problem is solved. Played by White when aiming for a quick draw.",
    "The French Defense Advance Variation (3.e5) closes the center and leads to slow maneuvering. White has space but must prevent Black's ...f6 counterattack. Black plays ...c5 and ...Nc6 to attack the e5 pawn.",
    "The Winawer Variation (3.Nc3 Bb4) is sharp and double-edged. After 4.e5 c5 5.a3 Bxc3+ 6.bxc3 Ne7, White gets the bishop pair and attacking chances while Black has structural counterplay with ...Qa5 and ...Ba6.",
    "The key thematic move in the French Defense for Black is ...c5, attacking the d4 pawn. Black should not hesitate to trade their bad bishop for White's active pieces to relieve the position.",

    # ── CARO-KANN DEFENSE ────────────────────────────────────────────────────
    "The Caro-Kann Defense (1.e4 c6) prepares ...d5 with solid pawn support. Black's light-squared bishop will not be locked in, unlike in the French. The position is solid but can be slightly passive.",
    "The Classical Caro-Kann (4.Nf3 Bf5 or 4.Nd2) leads to strategic battles. Black's light-squared bishop is well-placed on f5. White tries to exploit the d6 square as a weakness.",
    "The Advance Caro-Kann (3.e5) is similar to the French Advance but Black has already played ...c6, giving the queenside more support. Black aims for ...Bf5, ...e6, ...c5 to counterattack.",
    "The Panov-Botvinnik Attack (3.exd5 cxd5 4.c4) gives White an IQP structure with active piece play. Black must find counterplay actively; passive defense will be overwhelmed by White's piece activity.",

    # ── QUEEN'S GAMBIT ───────────────────────────────────────────────────────
    "The Queen's Gambit (1.d4 d5 2.c4) is not really a gambit. If Black accepts (2...dxc4), White regains the pawn easily while gaining the center. Black cannot hold the extra pawn without incurring major positional concessions.",
    "In the Queen's Gambit Declined (2...e6), Black solidifies d5 but locks in the c8 bishop. White plans to attack the d5 pawn with Nc3, Nf3, Bg5. Black must free the c8 bishop with ...Nbd7 and ...dxc4 or ...c5.",
    "The QGD Exchange Variation (3.cxd5 exd5) creates a symmetrical pawn structure with a minority attack. White plays b4-b5-bxc6 to create a weak pawn on c6. Black must find active counterplay with ...Nf6, ...Bf5, ...Ne4.",
    "The Tarrasch Defense (2...e6 3.Nc3 c5) is a fighting system. Black accepts an isolated queen's pawn (IQP) after cxd5 exd5 for active piece play. The IQP is a permanent weakness but gives development and central control.",
    "In the Queen's Gambit Accepted (2...dxc4 3.e3 e5), Black tries to hold the pawn with ...b5. White plays 4.Bxc4 and gets fast development. Black must return the pawn at the right moment to equalize.",

    # ── KING'S INDIAN DEFENSE ────────────────────────────────────────────────
    "The King's Indian Defense (1.d4 Nf6 2.c4 g6 3.Nc3 Bg7 4.e4 d6 5.Nf3 0-0) is a hypermodern setup. Black concedes the center early and plans to undermine it with ...e5 or ...c5. Rich counterplay potential.",
    "In the Classical King's Indian (6.Be2 e5 7.0-0), White has a broad center and Black attacks it with ...e5. The key plan for Black is the knight maneuver ...Ne8-d6-f4 or ...c6 and ...d5 to break open the position.",
    "The Sämisch Variation against the King's Indian (6.f3) aims to build an even stronger center and attack. White may castle queenside and launch a direct pawn storm. The game often becomes very tactical and double-edged.",
    "The Averbakh Variation against the King's Indian (6.Bg5) pressures f6 and aims to prevent ...e5. Black must find active play quickly or White will build an overwhelming center.",

    # ── NIMZO-INDIAN DEFENSE ─────────────────────────────────────────────────
    "The Nimzo-Indian Defense (1.d4 Nf6 2.c4 e6 3.Nc3 Bb4) pins the c3 knight and fights for the center without ...d5. Black often trades the bishop for the knight, giving White doubled pawns in exchange for long-term structural compensation.",
    "After 4.e3 0-0 5.Bd3 d5 (the Rubinstein Nimzo), play becomes positional. Black's plan is ...dxc4 Bxc4 ...c5 to pressure White's center and exploit the doubled pawns.",
    "The Sämisch Nimzo-Indian (4.a3 Bxc3+ 5.bxc3) gives White the bishop pair but doubled c-pawns. Black must prevent White from mobilizing the bishop pair. The position often becomes very sharp.",

    # ── ENGLISH OPENING ──────────────────────────────────────────────────────
    "The English Opening (1.c4) is a flexible, hypermodern system. White controls d5 without immediately committing with d4. The game can transpose into many structures depending on Black's response.",
    "Against the English, Black's solid option is 1...c5 (Symmetrical English), fighting for equal central control. Play often becomes positional with complex maneuvering around c4 and d4.",
    "The English can also transpose to a reversed Sicilian (1.c4 e5). White has an extra tempo over the Sicilian. Common White plans include Nc3, g3, Bg2, e3, Nge2, d4.",

    # ── TACTICAL MOTIFS: FORKS ───────────────────────────────────────────────
    "A fork is a move where one piece attacks two or more opponent pieces simultaneously. The attacker typically captures one of the forked pieces on the next move if the opponent cannot defend both.",
    "Knight forks are the most common. A knight on d5 can fork a king on c7 and a rook on e7 or f6. Always scan for knight fork patterns, especially when a knight can reach a square attacking the king and a rook/queen simultaneously.",
    "Pawn forks are powerful and often missed. A pawn on e5 attacking both d6 and f6 can win a piece if both defenders cannot escape. Pawn forks are irreversible and create lasting structural damage.",
    "Queen forks are dangerous but risky since the queen can then be attacked. Before playing a queen fork, ensure the queen has a safe escape square after capturing.",
    "A discovered fork occurs when a piece moves to reveal an attack by the piece behind it, while simultaneously the moving piece creates its own fork or check. This type of combination is very difficult to defend against.",

    # ── TACTICAL MOTIFS: PINS ────────────────────────────────────────────────
    "A pin is a tactic where a piece cannot move because doing so would expose a more valuable piece (or the king) behind it. An absolute pin is against the king; a relative pin is against any other piece.",
    "To break a pin, you can: (1) move the pinned piece if it doesn't lose material, (2) interpose another piece to block the pin, (3) attack the pinning piece to force it to retreat or be captured, or (4) move the shielded piece out of the line.",
    "Piling on a pin means adding more attackers to the pinned piece. If a knight is pinned by a bishop, bring a rook to attack it further. The pinned piece cannot take any of the attackers.",
    "In the opening, Bg5 pinning the f6 knight against the queen is a classic example. Black must decide whether to break the pin with ...h6 (driving the bishop away at the cost of weakening g6) or accept the pin and develop elsewhere.",

    # ── TACTICAL MOTIFS: SKEWERS AND DISCOVERED ATTACKS ─────────────────────
    "A skewer is the reverse of a pin. The more valuable piece is attacked first and forced to move, exposing a less valuable piece behind it for capture. Rooks and bishops commonly deliver skewers.",
    "A discovered attack occurs when a piece moves and reveals an attack by the piece behind it. The moving piece can simultaneously create a second threat, making it nearly impossible to defend.",
    "A discovered check is one of the most powerful moves in chess. The king must respond to the check, allowing the moving piece to capture freely or deliver another threat. Always look for discovered check opportunities.",
    "A double check (discovered check where both pieces give check simultaneously) forces the king to move — it is the only legal response. Double checks often lead to forced checkmates.",

    # ── TACTICAL MOTIFS: OVERLOADING AND DEFLECTION ──────────────────────────
    "Overloading occurs when a piece has too many defensive duties and cannot fulfill them all. Attack both targets simultaneously and one will fall.",
    "Deflection is a tactic that forces an important defending piece away from its post. A sacrifice or forcing move pulls the defender off the key square or diagonal, allowing the main combination to succeed.",
    "Removing the defender (also called 'removing the guard') means capturing or deflecting the piece that is protecting the key target. Once the defender is gone, the target is free to capture.",
    "Zwischenzug (in-between move) is an intermediate move — usually a check or capture — played instead of the 'expected' recapture. It changes the nature of the position and often wins material or forces a favorable resolution.",

    # ── CHECKMATE PATTERNS ───────────────────────────────────────────────────
    "Back-rank checkmate: the opponent's king is trapped on the back rank by its own pawns, and a rook or queen delivers checkmate. Always create a 'luft' square (h3, g3, etc.) to avoid this.",
    "Smothered mate: a knight delivers checkmate to a king surrounded by its own pieces with no escape. The typical pattern involves a queen sacrifice to force the king to be enclosed.",
    "Anastasia's mate: a rook and knight work together. The knight cuts off the king's escape squares while the rook delivers checkmate along the h-file (or a-file).",
    "Arabian mate: a rook and knight cooperate where the knight covers the king's escape squares in one direction and the rook delivers the mating blow.",
    "Scholar's mate attempt (2.Bc4, 3.Qh5, 4.Qxf7) is a very early checkmate threat. Black defends with 3...Nf6 (attacking the queen) or 3...g6 (driving the queen away). Never ignore threats to f7.",
    "The 'Fool's Mate' (1.f3 e5 2.g4 Qh4#) is the fastest checkmate in two moves. The lesson: never weaken the king's position with unnecessary pawn moves (f3, g4) in the opening.",
    "A rook lift (bringing a rook to the 3rd rank via Ra1-Ra3-Rh3) is a common attacking motif to shift a rook to the kingside without blocking pieces and threatening Rxh7.",

    # ── TACTICAL COMBINATIONS ────────────────────────────────────────────────
    "The Greek Gift sacrifice (Bxh7+) works when: (1) Black has castled kingside, (2) there is a knight on f3 to join the attack, (3) the queen can reach h5, and (4) Black's knight is on f6 (not g8). After ...Kxh7, Ng5+ and Qh5+ follows.",
    "The f7 weakness is a recurring theme. f7 is defended only by the king in the opening. Tactics involving Ng5, Bc4, Qh5 targeting f7 are common in many openings.",
    "A combination of bishop sacrifice on h6 (Bxh6 gxh6 Qxh6) followed by a rook lift to g3 or f5 can create a decisive kingside attack. This pattern works when Black's king is stripped of pawn cover.",
    "The Windmill (or seesaw) is a combination where a rook and bishop deliver repeated checks, picking up pieces each time. The king is forced to shuffle between squares while losing material.",

    # ── MIDDLEGAME STRATEGY: PIECE ACTIVITY ──────────────────────────────────
    "Piece activity is the most important factor in the middlegame. An active piece in the center beats a passive piece on the edge, even with identical material. Always ask: 'Which of my pieces is worst placed? How do I improve it?'",
    "The principle of the worst-placed piece: identify your least active piece and make a plan to improve it. This avoids aimless moves and keeps your position improving systematically.",
    "A knight on the rim is dim. Knights lose about half their mobility on the edge of the board and almost all of it in a corner. Keep knights centralized on e4, d4, f4, c5, etc.",
    "Bishops should be placed on open diagonals. Before exchanging pawns, consider which diagonal will open up and which of your bishops will benefit. Trade your bad bishop for the opponent's active one when possible.",
    "Rooks need open files to be effective. Place rooks on open or semi-open files, behind passed pawns, and on the 7th rank (a 'pig on the 7th'). Doubled rooks on an open file are very powerful.",
    "The 7th rank rook is devastating. A rook on the 7th rank attacks unprotected pawns and restricts the enemy king to the back rank. Two rooks on the 7th rank often win regardless of material.",

    # ── MIDDLEGAME STRATEGY: PLANNING ────────────────────────────────────────
    "Before making a move, ask three questions: (1) What is my opponent threatening? (2) What is my plan? (3) Does my move help my plan or stop the threat? This prevents reactive, move-to-move play.",
    "Prophylaxis is the habit of preventing the opponent's plan before it materializes. Even if your position is fine, think about what your opponent would like to do next and stop it.",
    "The two-weakness principle: if your opponent has one weakness, they can often defend it perfectly. Create a second weakness on the other wing. The defender cannot protect both weaknesses at the same time.",
    "Transformation of advantage: when you have a material advantage, trade pieces (not pawns). When you have a positional advantage (better pawn structure, better pieces), keep pieces on and avoid liquidation that gives the opponent activity.",
    "Space advantage should be maintained by keeping pieces on and avoiding exchanges. In a spacious position, your pieces have more room to maneuver. In a cramped position, your pieces are restricted.",
    "Do not rush. When you have a clear advantage, improve your position methodically before striking. Many games are lost by attacking too early before the position is ready.",
]
