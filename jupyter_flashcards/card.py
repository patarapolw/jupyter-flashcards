from markdown import markdown
from IPython.display import HTML
from typing import NamedTuple
import dateutil
from datetime import datetime

from .utils import parse_markdown
from .tags import tag_reader


class CardQuiz:
    def __init__(self, card_id, record):
        """

        :param int card_id:
        :param dict|OrderedDict record:
        """
        assert isinstance(record, CardTuple)

        self.record = record
        self.id = card_id

    def _repr_html_(self):
        html = parse_markdown(self.record.front)

        return html

    def show(self):
        html = parse_markdown(self.record.back)
        html += markdown("**Keywords:** " + ', '.join(tag_reader(self.record.keywords)))
        html += markdown("**Tags:** " + ', '.join(tag_reader(self.record.tags)))

        return HTML(html)


class CardTuple(NamedTuple):
    front: str = ''
    back: str = ''
    keywords: str = ''
    tags: str = ''
    srs_level: str = ''
    next_review: str = ''

    def to_formatted_tuple(self):
        return (self.front, self.back, self.keywords, self.tags,
                self.srs_level, self.next_review)

    @property
    def real_next_review(self):
        if self.next_review:
            return dateutil.parser.parse(self.next_review)
        else:
            return datetime.now()

    @real_next_review.setter
    def real_next_review(self, value):
        """

        :param datetime value:
        :return:
        """
        self.next_review = value.isoformat()
