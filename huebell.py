from ring_doorbell import Ring, Auth
import json
import datetime
import pytz

# Get log in credentials from config file
with open('config.json') as config_file:
    data = json.load(config_file)

RING_USERNAME = data['RING_USER']
RING_PASSWORD = data['RING_PASS']

# Sign in to Ring
auth = Auth("huebell/v1")
auth.fetch_token(RING_USERNAME, RING_PASSWORD)
ring = Ring(auth)
ring.update_data()

# Load doorbell and recent events
devices = ring.devices()
doorbell = devices['doorbots'][0]

print("\nLatest events:\n")
for event in doorbell.history(5):
    print(event['id'])
    print(event['kind'])
    print(event['created_at'])
    print('-'*30, "\n")

# Check for doorbell ding events
print("Checking the doorbell...\n")

utc = pytz.UTC
now = utc.localize(datetime.datetime.now())
alert = False

while not alert:
    for event in doorbell.history(1, kind='ding'):
        if event and event['created_at'] > now:
            print("*"*30, "Someone is at the door!", "*"*30, "", sep="\n")
            print(event)
            doorbell.recording_download(doorbell.history(limit=10, kind='ding')[0]['id'],
                                        filename='last_ding.mp4',
                                        override=True)
            print("\nLatest alert video downloaded")
            alert = True
