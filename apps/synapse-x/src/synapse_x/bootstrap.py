from synapse_x.config import get_settings


def bootstrap() -> None:
    settings = get_settings()
    print(f"SYNAPSE-X bootstrap ready. DB={settings['db_path']}")
