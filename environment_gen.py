import os
import os.path
import json
import random
import shutil
import typing

import numpy as np
from typing import Union

from procthor_v2.generation.agent import generate_starting_pose
from procthor_v2.utils.types import LeafRoom, MetaRoom
from procthor_v2.generation import HouseGenerator, RoomSpec, PROCTHOR10K_ROOM_SPEC_SAMPLER


def _load_json(file_path):
    with open(file_path) as json_file:
        return json.load(json_file)


def _dict_to_json(string, _dict):
    with open(f"{string}", "w") as convert_file:
        convert_file.write(json.dumps(_dict))


def _load_json_from_database(json_file: str) -> Union[list, dict]:
    dirname = os.path.dirname(__file__)
    filepath = os.path.join(dirname, json_file)
    with open(filepath, "r") as f:
        return json.load(f)


def _get_object_in_receptacles():
    return _load_json_from_database("procthor_v2/databases/receptacles.json")


def _get_object_from_database():
    return _load_json_from_database("procthor_v2/databases/asset-database.json")


def _check_distance(a: dict, b: dict, distance: int, chiave: str):
    if np.abs(a['position']['x'] - b['position']['x']) > distance or np.abs(
            a['position']['y'] - b['position']['y']) > distance:
        return False
    if np.square(distance) > (
            np.square(a['position']['x'] - b['position']['x']) + np.square(a['position']['y'] - b['position']['y'])):
        return chiave


def _random_with_N_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return random.randint(range_start, range_end)


def _add_huric_info(dizionario, data):
    procthor_objects = _load_json("translation/procthor_objects.json")
    objs = dizionario['objects']
    for elem in data['windows']:
        elem["huric_id"] = "finestra_" + str(_random_with_N_digits(13))
        elem["lexical_reference"] = ["finestra"]
    for elem in data['doors']:
        elem["huric_id"] = "porta_" + str(_random_with_N_digits(13))
        elem["lexical_reference"] = ["porta"]
    for elem in data['objects']:
        if elem["assetType"] in list(objs.keys()):
            elem["huric_id"] = objs[elem["assetType"]]["atom"]
            elem["lexical_reference"] = objs[elem["assetType"]]["lexical_reference"]
            elem["contain_ability"] = objs[elem["assetType"]]["contain_ability"]
            elem["support_ability"] = objs[elem["assetType"]]["support_ability"]
        else:
            elem["huric_id"] = elem["assetType"] + "_" + str(_random_with_N_digits(13))
            for k, v in procthor_objects.items():
                if elem["assetType"] == k:
                    elem["lexical_reference"] = v["lexical_reference"]
                    elem["contain_ability"] = v["contain_ability"]
                    elem["support_ability"] = v["support_ability"]
        if "children" in elem.keys():
            for child in elem['children']:
                if child["assetType"] in list(objs.keys()):
                    child["huric_id"] = objs[child["assetType"]]["atom"]
                    child["lexical_reference"] = objs[child["assetType"]]["lexical_reference"]
                    child["contain_ability"] = objs[child["assetType"]]["contain_ability"]
                    child["support_ability"] = objs[child["assetType"]]["support_ability"]
                else:
                    child["huric_id"] = child["assetType"] + "_" + str(_random_with_N_digits(13))
                    for k, v in procthor_objects.items():
                        if child["assetType"] == k:
                            child["lexical_reference"] = v["lexical_reference"]
                            child["contain_ability"] = v["contain_ability"]
                            child["support_ability"] = v["support_ability"]


def _rooms_generator(dizionario: dict):
    leafRoom_list = []
    id_room = 2
    for i in range(dizionario['rooms']["Kitchen"]):
        leafRoom_list.append(LeafRoom(room_id=id_room, ratio=2, room_type="Kitchen"))
        id_room = id_room + 1
    for i in range(dizionario['rooms']["LivingRoom"]):
        leafRoom_list.append(LeafRoom(room_id=id_room, ratio=2, room_type="LivingRoom"))
        id_room = id_room + 1
    for i in range(dizionario['rooms']["Bedroom"]):
        leafRoom_list.append(LeafRoom(room_id=id_room, ratio=1, room_type="Bedroom"))
        id_room = id_room + 1
    for i in range(dizionario['rooms']["Bathroom"]):
        leafRoom_list.append(LeafRoom(room_id=id_room, ratio=1, room_type="Bathroom"))
        id_room = id_room + 1
    return leafRoom_list


def environment_generator(dizionario: dict, stanza: str):
    spec = [MetaRoom(ratio=1, children=_rooms_generator(dizionario))]
    house_project = RoomSpec(room_spec_id="my_house", sampling_weight=2, spec=spec)

    room_obj = {}
    for k, v in dizionario['objects'].items():
        if k in _get_object_in_receptacles():
            room_obj[k] = {'position': v["position"], 'contain': [other_v for other_v in dizionario['objects'].keys()
                                                                  if dizionario['objects'][other_v]["position"] == v[
                                                                      "position"] and other_v != k]}
        elif k in _get_object_from_database():
            room_obj[k] = {'position': v["position"], 'contain': []}

    house_generator = HouseGenerator(
        split="train", seed=random.randrange(2 ** 32 - 1), room_spec=house_project,
        room_spec_sampler=PROCTHOR10K_ROOM_SPEC_SAMPLER, object_list=room_obj
    )
    house, _ = house_generator.sample()
    house.validate(house_generator.controller)

    huric_num = {"id": dizionario['id']}
    house.data.update(huric_num)

    """
       Check se bisogna inserire il robot nella stanza "opposta" a quella
       descritta nella "sentence" 
    """
    if stanza != "":
        for room in house.data["rooms"]:
            if room["roomType"] != stanza:
                num = int(room["id"][-1])
                pose = {num: house.rooms.get(num)}
                house.data["metadata"]["agent"] = generate_starting_pose(pose)

    """
       Aggiunta delle info presenti nel file huric per ogni oggetto presente nell' ambiente.
       Per gli oggetti descritti nel file huric viene mantenuto lo stesso id (atom).
       Per gli altri oggetti viene generato in maniera randomica mantenendo lo stesso stile "dell'atom".
    """

    _add_huric_info(dizionario, house.data)

    """
       Check e creazione delle cartelle per il salvataggio delle immagini e del file json.
    """

    if not os.path.exists("dataset"):
        os.mkdir("dataset")
    if os.path.exists(f"dataset/{dizionario['id']}"):
        shutil.rmtree(f"dataset/{dizionario['id']}")
    if not os.path.exists(f"dataset/{dizionario['id']}"):
        os.mkdir(f"dataset/{dizionario['id']}")
    _dict_to_json(f"dataset/{dizionario['id']}/gen_{dizionario['id']}.json", house.data)
    shutil.copyfile(f"huric/it/{dizionario['id']}.hrc", f"dataset/{dizionario['id']}/{dizionario['id']}.hrc")

    return house.data
