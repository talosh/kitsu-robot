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

conn = flapi.Connection(
    'ws.baselight1',
    username='filmlight',
    token='3599641beb617f68485b447589af230d'
)
conn.connect()

scene_path = conn.Scene.parse_path('fs.flux1:dlj0395_soviet_milk:grade:soviet_milk_grd_06')
scene = conn.Scene.open_scene( scene_path, { flapi.OPENFLAG_READ_ONLY } )

nshots = scene.get_num_shots()
if nshots > 0:
    shots = scene.get_shot_ids(0, nshots)
    for shot_ix, shot_inf in enumerate(shots):
        shot = scene.get_shot(shot_inf.ShotId)

        thumbnail_url = conn.ThumbnailManager.get_poster_uri(shot, 0, {'DCSpace': 'sRGB'})
        print (thumbnail_url)

        shot.release()

scene.close_scene()
scene.release()
conn.close()