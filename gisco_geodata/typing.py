from __future__ import annotations

from os import PathLike
from typing import (
    Literal,
    TypedDict,
    TYPE_CHECKING,
    Any,
    Union
)

if TYPE_CHECKING:
    from .theme import (
        PDF,
        XML
    )

# TODO: find a way to have this type alias without 'Union'
# and have it backwards compatible with python >= 3.9
FilePath = Union[str, PathLike[str]]
JSON = dict[str, Any]

Projection = Literal['4326', '3035', '3857']
FileFormat = Literal['csv', 'geojson', 'pbf', 'shp', 'svg', 'topojson']
Scale = Literal['100K', '01M', '03M', '10M', '20M', '60M']
SpatialType = Literal['AT', 'BN', 'LB', 'RG']
CountryBoundary = Literal['INLAND', 'COASTL']
NUTSLevel = Literal['LEVL_0', 'LEVL_1', 'LEVL_2', 'LEVL_3']
UrbanAuditCategory = Literal['C', 'F']

Units = dict[str, list[str]]
Files = dict[str, list[str]]
Packages = dict[str, dict]


class GeoJSON(TypedDict):
    crs: dict
    type: str
    features: list[dict]


class TitleMultilingual(TypedDict):
    de: str
    en: str
    fr: str


class Metadata(TypedDict):
    pdf: PDF
    url: str
    xml: XML
