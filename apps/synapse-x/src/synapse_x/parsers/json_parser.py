import json
from typing import Any


def parse_json_text(text: str) -> Any:
    return json.loads(text)
