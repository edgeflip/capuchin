from blinker import Namespace

client = Namespace()

facebook_connected = client.signal('facebook_connected')
