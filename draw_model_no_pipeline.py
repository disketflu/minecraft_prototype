# Draw models without a pipeline

import harfang as hg
import random
from math import cos, sin, pi

hg.InputInit()
hg.WindowSystemInit()

res_x, res_y = 1280, 720
win = hg.RenderInit('Harfang - Draw Models no Pipeline', res_x, res_y, hg.RF_VSync | hg.RF_MSAA4X)

# vertex layout and models
vtx_layout = hg.VertexLayoutPosFloatNormUInt8()

cube_mdl = hg.CreateCubeModel(vtx_layout, 1, 1, 1)
ground_mdl = hg.CreatePlaneModel(vtx_layout, 5, 5, 1, 1)

shader = hg.LoadProgramFromFile('resources_compiled/shaders/mdl')
pos_rgb = hg.LoadProgramFromFile('resources_compiled/shaders/pos_rgb')


# chunk
cubes_positions = []
covered_blocks = []
chunk_size = 400

for x in range(chunk_size):
	cubes_positions.append([])
	for y in range(chunk_size):
		cubes_positions[x].append([])
		for z in range(chunk_size):
			v = cos(x * pi / chunk_size) + sin(y * 4 * pi / chunk_size) + cos(z * 3 * pi / chunk_size)
			if v > 0:
				cubes_positions[x][y].append([False])
			else:
			 	cubes_positions[x][y].append([True])

			# random_number = random.uniform(0, 10)
			# if random_number > 2:
			# 	cubes_positions[x][y].append([False])
			# else:
			# 	cubes_positions[x][y].append([True])

def buildmodel():
	mdl_builder = hg.ModelBuilder()

	##### -Z
	for x in range(chunk_size):
		for y in range(chunk_size):
			for z in range(chunk_size):
				position = hg.Vec3(x, y, z)
				should_draw = cubes_positions[x][y][z][0]

				should_draw_xpositive = False
				should_draw_xnegative = False
				if x > 0 and x < chunk_size - 1:
					should_draw_xpositive = cubes_positions[x + 1][y][z][0]
					should_draw_xnegative = cubes_positions[x - 1][y][z][0]
				
				should_draw_ypositive = False
				should_draw_ynegative = False
				if y > 0 and y < chunk_size - 1:
					should_draw_ypositive = cubes_positions[x][y + 1][z][0]
					should_draw_ynegative = cubes_positions[x][y - 1][z][0]

				should_draw_zpositive = False
				should_draw_znegative = False
				if z > 0 and z < chunk_size - 1:
					should_draw_zpositive = cubes_positions[x][y][z + 1][0]
					should_draw_znegative = cubes_positions[x][y][z - 1][0]

				is_covered_block = False
				if should_draw_xpositive and should_draw_xnegative and should_draw_ypositive and should_draw_ynegative and should_draw_zpositive and should_draw_znegative:
					is_covered_block = True
					covered_blocks.append(hg.Vec3(x, y, z))
					

				if should_draw and not is_covered_block:
					vertex0 = hg.Vertex()
					vertex0.pos = hg.Vec3(-0.5 + position.x, -0.5 + position.y, -0.5 + position.z)
					vertex0.normal = hg.Vec3(0, 0, -1)
					vertex0.uv0 = hg.Vec2(0, 0)
					a = mdl_builder.AddVertex(vertex0)

					vertex1 = hg.Vertex()
					vertex1.pos = hg.Vec3(-0.5 + position.x, 0.5 + position.y, -0.5 + position.z)
					vertex1.normal = hg.Vec3(0, 0, -1)
					vertex1.uv0 = hg.Vec2(0, 1)
					b = mdl_builder.AddVertex(vertex1)

					vertex2 = hg.Vertex()
					vertex2.pos = hg.Vec3(0.5 + position.x, 0.5 + position.y, -0.5 + position.z)
					vertex2.normal = hg.Vec3(0, 0, -1)
					vertex2.uv0 = hg.Vec2(1, 1)
					c = mdl_builder.AddVertex(vertex2)

					vertex3 = hg.Vertex()
					vertex3.pos = hg.Vec3(0.5 + position.x, -0.5 + position.y, -0.5 + position.z)
					vertex3.normal = hg.Vec3(0, 0, -1)
					vertex3.uv0 = hg.Vec2(1, 0)
					d = mdl_builder.AddVertex(vertex3)

					mdl_builder.AddTriangle(d, c, b)
					mdl_builder.AddTriangle(b, a, d)

					##### +Z

					vertex0 = hg.Vertex()
					vertex0.pos = hg.Vec3(-0.5 + position.x, -0.5 + position.y, 0.5 + position.z)
					vertex0.normal = hg.Vec3(0, 0, 1)
					vertex0.uv0 = hg.Vec2(0, 0)
					a = mdl_builder.AddVertex(vertex0)

					vertex1 = hg.Vertex()
					vertex1.pos = hg.Vec3(-0.5 + position.x, 0.5 + position.y, 0.5 + position.z)
					vertex1.normal = hg.Vec3(0, 0, 1)
					vertex1.uv0 = hg.Vec2(0, 1)
					b = mdl_builder.AddVertex(vertex1)

					vertex2 = hg.Vertex()
					vertex2.pos = hg.Vec3(0.5 + position.x, 0.5 + position.y, 0.5 + position.z)
					vertex2.normal = hg.Vec3(0, 0, 1)
					vertex2.uv0 = hg.Vec2(1, 1)
					c = mdl_builder.AddVertex(vertex2)

					vertex3 = hg.Vertex()
					vertex3.pos = hg.Vec3(0.5 + position.x, -0.5 + position.y, 0.5 + position.z)
					vertex3.normal = hg.Vec3(0, 0, 1)
					vertex3.uv0 = hg.Vec2(1, 0)
					d = mdl_builder.AddVertex(vertex3)

					mdl_builder.AddTriangle(a, b, c)
					mdl_builder.AddTriangle(a, c, d)

					##### -Y

					vertex0 = hg.Vertex()
					vertex0.pos = hg.Vec3(-0.5 + position.x, -0.5 + position.y, -0.5 + position.z)
					vertex0.normal = hg.Vec3(0, -1, 0)
					vertex0.uv0 = hg.Vec2(0, 0)
					a = mdl_builder.AddVertex(vertex0)

					vertex1 = hg.Vertex()
					vertex1.pos = hg.Vec3(-0.5 + position.x, -0.5 + position.y, 0.5 + position.z)
					vertex1.normal = hg.Vec3(0, -1, 0)
					vertex1.uv0 = hg.Vec2(0, 1)
					b = mdl_builder.AddVertex(vertex1)

					vertex2 = hg.Vertex()
					vertex2.pos = hg.Vec3(0.5 + position.x, -0.5 + position.y, 0.5 + position.z)
					vertex2.normal = hg.Vec3(0, -1, 0)
					vertex2.uv0 = hg.Vec2(1, 1)
					c = mdl_builder.AddVertex(vertex2)

					vertex3 = hg.Vertex()
					vertex3.pos = hg.Vec3(0.5 + position.x, -0.5 + position.y, -0.5 + position.z)
					vertex3.normal = hg.Vec3(0, -1, 0)
					vertex3.uv0 = hg.Vec2(1, 0)
					d = mdl_builder.AddVertex(vertex3)

					mdl_builder.AddTriangle(a, b, c)
					mdl_builder.AddTriangle(a, c, d)

					######## +Y

					vertex0 = hg.Vertex()
					vertex0.pos = hg.Vec3(-0.5 + position.x, 0.5 + position.y, -0.5 + position.z)
					vertex0.normal = hg.Vec3(0, 1, 0)
					vertex0.uv0 = hg.Vec2(0, 0)
					a = mdl_builder.AddVertex(vertex0)

					vertex1 = hg.Vertex()
					vertex1.pos = hg.Vec3(-0.5 + position.x, 0.5 + position.y, 0.5 + position.z)
					vertex1.normal = hg.Vec3(0, 1, 0)
					vertex1.uv0 = hg.Vec2(0, 1)
					b = mdl_builder.AddVertex(vertex1)

					vertex2 = hg.Vertex()
					vertex2.pos = hg.Vec3(0.5 + position.x, 0.5 + position.y, 0.5 + position.z)
					vertex2.normal = hg.Vec3(0, 1, 0)
					vertex2.uv0 = hg.Vec2(1, 1)
					c = mdl_builder.AddVertex(vertex2)

					vertex3 = hg.Vertex()
					vertex3.pos = hg.Vec3(0.5 + position.x, 0.5 + position.y, -0.5 + position.z)
					vertex3.normal = hg.Vec3(0, 1, 0)
					vertex3.uv0 = hg.Vec2(1, 0)
					d = mdl_builder.AddVertex(vertex3)

					mdl_builder.AddTriangle(d, c, b)
					mdl_builder.AddTriangle(b, a, d)

					######## -X

					vertex0 = hg.Vertex()
					vertex0.pos = hg.Vec3(-0.5 + position.x, -0.5 + position.y, -0.5 + position.z)
					vertex0.normal = hg.Vec3(-1, 0, 0)
					vertex0.uv0 = hg.Vec2(0, 0)
					a = mdl_builder.AddVertex(vertex0)

					vertex1 = hg.Vertex()
					vertex1.pos = hg.Vec3(-0.5 + position.x, -0.5 + position.y, 0.5 + position.z)
					vertex1.normal = hg.Vec3(-1, 0, 0)
					vertex1.uv0 = hg.Vec2(0, 1)
					b = mdl_builder.AddVertex(vertex1)

					vertex2 = hg.Vertex()
					vertex2.pos = hg.Vec3(-0.5 + position.x, 0.5 + position.y, 0.5 + position.z)
					vertex2.normal = hg.Vec3(-1, 0, 0)
					vertex2.uv0 = hg.Vec2(1, 1)
					c = mdl_builder.AddVertex(vertex2)

					vertex3 = hg.Vertex()
					vertex3.pos = hg.Vec3(-0.5 + position.x, 0.5 + position.y, -0.5 + position.z)
					vertex3.normal = hg.Vec3(-1, 0, 0)
					vertex3.uv0 = hg.Vec2(1, 0)
					d = mdl_builder.AddVertex(vertex3)

					mdl_builder.AddTriangle(d, c, b)
					mdl_builder.AddTriangle(b, a, d)

					######## +X

					vertex0 = hg.Vertex()
					vertex0.pos = hg.Vec3(0.5 + position.x, -0.5 + position.y, -0.5 + position.z)
					vertex0.normal = hg.Vec3(1, 0, 0)
					vertex0.uv0 = hg.Vec2(0, 0)
					a = mdl_builder.AddVertex(vertex0)

					vertex1 = hg.Vertex()
					vertex1.pos = hg.Vec3(0.5 + position.x, -0.5 + position.y, 0.5 + position.z)
					vertex1.normal = hg.Vec3(1, 0, 0)
					vertex1.uv0 = hg.Vec2(0, 1)
					b = mdl_builder.AddVertex(vertex1)

					vertex2 = hg.Vertex()
					vertex2.pos = hg.Vec3(0.5 + position.x, 0.5 + position.y, 0.5 + position.z)
					vertex2.normal = hg.Vec3(1, 0, 0)
					vertex2.uv0 = hg.Vec2(1, 1)
					c = mdl_builder.AddVertex(vertex2)

					vertex3 = hg.Vertex()
					vertex3.pos = hg.Vec3(0.5 + position.x, 0.5 + position.y, -0.5 + position.z)
					vertex3.normal = hg.Vec3(1, 0, 0)
					vertex3.uv0 = hg.Vec2(1, 0)
					d = mdl_builder.AddVertex(vertex3)

					mdl_builder.AddTriangle(a, b, c)
					mdl_builder.AddTriangle(a, c, d)

	mdl_builder.EndList(0)
	mdl = mdl_builder.MakeModel(vtx_layout)
	return mdl

mdl = buildmodel()

# setup scene
scene = hg.Scene()
scene.canvas.color = hg.ColorI(200, 210, 208)
scene.environment.ambient = hg.Color.Black

cam = hg.CreateCamera(scene, hg.Mat4.Identity, 0.01, 1000)
scene.SetCurrentCamera(cam)

lgt = hg.CreateLinearLight(scene, hg.TransformationMat4(hg.Vec3(0, 0, 0), hg.Deg3(19, 59, 0)), hg.Color(1.5, 0.9, 1.2, 1), hg.Color(1.5, 0.9, 1.2, 1), 10, hg.LST_Map, 0.002, hg.Vec4(8, 20, 40, 120))
back_lgt = hg.CreatePointLight(scene, hg.TranslationMat4(hg.Vec3(30, 20, 25)), 100, hg.Color(0.8, 0.5, 0.4, 1), hg.Color(0.8, 0.5, 0.4, 1), 0)

# input devices and fps controller states
keyboard = hg.Keyboard()
mouse = hg.Mouse()

cam_pos = hg.Vec3(0, 1, -3)
cam_rot = hg.Vec3(0, 0, 0)

# main loop
angle = 0

while not hg.ReadKeyboard().Key(hg.K_Escape):
	keyboard.Update()
	mouse.Update()
	dt = hg.TickClock()

	# angle = angle + hg.time_to_sec_f(dt)

	hg.FpsController(keyboard, mouse, cam_pos, cam_rot, 20 if keyboard.Down(hg.K_LShift) else 8, dt)

	cam.GetTransform().SetPos(cam_pos)
	cam.GetTransform().SetRot(cam_rot)
	scene.Update(dt)

	hg.SetViewPerspective(0, 0, 0, res_x, res_y, cam.GetTransform().GetWorld())
	
	hg.DrawModel(0, mdl, shader, [], [], hg.TransformationMat4(hg.Vec3(1, 0.5, 1), hg.Vec3(angle, angle, angle)))
	
	# vid_scene_opaque = hg.GetSceneForwardPipelinePassViewId(pass_ids, hg.SFPP_Opaque)

	# for ray in raylist:
	# 	vtx = hg.Vertices(vtx_layout_lines, 2)
	# 	vtx.Begin(0).SetPos(ray[0]).SetColor0(hg.Color.Green).End()
	# 	vtx.Begin(1).SetPos(ray[1]).SetColor0(hg.Color.Green).End()
	# 	hg.DrawLines(vid_scene_opaque, vtx, pos_rgb)

	hg.Frame()
	hg.UpdateWindow(win)

hg.RenderShutdown()
