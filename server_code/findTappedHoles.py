import numpy as np

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



def apply_view_matrix(coord, view_matrix):
    # Convert the view matrix into a 4x4 numpy matrix
    view_matrix = np.array(view_matrix).reshape((4, 4))
    
    # Convert 3D coordinate to 4D homogeneous coordinate (adding 1 for w)
    coord_4d = np.array([coord[0], coord[1], coord[2], 1.0])
    
    # Apply the view matrix transformation
    transformed_coord_4d = np.dot(view_matrix, coord_4d)
    
    # Convert back to 3D by dividing by w (if w is not 1)
    if transformed_coord_4d[3] != 0:
        transformed_coord_3d = transformed_coord_4d[:3] / transformed_coord_4d[3]
    else:
        transformed_coord_3d = transformed_coord_4d[:3]
    
    return transformed_coord_3d

def check_hole_match(modelHoles, dxfHole, viewMatrix):
    dxfHole = np.array(dxfHole)
    
    for hole in modelHoles['Holes']:
        # Get the coordinates for both edges and the size
        cEdge1 = hole['cEdge1']
        cEdge2 = hole['cEdge2']
        size = hole['Size']
        
        # Transform the coordinates using the viewMatrix
        transformed_cEdge1 = apply_view_matrix(cEdge1, viewMatrix)
        transformed_cEdge2 = apply_view_matrix(cEdge2, viewMatrix)
        
        # Compare the transformed coordinates with dxfHole
        if np.allclose(transformed_cEdge1, dxfHole, atol=1e-6):
            return True, tuple(transformed_cEdge1), size
        if np.allclose(transformed_cEdge2, dxfHole, atol=1e-6):
            return True, tuple(transformed_cEdge2), size
    
    return False, None, None

# Call the function
result, matched_coord, hole_size = check_hole_match(modelHoles, dxfHole, viewMatrix)