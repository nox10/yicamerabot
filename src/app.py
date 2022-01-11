import os
import os.path
import time
from multiprocessing import Process

from telegram import Update
from telegram.ext import Updater, CallbackContext, MessageHandler, Filters, CommandHandler

import config.config as config
from IPCam import IPCam
from Notifyer.SaveVideo import SaveVideo
from Notifyer.Telegram import Telegram
from TelegramChat import TelegramChat
from YiHomeCamera import YiCam


class main:

    def __init__(self):
        # polymorphism (?)
        self.notifyer = SaveVideo(Telegram(), config.MEDIA_SAVE_PATH, compressVideo=config.VIDEO_COMPRESSION)
        camera = YiCam
        self.cameraStatus = ""
        self.cams = []

        for cam in config.CAMERAS:
            self.cams.append(IPCam(self.notifyer, camera(cam[0], sensitivity=cam[2]), cam[1]))

        botUpdater = Updater(config.TOKEN)
        dispatcher = botUpdater.dispatcher

        # Make them start at the same time (more or less)
        for cam in self.cams:
            cam.start()
            TelegramChat(cam, dispatcher, self.updateStatus)

        dispatcher.add_handler(
            MessageHandler(Filters.regex(config.CAMERA_STATUS), self.updateStatus))  # Get camera status
        dispatcher.add_handler(MessageHandler(Filters.voice, self.playVoice))  # Audio message
        dispatcher.add_handler(CommandHandler(config.PLAY_COMMAND, self.playSound))  # Play .wav audio
        dispatcher.add_handler(CommandHandler(config.SAY_COMMAND, self.textToSpeech))  # TTS command

        botUpdater.start_polling()

        self.updateStatus(force=False, disable_notification=True)

        while True:
            self.deleteOldMedia(config.MEDIA_SAVE_PATH, config.MEDIA_RETENTION)
            self.updateStatus(force=False)

    def textToSpeech(self, update: Update, context: CallbackContext):
        if update.message.chat.id != config.CHATID:
            return  # Ignore messages not from the chatid
        text = " ".join(context.args)
        if len(text) == 0:
            update.message.reply_text(config.EMPTY_ARGS, parse_mode="HTML", disable_notification=True)
        else:
            update.message.reply_text(config.TTS_SAYING(text), parse_mode="HTML", disable_notification=True)
            self.__playTTS(text, self.cams)

    def playSound(self, update: Update, context: CallbackContext):
        if update.message.chat.id != config.CHATID:
            return  # Ignore messages not from the chatid
        text = " ".join(context.args)
        if len(text) == 0:
            update.message.reply_text(config.EMPTY_ARGS, parse_mode="HTML")
        else:
            filename = config.SOUND_SAVE_PATH + text + ".wav"
            if os.path.isfile(filename):
                update.message.reply_text(config.PLAYING_FILE(filename), parse_mode="HTML", disable_notification=True)
                self.__playAudio(filename, self.cams)
            else:
                update.message.reply_text(config.FILE_NOT_FOUND(filename), parse_mode="HTML", disable_notification=True)

    def playVoice(self, update: Update, context: CallbackContext):
        if update.message.chat.id != config.CHATID:
            return  # Ignore messages not from the chatid
        update.message.reply_text(config.PLAY_VOICE, parse_mode="HTML", disable_notification=True)
        update.message.effective_attachment.get_file().download(config.AUDIO_TEMP_FILE)
        # Convert to 16 bit mono
        os.system(
            f"ffmpeg -i {config.AUDIO_TEMP_FILE} -acodec pcm_s16le -ac 1 -ar 16000 {config.AUDIO_TEMP_FILE}.wav -y")
        self.__playAudio(config.AUDIO_TEMP_FILE + ".wav", self.cams)

    def __playTTS(self, text, cams):
        # Use multiprocessing to send the command all at the same time
        proc = []
        for cam in cams:
            if cam.isOnline():
                proc.append(Process(target=cam.textToSpeech, args=(text,)))
        for p in proc:
            p.start()

    def __playAudio(self, filename, cams):
        # Use multiprocessing to send the command all at the same time
        proc = []
        for cam in cams:
            if cam.isOnline():
                proc.append(Process(target=cam.sendSound, args=(filename,)))
        for p in proc:
            p.start()

    def deleteOldMedia(self, path, olderThanDays):
        current_time = time.time()
        for f in os.listdir(path):
            f = path + f
            creation_time = os.path.getctime(f)
            if (current_time - creation_time) // (24 * 3600) >= olderThanDays:
                os.unlink(f)
                print('{} removed'.format(f))

    def updateStatus(self, update: Update = None, context: CallbackContext = None, force=True, count=1,
                     disable_notification=False):
        if update != None and update.message.chat.id != config.CHATID:
            return  # Ignore messages not from the chatid
        stat = self.__getOnlineStatus()

        if force:
            self.cameraStatus = stat
            try:
                self.notifyer.sendMessage(config.CAMERA_STATUS, self.cameraStatus,
                                          reply_markup=self.__generateKeyboard(),
                                          disable_notification=disable_notification)
            except Exception as e:
                print(e)
        else:
            time.sleep(10)

        if stat != self.cameraStatus:
            if count > config.STATE_CHANGE_DELAY:
                self.updateStatus(update, context, force=True, disable_notification=disable_notification)
            else:
                self.updateStatus(update, context, count=count + 1, disable_notification=disable_notification)

    def __generateKeyboard(self):
        keyboard = []
        for cam in self.cams:
            notifyAction = config.NOTIFY_OFF(cam.getName()) if cam.sendNotification() else config.NOTIFY_ON(
                cam.getName())
            onOffAction = config.TURNING_OFF(cam.getName()) if cam.isEnabled() else config.TURNING_ON(cam.getName())

            if cam.isOnline():
                if cam.isEnabled():
                    keyboard.append([config.IMAGE(cam.getName())])
                    keyboard.append([notifyAction, onOffAction])
                else:
                    keyboard.append([onOffAction])

        keyboard.append([config.CAMERA_STATUS])
        return keyboard

    def __getOnlineStatus(self):
        msg = ""
        for cam in self.cams:
            if cam.isOnline():
                if cam.isEnabled():
                    notification = config.NOTIFICATION_YES if cam.sendNotification() else config.NOTIFICATION_NO
                    msg += config.STATUS_ONLINE(cam.name, notification)
                else:
                    msg += config.STATUS_DISABLED(cam.name)
            else:
                msg += config.STATUS_OFFLINE(cam.name)

        return msg


if __name__ == "__main__":
    os.makedirs(config.SOUND_SAVE_PATH, exist_ok=True)
    os.makedirs(config.MEDIA_SAVE_PATH, exist_ok=True)

    main()
