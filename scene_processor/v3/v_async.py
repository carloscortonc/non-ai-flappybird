import numpy as np
import asyncio
import dxcam

GAME_BBOX = [722, 306, 477, 540]
PIPE_RELATIVE = [468, 0, 1, 444]
BIRD_RELATIVE = [205, 9, 1, 550]
EXITING_PIPE_RELATIVE = [BIRD_RELATIVE[0] - 30, PIPE_RELATIVE[1], 1, 1]

PIPE_SEPARATION = 160
BIRD_MARGIN = 65
JUMP = 40

class SceneProcessor:
	def __init__(self, onupdate):
		self.cam = dxcam.create()
		self.pipe_height_last = False
		self.pipe_exit_last = False
		self.pipes = []
		self.bird_height = 0
		self.onupdate = onupdate
		# start capturing process
		self.capture()

	def capture(self):
		var = True
		while var:
			# start_time = time.time()
			# self.captureFrame()
			asyncio.run(self.captureFrame())
			# print("FPS: ", (time.time() - start_time )* 1000.0)
			# var = False

	async def captureFrame(self):
		game = self.captureElement(GAME_BBOX)
		if game is None:
			return
		await asyncio.gather(
			self.capturePipeHeight(game),
			self.captureExitingPipe(game),
			self.captureBirdPosition(game)
		)
		bird = self.bird_height + BIRD_MARGIN
		pipe = self.pipes[0] + PIPE_SEPARATION if self.pipes.__len__() > 0 else 320
		self.onupdate({ "bird": bird, "pipe": pipe})

	isPipe = lambda _, pipe, col, row : pipe[col][row][2] != 206

	async def capturePipeHeight(self, game):
		if self.isPipe(game, 0 + PIPE_RELATIVE[1], PIPE_RELATIVE[0]) and not self.pipe_height_last:
			self.pipe_height_last = True
			pipe_height = 0
			while self.isPipe(game, pipe_height + PIPE_RELATIVE[1], PIPE_RELATIVE[0]):
				pipe_height += 1
			self.pipes.append(pipe_height)
		elif not self.isPipe(game, 0 + PIPE_RELATIVE[1], PIPE_RELATIVE[0]):
			self.pipe_height_last = False

	async def captureExitingPipe(self, game):
		if not self.isPipe(game, 0 + EXITING_PIPE_RELATIVE[1], EXITING_PIPE_RELATIVE[0]) and self.pipe_exit_last:
			self.pipe_exit_last = False
			self.pipes.pop(0)
		elif self.isPipe(game, 0 + EXITING_PIPE_RELATIVE[1], EXITING_PIPE_RELATIVE[0]):
			self.pipe_exit_last = True

	async def captureBirdPosition(self, game):
		isBird = lambda i: np.array_equal(game[i + BIRD_RELATIVE[1]][BIRD_RELATIVE[0]], [212, 191, 39])
		self.bird_height = -1
		bird_last = False
		while True:
			self.bird_height += 1
			checkBird = isBird(self.bird_height)
			if not checkBird and bird_last:
				break
			elif checkBird:
				bird_last = True

	def captureElement(self, bbox):
		return self.cam.grab(region=(bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3]))

	def cleanup(self):
		print("cleanup")
		return True
