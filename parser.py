from procthor_v2.databases import DEFAULT_PROCTHOR_DATABASE

import xml.etree.ElementTree as ET
import numpy as np
import random
import json


def _load_json(file_path):
    with open(file_path) as json_file:
        return json.load(json_file)


def _find_key(dizionario: dict, value: str) -> (bool, str):
    valore_minuscolo = value.lower()
    for chiave, val in dizionario.items():
        if valore_minuscolo in val or valore_minuscolo.capitalize() in val:
            return True, chiave
    return False, ""


def _choose_random_room(escludi_stanza, dizionario: dict):
    rooms = list(dizionario['rooms'].keys())
    if escludi_stanza in rooms:
        rooms.remove(escludi_stanza)
    choosen_room = random.choice(rooms)
    return choosen_room


def _check_rooms(dizionario: dict):
    return np.unique(list(dizionario.values())).size == 1


def xml_parser(file_path: str) -> dict:
    tree = ET.parse(file_path)
    root = tree.getroot()

    pt_db = DEFAULT_PROCTHOR_DATABASE

    traduttoreStanze = _load_json("translation/traduttore_stanze.json")
    traduttoreOggetti = _load_json("translation/traduttore_oggetti.json")
    dizionario = {'rooms': {"Kitchen": 0, "LivingRoom": 0, "Bedroom": 0, "Bathroom": 0}, 'objects': {}}
    dizionario.update(root.attrib)

    surface_list = []
    tokens_elements = root.findall('.//tokens')
    for tokens in tokens_elements:
        for token in tokens:
            pos = token.get('pos')
            if pos.lower() == "s":
                surface = token.get('surface')
                if _find_key(traduttoreStanze, surface)[0]:
                    dizionario['rooms'][_find_key(traduttoreStanze, surface)[1]] += 1
                    valore = _choose_random_room(_find_key(traduttoreStanze, surface)[1], dizionario)
                    dizionario['rooms'][valore] += 1

                surface_trad = next((k for k, v in traduttoreOggetti.items() if surface.capitalize() in v), "")
                surface_list.append(surface_trad)

    if _check_rooms(dizionario['rooms']):
        for elem in surface_list:
            if elem.capitalize() in ["Television"]:
                dizionario['rooms']["LivingRoom"] += 1
            elif elem.capitalize() in pt_db.ASSET_DATABASE:
                room_annotations = {
                    "inKitchens": "Kitchen",
                    "inLivingRooms": "LivingRoom",
                    "inBedrooms": "Bedroom",
                    "inBathrooms": "Bathroom"
                }
                possible_room = []
                for room_type, room_name in room_annotations.items():
                    for k, v in pt_db.PLACEMENT_ANNOTATIONS[room_type].items():
                        if k == elem and v > 0:
                            possible_room.append(room_name)

                if possible_room:
                    room = random.choice(possible_room)
                    dizionario['rooms'][room] += 1

    semantic_elements = root.findall('.//entities')

    for semantic_element in semantic_elements:
        entity_elements = semantic_element.findall('.//entity')
        for entity_element in entity_elements:
            entity_type = entity_element.get('type')
            entity_id = entity_element.get('atom')
            if _find_key(traduttoreStanze, entity_type)[0] and dizionario['rooms'][_find_key(traduttoreStanze, entity_type)[1]] == 0:
                dizionario['rooms'][_find_key(traduttoreStanze, entity_type)[1]] += 1
            if entity_type not in ["Madre", "Luce", "Fuori", "Mucchio"]:
                for k, v in traduttoreOggetti.items():
                    if entity_type in v:
                        entity_type = k
                obj = {'atom': entity_id, 'lexical_reference': []}
                for lexical_ref_elem in entity_element.find(".//attribute[@name='lexical_references']"):
                    if lexical_ref_elem is not None:
                        obj['lexical_reference'].append(lexical_ref_elem.text)

                support_ability_elem = entity_element.find(".//attribute[@name='support_ability']/value")
                if support_ability_elem is not None:
                    obj['support_ability'] = support_ability_elem.text

                contain_ability_elem = entity_element.find(".//attribute[@name='contain_ability']/value")
                if contain_ability_elem is not None:
                    obj['contain_ability'] = contain_ability_elem.text

                coordinate_elem = entity_element.find('coordinate')
                if coordinate_elem is not None:
                    obj['position'] = {
                        'x': float(coordinate_elem.get('x')),
                        'y': float(coordinate_elem.get('y')),
                        'z': float(coordinate_elem.get('z'))
                    }
                dizionario['objects'][entity_type] = obj
    print(dizionario)
    return dizionario
