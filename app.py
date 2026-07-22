import ctypes
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

import downloader
import history

if sys.platform == "win32":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ytdownloader.app")


COLORS = {
    "bg": "#0f0f17",
    "card": "#1a1a28",
    "border": "#2a2a3d",
    "text": "#f1f1f4",
    "muted": "#5a5a72",
    "accent": "#7c3aed",
    "accent_hover": "#6d28d9",
    "success": "#22c55e",
    "warn": "#f9e2af",
    "pink": "#ec4899",
}


class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, color, text_color="#ffffff", icon="",
                 command=None, height=42, radius=10, font_size=12, **kwargs):
        super().__init__(parent, height=height, bg=COLORS["bg"],
                         highlightthickness=0, **kwargs)
        self.command = command
        self.color = color
        self.text_color = text_color
        self.radius = radius
        self.h = height
        self.display_text = f"{icon}  {text}" if icon else text
        self.font_size = font_size
        self._enabled = True

        self.bind("<Configure>", self._draw)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        self.create_arc(x1, y1, x1 + 2*r, y1 + 2*r, start=90, extent=90, **kwargs)
        self.create_arc(x2 - 2*r, y1, x2, y1 + 2*r, start=0, extent=90, **kwargs)
        self.create_arc(x2 - 2*r, y2 - 2*r, x2, y2, start=270, extent=90, **kwargs)
        self.create_arc(x1, y2 - 2*r, x1 + 2*r, y2, start=180, extent=90, **kwargs)
        self.create_rectangle(x1 + r, y1, x2 - r, y2, **kwargs)
        self.create_rectangle(x1, y1 + r, x2, y2 - r, **kwargs)

    def _draw(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        self._rounded_rect(0, 0, w, self.h, self.radius,
                           fill=self.color, outline=self.color)
        self.create_text(w // 2, self.h // 2, text=self.display_text,
                         fill=self.text_color, font=("Segoe UI", self.font_size, "bold"))

    def _on_click(self, event):
        if self._enabled and self.command:
            self.command()

    def _on_enter(self, event):
        if self._enabled:
            self.configure(cursor="hand2")

    def _on_leave(self, event):
        self.configure(cursor="")

    def set_enabled(self, enabled):
        self._enabled = enabled
        self.configure(cursor="" if not enabled else "hand2")


class FormatCard(tk.Frame):
    def __init__(self, parent, icon, label, value, var, on_select, **kwargs):
        super().__init__(parent, bg=COLORS["card"], cursor="hand2", **kwargs)
        self.value = value
        self.var = var
        self.on_select = on_select
        self.icon_text = icon
        self.label_text = label

        self.configure(highlightbackground=COLORS["border"], highlightthickness=2,
                       padx=12, pady=10)

        self.icon_label = tk.Label(self, text=icon, font=("Segoe UI", 20),
                                   bg=COLORS["card"], fg=COLORS["muted"])
        self.icon_label.pack()

        self.text_label = tk.Label(self, text=label, font=("Segoe UI", 11, "bold"),
                                   bg=COLORS["card"], fg=COLORS["muted"])
        self.text_label.pack(pady=(4, 0))

        for widget in [self, self.icon_label, self.text_label]:
            widget.bind("<Button-1>", self._click)

        self.var.trace_add("write", lambda *_: self._update_style())
        self._update_style()

    def _click(self, event):
        self.var.set(self.value)
        self.on_select()

    def _update_style(self):
        active = self.var.get() == self.value
        border = COLORS["accent"] if active else COLORS["border"]
        fg = COLORS["accent"] if active else COLORS["muted"]
        text_fg = COLORS["text"] if active else COLORS["muted"]
        self.configure(highlightbackground=border)
        self.icon_label.configure(fg=fg)
        self.text_label.configure(fg=text_fg)


class QualityPill(tk.Label):
    def __init__(self, parent, text, value, var, **kwargs):
        super().__init__(parent, text=text, font=("Segoe UI", 10, "bold"),
                         cursor="hand2", padx=14, pady=4, **kwargs)
        self.value = value
        self.var = var
        self.bind("<Button-1>", lambda e: self.var.set(self.value))
        self.var.trace_add("write", lambda *_: self._update_style())
        self._update_style()

    def _update_style(self):
        if self.var.get() == self.value:
            self.configure(bg=COLORS["accent"], fg="#ffffff",
                           highlightbackground=COLORS["accent"])
        else:
            self.configure(bg=COLORS["card"], fg=COLORS["muted"],
                           highlightbackground=COLORS["border"])


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Downloader")
        self.geometry("500x600")
        self.resizable(False, False)
        self.configure(bg=COLORS["bg"])

        icon_path = Path(__file__).parent / "icon.ico"
        if icon_path.exists():
            self.iconbitmap(str(icon_path))

        self.cookies_path = downloader.COOKIES_FILE if downloader.COOKIES_FILE.exists() else None

        self._build_header()
        self._build_url_input()
        self._build_format_selector()
        self._build_quality_selector()
        self._build_cookies_status()
        self._build_download_button()
        self._build_progress()
        self._build_history()
        self._atualizar_historico()

    def _build_header(self):
        frame = tk.Frame(self, bg=COLORS["bg"], padx=24)
        frame.pack(fill="x", pady=(20, 0))

        left = tk.Frame(frame, bg=COLORS["bg"])
        left.pack(side="left")

        icon_frame = tk.Frame(left, bg="#dc2626", width=40, height=40)
        icon_frame.pack(side="left", padx=(0, 12))
        icon_frame.pack_propagate(False)
        tk.Label(icon_frame, text="↓", font=("Segoe UI", 16), bg="#dc2626",
                 fg="white").place(relx=0.5, rely=0.5, anchor="center")

        text_frame = tk.Frame(left, bg=COLORS["bg"])
        text_frame.pack(side="left")
        tk.Label(text_frame, text="YouTube Downloader", font=("Segoe UI", 16, "bold"),
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w")
        tk.Label(text_frame, text="Cole o link e baixe", font=("Segoe UI", 9),
                 bg=COLORS["bg"], fg=COLORS["muted"]).pack(anchor="w")

    def _build_url_input(self):
        frame = tk.Frame(self, bg=COLORS["bg"], padx=24)
        frame.pack(fill="x", pady=(16, 0))

        input_frame = tk.Frame(frame, bg=COLORS["card"], highlightbackground=COLORS["border"],
                               highlightthickness=1, padx=12, pady=8)
        input_frame.pack(fill="x")

        tk.Label(input_frame, text="⛓", font=("Segoe UI Symbol", 12),
                 bg=COLORS["card"], fg=COLORS["muted"]).pack(side="left", padx=(0, 8))

        self.url_var = tk.StringVar()
        entry = tk.Entry(input_frame, textvariable=self.url_var, font=("Segoe UI", 11),
                         bg=COLORS["card"], fg=COLORS["text"], insertbackground=COLORS["text"],
                         relief="flat", border=0)
        entry.pack(side="left", fill="x", expand=True)
        entry.configure(highlightthickness=0)

    def _build_format_selector(self):
        frame = tk.Frame(self, bg=COLORS["bg"], padx=24)
        frame.pack(fill="x", pady=(16, 0))

        self.modo_var = tk.StringVar(value="video")

        cards_frame = tk.Frame(frame, bg=COLORS["bg"])
        cards_frame.pack(fill="x")
        cards_frame.columnconfigure(0, weight=1)
        cards_frame.columnconfigure(1, weight=1)

        FormatCard(cards_frame, "▶", "Video MP4", "video",
                   self.modo_var, self._toggle_quality).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        FormatCard(cards_frame, "♪", "Audio MP3", "audio",
                   self.modo_var, self._toggle_quality).grid(row=0, column=1, sticky="ew", padx=(4, 0))

    def _build_quality_selector(self):
        self.quality_frame = tk.Frame(self, bg=COLORS["bg"], padx=24)
        self.quality_frame.pack(fill="x", pady=(12, 0))

        self.qualidade_var = tk.StringVar(value="melhor")
        pills_frame = tk.Frame(self.quality_frame, bg=COLORS["bg"])
        pills_frame.pack(fill="x")

        for text, value in [("Melhor", "melhor"), ("1080p", "1080"), ("720p", "720"), ("480p", "480")]:
            QualityPill(pills_frame, text, value, self.qualidade_var).pack(side="left", padx=(0, 6))

    def _build_cookies_status(self):
        frame = tk.Frame(self, bg=COLORS["bg"], padx=24)
        frame.pack(fill="x", pady=(12, 0))

        self.cookie_icon = tk.Label(frame, text="●", font=("Segoe UI", 10),
                                    bg=COLORS["bg"])
        self.cookie_icon.pack(side="left")

        self.cookie_status_var = tk.StringVar()
        self.cookie_label = tk.Label(frame, textvariable=self.cookie_status_var,
                                     font=("Segoe UI", 9), bg=COLORS["bg"])
        self.cookie_label.pack(side="left", padx=(4, 0))

        import_link = tk.Label(frame, text="Importar", font=("Segoe UI", 9, "underline"),
                               bg=COLORS["bg"], fg=COLORS["muted"], cursor="hand2")
        import_link.pack(side="right")
        import_link.bind("<Button-1>", lambda e: self._importar_cookies())

        self._atualizar_cookie_status()

    def _build_download_button(self):
        frame = tk.Frame(self, bg=COLORS["bg"], padx=24)
        frame.pack(fill="x", pady=(16, 0))

        self.btn_baixar = RoundedButton(frame, text="Baixar", color=COLORS["accent"],
                                        icon="↓", command=self._iniciar_download)
        self.btn_baixar.pack(fill="x")

    def _build_progress(self):
        frame = tk.Frame(self, bg=COLORS["bg"], padx=24)
        frame.pack(fill="x", pady=(8, 0))

        self.progress_canvas = tk.Canvas(frame, height=4, bg=COLORS["card"],
                                          highlightthickness=0)
        self.progress_canvas.pack(fill="x")
        self.progress_value = 0

        self.status_var = tk.StringVar(value="Pronto.")
        tk.Label(frame, textvariable=self.status_var, font=("Segoe UI", 9),
                 bg=COLORS["bg"], fg=COLORS["muted"]).pack(anchor="w", pady=(4, 0))

    def _build_history(self):
        frame = tk.Frame(self, bg=COLORS["bg"], padx=24)
        frame.pack(fill="both", expand=True, pady=(12, 0))

        header = tk.Frame(frame, bg=COLORS["bg"])
        header.pack(fill="x", pady=(0, 6))
        tk.Label(header, text="Recentes", font=("Segoe UI", 10, "bold"),
                 bg=COLORS["bg"], fg=COLORS["muted"]).pack(side="left")
        tk.Label(header, text="◷", font=("Segoe UI Symbol", 10),
                 bg=COLORS["bg"], fg=COLORS["muted"]).pack(side="right")

        self.history_frame = tk.Frame(frame, bg=COLORS["card"],
                                      highlightbackground=COLORS["border"],
                                      highlightthickness=1)
        self.history_frame.pack(fill="both", expand=True, pady=(0, 16))

    def _toggle_quality(self):
        if self.modo_var.get() == "audio":
            for widget in self.quality_frame.winfo_children():
                for pill in widget.winfo_children():
                    pill.configure(state="disabled", cursor="")
        else:
            for widget in self.quality_frame.winfo_children():
                for pill in widget.winfo_children():
                    pill.configure(state="normal", cursor="hand2")

    def _atualizar_cookie_status(self):
        if self.cookies_path and self.cookies_path.exists():
            self.cookie_status_var.set("Cookies carregados")
            self.cookie_label.configure(fg=COLORS["success"])
        else:
            self.cookie_status_var.set("Sem cookies (alguns vídeos podem falhar)")
            self.cookie_label.configure(fg=COLORS["warn"])

    def _importar_cookies(self):
        path = filedialog.askopenfilename(
            title="Selecionar cookies.txt",
            filetypes=[("Cookies", "*.txt"), ("Todos", "*.*")],
        )
        if path:
            dest = downloader.COOKIES_FILE
            dest.write_bytes(Path(path).read_bytes())
            self.cookies_path = dest
            self._atualizar_cookie_status()

    def _atualizar_historico(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        registros = history.carregar()
        if not registros:
            tk.Label(self.history_frame, text="Nenhum download ainda",
                     font=("Segoe UI", 10), bg=COLORS["card"],
                     fg=COLORS["muted"], pady=20).pack()
            return

        for i, reg in enumerate(registros[:8]):
            is_audio = "MP3" in reg.get("tipo", "")
            icon = "♪" if is_audio else "▶"
            icon_color = COLORS["pink"] if is_audio else COLORS["accent"]

            row = tk.Frame(self.history_frame, bg=COLORS["card"], padx=12, pady=6)
            row.pack(fill="x")

            if i < len(registros[:8]) - 1:
                sep = tk.Frame(self.history_frame, bg=COLORS["border"], height=1)
                sep.pack(fill="x")

            tk.Label(row, text=icon, font=("Segoe UI", 11), bg=COLORS["card"],
                     fg=icon_color).pack(side="left", padx=(0, 8))

            info = tk.Frame(row, bg=COLORS["card"])
            info.pack(side="left", fill="x", expand=True)

            titulo = reg.get("titulo", "")
            if len(titulo) > 42:
                titulo = titulo[:42] + "..."
            tk.Label(info, text=titulo, font=("Segoe UI", 10),
                     bg=COLORS["card"], fg=COLORS["text"], anchor="w").pack(fill="x")

            meta = f"{reg.get('tipo', '')} · {reg.get('data', '')}"
            tk.Label(info, text=meta, font=("Segoe UI", 8),
                     bg=COLORS["card"], fg=COLORS["muted"], anchor="w").pack(fill="x")

    def _update_progress_bar(self, pct):
        self.progress_canvas.delete("bar")
        if pct > 0:
            w = self.progress_canvas.winfo_width()
            fill_w = int(w * pct / 100)
            self.progress_canvas.create_rectangle(0, 0, fill_w, 4,
                                                   fill=COLORS["accent"], outline="", tags="bar")

    def _iniciar_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "Cole uma URL do YouTube.")
            return
        if not downloader.validar_url(url):
            messagebox.showerror("Erro", "URL inválida. Use um link do YouTube.")
            return

        self.btn_baixar.set_enabled(False)
        self._update_progress_bar(0)
        self.status_var.set("Iniciando download...")

        modo = self.modo_var.get()
        qualidade = self.qualidade_var.get()

        thread = threading.Thread(target=self._executar_download,
                                  args=(url, modo, qualidade), daemon=True)
        thread.start()

    def _hook_progresso(self, d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            baixado = d.get("downloaded_bytes", 0)
            if total > 0:
                pct = baixado / total * 100
                self.after(0, self._on_progress, pct, d)
        elif d["status"] == "finished":
            self.after(0, self._on_progress, 100, d)

    def _on_progress(self, pct, d):
        self._update_progress_bar(pct)
        if d["status"] == "finished":
            self.status_var.set("Processando arquivo final...")
        else:
            vel = d.get("_speed_str", "").strip()
            eta = d.get("_eta_str", "").strip()
            self.status_var.set(f"{pct:.0f}%  |  {vel}  |  ETA: {eta}")

    def _executar_download(self, url, modo, qualidade):
        try:
            titulo = downloader.baixar(url, modo, qualidade, self._hook_progresso,
                                       self.cookies_path)
            history.adicionar(titulo, modo, qualidade)
            self.after(0, self._download_concluido, titulo)
        except Exception as e:
            self.after(0, self._download_erro, str(e))

    def _download_concluido(self, titulo):
        self._update_progress_bar(100)
        self.status_var.set(f"Concluído: {titulo}")
        self.btn_baixar.set_enabled(True)
        self.url_var.set("")
        self._atualizar_historico()

    def _download_erro(self, erro):
        self._update_progress_bar(0)
        self.status_var.set("Erro no download.")
        self.btn_baixar.set_enabled(True)
        if "Sign in" in erro or "bot" in erro:
            messagebox.showerror("Erro", (
                "O YouTube bloqueou o download.\n\n"
                "Solução: exporte seus cookies do Chrome usando a extensão\n"
                "\"Get cookies.txt LOCALLY\" e importe pelo botão na interface."
            ))
        else:
            messagebox.showerror("Erro", f"Falha ao baixar:\n{erro}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
