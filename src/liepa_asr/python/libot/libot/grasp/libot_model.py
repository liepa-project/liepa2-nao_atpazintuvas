#!/usr/bin/env python2
# -*- coding: utf-8 -*-


'''
@author: Mindaugas Greibus
parses Nao dialog file
'''

import re 
import shlex
import libot.asr_gen.phrase_to_gram as phrase_to_gram
import libot.asr_gen.transcriber_re as transcriber_re
import collections  
import random

class NaoRuleEntry:
    def __init__(self):
        self.userIntentArr=[]
        self.botResponseArr=[]
        self.eventValue=""
        self.id=""
        self.parent_id=""
        self.instructionDict={}
        self.tag=""
    
    def fill(self, id, parent_id, userIntentArr, botResponseArr, eventValue, instructionDict, tag):
        self.id=id
        self.parent_id = parent_id
        self.userIntentArr = userIntentArr
        self.botResponseArr = botResponseArr
        self.eventValue = eventValue
        self.instructionDict = instructionDict
        self.tag = tag
        return self

    def __str__(self):
        return str(self.__dict__)


class NaoDialogModel:
    EVENT_FALLBACK="e:Dialog/Fallback"

    # ^stayinscope

    def __init__(self):
        self.dialog_rules=[]
        self.dialog_event_dict={}
        self.conceptDict={}
        # self.dialog_resouces = []
        # self.dialog_responses_dict = {}
    
    def __str__(self):
        return str(self.__dict__)


class NaoDialogContext:
    def __init__(self):
        self.previous_rules = []
        self.current_scope_parent_id = ""
        self.next_intents=[]
    def __str__(self):
        return str(self.__dict__)


class NaoDialogResponse:
    def __init__(self):
        self.ruleId = ""
        self.responseText = ""
        self.eventValue=""
        self.naoDialogContext=None
    
    def __str__(self):
        return str(self.__dict__)


class NaoDialogUtil:
    def __init__(self):
        pass

    def debug(self, *values):
        # print(values)
        pass

    def generate_sphinx_resouces(self, naoDialogModel):
        transformer = phrase_to_gram.PhraseTransformer()
        transcriber = transcriber_re.TranscriberRegexp()

        sphinx_dictionary = collections.OrderedDict()
        # print("[generate_sphinx_resouces]", naoDialogModel.dialog_resouces)
        for rule in naoDialogModel.dialog_rules:
            key =rule.userIntentArr
            for key in rule.userIntentArr:
            # value=item["value"]
                phrase = key.strip()
                if not phrase:
                    continue
                transformer.addPhrase(phrase)
                loop_dictionary = transcriber.processWords(phrase)
                sphinx_dictionary.update(loop_dictionary)
        gram = transformer.generateGram()
        sphinx_dictionary = collections.OrderedDict(sorted(sphinx_dictionary.items(), key=lambda t: t[0]))
        sphinx_dictionary_str = '\n'.join(['%s\t%s' % (key, value) for (key, value) in sphinx_dictionary.items()])
        return (gram, sphinx_dictionary_str)


    def generate_response(self, naoDialogModel, naoDialogContext, aRule):
        return random.choice(aRule.botResponseArr)
    
    def get_child_rules(self, naoDialogModel, parent_rule_id):
        return [aRule for aRule in naoDialogModel.dialog_rules if aRule.parent_id == parent_rule_id ]
    
    def get_rules_by_tag(self, naoDialogModel, tag):
        return [aRule for aRule in naoDialogModel.dialog_rules if aRule.tag == tag ]

    def set_context_scope(self, naoDialogModel, naoDialogContext, aRule):
        self.debug("[set_context_scope]seting context to rule", str(aRule))
        if(aRule):
            if("^stayinscope" in aRule.instructionDict):
                self.debug("[set_context_scope]Stay in same context")
            else:
                naoDialogContext.current_scope_parent_id = aRule.id
                self.debug("[set_context_scope]Setting new context")
        else:
            self.debug("[set_context_scope]Reseting context")
            naoDialogContext.current_scope_parent_id = ""

    def find_applicable_rules(self, naoDialogModel, naoDialogContext):
        applicable_rules = self.get_child_rules(naoDialogModel,naoDialogContext.current_scope_parent_id)
        self.debug("[find_applicable_rules]---- filter by parrent of previous rule", len(applicable_rules))
        if(len(applicable_rules)==0):
            self.set_context_scope(naoDialogModel,naoDialogContext, None)#reset child rules
            applicable_rules=self.get_child_rules(naoDialogModel,naoDialogContext.current_scope_parent_id)#only root rules
            self.debug("[find_applicable_rules]---- no applicable rules found. leats search in parent rules only", len(applicable_rules))
        return applicable_rules
        

    def find_response(self, naoDialogModel, naoDialogContext, aPhrase):
        phrase = aPhrase.strip().lower()
        naoDialogResponse = NaoDialogResponse()
        naoDialogResponse.naoDialogContext = naoDialogContext

        self.debug("[find_response]naoDialogContext: ++++++++++++++++++++++++++++++++++++++ phrase: {} +++++ naoDialogContext: {}".format(phrase, str(naoDialogContext)))

        applicable_rules = self.find_applicable_rules(naoDialogModel, naoDialogContext)
        
        # print("previous_rule: ", str(previous_rule))
        # print("applicable_rules: ", str(applicable_rules))

        
        for aRule in applicable_rules:
            if phrase in aRule.userIntentArr:
                naoDialogResponse.responseText=self.generate_response(naoDialogModel, naoDialogContext, aRule)
                if("^activate" in aRule.instructionDict):
                    instructionParam = aRule.instructionDict["^activate"]
                    rulesWithTags = self.get_rules_by_tag(naoDialogModel, instructionParam)
                    if(len(rulesWithTags)>0):
                        self.debug("[find_response] activating by tag {} another rule {}".format(instructionParam, rulesWithTags))
                        naoDialogResponse.responseText= naoDialogResponse.responseText + ". " + self.generate_response(naoDialogModel, naoDialogContext, rulesWithTags[0])
                        self.set_context_scope(naoDialogModel,naoDialogContext, rulesWithTags[0])
                    else:
                        self.debug("[find_response] we should activate tag {} but no rules fount".format(instructionParam))
                        self.set_context_scope(naoDialogModel,naoDialogContext, aRule)
                else:
                    self.set_context_scope(naoDialogModel,naoDialogContext, aRule)
                naoDialogResponse.ruleId = aRule.id
                naoDialogContext.previous_rules.append(aRule)
                
                if(aRule.eventValue):
                    naoDialogResponse.eventValue = aRule.eventValue
                # self.debug("[find_response] matched aRule", str(aRule))
                break

        if len(naoDialogResponse.responseText)==0:
            self.debug("[find_response] Response not found")
            if NaoDialogModel.EVENT_FALLBACK in naoDialogModel.dialog_event_dict:
                aRule = naoDialogModel.dialog_event_dict[NaoDialogModel.EVENT_FALLBACK]
                naoDialogResponse.responseText=self.generate_response(naoDialogModel, naoDialogContext, aRule)
                naoDialogResponse.ruleId = aRule.id

        self.debug("[find_response] ------ Responose:: ", str(naoDialogResponse))

        return naoDialogResponse
 
