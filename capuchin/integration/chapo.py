import requests

from capuchin import config


def get_redirect_url(url, canvas=True):
    redirector_path = ('/canvas' if canvas else '') + '/r/'
    redirector_url = 'https://' + config.REDIRECTOR_HOST + redirector_path

    response = requests.post(
        redirector_url,
        data={'url': url},
        headers={'Authorization': 'apikey {}'.format(config.REDIRECTOR_AUTH)},
        allow_redirects=False,
    )
    return response.headers['location']
