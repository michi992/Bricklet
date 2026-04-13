from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_nfc import BrickletNFC
import config
import time

class SecurityManager:
    def __init__(self):
        self.authorized = False
        # Hier die ID deiner NFC-Karte eintragen (erst einmal scannen & ID ablesen)
        self.admin_tag_id = None  # z.B. [4, 8, 15, 16, 23, 42]
        self._scanned_id = None

    def _cb_reader_state_changed(self, state, idle, nfc_ref):
        if state == BrickletNFC.READER_STATE_REQUEST_TAG_ID_READY:
            ret = nfc_ref.reader_get_tag_id()
            self._scanned_id = list(ret.tag_id)

    def check_card(self):
        ipcon = IPConnection()
        try:
            ipcon.connect(config.HOST, config.PORT)
            nfc = BrickletNFC(config.UIDS["NFC"], ipcon)
            self._scanned_id = None

            nfc.register_callback(
                BrickletNFC.CALLBACK_READER_STATE_CHANGED,
                lambda s, i: self._cb_reader_state_changed(s, i, nfc)
            )
            nfc.set_mode(BrickletNFC.MODE_READER)
            nfc.reader_request_tag_id()
            time.sleep(1.0)

            if self.admin_tag_id is None:
                # Erstes Scannen: ID registrieren
                self.admin_tag_id = self._scanned_id
                self.authorized = True
                print(f"Admin-Karte registriert: {self.admin_tag_id}")
            elif self._scanned_id == self.admin_tag_id:
                self.authorized = True
                print("NFC: Zugang gewährt.")
            else:
                self.authorized = False
                print("NFC: Zugang verweigert.")
        except Exception as e:
            print(f"NFC-Fehler: {e}")
            self.authorized = False
        finally:
            ipcon.disconnect()
        return self.authorized
