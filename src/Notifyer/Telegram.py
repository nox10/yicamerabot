import random

import telegram

import config.config as config


class Telegram:

    def __init__(self):
        self.bots = []

        for alt in config.TOKEN_ALL:
            self.bots.append(telegram.Bot(alt))

    def sendPhoto(self, media, caption="", reply_markup=None, disable_notification=False):
        if reply_markup is not None:
            reply_markup = telegram.ReplyKeyboardMarkup(reply_markup)

        random.shuffle(self.bots)
        error = True
        for bot in self.bots:
            try:
                bot.sendPhoto(config.CHATID, media, caption=caption, parse_mode="HTML", reply_markup=reply_markup,
                              disable_notification=disable_notification)
                error = False
                break
            except telegram.error.TimedOut as e:
                print(f"Timed out Send failed pass to alt {e}")
                error = False
                # Typically timed out is sent
                break
            except Exception as e:
                print(f"Send failed pass to alt {e}")
        return error

    def sendVideo(self, media, caption="", reply_markup=None, disable_notification=False, width=0, height=0):
        if reply_markup is not None:
            reply_markup = telegram.ReplyKeyboardMarkup(reply_markup)

        random.shuffle(self.bots)
        error = True
        for bot in self.bots:
            try:
                bot.sendVideo(config.CHATID, media, caption=caption, parse_mode="HTML", reply_markup=reply_markup,
                              width=width, height=height, disable_notification=disable_notification)
                error = False
                break
            except telegram.error.TimedOut as e:
                print(f"Timed out Send failed pass to alt {e}")
                error = False
                # Typically timed out is sent
                break
            except Exception as e:
                print(f"Send failed pass to alt {e}")
        return error

    def sendMessage(self, title, message="", reply_markup=None, disable_notification=False):
        if reply_markup is not None:
            reply_markup = telegram.ReplyKeyboardMarkup(reply_markup)

        text = f"<strong>{title}</strong>\n{message}"

        random.shuffle(self.bots)
        error = True
        for bot in self.bots:
            try:
                bot.sendMessage(config.CHATID, text, parse_mode="HTML", reply_markup=reply_markup,
                                disable_notification=disable_notification)
                error = False
                break
            except telegram.error.TimedOut as e:
                print(f"Timed out Send failed pass to alt {e} {title}")
                error = False
                # Typically timed out is sent
                break
            except Exception as e:
                print(f"Send failed pass to alt {e} {title}")

        if error:
            raise Exception("Run out of alt bot")
