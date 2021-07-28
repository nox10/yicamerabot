import requests
import urllib.request
import io
import os
from ftplib import FTP, error_perm
import time

class YiCam:

    videoPath = "/tmp/sd/record"
    tmpFile = "tmp.mp4.tmp"

    def __init__(self, config, ip):
        self.ip = ip
        self.config = config
        self.connectFTP()


    def connectFTP(self):
        try:
            self.ftp = FTP(self.ip, timeout=15)
            self.ftp.login(user="root", passwd = "")
            self.connected = True
        except Exception as e:
            print(e)
            self.connected = False

        return self.connected


    def isConnected(self):
        return self.connected


    def disconnect(self):
        self.ftp = False
        self.connected = False


    def getImage(self, highQuality = False, timeStamp = False):
        highQuality = "high" if highQuality else "low"
        timeStamp = "yes" if timeStamp else "no"

        url = f"http://{self.ip}:8080/cgi-bin/snapshot.sh?res={highQuality}&watermark={timeStamp}"
        response = requests.get(url, timeout=self.config.SNAPSHOT_TIMEOUT)
        return io.BytesIO(response.content) if (response.headers.get("content-type") == "image/jpeg") else False


    def isRecording(self):
        try:
            self.ftp.cwd(self.videoPath)
        except Exception as e:
            print(e)
            return False
        return self.tmpFile in self.ftp.nlst()

    
    def getTmpVideoSize(self):
        if self.isRecording():
            return self.ftp.size(f"{self.videoPath}/{self.tmpFile}")
        else:
            return -1


    def removeTmpVideo(self):
        if self.isRecording():
            self.ftp.delete(f"{self.videoPath}/{self.tmpFile}")


    def callbackVideoList(self, videoFunc, name):
        videoCount = 0
        self.ftp.cwd(self.videoPath)
        for folder in self.ftp.nlst():
            if folder != self.tmpFile:
                dirPath = f"{self.videoPath}/{folder}"
                self.ftp.cwd(dirPath)
                for videoFile in self.ftp.nlst():
                    filePath = f"/{self.videoPath}/{folder}/{videoFile}"
                    urlPath = f"ftp://root:@{self.ip}{filePath}"
                    print(urlPath)
                    videoObj = io.BytesIO(urllib.request.urlopen(urlPath).read())
                    videoFunc(videoObj, name)
                    self.ftp.delete(filePath)

                try:
                    self.ftp.rmd(dirPath)
                except error_perm as e:
                    print(e)