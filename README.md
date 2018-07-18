# Jupyter-flashcards

A Jupyter notebook utility to view flashcards in both Excel and markdown format. The image is also shown.

Not to mention that both the `*.xlsx` file and the image folder are directly editable.

The image folder auto-caches any images you add in the markdown (both online and local). The Excel file autosaves every time you edit it.

## Installation

- [Clone the project]().
- Create a virtual environment.
- [Install poetry](https://github.com/sdispater/poetry#installation)
- Run `poetry install`.
- Import this project in Jupyter notebook `from jupyter_flashcards import Flashcards`.

## Usage

```python
>>> from jupyter_flashcards import Flashcards
>>> fc = Flashcards('user/foo/')  # This is a folder name, although *.xlsx is also supported.
>>> fc.add(
    Front="http://www.pathologyoutlines.com/images/eye/PL04C.jpg",
    Back="retinoblastoma",
    Tags=["eye"]
)
A pyexcel-handsontable is shown. No HTML or markdown is rendered, though.
>>> card = fc.quiz('retino')  # A random card is choosed from the regex "retino"
>>> card
Show front side of the card on Jupyter Notebook. Images are also included (no need to be inside markdown tags, or img tags.) Markdown is rendered to HTML.
>>> card.show()
Back side of the card is show. Also render images, markdown and HTML.

```
In this case, the images are always cached at `foo/` folder for offline use.

For more information, see https://github.com/patarapolw/jupyter-flashcards/tree/master/docs/README.md

## Departure from the normal markdown

`/\n+\/` is converted to `\n\n`, meaning it doesn't matter if you press enter once; it will rendered to a new line.

## Excel file

It must be an Excel file with a worksheet named `flashcards` and has a first row of ['id', 'Front', 'Back', 'Keywords', 'Tags']. After the first row, every row must have an id specified. Id must be a number.

## Screenshots

<img src="https://raw.githubusercontent.com/patarapolw/jupyter-flashcards/master/screenshots/1.png" />
<img src="https://raw.githubusercontent.com/patarapolw/jupyter-flashcards/master/screenshots/2.png" />
<img src="https://raw.githubusercontent.com/patarapolw/jupyter-flashcards/master/screenshots/3.png" />

## Plans

Probably exporting to `pyfladesk`/`Flask`/`pyinstaller`, for non-python users, non-programmers to use.

## Related

- [TagDict](https://github.com/patarapolw/TagDict)
