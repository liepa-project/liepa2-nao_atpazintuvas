#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Liepa2 record data and send to Kaldi Recognition server"""

import traceback

import qi
import argparse
import sys
import time
import datetime

# Kaldi client
import socket,asyncore
#python3
#from queue import Queue
#python2
from Queue import Queue

class KaldiClient(asyncore.dispatcher):

    def __init__(self, host, port, callback = None):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect( (host, int(port)) )
        self.sending = True
        self.audioBuffer = Queue()
        self.callback_function  = callback
        self.last_transcription = ""
        self.id = datetime.datetime.now().strftime("%H:%M:%S")

    def handle_connect(self):
        print(self.id, "[handle_connect]")
        pass

    def handle_close(self):
        print(self.id, "[handle_close]")
        self.close()

    def handle_read(self):
        # print("[handle_read]")
        recognized =self.recv(1024)
        # print("buffer: ", recognized)
        if recognized[-1:] == '\n':
            print(self.id, "Final: ", recognized)# e.g. labas \rlabas \n
            last_recognized = recognized.split("\r")[-1].strip()
            if(len(last_recognized)==0):
                if(len(self.last_transcription)==0):
                    return "Initial value. Assume it is an recognizion noise"
                else:
                    last_recognized = self.last_transcription
            if self.callback_function:
                self.callback_function(self.id, last_recognized)
                self.last_transcription = ""
            self.handle_close() 
        # elif recognized[-1:] == '\r':
        #     print("Initial: ", recognized)
        else :
            self.last_transcription = recognized.strip()
            # print("[handle_read] Initial2: ", recognized.strip())

    def readable(self):
        # print("[readable]")
        return True

    def writable(self):
        # print("[writable]")
        return self.sending 

    def handle_write(self):
        try:
            # print("[handle_write] >> reading data")
            if(not self.audioBuffer.empty()):
                audioChunk = self.audioBuffer.get_nowait()
                # print("[handle_write] read data", len(audioChunk))
                self.send(audioChunk)
                # print("[handle_write] sent data")
            # else:
            #     print("Nothing to send")
        except:
            e = sys.exc_info()[0]
            print("[handle_write] e: ",self.id, e)
            traceback.print_exc()
            pass
    
    def pushToBuffer(self, audioChunk):
        # print("[pushToBuffer] >> ", len(audioChunk))
        try:
            self.audioBuffer.put_nowait(audioChunk)
        except:
            e = sys.exc_info()[0]
            print("[handle_write] e: ",self.id, e)
            traceback.print_exc()
            pass
    


class LiepaAsrKaldi(object):
    """
    Liepa Kaldi Client
    """

    def __init__( self, app):
        """
        Initialise services and variables.
        """
        super(LiepaAsrKaldi, self).__init__()
        app.start()
        session = app.session
        
        self.memory = session.service("ALMemory")
        self.memory.declareEvent("LiepaKaldiWordRecognized")
        # Get the service ALAudioDevice.
        self.audio_service = session.service("ALAudioDevice")
        # self.liepa_tts = session.service("LiepaTTS")
        self.isProcessingRequested = False
        self.module_name = "LiepaAsrKaldi"
        self.sampleRate = 16000.0 # hertz
        self.asrClient = None
    
    def recognized_callback(self, id, text):
        postprocessed_text = text.strip("pd").strip()
        print("{} recognized_callback = {}".format(id, postprocessed_text))
        # self.liepa_tts.say("Išgirdau. " + postprocessed_text)
        self.memory.raiseEvent("LiepaKaldiWordRecognized", postprocessed_text)
        self.stopProcessing() 
        

    def stopProcessing(self):
        print("[stopProcessing]")
        self.audio_service.unsubscribe(self.module_name)
        raise asyncore.ExitNow('Server is quitting!')


    def startProcessing(self):
        """
        Start processing
        """
        # ask for the front microphone signal sampled at 16kHz
        # if you want the 4 channels call setClientPreferences(self.module_name, 48000, 0, 0)
        print("[startProcessing] startProcessing")
        self.audio_service.setClientPreferences(self.module_name, 16000, 3, 0)
        self.audio_service.subscribe(self.module_name)
        self.isProcessingRequested = True


    def processRemote(self, nbOfChannels, nbOfSamplesByChannel, timeStamp, inputBuffer):
        """
        Compute RMS from mic.
        """
        try:
            # print("timeStamp",timeStamp)
            # print("nbOfSamplesByChannel",nbOfSamplesByChannel)
            if(self.asrClient):
                self.asrClient.pushToBuffer(inputBuffer)
        except:
            e = sys.exc_info()[0]
            print("[handle_write] e: ",e)
            traceback.print_exc()
            pass

    def run(self):
        """
        Loop on, wait for events until manual interruption.
        """
        print("Starting LiepaAsrKaldi")
        try:
            while True:
                if(self.isProcessingRequested):
                    self.isProcessingRequested = False
                    print("[run] self.isProcessingRequested", self.isProcessingRequested)
                    # sys.exit(0)
                    try:
                        self.asrClient = KaldiClient('192.168.1.203', '5050', self.recognized_callback)
                        print(self.asrClient.id,"[run] >>> staring asyncore")
                        asyncore.loop()
                        print(self.asrClient.id, "[run] <<< staring asyncore")
                        self.asrClient.close()
                        self.asrClient = None
                    except KeyboardInterrupt:
                        print "Interrupted by user, stopping LiepaAsrKaldi"
                        self.stopProcessing()
                        sys.exit(0)
                    except asyncore.ExitNow, e:
                        print("Finish client loop")
                        print(self.asrClient.id, "[run] <<< staring asyncore")
                        self.asrClient.close()
                        self.asrClient = None
                        pass
                    except:
                        e = sys.exc_info()[0]
                        print("[handle_write] e: ",e)
                        traceback.print_exc()
                        pass
                else:
                    time.sleep(1)
        except KeyboardInterrupt:
            print "Interrupted by user, stopping LiepaAsrKaldi"
            sys.exit(0)

            



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    try:
        # Initialize qi framework.
        connection_url = "tcp://" + args.ip + ":" + str(args.port)
        app = qi.Application(["LiepaAsrKaldi", "--qi-url=" + connection_url])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
            "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    MyLiepaAsrKaldi = LiepaAsrKaldi(app)
    app.session.registerService("LiepaAsrKaldi", MyLiepaAsrKaldi)
    # MyLiepaAsrKaldi.startProcessing()
    MyLiepaAsrKaldi.run()
