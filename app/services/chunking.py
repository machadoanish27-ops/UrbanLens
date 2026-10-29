"""Deterministic, structure-aware text chunking engine for UrbanLens knowledge documents."""

import re


HEADING_PATTERN = re.compile(r"^(?:#{1,6}\s+.*|[A-Z0-9\s\-_]{3,}:|[A-Z\s]{4,})$")


def is_heading(line: str) -> bool:
    """Detect whether a line is likely a section header."""
    s = line.strip()
    if not s or len(s) > 100:
        return False
    return bool(HEADING_PATTERN.match(s)) or s.startswith(("# ", "## ", "### ", "#### "))


def chunk_text(
    text: str,
    chunk_size: int = 600,
    overlap: int = 100,
    min_chunk_size: int = 40,
) -> list[str]:
    """Split text into deterministic, structure-aware chunks with overlap.

    Respects headings, paragraph boundaries, and list structures.

    Args:
        text: Normalized input text string.
        chunk_size: Target maximum characters per chunk.
        overlap: Character overlap between consecutive chunks.
        min_chunk_size: Minimum characters required to form an independent chunk.

    Returns:
        List of non-empty text chunks.
    """
    clean_text = text.strip()
    if not clean_text:
        return []

    if len(clean_text) <= chunk_size:
        return [clean_text]

    # Split into structural paragraph units
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", clean_text) if p.strip()]
    if not paragraphs:
        paragraphs = [clean_text]

    # Break oversized paragraphs into sentence / list blocks
    atomic_units: list[str] = []
    for para in paragraphs:
        if len(para) <= chunk_size:
            atomic_units.append(para)
        else:
            # Check if this paragraph contains list items
            if "\n-" in para or "\n*" in para or re.search(r"\n\d+\.", para):
                list_items = [item.strip() for item in para.split("\n") if item.strip()]
                for item in list_items:
                    if len(item) <= chunk_size:
                        atomic_units.append(item)
                    else:
                        sentences = re.split(r"(?<=[.!?])\s+", item)
                        for s in sentences:
                            s_strip = s.strip()
                            if s_strip:
                                atomic_units.append(s_strip)
            else:
                # Split paragraph on sentence boundaries
                sentences = re.split(r"(?<=[.!?])\s+", para)
                for s in sentences:
                    s_strip = s.strip()
                    if not s_strip:
                        continue
                    # If a single sentence exceeds chunk_size, split by whitespace words
                    if len(s_strip) > chunk_size:
                        words = s_strip.split()
                        cur_part: list[str] = []
                        cur_len = 0
                        for w in words:
                            if cur_len + len(w) + 1 > chunk_size and cur_part:
                                atomic_units.append(" ".join(cur_part))
                                cur_part = [w]
                                cur_len = len(w)
                            else:
                                cur_part.append(w)
                                cur_len += len(w) + 1
                        if cur_part:
                            atomic_units.append(" ".join(cur_part))
                    else:
                        atomic_units.append(s_strip)

    # Accumulate atomic units into chunks of ~chunk_size with overlap
    chunks: list[str] = []
    current_chunk: list[str] = []
    current_len = 0

    for unit in atomic_units:
        unit_len = len(unit)
        # Avoid leaving orphaned heading at the very end of a chunk
        if current_chunk and is_heading(current_chunk[-1]) and (current_len + unit_len + 1 > chunk_size):
            orphaned_heading = current_chunk.pop()
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
            current_chunk = [orphaned_heading, unit]
            current_len = len(orphaned_heading) + len(unit) + 2
            continue

        if current_len + unit_len + 1 > chunk_size and current_chunk:
            combined = "\n\n".join(current_chunk)
            chunks.append(combined)

            # Build overlap from trailing units
            overlap_units: list[str] = []
            overlap_len = 0
            for u in reversed(current_chunk):
                if overlap_len + len(u) + 1 <= overlap:
                    overlap_units.insert(0, u)
                    overlap_len += len(u) + 1
                else:
                    break

            current_chunk = overlap_units + [unit]
            current_len = sum(len(u) for u in current_chunk) + max(0, len(current_chunk) - 1)
        else:
            current_chunk.append(unit)
            current_len += unit_len + 1

    if current_chunk:
        combined = "\n\n".join(current_chunk)
        if not chunks or len(combined) >= min_chunk_size or combined not in chunks[-1]:
            chunks.append(combined)

    return chunks
