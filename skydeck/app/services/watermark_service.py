"""Server-side PDF watermarking engine.

Uses **reportlab** to generate a transparent watermark overlay containing
the user's name, timestamp, a unique hash ID, and a CONFIDENTIAL notice.
The overlay is then merged onto every page of the source PDF using **pypdf**.

The entire pipeline runs in-memory — no temp files touch disk.
"""

from __future__ import annotations

import hashlib
import io
import secrets
from datetime import datetime, timezone

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.core.config import settings

_FONT_SIZE = settings.WATERMARK_FONT_SIZE
_FONT_NAME = "Helvetica"
_WATERMARK_COLOR = Color(0.6, 0.6, 0.6, alpha=0.18)


def generate_watermark_hash(user_id: int, manual_id: int) -> str:
    """Produce a unique, traceable hash ID for this download event.

    Combines user id, manual id, a random nonce, and the current
    timestamp into a SHA-256 digest truncated to 16 hex chars.
    """
    raw = f"{user_id}:{manual_id}:{secrets.token_hex(8)}:{datetime.now(timezone.utc).isoformat()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _build_watermark_page(
    width: float,
    height: float,
    user_name: str,
    timestamp: str,
    watermark_hash: str,
) -> io.BytesIO:
    """Generate a single-page transparent PDF overlay via reportlab."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(width, height))

    c.setFont(_FONT_NAME, _FONT_SIZE)
    c.setFillColor(_WATERMARK_COLOR)

    c.saveState()
    c.translate(width / 2, height / 2)
    c.rotate(45)

    line_spacing = _FONT_SIZE * 1.8
    lines = [
        "CONFIDENTIAL",
        f"{user_name}",
        f"{timestamp}",
        f"ID: {watermark_hash}",
    ]
    y_offset = (len(lines) - 1) * line_spacing / 2
    for line in lines:
        c.drawCentredString(0, y_offset, line)
        y_offset -= line_spacing

    c.restoreState()

    c.setFont(_FONT_NAME, 8)
    c.setFillColor(Color(0.5, 0.5, 0.5, alpha=0.30))
    c.drawString(10, 10, f"WM:{watermark_hash}")

    c.save()
    buf.seek(0)
    return buf


def watermark_pdf(
    source_bytes: bytes,
    *,
    user_name: str,
    user_id: int,
    manual_id: int,
) -> tuple[io.BytesIO, str]:
    """Apply a forensic watermark to every page of *source_bytes*.

    Returns:
        A tuple of (watermarked_pdf_buffer, watermark_hash_id).

    Raises:
        ``PDFProcessingError`` when the source is corrupt, encrypted,
        or a system-level dependency (fonts, freetype) is missing.
    """
    from app.core.errors import PDFProcessingError

    watermark_hash = generate_watermark_hash(user_id, manual_id)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    try:
        reader = PdfReader(io.BytesIO(source_bytes))
    except Exception as exc:
        raise PDFProcessingError(
            f"Cannot read PDF — file may be corrupt or encrypted: {exc}"
        ) from exc

    writer = PdfWriter()

    try:
        for page in reader.pages:
            box = page.mediabox
            page_width = float(box.width)
            page_height = float(box.height)

            if page_width == 0 or page_height == 0:
                page_width, page_height = letter

            overlay_buf = _build_watermark_page(
                page_width, page_height, user_name, timestamp, watermark_hash
            )
            overlay_reader = PdfReader(overlay_buf)
            overlay_page = overlay_reader.pages[0]

            page.merge_page(overlay_page)
            writer.add_page(page)

        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
    except PDFProcessingError:
        raise
    except Exception as exc:
        raise PDFProcessingError(
            f"Watermark generation failed — possible missing system fonts or "
            f"unsupported PDF feature: {exc}"
        ) from exc

    return output, watermark_hash
