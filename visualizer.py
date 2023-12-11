import copy
import os.path
import json
import shutil

import numpy as np
from ai2thor.controller import Controller
from PIL import Image
from ai2thor.util.metrics import get_shortest_path_to_object
from matplotlib import pyplot as plt


def _dict_to_json(string, _dict):
    with open(f"{string}", "w") as convert_file:
        convert_file.write(json.dumps(_dict))


def add_images_to_obj(obj, inverted_dict):
    """ Aggiunge ai children. """
    obj_id = obj.get('id')
    if obj_id and obj_id in inverted_dict:
        obj['images'] = inverted_dict[obj_id]

    if 'children' in obj:
        for child in obj['children']:
            add_images_to_obj(child, inverted_dict)


def _add_photo_images(controller: Controller, house: dict, dicto: dict):
    # Creazione di un dizionario invertito
    inverted_dict = {}
    for image_name, objects in dicto.items():
        for obj_id, bbox in objects.items():
            inverted_dict.setdefault(obj_id, []).append({
                "image": image_name,
                "resolution": {"width": controller.width, "height": controller.height, "origin": "bottom left"},
                "bounding_box": bbox
            })

    for key in ['doors', 'objects', 'windows']:
        if key in house:
            for elem in house[key]:
                add_images_to_obj(elem, inverted_dict)
    _dict_to_json(f"dataset/{house['id']}/gen_{house['id']}.json", house)


def _add_images(elem):
    elem['images'] = []
    if 'children' in elem:
        for child in elem['children']:
            _add_images(child)


def _add_images_key(house):
    exclude_keys = ["rooms", "walls", "proceduralParameters", "metadata", "id"]

    for key, value in house.items():
        if key not in exclude_keys and isinstance(value, list):
            for elem in value:
                _add_images(elem)
    _dict_to_json(f"dataset/{house['id']}/gen_{house['id']}.json", house)


def _get_top_down_frame(data, controller: Controller, path: str, name: str):
    if not isinstance(controller, Controller):
        raise TypeError("You must pass a controller as an argument")
    # Setup the top-down camera
    event = controller.step(action="GetMapViewCameraProperties", raise_for_failure=True)
    controller.step(action="Teleport", **data["metadata"]["agent"])
    pose = copy.deepcopy(event.metadata["actionReturn"])

    bounds = event.metadata["sceneBounds"]["size"]
    max_bound = max(bounds["x"], bounds["z"])

    pose["fieldOfView"] = 50
    pose["position"]["y"] += 1.1 * max_bound
    pose["orthographic"] = False
    pose["farClippingPlane"] = 50
    del pose["orthographicSize"]

    # add the camera to the scene
    event = controller.step(
        action="AddThirdPartyCamera",
        **pose,
        skyboxColor="white",
        raise_for_failure=True,
    )
    Image.fromarray(event.third_party_camera_frames[-1]).save(path + name)

def _show_get_top_down_frame(data, controller: Controller):
    if not isinstance(controller, Controller):
        raise TypeError("You must pass a controller as an argument")
    # Setup the top-down camera
    event = controller.step(action="GetMapViewCameraProperties", raise_for_failure=True)
    controller.step(action="Teleport", **data["metadata"]["agent"])
    pose = copy.deepcopy(event.metadata["actionReturn"])

    bounds = event.metadata["sceneBounds"]["size"]
    max_bound = max(bounds["x"], bounds["z"])

    pose["fieldOfView"] = 50
    pose["position"]["y"] += 1.1 * max_bound
    pose["orthographic"] = False
    pose["farClippingPlane"] = 50
    del pose["orthographicSize"]

    # add the camera to the scene
    event = controller.step(
        action="AddThirdPartyCamera",
        **pose,
        skyboxColor="white",
        raise_for_failure=True,
    )
    Image.fromarray(event.third_party_camera_frames[-1]).show()
def _find_mid_point(coords):
    mid_x = sum(coord['x'] for coord in coords) / len(coords)
    mid_y = sum(coord['z'] for coord in coords) / len(coords)
    middle_point = {"x": mid_x, "z": mid_y}

    # Calculate distances and find the closest coordinate to the middle point
    closest_coord = None
    min_distance = float('inf')

    for coord in coords:
        distance = np.sqrt((coord['x'] - middle_point['x']) ** 2 + (coord['z'] - middle_point['z']) ** 2)
        if distance < min_distance:
            min_distance = distance
            closest_coord = coord
    return closest_coord


def show_reachable_position(controller, metadata, delta):
    if not isinstance(controller, Controller):
        raise TypeError("You must pass a controller as an argument")
    reachable_positions = controller.step(action="GetReachablePositions").metadata["actionReturn"]

    consecutive_tuples = [({'x': metadata["floorPolygon"][i]['x'], 'z': metadata["floorPolygon"][i]['z']},
                           {'x': metadata["floorPolygon"][i + 1]['x'], 'z': metadata["floorPolygon"][i + 1]['z']})
                          for i in range(len(metadata["floorPolygon"]) - 1)]
    consecutive_tuples.append(({'x': metadata["floorPolygon"][-1]['x'], 'z': metadata["floorPolygon"][-1]['z']},
                               {'x': metadata["floorPolygon"][0]['x'], 'z': metadata["floorPolygon"][0]['z']}))

    good_points = []
    for index, coord in enumerate(consecutive_tuples):
        good_coord = []
        x0 = coord[0]['x']
        z0 = coord[0]['z']
        x1 = coord[1]['x']
        z1 = coord[1]['z']
        x, x_delta, z, z_delta = 0, 0, 0, 0

        if x0 == x1:
            if z0 < z1:
                z = z0
                z_delta = z + delta
                x = x0
                x_delta = x + delta
            else:
                z = z0
                z_delta = z - delta
                x = x0
                x_delta = x - delta
        if z0 == z1:
            if x0 < x1:
                x = x0
                x_delta = x + delta
                z = z0
                z_delta = z - delta
            else:
                x = x0
                x_delta = x - delta
                z = z0
                z_delta = z + delta

        if x_delta > x:
            if z > z_delta:
                for elem in reachable_positions:
                    if x <= elem['x'] <= x_delta and z_delta <= elem['z'] <= z:
                        good_coord.append(elem)

            else:
                for elem in reachable_positions:
                    if x <= elem['x'] <= x_delta and z <= elem['z'] <= z_delta:
                        good_coord.append(elem)
        else:
            if z > z_delta:
                for elem in reachable_positions:
                    if x_delta <= elem['x'] <= x and z_delta <= elem['z'] <= z:
                        good_coord.append(elem)
            else:
                for elem in reachable_positions:
                    if x_delta <= elem['x'] <= x and z <= elem['z'] <= z_delta:
                        good_coord.append(elem)

        if len(good_coord) > 0:
            point = _find_mid_point(good_coord)
            xs = point['x']
            zs = point['z']
            plt.scatter(xs, zs, color="green")
            good_points.append(point)
    return good_points


def get_bounding_box(controller):
    dict = {}
    obj_frame_list = list(controller.last_event.instance_detections2D.instance_masks.keys())
    obj_list = []

    for obj in controller.last_event.metadata["objects"]:
        if not obj['objectType'] == 'Wall' and not obj['objectType'] == 'Floor':
            obj_list.append(obj['name'])

    matching_items = [item for item in obj_frame_list if item in obj_list]
    frame = controller.last_event.frame.copy()
    # print(f"lista immagini foto -> {matching_items}")
    for obj in matching_items:
        (x1, y1, x2, y2) = controller.last_event.instance_detections2D[obj]
        color = list(np.random.choice(range(256), size=3))
        dict[obj] = {'x1:': x1, 'y1': y1, 'x2': x2, 'y2': y2}
        frame[y1, x1:x2] = color
        frame[y2, x1:x2] = color
        frame[y1:y2, x1] = color
        frame[y1:y2, x2] = color

    return frame, dict


def visualize(house_data):
    if os.path.exists(f"dataset/{house_data['id']}/images"):
        shutil.rmtree(f"dataset/{house_data['id']}/images")
    if not os.path.exists(f"dataset/{house_data['id']}/images"):
        os.mkdir(f"dataset/{house_data['id']}/images")

    controller = Controller(

        agentMode="default",
        visibilityDistance=1.5,
        scene=house_data,

        # step sizes
        gridSize=0.25,
        snapToGrid=False,
        rotateStepDegrees=15,

        # image modalities
        renderDepthImage=False,
        renderInstancesSegmentation=False,

        # camera properties
        width=600,
        height=600,
        fieldOfView=90
    )

    controller.reset(scene=house_data, renderInstanceSegmentation=True)
    controller.step(action="Teleport", **house_data["metadata"]["agent"])
    _get_top_down_frame(house_data, controller, f"dataset/{house_data['id']}/images",
                        f"/{house_data['id']}_top_down.png")

    reachable_positions = controller.step(action="GetReachablePositions").metadata["actionReturn"]
    xs = [rp["x"] for rp in reachable_positions]
    zs = [rp["z"] for rp in reachable_positions]
    plt.scatter(xs, zs, color="red")
    dicto = {}
    # for o in house_data["objects"]:
    #     if "children" in o.keys():
    #         if len(o["children"]) > 0:
    #             event = controller.step(action='PositionsFromWhichItemIsInteractable', objectId=o["id"])
    #             x = event.metadata["actionReturn"]['x'][0]
    #             z = event.metadata["actionReturn"]['z'][0]
    #             rotation = event.metadata["actionReturn"]['rotation'][0]
    #             controller.step(action="Teleport", position={"x": x, "y": 0.95, "z": z}, rotation=rotation)
    #             frame = get_bounding_box(controller)
    #             Image.fromarray(frame[0]).show()

    for room in house_data["rooms"]:
        room_name = room["roomType"]
        if os.path.exists(f"dataset/{house_data['id']}/images/{room_name}"):
            shutil.rmtree(f"dataset/{house_data['id']}/images/{room_name}")
        if not os.path.exists(f"dataset/{house_data['id']}/images/{room_name}"):
            os.mkdir(f"dataset/{house_data['id']}/images/{room_name}")
            os.mkdir(f"dataset/{house_data['id']}/images/{room_name}/normal")
            os.mkdir(f"dataset/{house_data['id']}/images/{room_name}/bounding_box")
        pos = 0
        coords = show_reachable_position(controller, room, 1)
        for c in coords:
            if not os.path.exists(f"dataset/{house_data['id']}/images/{room_name}/normal/position_{pos}"):
                os.mkdir(f"dataset/{house_data['id']}/images/{room_name}/normal/position_{pos}")
            if not os.path.exists(f"dataset/{house_data['id']}/images/{room_name}/bounding_box/position_{pos}"):
                os.mkdir(f"dataset/{house_data['id']}/images/{room_name}/bounding_box/position_{pos}")
            controller.step("Teleport", position=c)
            step = 0
            while step < 360:
                controller.step(action="RotateRight", degrees=90)
                frame = get_bounding_box(controller)
                Image.fromarray(controller.last_event.frame).save(
                    f"dataset/{house_data['id']}/images/{room_name}/normal/position_{pos}/{house_data['id']}_{room_name}_pos_{pos}_{step}.jpg")
                Image.fromarray(frame[0]).save(
                    f"dataset/{house_data['id']}/images/{room_name}/bounding_box/position_{pos}/{house_data['id']}_{room_name}_bounding_box_pos_{pos}_{step}.jpg")
                dicto[f"images/{room_name}/bounding_box/position_{pos}/{house_data['id']}_{room_name}_bounding_box_pos_{pos}_{step}.jpg"] = frame[1]
                step += 90
            pos += 1
    plt.savefig(f"dataset/{house_data['id']}/images/{house_data['id']}_positions.jpg")

    _add_images_key(house_data)
    _add_photo_images(controller, house_data, dicto)

# TESTING NON CANCELLARE

# with open("dataset/4169/gen_4169.json") as json_file:
#     data = json.load(json_file)
#
# visualize(data)
