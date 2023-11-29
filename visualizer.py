import copy
import os.path

from ai2thor.controller import Controller
from PIL import Image


def _get_top_down_frame(data, controller: Controller, path: str):
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
    Image.fromarray(event.third_party_camera_frames[-1]).save(path+f"/{data['id']}_top_down.png")


def _add_cameras(metadata, controller: Controller, path: str, house_data):
    max_x, max_z = 0.0, 0.0
    for coord in metadata["floorPolygon"]:
        if max_x < coord['x']:
            max_x = coord['x']
        if max_z < coord['z']:
            max_z = coord['z']

    cam_index = 0
    for coord in metadata["floorPolygon"]:
        if coord['x'] == coord['z'] and coord['x'] == 0.0:
            camera = controller.step(
                action="AddThirdPartyCamera",
                position=dict(x=coord['x'], y=3, z=coord['z']),
                rotation=dict(x=30, y=45, z=0),
                fieldOfView=60,
                raise_for_failure=True,
            )
            Image.fromarray(camera.third_party_camera_frames[cam_index]).save(path+f"/{house_data['id']}_camera_{cam_index}.png")
            cam_index += 1
        if coord['x'] == coord['z'] and coord['x'] != 0.0:
            camera = controller.step(
                action="AddThirdPartyCamera",
                position=dict(x=coord['x'], y=3, z=coord['z']),
                rotation=dict(x=30, y=225, z=0),
                fieldOfView=60,
                raise_for_failure=True,
            )
            Image.fromarray(camera.third_party_camera_frames[cam_index]).save(path+f"/{house_data['id']}_camera_{cam_index}.png")
            cam_index += 1
        if coord['x'] != coord['z'] and coord['x'] == 0.0 and coord['z'] == max_z:
            camera = controller.step(
                action="AddThirdPartyCamera",
                position=dict(x=coord['x'], y=3, z=coord['z']),
                rotation=dict(x=30, y=135, z=0),
                fieldOfView=60,
                raise_for_failure=True,
            )
            Image.fromarray(camera.third_party_camera_frames[cam_index]).save(path+f"/{house_data['id']}_camera_{cam_index}.png")
            cam_index += 1

        if coord['x'] != coord['z'] and coord['x'] == max_x and coord['z'] == 0.0:
            camera = controller.step(
                action="AddThirdPartyCamera",
                position=dict(x=coord['x'], y=3, z=coord['z']),
                rotation=dict(x=30, y=315, z=0),
                fieldOfView=60,
                raise_for_failure=True,
            )
            Image.fromarray(camera.third_party_camera_frames[cam_index]).save(path+f"/{house_data['id']}_camera_{cam_index}.png")
            cam_index += 1


def visualize(house_data):
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

    for room in house_data["rooms"]:
        _add_cameras(room, controller, f"dataset/{house_data['id']}/images", house_data)

    _get_top_down_frame(house_data, controller, f"dataset/{house_data['id']}/images")
