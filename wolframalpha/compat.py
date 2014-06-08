import six
from six.moves import http_client

def fix_HTTPMessage():
	"""
	Python 2 uses a deprecated method signature and doesn't provide the
	forward compatibility.
	Add it.
	"""
	if six.PY3:
		return

	http_client.HTTPMessage.get_content_type = http_client.HTTPMessage.gettype
	http_client.HTTPMessage.get_param = http_client.HTTPMessage.getparam
