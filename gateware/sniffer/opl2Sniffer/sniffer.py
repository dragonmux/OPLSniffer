from collections import namedtuple
from nmigen import Elaboratable, Module, Signal, Cat, Memory, ClockDomain, ClockSignal
from nmigen.lib.fifo import AsyncFIFO

__all__ = ['Sniffer']

OPL = namedtuple('OPL', ('oplClk', 'data', 'load'))

class Sniffer(Elaboratable):
	def __init__(self):
		self.opl = OPL(Signal(name = 'oplClk'), Signal(name = 'oplData'), Signal(name = 'oplLoad'))

		self.validIncrement = Signal()
		self.data = Signal(16)
		self.load = Signal()
		self.latch = Signal()

	def elaborate(self, platform):
		m = Module()
		opl = self.opl
		data = self.data
		load = self.load
		latch = self.latch

		sampleFIFO = AsyncFIFO(width = 16, depth = 1024, r_domain = 'sync', w_domain = 'opl')
		m.submodules.sampleFIFO = sampleFIFO
		m.domains.opl = ClockDomain()

		m.d.comb += [
			ClockSignal('opl').eq(opl.oplClk),
			sampleFIFO.w_data.eq(data),
			sampleFIFO.w_en.eq(latch)
		]

		m.d.opl += [
			data.eq(Cat(data[1:], opl.data)),
			load.eq(opl.load),
			latch.eq((opl.load == 0) & (load == 1))
		]
		return m
