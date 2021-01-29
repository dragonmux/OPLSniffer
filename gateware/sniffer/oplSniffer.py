from nmigen import Elaboratable, Module

__all__ = ["OPLSniffer"]

class OPLSniffer(Elaboratable):
	def elaborate(self, platform):
		from .opl2Sniffer import OPL2Sniffer
		m = Module()
		m.submodules.opl2Sniffer = OPL2Sniffer(platform.request('opl'))
		return m
