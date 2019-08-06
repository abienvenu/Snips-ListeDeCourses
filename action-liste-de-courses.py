#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions


def add_item(item):
    return "Ok, il faut ajouter {} sur la liste de courses".format(item)


def del_item(item):
    return "Ok, il ne faut plus acheter de {}".format(item)


def get_list():
    return "Voici ce qu'il y a sur la liste de courses"


def del_list():
    return "Il faut purger la liste de courses"


def send_sms():
    return "Il faut envoyer la liste par SMS"


def intent_callback(hermes, intent_message):
    intent_name = intent_message.intent.intent_name.replace("abienvenu:", "")
    result = None
    if intent_name == "addItem":
        result = add_item(intent_message.slots.Item.first().value)
    if intent_name == "delItem":
        result = del_item(intent_message.slots.Item.first().value)
    if intent_name == "getList":
        result = get_list()
    if intent_name == "delList":
        result = del_list()
    if intent_name == "sendSMS":
        result = send_sms()

    if result is not None:
        hermes.publish_end_session(intent_message.session_id, result)


if __name__ == "__main__":
    mqtt_opts = MqttOptions()
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intents(intent_callback).start()
