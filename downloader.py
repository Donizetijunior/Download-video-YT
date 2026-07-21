import os
import re
import shutil
from pathlib import Path
from typing import Callable, Optional

import yt_dlp


def _encontrar_ffmpeg() -> Optional[str]:
    if shutil.which("ffmpeg"):
        return None
    winget_pkgs = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages"
    if winget_pkgs.exists():
        for ffmpeg in winget_pkgs.rglob("ffmpeg.exe"):
            return str(ffmpeg.parent)
    return None


FFMPEG_DIR = _encontrar_ffmpeg()

PASTA_DOWNLOADS = Path.home() / "Downloads" / "YouTube"
COOKIES_FILE = Path(__file__).parent / "cookies.txt"

URL_PATTERN = re.compile(
    r"^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)[\w\-]+"
)


def validar_url(url: str) -> bool:
    return bool(URL_PATTERN.match(url.strip()))


def garantir_pasta_downloads():
    PASTA_DOWNLOADS.mkdir(parents=True, exist_ok=True)


def montar_opcoes(modo: str, qualidade: str, hook: Optional[Callable] = None,
                  cookies_path: Optional[Path] = None) -> dict:
    caminho_saida = str(PASTA_DOWNLOADS / "%(title)s.%(ext)s")

    opcoes = {
        "outtmpl": caminho_saida,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "js_runtimes": {"node": {}, "deno": {}},
    }

    if FFMPEG_DIR:
        opcoes["ffmpeg_location"] = FFMPEG_DIR

    if cookies_path and cookies_path.exists():
        opcoes["cookiefile"] = str(cookies_path)

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
            formato = "bestvideo+bestaudio/best"
        else:
            formato = (
                f"bestvideo[height<={qualidade}]+bestaudio"
                f"/bestvideo+bestaudio/best"
            )
        opcoes.update({
            "format": formato,
            "merge_output_format": "mp4",
        })

    return opcoes


def baixar(url: str, modo: str, qualidade: str, hook: Optional[Callable] = None,
           cookies_path: Optional[Path] = None) -> str:
    garantir_pasta_downloads()
    opcoes = montar_opcoes(modo, qualidade, hook, cookies_path)

    with yt_dlp.YoutubeDL(opcoes) as ydl:
        info = ydl.extract_info(url, download=True)
        return info.get("title", "Desconhecido")
