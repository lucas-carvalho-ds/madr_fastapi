import unicodedata


def sanitize_name(name: str) -> str:  # pragma: no cover
    if not isinstance(name, str):
        return name

    # Normalize to composed form to keep accented characters
    s = unicodedata.normalize('NFKC', name)

    # Convert any whitespace to simple space
    s = ''.join(ch if not ch.isspace() else ' ' for ch in s)

    # Keep letters (L*), numbers (N*), and spaces only
    cleaned = ''.join(
        ch
        for ch in s
        if unicodedata.category(ch)[0] in {'L', 'N'} or ch == ' '
    )

    # Collapse multiple spaces and trim
    cleaned = ' '.join(cleaned.split())

    return cleaned.lower()
