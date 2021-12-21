from amaranth.vendor.xilinx_spartan_3_6 import XilinxSpartan6Platform
from amaranth.build import Resource, Clock, Pins, Attrs
from .resources import *

__all__ = ["OPLSnifferPlatform"]

class OPLSnifferPlatform(XilinxSpartan6Platform):
	device = 'xc6slx9'
	package = 'tqg144'
	speed = '2'
	default_rst = 'rst'
	default_clk = 'clk25MHz'

	resources = [
		Resource('rst', 0, Pins('P143', dir = 'i'), Attrs(IOSTANDARD = 'LVCMOS33', PULLUP = 'TRUE')),
		Resource('clk25MHz', 0, Pins('P94', dir = 'i'), Clock(25e6), Attrs(IOSTANDARD = 'LVCMOS33')),
		Resource('clk50MHz', 0, Pins('P123', dir = 'i'), Clock(50e6), Attrs(IOSTANDARD = 'LVCMOS33')),
		OPLResource('opl', 0, load = 'P14', data = 'P15', oplClk = 'P16', attrs = Attrs(IOSTANDARD = 'LVCMOS33')),
		*GPIOResources(default_name = 'gpioA', pins="P1 P2 P5 P6 P7 P8 P9 P10",
			attrs = Attrs(IOSTANDARD = 'LVCMOS33')),
		*GPIOResources(default_name = 'gpioB', pins="P21 P22 P23 P24 P25 P26 P27 P29",
			attrs = Attrs(IOSTANDARD = 'LVCMOS33'))
	]

	connectors = []
