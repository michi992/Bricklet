"""
Serverraum-Überwachung – Admin Dashboard
Startet mit: python gui_control.py
"""
import tkinter as tk
from tkinter import messagebox, font
import threading
import time
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_lcd_128x64 import BrickletLCD128x64

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
        self.root.geometry("520x600")
        self.root.configure(bg="#1e1e2e")
        self.root.resizable(False, False)

        self.segment_mode = "time"
        self.game = flappy_logic.FlappyBird()
        self._game_thread = None
        self._game_stop = threading.Event()
        self._flappy_mode = False
        self.security = nfc_auth.SecurityManager()
        self._build_ui()
        self.root.bind("<space>", self._flap_key)
        self.root.bind("<Escape>", self._stop_game_key)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._auto_update()

    def _build_ui(self):
        bg = "#1e1e2e"
        fg = "#cdd6f4"
        accent = "#89b4fa"

        # Titel
        tk.Label(self.root, text="🖥  Serverraum-Überwachung",
                 bg=bg, fg=accent, font=("Consolas", 16, "bold")).pack(pady=12)

        # Status-Frame
        sf = tk.Frame(self.root, bg="#313244", bd=2, relief="groove")
        sf.pack(fill="x", padx=20, pady=5)
        tk.Label(sf, text="Live-Sensordaten", bg="#313244", fg=accent,
                 font=("Consolas", 11, "bold")).grid(row=0, columnspan=2, pady=6)

        self.var_temp = tk.StringVar(value="Temp:     -- °C")
        self.var_lux  = tk.StringVar(value="Licht:    -- lx")
        self.var_hum  = tk.StringVar(value="Feucht.:  -- %")
        self.var_time = tk.StringVar(value="Zeit:     --:--:--")

        for i, v in enumerate([self.var_temp, self.var_lux, self.var_hum, self.var_time]):
            tk.Label(sf, textvariable=v, bg="#313244", fg=fg,
                     font=("Consolas", 12), anchor="w", width=28).grid(
                row=i+1, column=0, padx=16, pady=2, sticky="w")

        self.lbl_status = tk.Label(sf, text="● OK", bg="#313244",
                                   fg="#a6e3a1", font=("Consolas", 12, "bold"))
        self.lbl_status.grid(row=1, column=1, rowspan=3, padx=10)

        # Aktionen
        af = tk.Frame(self.root, bg=bg)
        af.pack(fill="x", padx=20, pady=10)
        tk.Label(af, text="Aktionen", bg=bg, fg=accent,
                 font=("Consolas", 11, "bold")).pack(anchor="w")

        buttons = [
            ("🔄  Werte aktualisieren",    "#89b4fa", "#1e1e2e", self._refresh),
            ("🕐  Segment: Zeit/Datum",    "#cba6f7", "#1e1e2e", self._toggle_segment),
            ("🔔  Test-Alarm (Beep)",      "#f38ba8", "#1e1e2e", self._test_alarm),
            ("🎵  Imperial March",         "#fab387", "#1e1e2e", self._play_march),
            ("🔒  Full Reset (NFC)",       "#f9e2af", "#1e1e2e", self._nfc_reset),
            ("🐦  Easter Egg (Flappy)",    "#a6e3a1", "#1e1e2e", self._easter_egg),
        ]
        for txt, bg_b, fg_b, cmd in buttons:
            tk.Button(af, text=txt, bg=bg_b, fg=fg_b, activebackground=fg_b,
                      activeforeground=bg_b, font=("Consolas", 11),
                      relief="flat", cursor="hand2", command=cmd
                      ).pack(fill="x", pady=3, ipady=5)

        # Log
        lf = tk.Frame(self.root, bg=bg)
        lf.pack(fill="both", expand=True, padx=20, pady=5)
        tk.Label(lf, text="Log", bg=bg, fg=accent,
                 font=("Consolas", 11, "bold")).pack(anchor="w")
        self.log_box = tk.Text(lf, height=7, bg="#181825", fg="#a6adc8",
                               font=("Consolas", 9), state="disabled",
                               relief="flat", insertbackground=fg)
        self.log_box.pack(fill="both", expand=True)

    def _log(self, msg):
        ts = time.strftime("%H:%M:%S")
        def _append():
            self.log_box.configure(state="normal")
            self.log_box.insert("end", f"[{ts}] {msg}\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")

        if threading.current_thread() is threading.main_thread():
            _append()
        else:
            self.root.after(0, _append)

    def _refresh(self):
        def _worker():
            try:
                data = sensors.get_all_metrics()
                self.var_temp.set(f"Temp:     {data['temp']:.1f} °C")
                self.var_lux.set( f"Licht:    {data['lux']:.1f} lx")
                self.var_hum.set( f"Feucht.:  {data['hum']:.1f} %")
                self.var_time.set(f"Zeit:     {time.strftime('%H:%M:%S')}")
                # Do not overwrite the LCD while Flappy Bird is active.
                if not self._flappy_mode and not self.game.active:
                    display_manager.update_lcd(data)
                # Alarm-Logik
                if data["temp"] >= config.TEMP_CRIT:
                    self.lbl_status.config(text="● KRITISCH", fg="#f38ba8")
                    self._log(f"ALARM: Temperatur kritisch! {data['temp']}°C")
                elif data["temp"] >= config.TEMP_WARN:
                    self.lbl_status.config(text="● WARNUNG", fg="#f9e2af")
                    self._log(f"Warnung: Temperatur {data['temp']}°C")
                else:
                    self.lbl_status.config(text="● OK", fg="#a6e3a1")
                self._log("Sensordaten aktualisiert.")
            except Exception as e:
                self._log(f"Fehler: {e}")
        threading.Thread(target=_worker, daemon=True).start()

    def _auto_update(self):
        self._refresh()
        self.root.after(10000, self._auto_update)

    def _toggle_segment(self):
        self.segment_mode = "date" if self.segment_mode == "time" else "time"
        threading.Thread(target=display_manager.show_on_segment,
                         args=(self.segment_mode,), daemon=True).start()
        self._log(f"Segmentanzeige: {self.segment_mode}")

    def _test_alarm(self):
        self._log("Test-Alarm gesendet.")
        threading.Thread(target=alarm_system.play_alarm, daemon=True).start()

    def _play_march(self):
        self._log("Imperial March gestartet!")
        threading.Thread(target=alarm_system.play_imperial_march, daemon=True).start()

    def _nfc_reset(self):
        def _worker():
            self._log("Warte auf NFC-Karte...")
            if self.security.check_card():
                self._log("NFC OK – System zurückgesetzt.")
                self.root.after(0, lambda: messagebox.showinfo(
                    "Reset", "System erfolgreich zurückgesetzt!"))
            else:
                self._log("NFC: Zugang verweigert.")
                self.root.after(0, lambda: messagebox.showerror(
                    "Fehler", "Keine gültige NFC-Karte erkannt!"))
        threading.Thread(target=_worker, daemon=True).start()

    def _easter_egg(self):
        if self._game_thread and self._game_thread.is_alive():
            self._log("Flappy Bird läuft bereits.")
            return

        self._flappy_mode = True
        self._game_stop.clear()
        self._game_thread = threading.Thread(target=self._run_flappy_on_lcd, daemon=True)
        self._game_thread.start()
        messagebox.showinfo(
            "Easter Egg",
            "Flappy Bird läuft auf dem LCD!\n"
            "Leertaste = Flap | ESC = Beenden",
        )

    def _run_flappy_on_lcd(self):
        ipcon = IPConnection()
        try:
            self._log("Flappy: Verbinde mit LCD...")
            ipcon.connect(config.HOST, config.PORT)
            lcd = BrickletLCD128x64(config.UIDS["LCD"], ipcon)
            lcd.clear_display()
            lcd.write_line(0, 0, "Flappy Initialisiere")
            self.game.set_lcd(lcd)
            self.game.start()
            self._log("🐦 Flappy Bird gestartet.")

            while self.game.active and not self._game_stop.is_set():
                self.game.tick()
                time.sleep(0.2)

            self.game.stop()
            self._flappy_mode = False
            self._log("Flappy Bird beendet.")
            self.root.after(0, self._refresh)
        except Exception as e:
            self._flappy_mode = False
            self._log(f"Flappy Bird Fehler: {e}")
        finally:
            try:
                ipcon.disconnect()
            except Exception:
                pass

    def _flap_key(self, _event=None):
        if self.game.active:
            self.game.flap()

    def _stop_game_key(self, _event=None):
        if self.game.active:
            self._game_stop.set()
        self._flappy_mode = False

    def _on_close(self):
        self._game_stop.set()
        self._flappy_mode = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminDashboard(root)
    root.mainloop()
