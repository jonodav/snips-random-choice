#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
import socket
import random

CONFIG_INI = "config.ini"

# If this skill is supposed to run on the satellite,
# please get this mqtt connection info from <config.ini>
# Hint: MQTT server is always running on the master device
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

class RandomChoice(object):
    """Class used to wrap action code with mqtt connection
        
        Please change the name refering to your application
    """

    def __init__(self):
        # get the configuration if needed
        try:
            self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
        except :
            self.config = None

        # start listening to MQTT
        self.start_blocking()

    def extract_options(self, intent_message):
        extractedOptions = []
        if intent_message.slots.options:
            for option in intent_message.slots.options.all():
                print type(option.value)
                extractedOptions.append(option.value)
        return extractedOptions
        
    # --> Sub callback function, one per intent
    def choiceCallback(self, hermes, intent_message):
        # terminate the session first if not continue
        #hermes.publish_end_session(intent_message.session_id, "")

        # action code goes here...
        print '[Received] intent: {}'.format(intent_message.intent.intent_name)

        options = self.extract_options(intent_message)
        hasadjective = False

        for (slot_value, slot) in intent_message.slots.items():
            if slot_value == "adjective":
                self.adjective = slot.first().value.encode("utf8")
                hasadjective = True
        
        if(hasadjective):
            tts = random.choice(options) + " is " + self.adjective
        else:
            tts = random.choice(options)
        hermes.publish_end_session(intent_message.session_id, tts)

    # --> Master callback function, triggered everytime an intent is recognized
    def master_intent_callback(self,hermes, intent_message):
        coming_intent = intent_message.intent.intent_name
        if coming_intent == 'thejonnyd:randomChoice':
            self.choiceCallback(hermes, intent_message)

        # more callback and if condition goes here...

    # --> Register callback function and start MQTT
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intents(self.master_intent_callback).start()
 
if __name__ == "__main__":
    RandomChoice()
