import math
import numpy

'''UTILITY FUNCTIONS'''
def search(lst, key, value):
    listIndex = next((index for (index, d) in enumerate(lst) if d[key] == value), None)
    return listIndex


def dotProduct(vector1, vector2):
    dotproductVal = (vector1[0] * vector2[0]) + (vector1[1] * vector2[1]) + (vector1[2] * vector2[2])
    dotproductVal = abs(dotproductVal)
    #dotproductVal = round(dotproductVal)
    #print(f'Dot Product is: {dotproductVal}')
    return dotproductVal


def pointDistance(point1, point2):
    dist = math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2 + (point1[2] - point2[2])**2)
    #print(f'Distance between points: {dist}')
    return dist

'''-----------------------------------------------------------------------------------------------------------------'''


def findExportFaces(body):
    global test_normal
    test_normal = 0
    faceInfo = {}   #Create dictionary of export data
    faceInfo['Operations'] = None
    tolerance = 0.0001
    tolerance2 = 0.0000000001
    perimeter = 0
    qtyFaces = len(body['Faces'])
    facesList = body['Faces'].copy()
    #print("There are ", qtyFaces, " faces")
    #Create a list of only the planar faces
    planarFaces = [i for i in facesList if i['surface']['type'] == 'plane'] # COuld replace facesList here with bodyDetails['bodies'][ibody]['faces'], one less list to worry about
    #Changed from ==0 to <2 to allow for no error if part with no planar faces such a sphere, or one planar face such as a cone is tested
    if len(planarFaces) <2:
        #print("No Planar faces")
        return False    #No planar faces
    '''
    Find the two largest face Indices
    https://www.geeksforgeeks.org/ways-sort-list-dictionaries-values-python-using-lambda-function/
    https://www.geeksforgeeks.org/python-indices-of-n-largest-elements-in-list/
    '''

    #Sort list into area ascending order - if difference between first two areas is within tolerance, then we have two matching largest areas
    descendingAreaList = sorted(range(len(planarFaces)), key = lambda sub: planarFaces[sub]['area'],reverse = True)[-len(planarFaces):]  #List of indices in area descending order
    if abs(planarFaces[descendingAreaList[0]]['area'] - planarFaces[descendingAreaList[1]]['area']) <= tolerance:
        #Check if the two largest faces are parallel
        #Faces are parallel if dot product = 1

        '''Coplanar Check
        if (planarFaces[descendingAreaList[0]]['surface']['normal'][0] / planarFaces[descendingAreaList[1]]['surface']['normal'][0]) == (planarFaces[descendingAreaList[0]]['surface']['normal'][1] / planarFaces[descendingAreaList[1]]['surface']['normal'][1]) and (planarFaces[descendingAreaList[0]]['surface']['normal'][1] / planarFaces[descendingAreaList[1]]['surface']['normal'][1]) == (planarFaces[descendingAreaList[0]]['surface']['normal'][2] / planarFaces[descendingAreaList[1]]['surface']['normal'][2]):
            print('Largest Planes are Coplanar')'''
        parallelCheck = abs((planarFaces[descendingAreaList[0]]['surface']['normal'][0] * planarFaces[descendingAreaList[1]]['surface']['normal'][0])
        + (planarFaces[descendingAreaList[0]]['surface']['normal'][1] * planarFaces[descendingAreaList[1]]['surface']['normal'][1])
        + (planarFaces[descendingAreaList[0]]['surface']['normal'][2] * planarFaces[descendingAreaList[1]]['surface']['normal'][2]))

        #print(parallelCheck)
        if abs(parallelCheck - 1) <= tolerance2:

            #Check thickness between faces
            #face0V5 = (planarFaces[descendingAreaList[0]]['surface']['origin']['x'], planarFaces[descendingAreaList[0]]['surface']['origin']['y'], planarFaces[descendingAreaList[0]]['surface']['origin']['z']) #v5
            #face1V5 = (planarFaces[descendingAreaList[1]]['surface']['origin']['x'], planarFaces[descendingAreaList[1]]['surface']['origin']['y'], planarFaces[descendingAreaList[1]]['surface']['origin']['z']) #v5
            partThk = pointDistance(planarFaces[descendingAreaList[0]]['surface']['origin'], planarFaces[descendingAreaList[1]]['surface']['origin']) #v1 API
            partThk = float(numpy.round(partThk, 3))  #Round number
            #print(f'Part Thickness: {partThk}')
            #partThk = round(partThk*1000)
            if partThk > body['Max Thickness']:
                #print("Part is too thick")
                return False
            #print(partThk)
            #print(f"Origin-0: {planarFaces[descendingAreaList[0]]['surface']['origin']}")
            #print(f"Origin-1: {planarFaces[descendingAreaList[1]]['surface']['origin']}")
            #print(f"The two largest planar faces found have equal area, they are: {planarFaces[descendingAreaList[0]]['id']} and {planarFaces[descendingAreaList[1]]['id']} and they are PARALLEL, Thickness is {partThk*1000, 'mm'}")
            #index [0] of descendingAreaList is the face with largest area which all remaining tests need to be carried out on
            largestFace0 = planarFaces[descendingAreaList[0]]['id']
            largestFace1 = planarFaces[descendingAreaList[1]]['id']
            #Get list index position for the main face in the list of all faces - facesList
            largestFace0_index = next((index for (index, d) in enumerate(facesList) if d["id"] == largestFace0), None)
            largestFace1_index = next((index for (index, d) in enumerate(facesList) if d["id"] == largestFace1), None)
        else:
            #print("Faces are NOT parallel, NOT ELIGIBLE FOR EXPORT")
            return False

    else:
        #print("The two largest planar faces found DO NOT have equal area, NOT ELIGIBLE FOR EXPORT")
        return False


#print(largestFace0_index)
#pprint(facesList)

    '''Function creates a list of edges for the selected face'''
    def get_face_edges(face_index):
        edge_list = list()
        edge_list.clear()
        for coedge_data in facesList[face_index]['loops']:
            coedges = coedge_data['coedges']
            for edge_data in coedges:
                edgeId = edge_data['edgeId']
                #edgeId = facesList[face_index]['loops']['coedges']['edgeId']
                edge_list.append(edgeId)
        return edge_list

    '''Function to check if the tested face is adjacent to both largest faces'''
    def  check_adjacent_faces():
        #Get edges of two largest faces
        largestFace0_Edges = get_face_edges(largestFace0_index)
        largestFace1_Edges = get_face_edges(largestFace1_index)

        for i in range(qtyFaces):
            if i == largestFace0_index or i == largestFace1_index:
                continue
            test_edge = get_face_edges(i)
            bool = (any(elem in largestFace0_Edges  for elem in test_edge)) and (any(elem in largestFace1_Edges  for elem in test_edge))
            if bool == False:
                return False

            return True

    '''Function to check all other faces are perpendicular'''
    def check_perpendicular_faces():
            largestFace0_Edges = get_face_edges(largestFace0_index)
            largestFace1_Edges = get_face_edges(largestFace1_index)
            #Normal for first largest face
            normal1 = facesList[largestFace0_index]['surface']['normal']
            #print(f"Normal1: {normal1}")
            #Normal for other largest face
            normal2 = facesList[largestFace1_index]['surface']['normal']
            #print(f"Normal2: {normal1}")
            #Get testing normal
            for i in range(qtyFaces):
                if i == largestFace0_index or i == largestFace1_index:
                    continue

                if facesList[i]['surface']['type'] == 'plane':
                    global test_normal
                    test_normal = facesList[i]['surface']['normal']
                    i_1 = abs((normal1[0] * test_normal[0]) + (normal1[1] * test_normal[1]) + (normal1[2] * test_normal[2]))
                    i_2 = abs((normal2[0] * test_normal[0]) + (normal2[1] * test_normal[1]) + (normal2[2] * test_normal[2]))
                    #print(f"Perpendicularity Planar Logging: i_1 = {i_1},  i_2 = {i_2}")
                    #Dot product should be = 0
                    #if i_1 != ((1-i_1) <= tolerance) and ((1-i_2) <= tolerance) != 0:
                    if abs(i_1 - 1) <= tolerance2 and abs(i_1 - 1) <= tolerance2:
                        #Faces are NOT perpendicular
                        #print('Planes are not Perpendicular')
                        return False

                else:
                    try:
                        test_normal = facesList[i]['surface']['axis']
                        #Axis needs to be parallel to main surfaces, ie dot product = 1

                        i_1 = abs((normal1[0] * test_normal[0]) + (normal1[1] * test_normal[1]) + (normal1[2] * test_normal[2]))
                        i_2 = abs((normal2[0] * test_normal[0]) + (normal2[1] * test_normal[1]) + (normal2[2] * test_normal[2]))
                        #print(f"Perpendicularity Axis Logging: i_1 = {i_1},  i_2 = {i_2}")
                        #if i_1 != 1 and i_2 != 1:
                        if abs(i_1 - 1) >= tolerance2 and abs(i_1 - 1) >= tolerance2:
                            #Axis not parallel to surface normals
                            #print('Axis is not perpendicular')
                            return False
                    except:
                        return False

            return True


    '''Function to find the longest edge and set view matrix - Find the longest edge of the face'''
    def getLongestEdge():
        edgeLengthFinal = 0
        longestLinear = 0
        longestNonLinear = 0
        linearEdgeFlag = 0
        largestFace0_Edges = get_face_edges(largestFace0_index)
        for a in largestFace0_Edges:
            #print(f"Longest Edges: = {largestFace0_Edges}")
            #print(f"Integer: = {a}")
            #print(f"Testing Edge: = {a}")
            longestEdgeIndex = search(body['Edges'], "id", a)
            if str(body['Edges'][longestEdgeIndex]['curve']['type']) == 'line':
                edgeLength = (body['Edges'][longestEdgeIndex]['geometry']['length'])
                if edgeLength >= longestLinear:
                    longestLinear = edgeLength
                    linearEdgeFlag = 1
                    longestLinearEdgeID = a
            else:
                edgeLength = (body['Edges'][longestEdgeIndex]['geometry']['length'])
                if edgeLength >= longestNonLinear:
                    longestNonLinear = edgeLength
                    longestNonLinearEdgeId = a
            if linearEdgeFlag == 1:
                longestEdgeID = longestLinearEdgeID
            else:
                longestEdgeID = longestNonLinearEdgeId
                #print(f"Edge ID: {longestEdgeID} = {edgeLengthFinal}")
        return longestEdgeID




    def createViewMatrix(longestEdgeID):
        viewMatrix = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]

        longestEdgeIndex = search(body['Edges'], "id", longestEdgeID)

        #x = 0,1,2
        viewMatrix[0] = body['Edges'][longestEdgeIndex]['geometry']['startVector'][0]                 #longestEdgeIndex['edges']['geometry']['startVector'][0]
        viewMatrix[1] = body['Edges'][longestEdgeIndex]['geometry']['startVector'][1]
        viewMatrix[2] = body['Edges'][longestEdgeIndex]['geometry']['startVector'][2]

        #y = 4,5,6
        '''Use numpy to find the cross product of x axis (startVector) and the face normal to give y axis'''
        yAxis = numpy.cross(body['Edges'][longestEdgeIndex]['geometry']['startVector'],facesList[largestFace0_index]['surface']['normal'] )
        viewMatrix[4] = -yAxis[0]
        viewMatrix[5] = -yAxis[1]
        viewMatrix[6] = -yAxis[2]


        #z = 8,9,10 - Normal
        viewMatrix[8] = facesList[largestFace0_index]['surface']['normal'][0]
        viewMatrix[9] = facesList[largestFace0_index]['surface']['normal'][1]
        viewMatrix[10] = facesList[largestFace0_index]['surface']['normal'][2]

        #Transform = 12,13,14 - Face origin - World origin
        viewMatrix[12] = facesList[largestFace0_index]['surface']['origin'][0] - 0
        viewMatrix[13] = facesList[largestFace0_index]['surface']['origin'][1] - 0
        viewMatrix[14] = facesList[largestFace0_index]['surface']['origin'][2] - 0

        #print(f"View Matrix: {viewMatrix}")
        return viewMatrix




    



    #print(largestFace0_Edges)
    #print(largestFace1_Edges)

    #Sheetmetal part already identified by a flag previously, needs to work this way
    #because the way a sheet metal pattern is described with faces means that some faces
    #are actually parallel and not perpendicular.
    if body['Sheet Metal'] == True:
        adj = True
        perp = True
        faceInfo['Operations'] = faceInfo['Operations'] + 'B'
    else:
        adj = check_adjacent_faces()
        perp = check_perpendicular_faces()
    #print("Faces adjacent result = ", adj)
    #print("Perpendicularity result = ", perp)

    if adj and perp == True:
        #Get perimeter of edge_list
        for i in body['Edges']:
            perimeter = perimeter + (i['geometry']['length'])
        longestEdge = getLongestEdge()
        #print("Longest Edge = ", longestEdge)
        viewMatrix = createViewMatrix(longestEdge)
        #Find the longest edge and it's direction vector - Used to set the x axis for the view matrix
        #Take care with a cylinder though, x direction needs to be perpendicular to its cylindrical axis.
        #https://math.stackexchange.com/questions/1502026/creating-a-bounding-box-for-2-points-with-a-custimizable-width
        #https://stackoverflow.com/questions/17332759/finding-vectors-with-2-points


        faceInfo["Face"] = largestFace0
        faceInfo["Thickness"] = partThk*1000
        faceInfo["Area"] = planarFaces[descendingAreaList[0]]['area']
        faceInfo["Origin"] = planarFaces[descendingAreaList[0]]['surface']['origin']
        faceInfo["Normal"] = planarFaces[descendingAreaList[0]]['surface']['normal']
        faceInfo["EdgePerimeter"] = perimeter
        faceInfo["LongestEdge"] = longestEdge
        faceInfo["ViewMatrix"] = viewMatrix
        faceInfo["Description"] = str(partThk*1000) + 'mm Laser Plate'
        faceInfo["BoxMinCorner"] = facesList[largestFace0_index]['box']['minCorner']
        faceInfo["BoxMaxCorner"] = facesList[largestFace0_index]['box']['maxCorner'] 

        #Clear List planarFaces
        planarFaces *= 0
        #Clear list facesList -
        facesList *= 0
        perimeter = 0

        return faceInfo
    else:
        return False

