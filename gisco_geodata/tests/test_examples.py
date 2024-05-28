"""This module will be used to test that the examples module."""

from pathlib import Path
import inspect
import importlib.util
from gisco_geodata import set_httpx_args


HERE = Path(__file__).parent


def test_examples():
    set_httpx_args(verify=False, timeout=60)
    module = HERE.parent.parent / 'examples'
    for py in module.rglob('*.py'):
        if py.stem.startswith('__'):
            continue
        module = importlib.util.spec_from_file_location(
            py.stem, py
        )
        examples = importlib.util.module_from_spec(module)
        module.loader.exec_module(examples)
        for name, func in inspect.getmembers(examples, inspect.isfunction):
            # Functions in the example folder should start with 'get'.
            if name.startswith('get') and func.__module__ == py.stem:
                print(func.__module__)
                func()  # this should not raise errors
