import harfang as hg

def handlePlayerMovement(keyboard, mouse, cam_pos, cam_rot, cam, scene, physics, flashlight_node, flashlight_light_node):
	world = hg.RotationMat3(cam_rot.x, cam_rot.y, cam_rot.z)
	front = hg.GetZ(world)
	right = hg.GetX(world)

	front.y = 0
	right.y = 0

	if keyboard.Down(hg.K_W):
		cam_pos += front * 0.05

	if keyboard.Down(hg.K_A):
		cam_pos -= right * 0.05

	if keyboard.Down(hg.K_S):
		cam_pos -= front * 0.05

	if keyboard.Down(hg.K_D):
		cam_pos += right * 0.05

	if mouse.Down(hg.MB_0):
		cam_rot.x -= mouse.DtY() * 0.0025
		cam_rot.y += mouse.DtX() * 0.0025

	if keyboard.Pressed(hg.K_F):
		if flashlight_light_node.IsEnabled():
			flashlight_light_node.Disable()
		else:
			flashlight_light_node.Enable()

	flashlight_pos = hg.Vec3(cam_pos.x + front.x * 0.2, cam_pos.y - 0.1, cam_pos.z + front.z * 0.2)
	flashlight_pos.x += right.x * 0.05
	flashlight_pos.z += right.z * 0.05
	flashlight_node.GetTransform().SetPos(flashlight_pos)
	flashlight_node.GetTransform().SetRot(hg.Vec3(0, cam_rot.y, 0))

	return cam_pos, cam_rot