from typing import Dict
from playercontroller import handlePlayerMovement
from distutils.command.build import build
import harfang as hg
import random
from math import cos, sin, pi, floor, ceil
import noise
import numpy as np

hg.InputInit()
hg.WindowSystemInit()

res_x, res_y = 1280, 720
win = hg.RenderInit('Harfang - Minecraft Prototype',
					res_x, res_y, hg.RF_VSync | hg.RF_MSAA4X)

#
pipeline = hg.CreateForwardPipeline()
res = hg.PipelineResources()
hg.AddAssetsFolder("resources_compiled")

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

mat_cube = hg.CreateMaterial(prg_ref, 'uBaseOpacityColor', hg.Vec4I(20, 225, 26), 'uOcclusionRoughnessMetalnessColor', hg.Vec4(1, 0.658, 1))
mat_water = hg.CreateMaterial(prg_ref, 'uBaseOpacityColor', hg.Vec4I(20, 205, 240), 'uOcclusionRoughnessMetalnessColor', hg.Vec4(1, 0.08, 0.08))
mat_sand = hg.CreateMaterial(prg_ref, 'uBaseOpacityColor', hg.Vec4I(250, 225, 6), 'uOcclusionRoughnessMetalnessColor', hg.Vec4(1, 0.658, 1))



#### TERRAIN GENERATION SETTINGS ####
shape = (50,50)
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
			# could also be 0.0 if using floats...
			value = None
		return value


def buildmodel(vtx_layout, world, chunk_size, chunk_pos):
	list_mats = []
	final_list_mats = [[], [], []]
	mdl_builder = hg.ModelBuilder()
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
                	                    base=40)
					material = 0
					if v < -0.1:
						material = 2 #water
					elif v < 0.02:
						material = 1 #sand
					# if v < 0 : 
					# 	v = -v
					correcty = round(v * 100)
					if y == correcty or y == correcty + 1 or y == correcty - 1:
						block_data = [True, material]
					# elif y == 0:
					# 	cubes_positions[x][y][z] = [True, 2]
					else:
						block_data = [False, 0]
					list_mats.append([[x, y, z], block_data])
				else:
					list_mats.append([[x, y, z], isworldobject])
	
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

			# should_draw_xpositive = False
			# should_draw_xnegative = False
			# if x > 0 and x < len(cubes_positions) - 1:
			# 	should_draw_xpositive = cubes_positions[x + 1][y][z][0]
			# 	should_draw_xnegative = cubes_positions[x - 1][y][z][0]
			# should_draw_ypositive = False
			# should_draw_ynegative = False
			# if y > 0 and y < len(cubes_positions) - 1:
			# 	should_draw_ypositive = cubes_positions[x][y + 1][z][0]
			# 	should_draw_ynegative = cubes_positions[x][y - 1][z][0]
			# should_draw_zpositive = False
			# should_draw_znegative = False
			# if z > 0 and z < len(cubes_positions) - 1:
			# 	should_draw_zpositive = cubes_positions[x][y][z + 1][0]
			# 	should_draw_znegative = cubes_positions[x][y][z - 1][0]
			# is_covered_block = False
			# if should_draw_xpositive and should_draw_xnegative and should_draw_ypositive and should_draw_ynegative and should_draw_zpositive and should_draw_znegative:
			# 	is_covered_block = True

			if should_draw:			# and not is_covered_block:
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
	# start sanity checks
	if x < -(chunk_size * chunk_amount) or y < -(chunk_size * chunk_amount) or z < -(chunk_size * chunk_amount):
		return None

	if x > chunk_size * chunk_amount - 1 or y > chunk_size * chunk_amount - 1 or z > chunk_size * chunk_amount - 1:
		return None
	# end sanity checks
		
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
	try:
		if chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][2] == hg.Vec3(chunk_x, chunk_y, chunk_z):
			appropriatechunk = chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)]
	except:
		print("Couldn't find chunk")

	if appropriatechunk == None:
		print("debug chunk finder :")
		print(x, y, z, "x y z")
		print(chunk_x, chunk_y, chunk_z, " chunk x y z")
		print(rounded_x, rounded_y, rounded_z, " rounded x y z \n")

	return appropriatechunk

def reloadsidechunks(vtx_layout, chunks, chunk_amount, chunk_size, x, y, z):
	chunktoreload0 = findchunkfromcoordinates(x, y + chunk_size, z, chunks, chunk_size, chunk_amount)
	chunktoreload1 = findchunkfromcoordinates(x, y - chunk_size, z, chunks, chunk_size, chunk_amount)
	chunktoreload2 = findchunkfromcoordinates(x + chunk_size, y, z, chunks, chunk_size, chunk_amount)
	chunktoreload3 = findchunkfromcoordinates(x - chunk_size, y , z, chunks, chunk_size, chunk_amount)
	chunktoreload4 = findchunkfromcoordinates(x, y, z + chunk_size, chunks, chunk_size, chunk_amount)
	chunktoreload5 = findchunkfromcoordinates(x, y, z - chunk_size, chunks, chunk_size, chunk_amount)

	if chunktoreload0 != None:
		mdl = buildmodel(vtx_layout, world, chunk_size, chunktoreload0[2])
		chunk_x = chunktoreload0[2].x
		chunk_y = chunktoreload0[2].y
		chunk_z = chunktoreload0[2].z
		mdl_ref = chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][3].GetObject().GetModelRef()
		res.DestroyModel(mdl_ref)
		mdl_ref = res.AddModel(str(random.uniform(0, 5000)), mdl)
		chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][3].GetObject().SetModelRef(mdl_ref)
		chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][1] = mdl

	if chunktoreload1 != None:
		mdl = buildmodel(vtx_layout, world, chunk_size, chunktoreload1[2])
		chunk_x = chunktoreload1[2].x
		chunk_y = chunktoreload1[2].y
		chunk_z = chunktoreload1[2].z
		mdl_ref = chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][3].GetObject().GetModelRef()
		res.DestroyModel(mdl_ref)
		mdl_ref = res.AddModel(str(random.uniform(0, 5000)), mdl)
		chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][3].GetObject().SetModelRef(mdl_ref)
		chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][1] = mdl

	if chunktoreload2 != None:
		mdl = buildmodel(vtx_layout, world, chunk_size, chunktoreload2[2])
		chunk_x = chunktoreload2[2].x
		chunk_y = chunktoreload2[2].y
		chunk_z = chunktoreload2[2].z
		mdl_ref = chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][3].GetObject().GetModelRef()
		res.DestroyModel(mdl_ref)
		mdl_ref = res.AddModel(str(random.uniform(0, 5000)), mdl)
		chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][3].GetObject().SetModelRef(mdl_ref)
		chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][1] = mdl

	if chunktoreload3 != None:
		mdl = buildmodel(vtx_layout, world, chunk_size, chunktoreload3[2])
		chunk_x = chunktoreload3[2].x
		chunk_y = chunktoreload3[2].y
		chunk_z = chunktoreload3[2].z
		mdl_ref = chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][3].GetObject().GetModelRef()
		res.DestroyModel(mdl_ref)
		mdl_ref = res.AddModel(str(random.uniform(0, 5000)), mdl)
		chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][3].GetObject().SetModelRef(mdl_ref)
		chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][1] = mdl

	if chunktoreload4 != None:
		mdl = buildmodel(vtx_layout, world, chunk_size, chunktoreload4[2])
		chunk_x = chunktoreload4[2].x
		chunk_y = chunktoreload4[2].y
		chunk_z = chunktoreload4[2].z
		mdl_ref = chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][3].GetObject().GetModelRef()
		res.DestroyModel(mdl_ref)
		mdl_ref = res.AddModel(str(random.uniform(0, 5000)), mdl)
		chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][3].GetObject().SetModelRef(mdl_ref)
		chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][1] = mdl

	if chunktoreload5 != None:
		mdl = buildmodel(vtx_layout, world, chunk_size, chunktoreload5[2])
		chunk_x = chunktoreload5[2].x
		chunk_y = chunktoreload5[2].y
		chunk_z = chunktoreload5[2].z
		mdl_ref = chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][3].GetObject().GetModelRef()
		res.DestroyModel(mdl_ref)
		mdl_ref = res.AddModel(str(random.uniform(0, 5000)), mdl)
		chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][3].GetObject().SetModelRef(mdl_ref)
		chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][1] = mdl

def deleteblock(world, vtx_layout, chunks, chunk_amount, chunk_size, x, y, z):
	chunktoreload = findchunkfromcoordinates(x, y, z, chunks, chunk_size, chunk_amount)

	if chunktoreload != None:
		# world[x][y][z][0] = False
		world.addValue((x, y, z), [False, 0])
		mdl = buildmodel(vtx_layout, world, chunk_size, chunktoreload[2])
		chunk_x = chunktoreload[2].x
		chunk_y = chunktoreload[2].y
		chunk_z = chunktoreload[2].z
		mdl_ref = chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][3].GetObject().GetModelRef()
		res.DestroyModel(mdl_ref)
		mdl_ref = res.AddModel(str(random.uniform(0, 5000)), mdl)
		chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][3].GetObject().SetModelRef(mdl_ref)
		chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][1] = mdl
		# reloadsidechunks(world, vtx_layout, chunks, chunk_amount, chunk_size, x, y, z)


def addblock(world, vtx_layout, chunks, chunk_amount, chunk_size, x, y, z):
	chunktoreload = findchunkfromcoordinates(x, y, z, chunks, chunk_size, chunk_amount)

	if chunktoreload != None:
		# world[x][y][z][0] = True
		world.addValue((x, y, z), [True, 0])
		mdl = buildmodel(vtx_layout, world, chunk_size, chunktoreload[2])
		chunk_x = chunktoreload[2].x
		chunk_y = chunktoreload[2].y
		chunk_z = chunktoreload[2].z
		mdl_ref = chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][3].GetObject().GetModelRef()
		res.DestroyModel(mdl_ref)
		mdl_ref = res.AddModel(str(random.uniform(0, 5000)), mdl)
		chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][3].GetObject().SetModelRef(mdl_ref)
		chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][1] = mdl
		# reloadsidechunks(world, vtx_layout, chunks, chunk_amount, chunk_size, x, y, z)

def generatechunks(chunk_amount, chunk_index):
	chunks = {}
	queue = []
	for curchunk_x in range(-chunk_amount, chunk_amount):
		chunks[curchunk_x] = {}
		for curchunk_y in range(-chunk_amount, chunk_amount):
			chunks[curchunk_x][curchunk_y] = {}
			for curchunk_z in range(-chunk_amount, chunk_amount):
				newchunk = None
				chunks[curchunk_x][curchunk_y][curchunk_z] = newchunk
				chunk_index += 1
				queue.append([curchunk_x, curchunk_y, curchunk_z])
	return chunks, queue

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

chunk_size = 10
chunk_amount = 5
chunk_generator_index = 0
chunks, queue = generatechunks(chunk_amount, chunk_size)
modified_blocks = DictionnarySparseMatrix()

# setup scene
scene = hg.Scene()
scene.canvas.color = hg.ColorI(200, 210, 208)
scene.environment.ambient = hg.Color.Black

cam = hg.CreateCamera(scene, hg.Mat4.Identity, 0.01, 1000)
scene.SetCurrentCamera(cam)

lgt = hg.CreateLinearLight(scene, hg.TransformationMat4(hg.Vec3(0, 0, 0), hg.Deg3(19, 59, 0)), hg.Color(
	1.5, 0.9, 1.2, 1), hg.Color(1.5, 0.9, 1.2, 1), 10, hg.LST_Map, 0.002, hg.Vec4(8, 20, 40, 120))
back_lgt = hg.CreatePointLight(scene, hg.TranslationMat4(hg.Vec3(
	30, 20, 25)), 100, hg.Color(0.8, 0.5, 0.4, 1), hg.Color(0.8, 0.5, 0.4, 1), 0)

# input devices and fps controller states
keyboard = hg.Keyboard()
mouse = hg.Mouse()

cam_pos = hg.Vec3(0, 100, 0)
cam_rot = hg.Vec3(0, 0, 0)

# main loop
chunk_index = -chunk_amount
frame = 0

while not hg.ReadKeyboard().Key(hg.K_Escape):
	keyboard.Update()
	mouse.Update()
	dt = hg.TickClock()

	hg.FpsController(keyboard, mouse, cam_pos, cam_rot,
					 20 if keyboard.Down(hg.K_LShift) else 8, dt)
	cam.GetTransform().SetPos(cam_pos)
	cam.GetTransform().SetRot(cam_rot)
	scene.Update(dt)

	if chunk_index < len(queue):
		mdl = buildmodel(vtx_layout, modified_blocks, chunk_size, hg.Vec3(queue[chunk_index][0] * chunk_size, queue[chunk_index][1] * chunk_size, queue[chunk_index][2] * chunk_size))
		mdl_ref = res.AddModel(str(chunk_index), mdl)
		chunk_node = hg.CreateObject(scene, hg.TranslationMat4(hg.Vec3(queue[chunk_index][0] * chunk_size, queue[chunk_index][1] * chunk_size, queue[chunk_index][2] * chunk_size)), mdl_ref, [mat_cube, mat_sand, mat_water])
		chunks[queue[chunk_index][0]][queue[chunk_index][1]][queue[chunk_index][2]] = [chunk_index, mdl, hg.Vec3(queue[chunk_index][0] * chunk_size, queue[chunk_index][1] * chunk_size, queue[chunk_index][2] * chunk_size), chunk_node]
		chunk_index += 1

	if keyboard.Pressed(hg.K_Space):
		rayp0 = cam.GetTransform().GetPos()
		rayp1 = rayp0 + hg.GetZ(cam.GetTransform().GetWorld()) * 3
		deleteblock(modified_blocks, vtx_layout, chunks, chunk_amount, chunk_size, round(rayp1.x), round(rayp1.y), round(rayp1.z))

	if mouse.Pressed(hg.MB_1):
		rayp0 = cam.GetTransform().GetPos()
		rayp1 = rayp0 + hg.GetZ(cam.GetTransform().GetWorld()) * 3
		addblock(modified_blocks, vtx_layout, chunks, chunk_amount, chunk_size, round(rayp1.x), round(rayp1.y), round(rayp1.z))

	vid, pass_ids = hg.SubmitSceneToPipeline(0, scene, hg.IntRect(0, 0, res_x, res_y), True, pipeline, res, pipeline_aaa, pipeline_aaa_config, frame)

	vid_scene_opaque = hg.GetSceneForwardPipelinePassViewId(pass_ids, hg.SFPP_Opaque)

	show_preview_block(cam, vtx_layout_lines, vid_scene_opaque, pos_rgb)

	hg.Touch(0)
	frame = hg.Frame()
	hg.UpdateWindow(win)

hg.RenderShutdown()
