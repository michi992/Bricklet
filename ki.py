# Import necessary libraries
import data
import speech_recognition as sr
from time import ctime
import time
import os
import pandas as pd # Import pandas for DataFrame functionality
import ipadresse
from collections import deque
from dataclasses import dataclass, field
from tinkerforge.ip_connection import IPConnection
from typing import Optional
import threading
from multiprocessing.managers import BaseManager
from vector_database import VectorDatabase # Ensure this module is defined elsewhere



@dataclass
class Slot:
    ip:str
    port:int
    uid: Optional[str] = None # Optional UID for specific device targeting
    data_queue: deque = field(default_factory=deque) # Queue to hold incoming data
    

class: IPPortPool:
    def __init__(self, network: str, port: list[int]):
        hosts = list(ipaddress.ip_network(network, strict=false).hosts())
        #Add all IPs and ports to the pool
        self.slots = dict[tuple, Slot] = {}
        for ip in hosts:
            for  port in ports:
                key = (str(ip), port)
                self.slots[key] = Slot(ip=str(ip), port=port)
                
        self.available: deque[tuple] = deque(self.slots.keys()) # Queue to manage available slots
        self.uid_map: dict[str, Slot] = {} # Map UID to Slot for quick lookup
        self.lock = threading.Lock() # Lock for thread-safe operations
    def acquire(self, uid: Optional[str] = None) -> Optional[Slot]:
        with self.lock:
            if uid in self.uid_map:
                return self.uid_map[uid]
            if not self.available:
                return None # No available slots
            key = self.available.popleft()
            slot = self.slots[key]
            slot.uid = uid
            sel.uid_map[uid] = slot
            return slot
            
    def release(self, uid: str):
        with self.lock:
            if uid in self.uid_map:
                slot = self.uid_map.pop(uid)
                slot.uid = None
                self.available.append((slot.ip, slot.port))
                
    def get_by_uid(self, uid: str) -> Optional[Slot]:
        with self.lock:
            return self.uid_map.get(uid)
        
    def status(self):
        with self.lock:
            print(f"Verfügbar: {len(self.available)}, Belegt: {len(self.uid_map)}")
            for uid, slot in self.uid_map.items():
                print(f"UID: {uid}, IP: {slot.ip}, Port: {slot.port}")

data = ("vector.py")

pool =IPPortPool(
    network="172.20.10.242"    
    ports=[4223]
    files[
        
    ]


def recordAudio():
# Record Audio
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Sag was!")
        audio = r.listen(source)

# Speech recognition using Google Speech Recognition

#try:
# Uses the default API key
# To use another API key: `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
#data = r.recognize_google(audio)
try:
    # Speech recognition using Google Speech Recognition
    data = r.recognize_google(audio)
    print("You said: " + data)
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e))

#takes parameter from the under functions of temp-fühl.u-abgage.py and processes it to give a response to the user
def jarvis(data):#-
if "wie gehts" in data:#-
print("Gut")#-
if "Uhrzeit" in data:#-
print(ctime())#-
if "Wo sind wir?" in data:#-
data = data.split(" ")#-
location = data[2]#-
print("Wir sind bei " + location)#-
os.system("chromium-browser https://www.google.nl/maps/place/" + location)#-
data = data.split("")
if "Temparatur" in data:#-
print("Die Temparatur beträgt" + str(temperature/100.0) + " Grad Celsius")#-
if "Datenbank" in data:#-


# Initialize Vector Database
db = VectorDatabase()

# Function to retrieve information from Vector Database
def retrieve_info(query):
results = db.query(query)

# Function to generate response based on retrieved information
def generate_response(info):
response = generate_text(f"Here is the information I found: {info}")


# Main function
def main():
audio_file = "audio.wav"
text = speech_to_text(audio_file) # Ensure this function is defined elsewhere
print(f"Transcript: {text}")
text_to_speech(text) # Ensure this function is defined elsewhere

# Retrieve information from Vector Database
info = retrieve_info(text)
