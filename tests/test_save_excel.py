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
        flashcards.save_excel(out_file(request.node.name, out_format='.xlsx'))
    flashcards.close()


@pytest.mark.parametrize('in_file', [
    "test.xlsx"
])
def test_save(in_file, out_file,
              test_file, request):
    flashcards = Flashcards(test_file(in_file))
    flashcards.save_excel(out_file(request.node.name, out_format='.xlsx'))
    flashcards.close()
