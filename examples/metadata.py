"""How to read the metadata of a certain dataset."""

import tempfile
from pathlib import Path
from xml.etree.ElementTree import Element

from gisco_geodata import UrbanAudit, set_httpx_args

if __name__ == '__main__':
    set_httpx_args(verify=False)

    ua = UrbanAudit()
    dataset = ua.get_datasets()[-1]
    metadata = dataset.metadata
    assert metadata is not None
    pdf = metadata['pdf']
    xml = metadata['xml']

    # Downloads the metadata.
    with tempfile.TemporaryDirectory() as tempdir:
        pdf_out = Path(tempdir) / 'urban_audit_metadata.pdf'
        pdf.download(
            pdf_out,
            open_file=False,  # if you are on Windows, this will open the file
        )

        # Minimal XML parsing examples (two).
        # They may only be applicable to this particular theme/dataset.
        # Read up:
        # https://docs.python.org/3/library/xml.etree.elementtree.html#module-xml.etree.ElementTree
        tree = xml.tree()

        # Example one
        def parse_all(tree: Element):
            """This will print all text found in the XML."""
            for child in tree:
                text = child.text
                if text is not None and (text := text.strip()):
                    print(text)
                if len(child):
                    parse_all(child)

        parse_all(tree)

        # Example two
        namespace = tree.tag[: tree.tag.find('}') + 1]
        statement = (
            tree.find(f'{namespace}dataQualityInfo')
            .find(f'{namespace}DQ_DataQuality')
            .find(f'{namespace}lineage')
            .find(f'{namespace}LI_Lineage')
            .find(f'{namespace}statement')
        )
        for child in statement:
            print(child.text)

    # Prints out the documentation.
    documentation = dataset.documentation
    assert documentation is not None
    print(documentation.text())
