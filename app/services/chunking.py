"""Deterministic text chunking engine for UrbanLens knowledge documents."""

import re


def chunk_text(
    text: str,
    chunk_size: int = 600,
    overlap: int = 100,
    min_chunk_size: int = 40,
) -> list[str]:
    """Split text into deterministic, boundary-aware chunks with overlap.

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

    # Break oversized paragraphs into sentence blocks
    atomic_units: list[str] = []
    for para in paragraphs:
        if len(para) <= chunk_size:
            atomic_units.append(para)
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
        # Avoid creating a tiny trailing duplicate chunk if covered by previous chunk
        if not chunks or len(combined) >= min_chunk_size or combined not in chunks[-1]:
            chunks.append(combined)

    return chunks
