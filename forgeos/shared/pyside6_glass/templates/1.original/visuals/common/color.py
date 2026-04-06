from __future__ import annotations

from .helpers import clean_text


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, float(value)))


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    text = clean_text(value).lstrip("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    if len(text) != 6:
        return (127, 127, 127)
    try:
        return (int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16))
    except Exception:
        return (127, 127, 127)


def mix_hex(a: str, b: str, ratio: float) -> str:
    ratio = clamp(ratio, 0.0, 1.0)
    ar, ag, ab = hex_to_rgb(a)
    br, bg, bb = hex_to_rgb(b)
    rr = int(round((ar * (1.0 - ratio)) + (br * ratio)))
    rg = int(round((ag * (1.0 - ratio)) + (bg * ratio)))
    rb = int(round((ab * (1.0 - ratio)) + (bb * ratio)))
    return f"#{rr:02x}{rg:02x}{rb:02x}"


def with_alpha(hex_color: str, opacity: float) -> str:
    opacity = clamp(opacity, 0.0, 1.0)
    r, g, b = hex_to_rgb(hex_color)
    return f"rgba({r}, {g}, {b}, {opacity:.3f})"

