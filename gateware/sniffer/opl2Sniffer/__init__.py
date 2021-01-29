from nmigen import Elaboratable, Module

__all__ = ["OPL2Sniffer"]

class OPL2Sniffer(Elaboratable):
	def __init__(self, opl):
		self.opl = opl

	def elaborate(self, platform):
		from .sniffer import Sniffer
		m = Module()
		opl = self.opl

		sniffer = Sniffer()
		m.submodules.sniffer = sniffer
		m.d.comb += [
			sniffer.opl.oplClk.eq(opl.oplClk.i),
			sniffer.opl.data.eq(opl.data.i),
			sniffer.opl.load.eq(opl.load.i)
		]
		return m
