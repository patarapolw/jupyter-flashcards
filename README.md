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
