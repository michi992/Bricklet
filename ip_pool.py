import ipaddress
from collections import deque
import threading
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Slot:
    ip: str
    port: int
    uid: Optional[str] = None
    data_queue: deque = field(default_factory=deque)

class IPPortPool:
    def __init__(self, network: str, ports: list):
        hosts = list(ipaddress.ip_network(network, strict=False).hosts())
        self.slots = {}
        for ip in hosts:
            for port in ports:
                key = (str(ip), port)
                self.slots[key] = Slot(ip=str(ip), port=port)
        self.available = deque(self.slots.keys())
        self.uid_map = {}
        self.lock = threading.Lock()

    def get_slot(self, uid: str = None) -> Optional[Slot]:
        with self.lock:
            if uid and uid in self.uid_map:
                return self.uid_map[uid]
            if self.available:
                key = self.available.popleft()
                slot = self.slots[key]
                if uid:
                    slot.uid = uid
                    self.uid_map[uid] = slot
                return slot
        return None

    def release_slot(self, uid: str):
        with self.lock:
            if uid in self.uid_map:
                slot = self.uid_map.pop(uid)
                slot.uid = None
                self.available.append((slot.ip, slot.port))
