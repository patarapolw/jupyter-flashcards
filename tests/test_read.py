import pytest

from jupyter_flashcards.app import Flashcards


@pytest.mark.parametrize('in_file', [
    "non-existent.xlsx",
    "non-existent.zip"
])
def test_read(in_file):
    Flashcards(in_file).close()
