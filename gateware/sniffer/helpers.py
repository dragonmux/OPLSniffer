class DotDict(dict):
	def __init__(self, dict):
		super().__init__(dict)

	def __getattr__(self, key):
		return self[key]
