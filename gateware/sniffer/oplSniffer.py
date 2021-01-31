from nmigen import Elaboratable, Module

__all__ = ["OPLSniffer"]

class OPLSniffer(Elaboratable):
	def elaborate(self, platform):
		from .opl2Sniffer import OPL2Sniffer
		from .pic16 import PIC16
		from .rom import ROM
		m = Module()
		m.submodules.opl2Sniffer = OPL2Sniffer(platform.request('opl'))
		processor = PIC16()
		m.submodules.processor = processor
		rom = ROM()
		m.submodules.rom = rom

		m.d.comb += [
			rom.address.eq(processor.iAddr),
			processor.iData.eq(rom.data),
			rom.read.eq(processor.iRead)
		]

		gpioB = platform.request('gpioB')
		m.d.comb += [
			gpioB.o.eq(processor.pData),
			gpioB.oe.eq(0xFF)
		]
		return m
