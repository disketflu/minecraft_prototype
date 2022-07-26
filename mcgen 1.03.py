import harfang as hg
import random
from math import cos, sin, pi, floor, ceil
import noise
import numpy as np
from multiprocessing import Process
from harfang_gui import HarfangUI as hgui

hg.InputInit()
hg.WindowSystemInit()

res_x, res_y = 1920, 1080
win = hg.RenderInit('Harfang - Minecraft Prototype',
					res_x, res_y, hg.RF_VSync | hg.RF_MSAA4X)

# include assets before hgui init
hg.AddAssetsFolder("resources_compiled")

# Setup HarfangGUI
hgui.init(["default.ttf"], [20], res_x, res_y)

#
pipeline = hg.CreateForwardPipeline()
res = hg.PipelineResources()

# AAA pipeline
pipeline_aaa_config = hg.ForwardPipelineAAAConfig()
pipeline_aaa = hg.CreateForwardPipelineAAAFromAssets("core", pipeline_aaa_config, hg.BR_Equal, hg.BR_Equal)
pipeline_aaa_config.sample_count = 1

# vertex layout and models
vtx_layout = hg.VertexLayoutPosFloatNormUInt8()
vtx_layout_lines = hg.VertexLayoutPosFloatColorUInt8()

cube_mdl = hg.CreateCubeModel(vtx_layout, 1, 1, 1)
ground_mdl = hg.CreatePlaneModel(vtx_layout, 5, 5, 1, 1)

shader = hg.LoadProgramFromFile('resources_compiled/shaders/mdl')
pos_rgb = hg.LoadProgramFromFile('resources_compiled/shaders/pos_rgb')

# create materials
prg_ref = hg.LoadPipelineProgramRefFromFile('resources_compiled/core/shader/pbr.hps', res, hg.GetForwardPipelineInfo())

mat_cube = hg.CreateMaterial(prg_ref, 'uBaseOpacityColor', hg.Vec4I(20, 225, 26), 'uOcclusionRoughnessMetalnessColor', hg.Vec4(1, 0.5, 0.25)) # default green
mat_water = hg.CreateMaterial(prg_ref, 'uBaseOpacityColor', hg.Vec4I(20, 205, 240), 'uOcclusionRoughnessMetalnessColor', hg.Vec4(1, 0.08, 0.8)) # water = metalness
mat_sand = hg.CreateMaterial(prg_ref, 'uBaseOpacityColor', hg.Vec4I(250, 225, 6), 'uOcclusionRoughnessMetalnessColor', hg.Vec4(1, 0.658, 0.1)) # yellow sand
mat_snow = hg.CreateMaterial(prg_ref, 'uBaseOpacityColor', hg.Vec4I(220, 220, 220), 'uOcclusionRoughnessMetalnessColor', hg.Vec4(1, 0.8, 0.5)) # snow = half metalness
mat_rock = hg.CreateMaterial(prg_ref, 'uBaseOpacityColor', hg.Vec4I(128, 128, 128), 'uOcclusionRoughnessMetalnessColor', hg.Vec4(1, 0.9, 0.2)) # rough grey 

#### TERRAIN GENERATION SETTINGS ####
scale = 100
octaves = 4
persistence = 0.5
lacunarity = 1.8
#### TERRAIN GENERATION SETTINGS ####

class DictionnarySparseMatrix:
	def __init__(self):
		self.elements = {}

	def addValue(self, tuple, value):
		self.elements[tuple] = value

	def deleteValue(self, tuple):
		value = self.elements.pop(tuple, None)
		return value

	def readValue(self, tuple):
		try:
			value = self.elements[tuple]
		except KeyError:
			value = None
		return value

	def readDict(self):
		return self.elements

def buildmodel(vtx_layout, world, chunk_size, chunk_pos):
	list_mats = []
	final_list_mats = [[], [], [], [], []]
	mdl_builder = hg.ModelBuilder()
	count_empty = 0
	for x in range(int(chunk_pos.x), int(chunk_pos.x + chunk_size)):
		for y in range(int(chunk_pos.y), int(chunk_pos.y + chunk_size)):
			for z in range(int(chunk_pos.z), int(chunk_pos.z + chunk_size)):
				isworldobject = world.readValue((x, y, z))
				if isworldobject == None:
					block_data = [False, 0]
					v = noise.pnoise3(x/scale, 
										y/scale, z/scale,
										octaves=octaves, 
										persistence=persistence, 
										lacunarity=lacunarity, 
										repeatx=1024, 
										repeaty=1024,
										repeatz=1024,  
										base=seed)
					material = 3 #snow
					if v < -0.1:
						material = 2 #water
					elif v < 0.02:
						material = 1 #sand
					elif v < 0.1:
						material = 0 # grass
					elif v < 0.25:
						material = 4 # rock
					correcty = round(v * 100)
					if y == correcty or y == correcty + 1 or y == correcty - 1 or y == correcty + 2 or y == correcty - 2:
						block_data = [True, material]
					else:
						block_data = [False, 0]
						count_empty +=1
					list_mats.append([[x, y, z], block_data])

				else:
					list_mats.append([[x, y, z], isworldobject])
					
	if count_empty == (chunk_size * chunk_size * chunk_size):
		return None

	list_mats.sort(key=lambda x: x[1][1])

	for i in list_mats:
		final_list_mats[i[1][1]].append(i)

	for material in final_list_mats:
		for cube in material:
			x = cube[0][0]
			y = cube[0][1]
			z = cube[0][2]
			position = hg.Vec3(x - chunk_pos.x, y - chunk_pos.y, z - chunk_pos.z)
			should_draw = cube[1][0]

			if should_draw:
				vertex0 = hg.Vertex()
				vertex0.pos = hg.Vec3(-0.5 + position.x, -
									  0.5 + position.y, -0.5 + position.z)
				vertex0.normal = hg.Vec3(0, 0, -1)
				vertex0.uv0 = hg.Vec2(0, 0)
				a = mdl_builder.AddVertex(vertex0)
				vertex1 = hg.Vertex()
				vertex1.pos = hg.Vec3(-0.5 + position.x,
									  0.5 + position.y, -0.5 + position.z)
				vertex1.normal = hg.Vec3(0, 0, -1)
				vertex1.uv0 = hg.Vec2(0, 1)
				b = mdl_builder.AddVertex(vertex1)
				vertex2 = hg.Vertex()
				vertex2.pos = hg.Vec3(
					0.5 + position.x, 0.5 + position.y, -0.5 + position.z)
				vertex2.normal = hg.Vec3(0, 0, -1)
				vertex2.uv0 = hg.Vec2(1, 1)
				c = mdl_builder.AddVertex(vertex2)
				vertex3 = hg.Vertex()
				vertex3.pos = hg.Vec3(
					0.5 + position.x, -0.5 + position.y, -0.5 + position.z)
				vertex3.normal = hg.Vec3(0, 0, -1)
				vertex3.uv0 = hg.Vec2(1, 0)
				d = mdl_builder.AddVertex(vertex3)
				mdl_builder.AddTriangle(d, c, b)
				mdl_builder.AddTriangle(b, a, d)
				# +
				vertex0 = hg.Vertex()
				vertex0.pos = hg.Vec3(-0.5 + position.x, -
									  0.5 + position.y, 0.5 + position.z)
				vertex0.normal = hg.Vec3(0, 0, 1)
				vertex0.uv0 = hg.Vec2(0, 0)
				a = mdl_builder.AddVertex(vertex0)
				vertex1 = hg.Vertex()
				vertex1.pos = hg.Vec3(-0.5 + position.x,
									  0.5 + position.y, 0.5 + position.z)
				vertex1.normal = hg.Vec3(0, 0, 1)
				vertex1.uv0 = hg.Vec2(0, 1)
				b = mdl_builder.AddVertex(vertex1)
				vertex2 = hg.Vertex()
				vertex2.pos = hg.Vec3(
					0.5 + position.x, 0.5 + position.y, 0.5 + position.z)
				vertex2.normal = hg.Vec3(0, 0, 1)
				vertex2.uv0 = hg.Vec2(1, 1)
				c = mdl_builder.AddVertex(vertex2)
				vertex3 = hg.Vertex()
				vertex3.pos = hg.Vec3(
					0.5 + position.x, -0.5 + position.y, 0.5 + position.z)
				vertex3.normal = hg.Vec3(0, 0, 1)
				vertex3.uv0 = hg.Vec2(1, 0)
				d = mdl_builder.AddVertex(vertex3)
				mdl_builder.AddTriangle(a, b, c)
				mdl_builder.AddTriangle(a, c, d)
				# -
				vertex0 = hg.Vertex()
				vertex0.pos = hg.Vec3(-0.5 + position.x, -
									  0.5 + position.y, -0.5 + position.z)
				vertex0.normal = hg.Vec3(0, -1, 0)
				vertex0.uv0 = hg.Vec2(0, 0)
				a = mdl_builder.AddVertex(vertex0)
				vertex1 = hg.Vertex()
				vertex1.pos = hg.Vec3(-0.5 + position.x, -
									  0.5 + position.y, 0.5 + position.z)
				vertex1.normal = hg.Vec3(0, -1, 0)
				vertex1.uv0 = hg.Vec2(0, 1)
				b = mdl_builder.AddVertex(vertex1)
				vertex2 = hg.Vertex()
				vertex2.pos = hg.Vec3(
					0.5 + position.x, -0.5 + position.y, 0.5 + position.z)
				vertex2.normal = hg.Vec3(0, -1, 0)
				vertex2.uv0 = hg.Vec2(1, 1)
				c = mdl_builder.AddVertex(vertex2)
				vertex3 = hg.Vertex()
				vertex3.pos = hg.Vec3(
					0.5 + position.x, -0.5 + position.y, -0.5 + position.z)
				vertex3.normal = hg.Vec3(0, -1, 0)
				vertex3.uv0 = hg.Vec2(1, 0)
				d = mdl_builder.AddVertex(vertex3)
				mdl_builder.AddTriangle(a, b, c)
				mdl_builder.AddTriangle(a, c, d)
				# +
				vertex0 = hg.Vertex()
				vertex0.pos = hg.Vec3(-0.5 + position.x,
									  0.5 + position.y, -0.5 + position.z)
				vertex0.normal = hg.Vec3(0, 1, 0)
				vertex0.uv0 = hg.Vec2(0, 0)
				a = mdl_builder.AddVertex(vertex0)
				vertex1 = hg.Vertex()
				vertex1.pos = hg.Vec3(-0.5 + position.x,
									  0.5 + position.y, 0.5 + position.z)
				vertex1.normal = hg.Vec3(0, 1, 0)
				vertex1.uv0 = hg.Vec2(0, 1)
				b = mdl_builder.AddVertex(vertex1)
				vertex2 = hg.Vertex()
				vertex2.pos = hg.Vec3(
					0.5 + position.x, 0.5 + position.y, 0.5 + position.z)
				vertex2.normal = hg.Vec3(0, 1, 0)
				vertex2.uv0 = hg.Vec2(1, 1)
				c = mdl_builder.AddVertex(vertex2)
				vertex3 = hg.Vertex()
				vertex3.pos = hg.Vec3(
					0.5 + position.x, 0.5 + position.y, -0.5 + position.z)
				vertex3.normal = hg.Vec3(0, 1, 0)
				vertex3.uv0 = hg.Vec2(1, 0)
				d = mdl_builder.AddVertex(vertex3)
				mdl_builder.AddTriangle(d, c, b)
				mdl_builder.AddTriangle(b, a, d)
				# -
				vertex0 = hg.Vertex()
				vertex0.pos = hg.Vec3(-0.5 + position.x, -
									  0.5 + position.y, -0.5 + position.z)
				vertex0.normal = hg.Vec3(-1, 0, 0)
				vertex0.uv0 = hg.Vec2(0, 0)
				a = mdl_builder.AddVertex(vertex0)
				vertex1 = hg.Vertex()
				vertex1.pos = hg.Vec3(-0.5 + position.x, -
									  0.5 + position.y, 0.5 + position.z)
				vertex1.normal = hg.Vec3(-1, 0, 0)
				vertex1.uv0 = hg.Vec2(0, 1)
				b = mdl_builder.AddVertex(vertex1)
				vertex2 = hg.Vertex()
				vertex2.pos = hg.Vec3(-0.5 + position.x,
									  0.5 + position.y, 0.5 + position.z)
				vertex2.normal = hg.Vec3(-1, 0, 0)
				vertex2.uv0 = hg.Vec2(1, 1)
				c = mdl_builder.AddVertex(vertex2)
				vertex3 = hg.Vertex()
				vertex3.pos = hg.Vec3(-0.5 + position.x,
									  0.5 + position.y, -0.5 + position.z)
				vertex3.normal = hg.Vec3(-1, 0, 0)
				vertex3.uv0 = hg.Vec2(1, 0)
				d = mdl_builder.AddVertex(vertex3)
				mdl_builder.AddTriangle(d, c, b)
				mdl_builder.AddTriangle(b, a, d)
				# +
				vertex0 = hg.Vertex()
				vertex0.pos = hg.Vec3(
					0.5 + position.x, -0.5 + position.y, -0.5 + position.z)
				vertex0.normal = hg.Vec3(1, 0, 0)
				vertex0.uv0 = hg.Vec2(0, 0)
				a = mdl_builder.AddVertex(vertex0)
				vertex1 = hg.Vertex()
				vertex1.pos = hg.Vec3(
					0.5 + position.x, -0.5 + position.y, 0.5 + position.z)
				vertex1.normal = hg.Vec3(1, 0, 0)
				vertex1.uv0 = hg.Vec2(0, 1)
				b = mdl_builder.AddVertex(vertex1)
				vertex2 = hg.Vertex()
				vertex2.pos = hg.Vec3(
					0.5 + position.x, 0.5 + position.y, 0.5 + position.z)
				vertex2.normal = hg.Vec3(1, 0, 0)
				vertex2.uv0 = hg.Vec2(1, 1)
				c = mdl_builder.AddVertex(vertex2)
				vertex3 = hg.Vertex()
				vertex3.pos = hg.Vec3(
					0.5 + position.x, 0.5 + position.y, -0.5 + position.z)
				vertex3.normal = hg.Vec3(1, 0, 0)
				vertex3.uv0 = hg.Vec2(1, 0)
				d = mdl_builder.AddVertex(vertex3)
				mdl_builder.AddTriangle(a, b, c)
				mdl_builder.AddTriangle(a, c, d)
		mdl_builder.EndList(cube[1][1])

	mdl = mdl_builder.MakeModel(vtx_layout)
	return mdl

def findchunkfromcoordinates(x, y, z, chunks, chunk_size, chunk_amount):
	appropriatechunk = None
	chunk_x = x
	chunk_y = y
	chunk_z = z

	rounded_x = round(x/chunk_size)*chunk_size
	if rounded_x - x > 0:
		chunk_x = rounded_x - chunk_size
	elif rounded_x - x < 0:
		chunk_x = rounded_x

	rounded_y = round(y/chunk_size)*chunk_size
	if rounded_y - y > 0:
		chunk_y = rounded_y - chunk_size
	elif rounded_y - y < 0:
		chunk_y = rounded_y

	rounded_z = round(z/chunk_size)*chunk_size
	if rounded_z - z > 0:
		chunk_z = rounded_z - chunk_size
	elif rounded_z - z < 0:
		chunk_z = rounded_z

	appropriatechunk = chunks.readValue((int(chunk_x / chunk_size), int(chunk_y / chunk_size), int(chunk_z / chunk_size)))

	return appropriatechunk

def deleteblock(world, vtx_layout, chunks, chunk_amount, chunk_size, x, y, z):
	chunktoreload = findchunkfromcoordinates(x, y, z, chunks, chunk_size, chunk_amount)

	if chunktoreload != None:
		world.addValue((x, y, z), [False, 0])
		mdl = buildmodel(vtx_layout, world, chunk_size, chunktoreload[2])
		if mdl is not None:
			mdl_ref = chunktoreload[3].GetObject().GetModelRef()
			res.DestroyModel(mdl_ref)
			mdl_ref = res.AddModel(str(random.uniform(0, 5000)), mdl)
			chunktoreload[3].GetObject().SetModelRef(mdl_ref)
			chunktoreload[1] = mdl


def addblock(world, vtx_layout, chunks, chunk_amount, chunk_size, x, y, z, blockvalue):
	chunktoreload = findchunkfromcoordinates(x, y, z, chunks, chunk_size, chunk_amount)

	if chunktoreload != None:
		if world.readValue((x, y, z)) == None:
			world.addValue((x, y, z), [True, blockvalue])
			mdl = buildmodel(vtx_layout, world, chunk_size, chunktoreload[2])
			if mdl is not None:
				mdl_ref = chunktoreload[3].GetObject().GetModelRef()
				res.DestroyModel(mdl_ref)
				mdl_ref = res.AddModel(str(random.uniform(0, 5000)), mdl)
				chunktoreload[3].GetObject().SetModelRef(mdl_ref)
				chunktoreload[1] = mdl

	elif world.readValue((x, y, z)) == None:
		world.addValue((x, y, z), [True, blockvalue])
		chunk_x = x
		chunk_y = y
		chunk_z = z

		rounded_x = round(x/chunk_size)*chunk_size
		if rounded_x - x > 0:
			chunk_x = rounded_x - chunk_size
		elif rounded_x - x < 0:
			chunk_x = rounded_x

		rounded_y = round(y/chunk_size)*chunk_size
		if rounded_y - y > 0:
			chunk_y = rounded_y - chunk_size
		elif rounded_y - y < 0:
			chunk_y = rounded_y

		rounded_z = round(z/chunk_size)*chunk_size
		if rounded_z - z > 0:
			chunk_z = rounded_z - chunk_size
		elif rounded_z - z < 0:
			chunk_z = rounded_z
		mdl = buildmodel(vtx_layout, modified_blocks, chunk_size, hg.Vec3(chunk_x, chunk_y, chunk_z))
		if mdl is not None:
			mdl_ref = res.AddModel(str(random.uniform(0, 5000)), mdl)
			chunk_node = hg.CreateObject(scene, hg.TranslationMat4(hg.Vec3(chunk_x, chunk_y, chunk_z)), mdl_ref, [mat_cube, mat_sand, mat_water, mat_snow, mat_rock])
			chunks.addValue((chunk_x / chunk_size, chunk_y / chunk_size, chunk_z / chunk_size), [random.uniform(0, 5000), mdl, hg.Vec3(chunk_x, chunk_y, chunk_z), chunk_node])
	
def generatechunks(chunk_amount):
	chunks = DictionnarySparseMatrix()
	queue = []
	for curchunk_x in range(-chunk_amount, chunk_amount):
		for curchunk_y in range(-5, 5):
			for curchunk_z in range(-chunk_amount, chunk_amount):
				queue.append([curchunk_x, curchunk_y, curchunk_z])

	return chunks, queue

def loadchunksaroundplayer(cam_pos, chunks, chunk_size, queue):
	toqueue = []
	for x in range(3):
		for y in range(3):
			for z in range(3):
				chunk_x_positive = cam_pos.x + (chunk_size * (x))
				chunk_y_positive = cam_pos.y + (chunk_size * (y))
				chunk_z_positive = cam_pos.z + (chunk_size * (z))

				chunk_x_negative = cam_pos.x - (chunk_size * (x))
				chunk_y_negative = cam_pos.y - (chunk_size * (y))
				chunk_z_negative = cam_pos.z - (chunk_size * (z))

				chunk_x = chunk_x_positive
				chunk_y = chunk_y_positive
				chunk_z = chunk_z_positive
				rounded_x = round(chunk_x/chunk_size)*chunk_size
				if rounded_x - x > 0:
					chunk_x = rounded_x - chunk_size
				elif rounded_x - x < 0:
					chunk_x = rounded_x
		
				rounded_y = round(chunk_y/chunk_size)*chunk_size
				if rounded_y - y > 0:
					chunk_y = rounded_y - chunk_size
				elif rounded_y - y < 0:
					chunk_y = rounded_y
		
				rounded_z = round(chunk_z/chunk_size)*chunk_size
				if rounded_z - z > 0:
					chunk_z = rounded_z - chunk_size
				elif rounded_z - z < 0:
					chunk_z = rounded_z

				if chunks.readValue((int(chunk_x / chunk_size), int(chunk_y / chunk_size), int(chunk_z / chunk_size))) == None and not [int(chunk_x / chunk_size), int(chunk_y / chunk_size), int(chunk_z / chunk_size)] in queue:
					toqueue.append([int(chunk_x / chunk_size), int(chunk_y / chunk_size), int(chunk_z / chunk_size)])

				#### NEGATIVE PART

				chunk_x = chunk_x_negative
				chunk_y = chunk_y_negative
				chunk_z = chunk_z_negative
		
				rounded_x = round(chunk_x/chunk_size)*chunk_size
				if rounded_x - x > 0:
					chunk_x = rounded_x - chunk_size
				elif rounded_x - x < 0:
					chunk_x = rounded_x
		
				rounded_y = round(chunk_y/chunk_size)*chunk_size
				if rounded_y - y > 0:
					chunk_y = rounded_y - chunk_size
				elif rounded_y - y < 0:
					chunk_y = rounded_y
		
				rounded_z = round(chunk_z/chunk_size)*chunk_size
				if rounded_z - z > 0:
					chunk_z = rounded_z - chunk_size
				elif rounded_z - z < 0:
					chunk_z = rounded_z

				if chunks.readValue((int(chunk_x / chunk_size), int(chunk_y / chunk_size), int(chunk_z / chunk_size))) is None and not [int(chunk_x / chunk_size), int(chunk_y / chunk_size), int(chunk_z / chunk_size)] in queue:
					toqueue.append([int(chunk_x / chunk_size), int(chunk_y / chunk_size), int(chunk_z / chunk_size)])

	return toqueue

def disttochunk(chunk):
	dist_to_cam = 500
	try:
		x = chunk[0] * chunk_size
		y = chunk[1] * chunk_size
		z = chunk[2] * chunk_size
		dist_to_cam = hg.Dist(hg.Vec3(x, y, z), cam_pos)
	except:
		return 500
	return dist_to_cam

def loadchunksinfinite(cam_pos, chunks, chunk_size, queue, x, y, z):
	toqueue = []

	chunk_x = cam_pos.x + (chunk_size * (x))
	chunk_y = cam_pos.y + (chunk_size * (y))
	chunk_z = cam_pos.z + (chunk_size * (z))

	rounded_x = round(chunk_x/chunk_size)*chunk_size
	if rounded_x - x > 0:
		chunk_x = rounded_x - chunk_size
	elif rounded_x - x < 0:
		chunk_x = rounded_x
	rounded_y = round(chunk_y/chunk_size)*chunk_size
	if rounded_y - y > 0:
		chunk_y = rounded_y - chunk_size
	elif rounded_y - y < 0:
		chunk_y = rounded_y
	rounded_z = round(chunk_z/chunk_size)*chunk_size
	if rounded_z - z > 0:
		chunk_z = rounded_z - chunk_size
	elif rounded_z - z < 0:
		chunk_z = rounded_z
	if chunks.readValue((int(chunk_x / chunk_size), int(chunk_y / chunk_size), int(chunk_z / chunk_size))) == None and not [int(chunk_x / chunk_size), int(chunk_y / chunk_size), int(chunk_z / chunk_size)] in queue:
		toqueue.append([int(chunk_x / chunk_size), int(chunk_y / chunk_size), int(chunk_z / chunk_size)])

	return toqueue

def show_preview_block(cam, vtx_layout_lines, vid_scene_opaque, pos_rgb):
	raylist = []

	rayp0 = cam.GetTransform().GetPos()
	rayp1 = rayp0 + hg.GetZ(cam.GetTransform().GetWorld()) * 3
	vtx = hg.Vertices(vtx_layout_lines, 4)

	floored_x = round(rayp1.x) - 0.5
	floored_y = round(rayp1.y) - 0.5
	floored_z = round(rayp1.z) - 0.5
	ceiled_x = floored_x + 1
	ceiled_y = floored_y + 1
	ceiled_z = floored_z + 1

	corner_0 = hg.Vec3(ceiled_x, floored_y, ceiled_z)
	corner_1 = hg.Vec3(floored_x, floored_y, ceiled_z)
	corner_2 = hg.Vec3(floored_x, floored_y, floored_z)
	corner_3 = hg.Vec3(ceiled_x, floored_y, floored_z)
	corner_4 = hg.Vec3(ceiled_x, ceiled_y, ceiled_z)
	corner_5 = hg.Vec3(floored_x, ceiled_y, ceiled_z)
	corner_6 = hg.Vec3(floored_x, ceiled_y, floored_z)
	corner_7 = hg.Vec3(ceiled_x, ceiled_y, floored_z)
	raylist.append([corner_0, corner_1])
	raylist.append([corner_1, corner_2])
	raylist.append([corner_2, corner_3])
	raylist.append([corner_3, corner_0])
	raylist.append([corner_4, corner_5])
	raylist.append([corner_5, corner_6])
	raylist.append([corner_6, corner_7])
	raylist.append([corner_7, corner_4])
	raylist.append([corner_0, corner_4])
	raylist.append([corner_1, corner_5])
	raylist.append([corner_2, corner_6])
	raylist.append([corner_3, corner_7])

	for ray in raylist:
		vtx = hg.Vertices(vtx_layout_lines, 2)
		vtx.Begin(0).SetPos(ray[0]).SetColor0(hg.Color.Green).End()
		vtx.Begin(1).SetPos(ray[1]).SetColor0(hg.Color.Green).End()
		hg.DrawLines(vid_scene_opaque, vtx, pos_rgb)

def chunksThread():
	global chunk_index, cam_pos, prvs_cam_pos
	if chunk_index < len(queue):
		chunk_diff = len(queue) - chunk_index
		if chunk_diff > 4 and prvs_cam_pos == cam_pos: # if player is not moving and more than 4 chunks are in queue, it will generate all 4 of them in a single frame since the game doesn't really seem to "freeze" when idle
			for i in range(4):
				try:
					mdl = buildmodel(vtx_layout, modified_blocks, chunk_size, hg.Vec3(queue[chunk_index][0] * chunk_size, queue[chunk_index][1] * chunk_size, queue[chunk_index][2] * chunk_size))
					if mdl is not None:
						mdl_ref = res.AddModel(str(chunk_index), mdl)
						chunk_node = hg.CreateObject(scene, hg.TranslationMat4(hg.Vec3(queue[chunk_index][0] * chunk_size, queue[chunk_index][1] * chunk_size, queue[chunk_index][2] * chunk_size)), mdl_ref, [mat_cube, mat_sand, mat_water, mat_snow, mat_rock])
						chunks.addValue((queue[chunk_index][0], queue[chunk_index][1], queue[chunk_index][2]), [chunk_index, mdl, hg.Vec3(queue[chunk_index][0] * chunk_size, queue[chunk_index][1] * chunk_size, queue[chunk_index][2] * chunk_size), chunk_node])
						queue[chunk_index] = []

				except Exception as e:
					print(e)

				chunk_index += 1
		else: # player is moving so we don't want to have lags or freezes so we only generate one
			try:
				mdl = buildmodel(vtx_layout, modified_blocks, chunk_size, hg.Vec3(queue[chunk_index][0] * chunk_size, queue[chunk_index][1] * chunk_size, queue[chunk_index][2] * chunk_size))
				if mdl is not None:
					mdl_ref = res.AddModel(str(chunk_index), mdl)
					chunk_node = hg.CreateObject(scene, hg.TranslationMat4(hg.Vec3(queue[chunk_index][0] * chunk_size, queue[chunk_index][1] * chunk_size, queue[chunk_index][2] * chunk_size)), mdl_ref, [mat_cube, mat_sand, mat_water, mat_snow, mat_rock])
					chunks.addValue((queue[chunk_index][0], queue[chunk_index][1], queue[chunk_index][2]), [chunk_index, mdl, hg.Vec3(queue[chunk_index][0] * chunk_size, queue[chunk_index][1] * chunk_size, queue[chunk_index][2] * chunk_size), chunk_node])
					queue[chunk_index] = []

			except Exception as e:
				print(e)

			chunk_index += 1
	else:
		deleted_chunks = []
		for chunk in chunks.readDict():
			if chunks.readValue(chunk)[3].IsValid() and chunks.readValue(chunk)[3].HasTransform():
				dist_to_cam = hg.Dist(hg.GetT(chunks.readValue(chunk)[3].GetTransform().GetWorld()), cam_pos)
				if dist_to_cam > 200:
					chunks.readValue(chunk)[3].RemoveObject()
					chunks.readValue(chunk)[3].DestroyInstance()
					deleted_chunks.append(chunk)

		for chunk in deleted_chunks:
			chunks.deleteValue(chunk)

def movingChunksQueue():
	global queue, prvs_cam_pos, cam_pos, chunks, chunk_size, added_chunks, added_queue_index, added_queue
	a = loadchunksaroundplayer(cam_pos, chunks, chunk_size, queue)
	for i in a:
		queue.append(i)
	prvs_cam_pos = hg.Vec3(cam_pos.x, cam_pos.y, cam_pos.z)
	added_chunks = False
	added_queue_index = 0
	added_queue.clear()

def idleChunksQueue():
	global queue, prvs_cam_pos, cam_pos, chunks, chunk_size, added_chunks, added_queue_index, added_queue
	diff = len(added_queue) - added_queue_index
	if diff > 4:
		for i in range(4):
			x = added_queue[added_queue_index][0]
			y = added_queue[added_queue_index][1]
			z = added_queue[added_queue_index][2]
			a = loadchunksinfinite(cam_pos, chunks, chunk_size, queue, x, y, z)
			for i in a:
				queue.append(i)
			added_queue_index += 1
	else:
		x = added_queue[added_queue_index][0]
		y = added_queue[added_queue_index][1]
		z = added_queue[added_queue_index][2]
		a = loadchunksinfinite(cam_pos, chunks, chunk_size, queue, x, y, z)
		for i in a:
			queue.append(i)
		added_queue_index += 1

chunk_size = 10
chunk_amount = 2
seed = random.randint(0,100)
chunks, queue = generatechunks(chunk_amount)
modified_blocks = DictionnarySparseMatrix()
current_block = 3

# setup scene
scene = hg.Scene()
hg.LoadSceneFromAssets("probescn/probe.scn", scene, res, hg.GetForwardPipelineInfo())
scene.canvas.color = hg.ColorI(200, 210, 208)
scene.environment.ambient = hg.Color.Black

cam = hg.CreateCamera(scene, hg.Mat4.Identity, 0.05, 1000)
scene.SetCurrentCamera(cam)

# lgt = hg.CreateLinearLight(scene, hg.TransformationMat4(hg.Vec3(0, 0, 0), hg.Deg3(19, 59, 0)), hg.Color(
# 	1, 1, 1, 1), hg.Color(1, 1, 1, 1), 10, hg.LST_Map, 0.002, hg.Vec4(8, 20, 40, 120))
# back_lgt = hg.CreatePointLight(scene, hg.TranslationMat4(hg.Vec3(
# 	30, 200, 25)), 0, hg.Color(1, 1, 1, 1), hg.Color(1, 1, 1, 1), 0)

# input devices and fps controller states
keyboard = hg.Keyboard()
mouse = hg.Mouse()

cam_pos = hg.Vec3(0, 10, 0)
cam_rot = hg.Vec3(0, 0, 0)
prvs_cam_pos = hg.Vec3(0, 10, 0)
added_chunks = True
added_queue = []
added_queue_index = 0
chunk_index = 0

# main loop
frame = 0
chunkp = Process(target=chunksThread)
movingchunkp = Process(target=movingChunksQueue)
idlechunkp = Process(target=idleChunksQueue)


while not hg.ReadKeyboard().Key(hg.K_Escape):
	keyboard.Update()
	mouse.Update()
	dt = hg.TickClock()
	hg.FpsController(keyboard, mouse, cam_pos, cam_rot,
					 20 if keyboard.Down(hg.K_LShift) else 8, dt)
	cam.GetTransform().SetPos(cam_pos)
	cam.GetTransform().SetRot(cam_rot)
	scene.Update(dt)

	chunkp.run() # run chunk process

	if prvs_cam_pos != cam_pos: 
		movingchunkp.run()

	elif not added_chunks:
		for x in range(-15, 15):
			for y in range(-15, 15):
				for z in range(-15, 15):
					added_queue.append([x, y, z])
		added_queue.sort(key=disttochunk)
		added_chunks = True

	if added_queue_index < len(added_queue):
		idlechunkp.run()
		
	if keyboard.Pressed(hg.K_Space):
		rayp0 = cam.GetTransform().GetPos()
		rayp1 = rayp0 + hg.GetZ(cam.GetTransform().GetWorld()) * 3
		deleteblock(modified_blocks, vtx_layout, chunks, chunk_amount, chunk_size, round(rayp1.x), round(rayp1.y), round(rayp1.z))

	if mouse.Pressed(hg.MB_1):
		rayp0 = cam.GetTransform().GetPos()
		rayp1 = rayp0 + hg.GetZ(cam.GetTransform().GetWorld()) * 3
		addblock(modified_blocks, vtx_layout, chunks, chunk_amount, chunk_size, round(rayp1.x), round(rayp1.y), round(rayp1.z), current_block)

	if keyboard.Pressed(hg.K_1):
		current_block = 0
	if keyboard.Pressed(hg.K_2):
		current_block = 1
	if keyboard.Pressed(hg.K_3):
		current_block = 2
	if keyboard.Pressed(hg.K_4):
		current_block = 3
	if keyboard.Pressed(hg.K_5):
		current_block = 4

	vid, pass_ids = hg.SubmitSceneToPipeline(0, scene, hg.IntRect(0, 0, res_x, res_y), True, pipeline, res, pipeline_aaa, pipeline_aaa_config, frame)
	# vid, pass_ids = hg.SubmitSceneToPipeline(0, scene, hg.IntRect(0, 0, res_x, res_y), True, pipeline, res) # without AAA

	vid_scene_opaque = hg.GetSceneForwardPipelinePassViewId(pass_ids, hg.SFPP_Opaque)

	show_preview_block(cam, vtx_layout_lines, vid_scene_opaque, pos_rgb)
	
	if hgui.begin_frame(dt, mouse, keyboard, res_x, res_y):
		
		if hgui.begin_window_2D("my_window",  hg.Vec2(res_x / 2 - 250, res_y - 150), hg.Vec2(460, 120), 1 ):

			_, current_block = hgui.radio_image_button("rib_0","block_images/grass.png", current_block, 0, hg.Vec2(80, 80))
			hgui.same_line()
			_, current_block = hgui.radio_image_button("rib_1","block_images/sand.png", current_block, 1)
			hgui.same_line()
			_, current_block = hgui.radio_image_button("rib_2","block_images/water.png", current_block, 2)
			hgui.same_line()
			_, current_block = hgui.radio_image_button("rib_3","block_images/snow.png", current_block, 3)
			hgui.same_line()
			_, current_block = hgui.radio_image_button("rib_4","block_images/stone.png", current_block, 4)

			hgui.end_window()

		hgui.end_frame(vid)


	hg.Touch(0)
	frame = hg.Frame()
	hg.UpdateWindow(win)

hg.RenderShutdown()
