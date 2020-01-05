#!/usr/bin/env python3
# -*- coding: utf-8 -*-


'''
@author: Mindaugas Greibus
parses Nao dialog file
'''

import re 
import shlex
import libot.nao_dialog_model as nao_dialog_model


class NaoDialogTrainContext:
    def __init__(self):
        self.next_id=0
        # previous_parent_id=None
        self.rule_level_arr=[]
        self.previous_rule_level=None

class NaoDialogTrainer:

    def __init__(self):
        self.topicRE = re.compile(r'^topic\:(.*)$')#topic: ~test_dialog()
        self.languageRE = re.compile(r'^language\:(.*)$')#language: Lithuanian
        self.conceptRE = re.compile(r'^concept\:\((.+)\) \^rand\[(.+)\]') #concept:(greetings) ^rand[sveiki "laba diena"]
        self.ruleRE = re.compile(r'^u\:\((.+)\)(.+)') #u:(Labas) Sveiki
        self.proposalRE = re.compile(r'^proposal\:(.+)') #proposal: %game1 ar mėgsti krepšinį
        self.subRuleRE = re.compile(r'^u(\d)\:\((.+)\)(.+)') #u1:(šunį) ar didelis?
        self.eventValueRE = re.compile(r'^(.*)\$libotserviceevent=(.*)$') #pamiršau laikrodį $libotserviceevent=pamiršau laikrodį
        self.trainContext = NaoDialogTrainContext()
        self.instructionsDict ={
            self.topicRE: self.parseTopic,
            self.languageRE: self.parseLanguage,
            self.conceptRE: self.parseConcept,
            self.ruleRE: self.parseRule,
            self.proposalRE: self.parseProposal,
            self.subRuleRE: self.parseSubrule,
        }

    def debug(self, *values):
        print(values)
        pass

    def parseTopic(self, naoDialogModel, trainCtx, line, topic_name):
        #topic: ~test_dialog()
        if(topic_name):
            return True
        return False

    def parseLanguage(self, naoDialogModel,trainCtx, line, lang_name):
        #language: Lithuanian
        if(lang_name):
            return True
        return False

    def parseConcept(self, naoDialogModel, trainCtx,  line, aConeptKey, aConceptValue):
        #concept:(greetings) ^rand[sveiki "laba diena"]
        coneptKey=aConeptKey.strip().lower()
        conceptValue=aConceptValue.strip().lower()
        conceptValueArr = shlex.split(conceptValue)
        naoDialogModel.conceptDict[coneptKey]=conceptValueArr
        # return (coneptKey, conceptValueArr)
        return True


    def parseProposal(self, naoDialogModel, trainCtx, line, aBotResponse):
        # id, parent_id,
        # userIntent = aUserIntent.strip().lower()
        botResponse = aBotResponse.strip().lower()
        naoRuleEntry = self.parseRuleFormat(naoDialogModel=naoDialogModel, 
            id="r"+str(trainCtx.next_id), parent_id="", 
            userIntent="", 
            botResponse=botResponse)
        trainCtx.rule_level_arr=["r"+str(trainCtx.next_id)]
        trainCtx.previous_rule_level=0
        trainCtx.next_id=trainCtx.next_id+1                
        naoDialogModel.dialog_rules.append(naoRuleEntry)
        return True


    def parseRule(self, naoDialogModel, trainCtx, line, aUserIntent, aBotResponse):
        # id, parent_id,
        userIntent = aUserIntent.strip().lower()
        botResponse = aBotResponse.strip().lower()
        naoRuleEntry = self.parseRuleFormat(naoDialogModel=naoDialogModel, 
            id="r"+str(trainCtx.next_id), parent_id="", 
            userIntent=userIntent, 
            botResponse=botResponse)
        trainCtx.rule_level_arr=["r"+str(trainCtx.next_id)]
        trainCtx.previous_rule_level=0
        trainCtx.next_id=trainCtx.next_id+1
        if(nao_dialog_model.NaoDialogModel.EVENT_FALLBACK.lower() == userIntent):
            self.debug("Adding new event: ", str(naoRuleEntry))
            naoDialogModel.dialog_event_dict[nao_dialog_model.NaoDialogModel.EVENT_FALLBACK]=naoRuleEntry
        else:                 
            naoDialogModel.dialog_rules.append(naoRuleEntry)
        return True



    def parseSubrule(self, naoDialogModel, trainCtx, line, aRuleLevel, aUserIntent, aBotResponse):
        current_rule_level = int(aRuleLevel.strip().lower())
        userIntent = aUserIntent.strip().lower()
        botResponse = aBotResponse.strip().lower()
        previous_parent_id = None
        # print("intial rule_level_arr: {} previous_rule_level({})==current_rule_level({})".format(rule_level_arr, previous_rule_level, current_rule_level))
        if(trainCtx.previous_rule_level==current_rule_level):
            # print("sampel level. Removing previous sibling {}".format(rule_level_arr[-1]))
            trainCtx.rule_level_arr=trainCtx.rule_level_arr[:-1]
        elif((trainCtx.previous_rule_level+1)==current_rule_level):
            # print("New level. leavae level array as is. last parent should be {}".format(rule_level_arr[-1]))
            pass
        elif((trainCtx.previous_rule_level-1)==current_rule_level):
            # print("One level up. removing two last elements: {} and {}".format(rule_level_arr[:-2], rule_level_arr[:-1]))
            trainCtx.rule_level_arr= trainCtx.rule_level_arr[:-2]
        else:
            # print("corupted file. Current level {} does not match previous {}".format(current_rule_level, str(rule_level_arr)))
            raise Exception("wrong file current level {} does not match previous {}".format(current_rule_level, str(trainCtx.rule_level_arr))) 
        previous_parent_id=trainCtx.rule_level_arr[-1]
        
        # print("parent_id:{} userIntent:{} levels:{}".format(previous_parent_id, userIntent, rule_level_arr))

        naoRuleEntry = self.parseRuleFormat(naoDialogModel=naoDialogModel, 
            id="r"+str(trainCtx.next_id), parent_id=previous_parent_id, 
            userIntent=userIntent, 
            botResponse=botResponse)
        trainCtx.rule_level_arr.append("r"+str(trainCtx.next_id))
        trainCtx.next_id=trainCtx.next_id+1
        trainCtx.previous_rule_level=current_rule_level
        # print("Adding subrule... {}<--{}[{}] ".format(naoRuleEntry.parent_id, naoRuleEntry.id, userIntent))
        
        naoDialogModel.dialog_rules.append(naoRuleEntry)
        return True

    def train(self, dialogStr):
        # dialog_resouces = []
        naoDialogModel = nao_dialog_model.NaoDialogModel()
        # next_id=0
        # # previous_parent_id=None
        # rule_level_arr=[]
        # previous_rule_level=None
        self.trainContext = NaoDialogTrainContext()

        for line in dialogStr.split("\n"):
            line = line.strip().lower().strip()

            if(len(line)==0):
                #noop
                continue

            if(line.startswith("#")):
                #noop
                continue

            self.debug("----------------------------------- {} ----------- ".format(line))

            lineProcessed = False
            for keyRegEx in self.instructionsDict:
                match = keyRegEx.match( line )
                if(match):
                    instructionFunc = self.instructionsDict[keyRegEx]
                    args = match.groups()
                    self.debug("Call ", str(instructionFunc))
                    result = instructionFunc(naoDialogModel, self.trainContext, line, *args)
                    self.debug("Call result:", result)
                    lineProcessed=True
                    continue
                    
            if(lineProcessed):
                continue

            print("Unprocessed: ", line)

        naoDialogModel.dialog_responses_dict = {}
        # for entry in naoDialogModel.dialog_resouces:
        #     naoDialogModel.dialog_responses_dict[entry["key"]]=entry

        return naoDialogModel

    def parseRuleFormat(self, naoDialogModel, id, parent_id, userIntent, botResponse):
        conceptUserKey=userIntent.strip("~")
        conceptBotKey=botResponse.strip("~")
        userIntentArr=[]
        botResponseArr=[]
        eventValue=None
        instructionDict={}
        tag=None
        if(conceptUserKey in naoDialogModel.conceptDict):
            userIntentArr = naoDialogModel.conceptDict[conceptUserKey]
        else:
            userIntentArr.append(userIntent)
        
        if(conceptBotKey in naoDialogModel.conceptDict):
            botResponseArr = naoDialogModel.conceptDict[conceptBotKey]
        else:
            iBotResponse = botResponse

            eventMatch=self.eventValueRE.match(iBotResponse)
            if(eventMatch):
                iBotResponse = eventMatch.group(1).strip()
                eventValue=eventMatch.group(2).strip()

            instructuctionMatch=re.compile(r'^(.*)(\^stayinscope)$').match(iBotResponse)
            if(instructuctionMatch):
                iBotResponse = instructuctionMatch.group(1).strip()
                instructuction=instructuctionMatch.group(2).strip()
                instructionDict[instructuction]=""

            instructuctionMatch=re.compile(r'^(.*)(\^activate)\((.*)\)$').match(iBotResponse)
            if(instructuctionMatch):
                iBotResponse = instructuctionMatch.group(1).strip()
                instructuction=instructuctionMatch.group(2).strip()
                instructuctionParam=instructuctionMatch.group(3).strip()
                instructionDict[instructuction]=instructuctionParam

            tagMatch=re.compile(r'^%([a-z0-9]*) (.*)$').match(iBotResponse)
            if(tagMatch):
                tag=tagMatch.group(1).strip()
                iBotResponse = tagMatch.group(2).strip()

            botResponseArr.append(iBotResponse)

        # print("[parseUter]", userIntentArr, botResponseArr)
        return nao_dialog_model.NaoRuleEntry().fill(id, parent_id, userIntentArr, botResponseArr,eventValue, instructionDict,tag)

    def generate_dialog_chart(self, naoDialogModel):
        """
        dot -Tps test.dot -o out.ps
        """
        #story = trained_data["story__intent_childs"]
        result = []
        
        activationDict={}
        tagDict={}
        
        #print(naoDialogModel.dialog_rules)
        for rule in naoDialogModel.dialog_rules:
            parent_node = rule.parent_id if rule.parent_id else "O"
            nodeLabel = rule.botResponseArr[0]
            if(rule.tag and len(rule.tag)>0):
                tagDict[rule.tag]=rule.id
                nodeLabel = nodeLabel + "|" + rule.tag
            if("^stayinscope" in rule.instructionDict):
                activationDict[rule.id]=rule.parent_id
            if("^activate" in rule.instructionDict):
                activateTag = rule.instructionDict["^activate"]
                activationDict[rule.id]=activateTag
            line = '{}[label="{{{}}}"]'.format(rule.id, nodeLabel)
            result.append(line)
            if(len(rule.userIntentArr[0])>0):
                line = '{} -> {}[label="{}"]'.format(parent_node, rule.id, rule.userIntentArr[0]) 
                result.append(line)
        
        for key in activationDict:
            node_id = key
            value_id = activationDict[key]
            if(value_id in tagDict):
                value_id = tagDict[value_id]
            line = '{} -> {}[color="#aaaaaa" constraint=true]'.format(node_id, value_id)
            result.append(line)


        result_str = "/*dot -Tpng t.dot -o out.png; eog out.png*/\n"+ \
            "digraph G {\n"+ \
            "\tnode [shape=record fontname=Arial];\n\t" + \
            ";\n\t".join(result)+";\n}"

        return result_str


