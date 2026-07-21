import re
from pathlib import Path
from typing import Callable, Optional

import yt_dlp

PASTA_DOWNLOADS = Path.home() / "Downloads" / "YouTube"

URL_PATTERN = re.compile(
    r"^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)[\w\-]+"
)


def validar_url(url: str) -> bool:
    return bool(URL_PATTERN.match(url.strip()))


def garantir_pasta_downloads():
    PASTA_DOWNLOADS.mkdir(parents=True, exist_ok=True)


def obter_info(url: str) -> dict:
    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
        return ydl.extract_info(url, download=False)


def montar_opcoes(modo: str, qualidade: str, hook: Optional[Callable] = None) -> dict:
    caminho_saida = str(PASTA_DOWNLOADS / "%(title)s.%(ext)s")

    opcoes = {
        "outtmpl": caminho_saida,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    if hook:
        opcoes["progress_hooks"] = [hook]

    if modo == "audio":
        opcoes.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        })
    else:
        if qualidade == "melhor":
            formato = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        else:
            formato = (
                f"bestvideo[height<={qualidade}][ext=mp4]+bestaudio[ext=m4a]"
                f"/best[height<={qualidade}]/best"
            )
        opcoes.update({
            "format": formato,
            "merge_output_format": "mp4",
        })

    return opcoes


def baixar(url: str, modo: str, qualidade: str, hook: Optional[Callable] = None) -> str:
    garantir_pasta_downloads()
    opcoes = montar_opcoes(modo, qualidade, hook)

    with yt_dlp.YoutubeDL(opcoes) as ydl:
        info = ydl.extract_info(url, download=True)
        return info.get("title", "Desconhecido")
