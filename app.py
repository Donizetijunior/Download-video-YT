import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

import downloader
import history


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Downloader")
        self.geometry("620x560")
        self.resizable(False, False)
        self.configure(bg="#1e1e2e")

        self.cookies_path = downloader.COOKIES_FILE if downloader.COOKIES_FILE.exists() else None

        self._style()
        self._build_input()
        self._build_action()
        self._build_history()
        self._atualizar_historico()

    def _style(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        bg = "#1e1e2e"
        fg = "#cdd6f4"
        accent = "#89b4fa"
        entry_bg = "#313244"
        btn_bg = "#45475a"

        self.style.configure(".", background=bg, foreground=fg, fieldbackground=entry_bg)
        self.style.configure("TLabel", background=bg, foreground=fg, font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"), foreground=accent)
        self.style.configure("TRadiobutton", background=bg, foreground=fg, font=("Segoe UI", 10))
        self.style.configure("TButton", background=btn_bg, foreground=fg,
                             font=("Segoe UI", 11, "bold"), padding=(16, 8))
        self.style.map("TButton", background=[("active", accent)])
        self.style.configure("Accent.TButton", background=accent, foreground="#1e1e2e")
        self.style.map("Accent.TButton", background=[("active", "#74c7ec")])
        self.style.configure("Small.TButton", font=("Segoe UI", 9), padding=(8, 4))
        self.style.configure("TCombobox", fieldbackground=entry_bg, foreground=fg)
        self.style.configure("Status.TLabel", font=("Segoe UI", 9), foreground="#a6adc8")
        self.style.configure("Cookie.TLabel", font=("Segoe UI", 8), foreground="#a6e3a1")
        self.style.configure("NoCookie.TLabel", font=("Segoe UI", 8), foreground="#f9e2af")
        self.style.configure("Treeview", background=entry_bg, foreground=fg,
                             fieldbackground=entry_bg, font=("Segoe UI", 9), rowheight=24)
        self.style.configure("Treeview.Heading", background=btn_bg, foreground=fg,
                             font=("Segoe UI", 9, "bold"))
        self.style.map("Treeview", background=[("selected", accent)],
                       foreground=[("selected", "#1e1e2e")])

    def _build_input(self):
        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="x")

        ttk.Label(frame, text="YouTube Downloader", style="Title.TLabel").pack(anchor="w")

        ttk.Label(frame, text="URL do vídeo:").pack(anchor="w", pady=(12, 4))
        self.url_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.url_var, font=("Segoe UI", 10)).pack(fill="x")

        options_frame = ttk.Frame(frame)
        options_frame.pack(fill="x", pady=(12, 0))

        left = ttk.Frame(options_frame)
        left.pack(side="left")
        ttk.Label(left, text="Formato:").pack(anchor="w")
        self.modo_var = tk.StringVar(value="video")
        ttk.Radiobutton(left, text="Vídeo (MP4)", variable=self.modo_var,
                        value="video", command=self._toggle_quality).pack(anchor="w")
        ttk.Radiobutton(left, text="Áudio (MP3)", variable=self.modo_var,
                        value="audio", command=self._toggle_quality).pack(anchor="w")

        right = ttk.Frame(options_frame)
        right.pack(side="left", padx=(40, 0))
        ttk.Label(right, text="Qualidade:").pack(anchor="w")
        self.qualidade_var = tk.StringVar(value="Melhor disponível")
        self.quality_combo = ttk.Combobox(right, textvariable=self.qualidade_var,
                                          values=["Melhor disponível", "1080p", "720p", "480p"],
                                          state="readonly", width=18)
        self.quality_combo.pack(anchor="w", pady=(4, 0))

        cookie_frame = ttk.Frame(frame)
        cookie_frame.pack(fill="x", pady=(10, 0))
        ttk.Button(cookie_frame, text="Importar cookies.txt", style="Small.TButton",
                   command=self._importar_cookies).pack(side="left")
        self.cookie_status_var = tk.StringVar()
        self.cookie_label = ttk.Label(cookie_frame, textvariable=self.cookie_status_var)
        self.cookie_label.pack(side="left", padx=(8, 0))
        self._atualizar_cookie_status()

    def _build_action(self):
        frame = ttk.Frame(self, padding=(16, 0, 16, 0))
        frame.pack(fill="x")

        self.btn_baixar = ttk.Button(frame, text="Baixar", style="Accent.TButton",
                                     command=self._iniciar_download)
        self.btn_baixar.pack(fill="x", pady=(8, 8))

        self.progress = ttk.Progressbar(frame, mode="determinate", length=100)
        self.progress.pack(fill="x")

        self.status_var = tk.StringVar(value="Pronto.")
        ttk.Label(frame, textvariable=self.status_var, style="Status.TLabel").pack(
            anchor="w", pady=(4, 0))

    def _build_history(self):
        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Histórico de downloads").pack(anchor="w", pady=(0, 4))

        cols = ("titulo", "tipo", "data")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=6)
        self.tree.heading("titulo", text="Título")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("data", text="Data")
        self.tree.column("titulo", width=320)
        self.tree.column("tipo", width=100)
        self.tree.column("data", width=140)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _toggle_quality(self):
        if self.modo_var.get() == "audio":
            self.quality_combo.configure(state="disabled")
        else:
            self.quality_combo.configure(state="readonly")

    def _atualizar_cookie_status(self):
        if self.cookies_path and self.cookies_path.exists():
            self.cookie_status_var.set(f"Cookies carregados: {self.cookies_path.name}")
            self.cookie_label.configure(style="Cookie.TLabel")
        else:
            self.cookie_status_var.set("Sem cookies (alguns vídeos podem falhar)")
            self.cookie_label.configure(style="NoCookie.TLabel")

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
            messagebox.showinfo("Cookies", "Cookies importados com sucesso!")

    def _atualizar_historico(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for reg in history.carregar():
            self.tree.insert("", "end", values=(reg["titulo"], reg["tipo"], reg["data"]))

    def _iniciar_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "Cole uma URL do YouTube.")
            return
        if not downloader.validar_url(url):
            messagebox.showerror("Erro", "URL inválida. Use um link do YouTube.")
            return

        self.btn_baixar.configure(state="disabled")
        self.progress["value"] = 0
        self.status_var.set("Iniciando download...")

        modo = self.modo_var.get()
        mapa_qualidade = {
            "Melhor disponível": "melhor", "1080p": "1080", "720p": "720", "480p": "480"
        }
        qualidade = mapa_qualidade.get(self.qualidade_var.get(), "melhor")

        thread = threading.Thread(target=self._executar_download,
                                  args=(url, modo, qualidade), daemon=True)
        thread.start()

    def _hook_progresso(self, d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            baixado = d.get("downloaded_bytes", 0)
            if total > 0:
                pct = baixado / total * 100
                self.after(0, self._update_progress, pct, d)
        elif d["status"] == "finished":
            self.after(0, self._update_progress, 100, d)

    def _update_progress(self, pct, d):
        self.progress["value"] = pct
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
        self.progress["value"] = 100
        self.status_var.set(f"Concluído: {titulo}")
        self.btn_baixar.configure(state="normal")
        self.url_var.set("")
        self._atualizar_historico()

    def _download_erro(self, erro):
        self.progress["value"] = 0
        self.status_var.set("Erro no download.")
        self.btn_baixar.configure(state="normal")
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
