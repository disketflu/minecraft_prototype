import harfang as hg

def test_collisions(cam, chunk_size, chunk_amount, world):
	forward = backwards = left = right = up = down = True
	rayp0 = cam.GetTransform().GetPos()
	raydistance = 0.5

	rayforward = rayp0 + hg.GetZ(cam.GetTransform().GetWorld()) * raydistance
	x = round(rayforward.x)
	y = round(rayforward.y)
	z = round(rayforward.z)

	# start sanity checks
	if x < 0 or y < 0 or z < 0:
		return None

	if x > chunk_size * chunk_amount - 1 or y > chunk_size * chunk_amount - 1 or z > chunk_size * chunk_amount - 1:
		return None
	# end sanity checks

	if world[x][y][z][0] != False:
		forward = False

	raybackwards = rayp0 - hg.GetZ(cam.GetTransform().GetWorld()) * raydistance
	x = round(raybackwards.x)
	y = round(raybackwards.y)
	z = round(raybackwards.z)

	# start sanity checks
	if x < 0 or y < 0 or z < 0:
		return None

	if x > chunk_size * chunk_amount - 1 or y > chunk_size * chunk_amount - 1 or z > chunk_size * chunk_amount - 1:
		return None
	# end sanity checks

	if world[x][y][z][0] != False:
		backwards = False

	rayleft = rayp0 - hg.GetX(cam.GetTransform().GetWorld()) * raydistance
	x = round(rayleft.x)
	y = round(rayleft.y)
	z = round(rayleft.z)

	# start sanity checks
	if x < 0 or y < 0 or z < 0:
		return None

	if x > chunk_size * chunk_amount - 1 or y > chunk_size * chunk_amount - 1 or z > chunk_size * chunk_amount - 1:
		return None
	# end sanity checks

	if world[x][y][z][0] != False:
		left = False

	rayright = rayp0 + hg.GetX(cam.GetTransform().GetWorld()) * raydistance
	x = round(rayright.x)
	y = round(rayright.y)
	z = round(rayright.z)

	# start sanity checks
	if x < 0 or y < 0 or z < 0:
		return None

	if x > chunk_size * chunk_amount - 1 or y > chunk_size * chunk_amount - 1 or z > chunk_size * chunk_amount - 1:
		return None
	# end sanity checks

	if world[x][y][z][0] != False:
		right = False

	rayup = rayp0 + hg.GetY(cam.GetTransform().GetWorld()) * raydistance
	x = round(rayup.x)
	y = round(rayup.y)
	z = round(rayup.z)

	# start sanity checks
	if x < 0 or y < 0 or z < 0:
		return None

	if x > chunk_size * chunk_amount - 1 or y > chunk_size * chunk_amount - 1 or z > chunk_size * chunk_amount - 1:
		return None
	# end sanity checks

	if world[x][y][z][0] != False:
		up = False

	raydown = rayp0 - hg.GetY(cam.GetTransform().GetWorld()) * raydistance
	x = round(raydown.x)
	y = round(raydown.y)
	z = round(raydown.z)

	# start sanity checks
	if x < 0 or y < 0 or z < 0:
		return None

	if x > chunk_size * chunk_amount - 1 or y > chunk_size * chunk_amount - 1 or z > chunk_size * chunk_amount - 1:
		return None
	# end sanity checks

	if world[x][y][z][0] == False:
		down = False

	return forward, backwards, left, right, up, down


def handlePlayerMovement(keyboard, mouse, cam_pos, cam_rot, cam, chunk_size, chunk_amount, genworld):
	world = hg.RotationMat3(cam_rot.x, cam_rot.y, cam_rot.z)
	front = hg.GetZ(world)
	side = hg.GetX(world)

	front.y = 0
	side.y = 0

	speed_multiplier = 5 if keyboard.Down(hg.K_LShift) else 1

	forward = backwards = left = right = up = down = True
	if test_collisions(cam, chunk_size, chunk_amount, genworld) != None:
		forward, backwards, left, right, up, down = test_collisions(cam, chunk_size, chunk_amount, genworld) 

	if keyboard.Down(hg.K_W) and forward:
		cam_pos += front * 0.01 * speed_multiplier

	if keyboard.Down(hg.K_A) and left:
		cam_pos -= side * 0.01 * speed_multiplier

	if keyboard.Down(hg.K_S) and backwards:
		cam_pos -= front * 0.01 * speed_multiplier

	if keyboard.Down(hg.K_D) and right:
		cam_pos += side * 0.01 * speed_multiplier

	if mouse.Down(hg.MB_0):
		cam_rot.x -= mouse.DtY() * 0.0025
		cam_rot.y += mouse.DtX() * 0.0025

	# jump
	if keyboard.Pressed(hg.K_Space) and up:
		cam_pos.y += 1.2

	if not down and not keyboard.Down(hg.K_Space):
		cam_pos.y -= 0.03

	return cam_pos, cam_rot