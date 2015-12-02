from django.template.loaders.base import Loader
from django.utils.crypto import get_random_string


def generate_tokens(**kwargs):
    """
    Returns a dict with random access_token and refresh_token.
    Whatever is passed via kwargs will be added or replace
    dict values.
    """
    defaults = {
        'access_token': get_random_string(length=30),
        'refresh_token': get_random_string(length=30)
    }
    defaults.update(kwargs)
    return defaults


class DummyTemplateLoader(Loader):
    is_usable = True

    def load_template_source(self, template_name, template_dirs=None):
        if template_name == 'login.html':
            return '{% csrf_token %}', 'dummy'
        return 'dummy', 'dummy'
