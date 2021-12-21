from amaranth import Elaboratable, Module, Signal, ClockDomain, DomainRenamer, ClockSignal, ResetSignal

__all__ = ["OPLSniffer"]

class OPLSniffer(Elaboratable):
	def elaborate(self, platform):
		from .opl2Sniffer import OPL2Sniffer
		from .pic16 import PIC16
		from .rom import ROM
		m = Module()
		m.domains.processor = ClockDomain()
		m.submodules.opl2Sniffer = OPL2Sniffer(platform.request('opl'))
		processor = DomainRenamer({'sync': 'processor'})(PIC16())
		m.submodules.processor = processor
		rom = ROM()
		m.submodules.rom = rom

		iBus = processor.iBus
		procReady = Signal(range(3))

		m.d.sync += [
			procReady.eq(procReady + ~procReady[1])
		]
		m.d.comb += [
			ClockSignal('processor').eq(ClockSignal()),
			ResetSignal('processor').eq(~procReady[1])
		]

		m.d.comb += [
			rom.address.eq(iBus.address),
			iBus.data.eq(rom.data),
			rom.read.eq(iBus.read)
		]

		gpioB = platform.request('gpioB')
		m.d.comb += [
			gpioB.o.eq(processor.pBus.writeData),
			processor.pBus.readData.eq(gpioB.i),
			gpioB.oe.eq(processor.pBus.write)
		]
		return m
