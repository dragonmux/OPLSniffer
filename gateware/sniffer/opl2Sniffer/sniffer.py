from collections import namedtuple
from nmigen import Elaboratable, Module, Signal, Cat, Memory, ClockDomain, ClockSignal
from nmigen.lib.fifo import AsyncFIFO

__all__ = ['Sniffer']

OPL = namedtuple('OPL', ('oplClk', 'data', 'load'))

class Sniffer(Elaboratable):
	def __init__(self):
		self.opl = OPL(Signal(name = 'oplClk'), Signal(name = 'oplData'), Signal(name = 'oplLoad'))

		self.sample = Signal(16)
		self.read = Signal()
		self.availableCount = Signal(10)
		self.fifoReadable = Signal()

		self.data = Signal(16)
		self.load = Signal()
		self.latch = Signal()
		self.fifoFull = Signal()

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
			self.sample.eq(sampleFIFO.r_data),
			sampleFIFO.r_en.eq(self.read),
			self.availableCount.eq(sampleFIFO.r_level),
			self.fifoReadable.eq(sampleFIFO.r_rdy),
			sampleFIFO.w_data.eq(data),
			sampleFIFO.w_en.eq(latch),
			self.fifoFull.eq(~sampleFIFO.w_rdy)
		]

		m.d.opl += [
			data.eq(Cat(data[1:], opl.data)),
			load.eq(opl.load),
			latch.eq((opl.load == 0) & (load == 1))
		]
		return m
