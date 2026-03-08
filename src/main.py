"""
Platnik ZUS Exporter - Main GUI Application
Exports ZUS declarations from Platnik database to n8n webhook.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import sys
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add src directory to path for imports
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent.parent

sys.path.insert(0, str(BASE_DIR / "src"))

from db_reader import DatabaseReader, format_okres_readable, generate_periods
from webhook_sender import WebhookSender, format_payload_preview


# Professional color scheme (unified across app)
COLORS = {
    'bg': '#0f0f1a',
    'card': '#1a1a2e',
    'card_hover': '#252540',
    'accent': '#6366f1',
    'accent_hover': '#818cf8',
    'primary': '#6366f1',
    'primary_hover': '#818cf8',
    'success': '#10b981',
    'success_light': '#d1fae5',
    'warning': '#f59e0b',
    'warning_light': '#fef3c7',
    'error': '#ef4444',
    'error_light': '#fee2e2',
    'text': '#f8fafc',
    'text_secondary': '#94a3b8',
    'text_muted': '#64748b',
    'border': '#334155',
    'input_bg': '#1e293b',
    'input_border': '#475569',
    'code_bg': '#0d1117',
    'code_fg': '#7ee787',
}


class Config:
    """Configuration manager."""

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.data = self._load()

    def _load(self) -> Dict:
        default_config = {
            "sql_server": r"localhost\SQLEXPRESS",
            "database": "tax_testowa",
            "sql_username": "",
            "sql_password": "",
            "webhook_url": ""
        }

        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    return {**default_config, **loaded}
            except (json.JSONDecodeError, IOError):
                pass

        return default_config

    def save(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def set(self, key: str, value):
        self.data[key] = value


class PlatnikExporterApp:
    """Main application class with professional UI."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Platnik ZUS Exporter")
        self.root.geometry("800x700")
        self.root.configure(bg=COLORS['bg'])
        self.root.resizable(True, True)
        self.root.minsize(700, 600)

        # Load config
        self.config = Config(BASE_DIR / "config.json")

        # Initialize database reader
        self.db_reader = DatabaseReader(
            self.config.get('sql_server'),
            self.config.get('database'),
            self.config.get('sql_username', ''),
            self.config.get('sql_password', '')
        )

        # Initialize webhook sender
        self.webhook_sender = WebhookSender(self.config.get('webhook_url'))

        # Current payload for preview
        self.current_payload = None

        # Period mapping
        self.period_codes = {}

        # Configure styles
        self._configure_styles()

        # Build UI
        self._build_ui()

        # Load initial data
        self.root.after(100, self._initial_load)

    def _configure_styles(self):
        """Configure ttk styles for professional look."""
        style = ttk.Style()
        style.theme_use('clam')

        # Combobox styling
        style.configure('Custom.TCombobox',
            fieldbackground=COLORS['input_bg'],
            background=COLORS['input_bg'],
            foreground=COLORS['text'],
            arrowcolor=COLORS['text'],
            bordercolor=COLORS['input_border'],
            lightcolor=COLORS['input_border'],
            darkcolor=COLORS['input_border'],
            padding=10
        )
        style.map('Custom.TCombobox',
            fieldbackground=[('readonly', COLORS['input_bg'])],
            selectbackground=[('readonly', COLORS['accent'])],
            selectforeground=[('readonly', 'white')]
        )

    def _build_ui(self):
        """Build the professional user interface."""
        C = COLORS

        # Main container
        main = tk.Frame(self.root, bg=C['bg'])
        main.pack(fill=tk.BOTH, expand=True, padx=24, pady=20)

        # ══════════════════════════════════════════════════════════════════
        # HEADER
        # ══════════════════════════════════════════════════════════════════
        header = tk.Frame(main, bg=C['bg'])
        header.pack(fill=tk.X, pady=(0, 20))

        # Logo/Icon area
        logo_frame = tk.Frame(header, bg=C['bg'])
        logo_frame.pack(side=tk.LEFT)

        # App icon
        icon = tk.Label(logo_frame, text="📊", font=('Segoe UI', 28),
            bg=C['bg'], fg=C['accent'])
        icon.pack(side=tk.LEFT, padx=(0, 12))

        # Title block
        title_block = tk.Frame(logo_frame, bg=C['bg'])
        title_block.pack(side=tk.LEFT)

        title = tk.Label(title_block, text="Platnik ZUS Exporter",
            font=('Segoe UI', 20, 'bold'), bg=C['bg'], fg=C['text'])
        title.pack(anchor=tk.W)

        subtitle = tk.Label(title_block, text="Eksport deklaracji ZUS do n8n",
            font=('Segoe UI', 10), bg=C['bg'], fg=C['text_muted'])
        subtitle.pack(anchor=tk.W)

        # Settings button (right side)
        settings_btn = self._create_icon_button(header, "⚙", self._open_config,
            tooltip="Konfiguracja")
        settings_btn.pack(side=tk.RIGHT)

        # ══════════════════════════════════════════════════════════════════
        # STATUS BAR (BOTTOM - pack first for correct order)
        # ══════════════════════════════════════════════════════════════════
        status_frame = tk.Frame(main, bg=C['card'], highlightbackground=C['border'],
            highlightthickness=1)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(12, 0))

        status_inner = tk.Frame(status_frame, bg=C['card'])
        status_inner.pack(fill=tk.X, padx=12, pady=8)

        self.status_icon = tk.Label(status_inner, text="●", font=('Segoe UI', 10),
            bg=C['card'], fg=C['success'])
        self.status_icon.pack(side=tk.LEFT, padx=(0, 6))

        self.status_bar = tk.Label(status_inner, text="Gotowy",
            font=('Segoe UI', 9), bg=C['card'], fg=C['text_muted'])
        self.status_bar.pack(side=tk.LEFT)

        # Version info
        version_lbl = tk.Label(status_inner, text="v1.0.0",
            font=('Segoe UI', 9), bg=C['card'], fg=C['text_muted'])
        version_lbl.pack(side=tk.RIGHT)

        # ══════════════════════════════════════════════════════════════════
        # ACTION BUTTONS (BOTTOM)
        # ══════════════════════════════════════════════════════════════════
        btn_frame = tk.Frame(main, bg=C['bg'])
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(16, 0))

        # Primary action - Send
        self.send_btn = self._create_button(btn_frame, "🚀  Wyślij do n8n", "primary",
            self._send_data, large=True)
        self.send_btn.pack(side=tk.LEFT, padx=(0, 12))

        # Secondary actions
        json_btn = self._create_button(btn_frame, "📄 Pokaż JSON", "secondary",
            self._show_full_json)
        json_btn.pack(side=tk.LEFT, padx=(0, 8))

        copy_btn = self._create_button(btn_frame, "📋 Kopiuj", "secondary",
            self._copy_json)
        copy_btn.pack(side=tk.LEFT)

        # ══════════════════════════════════════════════════════════════════
        # CONNECTION STATUS CARD
        # ══════════════════════════════════════════════════════════════════
        status_card = self._create_card(main, "Status połączenia", "🔌")
        status_card.pack(fill=tk.X, pady=(0, 12))

        status_inner = tk.Frame(status_card, bg=C['card'])
        status_inner.pack(fill=tk.X, padx=16, pady=(8, 14))

        # Two columns for status
        status_row = tk.Frame(status_inner, bg=C['card'])
        status_row.pack(fill=tk.X)

        # Database status
        db_col = tk.Frame(status_row, bg=C['card'])
        db_col.pack(side=tk.LEFT, fill=tk.X, expand=True)

        db_header = tk.Frame(db_col, bg=C['card'])
        db_header.pack(anchor=tk.W)
        tk.Label(db_header, text="🗄", font=('Segoe UI', 11),
            bg=C['card'], fg=C['text_muted']).pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(db_header, text="Baza danych", font=('Segoe UI', 9, 'bold'),
            bg=C['card'], fg=C['text_secondary']).pack(side=tk.LEFT)

        self.db_status_label = tk.Label(db_col, text="● Sprawdzanie...",
            font=('Segoe UI', 10), bg=C['card'], fg=C['warning'])
        self.db_status_label.pack(anchor=tk.W, pady=(2, 0))

        # Webhook status
        wh_col = tk.Frame(status_row, bg=C['card'])
        wh_col.pack(side=tk.LEFT, fill=tk.X, expand=True)

        wh_header = tk.Frame(wh_col, bg=C['card'])
        wh_header.pack(anchor=tk.W)
        tk.Label(wh_header, text="🔗", font=('Segoe UI', 11),
            bg=C['card'], fg=C['text_muted']).pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(wh_header, text="Webhook n8n", font=('Segoe UI', 9, 'bold'),
            bg=C['card'], fg=C['text_secondary']).pack(side=tk.LEFT)

        self.webhook_status_label = tk.Label(wh_col, text="● Nie skonfigurowany",
            font=('Segoe UI', 10), bg=C['card'], fg=C['text_muted'])
        self.webhook_status_label.pack(anchor=tk.W, pady=(2, 0))

        # ══════════════════════════════════════════════════════════════════
        # PERIOD SELECTION CARD
        # ══════════════════════════════════════════════════════════════════
        period_card = self._create_card(main, "Wybór okresu rozliczeniowego", "📅")
        period_card.pack(fill=tk.X, pady=(0, 12))

        period_inner = tk.Frame(period_card, bg=C['card'])
        period_inner.pack(fill=tk.X, padx=16, pady=(8, 14))

        # Period selection row
        period_row = tk.Frame(period_inner, bg=C['card'])
        period_row.pack(fill=tk.X)

        # Combobox with border
        combo_border = tk.Frame(period_row, bg=C['input_border'], padx=1, pady=1)
        combo_border.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.period_var = tk.StringVar()
        self.period_combo = ttk.Combobox(
            combo_border,
            textvariable=self.period_var,
            state='readonly',
            font=('Segoe UI', 11),
            style='Custom.TCombobox'
        )
        self.period_combo.pack(fill=tk.X, ipady=6)
        self.period_combo.bind('<<ComboboxSelected>>', self._on_period_selected)

        # Refresh button
        refresh_btn = self._create_button(period_row, "🔄", "icon",
            self._refresh_periods)
        refresh_btn.pack(side=tk.LEFT, padx=(10, 0))

        # Declaration count badge
        self.count_badge = tk.Frame(period_inner, bg=C['accent'], padx=10, pady=4)

        self.count_label = tk.Label(self.count_badge, text="0 deklaracji",
            font=('Segoe UI', 9, 'bold'), bg=C['accent'], fg='white')
        self.count_label.pack()

        # ══════════════════════════════════════════════════════════════════
        # PREVIEW CARD
        # ══════════════════════════════════════════════════════════════════
        preview_card = self._create_card(main, "Podgląd danych", "👁")
        preview_card.pack(fill=tk.BOTH, expand=True)

        preview_inner = tk.Frame(preview_card, bg=C['card'])
        preview_inner.pack(fill=tk.BOTH, expand=True, padx=16, pady=(8, 14))

        # Code preview area
        code_border = tk.Frame(preview_inner, bg=C['input_border'], padx=1, pady=1)
        code_border.pack(fill=tk.BOTH, expand=True)

        self.preview_text = scrolledtext.ScrolledText(
            code_border,
            font=('Consolas', 10),
            bg=C['code_bg'],
            fg=C['code_fg'],
            insertbackground=C['text'],
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=12,
            pady=10
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        self.preview_text.insert('1.0', '// Wybierz okres, aby zobaczyć podgląd danych...')
        self.preview_text.config(state=tk.DISABLED)

    def _create_card(self, parent, title: str, icon: str) -> tk.Frame:
        """Create a professional card with icon and title."""
        C = COLORS

        card = tk.Frame(parent, bg=C['card'], highlightbackground=C['border'],
            highlightthickness=1)

        # Header
        header = tk.Frame(card, bg=C['card'])
        header.pack(fill=tk.X, padx=16, pady=(12, 4))

        # Icon
        icon_lbl = tk.Label(header, text=icon, font=('Segoe UI', 13),
            bg=C['card'], fg=C['accent'])
        icon_lbl.pack(side=tk.LEFT, padx=(0, 8))

        # Title
        title_lbl = tk.Label(header, text=title,
            font=('Segoe UI', 11, 'bold'), bg=C['card'], fg=C['text'])
        title_lbl.pack(side=tk.LEFT)

        return card

    def _create_button(self, parent, text: str, style: str, command, large: bool = False) -> tk.Button:
        """Create a professional button with hover effect."""
        C = COLORS

        if style == "primary":
            bg, fg = C['accent'], 'white'
            hover_bg = C['accent_hover']
            font_style = 'bold'
        elif style == "icon":
            bg, fg = C['card'], C['text_secondary']
            hover_bg = C['card_hover']
            font_style = ''
        else:  # secondary
            bg, fg = C['card'], C['text_secondary']
            hover_bg = C['card_hover']
            font_style = ''

        padding = (20, 10) if large else (12, 6)

        btn = tk.Button(parent, text=text,
            font=('Segoe UI', 11 if large else 10, font_style),
            bg=bg, fg=fg,
            activebackground=hover_bg, activeforeground=fg,
            relief=tk.FLAT, padx=padding[0], pady=padding[1],
            cursor='hand2', command=command)

        def on_enter(e):
            btn.config(bg=hover_bg)
        def on_leave(e):
            btn.config(bg=bg)

        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)

        return btn

    def _create_icon_button(self, parent, icon: str, command, tooltip: str = "") -> tk.Button:
        """Create an icon-only button."""
        C = COLORS

        btn = tk.Button(parent, text=icon,
            font=('Segoe UI', 14),
            bg=C['bg'], fg=C['text_muted'],
            activebackground=C['card'], activeforeground=C['accent'],
            relief=tk.FLAT, padx=8, pady=4,
            cursor='hand2', command=command, bd=0)

        def on_enter(e):
            btn.config(fg=C['accent'])
        def on_leave(e):
            btn.config(fg=C['text_muted'])

        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)

        return btn

    def _initial_load(self):
        """Load initial data after UI is built."""
        self._check_connections()
        self._load_periods()

    def _check_connections(self):
        """Check database and webhook connections."""
        C = COLORS

        # Check database
        success, message = self.db_reader.test_connection()
        if success:
            self.db_status_label.config(text="● Połączono", fg=C['success'])
        else:
            short_msg = message[:30] + "..." if len(message) > 30 else message
            self.db_status_label.config(text=f"● {short_msg}", fg=C['error'])

        # Check webhook
        webhook_url = self.config.get('webhook_url', '')
        if webhook_url:
            self.webhook_status_label.config(text="● Skonfigurowany", fg=C['success'])
        else:
            self.webhook_status_label.config(text="● Nie skonfigurowany", fg=C['text_muted'])

    def _load_periods(self):
        """Load available periods from database."""
        periods = self.db_reader.get_available_periods()

        if not periods:
            periods = generate_periods(12)

        period_options = []
        self.period_codes = {}

        for okres in periods[:24]:  # Last 24 periods max
            readable = format_okres_readable(okres)
            display = f"{readable} ({okres})"
            period_options.append(display)
            self.period_codes[display] = okres

        self.period_combo['values'] = period_options

        if period_options:
            self.period_combo.current(0)
            self._on_period_selected(None)

    def _refresh_periods(self):
        """Refresh periods from database."""
        self._update_status("Odświeżanie...", "loading")
        self._check_connections()
        self._load_periods()
        self._update_status("Odświeżono", "success")

    def _on_period_selected(self, event):
        """Handle period selection change."""
        selected = self.period_var.get()
        if selected and selected in self.period_codes:
            okres = self.period_codes[selected]
            self._update_status(f"Pobieranie danych dla {okres}...", "loading")

            # Get declarations
            declarations = self.db_reader.get_declarations_for_period(okres)
            count = len(declarations)

            # Update count badge
            self.count_label.config(text=f"{count} deklaracji")
            if count > 0:
                self.count_badge.pack(anchor=tk.W, pady=(8, 0))
                self.count_badge.config(bg=COLORS['success'])
                self.count_label.config(bg=COLORS['success'])
            else:
                self.count_badge.pack(anchor=tk.W, pady=(8, 0))
                self.count_badge.config(bg=COLORS['text_muted'])
                self.count_label.config(bg=COLORS['text_muted'])

            # Prepare payload preview
            if declarations:
                okres_readable = format_okres_readable(okres)
                self.current_payload = self.webhook_sender.prepare_payload(
                    okres, okres_readable, declarations
                )
                preview = format_payload_preview(self.current_payload, max_clients=5)
            else:
                self.current_payload = None
                preview = "// Brak deklaracji w wybranym okresie."

            # Update preview text
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete('1.0', tk.END)
            self.preview_text.insert('1.0', preview)
            self.preview_text.config(state=tk.DISABLED)

            self._update_status("Gotowy", "success")

    def _show_full_json(self):
        """Show full JSON payload in a new window."""
        if not self.current_payload:
            messagebox.showinfo("Info", "Brak danych do wyświetlenia.\nWybierz okres z deklaracjami.")
            return

        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title("Pełny payload JSON")
        popup.geometry("800x600")
        popup.configure(bg=COLORS['bg'])

        # Header
        header = tk.Label(popup, text="Payload wysyłany do n8n",
            font=('Segoe UI', 14, 'bold'), bg=COLORS['bg'], fg=COLORS['text'])
        header.pack(pady=(15, 10))

        # JSON text
        json_text = scrolledtext.ScrolledText(
            popup,
            font=('Consolas', 10),
            bg='#0d1117',
            fg='#7ee787',
            insertbackground=COLORS['text'],
            relief=tk.FLAT,
            wrap=tk.NONE
        )
        json_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

        # Format JSON with indentation
        json_str = json.dumps(self.current_payload, indent=2, ensure_ascii=False)
        json_text.insert('1.0', json_str)
        json_text.config(state=tk.DISABLED)

        # Buttons
        btn_frame = tk.Frame(popup, bg=COLORS['bg'])
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 15))

        copy_btn = tk.Button(btn_frame, text="Kopiuj do schowka",
            font=('Segoe UI', 10), bg=COLORS['accent'], fg=COLORS['text'],
            relief=tk.FLAT, padx=15, pady=8, cursor='hand2',
            command=lambda: self._copy_to_clipboard(json_str))
        copy_btn.pack(side=tk.LEFT, padx=(0, 10))

        close_btn = tk.Button(btn_frame, text="Zamknij",
            font=('Segoe UI', 10), bg=COLORS['accent'], fg=COLORS['text'],
            relief=tk.FLAT, padx=15, pady=8, cursor='hand2',
            command=popup.destroy)
        close_btn.pack(side=tk.LEFT)

    def _copy_json(self):
        """Copy JSON payload to clipboard."""
        if not self.current_payload:
            messagebox.showinfo("Info", "Brak danych do skopiowania.")
            return

        json_str = json.dumps(self.current_payload, indent=2, ensure_ascii=False)
        self._copy_to_clipboard(json_str)
        self._update_status("JSON skopiowany do schowka!", "success")

    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard."""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()

    def _update_status(self, message: str, status_type: str = "info"):
        """Update status bar with icon and color."""
        C = COLORS

        if status_type == "success":
            icon, color = "●", C['success']
        elif status_type == "error":
            icon, color = "●", C['error']
        elif status_type == "loading":
            icon, color = "◌", C['warning']
        else:
            icon, color = "●", C['text_muted']

        self.status_icon.config(text=icon, fg=color)
        self.status_bar.config(text=message)
        self.root.update_idletasks()

    def _send_data(self):
        """Send data to webhook in background thread."""
        if not self.current_payload:
            messagebox.showwarning("Uwaga", "Brak danych do wysłania.\nWybierz okres z deklaracjami.")
            return

        if not self.config.get('webhook_url'):
            messagebox.showwarning("Uwaga", "Skonfiguruj URL webhooka w Konfiguracja")
            return

        # Confirm
        count = self.current_payload.get('liczba_klientow', 0)
        okres = self.current_payload.get('okres_czytelny', '')
        if not messagebox.askyesno("Potwierdzenie",
            f"Wysłać {count} deklaracji za {okres} do n8n?"):
            return

        # Disable button
        self.send_btn.config(state='disabled', text="⏳ Wysyłanie...")

        # Run in background thread
        thread = threading.Thread(target=self._do_send)
        thread.daemon = True
        thread.start()

    def _do_send(self):
        """Background thread for sending data."""
        try:
            okres = self.current_payload.get('okres', '')
            okres_readable = self.current_payload.get('okres_czytelny', '')
            klienci = self.current_payload.get('klienci', [])

            # Reconstruct declarations format for sender
            declarations = []
            for k in klienci:
                declarations.append({
                    'NIP': k['nip'],
                    'Firma': k['nazwa'],
                    'SkladkiSpoleczne': k['skladki_spoleczne'],
                    'FunduszPracy': k['fundusz_pracy'],
                    'FGSP': k['fgsp'],
                    'SumaDoZaplaty': k['suma_do_zaplaty']
                })

            self.root.after(0, lambda: self._update_status("Wysyłanie do n8n...", "loading"))

            success, message = self.webhook_sender.send(okres, okres_readable, declarations)

            self.root.after(0, lambda: self._send_complete(success, message))

        except Exception as e:
            self.root.after(0, lambda: self._send_complete(False, f"Błąd: {str(e)}"))

    def _send_complete(self, success: bool, message: str):
        """Handle send completion."""
        self.send_btn.config(state='normal', text="🚀  Wyślij do n8n")
        self._update_status(message, "success" if success else "error")

        if success:
            messagebox.showinfo("Sukces", message)
        else:
            messagebox.showerror("Błąd", message)

    def _open_config(self):
        """Open configuration dialog."""
        ConfigDialog(self.root, self.config, self._on_config_saved)

    def _on_config_saved(self):
        """Handle configuration save."""
        self.db_reader = DatabaseReader(
            self.config.get('sql_server'),
            self.config.get('database'),
            self.config.get('sql_username', ''),
            self.config.get('sql_password', '')
        )
        self.webhook_sender = WebhookSender(self.config.get('webhook_url'))

        self._check_connections()
        self._load_periods()


class ConfigDialog:
    """Professional configuration dialog window."""

    # Professional color scheme
    DIALOG_COLORS = {
        'bg': '#0f0f1a',
        'card': '#1a1a2e',
        'card_hover': '#252540',
        'accent': '#6366f1',
        'accent_hover': '#818cf8',
        'success': '#10b981',
        'danger': '#ef4444',
        'text': '#f8fafc',
        'text_secondary': '#94a3b8',
        'text_muted': '#64748b',
        'border': '#334155',
        'input_bg': '#1e293b',
        'input_border': '#475569',
    }

    def __init__(self, parent, config: Config, on_save_callback):
        self.config = config
        self.on_save_callback = on_save_callback

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Konfiguracja")
        self.dialog.configure(bg=self.DIALOG_COLORS['bg'])
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._build_ui()

        # Center dialog on parent
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")

    def _build_ui(self):
        """Build professional configuration dialog UI."""
        C = self.DIALOG_COLORS

        # Main container with padding
        main = tk.Frame(self.dialog, bg=C['bg'])
        main.pack(fill=tk.BOTH, expand=True, padx=24, pady=20)

        # ══════════════════════════════════════════════════════════════════
        # HEADER
        # ══════════════════════════════════════════════════════════════════
        header = tk.Frame(main, bg=C['bg'])
        header.pack(fill=tk.X, pady=(0, 16))

        # Icon + Title
        title_frame = tk.Frame(header, bg=C['bg'])
        title_frame.pack(side=tk.LEFT)

        icon = tk.Label(title_frame, text="⚙", font=('Segoe UI', 20),
            bg=C['bg'], fg=C['accent'])
        icon.pack(side=tk.LEFT, padx=(0, 10))

        title = tk.Label(title_frame, text="Konfiguracja",
            font=('Segoe UI', 18, 'bold'), bg=C['bg'], fg=C['text'])
        title.pack(side=tk.LEFT)

        # ══════════════════════════════════════════════════════════════════
        # MAIN SETTINGS CARD
        # ══════════════════════════════════════════════════════════════════
        main_card = self._create_card(main, "Połączenie z bazą danych", "🗄")
        main_card.pack(fill=tk.X, pady=(0, 12))

        card_inner = tk.Frame(main_card, bg=C['card'])
        card_inner.pack(fill=tk.X, padx=16, pady=(8, 16))

        # Server field
        self.server_entry = self._create_input_field(card_inner,
            "Serwer SQL", "np. localhost\\SQLEXPRESS lub 192.168.1.100",
            self.config.get('sql_server', ''))

        # Database field
        self.db_entry = self._create_input_field(card_inner,
            "Baza danych", "np. tax_testowa",
            self.config.get('database', ''))

        # ══════════════════════════════════════════════════════════════════
        # WEBHOOK CARD
        # ══════════════════════════════════════════════════════════════════
        webhook_card = self._create_card(main, "Integracja n8n", "🔗")
        webhook_card.pack(fill=tk.X, pady=(0, 12))

        webhook_inner = tk.Frame(webhook_card, bg=C['card'])
        webhook_inner.pack(fill=tk.X, padx=16, pady=(8, 16))

        self.webhook_entry = self._create_input_field(webhook_inner,
            "Webhook URL", "https://your-n8n.app.n8n.cloud/webhook/...",
            self.config.get('webhook_url', ''))

        # ══════════════════════════════════════════════════════════════════
        # OPTIONAL AUTH CARD (COLLAPSIBLE STYLE)
        # ══════════════════════════════════════════════════════════════════
        auth_card = self._create_card(main, "Autentykacja SQL (opcjonalne)", "🔐",
            subtitle="Pozostaw puste dla Windows Authentication")
        auth_card.pack(fill=tk.X, pady=(0, 16))

        auth_inner = tk.Frame(auth_card, bg=C['card'])
        auth_inner.pack(fill=tk.X, padx=16, pady=(8, 16))

        # Two columns for username/password
        auth_row = tk.Frame(auth_inner, bg=C['card'])
        auth_row.pack(fill=tk.X)

        # Username
        user_col = tk.Frame(auth_row, bg=C['card'])
        user_col.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.username_entry = self._create_input_field(user_col,
            "Użytkownik", "np. sa",
            self.config.get('sql_username', ''), compact=True)

        # Password
        pass_col = tk.Frame(auth_row, bg=C['card'])
        pass_col.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        self.password_entry = self._create_input_field(pass_col,
            "Hasło", "••••••••",
            self.config.get('sql_password', ''), is_password=True, compact=True)

        # ══════════════════════════════════════════════════════════════════
        # ACTION BUTTONS
        # ══════════════════════════════════════════════════════════════════
        btn_frame = tk.Frame(main, bg=C['bg'])
        btn_frame.pack(fill=tk.X, pady=(4, 0))

        # Cancel button (left)
        cancel_btn = self._create_button(btn_frame, "Anuluj", "secondary",
            self.dialog.destroy)
        cancel_btn.pack(side=tk.LEFT)

        # Right-side buttons
        right_btns = tk.Frame(btn_frame, bg=C['bg'])
        right_btns.pack(side=tk.RIGHT)

        test_btn = self._create_button(right_btns, "🔌 Test połączenia", "secondary",
            self._test)
        test_btn.pack(side=tk.LEFT, padx=(0, 8))

        save_btn = self._create_button(right_btns, "💾 Zapisz", "primary",
            self._save)
        save_btn.pack(side=tk.LEFT)

    def _create_card(self, parent, title: str, icon: str, subtitle: str = None) -> tk.Frame:
        """Create a professional card with icon and title."""
        C = self.DIALOG_COLORS

        card = tk.Frame(parent, bg=C['card'], highlightbackground=C['border'],
            highlightthickness=1)

        # Header row
        header = tk.Frame(card, bg=C['card'])
        header.pack(fill=tk.X, padx=16, pady=(12, 4))

        # Icon
        icon_lbl = tk.Label(header, text=icon, font=('Segoe UI', 14),
            bg=C['card'], fg=C['accent'])
        icon_lbl.pack(side=tk.LEFT, padx=(0, 8))

        # Title
        title_lbl = tk.Label(header, text=title,
            font=('Segoe UI', 11, 'bold'), bg=C['card'], fg=C['text'])
        title_lbl.pack(side=tk.LEFT)

        # Subtitle if provided
        if subtitle:
            sub_lbl = tk.Label(header, text=f"  •  {subtitle}",
                font=('Segoe UI', 9), bg=C['card'], fg=C['text_muted'])
            sub_lbl.pack(side=tk.LEFT)

        return card

    def _create_input_field(self, parent, label: str, placeholder: str,
                           value: str, is_password: bool = False,
                           compact: bool = False) -> tk.Entry:
        """Create a professional input field with label."""
        C = self.DIALOG_COLORS

        container = tk.Frame(parent, bg=C['card'])
        container.pack(fill=tk.X, pady=(0, 8 if compact else 10))

        # Label
        lbl = tk.Label(container, text=label,
            font=('Segoe UI', 9, 'bold'), bg=C['card'], fg=C['text_secondary'])
        lbl.pack(anchor=tk.W, pady=(0, 4))

        # Input with border effect
        input_border = tk.Frame(container, bg=C['input_border'], padx=1, pady=1)
        input_border.pack(fill=tk.X)

        entry = tk.Entry(input_border,
            font=('Segoe UI', 10),
            bg=C['input_bg'],
            fg=C['text'],
            insertbackground=C['text'],
            relief=tk.FLAT,
            show='●' if is_password else '')
        entry.pack(fill=tk.X, ipady=8, padx=1, pady=1)

        if value:
            entry.insert(0, value)
        else:
            # Placeholder effect
            entry.insert(0, placeholder)
            entry.config(fg=C['text_muted'])

            def on_focus_in(e):
                if entry.get() == placeholder:
                    entry.delete(0, tk.END)
                    entry.config(fg=C['text'], show='●' if is_password else '')

            def on_focus_out(e):
                if not entry.get():
                    entry.insert(0, placeholder)
                    entry.config(fg=C['text_muted'], show='')

            entry.bind('<FocusIn>', on_focus_in)
            entry.bind('<FocusOut>', on_focus_out)

        # Hover effect for border
        def on_enter(e):
            input_border.config(bg=C['accent'])
        def on_leave(e):
            input_border.config(bg=C['input_border'])

        entry.bind('<Enter>', on_enter)
        entry.bind('<Leave>', on_leave)

        return entry

    def _create_button(self, parent, text: str, style: str, command) -> tk.Button:
        """Create a professional button with hover effect."""
        C = self.DIALOG_COLORS

        if style == "primary":
            bg, fg = C['accent'], 'white'
            hover_bg = C['accent_hover']
        elif style == "success":
            bg, fg = C['success'], 'white'
            hover_bg = '#34d399'
        else:  # secondary
            bg, fg = C['card'], C['text_secondary']
            hover_bg = C['card_hover']

        btn = tk.Button(parent, text=text,
            font=('Segoe UI', 10, 'bold' if style == 'primary' else ''),
            bg=bg, fg=fg,
            activebackground=hover_bg, activeforeground=fg,
            relief=tk.FLAT, padx=16, pady=8, cursor='hand2',
            command=command)

        # Hover effect
        def on_enter(e):
            btn.config(bg=hover_bg)
        def on_leave(e):
            btn.config(bg=bg)

        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)

        return btn

    def _get_entry_value(self, entry: tk.Entry, placeholder: str = "") -> str:
        """Get entry value, ignoring placeholder text."""
        value = entry.get()
        if value == placeholder or entry.cget('fg') == self.DIALOG_COLORS['text_muted']:
            return ""
        return value.strip()

    def _save(self):
        """Save configuration."""
        self.config.set('sql_server', self._get_entry_value(self.server_entry, "np. localhost\\SQLEXPRESS lub 192.168.1.100"))
        self.config.set('database', self._get_entry_value(self.db_entry, "np. tax_testowa"))
        self.config.set('sql_username', self._get_entry_value(self.username_entry, "np. sa"))
        self.config.set('sql_password', self._get_entry_value(self.password_entry, "••••••••"))
        self.config.set('webhook_url', self._get_entry_value(self.webhook_entry, "https://your-n8n.app.n8n.cloud/webhook/..."))
        self.config.save()

        self.on_save_callback()
        self.dialog.destroy()

    def _test(self):
        """Test connections with professional result dialog."""
        C = self.DIALOG_COLORS

        server = self._get_entry_value(self.server_entry, "np. localhost\\SQLEXPRESS lub 192.168.1.100")
        database = self._get_entry_value(self.db_entry, "np. tax_testowa")
        username = self._get_entry_value(self.username_entry, "np. sa")
        password = self._get_entry_value(self.password_entry, "••••••••")
        webhook = self._get_entry_value(self.webhook_entry, "https://your-n8n.app.n8n.cloud/webhook/...")

        # Build result message
        results = []

        # Auth mode
        auth_mode = "SQL Server Auth" if (username and password) else "Windows Auth"
        results.append(f"Tryb: {auth_mode}\n")

        # Test database
        reader = DatabaseReader(server, database, username, password)
        db_ok, db_msg = reader.test_connection()
        status = "✅" if db_ok else "❌"
        results.append(f"{status} Baza danych\n   {db_msg}")

        # Test webhook
        if webhook:
            sender = WebhookSender(webhook)
            wh_ok, wh_msg = sender.test_connection()
            status = "✅" if wh_ok else "❌"
            results.append(f"\n{status} Webhook\n   {wh_msg}")
        else:
            results.append(f"\n⚠️ Webhook\n   Nie skonfigurowany")

        # Show result
        title = "Test zakończony pomyślnie" if db_ok else "Wykryto problemy"
        messagebox.showinfo(title, "\n".join(results))


def main():
    """Main entry point."""
    root = tk.Tk()

    try:
        icon_path = BASE_DIR / "icon.ico"
        if icon_path.exists():
            root.iconbitmap(str(icon_path))
    except:
        pass

    app = PlatnikExporterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
