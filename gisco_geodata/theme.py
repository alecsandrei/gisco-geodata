from __future__ import annotations

from typing import (
    Any,
    TypedDict,
    Union,
    Literal,
    Optional,
    overload,
)
from pathlib import Path
from functools import partial
from enum import Enum

from .parser import (
    get_properties,
    get_file,
    get_param,
    get_themes
)


PathLike = Union[Path, str]
JSON = dict[str, Any]
Projection = Literal['4326', '3035', '3857']
FileFormat = Literal['csv', 'geojson', 'pbf', 'shp', 'svg', 'topojson']
Scale = Literal['100K', '01M', '03M', '10M', '20M', '60M']
SpatialType = Literal['AT', 'BN', 'LB', 'RG']
CountryBoundary = Literal['INLAND', 'COASTL']
NUTSLevel = Literal['LEVL_0', 'LEVL_1', 'LEVL_2', 'LEVL_3']


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
    LAU = 'lau'
    NUTS = 'nuts'
    URBAN_AUDIT = 'urau'

    @property
    def properties(self) -> JSON:
        return get_themes()[self.value]

    @property
    def datasets(self) -> JSON:
        return get_properties(self.value)

    def get_datasets(self) -> list[Dataset]:
        return (
            [Dataset(self, year.split('-')[-1])
             for year in self.properties.keys()]
        )

    @property
    def title(self) -> str:
        return self.properties[Property.TITLE.value]

    @property
    def title_multilingual(self) -> str:
        return self.properties[Property.TITLE_MULTILINGUAL.value]

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
            self.value,
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


class Dataset:

    def __init__(self, theme: Theme, year: str):
        self.theme = theme
        self.year = year
        self.download = partial(self.theme.download, year=self.year)

    @property
    def properties(self) -> JSON:
        return self.theme.datasets[
            [k for k in self.theme.datasets.keys() if self.year in k][0]
        ]

    @property
    def date(self) -> str:
        return self.properties[Property.DATE.value]

    @property
    def documentation(self) -> str:
        return self.properties[Property.DOCUMENTATION.value]

    @property
    def files(self) -> str:
        return self.properties[Property.FILES.value]

    @property
    def hashtag(self) -> str:
        return self.properties[Property.HASHTAG.value]

    @property
    def metadata(self) -> Metadata:
        return self.properties[Property.METADATA.value]

    @property
    def packages(self) -> str:
        return self.properties[Property.PACKAGES.value]

    @property
    def title(self) -> str:
        return self.properties[Property.TITLE.value]

    @property
    def title_multilingual(self) -> TitleMultilingual:
        return self.properties[Property.TITLE_MULTILINGUAL.value]

    @property
    def units(self) -> str:
        return self.properties[Property.UNITS.value]

    def get_property(self, property: str) -> Any:
        return self.properties[property]

    def get_file_name_from_stem(
        self,
        file_format: str,
        file_stem: str
    ) -> Optional[str]:
        json_ = get_param(self.theme.value, self.files)[file_format]
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
        content = get_file(self.theme.value, file_format, file_name)
        with open(Path(out_dir) / file_name, 'wb') as f:
            f.write(content)
