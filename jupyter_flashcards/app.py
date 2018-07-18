from pathlib import Path
from collections import OrderedDict
from time import time
from urllib.parse import urlparse
import re
import random
from threading import Timer
from IPython.display import IFrame

import pyexcel
import pyexcel_export

from .tags import to_raw_tags, tag_reader
from .utils import get_url_images_in_text
from .cache import cache_image_from_file, cache_image_from_url
from .card import CardQuiz, CardTuple
from .exceptions import (FileExtensionException, DatabaseHeaderException, NoDataError,
                         BadArgumentsException)
from .dir import module_path


class Flashcards:
    SHEET_NAME = 'flashcards'

    def __init__(self, in_file):
        """

        :param str|Path in_file: can be a folder, *.xlsx or *.zip
        """
        self.modified = time()

        if not isinstance(in_file, Path):
            in_file = Path(in_file)

        self.working_dir = in_file.parent.joinpath(in_file.stem)

        self.image_dir = dict(
            _path=self.working_dir.joinpath(in_file.stem)
        )
        if in_file.exists():
            if in_file.suffix != '':
                if in_file.suffix == '.xlsx':
                    self.excel = in_file

                    for file in in_file.parent.joinpath(in_file.stem).iterdir():
                        self.image_dir[file.name] = file

                else:
                    raise FileExtensionException('Invalid file extension.')

                raw_data, self.meta = pyexcel_export.get_data(self.excel)

                self.data = self._load_raw_data(raw_data)
            else:
                self.excel = in_file.joinpath(in_file.stem + '.xlsx')
                self.working_dir = in_file.joinpath(in_file.stem)

                if not self.working_dir.exists():
                    self.working_dir.mkdir()

                raw_data, self.meta = pyexcel_export.get_data(self.excel)

                self.data = self._load_raw_data(raw_data)

                if in_file.joinpath(in_file.stem).exists():
                    for file in in_file.joinpath(in_file.stem).iterdir():
                        self.image_dir[file.name] = file

        else:
            if in_file.suffix == '.xlsx':
                self.excel = in_file
            else:
                raise FileExtensionException('Invalid file extension.')

            self.data = OrderedDict()
            self.meta = pyexcel_export.get_meta()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        pass

    def save(self, out_file=None):
        if out_file is None:
            out_file = self.working_dir

        if not isinstance(out_file, Path):
            out_file = Path(out_file)

        if out_file.is_dir():
            out_file = out_file.parent.joinpath(out_file.stem + '.xlsx')

        if out_file.suffix != '.xlsx':
            raise FileExtensionException('Unsupported file format.')

        if len(self.data) == 0:
            raise NoDataError("There is no data to save.")

        out_matrix = []
        header = [header_item.title() if header_item != 'id' else header_item
                  for header_item in list(self.data.values())[0]._fields]
        out_matrix.append(header)

        for card_id, card_tuple in self.data.items():
            out_matrix.append(list(card_tuple))

        out_data = OrderedDict()
        out_data[self.SHEET_NAME] = out_matrix

        pyexcel_export.save_data(out_file=out_file, data=out_data, meta=self.meta)

    def add(self, **kwargs):
        if 'front' not in kwargs.keys():
            raise BadArgumentsException("'front' not in kwargs.keys()")

        item_id = int(time() * 1000)
        self.data[str(item_id)] = CardTuple(id=item_id)

        return item_id, self.append(item_id, **kwargs)

    def append(self, item_id, **kwargs):
        """

        :param int|str item_id:
        :param kwargs:
        :return:
        """
        item_id = str(item_id)

        if item_id not in self.data.keys():
            raise KeyError("Cannot append to {}.".format(item_id))

        if self.data[item_id].keywords:
            orig_keywords = self.data[item_id].keywords
        else:
            orig_keywords = ''

        if self.data[item_id].tags:
            orig_tags = self.data[item_id].tags
        else:
            orig_tags = ''

        keywords = kwargs.get('keywords', [])
        keywords.extend(tag_reader(orig_keywords))
        kwargs['keywords'] = to_raw_tags(keywords)

        tags = kwargs.get('tags', [])
        tags.extend(tag_reader(orig_tags))
        kwargs['tags'] = to_raw_tags(tags)

        orig_front = self.data[item_id].front
        orig_back = self.data[item_id].back

        if orig_front and orig_front[-1] != '\n':
            kwargs['front'] = orig_front + '\n' + kwargs.get('front', '')
        else:
            kwargs['front'] = orig_front + kwargs.get('front', '')

        if orig_back and orig_back[-1] != '\n':
            kwargs['back'] = orig_back + '\n' + kwargs.get('back', '')
        else:
            kwargs['back'] = orig_back + kwargs.get('back', '')

        self._cache_image(item_id, kwargs['front'])
        self._cache_image(item_id, kwargs['back'])

        self.data[item_id]._update(kwargs)

        self.save()

        return CardQuiz(self.data[item_id], image_dir=self.image_dir)

    def update(self, item_id: int, **kwargs):
        item_id = str(item_id)

        if item_id not in self.data.keys():
            raise KeyError("Cannot reset to {}.".format(item_id))

        if 'keywords' in kwargs.keys():
            kwargs['keywords'] = to_raw_tags(kwargs['keywords'])
        if 'tags' in kwargs.keys():
            kwargs['tags'] = to_raw_tags(kwargs['tags'])

        self._cache_image(item_id, kwargs.get('front', ''))
        self._cache_image(item_id, kwargs.get('back', ''))

        self.data[item_id]._update(kwargs)

        self.save()

        return CardQuiz(self.data[item_id], image_dir=self.image_dir)

    def _cache_image(self, item_id, text):
        for url in get_url_images_in_text(text):
            image_name = '{}-{}'.format(item_id, Path(url).name)
            if not urlparse(url).netloc:
                cache_image_from_file(image_name=image_name, image_path=url, image_dir=self.image_dir)
            else:
                cache_image_from_url(image_name=image_name, image_url=url, image_dir=self.image_dir)

    def remove(self, item_id):
        item_id = str(item_id)

        if item_id not in self.data.keys():
            raise KeyError("Cannot remove from {}.".format(item_id))

        self.data.pop(item_id)
        self.image_cleanup(item_id)

        self.save()

    def image_cleanup(self, item_id):
        record = self.data[str(item_id)]

        for url in get_url_images_in_text(record.front + '\n' + record.back):
            image_name = '{}-{}'.format(record.id, Path(url).name)

            if image_name in self.image_dir.keys():
                self.image_dir.pop(image_name)

            if self.image_dir['_path'].joinpath(image_name).exists():
                self.image_dir['_path'].joinpath(image_name).unlink()

    def find(self, keyword_regex: str = '', tags=None):
        if tags is None:
            tags = list()
        elif isinstance(tags, str):
            tags = [tags]
        else:
            tags = tags

        matched_entries = set()
        for item_id, item in self.data.items():
            keywords = tag_reader(item.keywords)
            keywords.add(item.front)
            keywords.add(item.back)

            for keyword in keywords:
                if re.search(keyword_regex, keyword, flags=re.IGNORECASE):
                    matched_entries.add(item_id)

        for item_id in matched_entries:
            if len(tags) == 0:
                yield self.data[item_id]
            elif compare_list_match_regex(tags, tag_reader(self.data[item_id].tags)):
                yield self.data[item_id]

    def preview(self, keyword_regex: str='', tags: list=None,
                file_format='handsontable', width=800, height=300):

        file_output = self.working_dir.joinpath('preview.{}.html'.format(file_format))

        try:
            pyexcel.save_as(
                records=[item._asdict() for item in self.find(keyword_regex, tags)],
                dest_file_name=str(file_output.absolute()),
                dest_sheet_name='Preview',
                # readOnly=False,
                js_url=module_path('handsontable.full.min.js'),
                css_url=module_path('handsontable.full.min.css')
            )

            return IFrame(str(file_output.relative_to('.')), width=width, height=height)
        finally:
            Timer(5, file_output.unlink).start()

    def quiz(self, keyword_regex: str='', tags: list=None, exclude: list =None, image_only=False):
        if exclude is None:
            exclude = list()
        else:
            exclude = [int(item_id) for item_id in exclude]

        all_records = [record for record in self.find(keyword_regex, tags) if record.id not in exclude]

        if image_only:
            all_records = [record for record in all_records
                           if len(get_url_images_in_text(record.front)) > 0]

        if len(all_records) == 0:
            return "There is no record matching the criteria."

        record = random.choice(all_records)

        return CardQuiz(record, image_dir=self.image_dir)

    def _load_raw_data(self, raw_data):
        if self.SHEET_NAME not in raw_data.keys():
            raise DatabaseHeaderException('Invalid Excel database.')

        data = OrderedDict()

        headers = [header_item.lower() for header_item in raw_data[self.SHEET_NAME][0]]
        if headers[0] != 'id':
            raise DatabaseHeaderException('Invalid Excel database.')

        for row in raw_data[self.SHEET_NAME][1:]:
            if row[0]:
                data[str(row[0])] = CardTuple(**dict(zip(headers, row)))

        return data

    @property
    def tags(self):
        tags = set()

        for v in self.data.values():
            tags.update(tag_reader(v.tags))

        return tags

    def view_id(self, item_id):
        return CardQuiz(self.data[str(item_id)], image_dir=self.image_dir)


def compare_list_match_regex(subset, superset):
    def _sub_compare(sub_item):
        for super_item in superset:
            if re.search(sub_item, super_item, flags=re.IGNORECASE):
                return True

        return False

    result = []
    for sub_item in subset:
        result.append(_sub_compare(sub_item))

    return all(result)
