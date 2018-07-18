# Jupyter-flashcards

Jupyter notebook utility to view flashcards in both Excel and markdown format.

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
Back side of the card is show. Also render images and HTML.

```
For more information, see https://github.com/patarapolw/jupyter-flashcards/tree/master/docs/README.md

## Screenshots

<img src="https://raw.githubusercontent.com/patarapolw/jupyter-flashcards/master/screenshots/1.png" />
<img src="https://raw.githubusercontent.com/patarapolw/jupyter-flashcards/master/screenshots/2.png" />
<img src="https://raw.githubusercontent.com/patarapolw/jupyter-flashcards/master/screenshots/3.png" />

## Plans

Probably exporting to `pyfladesk`/`Flask`, for non-python users, non-programmers to use.

## Related

- [TagDict](https://github.com/patarapolw/TagDict)
