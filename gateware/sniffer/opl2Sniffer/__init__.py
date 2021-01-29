from nmigen import Elaboratable, Module

__all__ = ["OPL2Sniffer"]

class OPL2Sniffer(Elaboratable):
	def __init__(self, opl):
		self.opl = opl

	def elaborate(self, platform):
		from .sniffer import Sniffer
		m = Module()
		m.submodules.sniffer = Sniffer(self.opl)
		return m
