import os.path
import bpy
import struct
import os
import math
from mathutils import Matrix
from bpy.props import *
from collections import OrderedDict

debug = True
log = False
profile = True
version = 3200

class XPlaneDebugger():
    def __init__(self):
        self.log = False

    def start(self,log):
        import time
#        import sys
#        import logging

        self.log = log

        if self.log:
            (name,ext) = os.path.splitext(bpy.context.blend_data.filepath)
            dir = os.path.dirname(bpy.context.blend_data.filepath)
            self.logfile = os.path.join(dir,name+'_'+time.strftime("%y-%m-%d-%H-%M-%S")+'_xplane2blender.log')

            # touch the file
            file = open(self.logfile,"w");
            file.close()

#            self.excepthook = sys.excepthook
#            sys.excepthook = self.exception
#            self.logger = logging.getLogger()
#            self.streamHandler = logging.StreamHandler()
#            self.fileHandler = logging.FileHandler(self.logfile)
#            self.logger.addHandler(self.streamHandler)
            
    def write(self,msg):
        file = open(self.logfile,"a")
        #file.seek(1,os.SEEK_END)
        file.write(msg)
        file.close()

    def debug(self,msg):
        print(msg)
        if self.log:
            self.write(msg+"\n")
        
    def exception(self,type,value,traceback):
        o = "Exception: "+type+"\n"
        o += "\t"+value+"\n"
        o += "\tTraceback: "+str(traceback)+"\n"
        self.write(o)
        
    def end(self):
        self.log = False
#        sys.excepthook = self.excepthook

if debug:
    debugger = XPlaneDebugger()

class XPlaneProfiler():
    def __init__(self):
        self.times = {}

    def start(self,name):
        from time import time

        if name in self.times:
            if self.times[name][3]:
                self.times[name][0] = time()
                self.times[name][3] = False

            self.times[name][2]+=1
        else:
            self.times[name] = [time(),0.0,1,False]

    def end(self,name):
        from time import time
        
        if name in self.times:
            self.times[name][1]+=time()-self.times[name][0]
            self.times[name][3] = True

    def getTime(self,name):
        return '%s: %6.4f sec (calls: %d)' % (name,self.times[name][1],self.times[name][2])

    def getTimes(self):
        _times = ''
        for name in self.times:
            _times+=self.getTime(name)+"\n"

        return _times


if profile:
    profiler = XPlaneProfiler()

class XPlaneCoords():
    def __init__(self,object):
        self.object = object

    def worldLocation(self):
        matrix = XPlaneCoords.convertMatrix(self.object.matrix_world)
        loc = matrix.translation_part()
        return loc #self.convert([loc[0],loc[1],loc[2]])

    def worldRotation(self):
        matrix = XPlaneCoords.convertMatrix(self.object.matrix_world)
        rot = matrix.rotation_part().to_euler("XZY")
        return rot #[-rot[0],rot[1],rot[2]]

    def worldAngle(self):
        return self.angle(self.worldRotation())

    def worldScale(self):
        matrix = XPlaneCoords.convertMatrix(self.object.matrix_world)
        scale = matrix.scale_part()
        return scale #self.convert([scale[0],scale[1],scale[2]],True)

    def world(self):
        matrix = XPlaneCoords.convertMatrix(self.object.matrix_world)
        loc = matrix.translation_part()
        rot = matrix.rotation_part().to_euler("XZY")
        scale = matrix.scale_part()
        return {'location':loc,'rotation':rot,'scale':scale,'angle':self.angle(rot)}

    def localLocation(self,parent):
        matrix = self.relativeConvertedMatrix(parent)
        loc = matrix.translation_part()
        return loc #self.convert([loc[0],loc[1],loc[2]])
        
    def localRotation(self,parent):
        matrix = self.relativeConvertedMatrix(parent)
        rot = matrix.rotation_part().to_euler("XYZ")
        return rot #self.convert([rot[0],rot[1],rot[2]])

    def localAngle(self,parent):
        return self.angle(self.localRotation())

    def localScale(self,parent):
        matrix = self.relativeConvertedMatrix(parent)
        scale = matrix.scale_part()
        return scale #self.convert([scale[0],scale[1],scale[2]],True)

    def local(self,parent):
        matrix = self.relativeConvertedMatrix(parent)
        loc = matrix.translation_part()
        rot = matrix.rotation_part().to_euler("XYZ")
        scale = matrix.scale_part()
        return {'location':loc,'rotation':rot,'scale':scale,'angle':self.angle(rot)}

    def angle(self,rot):
        return [math.degrees(rot[0]),math.degrees(rot[1]),math.degrees(rot[2])]

    def convert(self,co,scale = False):
        if (scale):
            return [co[0],co[2],co[1]]
        else:
            return [-co[0],co[2],co[1]]

    def relativeMatrix(self,parent):
        return self.object.matrix_world * parent.matrix_world.copy().invert()

    def relativeConvertedMatrix(self,parent):
        return XPlaneCoords.convertMatrix(self.object.matrix_world) * XPlaneCoords.convertMatrix(parent.matrix_world.copy().invert())

    @staticmethod
    def convertMatrix(matrix):
        import mathutils
        rmatrix = Matrix.Rotation(math.radians(-90),4,'X')
        return rmatrix*matrix


class XPlaneLight():
    def __init__(self,object):
        self.object = object
        self.name = object.name
        self.indices = [0,0]
        self.color = [object.data.color[0],object.data.color[1],object.data.color[2]]
        self.type = object.data.xplane.lightType

        # change color according to type
        if self.type=='flashing':
            self.color[0] = -self.color[0]
        elif self.type=='pulsing':
            self.color[0] = 9.9
            self.color[1] = 9.9
            self.color[2] = 9.9
        elif self.type=='strobe':
            self.color[0] = 9.8
            self.color[1] = 9.8
            self.color[2] = 9.8
        elif self.type=='traffic':
            self.color[0] = 9.7
            self.color[1] = 9.7
            self.color[2] = 9.7


class XPlaneLine():
    def __init_(self,object):
        self.object = object
        self.name = object.name
        self.indices = [0,0]


class XPlaneKeyframe():
    def __init__(self,keyframe,index,dataref,prim):
        self.value = keyframe.co[1]
        self.dataref = dataref
        self.translation = [0.0,0.0,0.0]
        self.rotation = [0.0,0.0,0.0]
        self.scale = [0.0,0.0,0.0]
        self.index = index
        self.primitive = prim
        object = prim.object

        # goto keyframe and read out object values
        # TODO: support subframes?
        self.frame = int(round(keyframe.co[0]))
        bpy.context.scene.frame_set(frame=self.frame)
        coords = XPlaneCoords(object)

        self.hide = object.hide_render

        if prim.parent!=None:
             # update objects so we get values from the keyframe
            prim.parent.object.update(scene=bpy.context.scene)
            object.update(scene=bpy.context.scene)
            
            world = coords.world()
            local = coords.local(prim.parent.object)

            self.location = world["location"]
            self.angle = world["angle"]
            self.scale = world["scale"]           
            
            self.locationLocal = local["location"]
            self.angleLocal = local["angle"]
            self.scaleLocal = local["scale"]
            # TODO: multiply location with scale of parent

            print(prim.name)
            print(self.locationLocal)
            print(prim.locationLocal)
            print(self.angleLocal)
            print(prim.angleLocal)

            for i in range(0,3):
                # remove initial location and rotation to get offset
                self.translation[i] = self.locationLocal[i]-prim.locationLocal[i]
                self.rotation[i] = self.angleLocal[i]-prim.angleLocal[i]
        else:
            # update object so we get values from the keyframe
            object.update(scene=bpy.context.scene)

            world = coords.world()

            self.location = world["location"]
            self.angle = world["angle"]
            self.scale = world["scale"]

            self.locationLocal = self.location
            self.angleLocal = self.angle
            self.scaleLocal = self.scale

            # remove initial location and rotation to get offset
            for i in range(0,3):
                self.translation[i] = self.location[i]-prim.location[i]
                self.rotation[i] = self.angle[i]-prim.angle[i]


class XPlanePrimitive():
    def __init__(self,object,parent = None):
        self.object = object
        self.name = object.name
        self.children = []
        self.parent = parent

        self.indices = [0,0]
        self.material = XPlaneMaterial(self.object)
        self.faces = None
        self.datarefs = {}
        self.attributes = {}
        self.animations = {}
        self.datarefs = {}
        
        # add custom attributes
        for attr in object.xplane.customAttributes:
            self.attributes[attr.name] = attr.value

        self.getCoordinates()
        self.getAnimations()

    def getCoordinates(self):
        # goto first frame so everything is in inital state
        bpy.context.scene.frame_set(frame=1)
        coords = XPlaneCoords(self.object)

        if self.parent!=None:
            # update object display so we have initial values
            self.parent.object.update(scene=bpy.context.scene)
            self.object.update(scene=bpy.context.scene)

            world = coords.world()
            local = coords.local(self.parent.object)

            # store initial location, rotation and scale
            self.location = world["location"]
            self.angle = world["angle"]
            self.scale = world["scale"]         
            
            self.locationLocal = local["location"]
            self.angleLocal = local["angle"]
            self.scaleLocal = local["scale"]
        else:
            # update object display so we have initial values
            self.object.update(scene=bpy.context.scene)
            
            world = coords.world()

            # store initial location, rotation and scale
            self.location = world["location"]
            self.angle = world["angle"]
            self.scale = world["scale"]
            self.locationLocal = [0.0,0.0,0.0]
            self.angleLocal = [0.0,0.0,0.0]
            self.scaleLocal = [0.0,0.0,0.0]

    def getAnimations(self):
        #check for animation
        if debug:
            debugger.debug("\t\t checking animations")
        if (self.object.animation_data != None and self.object.animation_data.action != None and len(self.object.animation_data.action.fcurves)>0):
            if debug:
                debugger.debug("\t\t animation found")
            #check for dataref animation by getting fcurves with the dataref group
            for fcurve in self.object.animation_data.action.fcurves:
                if debug:
                    debugger.debug("\t\t checking FCurve %s" % fcurve.data_path)
                if (fcurve.group != None and fcurve.group.name == "XPlane Datarefs"):
                    # get dataref name
                    index = int(fcurve.data_path.replace('["xplane"]["datarefs"][','').replace(']["value"]',''))
                    dataref = self.object.xplane.datarefs[index].path

                    if debug:
                        debugger.debug("\t\t adding dataref animation: %s" % dataref)
                        
                    if len(fcurve.keyframe_points)>1:
                        # time to add dataref to animations
                        self.animations[dataref] = []
                        self.datarefs[dataref] = self.object.xplane.datarefs[index]

                        # store keyframes temporary, so we can resort them
                        keyframes = []

                        for keyframe in fcurve.keyframe_points:
                            if debug:
                                debugger.debug("\t\t adding keyframe: %6.3f" % keyframe.co[0])
                            keyframes.append(keyframe)

                        # sort keyframes by frame number
                        keyframesSorted = sorted(keyframes, key=lambda keyframe: keyframe.co[0])
                        
                        for i in range(0,len(keyframesSorted)):
                            self.animations[dataref].append(XPlaneKeyframe(keyframesSorted[i],i,dataref,self))


class XPlaneMaterial():
    def __init__(self,object):
        self.object = object
        self.texture = None
        self.uv_name = None

        # Material
        self.attributes = {"ATTR_diffuse_rgb":None,
                           "ATTR_specular_rgb":None,
                           "ATTR_emission_rgb":None,
                           "ATTR_shiny_rat":None,
                           "ATTR_hard":None,
                           "ATTR_no_hard":None,
                           "ATTR_cull":None,
                           "ATTR_no_cull":None,                           
                           "ATTR_depth":None,
                           "ATTR_no_depth":None,
                           "ATTR_blend":None,
                           "ATTR_no_blend":None}

        if len(object.data.materials)>0:
            mat = object.data.materials[0]

            # diffuse
            if mat.diffuse_intensity>0:
                diffuse = [mat.diffuse_intensity*mat.diffuse_color[0],
                            mat.diffuse_intensity*mat.diffuse_color[1],
                            mat.diffuse_intensity*mat.diffuse_color[2]]
                self.attributes['ATTR_diffuse_rgb'] = "%6.3f %6.3f %6.3f" % (diffuse[0], diffuse[1], diffuse[2])

            # specular
            if mat.specular_intensity>0:
                specular = [mat.specular_intensity*mat.specular_color[0],
                            mat.specular_intensity*mat.specular_color[1],
                            mat.specular_intensity*mat.specular_color[2]]
                self.attributes['ATTR_specular_rgb'] = "%6.3f %6.3f %6.3f" % (specular[0], specular[1], specular[2])
                self.attributes['ATTR_shiny_rat'] = "%6.3f" % mat.specular_hardness

            # emission
            if mat.emit>0:
                emission = [mat.emit*mat.diffuse_color[0],
                            mat.emit*mat.diffuse_color[1],
                            mat.emit*mat.diffuse_color[2]]
                self.attributes['ATTR_emission_rgb'] = "%6.3f %6.3f %6.3f" % (emission[0], emission[1], emission[2])

            # surface type
            if mat.xplane.surfaceType != 'none':
                self.attributes['ATTR_hard'] = mat.xplane.surfaceType

            # backface culling
            if self.object.data.show_double_sided:
                self.attributes['ATTR_no_cull'] = True
            else:
                self.attributes['ATTR_cull'] = True

            # blend
            if mat.xplane.blend:
                self.attributes['ATTR_no_blend'] = "%6.3f" % mat.xplane.blendRatio

            # depth check
            if self.object.xplane.depth == False:
                self.attributes['ATTR_no_depth'] = True;

            # Texture and uv-coordinates
            if(len(mat.texture_slots)>0 and hasattr(mat.texture_slots[0],'use') and mat.texture_slots[0].use and mat.texture_slots[0].texture.type=="IMAGE"):
                tex =  mat.texture_slots[0].texture
                if(tex.image.file_format=='PNG'):
                    self.texture = os.path.basename(tex.image.filepath)

                if mat.texture_slots[0].texture_coords == 'UV':
                    self.uv_name = mat.texture_slots[0].uv_layer

            # add custom attributes
            for attr in mat.xplane.customAttributes:
                self.attributes[attr.name] = attr.value

class XPlaneFace():
    def __init__(self):
        self.vertices = [(0.0,0.0,0.0),(0.0,0.0,0.0),(0.0,0.0,0.0)]
        self.normals = [(0.0,0.0,0.0),(0.0,0.0,0.0),(0.0,0.0,0.0)]
        self.indices = [0,0,0]
        self.uvs = [(0.0,0.0),(0.0,0.0),(0.0,0.0)]
        self.smooth = False


class XPlaneFaces():
    def __init__(self):
        self.faces = []

    def append(self,face):
        self.faces.append(face)

    def remove(self,face):
        del self.faces[face]

    def get(self,i):
        if len(self.faces)-1>=i:
            return self.faces[i]
        else:
            return None


class XPlaneMesh():
    def __init__(self,file):
        self.vertices = []
        self.indices = []

        # store the global index, as we are reindexing faces
        globalindex = 0

        for prim in file['primitives']:
            prim.indices[0] = len(self.indices)
            
            # store the world translation matrix
            matrix = XPlaneCoords.convertMatrix(prim.object.matrix_world)

            # create a copy of the object mesh with modifiers applied
            mesh = prim.object.create_mesh(bpy.context.scene, True, "PREVIEW")
            
            # transform mesh with the world matrix
            mesh.transform(matrix)

            # with the new mesh get uvFaces list
            uvFaces = self.getUVFaces(mesh,prim.material.uv_name)

#            faces = XPlaneFaces()

            # convert faces to triangles
            tempfaces = []
            for i in range(0,len(mesh.faces)):
                if uvFaces != None:
                    tempfaces.extend(self.faceToTrianglesWithUV(mesh.faces[i],uvFaces[i]))
                else:
                    tempfaces.extend(self.faceToTrianglesWithUV(mesh.faces[i],None))
                    
            for f in tempfaces:
#                xplaneFace = XPlaneFace()
                l = len(f['indices'])
                for i in range(0,len(f['indices'])):
                    # get the original index but reverse order, as this is reversing normals
                    vindex = f['indices'][2-i]
                    
                    # get the vertice from original mesh
                    v = mesh.vertices[vindex]
                    co = v.co
                    
                    vert = [co[0],co[1],co[2],v.normal[0],v.normal[1],v.normal[2],f['uv'][i][0],f['uv'][i][1]]

                    index = globalindex
                    self.vertices.append(vert)
                    globalindex+=1
                    
                    # store face information alltogether in one struct
#                    xplaneFace.vertices[i] = (vert[0],vert[1],vert[2])
#                    xplaneFace.normals[i] = (vert[3],vert[4],vert[5])
#                    xplaneFace.uvs[i] = (vert[6],vert[7])
#                    xplaneFace.indices[i] = index
                    
                    self.indices.append(index)
                    
#                faces.append(xplaneFace)

            # store the faces in the prim
#            prim.faces = faces
            prim.indices[1] = len(self.indices)
            
            #TODO: now optimize vertex-table and remove duplicates
            #index = self.getDupliVerticeIndex(vert,endIndex)
        
            
    def getDupliVerticeIndex(self,v,startIndex = 0):
        if profile:
            profiler.start('XPlaneMesh.getDupliVerticeIndex')
            
        for i in range(len(self.vertices)):
            match = True
            ii = startIndex
            while ii<len(self.vertices[i]):
                if self.vertices[i][ii] != v[ii]:
                    match = False
                    ii = len(self.vertices[i])
                ii+=1
                
            if match:
                return i

        if profile:
            profiler.end('XPlaneMesh.getDupliVerticeIndex')

        return -1

    def getUVFaces(self,mesh,uv_name):
        # get the uv_texture
        if (uv_name != None and len(mesh.uv_textures)>0):
            uv_layer = None
            if uv_name=="":
                uv_layer = mesh.uv_textures[0]
            else:
                i = 0
                while uv_layer == None and i<len(mesh.uv_textures):
                    if mesh.uv_textures[i].name == uv_name:
                        uv_layer = mesh.uv_textures[i]
                    i+=1

            if uv_layer!=None:
                return uv_layer.data
            else:
                return None
        else:
            return None

    def faceToTrianglesWithUV(self,face,uv):
        if profile:
            profiler.start('XPlaneMesh.faceToTrianglesWithUV')

        triangles = []
        #inverse uv's as we are inversing face indices later
        if len(face.vertices)==4: #quad
            if uv != None:
                triangles.append( {"uv":[[uv.uv3[0], uv.uv3[1]], [uv.uv2[0], uv.uv2[1]], [uv.uv1[0], uv.uv1[1]]], "indices":[face.vertices[0], face.vertices[1], face.vertices[2]]})
                triangles.append( {"uv":[[uv.uv1[0], uv.uv1[1]], [uv.uv4[0], uv.uv4[1]], [uv.uv3[0], uv.uv3[1]]], "indices":[face.vertices[2], face.vertices[3], face.vertices[0]]})
            else:
                triangles.append( {"uv":[[0.0, 0.0], [0.0, 0.0], [0.0, 0.0]], "indices":[face.vertices[0], face.vertices[1], face.vertices[2]]})
                triangles.append( {"uv":[[0.0, 0.0], [0.0, 0.0], [0.0, 0.0]], "indices":[face.vertices[2], face.vertices[3], face.vertices[0]]})
        else:
            if uv != None:
                triangles.append( {"uv":[[uv.uv3[0], uv.uv3[1]], [uv.uv2[0], uv.uv2[1]], [uv.uv1[0], uv.uv1[1]]], "indices":face.vertices})
            else:
                triangles.append( {"uv":[[0.0, 0.0], [0.0, 0.0], [0.0, 0.0]], "indices":face.vertices})

        if profile:
            profiler.end('XPlaneMesh.faceToTrianglesWithUV')

        return triangles

    def faceValues(self,face, mesh, matrix):
        fv = []
        for verti in face.vertices_raw:
            fv.append(matrix * mesh.vertices[verti].co)
        return fv

    def writeVertices(self):
        if profile:
            profiler.start('XPlaneMesh.writeVertices')

        o=''
        for v in self.vertices:
            # dump the vertex data
            o+="VT"
            for i in v:
                o+="\t%6.4f" % i
            o+="\n"

        if profile:
            profiler.end('XPlaneMesh.writeVertices')

        return o

    def writeIndices(self):
        if profile:
            profiler.start('XPlaneMesh.writeIndices')

        o=''
        group = []
        for i in self.indices:
            # append index to group if we havent collected 10 yet
            if len(group)<10:
                group.append(i)
            else:
                # dump 10 indices at once
                o+='IDX10'
                for ii in group:
                    o+="\t%d" % ii

                o+="\n"
                group = []
                group.append(i)
        
        # dump overhanging indices
        for i in group:
            o+="IDX\t%d\n" % i

        if profile:
            profiler.end('XPlaneMesh.writeIndices')

        return o

class XPlaneLights():
    def __init__(self,file):
        self.vertices = []
        self.indices = []

        # store the global index, as we are reindexing faces
        globalindex = 0

        for light in file['lights']:
            light.indices[0] = globalindex

            # store the world translation matrix
            matrix = light.object.matrix_world
            
            # get the vertice from original mesh
            v = light.object.location

            # convert local to global coordinates
            co = matrix * v

            self.vertices.append([-co[0],co[2],co[1],light.color[0],light.color[1],light.color[2]])
            self.indices.append(globalindex)
            globalindex+=1

            light.indices[1] = globalindex

        # reverse indices due to the inverted z axis
        self.indices.reverse()

    def writeVertices(self):
        o=''
        for v in self.vertices:
            o+='VLIGHT'
            for f in v:
                o+='\t%6.4f' % f
            o+='\n'
        
        return o

class XPlaneCommands():
    def __init__(self,file):
        self.file = file
        
        # stores attribtues that reset other attributes
        self.reseters = {}

        # stores all already written attributes
        self.written = {}

        # stores already written primitives, that have been written due to nested animations
        self.writtenPrimitives = []

    def write(self):
        o=''
         
        # write down all objects
        for prim in self.file['primitives']:
            if prim not in self.writtenPrimitives:
                o+=self.writePrimitive(prim,0)

        # write down all lights
        if len(self.file['lights'])>0:
            o+="LIGHTS\t0 %d\n" % len(self.file['lights'])
            
        return o

    def writePrimitive(self,prim,animLevel):
        if profile:
            profiler.start("XPlaneCommands.writePrimitve")
            
        o = ''
        
        animationStarted = False
        tabs = self.getAnimTabs(animLevel)

        if debug:
            o+="%s# %s\n" % (tabs,prim.name)

        if len(prim.animations)>0:
            animationStarted = True

            # begin animation block
            o+="%sANIM_begin\n" % tabs
            animLevel+=1
            tabs = self.getAnimTabs(animLevel)

            for dataref in prim.animations:
                if len(prim.animations[dataref])>1:
                    o+=self.writeKeyframes(prim,dataref,tabs)

        o+=self.writeMaterial(prim,tabs)
        o+=self.writeCustomAttributes(prim,tabs)

        # triangle rendering
        offset = prim.indices[0]
        count = prim.indices[1]-prim.indices[0]
        o+="%sTRIS\t%d %d\n" % (tabs,offset,count)

        self.writtenPrimitives.append(prim)

        if animationStarted:
            if len(prim.children)>0:
                for childPrim in prim.children:
                    if childPrim not in self.writtenPrimitives:
                        o+=self.writePrimitive(childPrim,animLevel)
            # TODO: check if primitive has an animated parent in another file, if so add a dummy anim-block around it?

            # end animation block
            o+="%sANIM_end\n" % self.getAnimTabs(animLevel-1)

        if profile:
            profiler.end("XPlaneCommands.writePrimitive")
            
        return o

    def getAnimTabs(self,level):
        tabs = ''
        for i in range(0,level):
            tabs+='\t'
        
        return tabs

    def getAnimLevel(self,prim):
        parent = prim
        level = 0
        
        while parent != None:
            parent = parent.parent
            if (parent!=None):
                level+=1
        
        return level

    def writeMaterial(self,prim,tabs):
        o = ''
        for attr in prim.material.attributes:
            if prim.material.attributes[attr]!=None:
                if(prim.material.attributes[attr]==True):
                    value = ""
                    line = '%s\n' % attr
                else:
                    value = prim.material.attributes[attr]
                    line = '%s\t%s\n' % (attr,value)

                o+=tabs+line
                # only write line if attribtue wasn't already written with same value
#                    if attr in self.written:
#                        if self.written[attr]!=value:
#                            o+=line
#                            self.written[attr] = value
#                    else:
#                        o+=line
#                        self.written[attr] = value
        return o

    def writeCustomAttributes(self,prim,tabs):
        o = ''
        for attr in prim.attributes:
            line='%s\t%s\n' % (attr,prim.attributes[attr])
            o+=tabs+line
        return o

    def writeKeyframes(self,prim,dataref,tabs):
        o = ''

        keyframes = prim.animations[dataref]

        totalTrans = [0.0,0.0,0.0]
        totalRot = [0.0,0.0,0.0]

        # TODO: staticTrans can be merged into regular translations
        staticTrans = ['','']
        staticTrans[0] = "%sANIM_trans\t%6.4f\t%6.4f\t%6.4f\t%6.4f\t%6.4f\t%6.4f\t0\t0\tnone\n" % (tabs,prim.locationLocal[0],prim.locationLocal[1],prim.locationLocal[2],prim.locationLocal[0],prim.locationLocal[1],prim.locationLocal[2])
        staticTrans[1] = "%sANIM_trans\t%6.4f\t%6.4f\t%6.4f\t%6.4f\t%6.4f\t%6.4f\t0\t0\tnone\n" % (tabs,-prim.locationLocal[0],-prim.locationLocal[1],-prim.locationLocal[2],-prim.locationLocal[0],-prim.locationLocal[1],-prim.locationLocal[2])
        
        trans = "%sANIM_trans_begin\t%s\n" % (tabs,dataref)
        rot = ['','','']
        rot[0] = "%sANIM_rotate_begin\t1.0\t0.0\t0.0\t%s\n" % (tabs,dataref)
        rot[1] = "%sANIM_rotate_begin\t0.0\t1.0\t0.0\t%s\n" % (tabs,dataref)
        rot[2] = "%sANIM_rotate_begin\t0.0\t0.0\t1.0\t%s\n" % (tabs,dataref)
        
        for keyframe in keyframes:
            totalTrans[0]+=abs(keyframe.translation[0])
            totalTrans[1]+=abs(keyframe.translation[1])
            totalTrans[2]+=abs(keyframe.translation[2])
            trans+="%s\tANIM_trans_key\t%6.4f\t%6.4f\t%6.4f\t%6.4f\n" % (tabs,keyframe.value,keyframe.translation[0],keyframe.translation[1],keyframe.translation[2])
            
            totalRot[0]+=abs(keyframe.rotation[0])
            totalRot[1]+=abs(keyframe.rotation[1])
            totalRot[2]+=abs(keyframe.rotation[2])

            for i in range(0,3):
                rot[i]+="%s\tANIM_rotate_key\t%6.4f\t%6.4f\n" % (tabs,keyframe.value,keyframe.rotation[i])

            if debug:
                debugger.debug("%s keyframe %d@%d" % (keyframe.primitive.name,keyframe.index,keyframe.frame))
#                print("location/prim.location")
#                print(keyframe.location)
#                print(keyframe.primitive.location)
#                print("locationLocal/prim.locationLocal")
#                print(keyframe.locationLocal)
#                print(keyframe.primitive.locationLocal)
#                print("")
            
        trans+="%sANIM_trans_end\n" % tabs
        rot[0]+="%sANIM_rotate_end\n" % tabs
        rot[1]+="%sANIM_rotate_end\n" % tabs
        rot[2]+="%sANIM_rotate_end\n" % tabs

        if totalTrans[0]!=0.0 or totalTrans[1]!=0.0 or totalTrans[2]!=0.0:
            o+=trans
            # add loops if any
            if prim.datarefs[dataref].loop>0:
                o+="%sANIM_keyframe_loop\t%d\n" % (tabs,prim.datarefs[dataref].loop)

        if totalRot[0]!=0.0 or totalRot[1]!=0.0 or totalRot[2]!=0.0:
            o+=staticTrans[0]
            
            if totalRot[0]!=0.0:
                o+=rot[0]
            if totalRot[1]!=0.0:
                o+=rot[1]
            if totalRot[2]!=0.0:
                o+=rot[2]

            # add loops if any
            if prim.datarefs[dataref].loop>0:
                o+="%sANIM_keyframe_loop\t%d\n" % (tabs,prim.datarefs[dataref].loop)
                
            o+=staticTrans[1]
        
        return o

class XPlaneData():
    def __init__(self):
        self.files = {}

    # Returns the corresponding xplane-Layer to a blender layer index
    def getXPlaneLayer(self,layer):
        return bpy.context.scene.xplane.layers[layer]

    # Returns the filename for a layer. If no name was given by user it will be generated.
    def getFilenameFromXPlaneLayer(self,xplaneLayer):
        if xplaneLayer.name == "":
            filename = "layer_%s" % (str(xplaneLayer.index+1).zfill(2))
        else:
            filename = xplaneLayer.name

        if xplaneLayer.cockpit:
            filename +="_cockpit"

        return filename

    # Returns indices of all active blender layers
    def getActiveLayers(self):
        layers = []
        for i in range(0,len(bpy.context.scene.layers)):
            if bpy.context.scene.layers[i]:
                layers.append(i)

        return layers

    # Returns all first level Objects of a blender layer
    def getObjectsByLayer(self,layer):
        objects = []
        for object in bpy.context.scene.objects:
            #only add top level objects that have no parents
            if (object.parent==None):
                for i in range(len(object.layers)):
                    if object.layers[i]==True and i == layer:
                        objects.append(object)

        return objects

    # Returns an empty obj-file hash
    def getEmptyFile(self,parent):
        return {'primitives':[],'lights':[],'lines':[],'parent':parent}

    # Returns exportable child objects. If those are nested within bones or something else it will look recursive for objects.
    def getChildObjects(self,parent,found = None):
        if found==None:
            found = []
        if len(parent.children)>0:
            for child in parent.children:
                if child.type in ["MESH","LAMP"]:
                    found.append(child)
                else:
                    self.getChildObjects(child,found)
        
        return found

    # collects all exportable objects from the scene
    def collect(self):
        if profile:
            profiler.start("XPlaneData.collect")
        
        for layer in self.getActiveLayers():
            xplaneLayer = self.getXPlaneLayer(layer)
            filename = self.getFilenameFromXPlaneLayer(xplaneLayer)
            self.files[filename] = self.getEmptyFile(xplaneLayer)
            self.collectObjects(self.getObjectsByLayer(layer),filename)
            self.splitFileByTexture(xplaneLayer)
                
        if profile:
            profiler.end("XPlaneData.collect")

    def collectObjects(self,objects,filename):
        for obj in objects:
            if debug:
                debugger.debug("scanning "+obj.name)
                
            if obj.hide==False:
                # look for children
                children = self.getChildObjects(obj)

                # mesh: let's create a prim out of it
                if obj.type=="MESH":
                    if debug:
                        debugger.debug("\t "+obj.name+": adding to list")
                    prim = XPlanePrimitive(obj)
                    self.files[filename]['primitives'].append(prim)

                    # if object has children add them to the prim
                    if len(children)>0:
                        self.addChildren(prim,children,filename)

                # lamp: let's create a XPlaneLight. Those cannot have children.
                elif obj.type=="LAMP":
                    if debug:
                        debugger.debug("\t "+child.name+": adding to list")
                    self.files[filename]['lights'].append(XPlaneLight(child))
                    
                # something else: lets go through the valid children and add them
                elif len(children)>0:
                    self.collectObjects(children,filename)

    def addChildren(self,prim,objects,filename):
        for obj in objects:
            if debug:
                debugger.debug("\t\t scanning "+obj.name)

            if obj.hide==False:
                if obj.type=="MESH":
                    if debug:
                        debugger.debug("\t\t "+obj.name+": adding to list")
                    childPrim = XPlanePrimitive(obj,prim)
                    prim.children.append(childPrim)
                    
                    # add prim to file
                    self.files[filename]['primitives'].append(childPrim)

                    # recursion
                    children = self.getChildObjects(obj)
                    if len(children)>0:
                        self.addChildren(childPrim,children,filename)
                        

    def splitFileByTexture(self,parent):
        name = self.getFilenameFromXPlaneLayer(parent)
        filename = None
        textures = []
        if len(self.files[name])>0:
            # stores prims that have to be removed after iteration
            remove = []
            for prim in self.files[name]['primitives']:
                if prim.material.texture!=None:
                    filename = name+'_'+prim.material.texture[0:-4]
                    
                    # create new file list if not existant
                    if filename not in self.files:
                        self.files[filename] = self.getEmptyFile(parent)

                    # store prim in the file list
                    self.files[filename]['primitives'].append(prim)
                    remove.append(prim)

            # remove prims that have been placed in other files
            for prim in remove:
                self.files[name]['primitives'].remove(prim)

            # add texture to list
            if filename:
                textures.append(filename)

            # do some house cleaning
            # if there is only one texture in use and no objects without texture, put everything in one file
            if (len(textures)==1 and len(self.files[name]['primitives'])==0):
                self.files[textures[0]]['lights'] = self.files[name]['lights']
                self.files[textures[0]]['lines'] = self.files[name]['lines']
                del self.files[name]
    

class XPlaneHeader():
    def __init__(self,file,mesh,lights,version):
        self.version = version
        self.mode = "default"
        self.attributes = OrderedDict([("TEXTURE",None),
                        ("TEXTURE_LIT",None),
                        ("TEXTURE_NORMAL",None),
                        ("POINT_COUNTS",None),
                        ("slung_load_weight",None),
                        ("COCKPIT_REGION",None)])

        # set slung load
        if file['parent'].slungLoadWeight>0:
            self.attributes['slung_load_weight'] = file['parent'].slungLoadWeight

        # set Texture
        if(len(file['primitives'])>0 and file['primitives'][0].material.texture != None):
            tex = file['primitives'][0].material.texture
            self.attributes['TEXTURE'] = tex
            self.attributes['TEXTURE_LIT'] = tex[0:-4]+'_LIT.png'
            self.attributes['TEXTURE_NORMAL'] = tex[0:-4]+'_NML.png'

        # get point counts
        tris = len(mesh.vertices)
        lines = 0
        lites = len(lights.vertices)
        indices = len(mesh.indices)
        
        self.attributes['POINT_COUNTS'] = "%d\t%d\t%d\t%d" % (tris,lines,lites,indices)

        # add custom attributes
        for attr in file['parent'].customAttributes:
            self.attributes[attr.name] = attr.value

    def write(self):
        import platform

        system = platform.system()

        # line ending types (I = UNIX/DOS, A = MacOS)
        if 'Mac OS' in system:
            o = 'A\n'
        else:
            o = 'I\n'

        # version number
        if self.version>=8:
            o+='800\n'

        o+='OBJ\n\n'

        # attributes
        for attr in self.attributes:
            if self.attributes[attr]!=None:
                o+='%s\t%s\n' % (attr,self.attributes[attr])
        
        return o
        

class ExportXPlane9(bpy.types.Operator):
    '''Export to XPlane Object file format (.obj)'''
    bl_idname = "export.xplane_obj"
    bl_label = 'Export XPlane Object'
    
    filepath = StringProperty(name="File Path", description="Filepath used for exporting the XPlane file(s)", maxlen= 1024, default= "")
    check_existing = BoolProperty(name="Check Existing", description="Check and warn on overwriting existing files", default=True, options={'HIDDEN'})

    def execute(self, context):
        if debug:
            debugger.start(log)

        if profile:
            profiler.start("ExportXPlane9")

        filepath = self.properties.filepath
        if filepath=='':
            filepath = bpy.context.blend_data.filepath

        filepath = os.path.dirname(filepath)
        #filepath = bpy.path.ensure_ext(filepath, ".obj")

        #store current frame as we will go back to it
        currentFrame = bpy.context.scene.frame_current

        # goto first frame so everything is in inital state
        bpy.context.scene.frame_set(frame=1)
        bpy.context.scene.update()

        data = XPlaneData()
        data.collect()

        # goto first frame again so everything is in inital state
        bpy.context.scene.frame_set(frame=1)
        bpy.context.scene.update()

        if len(data.files)>0:
            if debug:
                debugger.debug("Writing XPlane Object file(s) ...")
            for file in data.files:
                o=''
                if (len(data.files[file]['primitives'])>0 or len(data.files[file]['lights'])>0 or len(data.files[file]['lines'])>0):
                    mesh = XPlaneMesh(data.files[file])
                    lights = XPlaneLights(data.files[file])
                    header = XPlaneHeader(data.files[file],mesh,lights,9)
                    commands = XPlaneCommands(data.files[file])
                    o+=header.write()
                    o+="\n"
                    o+=mesh.writeVertices()
                    o+="\n"
                    o+=lights.writeVertices()
                    o+="\n"
                    o+=mesh.writeIndices()
                    o+="\n"
                    o+=commands.write()
                    
                    o+="\n# Build with Blender %s (build %s) Exported with XPlane2Blender %3.2f" % (bpy.app.version_string,bpy.app.build_revision,version/1000)

                    if profile:
                        profiler.start("ExportXPlane9 %s" % file)

                    # write the file
                    fullpath = os.path.join(filepath,file+'.obj')
                    if debug:
                        debugger.debug("Writing %s" % fullpath)
                    file = open(fullpath, "w")
                    file.write(o)
                    file.close()

                    if profile:
                        profiler.end("ExportXPlane9 %s" % file)
                else:
                    if debug:
                        debugger.debug("No objects to export, aborting ...")
        else:
            if debug:
                debugger.debug("No objects to export, aborting ...")

        # return to stored frame
        bpy.context.scene.frame_set(frame=currentFrame)
        bpy.context.scene.update()

        if profile:
            profiler.end("ExportXPlane9")
            if debug:
                debugger.debug("\nProfiling results:")
                debugger.debug(profiler.getTimes())

        if debug:
            debugger.end()

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}