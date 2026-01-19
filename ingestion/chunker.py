import re

HEADER_PATTERN = re.compile(r"^\s*\d+(\.\d+)*\.?\s+.+", re.MULTILINE)

def clean_text(text: str) -> str:
    text = text.replace("\r", "")
    text = re.sub(r'\n{2,}', '\n', text)
    return text.strip()


def split_by_sections(text: str):
    """
    Dynamically splits text based on detected section headers.
    Returns list of (section_title, section_text)
    """
    matches = list(HEADER_PATTERN.finditer(text))

    sections = []

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        header = match.group().strip()
        content = text[start:end].replace(header, "").strip()

        sections.append((header, content))

    return sections


def chunk_text(text: str, max_tokens: int = 350):
    words = text.split()
    chunks = []

    for i in range(0, len(words), max_tokens):
        chunk = " ".join(words[i:i + max_tokens])
        if chunk.strip():
            chunks.append(chunk)

    return chunks
