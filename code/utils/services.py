from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import tempfile
from bs4 import BeautifulSoup


def get_temp_image(name='test.png'):
    image = Image.new('RGB', (100, 100), color='red')
    temp_file = tempfile.NamedTemporaryFile(suffix='.png')
    image.save(temp_file, format='PNG')
    temp_file.seek(0)
    return SimpleUploadedFile(name, temp_file.read(), content_type='image/png')


def make_rtl(html):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "li", "td", "th"]):
        tag["dir"] = "rtl"

    return str(soup)