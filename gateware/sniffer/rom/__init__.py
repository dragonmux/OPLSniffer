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
		writePort = memory.write_port()
		readPort = memory.read_port(transparent = False)
		m.submodules += writePort
		m.submodules.rom = readPort

		m.d.comb += [
			writePort.addr.eq(0),
			writePort.data.eq(0),
			writePort.en.eq(0),

			readPort.addr.eq(self.address),
			self.data.eq(readPort.data),
			readPort.en.eq(self.read)
		]
		return m
