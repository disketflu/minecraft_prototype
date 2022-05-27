# Draw models without a pipeline

from distutils.command.build import build
import harfang as hg
import random
from math import cos, sin, pi, floor, ceil

hg.InputInit()
hg.WindowSystemInit()

res_x, res_y = 1280, 720
win = hg.RenderInit('Harfang - Minecraft Prototype',
					res_x, res_y, hg.RF_VSync | hg.RF_MSAA4X)

#
pipeline = hg.CreateForwardPipeline()
res = hg.PipelineResources()

# vertex layout and models
vtx_layout = hg.VertexLayoutPosFloatNormUInt8()

cube_mdl = hg.CreateCubeModel(vtx_layout, 1, 1, 1)
ground_mdl = hg.CreatePlaneModel(vtx_layout, 5, 5, 1, 1)

shader = hg.LoadProgramFromFile('resources_compiled/shaders/mdl')
pos_rgb = hg.LoadProgramFromFile('resources_compiled/shaders/pos_rgb')

# create materials
prg_ref = hg.LoadPipelineProgramRefFromFile('resources_compiled/core/shader/pbr.hps', res, hg.GetForwardPipelineInfo())

mat_cube = hg.CreateMaterial(prg_ref, 'uBaseOpacityColor', hg.Vec4I(255, 255, 56), 'uOcclusionRoughnessMetalnessColor', hg.Vec4(1, 0.658, 1))

def createworld(chunk_amount, chunk_size):
	cubes_positions = []
	for x in range(chunk_size * chunk_amount):
		cubes_positions.append([])
		for y in range(chunk_size * chunk_amount):
			cubes_positions[x].append([])
			for z in range(chunk_size * chunk_amount):
				v = cos(x * 4 * pi / (chunk_size * chunk_amount)) + cos(z * pi / (chunk_size * chunk_amount)) + sin(y * 2 * pi / (chunk_size * chunk_amount)) 
				if v > 0:
					cubes_positions[x][y].append([False])
				else:
					cubes_positions[x][y].append([True])
	return cubes_positions

def buildmodel(vtx_layout, cubes_positions, chunk_size, chunk_pos):
	mdl_builder = hg.ModelBuilder()
	for x in range(int(chunk_pos.x), int(chunk_pos.x + chunk_size)):
		for y in range(int(chunk_pos.y), int(chunk_pos.y + chunk_size)):
			for z in range(int(chunk_pos.z), int(chunk_pos.z + chunk_size)):
				position = hg.Vec3(x - chunk_pos.x, y - chunk_pos.y, z - chunk_pos.z)
				should_draw = cubes_positions[x][y][z][0]

				should_draw_xpositive = False
				should_draw_xnegative = False
				if x > 0 and x < len(cubes_positions) - 1:
					should_draw_xpositive = cubes_positions[x + 1][y][z][0]
					should_draw_xnegative = cubes_positions[x - 1][y][z][0]

				should_draw_ypositive = False
				should_draw_ynegative = False
				if y > 0 and y < len(cubes_positions) - 1:
					should_draw_ypositive = cubes_positions[x][y + 1][z][0]
					should_draw_ynegative = cubes_positions[x][y - 1][z][0]

				should_draw_zpositive = False
				should_draw_znegative = False
				if z > 0 and z < len(cubes_positions) - 1:
					should_draw_zpositive = cubes_positions[x][y][z + 1][0]
					should_draw_znegative = cubes_positions[x][y][z - 1][0]

				is_covered_block = False
				if should_draw_xpositive and should_draw_xnegative and should_draw_ypositive and should_draw_ynegative and should_draw_zpositive and should_draw_znegative:
					is_covered_block = True

				if should_draw and not is_covered_block:
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

					# +Z

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

					# -Y

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

					# +Y

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

					# -X

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

					# +X

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

	mdl_builder.EndList(0)
	mdl = mdl_builder.MakeModel(vtx_layout)
	return mdl

def findchunkfromcoordinates(x, y, z, chunks, chunk_size, chunk_amount):
	# start sanity checks
	if x < 0 or y < 0 or z < 0:
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

	if chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][2] == hg.Vec3(chunk_x, chunk_y, chunk_z):
		appropriatechunk = chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)]

	if appropriatechunk == None:
		print("debug chunk finder :")
		print(x, y, z, "x y z")
		print(chunk_x, chunk_y, chunk_z, " chunk x y z")
		print(rounded_x, rounded_y, rounded_z, " rounded x y z \n")

	return appropriatechunk
	

def deleterandomblock(world, vtx_layout, chunks, chunk_amount, chunk_size):
	delete = random.uniform(0, 30)
	if delete < 2:
		random_x = random.randint(0, chunk_amount * chunk_size - 1)
		random_y = random.randint(0, chunk_amount * chunk_size - 1)
		random_z = random.randint(0, chunk_amount * chunk_size - 1)
		chunktoreload = findchunkfromcoordinates(random_x, random_y, random_z, chunks, chunk_size, chunk_amount)
		if chunktoreload != None:
			world[random_x][random_y][random_z][0] = False
			mdl = buildmodel(vtx_layout, world, chunk_size, chunktoreload[2])
			chunk_x = chunktoreload[2].x
			chunk_y = chunktoreload[2].y
			chunk_z = chunktoreload[2].z
			chunks[int(chunk_x / chunk_amount)][int(chunk_y  / chunk_amount)][int(chunk_z  / chunk_amount)][1] = mdl

def deleteblock(world, vtx_layout, chunks, chunk_amount, chunk_size, x, y, z):
	chunktoreload = findchunkfromcoordinates(x, y, z, chunks, chunk_size, chunk_amount)
	if chunktoreload != None:
		world[x][y][z][0] = False
		mdl = buildmodel(vtx_layout, world, chunk_size, chunktoreload[2])
		chunk_x = chunktoreload[2].x
		chunk_y = chunktoreload[2].y
		chunk_z = chunktoreload[2].z
		mdl_ref = res.AddModel(str(random.uniform(0, 5000)), mdl)
		chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][3].GetObject().SetModelRef(mdl_ref)
		chunks[int(chunk_x / chunk_size)][int(chunk_y  / chunk_size)][int(chunk_z  / chunk_size)][1] = mdl

def generatechunks(chunk_amount, chunk_size, vtx_layout, world, chunk_index):
	chunks = []
	queue = []
	for curchunk_x in range(chunk_amount):
		chunks.append([])
		for curchunk_y in range(chunk_amount):
			chunks[curchunk_x].append([])
			for curchunk_z in range(chunk_amount):
				newchunk = None
				chunks[curchunk_x][curchunk_y].append(newchunk)
				chunk_index += 1
				queue.append([curchunk_x, curchunk_y, curchunk_z])
	return chunks, queue

chunk_size = 10
chunk_amount = 10
chunk_generator_index = 0
world = createworld(chunk_amount, chunk_size)
chunks, queue = generatechunks(chunk_amount, chunk_size, vtx_layout, world, chunk_generator_index)

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

cam_pos = hg.Vec3(0, 1, -3)
cam_rot = hg.Vec3(0, 0, 0)

# main loop
chunk_index = 0
frame = 0

while not hg.ReadKeyboard().Key(hg.K_Escape):
	keyboard.Update()
	mouse.Update()
	dt = hg.TickClock()

	# angle = angle + hg.time_to_sec_f(dt)

	hg.FpsController(keyboard, mouse, cam_pos, cam_rot,
					 20 if keyboard.Down(hg.K_LShift) else 8, dt)

	cam.GetTransform().SetPos(cam_pos)
	cam.GetTransform().SetRot(cam_rot)
	scene.Update(dt)

	hg.SetViewPerspective(0, 0, 0, res_x, res_y, cam.GetTransform().GetWorld())

	# deleterandomblock(world, vtx_layout, chunks, chunk_amount, chunk_size)
	
	if chunk_index < len(queue):
		mdl = buildmodel(vtx_layout, world, chunk_size, hg.Vec3(queue[chunk_index][0] * chunk_size, queue[chunk_index][1] * chunk_size, queue[chunk_index][2] * chunk_size))
		mdl_ref = res.AddModel(str(chunk_index), mdl)
		chunk_node = hg.CreateObject(scene, hg.TranslationMat4(hg.Vec3(queue[chunk_index][0] * chunk_size, queue[chunk_index][1] * chunk_size, queue[chunk_index][2] * chunk_size)), mdl_ref, [mat_cube])
		chunks[queue[chunk_index][0]][queue[chunk_index][1]][queue[chunk_index][2]] = [chunk_index, mdl, hg.Vec3(queue[chunk_index][0] * chunk_size, queue[chunk_index][1] * chunk_size, queue[chunk_index][2] * chunk_size), chunk_node]
		chunk_index += 1

	if keyboard.Pressed(hg.K_Space):
		rayp0 = cam.GetTransform().GetPos()
		rayp1 = rayp0 + hg.GetZ(cam.GetTransform().GetWorld()) * 2
		deleteblock(world, vtx_layout, chunks, chunk_amount, chunk_size, round(rayp1.x), round(rayp1.y), round(rayp1.z))

	# vid_scene_opaque = hg.GetSceneForwardPipelinePassViewId(pass_ids, hg.SFPP_Opaque)

	# for ray in raylist:
	# 	vtx = hg.Vertices(vtx_layout_lines, 2)
	# 	vtx.Begin(0).SetPos(ray[0]).SetColor0(hg.Color.Green).End()
	# 	vtx.Begin(1).SetPos(ray[1]).SetColor0(hg.Color.Green).End()
	# 	hg.DrawLines(vid_scene_opaque, vtx, pos_rgb)

	hg.SubmitSceneToPipeline(0, scene, hg.IntRect(0, 0, res_x, res_y), True, pipeline, res)


	hg.Touch(0)
	frame = hg.Frame()
	hg.UpdateWindow(win)

hg.RenderShutdown()
