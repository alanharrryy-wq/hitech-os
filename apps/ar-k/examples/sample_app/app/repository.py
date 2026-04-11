import json


class Repository:
    def load(self) -> dict:
        return {"source": json.loads('{"kind": "repository"}')["kind"]}
