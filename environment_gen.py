import os
import os.path
import json
import random
import shutil
import numpy as np
from typing import Union
from procthor_v2.utils.types import LeafRoom, MetaRoom
from procthor_v2.generation import HouseGenerator, RoomSpec, PROCTHOR10K_ROOM_SPEC_SAMPLER


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


def environment_generator(dizionario: dict):
    spec = [MetaRoom(ratio=1, children=_rooms_generator(dizionario))]
    house_project = RoomSpec(room_spec_id="my_house", sampling_weight=2, spec=spec)

    room_obj = {}
    for k, v in dizionario['objects'].items():
        # print(f"{k}->{v}")
        if k in _get_object_in_receptacles():
            room_obj[k] = {'position': v["position"], 'contain': [other_v for other_v in dizionario['objects'].keys()
                                                                  if dizionario['objects'][other_v]["position"] == v[
                                                                      "position"] and other_v != k]}
    new_room_obj = {}
    for k, v in room_obj.items():
        new_room_obj[k] = {'near': [_check_distance(v, v2, 2, k2) for k2, v2 in room_obj.items() if
                                    room_obj[k] != room_obj[k2]]}
        if None in new_room_obj[k]['near']: new_room_obj[k]['near'] = list(filter(None.__ne__, new_room_obj[k]['near']))
        if False in new_room_obj[k]['near']: new_room_obj[k]['near'] = list(
            filter(False.__ne__, new_room_obj[k]['near']))
        room_obj[k].update(new_room_obj[k])

    print(room_obj)

    house_generator = HouseGenerator(
        split="train", seed=random.randrange(2 ** 32 - 1), room_spec=house_project,
        room_spec_sampler=PROCTHOR10K_ROOM_SPEC_SAMPLER, object_list=room_obj
    )
    house, _ = house_generator.sample()
    house.validate(house_generator.controller)
    huric_id = {"id": dizionario['id']}
    house.data.update(huric_id)

    objs = dizionario['objects']
    for elem in house.data['objects']:
        if elem in list(objs.keys()):
            elem["huric_id"] = objs["atom"]
        else:
            elem["huric_id"] = elem["assetId"] + "_" + str(_random_with_N_digits(13))

    if not os.path.exists("dataset"):
        os.mkdir("dataset")
    if os.path.exists(f"dataset/{dizionario['id']}"):
        shutil.rmtree(f"dataset/{dizionario['id']}")
    if not os.path.exists(f"dataset/{dizionario['id']}"):
        os.mkdir(f"dataset/{dizionario['id']}")
    _dict_to_json(f"dataset/{dizionario['id']}/gen_{dizionario['id']}.json", house.data)
    # nome_file_json = f"{uuid.uuid4()}.json"
    # dict_to_json(f"{nome_file_json}", house.data)
    # name_img = f"room_seed_{house_generator.seed}.png"
    # (get_top_down_frame(house_generator.controller, house.data)
    #  .save(f"/Users/daniilmastrangeli/Desktop/progettoFinaleBasili/immagini/{name_img}"))
    # return (nome_file_json, name_img)
    return house.data
