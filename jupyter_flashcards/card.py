from markdown import markdown
from IPython.display import HTML
import dateutil
from datetime import datetime, timedelta
from namedlist import namedlist

from .utils import parse_markdown
from .tags import tag_reader
from .srs import SRS


class CardQuiz:
    def __init__(self, card_id, record):
        """

        :param int card_id:
        :param CardTuple record:
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

    def next_srs(self):
        if not self.record.srs_level:
            self.record.srs_level = str(1)
        else:
            self.record.srs_level = str(int(self.record.srs_level) + 1)

        self.record.real_next_review = (datetime.now(datetime.now().astimezone().tzinfo)
                                        + SRS.get(int(self.record.srs_level), timedelta(weeks=4)))

    correct = right = next_srs

    def previous_srs(self, duration=timedelta(hours=4)):
        if self.record.srs_level and int(self.record.srs_level) > 1:
            self.record.srs_level = str(int(self.record.srs_level) - 1)

        self.bury(duration)

    incorrect = wrong = previous_srs

    def bury(self, duration=timedelta(hours=4)):
        self.record.real_next_review = (datetime.now(datetime.now().astimezone().tzinfo)
                                        + duration)


CardNL = namedlist('CardNL', ['front', 'back', 'keywords', 'tags', 'srs_level', 'next_review'], default='')


class CardTuple(CardNL):
    def to_formatted_tuple(self):
        return (self.front, self.back, self.keywords, self.tags,
                self.srs_level, self.next_review)

    @property
    def real_next_review(self):
        if self.next_review:
            return dateutil.parser.parse(self.next_review)
        else:
            return datetime.now(datetime.now().astimezone().tzinfo)

    @real_next_review.setter
    def real_next_review(self, value):
        """

        :param datetime value:
        :return:
        """
        self.next_review = value.isoformat()
