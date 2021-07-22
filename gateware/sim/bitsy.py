#!/usr/bin/env python3
from nmigen.sim import Simulator, Settle
from nmigen import Signal, Const, Array

from sys import argv, path
from pathlib import Path

gatewarePath = Path(argv[0]).resolve().parent
if (gatewarePath.parent / 'sniffer').is_dir():
		path.insert(0, str(gatewarePath.parent))

from bitsy import IOWO

dut = IOWO(sim = True)
program = Array(
	(Const(opcode, 16) for opcode in
	[ # This program starts at address 0
		0x3004, # MOVLW     4
		0x0090, # MOVWF     0x10
		0x0091, # MOVWF     0x11
		0x0092, # MOVWF     0x12 - This should be address 3

		0x3001, # MOVLW     0x01
		0x0681, # XORWF     0x01,f - Toggles the red LED on/off

		0x3004, # MOVLW     4
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
	])
)
insn = Signal(16)
insnNext = Signal.like(insn)

def benchSync():
	yield Settle()
	for _ in range(1600):
		yield insnNext.eq(program[dut.address])
		yield dut.data.eq(insn)
		yield
		yield Settle()
		if (yield dut.read):
			yield insn.eq(insnNext)
		else:
			yield insn.eq(0)

sim = Simulator(dut)
# This defines the sync clock to have a period of 1/12MHz
sim.add_clock(83.3333e-9, domain = 'sync')
sim.add_sync_process(benchSync, domain = 'sync')

with sim.write_vcd('bitsy.vcd'):
	sim.reset()
	sim.run()
