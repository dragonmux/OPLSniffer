from nmigen import Elaboratable, Module

__all__ = ["OPLSniffer"]

class OPLSniffer(Elaboratable):
	def elaborate(self, platform):
		from .opl2Sniffer import OPL2Sniffer
		from .pic16 import PIC16
		m = Module()
		m.submodules.opl2Sniffer = OPL2Sniffer(platform.request('opl'))
		m.submodules.processor = PIC16()
		return m
