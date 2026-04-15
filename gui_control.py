import tkinter as tk
from tkinter import messagebox
import threading
import time

# Deine Module
import config
import sensors
import display_manager
import alarm_system
import nfc_auth
import flappy_logic

class AdminDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Tinkerforge Control Center")
        self.root.geometry("550x950")
        self.root.configure(bg="#1e1e2e")

        self.security = nfc_auth.SecurityManager()
        self.game = flappy_logic.FlappyBird()
        
        # Datenbank: {"[4, 29, 124, ...]": "Rolle"}
        self.user_db = {} 
        
        self._build_ui()
        self._auto_update()

    def _build_ui(self):
        bg, fg, accent, s_bg = "#1e1e2e", "#cdd6f4", "#89b4fa", "#313244"

        # Titel & Sensoren (Alt-Funktion)
        tk.Label(self.root, text="🖥 System Monitor", bg=bg, fg=accent, font=("Consolas", 16, "bold")).pack(pady=10)
        
        self.sf = tk.Frame(self.root, bg=s_bg, bd=2, relief="groove")
        self.sf.pack(fill="x", padx=20, pady=5)
        self.var_temp = tk.StringVar(value="Temp: -- °C")
        tk.Label(self.sf, textvariable=self.var_temp, bg=s_bg, fg=fg, font=("Consolas", 12)).pack(pady=10)

        # --- NEU: KARTEN VERWALTUNG ---
        nf = tk.Frame(self.root, bg=s_bg, bd=2, relief="groove")
        nf.pack(fill="x", padx=20, pady=10)
        
        self.card_listbox = tk.Listbox(nf, height=6, bg="#181825", fg=fg, font=("Consolas", 10))
        self.card_listbox.pack(fill="x", padx=15, pady=10)

        role_f = tk.Frame(nf, bg=s_bg)
        role_f.pack(fill="x", pady=5)
        tk.Button(role_f, text="ADMIN", bg="#f9e2af", width=12, command=lambda: self._set_role("Admin")).pack(side="left", expand=True)
        tk.Button(role_f, text="TECHNIKER", bg="#89b4fa", width=12, command=lambda: self._set_role("Techniker")).pack(side="left", expand=True)
        tk.Button(role_f, text="LÖSCHEN", bg="#f38ba8", width=12, command=self._delete_card).pack(side="left", expand=True)

        tk.Button(self.root, text="➕ NEUE KARTE EINLESEN", bg="#a6e3a1", font=("Consolas", 10, "bold"),
                  command=self._scan_new_card_workflow).pack(fill="x", padx=20, pady=5)

        # --- SYSTEM AKTIONEN (ALT-FUNKTIONEN) ---
        af = tk.Frame(self.root, bg=bg)
        af.pack(fill="x", padx=20, pady=10)
        
        actions = [
            ("🕐 Segment Wechsel", "#cba6f7", self._toggle_segment),
            ("🎵 Imperial March", "#fab387", self._play_march),
            ("🐦 Flappy Bird", "#a6e3a1", self._easter_egg),
            ("🔔 Alarm Test", "#f38ba8", self._test_alarm)
        ]
        for txt, col, cmd in actions:
            tk.Button(af, text=txt, bg=col, font=("Consolas", 10), command=cmd).pack(fill="x", pady=2)

        self.log_box = tk.Text(self.root, height=8, bg="#181825", fg="#a6adc8", font=("Consolas", 9))
        self.log_box.pack(fill="both", padx=20, pady=10)

    def _log(self, msg):
        self.log_box.insert("end", f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log_box.see("end")

    # --- NEUE LOGIK FÜR KARTEN ---
    def _scan_new_card_workflow(self):
        self._log("NFC: Bitte Karte vorhalten...")
        def _worker():
            # Ruft die neue get_raw_id Methode auf
            raw_id = self.security.get_raw_id(timeout=10)
            if raw_id:
                cid = str(raw_id)
                if cid not in self.user_db:
                    self.user_db[cid] = "Keine" # Initial 0 Rechte
                    self._log(f"Karte erkannt: {cid}")
                    self.root.after(0, self._refresh_list)
                else:
                    self._log("Karte ist bereits in der Liste.")
            else:
                self._log("NFC: Zeitüberschreitung.")
        threading.Thread(target=_worker, daemon=True).start()

    def _refresh_list(self):
        self.card_listbox.delete(0, tk.END)
        for cid, role in self.user_db.items():
            self.card_listbox.insert(tk.END, f"[{role:^10}] ID: {cid}")
        # Die Security-Logik mit dem neuen Dictionary füttern
        self.security.admin_tag_id = self.user_db

    def _set_role(self, role):
        sel = self.card_listbox.curselection()
        if not sel: return
        cid = self.card_listbox.get(sel[0]).split("ID: ")[1]
        self.user_db[cid] = role
        self._refresh_list()
        self._log(f"Berechtigung geändert: {cid} -> {role}")

    def _delete_card(self):
        sel = self.card_listbox.curselection()
        if not sel: return
        cid = self.card_listbox.get(sel[0]).split("ID: ")[1]
        del self.user_db[cid]
        self._refresh_list()
        self._log(f"Karte gelöscht: {cid}")

    # --- ALT-FUNKTIONEN (SENSOREN ETC) ---
    def _auto_update(self):
        try:
            data = sensors.get_all_metrics()
            self.var_temp.set(f"Temperatur: {data['temp']:.1f} °C")
        except: pass
        self.root.after(5000, self._auto_update)

    def _toggle_segment(self):
        display_manager.toggle_segment_mode()
        threading.Thread(target=display_manager.show_on_segment, daemon=True).start()

    def _play_march(self):
        threading.Thread(target=alarm_system.play_imperial_march, daemon=True).start()

    def _test_alarm(self):
        threading.Thread(target=alarm_system.play_alarm, daemon=True).start()

    def _easter_egg(self):
        self.game.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminDashboard(root)
    root.mainloop()