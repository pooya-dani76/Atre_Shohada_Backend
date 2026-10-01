from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import tempfile


def get_temp_image(name='test.png'):
    image = Image.new('RGB', (100, 100), color='red')
    temp_file = tempfile.NamedTemporaryFile(suffix='.png')
    image.save(temp_file, format='PNG')
    temp_file.seek(0)
    return SimpleUploadedFile(name, temp_file.read(), content_type='image/png')