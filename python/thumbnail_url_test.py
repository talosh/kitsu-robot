import os

app_path = os.path.dirname(os.path.abspath(__file__))
flapi_module_path = os.path.join(
    os.path.dirname(app_path),
    'flapi',
    'python'
)

print (flapi_module_path)