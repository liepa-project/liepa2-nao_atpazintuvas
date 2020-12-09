#!/usr/bin/env python

import qi
import argparse
import sys
import time
import numpy as np
import wave

import requests
import datetime
"""
    Create by Mindaugas Greibus 2020-12-01
"""


class LiepaSpeechExternalModule(object):
    """
    A simple get signal from the front microphone of Nao & calculate its rms power.
    It requires numpy.
    """

    def __init__( self, app):
        """
        Initialise services and variables.
        """
        super(LiepaSpeechExternalModule, self).__init__()
        app.start()
        session = app.session

        self.module_name = "LiepaSpeechExternal"
        # Get the service ALAudioDevice.
        self.audio_service = session.service("ALAudioDevice")
        self.audio_player = session.service("ALAudioPlayer")
        self.logger = qi.Logger(self.module_name)
        self.nbOfFramesToProcess = 30
        self.framesCount=0
        self.micFront = []
        self.sampleRate = 16000.0 # hertz
        
        self.wavFileName = '/tmp/liepa_asr_sound.wav'
        self.mp3FileName = '/tmp/liepa_tts_sound.mp3'
        self.server_name="192.168.1.203:1444" # or "liepa.rastija.lt:444"
        self.server_login=""
        self.server_password=""
        self.server_clientId=""

        self.access_token = ""
        self.memory = session.service("ALMemory")
        self.memory.declareEvent("LiepaExternalWordRecognized")
        self.isUttStarted = False
        self.isInitialized = False



    def init(self, server_name_port, login, password, clientId):
        """
            Initialize all necessary elements for new recording session. 
            function logs in to external server and subscribe audio service
        """
        self.logger.error("[init]+++")
        print("[init]+++")
        print("[init] server name", server_name_port)
        self.server_name= server_name_port
        self.server_login=login
        self.server_password=password
        self.server_clientId=clientId
        self.access_token = self.login()
        # self.isProcessingDone=True
        self.isUttStarted = False
        if self.isInitialized == False:
            self.audio_service.setClientPreferences(self.module_name, self.sampleRate, 3, 0)
            self.audio_service.subscribe(self.module_name)
            self.isInitialized = True
        self.logger.error("[init]---")
        print("[init]---")
        return "init: done" 


    def login(self):       
        """
            Logs to external server
        """ 
        self.logger.error("[login]+++")
        print("[login]+++")
        loginUrl = "https://{server_name}/token".format(server_name=self.server_name)
        print("[login] loginUrl", loginUrl)
        payload = {'grant_type':'password','username':self.server_login,'password':self.server_password,'client_id':self.server_clientId}
        tokenResponse = requests.post(loginUrl, data=payload, verify=False)
        tokenJson=tokenResponse.json()
        access_token=tokenJson["access_token"]
        print("[login]",tokenJson)
        self.logger.error("[login]---")
        print("[login]---")
        return access_token

    def recognize(self, access_token, file_name):
        """
            Sends wav faile for recogntion to external server
        """ 
        self.logger.error("[recognize]")
        print("[recognize]+++")
        files = {'file': open(file_name, 'rb')}
        theHeaders= {'Authorization': 'Bearer ' + access_token}
        recognitionUrl = "https://{server_name}/api/RecognizerServiceExecution/ATP.Robotas".format(server_name=self.server_name)
        getdata = requests.post(recognitionUrl, files=files,headers=theHeaders, verify=False)
        print(getdata.json())
        print("[recognize]---")
        return getdata.json()




    def shutdown(self):
        """
            In case of emergency this function should be called. 
            it will shutdown service. Service or robot restart is needed. 
        """ 
        self.logger.error("[shutdown]+++")
        print("[shutdown]+++")
        #MG: check why it blocks
        self.audio_service.unsubscribe(self.module_name)
        self.logger.error("[shutdown]---")
        print("[shutdown]---")
        sys.exit(0)



    def start(self, nbOfFramesToProcess):
        """
            Create new audio files for recroding and sets indicator to start recording 
        """
        # ask for the front microphone signal sampled at 16kHz
        # if you want the 4 channels call setClientPreferences(self.module_name, 48000, 0, 0)
        self.logger.error("[start] start processing")
        print("[start]+++")
        if self.isInitialized == False:
            print("Cannot start. Please call init() first")
            return
        if nbOfFramesToProcess > 10:
            self.nbOfFramesToProcess = nbOfFramesToProcess
        self.obj = wave.open(self.wavFileName,'w')
        self.obj.setnchannels(1) # mono
        self.obj.setsampwidth(2)
        self.obj.setframerate(self.sampleRate)
        # self.isProcessingDone=False
        # self.isProcessingRequested = True
        self.isUttStarted=True
        self.framesCount=0
        print("[start]---")
        return "start: done" 

        
    

    def pause(self):
        """
            Temporaly stop recording by seting indictor to ignore future audio frames
        """
        print("[pause]+++")
        # self.isProcessingDone=True
        # self.isProcessingRequested = False
        self.isUttStarted=False



    def processRemote(self, nbOfChannels, nbOfSamplesByChannel, timeStamp, inputBuffer):
        """
        Start processing consuming audio files after subscription.  
        As audio unsubscribe() blocks app it is added  isInitialized frames if no recording is needed.
        This function does not use voice activity detection, but rather timeout approach
        """
        self.framesCount = self.framesCount + 1
        # print("[processRemote] ?")
        if self.isUttStarted == False:
            return

        if (self.framesCount <= self.nbOfFramesToProcess):
            self.obj.writeframesraw( inputBuffer )
            # convert inputBuffer to signed integer as it is interpreted as a string by python
            # self.micFront=self.convertStr2SignedInt(inputBuffer)
            #compute the rms level on front mic
            # rmsMicFront = self.calcRMSLevel(self.micFront)
            # print ("rms level mic front = " + str(rmsMicFront))
            #print(".")
        else :
            self.isUttStarted=False
            self.obj.close()
            recognition_obj = self.recognize(self.access_token,self.wavFileName)
            #MyLiepaSpeechExternalModule.recognize(MyLiepaSpeechExternalModule.access_token,MyLiepaSpeechExternalModule.wavFileName)
            result_text = u"Aptikta klaida!"
            if "result" in recognition_obj:
                result_text = recognition_obj["result"]
            elif "message" in recognition_obj:
                result_text = "Gauta klaida: " + recognition_obj["message"]
            print("[processRemote]recogntion result: ",result_text)
            self.memory.raiseEvent("LiepaExternalWordRecognized", result_text)
            self.pause()


    def sayText(self, tts_text):
        self.logger.error("[sayText]")
        access_token=self.access_token
        print("[recognize]+++")
        tts_json = {'Text': tts_text, "Speed":100}
        theHeaders= {'Authorization': 'Bearer ' + access_token}
        recognitionUrl = "https://{server_name}/api/SynthesizerServiceExecution/SINT.Edvardas".format(server_name=self.server_name)
        response = requests.post(recognitionUrl, json=tts_json,headers=theHeaders, verify=False)

        if response.status_code == 200:
            with open(self.mp3FileName, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        
        
        fileId = self.audio_player.loadFile(self.mp3FileName)
        self.audio_player.play(fileId, _async=False)


        
        print("[sayText]---")
        return "sayText"

            

    def calcRMSLevel(self,data) :
        """
        Calculate RMS level
        """
        rms = 20 * np.log10( np.sqrt( np.sum( np.power(data,2) / len(data)  )))
        return rms

    def convertStr2SignedInt(self, data) :
        """
        This function takes a string containing 16 bits little endian sound
        samples as input and returns a vector containing the 16 bits sound
        samples values converted between -1 and 1.
        """
        signedData=[]
        ind=0;
        for i in range (0,len(data)/2) :
            signedData.append(data[ind]+data[ind+1]*256)
            ind=ind+2

        for i in range (0,len(signedData)) :
            if signedData[i]>=32768 :
                signedData[i]=signedData[i]-65536

        for i in range (0,len(signedData)) :
            signedData[i]=signedData[i]/32768.0

        return signedData






### Based on /data/home/nao/.local/share/PackageManager/apps/adjust_volume.py
def main():
    # Create and Start the Application
    app = qi.Application()
    app.start()
    # Create the ALGenerateKnowledge Service
    ps = LiepaSpeechExternalModule(app)
    # Register It
    app.session.registerService("LiepaSpeechExternal", ps)
    # Run the Application
    print("Running!")
    app.run()
    


if __name__ == "__main__":
    main()

