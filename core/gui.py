
import os
import sys
import threading
import queue
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path


APP_NAME = "Magic Print Manager"
APP_VERSION = "1.0.2"

ROOT = Path(__file__).resolve().parent.parent
JOBS = ROOT / "jobs"
OUTPUT = ROOT / "output"

COLORS = {
    "background": "#101D32",
    "panel": "#1C2E48",
    "panel_light": "#263B59",
    "blue": "#1677E8",
    "blue_hover": "#2589F5",
    "text": "#FFFFFF",
    "muted": "#91A9C8",
    "success": "#4ADE80",
    "error": "#F87171",
    "border": "#344762",
}


class MagicPrintManager:

    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("560x570")
        self.root.minsize(520, 540)
        self.root.configure(bg=COLORS["background"])

        self.csv_path = None
        self.result_queue = queue.Queue()

        self.configure_styles()
        self.build_interface()
        self.check_queue()

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "App.TFrame",
            background=COLORS["background"]
        )

        style.configure(
            "Title.TLabel",
            background=COLORS["background"],
            foreground=COLORS["text"],
            font=("Segoe UI", 16, "bold")
        )

        style.configure(
            "Subtitle.TLabel",
            background=COLORS["background"],
            foreground=COLORS["muted"],
            font=("Segoe UI", 7)
        )

        style.configure(
            "Field.TLabel",
            background=COLORS["panel"],
            foreground=COLORS["muted"],
            font=("Segoe UI", 7, "bold")
        )

        style.configure(
            "Status.TLabel",
            background=COLORS["background"],
            foreground=COLORS["muted"],
            font=("Segoe UI", 8)
        )

        style.configure(
            "TEntry",
            fieldbackground=COLORS["panel_light"],
            foreground=COLORS["text"],
            insertcolor=COLORS["text"],
            bordercolor=COLORS["border"],
            padding=4
        )

        style.configure(
            "Action.TButton",
            background=COLORS["blue"],
            foreground=COLORS["text"],
            font=("Segoe UI", 8, "bold"),
            padding=6,
            borderwidth=0
        )

        style.map(
            "Action.TButton",
            background=[
                ("disabled", COLORS["panel_light"]),
                ("active", COLORS["blue_hover"])
            ],
            foreground=[
                ("disabled", COLORS["muted"])
            ]
        )

        style.configure(
            "Secondary.TButton",
            background=COLORS["panel_light"],
            foreground=COLORS["text"],
            font=("Segoe UI", 7, "bold"),
            padding=4,
            borderwidth=0
        )

        style.map(
            "Secondary.TButton",
            background=[("active", COLORS["blue"])]
        )

    def build_interface(self):
        main = ttk.Frame(
            self.root,
            style="App.TFrame",
            padding=11
        )
        main.pack(fill="both", expand=True)

        # Cabeçalho
        header = ttk.Frame(main, style="App.TFrame")
        header.pack(fill="x", pady=(0, 8))

        logo = tk.Label(
            header,
            text="M",
            bg=COLORS["blue"],
            fg=COLORS["text"],
            font=("Segoe UI", 16, "bold"),
            width=2,
            height=1
        )
        logo.pack(side="left", padx=(0, 9))

        title_frame = ttk.Frame(
            header,
            style="App.TFrame"
        )
        title_frame.pack(side="left", fill="y")

        ttk.Label(
            title_frame,
            text="MAGIC PRINT MANAGER",
            style="Title.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            title_frame,
            text=f"MTG PROXY PRINTING  |  A4  |  v{APP_VERSION}",
            style="Subtitle.TLabel"
        ).pack(anchor="w")

        # Configuração
        setup = self.create_panel(
            main,
            "01  |  CONFIGURAÇÃO DA COLEÇÃO"
        )

        ttk.Label(
            setup,
            text="ARQUIVO CSV",
            style="Field.TLabel"
        ).pack(anchor="w", pady=(6, 3))

        file_frame = tk.Frame(
            setup,
            bg=COLORS["panel"]
        )
        file_frame.pack(fill="x")

        self.file_label = tk.Label(
            file_frame,
            text="Nenhum arquivo selecionado",
            bg=COLORS["panel_light"],
            fg=COLORS["muted"],
            font=("Segoe UI", 8),
            anchor="w",
            padx=7,
            pady=5
        )
        self.file_label.pack(
            side="left",
            fill="x",
            expand=True
        )

        ttk.Button(
            file_frame,
            text="PROCURAR",
            style="Secondary.TButton",
            command=self.select_csv
        ).pack(side="right", padx=(7, 0))

        ttk.Label(
            setup,
            text="NOME DA COLEÇÃO",
            style="Field.TLabel"
        ).pack(anchor="w", pady=(7, 3))

        self.collection_entry = ttk.Entry(setup)
        self.collection_entry.pack(fill="x")

        self.generate_button = ttk.Button(
            setup,
            text="GERAR PDF DUPLEX",
            style="Action.TButton",
            command=self.generate
        )
        self.generate_button.pack(
            fill="x",
            pady=(8, 1)
        )

        # Resultado
        results = self.create_panel(
            main,
            "02  |  RESULTADO DO PROCESSAMENTO"
        )

        stats = tk.Frame(
            results,
            bg=COLORS["panel"]
        )
        stats.pack(fill="x", pady=(7, 5))

        self.cards_value = self.create_stat(
            stats, "—", "CARTAS"
        )
        self.sheets_value = self.create_stat(
            stats, "—", "FOLHAS A4"
        )
        self.pages_value = self.create_stat(
            stats, "—", "PÁGINAS DUPLEX"
        )

        self.result_label = tk.Label(
            results,
            text="Aguardando processamento...",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Segoe UI", 8),
            anchor="w"
        )
        self.result_label.pack(fill="x", pady=(0, 1))

        # PDF final
        files = self.create_panel(
            main,
            "03  |  PDF FINAL GERADO"
        )

        self.duplex_label = self.create_file_row(
            files, "PDF DUPLEX"
        )

        buttons_frame = tk.Frame(
            files,
            bg=COLORS["panel"]
        )
        buttons_frame.pack(
            fill="x",
            pady=(7, 0)
        )

        self.copy_log_button = ttk.Button(
            buttons_frame,
            text="COPIAR LOG",
            style="Secondary.TButton",
            command=self.copy_log
        )
        self.copy_log_button.pack(side="left")

        self.open_folder_button = ttk.Button(
            buttons_frame,
            text="ABRIR PASTA DE SAÍDA",
            style="Secondary.TButton",
            command=self.open_output_folder,
            state="disabled"
        )
        self.open_folder_button.pack(side="right")

        # Log
        log_panel = self.create_panel(
            main,
            "04  |  LOG DE PROCESSAMENTO"
        )

        self.log = tk.Text(
            log_panel,
            height=4,
            bg="#0B1627",
            fg="#A9C5E8",
            insertbackground=COLORS["text"],
            font=("Consolas", 8),
            relief="flat",
            borderwidth=0,
            padx=7,
            pady=5,
            state="disabled",
            wrap="word"
        )
        self.log.pack(
            fill="both",
            expand=True,
            pady=(6, 0)
        )

        # Rodapé
        self.status = ttk.Label(
            main,
            text="●  AGUARDANDO SELEÇÃO DE ARQUIVO",
            style="Status.TLabel"
        )
        self.status.pack(anchor="w", pady=(4, 0))

    def create_panel(self, parent, title):
        frame = tk.Frame(
            parent,
            bg=COLORS["panel"],
            padx=10,
            pady=7,
            highlightthickness=1,
            highlightbackground=COLORS["border"]
        )
        frame.pack(fill="x", pady=(0, 6))

        tk.Label(
            frame,
            text=title,
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 8, "bold"),
            anchor="w"
        ).pack(fill="x")

        return frame

    def create_stat(self, parent, value, label):
        frame = tk.Frame(
            parent,
            bg=COLORS["panel_light"],
            padx=7,
            pady=5
        )
        frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 5)
        )

        value_label = tk.Label(
            frame,
            text=value,
            bg=COLORS["panel_light"],
            fg="#60A5FA",
            font=("Segoe UI", 16, "bold")
        )
        value_label.pack(anchor="w")

        tk.Label(
            frame,
            text=label,
            bg=COLORS["panel_light"],
            fg=COLORS["muted"],
            font=("Segoe UI", 7, "bold")
        ).pack(anchor="w")

        return value_label

    def create_file_row(self, parent, label):
        row = tk.Frame(
            parent,
            bg=COLORS["panel"]
        )
        row.pack(fill="x", pady=(6, 0))

        tk.Label(
            row,
            text="PDF",
            bg=COLORS["panel_light"],
            fg="#60A5FA",
            font=("Segoe UI", 7, "bold"),
            padx=5,
            pady=3
        ).pack(side="left")

        value = tk.Label(
            row,
            text=f"{label}: —",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Segoe UI", 8),
            anchor="w"
        )
        value.pack(side="left", padx=7)

        return value

    def write_log(self, message):
        self.log.config(state="normal")
        self.log.insert("end", message + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def copy_log(self):
        content = self.log.get("1.0", "end-1c")

        if not content.strip():
            messagebox.showinfo(
                "Log vazio",
                "Ainda não existem informações para copiar."
            )
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.root.update()

        self.status.config(
            text="●  LOG COPIADO PARA A ÁREA DE TRANSFERÊNCIA",
            foreground=COLORS["success"]
        )

    def select_csv(self):
        filename = filedialog.askopenfilename(
            title="Selecionar arquivo CSV",
            initialdir=JOBS,
            filetypes=[("Arquivos CSV", "*.csv")]
        )

        if not filename:
            return

        self.csv_path = Path(filename)

        self.file_label.config(
            text=self.csv_path.name,
            fg=COLORS["text"]
        )

        self.collection_entry.delete(0, "end")
        self.collection_entry.insert(
            0, self.csv_path.stem
        )

        self.write_log(
            f"Arquivo selecionado: {self.csv_path.name}"
        )

        self.status.config(
            text="●  ARQUIVO SELECIONADO"
        )

    def generate(self):
        if self.csv_path is None:
            messagebox.showwarning(
                "Atenção",
                "Selecione um arquivo CSV primeiro."
            )
            return

        collection_name = self.collection_entry.get().strip()

        if not collection_name:
            messagebox.showwarning(
                "Atenção",
                "Informe o nome da coleção."
            )
            return

        self.generate_button.config(state="disabled")
        self.open_folder_button.config(state="disabled")

        self.result_label.config(
            text="Processando coleção...",
            fg=COLORS["muted"]
        )

        self.cards_value.config(text="—")
        self.sheets_value.config(text="—")
        self.pages_value.config(text="—")

        self.duplex_label.config(text="PDF DUPLEX: —")

        self.status.config(
            text="●  PROCESSANDO...",
            foreground="#60A5FA"
        )

        self.write_log("Iniciando geração...")

        thread = threading.Thread(
            target=self.process_job,
            args=(self.csv_path.name, collection_name),
            daemon=True
        )
        thread.start()

    def process_job(self, csv_filename, collection_name):
        try:
            sys.path.insert(0, str(ROOT / "core"))

            from build_duplex import build_duplex

            result = build_duplex(
                csv_filename,
                collection_name=collection_name
            )

            self.result_queue.put(("success", result))

        except Exception as error:
            self.result_queue.put(("error", str(error)))

    def check_queue(self):
        try:
            while True:
                status, data = self.result_queue.get_nowait()

                if status == "success":
                    self.show_result(data)
                else:
                    self.show_error(data)

        except queue.Empty:
            pass

        self.root.after(200, self.check_queue)

    def show_result(self, result):
        self.cards_value.config(
            text=str(result["total_cards"])
        )
        self.sheets_value.config(
            text=str(result["total_sheets"])
        )
        self.pages_value.config(
            text=str(result["total_pages"])
        )

        self.result_label.config(
            text=f"Coleção: {result['collection']}",
            fg=COLORS["success"]
        )

        self.duplex_label.config(
            text=f"PDF DUPLEX: {result['duplex_file'].name}",
            fg=COLORS["text"]
        )

        self.generate_button.config(state="normal")
        self.open_folder_button.config(state="normal")

        self.status.config(
            text="●  PROCESSAMENTO CONCLUÍDO",
            foreground=COLORS["success"]
        )

        self.write_log("Geração concluída com sucesso.")

        messagebox.showinfo(
            "Sucesso",
            "PDF duplex gerado com sucesso!"
        )

    def show_error(self, error):
        self.generate_button.config(state="normal")

        self.status.config(
            text="●  ERRO NO PROCESSAMENTO",
            foreground=COLORS["error"]
        )

        self.write_log(f"ERRO: {error}")

        messagebox.showerror(
            "Erro na geração",
            error
        )

    def open_output_folder(self):
        OUTPUT.mkdir(exist_ok=True)
        os.startfile(str(OUTPUT))


if __name__ == "__main__":
    root = tk.Tk()
    app = MagicPrintManager(root)
    root.mainloop()
