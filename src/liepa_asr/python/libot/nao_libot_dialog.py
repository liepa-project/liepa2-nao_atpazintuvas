#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Get Signal from Front Microphone & Calculate its rms Power"""


import qi
import qi.logging
import argparse
import sys
import time
import numpy as np
# import asr_generation.phrase_to_gram
# import asr_generation.transcriber_re
# import asr_generation.nao_dialog as nao_dialog
import libot.grasp.libot_trainer as trainer
import libot.grasp.libot_model as model
# import collections




class LibotDialog(object):

    def __init__(self, app):
        """
        Initialisation of qi framework and event detection.
        """
        super(LibotDialog, self).__init__()
        app.start()
        self.session = app.session
        self.logger = qi.logging.Logger("LibotService.logging")
        self.memory = self.session.service("ALMemory")
        self.liepaTTS = self.session.service("LiepaTTS")
        self.liepaASR = self.session.service("LiepaASR")
        self.recognizedSubscriber =  self.memory.subscriber("LiepaWordRecognized")
        self.unrecognizedSubscriber =  self.memory.subscriber("LiepaWordRecognizedNOT")        
        self.recognizedSubscriber.signal.connect(self.on_phrase_recognized)
        self.unrecognizedSubscriber.signal.connect(self.on_phrase_unrecognized)
        # self.dialog_resouces = {"labas":"sveikas","kaip sekasi":"gerai","kiek valandų":"pamiršau laikrodį"}
        self.naoDialogModel = None
        self.naoDialogContext = None
        self.memory.declareEvent("Libot/DialogEvent")
        self.memory.declareEvent("Libot/DialogStepDone")


    def loadTopicContent(self, file_path):
        f = open(file_path, "r")
        dialog_sting = f.read()
        f.close()
        naoDialogTrainer = trainer.NaoDialogTrainer()
        self.naoDialogModel = naoDialogTrainer.train(dialog_sting)
        self.logger.info("[loadTopicContent]  Done")


    def train_dialog(self):
        (gram_str, sphinx_dictionary_str) = model.NaoDialogUtil().generate_sphinx_resouces(self.naoDialogModel)
        f = open("/tmp/liepa_dialog.gram", "w")
        f.write(gram_str)
        f.close()
        f = open("/tmp/liepa_dialog.dict", "w")
        f.write(sphinx_dictionary_str)
        f.close()
        self.logger.info("[train_dialog]  ", gram_str)


    def activateTopic(self):
        self.train_dialog()
        self.liepaASR.pause()
        self.liepaASR.setAcousticModelPath("/home/nao/naoqi/lib/LiepaASRResources/liepa-2019_garsynas_3.0and1_56_ZR-01.3_37.cd_ptm_4000")
        self.liepaASR.setGrammarPath("/tmp/liepa_dialog.gram")
        self.liepaASR.setDictionaryPath("/tmp/liepa_dialog.dict")
        self.logger.info("[activateTopic]  Done")

    def start_dialog(self):
        self.naoDialogContext = model.NaoDialogContext()
        self.liepaASR.start()
        self.logger.info("[start_dialog] ASR start Done")

    def stop_dialog(self):
        self.naoDialogContext = None
        self.liepaASR.pause()
        self.logger.info("[stop_dialog]  Done")

    def next_step(self):
        self.logger.info("[on_phrase_recognized]  ASR start")
        self.liepaASR.start()

    def on_phrase_recognized(self, phrase):
        #print(phrase)
        self.logger.info("[on_phrase_recognized]  ", phrase)
        naoDialogResponse = model.NaoDialogUtil().find_response(self.naoDialogModel, self.naoDialogContext, phrase)
        self.say(naoDialogResponse.responseText)
        eventValue = "NA"
        if(naoDialogResponse.eventValue):
            eventValue =naoDialogResponse.eventValue
        self.memory.raiseEvent("Libot/DialogEvent", eventValue)
        self.memory.raiseEvent("Libot/DialogStepDone", naoDialogResponse.ruleId)
        # self.logger.info("[on_phrase_recognized]  ASR start")
        # self.liepaASR.start()

    def on_phrase_unrecognized(self, missedCount):
        #print(phrase)
        self.logger.info("[on_phrase_unrecognized]  ", missedCount)
        if(missedCount>3):
            self.say("Nesupratau")
        # self.logger.info("[on_phrase_recognized]  ASR start")
        # self.liepaASR.start()
        self.memory.raiseEvent("Libot/DialogStepDone", "rNA")
        self.memory.raiseEvent("Libot/DialogEvent", "NA")


    def say(self, message):
        self.logger.info("[say]  +++", message)
        self.liepaTTS.sayText(message)
        self.logger.info("[say]  ---", message)
        return message

    def signalCallback(self, c):
        print()
        
    def onConnect(self, c):
        if c:
            print "First connection"
        else:
            print "No more connections"




def main():
    app = qi.Application()
    app.start()
    session = app.session
    myLibotDialog = LibotDialog(app)
    session.registerService("LibotDialog", myLibotDialog)
    app.run()

if __name__ == "__main__":
    main()
