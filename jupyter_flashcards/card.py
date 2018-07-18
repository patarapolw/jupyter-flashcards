from markdown import markdown
from urllib.parse import urlparse
from IPython.display import HTML
import re
import namedlist as nl
from pathlib import Path

from .utils import get_url_images_in_text
from .cache import cache_image_from_url, cache_image_from_file
from .tags import tag_reader

CardTuple = nl.namedlist('CardTuple', [
    'id',
    ('front', ''),
    ('back', ''),
    ('keywords', ''),
    ('tags', '')
])


class CardQuiz:
    def __init__(self, record, image_dir):
        """

        :param dict|OrderedDict record:
        :param dict image_dir:
        """
        assert isinstance(record, CardTuple)

        self.record = record
        self.image_dir = image_dir
        self.id = record.id

    def _repr_html_(self):
        html = self._parse_markdown(re.sub(r'\n+', '\n\n', self.record.front))
        # html += "<br />" + markdown(self.record.keywords)
        # html += "<br />" + markdown(self.record.tags)

        return html

    def show(self):
        html = self._parse_markdown(re.sub(r'\n+', '\n\n', self.record.back))
        html += markdown("**Keywords:** " + ', '.join(tag_reader(self.record.keywords)))
        html += markdown("**Tags:** " + ', '.join(tag_reader(self.record.tags)))

        return HTML(html)

    def _parse_markdown(self, text):
        for url in get_url_images_in_text(text):
            image_name = '{}-{}'.format(self.record.id, Path(url).name)

            if urlparse(url).netloc:
                text = text.replace(url, '<img src="{}" />'
                                    .format(str(cache_image_from_url(image_name=image_name, image_url=url,
                                                                     image_dir=self.image_dir)
                                                .relative_to('.'))))
            else:
                text = text.replace(url, '<img src="{}" />'
                                    .format(str(cache_image_from_file(image_name=image_name, image_path=url,
                                                                      image_dir=self.image_dir)
                                                .relative_to('.'))))

        return markdown(text)
