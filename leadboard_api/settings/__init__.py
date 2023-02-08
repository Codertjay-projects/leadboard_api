"""
Currently we have up to three different mode which are, LOCAL, PRODUCTION, PRODUCTION_DEBUG

The production_debug enables us to use the debug mode
"""
from decouple import config

# .ENV debug value
DEBUG = config('DEBUG', default=False, cast=bool)
# os debug value


# Use the variables set in the .env
if DEBUG:
    from .local import *
elif not DEBUG:
    from .production import *


