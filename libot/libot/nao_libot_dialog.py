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
import libot.nao_dialog_trainer as nao_dialog_trainer
import libot.nao_dialog_model as nao_dialog_model
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
        # self.dialog_resouces = {"labas":"sveikas","kaip sekasi":"gerai","kiek valandų":"pamiršau laikrodį"}
        self.naoDialogModel = None
        self.memory.declareEvent("LibotServiceEvent")


    def loadTopicContent(self, file_path):
        f = open(file_path, "r")
        dialog_sting = f.read()
        f.close()
        naoDialogTrainer = nao_dialog_trainer.NaoDialogTrainer()
        self.naoDialogModel = naoDialogTrainer.train(dialog_sting)
        # entryArray = naoDialog.parse(dialog_sting)
        # self.logger.info("[load_dialog]  ", entryArray)
        # self.dialog_resouces = {}
        # for entry in entryArray:
        #     self.dialog_resouces[entry["key"]]=entry

    def train_dialog(self):
        # transformer = asr_generation.phrase_to_gram.PhraseTransformer()
        # transcriber = asr_generation.transcriber_re.TranscriberRegexp()

        # sphinx_dictionary = collections.OrderedDict()
        # for key, value in self.dialog_resouces.items():
        #     phrase = key.strip()
        #     if not phrase:
        #         continue
        #     transformer.addPhrase(phrase)
        #     loop_dictionary = transcriber.processWords(phrase)
        #     sphinx_dictionary.update(loop_dictionary)
        # gram = transformer.generateGram()
        # sphinx_dictionary = collections.OrderedDict(sorted(sphinx_dictionary.items(), key=lambda t: t[0]))

        (gram_str, sphinx_dictionary_str) = nao_dialog_model.NaoDialogUtil().generate_sphinx_resouces(self.naoDialogModel)
        f = open("/tmp/liepa_dialog.gram", "w")
        f.write(gram_str)
        f.close()
        f = open("/tmp/liepa_dialog.dict", "w")
        f.write(sphinx_dictionary_str)
        # for key, value in sphinx_dictionary.items():
        #     f.write("{}\t{}\n".format(key, value))
        f.close()
        self.logger.info("[train_dialog]  ", gram_str)
        # print(gram)
        # 
    



    def activateTopic(self):
        self.train_dialog()
        self.liepaASR.pause()
        self.liepaASR.setAcousticModelPath("/home/nao/naoqi/lib/LiepaASRResources/liepa-2019_garsynas_3.0and1_56_ZR-01.3_37.cd_ptm_4000")
        self.liepaASR.setGrammarPath("/tmp/liepa_dialog.gram")
        self.liepaASR.setDictionaryPath("/tmp/liepa_dialog.dict")
        self.logger.info("[init_dialog]  ")

    def start_dialog(self):
        self.liepaASR.start()
        self.recognizedSubscriber.signal.connect(self.on_phrase_recognized)
        self.unrecognizedSubscriber.signal.connect(self.on_phrase_unrecognized)
        self.logger.info("[start_dialog]  ")

    def stop_dialog(self):
        self.liepaASR.pause()
        self.logger.info("[stop_dialog]  ")


    def on_phrase_recognized(self, phrase):
        #print(phrase)
        self.logger.info("[on_phrase_recognized]  ", phrase)
        response=None
        eventValue=None
        (response,eventValue) = nao_dialog_model.NaoDialogUtil().find_response(self.naoDialogModel, phrase)
        # try:
        #     response = self.dialog_resouces[phrase]["value"]
        #     eventValue = self.dialog_resouces[phrase]["eventValue"]
        # except KeyError:
        #     print("Key not found", phrase)
        #     response="Nesupratau"

        self.liepaTTS.sayText(response)
        if(eventValue):
            self.memory.raiseEvent("LibotServiceEvent", eventValue)
        self.liepaASR.start()

    def on_phrase_unrecognized(self, missedCount):
        #print(phrase)
        self.logger.info("[on_phrase_unrecognized]  ", missedCount)
        if(missedCount>3):
            self.liepaTTS.sayText("Nesupratau")
        self.liepaASR.start()


    def echo(self, message):
        self.liepaTTS.sayText("Labas")
        return message


def main():
    app = qi.Application()
    app.start()
    session = app.session
    myLibotDialog = LibotDialog(app)
    session.registerService("LibotDialog", myLibotDialog)
    app.run()

if __name__ == "__main__":
    main()
