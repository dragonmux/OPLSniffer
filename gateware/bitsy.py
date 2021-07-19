#!/usr/bin/env python3

from sys import argv, path, exit
from pathlib import Path

from nmigen.hdl.ast import ClockSignal, ResetSignal
from nmigen.hdl.cd import ClockDomain
from nmigen.hdl.xfrm import DomainRenamer, ResetInserter

gatewarePath = Path(argv[0]).resolve()
if (gatewarePath.parent / 'sniffer').is_dir():
		path.insert(0, str(gatewarePath.parent))

from nmigen import Elaboratable, Module, Signal, Memory, Cat, Repl, Instance
from nmigen_boards.icebreaker_bitsy import ICEBreakerBitsyPlatform

class RAM(Elaboratable):
	def __init__(self):
		self.readData = Signal(8)
		self.writeData = Signal(8)
		self.address = Signal(3)
		self.read = Signal()
		self.write = Signal()

		self.contents = Memory(width = 8, depth = 2 ** 3)

	def elaborate(self, platform):
		m = Module()
		memory = self.contents
		writePort = memory.write_port()
		readPort = memory.read_port(transparent = False)
		m.submodules += writePort
		m.submodules += readPort

		m.d.comb += [
			writePort.addr.eq(self.address),
			writePort.data.eq(self.writeData),
			writePort.en.eq(self.write),

			readPort.addr.eq(self.address),
			self.readData.eq(readPort.data),
			readPort.en.eq(self.read)
		]
		return m

class Rebooter(Elaboratable):
	def __init__(self, *, sampleCounterWidth = 7, longCounterWidth = 17, buttonInverted = True):
		self.sampleCounterWidth = sampleCounterWidth
		self.longCounterWidth = longCounterWidth
		self.buttonInverted = buttonInverted

		# Inputs
		self.bootSelect = Signal()
		self.bootNow = Signal()
		self.buttonInput = Signal()

		# Outputs
		self.buttonValue = Signal()
		self.buttonPressed = Signal()
		self.willReboot = Signal()
		self.rebootTriggered = Signal()

	def elaborate(self, platform):
		m = Module()

		# Button sampling logic
		buttonCurrent = Signal()
		buttonInverted = 1 if self.buttonInverted else 0
		buttonValue = self.buttonValue
		buttonFalling = Signal()
		debounce = Signal(3)
		sampleCounterWidth = self.sampleCounterWidth + 1
		sampleCounter = Signal(sampleCounterWidth)
		sampleNow = Signal()

		_sampleCounterInc = Signal.like(sampleCounter)
		_sampleCounterMask = Signal.like(sampleCounter)
		_sampleCounterMaskBit = Signal()

		m.d.comb += [
			_sampleCounterInc.eq(Cat(sampleCounter[0:(sampleCounterWidth - 1)], 0) + 1),
			_sampleCounterMask.eq(Repl(_sampleCounterMaskBit, sampleCounterWidth)),
			_sampleCounterMaskBit.eq(~sampleCounter[sampleCounterWidth - 1]),
			sampleNow.eq(sampleCounter[sampleCounterWidth - 1]),
			buttonValue.eq(debounce[2]),
		]

		m.d.sync += [
			buttonCurrent.eq(self.buttonInput ^ buttonInverted),
			# This takes the top bit of the counter, inverts and replicates it, and ands that with
			# The rest of the counter incremented by 1, which creates a self-resetting counter
			sampleCounter.eq(_sampleCounterInc & _sampleCounterMask),
			buttonFalling.eq((debounce == 0b100) & ~buttonCurrent & sampleNow),
		]

		with m.If(sampleNow):
			with m.Switch(Cat(buttonCurrent, debounce)):
				with m.Case('0--0'):
					m.d.sync += debounce.eq(0b000)
				with m.Case('0001'):
					m.d.sync += debounce.eq(0b001)
				with m.Case('0011'):
					m.d.sync += debounce.eq(0b010)
				with m.Case('0101'):
					m.d.sync += debounce.eq(0b011)
				with m.Case('0111', '1--1'):
					m.d.sync += debounce.eq(0b111)
				with m.Case('1110'):
					m.d.sync += debounce.eq(0b110)
				with m.Case('1100'):
					m.d.sync += debounce.eq(0b101)
				with m.Case('1010'):
					m.d.sync += debounce.eq(0b100)
				with m.Case('1000'):
					m.d.sync += debounce.eq(0b000)
				with m.Default():
					m.d.sync += debounce.eq(0b000)

		# Long-press and Arming logic
		armed = Signal()
		longCounterWidth = self.longCounterWidth + 1
		longCounter = Signal(longCounterWidth)

		_longCounterInc = Signal.like(longCounter)
		_longCounterMask = Signal.like(longCounter)
		_longCounterMaskBit = Signal()

		m.d.comb += [
			_longCounterInc.eq(longCounter + Cat(~longCounter[longCounterWidth - 1], Repl(0, longCounterWidth - 1))),
			_longCounterMask.eq(Repl(_longCounterMaskBit, longCounterWidth)),
			_longCounterMaskBit.eq(~(armed ^ buttonValue)),
		]

		m.d.sync += [
			armed.eq(armed | longCounter[longCounterWidth - 3]),
			longCounter.eq(_longCounterInc & _longCounterMask),
		]

		# Command logic
		warmbootSelect = Signal(2)
		warmbootRequest = Signal()
		willReboot = self.willReboot

		m.d.comb += willReboot.eq(armed & longCounter[longCounterWidth - 1])

		with m.If(~warmbootRequest):
			with m.If(self.bootNow):
				m.d.sync += [
					warmbootSelect.eq(self.bootSelect),
					warmbootRequest.eq(1),
					self.buttonPressed.eq(0),
				]
			with m.Else():
				m.d.sync += [
					warmbootSelect.eq(0b01),
					warmbootRequest.eq((willReboot & buttonFalling) | warmbootRequest),
					self.buttonPressed.eq(armed & buttonFalling & ~longCounter[longCounterWidth - 1]),
				]

		# Rebooter
		warmbootNow = Signal()
		m.d.sync += warmbootNow.eq(warmbootRequest)
		m.d.comb += self.rebootTriggered.eq(warmbootNow)

		# This is not generated when this elaboratable is sim'd.
		if platform is not None:
			m.submodules += Instance(
				'SB_WARMBOOT',
				i_BOOT = warmbootNow,
				i_S0 = warmbootSelect[0],
				i_S1 = warmbootSelect[1],
			)

		return m

class IOWO(Elaboratable):
	program = [ # This program starts at address 0
		0x3064, # MOVLW     100
		0x0090, # MOVWF     0x10
		0x0091, # MOVWF     0x11
		0x0092, # MOVWF     0x12 - This should be address 3

		0x3001, # MOVLW     0x01
		0x0680, # XORWF     0x00,f - Toggles the red LED on/off

		0x3064, # MOVLW     100
		0x0B90, # DECFSZ    0x10,f - This should be address 7
		0x2807, # GOTO      0x007
		0x0090, # MOVWF     0x10 - Reload the counter
		0x0B91, # DECFSZ    0x11,f
		0x2807, # GOTO      0x007
		0x0091, # MOVWF     0x11 - Reload the counter
		0x0B92, # DECFSZ    0x12,f
		0x2807, # GOTO      0x007
		0x2803, # GOTO      0x003 - Once we've gone through 100*100*100 iterations,
				#                   jump back to the instruction that reloads the last counter
	]

	def __init__(self, *, sim = False):
		if sim:
			self.ledR = Signal()
			self.ledG = Signal()
			self.userBtn = Signal()

			self.address = Signal(12)
			self.data = Signal(16)
			self.read = Signal()

	def elaborate(self, platform):
		from sniffer.pic16 import PIC16
		from sniffer.rom import ROM
		m = Module()
		m.domains.processor = ClockDomain()
		m.submodules.processor = processor = DomainRenamer({'sync': 'processor'})(PIC16())
		# This is not generated when this elaboratable is sim'd.
		if platform is not None:
			m.submodules.rom = rom = ROM()
		m.submodules.rebooter = rebooter = Rebooter(longCounterWidth = 23, buttonInverted = False)
		m.submodules.ram = ram = RAM()

		# This is not generated when this elaboratable is sim'd.
		if platform is not None:
			rom.contents.init = IOWO.program

			m.d.comb += [
				rom.address.eq(processor.iAddr),
				processor.iData.eq(rom.data),
				rom.read.eq(processor.iRead),
			]
		else:
			m.d.comb += [
				self.address.eq(processor.iAddr),
				processor.iData.eq(self.data),
				self.read.eq(processor.iRead),
			]

		ready = Signal(range(3))
		gpio = Signal(8)
		read = Signal()

		m.d.sync += [
			read.eq(processor.pRead),
			ready.eq(ready + ~ready[1])
		]
		m.d.comb += [
			ClockSignal('processor').eq(ClockSignal()),
			ResetSignal('processor').eq(~ready[1])
		]

		with m.If(processor.pAddr == 0):
			with m.If(processor.pWrite):
				m.d.sync += gpio.eq(processor.pWriteData)
			with m.If(read):
				m.d.comb += processor.pReadData.eq(gpio)
		with m.Elif(processor.pAddr[4:] == 1):
			with m.If(processor.pWrite):
				m.d.comb += ram.writeData.eq(processor.pWriteData)
			with m.If(read):
				m.d.comb += processor.pReadData.eq(ram.readData)
			m.d.comb += [
				ram.address.eq(processor.pAddr[:4]),
				ram.read.eq(processor.pRead),
				ram.write.eq(processor.pWrite),
			]

		# This is not generated when this elaboratable is sim'd.
		if platform is not None:
			ledR = platform.request('led_r')
			m.d.comb += [
				ledR.o.eq(gpio[0])
			]

			ledG = platform.request('led_g')
			userBtn = platform.request('button', 0)
			m.d.comb += [
				rebooter.buttonInput.eq(userBtn),
				ledG.eq(rebooter.willReboot)
			]
		else:
			m.d.comb += [
				self.ledR.eq(gpio[0]),
				rebooter.buttonInput.eq(self.userBtn),
				self.ledG.eq(rebooter.willReboot),
			]
		return m

if __name__ == '__main__':
	platform = ICEBreakerBitsyPlatform()
	platform.build(IOWO(), name = "bitsy", do_program = True)
