import time
import json
import os
from tinkerforge.ip_connection import IPConnection
# WICHTIG: Nutze BrickletNFCV2 für die aktuelle Hardware-Generation
from tinkerforge.bricklet_nfc_v2 import BrickletNFCV2 
import config

TAGS_FILE = "authorized_tags.json"

def _load_tags() -> dict:
    if os.path.exists(TAGS_FILE):
        try:
            with open(TAGS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_tags(tags: dict):
    with open(TAGS_FILE, "w") as f:
        json.dump(tags, f, indent=2)

def get_all_tags() -> dict:
    return _load_tags()

def add_tag(tag_id: str, name: str = "Unbekannt"):
    tags = _load_tags()
    tags[tag_id] = name
    _save_tags(tags)

def remove_tag(tag_id: str):
    tags = _load_tags()
    if tag_id in tags:
        del tags[tag_id]
        _save_tags(tags)

class SecurityManager:
    def __init__(self):
        self.authorized = False
        self._last_tag = None

    def check_card(self) -> bool:
        ipcon = IPConnection()
        try:
            ipcon.connect(config.HOST, config.PORT)
            
            # Initialisierung des NFC 2.0 Bricklets
            nfc = BrickletNFCV2(config.UIDS["NFC"], ipcon)
            
            print("[NFC] Suche nach Tag...")
            # Startet den Scan-Vorgang
            nfc.reader_request_tag_id()
            
            # Kurze Pause, damit die Hardware Zeit zum Reagieren hat
            time.sleep(0.5)
            
            # Status abfragen
            state, _, _ = nfc.get_reader_state()
            
            # Prüfen, ob ein Tag erfolgreich gelesen wurde
            if state == BrickletNFCV2.READER_STATE_REQUEST_TAG_ID_READY:
                # In V2 liefert get_tag_id() direkt die Liste der Bytes zurück
                ret = nfc.get_tag_id()
                tag_id = ":".join(f"{b:02X}" for b in ret)
                self._last_tag = tag_id
                
                print(f"[NFC] Tag-ID gefunden: {tag_id}")
                tags = _load_tags()
                
                if tag_id in tags:
                    self.authorized = True
                    print(f"[NFC] Zugang gewährt: {tags[tag_id]}")
                    return True
                else:
                    self.authorized = False
                    print("[NFC] Zugang verweigert! (Unbekannter Tag)")
                    return False
            else:
                print("[NFC] Kein Tag in Reichweite oder Fehler.")
                return False

        except Exception as e:
            print(f"[NFC] Fehler während der Kommunikation: {e}")
            return False
        finally:
            try:
                ipcon.disconnect()
            except:
                pass

    def get_last_tag(self):
        return self._last_tag

    def revoke(self):
        self.authorized = False

if __name__ == "__main__":
    # Test-Lauf
    sm = SecurityManager()
    print("--- Bitte Karte an das NFC-Modul halten ---")
    result = sm.check_card()
    print("-" * 40)
    print(f"Ergebnis: {'ERLAUBT' if result else 'ABGELEHNT'}")
    if sm.get_last_tag():
        print(f"Letzter gelesener Tag: {sm.get_last_tag()}")