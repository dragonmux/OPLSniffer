from amaranth import Elaboratable, Module, Signal
from amaranth_soc.memory import MemoryMap
from ..soc.peripheral import Peripheral

__all__ = ['BusInterface']

class BusInterface(Peripheral, Elaboratable):
	def __init__(self):
		super().__init__()

		bank = self.csr_bank()
		self._availableSamples = bank.csr(16, 'r')
		self._nextSample = bank.csr(16, 'r')

		#self._bridge = self.bridge(data_width = 8, granularity = 8, alignment = 1)
		#self.bus = self._bridge.bus

		self.availableSamples = Signal(16)
		self.readSample = Signal()
		self.sample = Signal(16)

	def elaborate(self, platform):
		m = Module()
		#m.submodules.bridge = self._bridge

		m.d.comb += [
			self._availableSamples.r_data.eq(self.availableSamples),
			self._nextSample.r_data.eq(self.sample)
		]

		m.d.sync += [
			self.readSample.eq(self._nextSample.r_stb)
		]

		return m
