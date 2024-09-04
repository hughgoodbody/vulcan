import numpy as np
import json
import requests
import pprint

def get_model_tapped_holes(onshape, did, wvm_type, wv, eid, pid):

  url = '/api/partstudios/d/%s/%s/%s/e/%s/featurescript' % (did, wvm_type, wv, eid)
  method = 'POST'
  payload = {
    'script': """function(context is Context, queries is map){
            
        var tappedHoles = {};
        var holeTotals = [];
        var tempHoles = [];
        var holeTallyMap = {};
        var onshapeTappedHoles = [];
        var holeQty = 0;
        var allBodies = qEverything(EntityType.BODY);

        for (var body in evaluateQuery(context, allBodies))
        {
            //println(body.transientId);
            if (body.transientId == definition.transId)
            {
                //debug(context, body, DebugColor.RED);
                var internals = qOwnedByBody(body, EntityType.FACE);
                var holes = qHoleFaces(internals);
                var evHoles = evaluateQuery(context, holes);
                //println(evHoles);
                for (var item in evHoles)
                {
                    var holeAtts = getAttributes(context, {
                            "entities" : item,

                        });
                    if ((size(holeAtts) == 0))
                    {
                        //println("Hole not tapped");
                    }
                    else
                    {
                        //println(holeAtts);
                        //Get coordinates of edges of face
                        var holeEdges = qAdjacent(item, AdjacencyType.EDGE, EntityType.EDGE);
                        //debug(context, holeEdges, DebugColor.GREEN);
                        var evHoleEdges = evaluateQuery(context, holeEdges);
                        for (var i = 0; i < size(evHoleEdges); i += 1)
                        {
                            var centre = evCurveDefinition(context, {
                                    "edge" : evHoleEdges[i]
                                });
                            //println("Centre coordinates" ~ centre.coordSystem.origin);

                            //Strip down to just numbers
                            //Place circle coordinates into tapped holes map
                            if (i == 1)
                            {
                                tappedHoles.cEdge1 = [centre.coordSystem.origin[0].value, centre.coordSystem.origin[1].value, centre.coordSystem.origin[2].value];
                            }
                            else
                            {
                                tappedHoles.cEdge2 = [centre.coordSystem.origin[0].value, centre.coordSystem.origin[1].value, centre.coordSystem.origin[2].value];
                            }
                            tappedHoles.Size = toString(holeAtts[0].tapSize);
                            tappedHoles.Size = '"' ~ tappedHoles.Size ~ '"';
                            
                        }
                        //println(tappedHoles);
                        onshapeTappedHoles = append(onshapeTappedHoles, tappedHoles);
                    }
                }
                //Create temp list of discrete hole sizes
                for (var item in onshapeTappedHoles)
                {
                    if (isIn(item.Size, tempHoles))
                    {
                        
                    }
                    else
                    {
                        tempHoles = append(tempHoles,item.Size);
                    }
                }
                //Find quantity of each discrete hole size
                for (var thitem in tempHoles)
                {
                    for (var item in onshapeTappedHoles)
                    {
                        if (item.Size == thitem)
                        {
                          holeQty = holeQty + 1;  
                        }
                    }
                    holeTotals = append(holeTotals, {"Size": thitem, "Qty": holeQty});
                    holeQty = 0;
                }
                //println(onshapeTappedHoles);
                //println(tempHoles);
                //println(holeTotals);
                var output = {"Holes": onshapeTappedHoles, "Totals": holeTotals};
                println(output);
               
                //debug(context, holes, DebugColor.RED);
            }
        }
        
    
  return output;
  }
  """,
    'queries': [{ "key" : "id", "value" : [ pid ] }]
            }
  params = {}
  resp = onshape.request(method, url, query=params, body=payload)
  resp = json.loads(resp.content)
  pprint(f"Tapped Hole Output: {resp}")
  # Going to be something like this: resp['result']['message']['value']
  return resp



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