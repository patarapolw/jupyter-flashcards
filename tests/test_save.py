import pytest
from pathlib import Path

from jupyter_flashcards.app import Flashcards


@pytest.mark.parametrize('in_file', [
    "non-existent.xlsx",
    "non-existent.zip"
])
def test_save_non_existent(in_file, out_file,
                           request):
    flashcards = Flashcards(in_file)
    with pytest.raises(ValueError):
        flashcards.save(out_file(request.node.name))
    flashcards.close()


@pytest.mark.parametrize('in_file', [
    "test.xlsx"
])
def test_export(in_file,
                test_file, out_file, request):
    flashcards = Flashcards(test_file(in_file))
    flashcards.save(out_file(request.node.name, out_format='.zip'))
    flashcards.close()
