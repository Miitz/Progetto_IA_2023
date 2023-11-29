from typing import Protocol, Optional, Set, Any, Dict, List, Union, TYPE_CHECKING

import numpy as np
from ai2thor.controller import Controller
from matplotlib.patches import Polygon

if TYPE_CHECKING:
    from procthor_v2.databases import ProcTHORDatabase
    from procthor_v2.generation import RoomSpec, HouseStructure, PartialHouse
    from procthor_v2.generation.objects import ProceduralRoom

from procthor_v2.utils.types import Split, BoundaryGroups, Object


class SampleHouseStructureProtocol(Protocol):
    def __call__(
        self,
        interior_boundary: Optional[np.ndarray],
        room_ids: Set,
        room_spec: "RoomSpec",
        interior_boundary_scale: float,
    ) -> "HouseStructure":
        pass


class AddDoorsProtocol(Protocol):
    def __call__(
        self,
        partial_house: "PartialHouse",
        controller: Controller,
        pt_db: "ProcTHORDatabase",
        split: Split,
    ) -> Any:
        pass


class AddLightsProtocol(Protocol):
    def __call__(
        self,
        partial_house: "PartialHouse",
        controller: Controller,
        pt_db: "ProcTHORDatabase",
        split: Split,
        floor_polygons: Dict[str, Polygon],
        ceiling_height: float,
    ) -> Any:
        pass


class AddSkyboxProtocol(Protocol):
    def __call__(
        self,
        partial_house: "PartialHouse",
        controller: Controller,
        pt_db: "ProcTHORDatabase",
        split: Split,
    ) -> Any:
        pass


class AddExteriorWallsProtocol(Protocol):
    def __call__(
        self,
        partial_house: "PartialHouse",
        controller: Controller,
        pt_db: "ProcTHORDatabase",
        split: Split,
        boundary_groups: BoundaryGroups,
    ) -> Any:
        pass


class AddRoomsProtocol(Protocol):
    def __call__(
        self,
        partial_house: "PartialHouse",
        controller: Controller,
        pt_db: "ProcTHORDatabase",
        split: str,
        floor_polygons: Dict[str, Polygon],
        room_type_map: Dict[int, str],
        door_polygons: Dict[int, List[Polygon]],
    ) -> Any:
        pass


class AddFloorObjectsProtocol(Protocol):
    def __call__(
        self,
        partial_house: "PartialHouse",
        controller: Controller,
        pt_db: "ProcTHORDatabase",
        split: Split,
        max_floor_objects: int,
        room_object: Dict[str, list[str]]
    ) -> Any:
        pass


class AddWallObjectsProtocol(Protocol):
    def __call__(
        self,
        partial_house: "PartialHouse",
        controller: Controller,
        pt_db: "ProcTHORDatabase",
        split: Split,
        rooms: Dict[int, "ProceduralRoom"],
        boundary_groups: BoundaryGroups,
        room_type_map: Dict[int, str],
        ceiling_height: float,
    ) -> Any:
        pass


class AddSmallObjectsProtocol(Protocol):
    def __call__(
        self,
        partial_house: "PartialHouse",
        controller: Controller,
        pt_db: "ProcTHORDatabase",
        split: Split,
        rooms: Dict[int, "ProceduralRoom"],
        room_object: Dict[str, list[str]]
    ) -> Any:
        pass


class RandomizeObjectAttributesProtocol(Protocol):
    def __call__(
        self,
        objects: List[Object],
        pt_db: "ProcTHORDatabase",
    ) -> Any:
        pass


UnionGenerationProtocols = Union[
    SampleHouseStructureProtocol,
    AddDoorsProtocol,
    AddLightsProtocol,
    AddSkyboxProtocol,
    AddExteriorWallsProtocol,
    AddRoomsProtocol,
    AddFloorObjectsProtocol,
    AddWallObjectsProtocol,
    AddSmallObjectsProtocol,
]
