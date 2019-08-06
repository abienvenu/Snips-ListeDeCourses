#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions


def add_item(item):
    return "Ok, il faut ajouter {}".format(item)


def intent_callback(hermes, intent_message):
    intent_name = intent_message.intent.intent_name.replace("abienvenu:", "")
    result = None
    if intent_name == "addItem":
        result = add_item(intent_message.slots.Item.first().value)

    if result is not None:
        hermes.publish_end_session(intent_message.session_id, result)


if __name__ == "__main__":
    mqtt_opts = MqttOptions()
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intents(intent_callback).start()
