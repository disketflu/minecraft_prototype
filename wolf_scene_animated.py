from playercontroller import handlePlayerMovement
import harfang as hg

from utils import RangeAdjust

# init program and window
hg.InputInit()
hg.WindowSystemInit()

res_x, res_y = 1920, 1080
win = hg.RenderInit('Wolf Animations Example', res_x, res_y, hg.RF_VSync | hg.RF_MSAA4X)

# prepare pipeline
pipeline = hg.CreateForwardPipeline()
res = hg.PipelineResources()

hg.AddAssetsFolder("resources_compiled")

# load scene
scene = hg.Scene()
hg.LoadSceneFromAssets("level/mainscene.scn", scene, res, hg.GetForwardPipelineInfo())
cam = hg.CreateCamera(scene, hg.Mat4.Identity, 0.01, 1000)
scene.SetCurrentCamera(cam)

# shaders, layouts, materials etc
vtx_layout = hg.VertexLayoutPosFloatNormUInt8()
vtx_layout_lines = hg.VertexLayoutPosFloatColorUInt8()
prg_ref = hg.LoadPipelineProgramRefFromAssets('core/shader/pbr.hps', res, hg.GetForwardPipelineInfo())
mat_ground = hg.CreateMaterial(prg_ref, 'uBaseOpacityColor', hg.Vec4I(10, 10, 10), 'uOcclusionRoughnessMetalnessColor', hg.Vec4(1, 1, 0))
mdl_ref = res.AddModel('ground', hg.CreateCubeModel(vtx_layout, 200, 0.01, 200))
render_state_quad_occluded = hg.ComputeRenderState(hg.BM_Alpha, False)
sphere_mdl = hg.CreateSphereModel(vtx_layout, 0.05, 12, 24)
sphere_ref = res.AddModel('sphere', sphere_mdl)
mat_spheres = hg.CreateMaterial(prg_ref, 'uBaseOpacityColor', hg.Vec4I(255, 71, 75), 'uOcclusionRoughnessMetalnessColor', hg.Vec4(1, 0.5, 0.1))
pos_rgb = hg.LoadProgramFromAssets("shaders/pos_rgb")

# input devices and fps controller states
keyboard = hg.Keyboard()
mouse = hg.Mouse()

# AAA pipeline
pipeline_aaa_config = hg.ForwardPipelineAAAConfig()
pipeline_aaa = hg.CreateForwardPipelineAAAFromAssets("core", pipeline_aaa_config, hg.BR_Equal, hg.BR_Equal)
pipeline_aaa_config.sample_count = 1

# main loop
frame = 0
hg.CreatePhysicCube(scene, hg.Vec3(200, 0.01, 200), hg.TranslationMat4(hg.Vec3(0, -0.05, 0)), mdl_ref, [mat_ground], 0)
flashlight_node = scene.GetNode("Flashlight")
flashlight_light_node = scene.GetNodeEx("Flashlight:Light")
wolf_node = scene.GetNode("Wolf_with_Animations")
wolf_mouth_node = scene.GetNodeEx("Wolf_with_Animations:Node/Wolf/Becken/Bauch/Bauch_001/Brust/Hals/Kopf_002/Kopf/Augen_con")
wolf_run = wolf_node.GetInstanceSceneAnim("01_Run")
wolf_idle = wolf_node.GetInstanceSceneAnim("04_Idle")
wolf_anim_ref = scene.PlayAnim(wolf_idle, hg.ALM_Loop)
wolf_reset = True
cam_pos = hg.Vec3(0.3, 0.5, 0.9)
cam_rot = hg.Vec3(0.6, -2.38, 0)
wolf_call_time = 0
wolf_call_pos = hg.Vec3(0, 0, 0)

# setup physics
physics = hg.SceneBullet3Physics()
physics.SceneCreatePhysicsFromAssets(scene)
physics_step = hg.time_from_sec_f(1 / 60)
clocks = hg.SceneClocks()

print("Press R to call the Wolf")
print("Press F to turn on / off the flashlight")

while not hg.ReadKeyboard().Key(hg.K_Escape):
	keyboard.Update()
	mouse.Update()

	dt = hg.TickClock()
	dts = hg.time_to_sec_f(dt)

	cam_pos, cam_rot = handlePlayerMovement(keyboard, mouse, cam_pos, cam_rot, cam, scene, physics, flashlight_node, flashlight_light_node)

	cam.GetTransform().SetPos(cam_pos)
	cam.GetTransform().SetRot(cam_rot)

	if keyboard.Pressed(hg.K_R) and wolf_call_time + hg.time_from_sec_f(5) < hg.GetClock():
		wolf_call_time = hg.GetClock()
		wolf_call_pos = wolf_node.GetTransform().GetPos()
		scene.StopAnim(wolf_anim_ref)
		wolf_anim_ref = scene.PlayAnim(wolf_run, hg.ALM_Loop)
		wolf_reset = False
	mapped_time = RangeAdjust(hg.GetClock(), wolf_call_time, wolf_call_time + hg.time_from_sec_f(5), 0, 1)
	if mapped_time < 0.9 and wolf_call_time + hg.time_from_sec_f(5) > hg.GetClock() and wolf_call_pos != hg.Vec3(0, 0, 0):
		wolf_pos = hg.Lerp(wolf_call_pos, cam_pos, mapped_time)
		wolf_node.GetTransform().SetPos(hg.Vec3(wolf_pos.x, 0, wolf_pos.z))
		wanted_rot = hg.GetRotation(hg.Mat4LookAt(wolf_node.GetTransform().GetPos(), cam.GetTransform().GetPos()))
		wolf_node.GetTransform().SetRot(hg.Vec3(0, wanted_rot.y, 0))
	elif wolf_reset==False:
		scene.StopAnim(wolf_anim_ref)
		wolf_anim_ref = scene.PlayAnim(wolf_idle, hg.ALM_Loop)
		wolf_reset = True

	hg.SceneUpdateSystems(scene, clocks, dt, physics, physics_step, 1)
	view_id, pass_ids = hg.SubmitSceneToPipeline(0, scene, hg.IntRect(0, 0, res_x, res_y), True, pipeline, res, pipeline_aaa, pipeline_aaa_config, frame)
	# view_id, pass_ids = hg.SubmitSceneToPipeline(0, scene, hg.IntRect(0, 0, res_x, res_y), True, pipeline, res) # render without AAA

	### DEBUG NOSE POSITION ###

	vid_scene_opaque = hg.GetSceneForwardPipelinePassViewId(pass_ids, hg.SFPP_Opaque)

	# vtx = hg.Vertices(vtx_layout_lines, 2)
	# vtx.Begin(0).SetPos(hg.GetTranslation(wolf_mouth_node.GetTransform().GetWorld())).SetColor0(hg.Color.Green).End()
	# vtx.Begin(1).SetPos(hg.Vec3(cam_pos.x, 0, cam_pos.z)).SetColor0(hg.Color.Green).End()
	# hg.DrawLines(vid_scene_opaque, vtx, pos_rgb)

	### END DEBUG ###

	frame = hg.Frame()
	hg.UpdateWindow(win)

hg.RenderShutdown()
hg.DestroyWindow(win)