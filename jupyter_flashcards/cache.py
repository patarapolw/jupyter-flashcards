import requests
from pathlib import Path
import logging

debugger_logger = logging.getLogger('debug')


def cache_image_from_url(image_name, image_url, image_dir, forced=False):
    if forced or image_name not in image_dir.keys():
        assert isinstance(image_dir['_path'], Path)

        image_dir[image_name] = image_dir['_path'].joinpath(image_name)

        with image_dir[image_name].open('wb') as f:
            try:
                response = requests.get(image_url, stream=True)

                if not response.ok:
                    debugger_logger.debug(response)

                for block in response.iter_content(1024):
                    if not block:
                        break

                    f.write(block)

                return image_dir[image_name]

            except requests.exceptions.ConnectionError as e:
                debugger_logger.debug(e)

                return False

    return image_dir[image_name]


def cache_image_from_file(image_name, image_path, image_dir, forced=False):
    if forced or image_name not in image_dir.keys():
        assert isinstance(image_dir['_path'], Path)

        image_dir[image_name] = image_dir['_path'].joinpath(image_name)

        image_dir[image_name].write_bytes(Path(image_path).read_bytes())

        return image_dir[image_name]
    else:
        return False
