from nmigen import Record

__all__ = ('InstructionBus', 'PeripheralBus')

class InstructionBus(Record):
	def __init__(self, *, name = None):
		layout = [
			("address", 12),
			("data", 14),
			("read", 1),
		]

		super().__init__(layout, name = name, src_loc_at = 1)

class PeripheralBus(Record):
	def __init__(self, *, name = None):
		layout = [
			("address", 7),
			("read", 1),
			("readData", 8),
			("write", 1),
			("writeData", 8),
		]

		super().__init__(layout, name = name, src_loc_at = 1)
