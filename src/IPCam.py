import threading
import time

import config.config as config


class IPCam:

    def __init__(self, Notifyer, Camera, name, enabled=True, notification=True):

        self.log = True
        self.recording = False
        self.startTime = time.time()
        self.name = name
        self.Notifyer = Notifyer
        self.Camera = Camera
        self.recordingSize = -1
        self.counter = 1
        self.enabled = enabled
        self.notification = notification

        self.__printLog("Created")

    def start(self):
        self.startTime = time.time()
        self.__printLog("Starting...")
        self.update()

    def enableCam(self, enabled):
        self.__printLog(f"Set camera to {enabled}")
        if self.Camera.switchCamera(enabled):
            self.enabled = enabled
            return True
        return False

    def sendNotification(self):
        return self.notification

    def setNotification(self, sendNotificaton):
        self.notification = sendNotificaton

    def isEnabled(self):
        return self.enabled

    def isOnline(self):
        return self.Camera.isConnected()

    def getName(self):
        return self.name

    def textToSpeech(self, text):
        if self.Camera.isConnected():
            self.Camera.textToSpeech(text)

    def sendSound(self, filename):
        if self.Camera.isConnected():
            self.Camera.sendSound(filename)

    def update(self):
        try:
            self.updateCycle()
        except Exception as e:
            print(f"Update error exception: {e}")

        # Call itself after x sec
        thread = threading.Timer(0.5, self.update)
        thread.daemon = True
        thread.start()

    def updateCycle(self):
        if self.Camera.isConnected():
            try:
                if self.counter % 1 == 0:
                    self.movementCheck()
                if self.counter % 3 == 0:
                    self.sendVideo()
                if self.counter % 7 == 0:
                    self.unstuckTmpVideo()
                if self.counter % 21 == 0:
                    self.__printLog("RUNNING")
            except Exception as e:
                print(f"Camera disconnected exception: {e}")
                self.Camera.disconnect()

        elif self.counter % 4 == 0:
            status = "SUCCESS" if self.Camera.connectFTP() else "FAIL"
            self.__printLog(f"Reconnecting result: {status}")

        self.counter = (self.counter + 1) % 100

    def movementCheck(self):
        if self.Camera.isRecording():
            self.__printLog(f"Camera is recording size {round(self.Camera.getTmpVideoSize() / (1024 * 1024.0), 2)} MB")
            if not self.recording:
                self.__printLog("Trigger video recording")
                self.__movementTriggered()
                self.recording = True
        else:
            if self.recording:
                self.__printLog("Recording ended")
            self.recording = False

    def unstuckTmpVideo(self):
        if self.Camera.isRecording():
            size = self.Camera.getTmpVideoSize()
            if self.recordingSize != -1:
                if self.recordingSize == size:
                    self.__printLog(f" #### UNSTUCK STUCK VIDEO size = {round(size / (1024 * 1024.0), 2)} MB")
                    self.Camera.removeTmpVideo()
            self.recordingSize = size
            self.__printLog(f"Check size is {round(self.recordingSize / (1024 * 1024.0), 2)} MB")

    def sendVideo(self):
        if self.isOnline():
            if self.isEnabled():
                self.Camera.callbackVideoList(self.name, self.Notifyer.sendVideo, notification=self.notification)
            else:
                self.Camera.callbackVideoList()
        else:
            print("Calling sendVideo when offline")

    def sendImage(self, caption="", force=False):
        if self.isEnabled():
            try:
                res = self.Camera.getImage(highQuality=not config.VIDEO_COMPRESSION,
                                           timeStamp=config.SNAPSHOT_TIMESTAMP_WATERMARK)
            except Exception as e:
                self.__printLog(f"SEND IMAGE ISSUE EX: {e}")
                res = False
            if res:
                notification = True if force else self.notification
                self.__printLog("Send photo")
                self.Notifyer.sendPhoto(res,
                                        # self.name +
                                        caption, notification=notification)
                return True

            self.__sendMessage(config.CAMERA_OFFLINE)
        else:
            self.__sendMessage(config.CAMERA_DISABLED)
        return False

    def __movementTriggered(self):
        # self.__sendMessage(CONFIG.MOTION_DETECTED)
        # self.sendImage()
        time.sleep(0.5)
        self.sendImage(config.MOTION_DETECTED)

    def __printLog(self, msg):
        if self.log:
            timePassed = int(time.time() - self.startTime)
            print(f"{self.name} {timePassed} {msg}")

    def __sendMessage(self, msg):
        if self.log:
            self.__printLog(f"Telegram-> {msg}")
        try:
            self.Notifyer.sendMessage(f"{self.name}", f"{msg}")
        except Exception as e:
            print(f"FAILED TO SEND: {msg} exception: {e}")
            time.sleep(5)
        time.sleep(0.7)
