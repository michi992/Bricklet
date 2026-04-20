"""
Serverraum-Überwachung – Admin Dashboard (Final)
Start: python gui_control.py
"""
import tkinter as tk
from tkinter import messagebox
import threading
import time

import config
import sensors
import display_manager
import alarm_system
import nfc_auth
import flappy_logic

class AdminDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Tinkerforge Serverraum-Überwachung")
        self.root.geometry("550x950")
        self.root.configure(bg="#1e1e2e")
        self.root.resizable(False, False)

        self.segment_mode = "time"
        self.game = flappy_logic.FlappyBird()
        self.security = nfc_auth.SecurityManager()
        self.user_db = {}  # {"ID-String": "Rolle"}

        self._build_ui()
        self._auto_update()

        # Segment-Loop beim Start automatisch starten
        display_manager.start_segment_loop()

    def _build_ui(self):
        bg, fg, accent, s_bg = "#1e1e2e", "#cdd6f4", "#89b4fa", "#313244"

        # Titel
        tk.Label(self.root, text="🖥  Serverraum-Überwachung",
                 bg=bg, fg=accent, font=("Consolas", 16, "bold")).pack(pady=10)

        # --- Sensor-Frame ---
        sf = tk.Frame(self.root, bg=s_bg, bd=2, relief="groove")
        sf.pack(fill="x", padx=20, pady=5)
        tk.Label(sf, text="Live-Sensordaten", bg=s_bg, fg=accent,
                 font=("Consolas", 11, "bold")).grid(row=0, columnspan=2, pady=6)

        self.var_temp = tk.StringVar(value="Temp:     -- °C")
        self.var_lux  = tk.StringVar(value="Licht:    -- lx")
        self.var_hum  = tk.StringVar(value="Feucht.:  -- %")
        self.var_time = tk.StringVar(value="Zeit:     --:--:--")

        for i, v in enumerate([self.var_temp, self.var_lux, self.var_hum, self.var_time]):
            tk.Label(sf, textvariable=v, bg=s_bg, fg=fg,
                     font=("Consolas", 12), anchor="w", width=28).grid(
                row=i+1, column=0, padx=16, pady=2, sticky="w")

        self.lbl_status = tk.Label(sf, text="● OK", bg=s_bg,
                                   fg="#a6e3a1", font=("Consolas", 12, "bold"))
        self.lbl_status.grid(row=1, column=1, rowspan=3, padx=10)

        # --- NFC Karten-Management ---
        nf = tk.Frame(self.root, bg=s_bg, bd=2, relief="groove")
        nf.pack(fill="x", padx=20, pady=10)
        tk.Label(nf, text="NFC Berechtigungs-Management", bg=s_bg,
                 fg="#fab387", font=("Consolas", 11, "bold")).pack(pady=5)

        self.card_listbox = tk.Listbox(nf, height=6, bg="#181825", fg=fg,
                                       font=("Consolas", 10), borderwidth=0,
                                       selectbackground="#45475a")
        self.card_listbox.pack(fill="x", padx=15, pady=5)

        # Rollen-Buttons
        role_f = tk.Frame(nf, bg=s_bg)
        role_f.pack(fill="x", padx=10, pady=5)
        tk.Button(role_f, text="Admin",     bg="#f9e2af", relief="flat",
                  command=lambda: self._set_role("Admin")).pack(side="left", expand=True, padx=2)
        tk.Button(role_f, text="Techniker", bg="#89b4fa", relief="flat",
                  command=lambda: self._set_role("Techniker")).pack(side="left", expand=True, padx=2)
        tk.Button(role_f, text="Sperren",   bg="#6c7086", fg="white", relief="flat",
                  command=lambda: self._set_role("Keine")).pack(side="left", expand=True, padx=2)

        # Scan & Löschen
        mgmt_f = tk.Frame(nf, bg=s_bg)
        mgmt_f.pack(fill="x", padx=10, pady=10)
        tk.Button(mgmt_f, text="➕ Neue Karte einlesen (0 Rechte)", bg="#a6e3a1",
                  relief="flat", font=("Consolas", 10, "bold"),
                  command=self._scan_new_card).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(mgmt_f, text="🗑 Löschen", bg="#f38ba8", relief="flat",
                  command=self._delete_card).pack(side="left", padx=2)

        # --- System-Aktionen ---
        af = tk.Frame(self.root, bg=bg)
        af.pack(fill="x", padx=20, pady=5)
        tk.Label(af, text="System-Aktionen", bg=bg, fg=accent,
                 font=("Consolas", 11, "bold")).pack(anchor="w")

        buttons = [
            ("🕐  Segment: Zeit/Datum",  "#cba6f7", self._toggle_segment),
            ("🔔  Test-Alarm (Beep)",     "#f38ba8", self._test_alarm),
            ("🎵  Imperial March",        "#fab387", self._play_march),
            ("🔒  Auth-Check (NFC)",      "#f9e2af", self._nfc_reset),
            ("🐦  Easter Egg (Flappy)",   "#a6e3a1", self._easter_egg),
        ]
        for txt, color, cmd in buttons:
            tk.Button(af, text=txt, bg=color, fg="#1e1e2e",
                      font=("Consolas", 10, "bold"), relief="flat",
                      cursor="hand2", command=cmd).pack(fill="x", pady=2, ipady=4)

        # --- Log ---
        lf = tk.Frame(self.root, bg=bg)
        lf.pack(fill="both", expand=True, padx=20, pady=10)
        self.log_box = tk.Text(lf, height=7, bg="#181825", fg="#a6adc8",
                               font=("Consolas", 9), state="disabled", relief="flat")
        self.log_box.pack(fill="both", expand=True)

    def _log(self, msg):
        ts = time.strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{ts}] {msg}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    # --- NFC Karten-Logik ---

    def _scan_new_card(self):
        self._log("NFC: Bitte Karte vorhalten...")
        def _worker():
            cid = self.security.get_raw_id(timeout=10)
            if cid:
                if cid not in self.user_db:
                    self.user_db[cid] = "Keine"
                    self._log(f"Neue Karte erkannt: {cid} (0 Rechte)")
                    self.root.after(0, self._refresh_list)
                else:
                    self._log("Karte bereits in der Liste.")
            else:
                self._log("NFC: Kein Tag gefunden / Timeout.")
        threading.Thread(target=_worker, daemon=True).start()

    def _refresh_list(self):
        self.card_listbox.delete(0, tk.END)
        for cid, role in self.user_db.items():
            self.card_listbox.insert(tk.END, f"[{role:^10}] ID: {cid}")
        self.security.admin_tag_id = self.user_db

    def _set_role(self, new_role):
        sel = self.card_listbox.curselection()
        if not sel:
            messagebox.showwarning("Auswahl", "Bitte eine Karte auswählen!")
            return
        cid = self.card_listbox.get(sel[0]).split("ID: ")[1]
        self.user_db[cid] = new_role
        self._refresh_list()
        self._log(f"Berechtigung: {cid} -> {new_role}")

    def _delete_card(self):
        sel = self.card_listbox.curselection()
        if not sel:
            messagebox.showwarning("Auswahl", "Bitte eine Karte auswählen!")
            return
        cid = self.card_listbox.get(sel[0]).split("ID: ")[1]
        del self.user_db[cid]
        self._refresh_list()
        self._log(f"Karte gelöscht: {cid}")

    # --- Sensor-Logik ---

    def _refresh_sensors(self):
        try:
            data = sensors.get_all_metrics()
            self.var_temp.set(f"Temp:     {data['temp']:.1f} °C")
            self.var_lux.set( f"Licht:    {data['lux']:.1f} lx")
            self.var_hum.set( f"Feucht.:  {data['hum']:.1f} %")
            self.var_time.set(f"Zeit:     {time.strftime('%H:%M:%S')}")
            if data["temp"] >= config.TEMP_CRIT:
                self.lbl_status.config(text="● KRITISCH", fg="#f38ba8")
                self._log(f"ALARM: Temperatur kritisch! {data['temp']:.1f}°C")
                threading.Thread(target=alarm_system.play_imperial_march, daemon=True).start()
            elif data["temp"] >= config.TEMP_WARN:
                self.lbl_status.config(text="● WARNUNG",  fg="#f9e2af")
                self._log(f"WARNUNG: Temperatur {data['temp']:.1f}°C")
                threading.Thread(target=alarm_system.play_alarm, daemon=True).start()
            else:
                self.lbl_status.config(text="● OK",       fg="#a6e3a1")
        except Exception as e:
            self._log(f"Sensor-Fehler: {e}")

    def _auto_update(self):
        self._refresh_sensors()
        self.root.after(5000, self._auto_update)

    # --- System-Aktionen ---

    def _toggle_segment(self):
        mode = display_manager.toggle_segment_mode()
        self._log(f"Segment-Modus: {mode}")

    def _test_alarm(self):
        self._log("Alarm-Test gestartet.")
        threading.Thread(target=alarm_system.play_alarm, daemon=True).start()

    def _play_march(self):
        self._log("Imperial March gestartet.")
        threading.Thread(target=alarm_system.play_imperial_march, daemon=True).start()

    def _nfc_reset(self):
        def _worker():
            self._log("Auth-Check: Bitte Admin-Karte scannen...")
            if self.security.check_card():
                self._log("ZUGRIFF ERLAUBT.")
                self.root.after(0, lambda: messagebox.showinfo("NFC Auth", "Zugriff gestattet!"))
            else:
                self._log("ZUGRIFF VERWEIGERT.")
                self.root.after(0, lambda: messagebox.showerror("NFC Auth", "Ungültige Karte!"))
        threading.Thread(target=_worker, daemon=True).start()

    def _easter_egg(self):
        self._log("Flappy Bird gestartet (LCD).")
        self.game.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminDashboard(root)
    root.mainloop()