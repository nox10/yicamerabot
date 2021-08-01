from TelegramNotifyer import Telegram
from DummyNotifyer import Dummy

from YiHomeCamera import YiCam
from IPCam import IPCam
from SaveVideo import SaveVideo

from TelegramChat import TelegramChat

from config import *

import telegram
import time
import os

from telegram import *
from telegram.ext import *


class main:

    def __init__(self):
        #polymorphism (?)
        self.notifyer = SaveVideo(Telegram(), MEDIA_SAVE_PATH)
        self.camera = YiCam
        self.cameraStatus = ""

        self.cams = []

        for CAMERA in CAMERAS:
            self.cams.append(IPCam(self.notifyer, self.camera(CAMERA[0]), CAMERA[1]))


        botUpdater = Updater(TOKEN)
        dispatcher = botUpdater.dispatcher

        dispatcher.add_handler(MessageHandler(Filters.regex(ONLINE_LIST), self.updateStatus))


        #Make them start at the same time (more or less)
        for cam in self.cams:
            cam.start()
            TelegramChat(cam, dispatcher, self.updateStatus)


        botUpdater.start_polling()

        while True:
            self.deleteOldMedia(MEDIA_SAVE_PATH, 7)
            self.updateStatus(force = False)
            time.sleep(10)


    def deleteOldMedia(self, path, olderThanDays):
        current_time = time.time()
        for f in os.listdir(path):
            f = path + f
            creation_time = os.path.getctime(f)
            if (current_time - creation_time) // (24 * 3600) >= olderThanDays:
                os.unlink(f)
                print('{} removed'.format(f))


    def updateStatus(self, update: Update = None, context: CallbackContext = None, force = True):
        stat = self.getOnlineStatus()
        if stat != self.cameraStatus or force:
            self.cameraStatus = stat
            try:
                self.notifyer.sendMessage(CAMERA_STATUS, self.cameraStatus, reply_markup = self.generateKeyboard())
            except Exception as e:
                print(e) #If too many messages have been sent, an exception can occur #FIXME


    def generateKeyboard(self):
        keyboard = []
        for cam in self.cams:
            if cam.isOnline():
                status = TURNING_ON if not cam.sendNotification() else TURNING_OFF
                keyboard.append([f"{cam.getName()} {IMAGE}", f"{status} {cam.getName()}"])

        keyboard.append([ONLINE_LIST])
        return keyboard


    def getOnlineStatus(self):
        msg = ""
        for cam in self.cams:
            status = STATUS_ONLINE if cam.isOnline() else STATUS_OFFLINE
            notification = INTENT_YES if cam.sendNotification() else INTENT_NO
            msg += ONLINE_STATUS_MSG(cam.name, status, notification)

        return msg



if __name__ == "__main__":
    main()