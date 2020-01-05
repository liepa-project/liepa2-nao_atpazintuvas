# -*- coding: utf-8 -*-

import unittest
import libot.nao_dialog_trainer as nao_dialog_trainer
import libot.nao_dialog_model as nao_dialog_model
import collections


class NaoDialogTest(unittest.TestCase):

    def setUp(self):
        self.naoDialogUtil = nao_dialog_model.NaoDialogUtil()
        pass

    def util_find_reponse(self, naoDialogModel, naoDialogContext, user_step, bot_step):
        response=self.naoDialogUtil.find_response(naoDialogModel, naoDialogContext, user_step)
        self.assertEqual(bot_step,response.responseText)
        return response
    
    def util_find_reponse_in(self, naoDialogModel, naoDialogContext, user_step, bot_step):
        response=self.naoDialogUtil.find_response(naoDialogModel, naoDialogContext, user_step)
        self.assertIs(True, response.responseText in bot_step)
        return response

    def util_find_reponse_with_event(self, naoDialogModel, naoDialogContext, user_step, bot_step, eventValue):
        response=self.naoDialogUtil.find_response(naoDialogModel, naoDialogContext, user_step)
        self.assertEqual(bot_step,response.responseText)
        self.assertEqual(eventValue,response.eventValue)
        return response


        
    # dialog_scenario = collections.OrderedDict([("Labas","sveikinas"), ("Kaip tau sekasi","normoje")])
    def util_find_reponses(self, naoDialogModel, dialog_scenario):
        naoDialogContext = nao_dialog_model.NaoDialogContext()
        naoDialogUtil = nao_dialog_model.NaoDialogUtil()
        response_arr = []
        for user_step,bot_step in dialog_scenario.items():
            response = naoDialogUtil.find_response(naoDialogModel,naoDialogContext, user_step)
            response_arr.append(response)
            self.assertEqual(bot_step,response.responseText)
        return response_arr
            

    

    def test_dialog_parser_simple(self):
        dialog_str = """topic: ~test_dialog()
language: ltu
u:(Labas) Sveiki
u:(Kaip tau sekasi) Normoje
u:(kuri diena) geroji"""
        naoDialogTrainer = nao_dialog_trainer.NaoDialogTrainer()
        naoDialogModel = naoDialogTrainer.train(dialog_str)
        naoDialogContext = nao_dialog_model.NaoDialogContext()

        self.util_find_reponse(naoDialogModel, naoDialogContext, "Labas", "sveiki")
        self.util_find_reponse(naoDialogModel, naoDialogContext, "Kaip tau sekasi", "normoje")
        self.util_find_reponse(naoDialogModel, naoDialogContext, "kuri diena", "geroji")



    def test_dialog_parser_concept(self):
        dialog_str = """topic: ~test_dialog()
language: ltu
concept:(greetings) ^rand[sveiki "laba diena"]
u:(~greetings) ~greetings
u:(Kaip tau sekasi) Normoje"""
        naoDialogTrainer = nao_dialog_trainer.NaoDialogTrainer()
        naoDialogModel = naoDialogTrainer.train(dialog_str)

        naoDialogContext = nao_dialog_model.NaoDialogContext()

        self.util_find_reponse_in(naoDialogModel, naoDialogContext, "sveiki", ["sveiki",'laba diena'])
        self.util_find_reponse(naoDialogModel, naoDialogContext, "Kaip tau sekasi", "normoje")


    def test_dialog_parser_variable(self):
        dialog_str = """topic: ~test_dialog()
language: Lithuanian
u:(Kaip tau sekasi) Normoje
u:(kuri diena) geroji $LibotServiceEvent=geroji
u:(kiek valandų) pamiršau laikrodį $LibotServiceEvent=kelti_ranka
"""
        naoDialogTrainer = nao_dialog_trainer.NaoDialogTrainer()
        naoDialogModel = naoDialogTrainer.train(dialog_str)

        naoDialogContext = nao_dialog_model.NaoDialogContext()

        self.util_find_reponse(naoDialogModel, naoDialogContext, "Kaip tau sekasi", "normoje")
        self.util_find_reponse_with_event(naoDialogModel, naoDialogContext, "kuri diena", "geroji", "geroji")
        self.util_find_reponse_with_event(naoDialogModel, naoDialogContext, "kiek valandų", "pamiršau laikrodį", "kelti_ranka")
        

    def test_dialog_generate_resouces(self):
        dialog_str = """topic: ~test_dialog()
language: Lithuanian
concept:(greetings) ^rand[sveiki "laba diena"]
u:(~greetings) ~greetings
u:(Kaip tau sekasi) Normoje
u:(kuri diena) geroji"""
        naoDialogTrainer = nao_dialog_trainer.NaoDialogTrainer()
        naoDialogModel = naoDialogTrainer.train(dialog_str)
        (gram, sphinx_dictionary) = nao_dialog_model.NaoDialogUtil().generate_sphinx_resouces(naoDialogModel)
        self.assertEqual(gram,"#JSGF V1.0;\n\ngrammar adr_element;\n\npublic <adr_element> =\nsveiki|\nlaba diena|\nkaip tau sekasi|\nkuri diena;")
        self.assertEqual(sphinx_dictionary,"diena\tD I E N A\nkaip\tK A I P\nkuri\tK U R I\nlaba\tL A B A\nsekasi\tS E K A S I\nsveiki\tS V E I K I\ntau\tT A U")


    def test_dialog_parser_subrule(self):
        dialog_str = """topic: ~test_dialog()
language: Lithuanian
u:(pakalbam apie gyvūnus) tu turi katę ar šunį?
    u1:(šunį) ar didelis?
        u2:(taip) prižiūrėk kad daug bėgiotų
        u2:(ne) jie tokie mieli
    u1:(katę) ar gyveni bute?
        u2:(taip) tikiuosi bute daug miega
        u2:(ne) ar katinas eina į lauką?
            u3:(taip) ar gaudo peles?
u:(pakalbam apie sportą) puiki mintis
    """

        naoDialogTrainer = nao_dialog_trainer.NaoDialogTrainer()
        naoDialogModel = naoDialogTrainer.train(dialog_str)
        # chart = naoDialogTrainer.generate_dialog_chart(naoDialogModel)
        # print(chart)

        naoDialogContext = nao_dialog_model.NaoDialogContext()

        self.util_find_reponse(naoDialogModel, naoDialogContext, "pakalbam apie gyvūnus", "tu turi katę ar šunį?")
        self.util_find_reponse(naoDialogModel, naoDialogContext, "katę", "ar gyveni bute?")
        self.util_find_reponse(naoDialogModel, naoDialogContext, "ne", "ar katinas eina į lauką?")
        self.util_find_reponse(naoDialogModel, naoDialogContext, "taip", "ar gaudo peles?")
        self.util_find_reponse(naoDialogModel, naoDialogContext, "pakalbam apie sportą", "puiki mintis")


    def test_dialog_parser_activate_proposal(self):
        dialog_str = """topic: ~test_dialog()
language: Lithuanian
u:(labas) %game0 ar patinka žaisti?
    u1:(taip) Smagu ^activate(game1)
    u1:(ne) bet gal su robotu pažaisi? 

proposal: %game1 ar mėgsti krepšinį
    u1:(taip) Aš irgi taiklus ^activate(game0)
    u1:(ne) Supratu ^activate(game0)
    """

        naoDialogTrainer = nao_dialog_trainer.NaoDialogTrainer()
        naoDialogModel = naoDialogTrainer.train(dialog_str)
        # chart = naoDialogTrainer.generate_dialog_chart(naoDialogModel)
        # print(chart)

        naoDialogContext = nao_dialog_model.NaoDialogContext()

        self.util_find_reponse(naoDialogModel, naoDialogContext, "labas", "ar patinka žaisti?")
        self.util_find_reponse(naoDialogModel, naoDialogContext, "taip", "smagu. ar mėgsti krepšinį")
        # self.util_find_reponse(naoDialogModel, naoDialogContext, "labas", "")
        self.util_find_reponse(naoDialogModel, naoDialogContext, "ne", "supratu. ar patinka žaisti?")
        self.util_find_reponse(naoDialogModel, naoDialogContext, "ne", "bet gal su robotu pažaisi?")


    def test_dialog_parser_stayInContext(self):
        dialog_str = """topic: ~test_dialog()
    language: Lithuanian
    u:(labas) ar patinka žaisti?
        u1:(taip) Smagu
        u1:(ne) bet gal su robotu pažaisi ^stayInScope
    """

        naoDialogTrainer = nao_dialog_trainer.NaoDialogTrainer()
        naoDialogModel = naoDialogTrainer.train(dialog_str)
        # chart = naoDialogTrainer.generate_dialog_chart(naoDialogModel)
        # print(chart)

        naoDialogContext = nao_dialog_model.NaoDialogContext()

        self.util_find_reponse(naoDialogModel, naoDialogContext, "labas", "ar patinka žaisti?")
        self.util_find_reponse(naoDialogModel, naoDialogContext, "ne", "bet gal su robotu pažaisi")
        self.util_find_reponse(naoDialogModel, naoDialogContext, "labas", "")
        self.util_find_reponse(naoDialogModel, naoDialogContext, "taip", "smagu")
        self.util_find_reponse(naoDialogModel, naoDialogContext, "labas", "ar patinka žaisti?")


    def test_dialog_parser_event(self):
        dialog_str = """topic: ~test_dialog()
language: Lithuanian
u:(Kaip tau sekasi) Normoje
u:(kuri diena) geroji

u:(e:Dialog/Fallback) Neturiu atsakymo
"""
        naoDialogTrainer = nao_dialog_trainer.NaoDialogTrainer()
        naoDialogModel = naoDialogTrainer.train(dialog_str)

        naoDialogContext = nao_dialog_model.NaoDialogContext()

        self.util_find_reponse(naoDialogModel, naoDialogContext, "nemokyta frazė", "neturiu atsakymo")
        self.util_find_reponse(naoDialogModel, naoDialogContext, "kuri diena", "geroji")


