from __future__ import annotations

from typing import (
    Any,
    TypedDict,
    Sequence,
    Union,
    Literal,
    Optional,
    overload,
)
from pathlib import Path
from functools import partial
from enum import Enum
from dataclasses import dataclass

from .parser import (
    get_datasets,
    get_file,
    get_param,
    get_themes
)
from .utils import geopandas_is_available

GEOPANDAS_AVAILABLE = geopandas_is_available()

if GEOPANDAS_AVAILABLE:
    import geopandas as gpd


PathLike = Union[Path, str]
JSON = dict[str, Any]
Projection = Literal['4326', '3035', '3857']
FileFormat = Literal['csv', 'geojson', 'pbf', 'shp', 'svg', 'topojson']
Scale = Literal['100K', '01M', '03M', '10M', '20M', '60M']
SpatialType = Literal['AT', 'BN', 'LB', 'RG']
Geometry = Literal['point', 'geometry']
CountryBoundary = Literal['INLAND', 'COASTL']
NUTSLevel = Literal['LEVL_0', 'LEVL_1', 'LEVL_2', 'LEVL_3']
Units = dict[str, list[str]]
Files = dict[str, list[str]]


class GeoJSON(TypedDict):
    crs: dict
    type: str
    features: list[dict]


class TitleMultilingual(TypedDict):
    de: str
    en: str
    fr: str


class Metadata(TypedDict):
    pdf: str
    url: str
    xml: str


class Property(Enum):
    DATE = 'date'
    DOCUMENTATION = 'documentation'
    FILES = 'files'
    HASHTAG = 'hashtag'
    METADATA = 'metadata'
    PACKAGES = 'packages'
    TITLE = 'title'
    TITLE_MULTILINGUAL = 'titleMultilingual'
    UNITS = 'units'


class Language(Enum):
    GERMAN = 'de'
    ENGLISH = 'en'
    FRENCH = 'fr'


class Theme(Enum):
    COASTAL_LINES = 'coas'
    COMMUNES = 'communes'
    COUNTRIES = 'countries'
    LOCAL_ADMINISTRATIVE_UNITS = 'lau'
    NUTS = 'nuts'
    URBAN_AUDIT = 'urau'


@dataclass
class ThemeParser:
    name: str

    @property
    def properties(self) -> JSON:
        return get_themes()[self.name]

    @property
    def datasets(self) -> JSON:
        return get_datasets(self.name)

    def get_datasets(self) -> list[Dataset]:
        return (
            [Dataset(self, year.split('-')[-1])
             for year in self.datasets.keys()]
        )

    def get_property(self, property: str) -> Any:
        return self.properties[property]

    def get_dataset(self, year: str) -> Dataset:
        return Dataset(self, year)

    @overload
    def download(
        self,
        *,
        file_format: FileFormat,
        out_dir: PathLike,
        year: str,
        spatial_type: SpatialType,
        scale: Optional[Scale] = None,
        projection: Optional[Projection] = None,
        country_boundary: Optional[CountryBoundary] = None,
        **kwargs: str
    ):
        ...

    @overload
    def download(
        self,
        *,
        file_format: str,
        out_dir: PathLike,
        year: str,
        spatial_type: str,
        scale: Optional[str] = None,
        projection: Optional[str] = None,
        country_boundary: Optional[CountryBoundary] = None,
        **kwargs: str
    ):
        ...

    @overload
    def download(
        self,
        *,
        file_format: FileFormat,
        out_dir: PathLike,
        year: str,
        spatial_type: SpatialType,
        scale: Optional[Scale] = None,
        projection: Optional[Projection] = None,
        nuts_level: Optional[NUTSLevel] = None,
        **kwargs: str
    ):
        ...

    @overload
    def download(
        self,
        *,
        file_format: str,
        out_dir: PathLike,
        year: str,
        spatial_type: str,
        scale: Optional[str] = None,
        projection: Optional[str] = None,
        nuts_level: Optional[str] = None,
        **kwargs: str
    ):
        ...

    def download(
        self,
        *,
        file_format: str,
        out_dir: PathLike,
        year: str,
        spatial_type: str,
        scale: Optional[str] = None,
        projection: Optional[str] = None,
        country_boundary: Optional[str] = None,
        nuts_level: Optional[str] = None,
        **kwargs: str
    ):

        self.get_dataset(year)._download(
            self.name,
            spatial_type,
            scale,
            year,
            projection,
            country_boundary,  # type: ignore
            nuts_level,
            **kwargs,
            file_format=file_format,
            out_dir=out_dir
        )


class CoastalLines(ThemeParser):
    name = Theme.COASTAL_LINES.value

    def __init__(self, name: Optional[str] = None):
        if name:
            self.name = name
        super().__init__(self.name)


class Communes(ThemeParser):
    name = Theme.COMMUNES.value

    def __init__(self, name: Optional[str] = None):
        if name:
            self.name = name
        super().__init__(self.name)


class Countries(ThemeParser):
    name = Theme.COUNTRIES.value

    def __init__(self, name: Optional[str] = None):
        if name:
            self.name = name
        super().__init__(self.name)

    @property
    def default_dataset(self) -> Dataset:
        return self.get_datasets()[-1]

    def get_units(self, year: Optional[str] = None) -> Units:
        if year is None:
            return self.default_dataset.units
        return Dataset(self, year).units

    @overload
    def get(
        self,
        *,
        countries: Union[str, Sequence[str]],
        spatial_type: Literal['LB'],
        projection: Projection = '4326',
        year: Optional[str] = None,
    ) -> Union[list[GeoJSON], gpd.GeoDataFrame]:
        ...

    @overload
    def get(
        self,
        *,
        countries: Union[str, Sequence[str]],
        spatial_type: Literal['RG'],
        scale: Scale = '20M',
        projection: Projection = '4326',
        year: Optional[str] = None,
    ) -> Union[list[GeoJSON], gpd.GeoDataFrame]:
        ...

    def get(
        self,
        *,
        countries: Union[str, Sequence[str]],
        spatial_type: str = 'RG',
        projection: str = '4326',
        scale: Optional[str] = '20M',
        year: Optional[str] = None,
    ) -> Union[list[GeoJSON], gpd.GeoDataFrame]:
        if year is None:
            year = self.default_dataset.year
        region = '{country}-region-{scale}-{projection}-{year}.geojson'
        label = '{country}-label-{projection}-{year}.geojson'
        geojson = []
        for country in countries:
            if spatial_type == 'RG':
                param = region.format(
                    country=country,
                    scale=scale,
                    projection=projection,
                    year=year
                )
                geojson.append(get_param(self.name, 'distribution', param))
            elif spatial_type == 'LB':
                param = label.format(
                    country=country,
                    projection=projection,
                    year=year
                )
                geojson.append(get_param(self.name, 'distribution', param))
            else:
                raise ValueError(
                    f'Wrong parameter {spatial_type}.'
                    'Allowed are "RG" and "LB".'
                )
        if GEOPANDAS_AVAILABLE:
            return gpd.GeoDataFrame(data=geojson)
        return geojson


class LocalAdministrativeUnits(ThemeParser):
    name = Theme.LOCAL_ADMINISTRATIVE_UNITS.value

    def __init__(self, name: Optional[str] = None):
        if name:
            self.name = name
        super().__init__(self.name)


class NUTS(ThemeParser):
    name = Theme.NUTS.value

    def __init__(self, name: Optional[str] = None):
        if name:
            self.name = name
        super().__init__(self.name)


class UrbanAudit(ThemeParser):
    name = Theme.URBAN_AUDIT.value

    def __init__(self, name: Optional[str] = None):
        if name:
            self.name = name
        super().__init__(self.name)


@dataclass
class Dataset:
    theme_parser: ThemeParser
    year: str

    def __post_init__(self):
        self.download = partial(self.theme_parser.download, year=self.year)

    @property
    def properties(self) -> JSON:
        return self.theme_parser.datasets[
            [k for k in self.theme_parser.datasets.keys() if self.year in k][0]
        ]

    @property
    def units(self) -> Units:
        return get_param(
            self.theme_parser.name, self.get_property(Property.UNITS.value)
        )

    @property
    def files(self) -> Files:
        return get_param(
            self.theme_parser.name, self.get_property(Property.FILES.value)
        )

    def get_property(self, property: str) -> Any:
        return self.properties[property]

    def get_file_name_from_stem(
        self,
        file_format: str,
        file_stem: str
    ) -> Optional[str]:
        json_ = self.files[file_format]
        for value in json_:
            # We check against 'SPATIALTYPE_YEAR_PROJECTION' etc.
            # instead of 'THEME_SPATIALTYPE_YEAR_PROJECTION'.
            # Naming of the 'THEME' inside the file names is inconsistent.
            # For example, for 'Communes' the file name starts with 'COMM'.
            to_check_against = '_'.join(value.split('_')[1:])
            if to_check_against.startswith(file_stem):
                return value
        return None

    def _download(
        self,
        *args: Optional[str],
        file_format: str,
        out_dir: PathLike
    ):
        # args[1:] to not consider the first part of the file name.
        # the reason this is done it's because the naming is inconsistent
        # e.g., for the 'Communes' theme, the first argument should be 'COMM'
        # which can't be parsed from anywhere.
        file_stem = '_'.join(arg for arg in args[1:] if arg is not None)
        file_stem_upper = file_stem.upper()
        file_name = self.get_file_name_from_stem(file_format, file_stem_upper)
        assert file_name is not None, f'File not found: {file_stem}'
        content = get_file(
            self.theme_parser.name, file_format, file_name
        )
        with open(Path(out_dir) / file_name, 'wb') as f:
            f.write(content)
