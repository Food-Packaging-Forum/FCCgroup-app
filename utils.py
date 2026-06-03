import base64
from pathlib import Path


def _svg_as_data_uri(svg_path: Path) -> str:
    svg_bytes = svg_path.read_bytes()
    encoded = base64.b64encode(svg_bytes).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"