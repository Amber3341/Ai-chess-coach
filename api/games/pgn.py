def normalize_pgn_text(pgn_text: str) -> str:
    """Tolerate extra blank lines between PGN tag pairs.

    Some copy/paste paths insert a blank line after every header. Standard PGN
    uses the first blank line to separate headers from moves, so python-chess
    otherwise reads those files as header-only games.
    """
    lines = pgn_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    headers: list[str] = []
    movetext: list[str] = []
    in_headers = True

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if in_headers and stripped.startswith("["):
            headers.append(stripped)
            continue

        in_headers = False
        movetext.append(stripped)

    if headers and movetext:
        return "\n".join(headers) + "\n\n" + " ".join(movetext) + "\n"

    return "\n".join(headers + movetext).strip() + "\n"
