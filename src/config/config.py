import os

TOKEN = os.environ.get('BOT_TOKEN')
CHATID = int(os.environ.get('CHAT_ID'))

CAM_USER = os.environ.get('CAM_USER')
CAM_PASSWORD = os.environ.get('CAM_PASSWORD')
FTP_PASSWORD = os.environ.get('CAM_FTP_PASSWORD')

# [IP_ADDRESS, NICKNAME, SENSITIVITY]
CAMERAS = [
    [os.environ.get('CAM_IP'), os.environ.get('CAM_NAME'), os.environ.get('CAM_SENSITIVITY')],
    # ["192.168.1.11", "camera_kitchen", "low"],
]

# Secondary token are used to bypass group chat api limit rate
TOKEN_ALL = [
    TOKEN,
    # "<<<TOKEN_SECONDARY>>>",
    # "<<<TOKEN_SECONDARY>>>",
]

STATE_CHANGE_DELAY = 3

SNAPSHOT_TIMEOUT = 6
SETTINGS_TIMEOUT = 18
MEDIA_RETENTION = 0  # Delete photo/video after x days 0 for instant deletion
VIDEO_COMPRESSION = False
SNAPSHOT_TIMESTAMP_WATERMARK = True

PROJECT_PATH = './'
SOUND_SAVE_PATH = "%s/sound" % PROJECT_PATH

SOUND_SAVE_PATH = (SOUND_SAVE_PATH + "/").replace("//",
                                                  "/")  # Make sure that a leading / is always present no matter what

AUDIO_TEMP_FILE = "audio_voice_file.mp4"

MEDIA_SAVE_PATH = "%s/recording" % PROJECT_PATH

MEDIA_SAVE_PATH = (MEDIA_SAVE_PATH + "/").replace("//",
                                                  "/")  # Make sure that a leading / is always present no matter what

# Add padding to match the camera with the longest name
maxlen = 0
for cam in CAMERAS:
    if len(cam[1]) > maxlen:
        maxlen = len(cam[1])

for cam in CAMERAS:
    if len(cam[1]) < maxlen:
        cam[1] += (maxlen - len(cam[1])) * " "

# Use the right one or create one for your language

from config.locale_EN import *

TURNING_ON("123")  # To suppress PyCharm import warning
