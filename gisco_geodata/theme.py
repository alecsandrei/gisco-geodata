from __future__ import annotations

import asyncio
from dataclasses import dataclass
import datetime
from enum import Enum
from functools import partial
import os
from pathlib import Path
import sys
from typing import (
    Any,
    Sequence,
    Literal,
    Optional,
    overload,
    cast
)

from .utils import (
    geopandas_is_available,
    handle_completed_requests,
    gdf_from_geojson
)
from .parser import (
    get_datasets,
    get_file,
    get_param,
    get_themes,
)
from .typing import (
    FilePath,
    SpatialType,
    CountryBoundary,
    Scale,
    Projection,
    NUTSLevel,
    GeoJSON,
    Units,
    UrbanAuditCategory,
    Metadata,
    FileFormat,
    JSON,
    TitleMultilingual,
    Packages,
    Files
)

PLATFORM = sys.platform
SEMAPHORE_VALUE = 50
GEOPANDAS_AVAILABLE = geopandas_is_available()


if GEOPANDAS_AVAILABLE:
    import geopandas as gpd


_UNITS_REGION = '{unit}-region-{scale}-{projection}-{year}.geojson'
_UNITS_LABEL = '{unit}-label-{projection}-{year}.geojson'


@dataclass
class MetadataFile:
    file_name: str
    dataset: Dataset

    def download(
        self,
        out_file: FilePath,
        open_file: bool = True
    ):
        with open(out_file, mode='wb') as f:
            bytes_ = asyncio.run(
                get_param(
                    self.dataset.theme_parser.name,
                    self.file_name,
                    return_type='bytes'
                )
            )
            f.write(bytes_)
        if open_file and PLATFORM == 'win32':
            os.startfile(out_file)  # type: ignore


class PDF(MetadataFile):
    ...


class XML(MetadataFile):
    ...


@dataclass
class Documentation:
    dataset: Dataset
    file_name: str

    @property
    def content(self) -> bytes:
        return asyncio.run(
            get_param(
                self.dataset.theme_parser.name,
                self.file_name,
                return_type='bytes'
            )
        )

    def text(self, encoding: str = 'utf-8') -> str:
        return self.content.decode(encoding=encoding)

    def save(
        self,
        out_file: FilePath,
        open_file: bool = True
    ):
        with open(out_file, mode='wb') as f:
            f.write(self.content)
        if open_file and PLATFORM == 'win32':
            os.startfile(out_file)  # type: ignore


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
    def title_multilingual(self) -> Optional[TitleMultilingual]:
        return self.properties.get(
            Property.TITLE_MULTILINGUAL.value, None
        )

    @property
    def title(self) -> Optional[str]:
        return self.properties.get(
            Property.TITLE.value, None
        )

    @property
    def datasets(self) -> JSON:
        return get_datasets(self.name)

    @property
    def default_dataset(self) -> Dataset:
        return self.get_datasets()[-1]

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
        spatial_type: str,
        year: Optional[str] = None,
        file_format: Literal['geojson'] = 'geojson',
        out_dir: Literal[None] = None,
        scale: Optional[str] = None,
        projection: Optional[str] = None,
        country_boundary: Optional[str] = None,
        nuts_level: Optional[str] = None,
        **kwargs: str
    ) -> GeoJSON | gpd.GeoDataFrame:
        ...

    @overload
    def download(
        self,
        *,
        file_format: FileFormat,
        out_dir: FilePath,
        spatial_type: SpatialType,
        year: Optional[str] = None,
        scale: Optional[Scale] = None,
        projection: Optional[Projection] = None,
        country_boundary: Optional[CountryBoundary] = None,
        **kwargs: str
    ) -> None:
        ...

    @overload
    def download(
        self,
        *,
        file_format: str,
        out_dir: FilePath,
        spatial_type: str,
        year: Optional[str] = None,
        scale: Optional[str] = None,
        projection: Optional[str] = None,
        country_boundary: Optional[CountryBoundary] = None,
        **kwargs: str
    ) -> None:
        ...

    @overload
    def download(
        self,
        *,
        file_format: FileFormat,
        out_dir: FilePath,
        spatial_type: SpatialType,
        year: Optional[str] = None,
        scale: Optional[Scale] = None,
        projection: Optional[Projection] = None,
        nuts_level: Optional[NUTSLevel] = None,
        **kwargs: str
    ) -> None:
        ...

    @overload
    def download(
        self,
        *,
        file_format: str,
        out_dir: FilePath,
        spatial_type: str,
        year: Optional[str] = None,
        scale: Optional[str] = None,
        projection: Optional[str] = None,
        nuts_level: Optional[str] = None,
        **kwargs: str
    ) -> None:
        ...

    def download(
        self,
        *,
        spatial_type: str,
        file_format: Optional[str] = None,
        year: Optional[str] = None,
        out_dir: Optional[FilePath] = None,
        scale: Optional[str] = None,
        projection: Optional[str] = None,
        country_boundary: Optional[str] = None,
        nuts_level: Optional[str] = None,
        **kwargs: str
    ) -> Optional[GeoJSON | gpd.GeoDataFrame]:
        if year is None:
            year = self.default_dataset.year
        if file_format is None:
            file_format = 'geojson'
        return self.get_dataset(year)._download(
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


class LocalAdministrativeUnits(ThemeParser):
    name = Theme.LOCAL_ADMINISTRATIVE_UNITS.value

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

    async def get_units(self, year: Optional[str] = None) -> Units:
        if year is None:
            return await self.default_dataset.get_units()
        return await Dataset(self, year).get_units()

    async def _gather_units(
        self,
        countries: Optional[Sequence[str]] = None,
    ):
        def filter_logic(k: str):
            if countries is not None:
                return k in countries
            return True

        return filter(filter_logic, await self.get_units())

    async def _get_one(
        self,
        unit,
        spatial_type,
        scale,
        projection,
        year,
        semaphore
    ):
        if spatial_type == 'RG':
            param = _UNITS_REGION.format(
                unit=unit,
                scale=scale,
                projection=projection,
                year=year
            )
        elif spatial_type == 'LB':
            param = _UNITS_LABEL.format(
                unit=unit,
                projection=projection,
                year=year
            )
        else:
            raise ValueError(
                f'Wrong parameter {spatial_type}.'
                'Allowed are "RG" and "LB".'
            )
        try:
            async with semaphore:
                geojson = cast(
                    GeoJSON,
                    await get_param(
                        self.name, 'distribution', param
                    )
                )
        except Exception:
            raise
        return geojson

    async def _get_many(
        self,
        countries,
        spatial_type,
        scale,
        projection,
        year
    ):
        semaphore = asyncio.Semaphore(SEMAPHORE_VALUE)
        units = await self._gather_units(countries)
        to_do = [
            self._get_one(
                unit, spatial_type, scale, projection, year, semaphore
            )
            for unit in units
        ]
        if not units:
            print(
                f"No unit was found for parameters:\n"
                f"countries {countries},\n"
                f"spatial type {spatial_type},\n"
                f"scale {scale},\n"
                f"projection {projection},\n"
                f"year {year}"
            )
            raise ValueError
        to_do_iter = asyncio.as_completed(to_do)
        result = await handle_completed_requests(coros=to_do_iter)
        return result

    @overload
    def get(
        self,
        *,
        countries: Optional[str | Sequence[str]] = None,
        spatial_type: Literal['LB'],
        projection: Projection = '4326',
        year: Optional[str] = None,
    ) -> list[GeoJSON] | gpd.GeoDataFrame:
        ...

    @overload
    def get(
        self,
        *,
        countries: Optional[str | Sequence[str]] = None,
        spatial_type: Literal['RG'],
        scale: Scale = '20M',
        projection: Projection = '4326',
        year: Optional[str] = None,
    ) -> list[GeoJSON] | gpd.GeoDataFrame:
        ...

    def get(
        self,
        *,
        countries: Optional[str | Sequence[str]] = None,
        spatial_type: str = 'RG',
        projection: str = '4326',
        scale: Optional[str] = '20M',
        year: Optional[str] = None,
    ) -> list[GeoJSON] | gpd.GeoDataFrame:
        if isinstance(countries, str):
            countries = [countries]
        if year is None:
            year = self.default_dataset.year
        coro = self._get_many(
            countries,
            spatial_type,
            scale,
            projection,
            year
        )
        geojson = asyncio.run(coro)
        if GEOPANDAS_AVAILABLE:
            return gdf_from_geojson(geojson)
        return geojson


class NUTS(ThemeParser):
    name = Theme.NUTS.value

    def __init__(self, name: Optional[str] = None):
        if name:
            self.name = name
        super().__init__(self.name)

    async def get_units(self, year: Optional[str] = None) -> Units:
        if year is None:
            return await self.default_dataset.get_units()
        return await Dataset(self, year).get_units()

    async def _gather_units(
        self,
        nuts_level: NUTSLevel,
        countries: Optional[Sequence[str]] = None,
    ):
        def filter_logic(k: str):
            conditions = []
            if countries is not None:
                conditions.append(k in countries)
            conditions.append(
                len(k)-2 == int(nuts_level[-1])
            )
            return all(conditions)
        return filter(filter_logic, await self.get_units())

    async def _get_one(
        self,
        unit,
        spatial_type,
        scale,
        projection,
        year,
        semaphore
    ):
        if spatial_type == 'RG':
            param = _UNITS_REGION.format(
                unit=unit,
                scale=scale,
                projection=projection,
                year=year
            )
        elif spatial_type == 'LB':
            param = _UNITS_LABEL.format(
                unit=unit,
                projection=projection,
                year=year
            )
        else:
            raise ValueError(
                f'Wrong parameter {spatial_type}.'
                'Allowed are "RG" and "LB".'
            )
        try:
            async with semaphore:
                geojson = cast(
                    GeoJSON,
                    await get_param(
                        self.name, 'distribution', param
                    )
                )
        except Exception:
            raise
        return geojson

    async def _get_many(
        self,
        nuts_level,
        countries,
        spatial_type,
        scale,
        projection,
        year
    ):
        semaphore = asyncio.Semaphore(SEMAPHORE_VALUE)
        units = await self._gather_units(nuts_level, countries)
        to_do = [
            self._get_one(
                unit, spatial_type, scale, projection, year, semaphore
            )
            for unit in units
        ]
        if not units:
            print(
                f"No unit was found for parameters:\n"
                f"countries {countries},\n"
                f"NUTS level {nuts_level}, \n"
                f"spatial type {spatial_type},\n"
                f"scale {scale},\n"
                f"projection {projection},\n"
                f"year {year}"
            )
            raise ValueError
        to_do_iter = asyncio.as_completed(to_do)
        results = await handle_completed_requests(coros=to_do_iter)
        return results

    @overload
    def get(
        self,
        *,
        countries: Optional[str | Sequence[str]] = None,
        nuts_level: NUTSLevel = 'LEVL_0',
        spatial_type: Literal['LB'] = 'LB',
        projection: Projection = '4326',
        year: Optional[str] = None,
    ) -> list[GeoJSON] | gpd.GeoDataFrame:
        ...

    @overload
    def get(
        self,
        *,
        countries: Optional[str | Sequence[str]] = None,
        nuts_level: NUTSLevel = 'LEVL_0',
        spatial_type: Literal['RG'] = 'RG',
        scale: Scale = '20M',
        projection: Projection = '4326',
        year: Optional[str] = None,
    ) -> list[GeoJSON] | gpd.GeoDataFrame:
        ...

    def get(
        self,
        *,
        countries: Optional[str | Sequence[str]] = None,
        nuts_level: NUTSLevel = 'LEVL_0',
        spatial_type: str = 'RG',
        projection: str = '4326',
        scale: Optional[str] = '20M',
        year: Optional[str] = None
    ) -> list[GeoJSON] | gpd.GeoDataFrame:
        if isinstance(countries, str):
            countries = [countries]
        if year is None:
            year = self.default_dataset.year
        coro = self._get_many(
            nuts_level,
            countries,
            spatial_type,
            scale,
            projection,
            year
        )
        geojson = asyncio.run(coro)
        if GEOPANDAS_AVAILABLE:
            return gdf_from_geojson(geojson)
        return geojson


class UrbanAudit(ThemeParser):
    name = Theme.URBAN_AUDIT.value

    def __init__(self, name: Optional[str] = None):
        if name:
            self.name = name
        super().__init__(self.name)

    async def get_units(self, year: Optional[str] = None) -> Units:
        if year is None:
            return await self.default_dataset.get_units()
        return await Dataset(self, year).get_units()

    async def _gather_units(
        self,
        category: Optional[UrbanAuditCategory] = None,
        countries: Optional[Sequence[str]] = None,
    ):
        def filter_logic(k: str):
            # Unit names have the schema "RO001F".
            # We select the units that start with any provided
            # country and endwith the provided category
            conditions = []
            if countries is not None:
                conditions.append(
                    any(k.startswith(country) for country in countries)
                )
            if category is not None:
                conditions.append(k.endswith(category))
            return all(conditions)
        units = await self.get_units()
        if category is None and countries is None:
            return units
        return filter(filter_logic, units)

    async def _get_one(
        self,
        unit,
        spatial_type,
        scale,
        projection,
        year,
        semaphore
    ):
        if spatial_type == 'RG':
            param = _UNITS_REGION.format(
                unit=unit,
                scale=scale,
                projection=projection,
                year=year
            )
        elif spatial_type == 'LB':
            param = _UNITS_LABEL.format(
                unit=unit,
                projection=projection,
                year=year
            )
        else:
            raise ValueError(
                f'Wrong parameter {spatial_type}.'
                'Allowed are "RG" and "LB".'
            )
        try:
            async with semaphore:
                geojson = cast(
                    GeoJSON,
                    await get_param(
                        self.name, 'distribution', param
                    )
                )
        except Exception:
            raise
        else:
            return geojson

    async def _get_many(
        self,
        countries,
        category,
        spatial_type,
        scale,
        projection,
        year
    ):
        semaphore = asyncio.Semaphore(SEMAPHORE_VALUE)
        units = await self._gather_units(category, countries)
        if not units:
            print(
                f"No units were found for parameters:\n"
                f"countries {countries},\n"
                f"category {category},\n"
                f"spatial type {spatial_type},\n"
                f"scale {scale},\n"
                f"projection {projection},\n"
                f"year {year}"
            )
            raise ValueError
        to_do = [
            self._get_one(
                unit, spatial_type, scale, projection, year, semaphore
            )
            for unit in units
        ]
        to_do_iter = asyncio.as_completed(to_do)
        results = await handle_completed_requests(coros=to_do_iter)
        return results

    @overload
    def get(
        self,
        *,
        countries: Optional[str | Sequence[str]] = None,
        category: Optional[UrbanAuditCategory] = None,
        spatial_type: Literal['LB'] = 'LB',
        projection: Projection = '4326',
        year: Optional[str] = None,
    ) -> list[GeoJSON] | gpd.GeoDataFrame:
        ...

    @overload
    def get(
        self,
        *,
        spatial_type: Literal['RG'] = 'RG',
        countries: Optional[str | Sequence[str]] = None,
        category: Optional[UrbanAuditCategory] = None,
        projection: Projection = '4326',
        scale: Scale = '100K',
        year: Optional[str] = None,
    ) -> list[GeoJSON] | gpd.GeoDataFrame:
        ...

    def get(
        self,
        *,
        spatial_type: str = 'RG',
        countries: Optional[str | Sequence[str]] = None,
        category: Optional[UrbanAuditCategory] = None,
        projection: str = '4326',
        scale: str = '100K',
        year: Optional[str] = None
    ) -> list[GeoJSON] | gpd.GeoDataFrame:
        if isinstance(countries, str):
            countries = [countries]
        if year is None:
            year = self.default_dataset.year
        coro = self._get_many(
            countries,
            category,
            spatial_type,
            scale,
            projection,
            year
        )
        geojson = asyncio.run(coro)
        if GEOPANDAS_AVAILABLE:
            return gdf_from_geojson(geojson)
        return geojson


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
    def date(self) -> datetime.datetime:
        # Datetime from gisco services has schema day/month/year
        # e.g. 01/12/2003
        return datetime.datetime(
            *map(
                int,
                self.properties[Property.DATE.value].split('/')[::-1]
            )  # type: ignore
        )

    @property
    def documentation(self) -> Optional[Documentation]:
        return self.get_documentation()

    @property
    def title(self) -> Optional[str]:
        return self.properties.get(
            Property.TITLE.value, None
        )

    @property
    def title_multilingual(self) -> Optional[TitleMultilingual]:
        return self.properties[Property.TITLE_MULTILINGUAL.value]

    @property
    def hashtag(self) -> Optional[str]:
        return self.properties[Property.HASHTAG.value]

    @property
    def metadata(self) -> Optional[Metadata]:
        return self.get_metadata()

    @property
    def units(self) -> Optional[Units]:
        return asyncio.run(self.get_units())

    @property
    def files(self) -> Files:
        return asyncio.run(self.get_files())

    @property
    def packages(self) -> Optional[Packages]:
        return self.get_packages()

    def get_documentation(self) -> Optional[Documentation]:
        documentation = self.properties.get(
            Property.DOCUMENTATION.value, None
        )
        if documentation is None:
            return None
        return Documentation(
            self,
            documentation
        )

    def get_packages(self) -> Optional[Packages]:
        # TODO: Maybe improve this somehow later on?
        packages = self.properties.get(
            Property.PACKAGES.value, None
        )
        if packages is None:
            return None
        return asyncio.run(
            get_param(self.theme_parser.name, packages)
        )

    def get_metadata(self) -> Optional[Metadata]:
        # We do an isinstance check because it was possible that
        # the value was set before, metadata could be stored
        # by async lru cache.
        metadata_props = self.properties.get(
            Property.METADATA.value, None
        )
        if metadata_props is None:
            return None
        if not isinstance(metadata_props['pdf'], MetadataFile):
            metadata_props['pdf'] = MetadataFile(
                metadata_props['pdf'],
                dataset=self
            )
        if not isinstance(metadata_props['xml'], MetadataFile):
            metadata_props['xml'] = MetadataFile(
                metadata_props['xml'],
                dataset=self
            )
        return metadata_props

    async def get_files(self) -> Files:
        return await get_param(
            self.theme_parser.name, self.get_property(Property.FILES.value)
        )

    async def get_units(self) -> Units:
        return await get_param(
            self.theme_parser.name, self.get_property(Property.UNITS.value)
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
        out_dir: Optional[FilePath]
    ) -> Optional[GeoJSON | gpd.GeoDataFrame]:
        if out_dir is None and file_format != 'geojson':
            raise ValueError(
                'out_dir can only be none ',
                'if the file format is geojson.'
            )
        if (
            out_dir is None
            and file_format == 'geojson'
            and not GEOPANDAS_AVAILABLE
        ):
            raise ValueError(
                'Geopandas needs to be installed if out_dir is not provided ',
                'and the file_format is geojson.'
            )
        # args[1:] to not consider the first part of the file name.
        # the reason this is done it's because the naming is inconsistent
        # e.g., for the 'Communes' theme, the first argument should be 'COMM'
        # which can't be parsed from anywhere.
        file_stem = '_'.join(arg for arg in args[1:] if arg is not None)
        file_stem_upper = file_stem.upper()
        file_name = self.get_file_name_from_stem(file_format, file_stem_upper)
        if file_name is None:
            to_choose_from = '\n'.join(
                self.files[file_format.lower()]
            )
            raise ValueError(
                f'No file found for {file_stem_upper}\n' +
                f"Available to choose from:\n{to_choose_from}"
            )

        content = asyncio.run(
            get_file(
                self.theme_parser.name, file_format, file_name
            )
        )

        if out_dir is not None:
            with open(Path(out_dir) / file_name, 'wb') as f:
                f.write(content)
            return None
        else:
            coro = cast(
                GeoJSON,
                asyncio.run(
                    get_param(self.theme_parser.name, file_format, file_name)
                )
            )
            if GEOPANDAS_AVAILABLE and file_format == 'geojson':
                return gdf_from_geojson(coro)
            else:
                return coro
