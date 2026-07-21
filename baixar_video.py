#!/usr/bin/env python3
"""
CLI para baixar vídeos do YouTube.
Uso:
    python baixar_video.py
    python baixar_video.py "https://www.youtube.com/watch?v=XXXXXXXXX"
"""

import sys

import downloader


def hook_progresso(d):
    if d["status"] == "downloading":
        percentual = d.get("_percent_str", "").strip()
        velocidade = d.get("_speed_str", "").strip()
        eta = d.get("_eta_str", "").strip()
        print(f"\rBaixando... {percentual}  |  Velocidade: {velocidade}  |  ETA: {eta}   ", end="")
    elif d["status"] == "finished":
        print("\nDownload concluído. Processando arquivo final...")


def perguntar_modo() -> str:
    print("\nO que deseja baixar?")
    print("  1) Vídeo (MP4)")
    print("  2) Apenas áudio (MP3)")
    escolha = input("Escolha [1/2]: ").strip()
    return "audio" if escolha == "2" else "video"


def perguntar_qualidade() -> str:
    print("\nQualidade do vídeo:")
    print("  1) Melhor disponível")
    print("  2) 1080p")
    print("  3) 720p")
    print("  4) 480p")
    escolha = input("Escolha [1-4] (padrão: melhor): ").strip()
    mapa = {"1": "melhor", "2": "1080", "3": "720", "4": "480"}
    return mapa.get(escolha, "melhor")


def main():
    print("=" * 50)
    print("   BAIXADOR DE VÍDEOS DO YOUTUBE (yt-dlp)")
    print("=" * 50)

    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("\nCole a URL do vídeo do YouTube: ").strip()

    if not url:
        print("Nenhuma URL informada. Encerrando.")
        return

    if not downloader.validar_url(url):
        print("URL inválida. Use um link do YouTube.")
        return

    modo = perguntar_modo()
    qualidade = "melhor"
    if modo == "video":
        qualidade = perguntar_qualidade()

    print(f"\nIniciando download em: {downloader.PASTA_DOWNLOADS}\n")

    try:
        titulo = downloader.baixar(url, modo, qualidade, hook_progresso)
        print(f"\n✅ Download finalizado: {titulo}")
    except Exception as e:
        print(f"\n❌ Erro: {e}")


if __name__ == "__main__":
    main()
