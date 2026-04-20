import time
import threading
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_nfc import BrickletNFC
import config

class SecurityManager:
    def __init__(self):
        self.admin_tag_id = {}  # {"ID-String": "Rolle"}
        self._scanned_id = None
        self._on_card_callback = None  # Wird von gui_control gesetzt
        self._monitor_thread = None
        self._monitoring = False

    def set_card_callback(self, callback):
        """
        Registriert eine Funktion die aufgerufen wird wenn eine Karte erkannt wird.
        callback(role: str, card_id: str)
        """
        self._on_card_callback = callback

    def start_monitor(self):
        """Startet dauerhaften NFC-Monitor im Hintergrund."""
        if self._monitoring:
            return
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def stop_monitor(self):
        self._monitoring = False

    def _monitor_loop(self):
        """Dauerhafter Loop: erkennt Karten und ruft Callback auf."""
        last_id = None
        last_trigger = 0

        while self._monitoring:
            try:
                cid = self.get_raw_id(timeout=2)
                now = time.time()

                if cid and cid != last_id and (now - last_trigger) > 3:
                    last_id = cid
                    last_trigger = now
                    role = self.admin_tag_id.get(cid, None)
                    print(f"[NFC Monitor] Karte: {cid} -> Rolle: {role}")
                    if role and self._on_card_callback:
                        self._on_card_callback(role, cid)
                elif not cid:
                    last_id = None  # Karte wurde entfernt

            except Exception as e:
                print(f"[NFC Monitor] Fehler: {e}")
                time.sleep(1)

    def get_raw_id(self, timeout=10):
        """Liest eine Karten-ID ein, ohne sie zu bewerten."""
        ipcon = IPConnection()
        nfc = None
        try:
            ipcon.connect(config.HOST, config.PORT)
            nfc = BrickletNFC(config.UIDS["NFC"], ipcon)
            nfc.reader_request_tag_id()

            start = time.time()
            while (time.time() - start) < timeout:
                state, _ = nfc.reader_get_state()
                if state == BrickletNFC.READER_STATE_REQUEST_TAG_ID_READY:
                    ret = nfc.reader_get_tag_id()
                    self._scanned_id = str(list(ret.tag_id))
                    return self._scanned_id
                elif state == BrickletNFC.READER_STATE_REQUEST_TAG_ID_ERROR:
                    break
                time.sleep(0.1)

        except Exception as e:
            print(f"NFC Hardware Fehler: {e}")
        finally:
            try:
                ipcon.disconnect()
            except:
                pass
        return None

    def check_card(self):
        """Prüft ob die gescannte Karte Admin- oder Techniker-Rechte hat."""
        rid = self.get_raw_id()
        if rid and rid in self.admin_tag_id:
            return self.admin_tag_id[rid] in ["Admin", "Techniker"]
        return False

    def get_role(self, card_id):
        """Gibt die Rolle einer Karte zurück oder None."""
        return self.admin_tag_id.get(card_id, None)