from pathlib import Path

from gisco_geodata import (
    set_httpx_args,
    Countries,
    CoastalLines
)
from gisco_geodata.theme import Property

set_httpx_args(verify=False)


def test_metadata(tmpdir: Path):
    countries = Countries()
    dataset = countries.get_dataset(year='2006')
    pdf = tmpdir / 'pdf_file.pdf'
    xml = tmpdir / 'xml_file.xml'
    assert dataset.metadata is not None
    dataset.metadata['pdf'].download(
        out_file=pdf,
        open_file=False
    )
    dataset.metadata['xml'].download(
        out_file=xml,
        open_file=False
    )
    assert pdf.exists()
    assert xml.exists()


def test_documentation(tmpdir: Path):
    coastal_lines = CoastalLines()
    dataset = coastal_lines.get_dataset('2016')
    documentation = dataset.documentation
    assert documentation is not None
    assert isinstance(documentation.text(), str)
    file = tmpdir / 'documentation.txt'
    documentation.save(out_file=file, open_file=False)


def test_theme_all():
    theme = CoastalLines()
    # At 28/5/2024, the GISCO API is broken
    # and the key is titleMultilinual instead of
    # titleMultilingual. That's why it's being commented out
    # props = ['title', 'title_multilingual']
    props = ['title']
    for prop in props:
        property = getattr(theme, prop)
        assert property is not None


def test_dataset_all():
    props = list(Property._member_map_.keys())
    countries = Countries()
    dataset = countries.default_dataset
    for prop in props:
        property = getattr(dataset, prop.lower())
        assert property is not None
