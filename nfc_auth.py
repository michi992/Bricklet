import time
import threading
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_nfc import BrickletNFC
import config

class SecurityManager:
    def __init__(self):
        self.admin_tag_id = {}  # {"ID-String": "Rolle"}
        self._scanned_id = None
        self._scan_complete = threading.Event()
        self._current_state = None

    def _cb_reader_state_changed(self, state, idle):
        """Callback für Statusänderungen des NFC Bricklets."""
        self._current_state = state
        if state == BrickletNFC.READER_STATE_REQUEST_TAG_ID_READY:
            # Tag wurde erfolgreich gelesen
            pass
        elif state == BrickletNFC.READER_STATE_REQUEST_TAG_ID_ERROR:
            print("NFC Fehler: Tag konnte nicht gelesen werden.")
            self._scan_complete.set()

    def get_raw_id(self, timeout=10):
        """Liest eine Karten-ID ein, ohne sie zu bewerten."""
        ipcon = IPConnection()
        nfc = None
        try:
            ipcon.connect(config.HOST, config.PORT)
            ipcon.set_timeout(5000) # 5 Sekunden Timeout
            nfc = BrickletNFC(config.UIDS["NFC"], ipcon)
            
            # Registriere Callback für Statusänderungen
            nfc.register_callback(nfc.CALLBACK_READER_STATE_CHANGED, self._cb_reader_state_changed)
            
            # Starte den Lesevorgang
            nfc.reader_request_tag_id()
            
            start_time = time.time()
            while (time.time() - start_time) < timeout:
                # Prüfe den aktuellen Status
                state, _ = nfc.reader_get_state()
                self._current_state = state
                
                if state == BrickletNFC.READER_STATE_REQUEST_TAG_ID_READY:
                    # Tag-ID erfolgreich gelesen
                    ret = nfc.reader_get_tag_id()
                    # Konvertiere die ID in einen String, z.B. "[1, 2, 3, 4]"
                    self._scanned_id = str(list(ret.tag_id[:ret.tag_id_length]))
                    return self._scanned_id
                elif state == BrickletNFC.READER_STATE_REQUEST_TAG_ID_ERROR:
                    # Fehler beim Lesen
                    print("NFC: Fehler beim Lesen der Karte.")
                    break
                time.sleep(0.1)
                
        except Exception as e:
            print(f"NFC Hardware Fehler: {e}")
        finally:
            try:
                if nfc:
                    # Stoppe den Lesevorgang
                    nfc.reader_request_tag_id() # Erneuter Aufruf, um den Modus zu beenden (laut API)
            except:
                pass
            try:
                ipcon.disconnect()
            except:
                pass
            self._scan_complete.clear()
        return None

    def check_card(self):
        """Prüft ob die gescannte Karte Admin- oder Techniker-Rechte hat."""
        rid = self.get_raw_id()
        if rid and rid in self.admin_tag_id:
            return self.admin_tag_id[rid] in ["Admin", "Techniker"]
        return False