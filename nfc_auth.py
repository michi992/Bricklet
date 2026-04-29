import time
import threading
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_nfc import BrickletNFC
import config


class SecurityManager:

    def __init__(self):
        self.admin_tag_id = {}  # {"ID-String": "Rolle"}
        self._scanned_id = None
        self._card_callback = None
        self._monitor_running = False

    def set_card_callback(self, callback):
        """Setzt den Callback der aufgerufen wird, wenn eine bekannte Karte erkannt wird."""
        self._card_callback = callback

    def start_monitor(self):
        """Startet den dauerhaften NFC-Monitor-Loop im Hintergrund."""
        if self._monitor_running:
            return
        self._monitor_running = True
        threading.Thread(target=self._monitor_loop, daemon=True).start()

    def stop_monitor(self):
        """Stoppt den Monitor-Loop."""
        self._monitor_running = False

    def _monitor_loop(self):
        """Dauerhafter Loop: sucht ständig nach neuen NFC-Tags."""
        while self._monitor_running:
            try:
                rid = self.get_raw_id(timeout=5)
                if rid and rid in self.admin_tag_id:
                    role = self.admin_tag_id[rid]
                    if self._card_callback:
                        self._card_callback(role, rid)
            except Exception as e:
                print(f"[NFC Monitor] Fehler: {e}")
            time.sleep(1)

    def get_raw_id(self, timeout=10):
        """Liest eine Karten-ID ein und gibt sie als String zurück."""
        ipcon = IPConnection()
        nfc = None
        try:
            ipcon.connect(config.HOST, config.PORT)
            nfc = BrickletNFC(config.UIDS["NFC"], ipcon)

            # *** FIX: Bricklet muss zuerst in den Reader-Modus versetzt werden ***
            nfc.set_mode(BrickletNFC.MODE_READER)
            time.sleep(0.25)  # warten bis Modus aktiv

            # Lesevorgang starten
            nfc.reader_request_tag_id()

            start_time = time.time()
            while (time.time() - start_time) < timeout:
                state, _ = nfc.reader_get_state()

                if state == BrickletNFC.READER_STATE_REQUEST_TAG_ID_READY:
                    ret = nfc.reader_get_tag_id()
                    scanned_id = str(list(ret.tag_id[:ret.tag_id_length]))
                    return scanned_id

                elif state == BrickletNFC.READER_STATE_REQUEST_TAG_ID_ERROR:
                    # Kein Tag in Reichweite – erneut versuchen
                    nfc.reader_request_tag_id()

                time.sleep(0.1)

        except Exception as e:
            print(f"[NFC] Hardware Fehler: {e}")
        finally:
            try:
                # Modus zurücksetzen auf OFF (kein erneutes reader_request_tag_id!)
                if nfc:
                    nfc.set_mode(BrickletNFC.MODE_OFF)
            except:
                pass
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
