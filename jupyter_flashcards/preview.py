from markdown import markdown
import pyexcel
import json
from pathlib import Path
from IPython.display import IFrame

from .utils import get_url_images_in_text
from .dir import static_path


def save_preview_table(array, dest_file_name, image_dir,
                       markdown_cols=None, width=800, height=300):
    if markdown_cols is None:
        markdown_cols = list()

    for i, row in enumerate(array):
        if i == 0:
            continue

        for j, cell in enumerate(row):
            if j in markdown_cols:
                for url in get_url_images_in_text(array[i][j]):
                    image_path = str(image_dir['_path'].joinpath('{}-{}'.format(array[i][0], Path(url).name)))

                    array[i][j] = markdown(array[i][j]
                                           .replace(url, '<div class="hoverShowImage" id="{}">{}</a>'
                                                    .format(image_path, url)))

    img_ref = dict()
    for k, v in image_dir.items():
        img_ref[k] = str(v)

    pyexcel.save_as(
        array=array[1:],
        dest_file_name=dest_file_name,
        dest_sheet_name='Preview',
        readOnly=False,
        js_url=static_path('handsontable.full.min.js'),
        css_url=static_path('handsontable.full.min.css')
    )

    columns = list()
    columnWidths = list()
    for i, header_item in enumerate(array[0]):
        if i in markdown_cols:
            columns.append({"data": i, "renderer": "html"})
        else:
            columns.append({"data": i})

        columnWidths.append(100)

    with open(dest_file_name, 'r+') as f:
        contents = f.readlines()
        for i, row in enumerate(contents):
            if 'actualconfig["data"] = mydata;' in row:
                contents.insert(i + 1, '''
    actualconfig["readOnly"] = false;
    actualconfig["colHeaders"] = {};
    actualconfig["columns"] = {};
    actualconfig["columnWidth"] = {};
                    '''.format(json.dumps(array[0]),
                               json.dumps(columns),
                               json.dumps(columnWidths)))
                break

        for i, row in enumerate(contents):
            if '<head>' in row:
                contents.insert(i+1, '''
    <link rel="stylesheet" type="text/css" href="/notebooks/jupyter_flashcards/static/jquery-ui.min.css">
    <link rel="stylesheet" type="text/css" href="/notebooks/jupyter_flashcards/static/jquery-ui.structure.min.css">
    <link rel="stylesheet" type="text/css" href="/notebooks/jupyter_flashcards/static/jquery-ui.theme.min.css">
                ''')
            if '<script>' in row:
                contents.insert(i, '''
    <script>img_ref = {};</script>
    <script src="/notebooks/jupyter_flashcards/static/jquery-3.3.1.min.js"></script>
    <script src="/notebooks/jupyter_flashcards/static/jquery-ui.min.js"></script>
    <script src="/notebooks/jupyter_flashcards/static/previewtable.js"></script>
                '''.format(json.dumps(img_ref)))

                break

        f.seek(0)
        f.write(''.join(contents))

    return IFrame(dest_file_name, width=width, height=height)
