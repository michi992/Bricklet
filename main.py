"""
Serverraum-Überwachung – Hauptprogramm (ohne GUI)
Startet mit: python main.py
"""
import time
import threading
import config
import sensors
import display_manager
import alarm_system

def monitoring_loop():
    segment_mode = "time"
    print("Serverraum-Überwachung gestartet. Strg+C zum Beenden.")
    while True:
        try:
            data = sensors.get_all_metrics()
            print(f"[{time.strftime('%H:%M:%S')}] "
                  f"Temp: {data['temp']:.1f}°C | "
                  f"Licht: {data['lux']:.1f}lx | "
                  f"Feucht: {data['hum']:.1f}%")

            display_manager.update_lcd(data)
            display_manager.show_on_segment(segment_mode)

            if data["temp"] >= config.TEMP_CRIT:
                print("!!! KRITISCHER ALARM: Temperatur zu hoch !!!")
                alarm_system.play_imperial_march()
            elif data["temp"] >= config.TEMP_WARN:
                print("!!! WARNUNG: Temperatur erhöht !!!")
                alarm_system.play_alarm()

        except KeyboardInterrupt:
            print("Programm beendet.")
            break
        except Exception as e:
            print(f"Fehler: {e}")

        time.sleep(5)

if __name__ == "__main__":
    monitoring_loop()
