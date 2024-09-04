
def get_model_tapped_holes(onshape, pid):

  url = '/api/partstudios/d/%s/%s/%s/e/%s/featurescript' % (did, wvm_type, wv, eid)
  method = 'POST'
  payload = {
    'script': """function(context is Context, queries is map){
            // Define the function's action


  return tappedHoleDict;
  }
  """,
    'queries': [{ "key" : "id", "value" : [ pid ] }]
            }
  params = {}
  resp = onshape.request(method, url, query=params, body=payload)
  resp = json.loads(resp.content)

  return tappedHoles

def transform_model_to_dxf_coordinates(viewMatrix, modelCoordinates):

  return holeCoordinateDxf


def is_dxf_hole_tapped():

  return