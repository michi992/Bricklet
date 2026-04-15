import time
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_nfc import BrickletNFC
import config

class SecurityManager:
    def __init__(self):
        self.admin_tag_id = {} # Wird von der GUI gefüllt: {"ID": "Rolle"}
        self._scanned_id = None

    def get_raw_id(self, timeout=10):
        """Liest eine ID ein, ohne sie zu bewerten. Ideal für neue Karten."""
        ipcon = IPConnection()
        try:
            ipcon.connect(config.HOST, config.PORT)
            nfc = BrickletNFC(config.UIDS["NFC"], ipcon)
            
            # Karte anfordern
            nfc.request_tag_id(BrickletNFC.TAG_TYPE_MIFARE_CLASSIC)
            time.sleep(0.5)
            
            ret = nfc.get_tag_id()
            if ret.tag_id:
                # Erstellt einen String aus der ID-Liste für die GUI
                raw_id = list(ret.tag_id[:ret.tag_id_length])
                return str(raw_id)
        except Exception as e:
            print(f"NFC Hardware Fehler: {e}")
        finally:
            ipcon.disconnect()
        return None

    def check_card(self):
        """Alte Funktion für den Auth-Check Button (Kompatibilität)."""
        rid = self.get_raw_id()
        if rid and rid in self.admin_tag_id:
            # Nur Admin und Techniker dürfen passieren
            return self.admin_tag_id[rid] in ["Admin", "Techniker"]
        return False