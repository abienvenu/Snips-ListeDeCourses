#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import configparser
import io
import requests
from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions


class SnipsConfigParser(configparser.SafeConfigParser):
    def to_dict(self):
        return {
            section: {
                option_name: option
                for option_name, option in self.items(section)
            }
            for section in self.sections()
        }


def read_configuration_file():
    try:
        with io.open(
            "config.ini",
            encoding="utf-8"
        ) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, configparser.Error):
        return dict()


def load_list():
    try:
        with open("liste.txt", "r") as infile:
            return set(json.load(infile))
    except IOError:
        return set()


def save_list(data):
    with open("liste.txt", "w") as outfile:
        json.dump(list(data), outfile)


def add_item(item):
    liste = load_list()
    if item in liste:
        return "Il y a déjà {} sur la liste de courses".format(item)
    liste.add(item)
    save_list(liste)
    return "J'ai ajouté {} sur la liste de courses".format(item)


def del_item(item):
    liste = load_list()
    if item not in liste:
        return "Il n'y a pas de {} sur la liste de courses".format(item)
    liste.remove(item)
    save_list(liste)
    return "J'ai supprimé {} de la liste de courses".format(item)


def get_list():
    liste = load_list()
    if not liste:
        return "La liste de courses est vide"
    return "Voici ce qu'il y a sur la liste de courses: {}".format(
        ", ".join(liste))


def del_list():
    save_list(set())
    return "J'ai purgé la liste de courses"


def send_sms():
    liste = load_list()
    if not liste:
        return "La liste de courses est vide"
    config = read_configuration_file()
    smsData = {
        "user": config['secret']['identifiant_free'],
        "pass": config['secret']['cle_identification'],
        "msg": "Liste de courses: {}".format(", ".join(liste))
    }
    try:
        response = requests.get(
            "https://smsapi.free-mobile.fr/sendmsg",
            params=smsData,
            timeout=2
        )
    except requests.exceptions.Timeout:
        return "Le service SMS de free ne répond pas"

    code = response.status_code
    if code == 200:
        return "J'ai envoyé la liste de courses par SMS"
    elif code == 402:
        return "Désolé, je ne peux pas envoyer trop de SMS"
    elif code == 403:
        return "Le service n'est pas activé sur l'espace abonné, "
        "ou le login ou la clé sont incorrects"
    elif code == 500:
        return "Désolé, le service SMS de Free est dans les choux"
    else:
        return "Désolé, l'envoi du SMS a échoué avec l'erreur {}".format(
            response.status_code)


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
