from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_ptc_v2 import BrickletPTCV2
from tinkerforge.bricklet_ambient_light_v3 import BrickletAmbientLightV3
from tinkerforge.bricklet_humidity_v2 import BrickletHumidityV2
import config

def get_all_metrics():
    ipcon = IPConnection()
    try:
        ipcon.connect(config.HOST, config.PORT)
        ptc = BrickletPTCV2(config.UIDS["PTC"], ipcon)
        al = BrickletAmbientLightV3(config.UIDS["AMBIENT"], ipcon)
        hum = BrickletHumidityV2(config.UIDS["HUMIDITY"], ipcon)
        return {
            "temp": ptc.get_temperature() / 100.0,
            "lux": al.get_illuminance() / 100.0,
            "hum": hum.get_humidity() / 10.0
        }
    except Exception as e:
        print(f"Sensorfehler: {e}")
        return {"temp": 0.0, "lux": 0.0, "hum": 0.0}
    finally:
        ipcon.disconnect()

if __name__ == "__main__":
    data = get_all_metrics()
    print(f"Temp: {data['temp']}°C | Licht: {data['lux']} lx | Feuchte: {data['hum']}%")
