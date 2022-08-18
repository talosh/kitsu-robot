import os
import sys

app_path = os.path.dirname(os.path.abspath(__file__))
flapi_module_path = os.path.join(
    os.path.dirname(app_path),
    'flapi',
    'python'
)

if sys.path[0] != flapi_module_path:
    sys.path.insert(0, flapi_module_path)
import flapi

