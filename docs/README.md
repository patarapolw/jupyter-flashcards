## Flashcards class

### `Flashcards(in_file)`

- `in_file` can be a string or a Path-like object. Supported file formats are a folder containing an Excel file or just simply a bare Excel file.
- `Flashcards()` can also work as a context manager, but there is nothing to clean on `close()` at the moment.

### `Flashcards.save(out_file)`

- If `out_file` is not given, it will be the same as `in_file`.
- It can be either an `Excel` or a folder.

### `Flashcards.find(keyword_regex: str = '', tags: list=None)`

- Return a generator containing CardTuple's.
- If nothing is supplied, it will return the whole collection.
- keyword_regex is a regex matching `front`, `back` and `keywords`.

### `Flashcards.view(keyword_regex: str='', tags: list=None, file_format='handsontable', width=800, height=300)`

- Same as `Flashcards.find`, but return a `pyexcel-handsontable` viewable on Jupyter Notebook.

### `Flashcards.view_id(item_id)`

- Front side and back side is shown on the Jupyter cell.
- Nothing is returned.

### `Flashcards.quiz(keyword_regex: str='', tags: list=None)`

- Randomize one flashcard to quiz on.
- Return a `CardQuiz` object, which is directly `_repr_html_` as the front of the card.

### `Flashcards.tag`

- A property, returning all the possible tags.
- Anyway, when searching the tags, it doesn't have to be exactly the same, but all tags must match regex.

## CardQuiz class

The only you would probably use is `CardQuiz.show()`.

- Show the back of the card.
