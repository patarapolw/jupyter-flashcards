import re


def get_url_images_in_text(text):
    return re.findall(r'([^\s<>"\']+\.(?:png|jpg|jpeg|gif))', text)
