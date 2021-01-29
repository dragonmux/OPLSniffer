from collections import namedtuple
from nmigen import Elaboratable, Module, Signal, Cat, Memory, ClockDomain, ClockSignal
from nmigen.lib.fifo import AsyncFIFO

__all__ = ['Sniffer']

OPL = namedtuple('OPL', ('oplClk', 'data', 'load'))

class Sniffer(Elaboratable):
	def __init__(self):
		self.opl = OPL(Signal(), Signal(), Signal())

		self.validIncrement = Signal()
		self.data = Signal(16)

	def elaborate(self, platform):
		m = Module()
		opl = self.opl
		data = self.data

		sampleFIFO = AsyncFIFO(width = 16, depth = 1024, r_domain = 'sync', w_domain = 'opl')
		m.submodules.sampleFIFO = sampleFIFO
		m.domains.opl = ClockDomain()

		m.d.comb += [
			ClockSignal('opl').eq(opl.oplClk),
			sampleFIFO.w_data.eq(data)
		]

		m.d.opl += [
			data.eq(Cat(data[1:], opl.data))
		]
		return m
