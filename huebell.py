from ring_doorbell import Ring, Auth
from phue import Bridge
import json
from time import sleep
import sys

# Get config variables from config file
with open('config.json') as config_file:
    data = json.load(config_file)

# Connect to Hue Bridge
b = Bridge(data['HUE_IP'])

# First time need to press the button on the Bridge and connect (within 30 seconds)
# b.connect()

lights = []
hue_lights = b.lights

print("[Hue] Connected")

# Sign in to Ring
RING_USERNAME = data['RING_USER']
RING_PASSWORD = data['RING_PASS']
auth = Auth("huebell/v1")
auth.fetch_token(RING_USERNAME, RING_PASSWORD)
ring = Ring(auth)
ring.update_data()
print("[Ring] Connected")

# Load doorbell
devices = ring.devices()
doorbell = devices['doorbots'][0]


def flash_lights():
    # Get current status of all lights
    for l in hue_lights:
        light = {
            'name': l.name,
            'light': l,
            'status': b.get_light(l.name, 'on'),
            'bright': b.get_light(l.name, 'bri')
        }
        lights.append(light)

    # Turn on hallway light
    b.set_light(data['HUE_LIGHT'], {'on': True, 'bri': 250})

    # Flash all lights
    for light in lights:
        if light['name'] != data['HUE_LIGHT']:
            b.set_light(light['name'], 'on', True)
            b.set_light(light['name'], 'bri', 250)
    sleep(3)
    for light in lights:
        if light['name'] != data['HUE_LIGHT']:
            b.set_light(light['name'], 'bri', light['bright'])
            if light['status'] == False:
                b.set_light(light['name'], 'on', False)


# Check for doorbell ding events
print("Checking for doorbell...\n")
ding = False

try:
    while not ding:
        ring.update_dings()
        alert = ring.active_alerts()
        if alert and alert[0]['kind'] == 'ding':
            print("*"*30, "Someone is at the door!", "*"*30, "", sep="\n")
            flash_lights()
            event = doorbell.history(limit=1, kind='ding')[0]
            print(event)
            doorbell.recording_download(doorbell.history(limit=10, kind='ding')[0]['id'],
                                        filename='last_ding.mp4',
                                        override=True)
            print("\n[Ring] Latest alert video downloaded")

            # Comment out line below for continuous loop even after doorbell rung
            ding = True

except KeyboardInterrupt:
    print("\nClosing down")
    sys.exit(0)
