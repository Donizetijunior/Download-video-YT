import json
from datetime import datetime
from pathlib import Path

HISTORY_FILE = Path.home() / "Downloads" / "YouTube" / "historico.json"


def carregar() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def salvar(registros: list[dict]):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(registros, ensure_ascii=False, indent=2), encoding="utf-8")


def adicionar(titulo: str, modo: str, qualidade: str):
    registros = carregar()
    registros.insert(0, {
        "titulo": titulo,
        "tipo": "MP3" if modo == "audio" else f"MP4 ({qualidade})",
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
    })
    registros = registros[:50]
    salvar(registros)
