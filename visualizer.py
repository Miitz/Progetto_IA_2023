import copy
import os.path
import json
import shutil

import numpy as np
from ai2thor.controller import Controller
from PIL import Image
from matplotlib import pyplot as plt


def _dict_to_json(string, _dict):
    with open(f"{string}", "w") as convert_file:
        convert_file.write(json.dumps(_dict))


def _find_mid_point(max_val, min_val):
    return ((max_val - min_val) / 2) + min_val


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


def _setup_camera(controller: Controller, x, z, rotation, path, cam_index, house_data):
    camera = controller.step(
        action="AddThirdPartyCamera",
        position=dict(x=x, y=3, z=z),
        rotation=dict(x=45, y=rotation, z=0),
        fieldOfView=60,
        raise_for_failure=True,
    )

    # house_data["cameras"].update({f"camera_{cam_index}": []})

    Image.fromarray(camera.third_party_camera_frames[cam_index]).save(
        path + f"/{house_data['id']}_camera_{cam_index}.png")
    cam_index = cam_index + 1
    return cam_index


def _add_cameras(metadata, controller: Controller, path: str, house_data, cam_index: int):
    consecutive_tuples = [({'x': metadata["floorPolygon"][i]['x'], 'z': metadata["floorPolygon"][i]['z']},
                           {'x': metadata["floorPolygon"][i + 1]['x'], 'z': metadata["floorPolygon"][i + 1]['z']})
                          for i in range(len(metadata["floorPolygon"]) - 1)]
    consecutive_tuples.append(({'x': metadata["floorPolygon"][-1]['x'], 'z': metadata["floorPolygon"][-1]['z']},
                               {'x': metadata["floorPolygon"][0]['x'], 'z': metadata["floorPolygon"][0]['z']}))
    for index, coord in enumerate(consecutive_tuples):
        x0 = coord[0]['x']
        z0 = coord[0]['z']
        x1 = coord[1]['x']
        z1 = coord[1]['z']

        if x0 == x1:
            if z0 < z1:
                if z0 == 0.0 or z1 == 0.0:
                    cam_index = _setup_camera(controller, x0, z1 / 2, 90, path, cam_index, house_data)
                else:
                    cam_index = _setup_camera(controller, x0, _find_mid_point(z1, z0), 90, path, cam_index, house_data)
            else:
                if z0 == 0.0 or z1 == 0.0:
                    cam_index = _setup_camera(controller, x0, z0 / 2, 270, path, cam_index, house_data)
                else:
                    cam_index = _setup_camera(controller, x0, _find_mid_point(z0, z1), 270, path, cam_index, house_data)
        if z0 == z1:
            if x0 < x1:
                if x0 == 0.0 or x1 == 0.0:
                    cam_index = _setup_camera(controller, x1 / 2, z0, 180, path, cam_index, house_data)
                else:
                    cam_index = _setup_camera(controller, _find_mid_point(x1, x0), z0, 180, path, cam_index, house_data)
            else:
                if x0 == 0.0 or x1 == 0.0:
                    cam_index = _setup_camera(controller, x0 / 2, z0, 0, path, cam_index, house_data)
                else:
                    cam_index = _setup_camera(controller, _find_mid_point(x0, x1), z0, 0, path, cam_index, house_data)

    return cam_index


def show_reachable_position(controller, data):
    if not isinstance(controller, Controller):
        raise TypeError("You must pass a controller as an argument")
    reachable_positions = controller.step(action="GetReachablePositions").metadata["actionReturn"]

    coord = data["rooms"][0]["floorPolygon"]
    coord_x = data["rooms"][0]["floorPolygon"][3]["x"]
    coord_z = data["rooms"][0]["floorPolygon"][3]["z"]
    x_max = 3.825
    z_max = 3.825
    delta = 1
    if coord_x + delta > x_max:
        point_x = coord_x - delta
    else:
        point_x = coord_x + delta

    if coord_z + delta > z_max:
        point_z = coord_z - delta
    else:
        point_z = coord_z + delta
    good_coord = []
    for elem in reachable_positions:
        if point_x <= elem["x"] <= coord_x and coord_z <= elem["z"] <= point_z:
            good_coord.append(elem)
    print(good_coord)
    xs = [rp["x"] for rp in reachable_positions]
    zs = [rp["z"] for rp in reachable_positions]
    plt.scatter(xs, zs, color="red")
    # fig, ax = plt.subplots(1, 1)
    # ax.scatter(xs, zs)
    # ax.set_xlabel("$x$")
    # ax.set_ylabel("$z$")
    # ax.set_title("Reachable Positions in the Scene")
    # ax.set_aspect("equal")
    xs = [rp["x"] for rp in good_coord]
    zs = [rp["z"] for rp in good_coord]
    plt.scatter(xs, zs, color="blue")
    plt.show()
    return good_coord

def get_bounding_box(controller):
    obj_frame_list = list(controller.last_event.instance_detections2D.instance_masks.keys())
    obj_list = []

    for obj in controller.last_event.metadata["objects"]:
        if not obj['objectType'] == 'Wall' and not obj['objectType'] == 'Floor':
            obj_list.append(obj['name'])

    matching_items = [item for item in obj_frame_list if item in obj_list]
    frame = controller.last_event.frame.copy()

    for obj in matching_items:
        (x1, y1, x2, y2) = controller.last_event.instance_detections2D[obj]
        color = list(np.random.choice(range(256), size=3))
        print(obj, (x1, y1, x2, y2))
        frame[y1, x1:x2] = color
        frame[y2, x1:x2] = color
        frame[y1:y2, x1] = color
        frame[y1:y2, x2] = color

    Image.fromarray(frame).show()

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

    coord = show_reachable_position(controller, house_data)
    controller.step(action="Teleport", position=coord[0])
    house_data["metadata"]["agent"]["position"] = coord[0]
    cam_index = 0

    # for room in house_data["rooms"]:
    #     cam_index = _add_cameras(room, controller, f"dataset/{house_data['id']}/images", house_data, cam_index)

    _get_top_down_frame(house_data, controller, f"dataset/{house_data['id']}/images",
                        f"/{house_data['id']}_top_down_after.png")
    step = 0
    while step < 360:
        controller.step(action="RotateRight", degrees=90)
        # print(list(controller.last_event.instance_detections2D.instance_masks.keys()))
        get_bounding_box(controller)
        Image.fromarray(controller.last_event.frame).save(f"dataset/{house_data['id']}/images/camera_0_{step}.jpg")
        step += 90

    # TESTING NON CANCELLARE
    # _dict_to_json(f"dataset/{house_data['id']}/gen_{house_data['id']}.json", house_data)
    # camera = controller.step(
    #     action="AddThirdPartyCamera",
    #     position=dict(x=8.756, y=3, z=((6.567 - 2.189) / 2) + 2.189),
    #     rotation=dict(x=45, y=270, z=0),
    #     fieldOfView=60,
    #     raise_for_failure=True,
    # )
    # Image.fromarray(camera.third_party_camera_frames[0]).show()

# TESTING NON CANCELLARE

with open("dataset/4169/gen_4169.json") as json_file:
    data = json.load(json_file)

visualize(data)
