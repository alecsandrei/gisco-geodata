import pkg_resources


def is_package_installed(name: str) -> bool:
    try:
        pkg_resources.get_distribution(name)
        return True
    except pkg_resources.DistributionNotFound:
        return False


def geopandas_is_available() -> bool:
    return is_package_installed('geopandas')
