from nmigen import Elaboratable, Module

__all__ = ["OPL2Sniffer"]

class OPL2Sniffer(Elaboratable):
	def __init__(self, opl):
		self.opl = opl

	def elaborate(self, platform):
		from .sniffer import Sniffer
		from .busInterface import BusInterface
		m = Module()
		opl = self.opl
		gpioA0 = platform.request('gpioA', 0)
		gpioA1 = platform.request('gpioA', 1)

		sniffer = Sniffer()
		m.submodules.sniffer = sniffer
		m.d.comb += [
			sniffer.opl.oplClk.eq(opl.oplClk.i),
			sniffer.opl.data.eq(opl.data.i),
			sniffer.opl.load.eq(opl.load.i),
			gpioA0.oe.eq(1),
			gpioA0.o.eq(sniffer.fifoFull),
			gpioA1.oe.eq(1),
			gpioA1.o.eq(sniffer.fifoReadable)
		]

		busInterface = BusInterface()
		m.submodules.busInterface = busInterface
		m.d.comb += [
			busInterface.availableSamples.eq(sniffer.availableCount),
			sniffer.read.eq(busInterface.readSample),
			busInterface.sample.eq(sniffer.sample)
		]
		return m
