from pathlib import Path
from collections import OrderedDict
from time import time
import re
import random
from threading import Timer
from IPython.display import display
from bs4 import BeautifulSoup

import pyexcel_export
from pyhandsontable import view_table

from .tags import tag_reader
from .utils import get_url_images_in_text, compare_list_match_regex
from .card import CardQuiz, CardTuple


class Flashcards:
    def __init__(self, in_file, sheet_name=None):
        """

        :param str|Path in_file: can be a folder, *.xlsx or *.zip
        :param str sheet_name:
        """
        if sheet_name is None:
            sheet_name = 'flashcards'

        self.modified = time()
        self._sheet_name = sheet_name

        if not isinstance(in_file, Path):
            in_file = Path(in_file)

        self.working_dir = in_file.parent.joinpath(in_file.stem)

        if in_file.exists():
            if in_file.suffix != '':
                self.excel = in_file
                self.all_sheets, self.meta = pyexcel_export.get_data(str(self.excel))

                self.data = self._load_raw_data(self.all_sheets, self._sheet_name)
            else:
                self.excel = in_file.joinpath(in_file.stem + '.xlsx')
                self.working_dir = in_file.joinpath(in_file.stem)

                if not self.working_dir.exists():
                    self.working_dir.mkdir()

                self.all_sheets, self.meta = pyexcel_export.get_data(str(self.excel))

                self.data = self._load_raw_data(self.all_sheets, self._sheet_name)

        else:
            self.excel = in_file
            self.data = OrderedDict()

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

        out_matrix = []
        header = [header_item.title() if header_item != 'id' else header_item
                  for header_item in list(self.data.values())[0]._fields]
        out_matrix.append(header)

        for card_id, card_tuple in self.data.items():
            out_matrix.append(list(card_tuple))

        self.all_sheets[self._sheet_name] = out_matrix

        pyexcel_export.save_data(out_file=out_file, data=self.all_sheets, meta=self.meta)

    # def add(self, append_to=None, **kwargs):
    #     """
    #
    #     :param append_to: if append to_is specified, the method self.append is used, with item_id = append_to
    #     :param kwargs:
    #     :return:
    #     """
    #     if append_to is None:
    #         item_id = int(time() * 1000)
    #         self.data[str(item_id)] = CardTuple()
    #
    #         print("Card id: {}".format(item_id))
    #
    #         return self.append(item_id, **kwargs)
    #     else:
    #         return self.append(append_to, **kwargs)
    #
    # def append(self, item_id, **kwargs):
    #     """
    #
    #     :param int|str item_id:
    #     :param kwargs:
    #     :return:
    #     """
    #     item_id = str(item_id)
    #
    #     if item_id not in self.data.keys():
    #         raise KeyError("Cannot append to {}.".format(item_id))
    #
    #     if self.data[item_id].keywords:
    #         orig_keywords = self.data[item_id].keywords
    #     else:
    #         orig_keywords = ''
    #
    #     if self.data[item_id].tags:
    #         orig_tags = self.data[item_id].tags
    #     else:
    #         orig_tags = ''
    #
    #     keywords = kwargs.get('keywords', [])
    #     keywords.extend(tag_reader(orig_keywords))
    #     kwargs['keywords'] = to_raw_tags(keywords)
    #
    #     tags = kwargs.get('tags', [])
    #     tags.extend(tag_reader(orig_tags))
    #     kwargs['tags'] = to_raw_tags(tags)
    #
    #     orig_front = self.data[item_id].front
    #     orig_back = self.data[item_id].back
    #
    #     if orig_front and orig_front[-1] != '\n':
    #         kwargs['front'] = orig_front + '\n' + kwargs.get('front', '')
    #     else:
    #         kwargs['front'] = orig_front + kwargs.get('front', '')
    #
    #     if orig_back and orig_back[-1] != '\n':
    #         kwargs['back'] = orig_back + '\n' + kwargs.get('back', '')
    #     else:
    #         kwargs['back'] = orig_back + kwargs.get('back', '')
    #
    #     self.data[item_id]._update(kwargs)
    #
    #     self.save()
    #
    #     card = CardQuiz(int(item_id), self.data[item_id])
    #
    #     display(card)
    #     display(card.show())
    #
    #     # return card
    #
    # def update(self, item_id: int, **kwargs):
    #     item_id = str(item_id)
    #
    #     if item_id not in self.data.keys():
    #         raise KeyError("Cannot reset to {}.".format(item_id))
    #
    #     if 'keywords' in kwargs.keys():
    #         kwargs['keywords'] = to_raw_tags(kwargs['keywords'])
    #     if 'tags' in kwargs.keys():
    #         kwargs['tags'] = to_raw_tags(kwargs['tags'])
    #
    #     self.data[item_id]._update(kwargs)
    #
    #     self.save()
    #
    #     card = CardQuiz(int(item_id), self.data[item_id])
    #
    #     display(card)
    #     display(card.show())
    #
    #     # return card
    #
    # def remove(self, item_id):
    #     item_id = str(item_id)
    #
    #     if item_id not in self.data.keys():
    #         raise KeyError("Cannot remove from {}.".format(item_id))
    #
    #     self.data.pop(item_id)
    #
    #     self.save()
    #
    #     return "{} removed.".format(item_id)

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
                yield item_id, self.data[item_id]
            elif compare_list_match_regex(tags, tag_reader(self.data[item_id].tags)):
                yield item_id, self.data[item_id]

    def view(self, keyword_regex: str = '', tags: list = None, width=800, height=500):
        renderers = {
            1: 'markdownRenderer',
            2: 'markdownRenderer'
        }
        config = {
            'colHeaders': ['id'] + list(CardTuple._fields),
            'rowHeaders': False
        }

        filename = Path('temp.handsontable.html')
        try:
            table = view_table(data=list(reversed([[i] + list(record.to_formatted_tuple())
                                                   for i, record in self.find(keyword_regex, tags)])),
                               width=width,
                               height=height,
                               renderers=renderers,
                               config=config,
                               filename=str(filename),
                               autodelete=False)
            with filename.open('r') as f:
                soup = BeautifulSoup(f.read(), 'html5lib')

            style = soup.new_tag('style')

            with Path('jupyter_flashcards/renderer/markdown-hot.css').open('r') as f:
                style.append(f.read())

            soup.head.append(style)

            div = soup.new_tag('div')

            js_markdown = soup.new_tag('script',
                                       src='https://cdn.rawgit.com/showdownjs/showdown/1.8.6/dist/showdown.min.js')
            js_custom = soup.new_tag('script')

            with Path('jupyter_flashcards/renderer/markdown-hot.js').open('r') as f:
                js_custom.append(f.read())

            div.append(js_markdown)
            div.append(js_custom)

            script_tag = soup.find('script', {'id': 'generateHandsontable'})
            soup.body.insert(soup.body.contents.index(script_tag), div)

            with filename.open('w') as f:
                f.write(str(soup))

            return table
        finally:
            Timer(5, filename.unlink).start()
            # pass

    def iter_quiz(self, keyword_regex: str = '', tags: list = None, exclude: list = None, image_only=False,
                  begin: int = None, last: int = None):
        if exclude is None:
            exclude = list()

        all_records = list(reversed([(i, record)
                                     for i, record in self.find(keyword_regex, tags)
                                     if i not in exclude]))[begin:last]

        if image_only:
            all_records = [(i, record) for i, record in all_records
                           if len(get_url_images_in_text(record.front)) > 0]

        if len(all_records) == 0:
            return "There is no record matching the criteria."

        random.shuffle(all_records)
        for i, record in all_records:
            yield CardQuiz(i, record)

    def quiz(self, keyword_regex: str = '', tags: list = None, exclude: list = None, image_only=False,
             begin: int = None, last: int = None):
        return next(self.iter_quiz(keyword_regex, tags, exclude, image_only, begin=begin, last=last))

    @staticmethod
    def _load_raw_data(raw_data, sheet_name):
        data = OrderedDict()

        headers = [header_item.lower().replace(' ', '_') for header_item in raw_data[sheet_name][0]]
        for i, row in enumerate(raw_data[sheet_name][1:]):
            data[i] = CardTuple(**dict(zip(headers, row)))

        return data

    @property
    def tags(self):
        tags = set()

        for v in self.data.values():
            tags.update(tag_reader(v.tags))

        return tags

    def view_id(self, item_id):
        card = CardQuiz(item_id, self.data[str(item_id)])

        display(card)
        display(card.show())

        # return card

    @property
    def sheet_name(self):
        return self._sheet_name

    @sheet_name.setter
    def sheet_name(self, value):
        self._sheet_name = value
        self.data = self._load_raw_data(self.all_sheets, self._sheet_name)
