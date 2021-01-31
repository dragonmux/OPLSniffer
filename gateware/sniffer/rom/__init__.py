from nmigen import Elaboratable, Module, Signal, Memory

__all__ = ['ROM']

class ROM(Elaboratable):
	def __init__(self):
		self.data = Signal(16)
		self.address = Signal(12)
		self.read = Signal()

	def elaborate(self, platform):
		m = Module()
		memory = Memory(width = 16, depth = 2 ** 12)
		rom = memory.read_port(transparent = False)
		m.submodules.rom = rom

		m.d.comb += [
			rom.addr.eq(self.address),
			self.data.eq(rom.data),
			rom.en.eq(self.read)
		]
		return m
