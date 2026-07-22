# Download Video YT

Aplicação em Python para baixar vídeos ou áudio do YT usando `yt-dlp`. Disponível com interface gráfica (GUI) e linha de comando (CLI).

## Requisitos

1. **Python 3.10+**
2. **ffmpeg** instalado no sistema:
   - **Windows:** `winget install ffmpeg` (reinicie o terminal depois)
   - **macOS:** `brew install ffmpeg`
   - **Linux:** `sudo apt install ffmpeg`
   - Confirme com `ffmpeg -version`

## Instalação Rápida (Windows)

1. Baixe ou clone o repositório
2. Dê duplo clique em **`instalar.bat`** — ele configura tudo automaticamente
3. Dê duplo clique em **`iniciar.bat`** para abrir o app

Pronto! Não precisa mexer em terminal.

> Requisitos: [Python 3.10+](https://www.python.org/downloads/) (marque **"Add Python to PATH"** na instalação)

## Instalação Manual

```bash
git clone https://github.com/Donizetijunior/Download-video-YT.git
cd Download-video-YT
python -m venv venv
```

Ative a venv:

- **Windows PowerShell:** `venv\Scripts\Activate.ps1`
- **Windows cmd:** `venv\Scripts\activate.bat`
- **Linux/macOS:** `source venv/bin/activate`

Instale as dependências:

```bash
pip install -r requirements.txt
```

## Uso

### Interface Gráfica (recomendado)

Duplo clique em `iniciar.bat` ou:

```bash
python app.py
```

- Cole a URL do vídeo
- Escolha entre Vídeo (MP4) ou Áudio (MP3)
- Selecione a qualidade desejada
- Clique em **Baixar**
- Acompanhe o progresso e veja o histórico de downloads

### Linha de Comando

```bash
python baixar_video.py
```

Ou passe a URL direto:

```bash
python baixar_video.py "https://www.youtube.com/watch?v=XXXXXXXXX"
```

## Configurando Cookies (bloqueio do YT)

Depois de alguns downloads seguidos, o YT pode bloquear com a mensagem **"Sign in to confirm you're not a bot"**. Isso é normal — ele detecta muitas requisições e pede autenticação.

A solução é exportar os cookies da sua conta do YT e importar no app. Fazendo isso, o YT entende que é você e libera os downloads.

### Passo a passo

1. **Instale a extensão no Chrome:** procure por **"Get cookies.txt LOCALLY"** na [Chrome Web Store](https://chromewebstore.google.com/) e instale

2. **Exporte os cookies:**
   - Abra o YT no Chrome e faça login na sua conta Google (se ainda não estiver)
   - Clique no ícone da extensão **"Get cookies.txt LOCALLY"**
   - Clique em **"Export"** — vai baixar um arquivo `cookies.txt`

3. **Importe no app:**
   - Abra o YT Downloader
   - Clique no botão **"Importar cookies.txt"**
   - Selecione o arquivo `cookies.txt` que você exportou
   - O status vai mudar para **"Cookies carregados"** (em verde)

Pronto! Agora os downloads vão funcionar normalmente.

> **Dica:** se depois de um tempo o erro voltar, é só repetir o processo — os cookies expiram.
>
> **Importante:** o arquivo `cookies.txt` contém dados da sua conta. Não compartilhe ele com ninguém.

## Estrutura

| Arquivo | Descrição |
|---|---|
| `app.py` | Interface gráfica (Tkinter) |
| `baixar_video.py` | Interface de linha de comando |
| `downloader.py` | Lógica de download (compartilhada) |
| `history.py` | Gerenciamento do histórico |

Os arquivos são salvos em `~/Downloads/YT/`.

## Observações

- Baixe apenas conteúdo que você tem direito de baixar.
- O script ignora playlists por padrão.
