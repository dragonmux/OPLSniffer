#!/usr/bin/env python3
from nmigen.sim import Simulator
from nmigen import Signal, Const, unsigned

from sys import argv, path
from pathlib import Path

gatewarePath = Path(argv[0]).resolve().parent.parent.parent
if (gatewarePath.parent / 'sniffer').is_dir():
		path.insert(0, str(gatewarePath.parent))

from sniffer.pic16.types import Opcodes
from sniffer.pic16 import PIC16

dut = PIC16()

def benchSync():
	assert (yield dut.iRead) == 0
	# Perform NOP
	yield dut.iData.eq(0b00_0000_0000_0000)
	yield
	assert (yield dut.iRead) == 1
	yield
	assert (yield dut.iRead) == 0
	yield
	yield
	assert (yield dut.iRead) == 0
	# Perform MOVLW 0x1F
	yield dut.iData.eq(0b11_0000_0001_1111)
	yield
	assert (yield dut.iRead) == 1
	yield
	assert (yield dut.iRead) == 0
	yield
	yield
	assert (yield dut.iRead) == 0
	# Perform ADDLW 5
	yield dut.iData.eq(0b11_1110_0000_0101)
	yield
	assert (yield dut.wreg) == 0x1F
	assert (yield dut.iRead) == 1
	yield
	assert (yield dut.iRead) == 0
	yield
	yield
	assert (yield dut.iRead) == 0
	# Perform ADDWF 5,f
	yield dut.iData.eq(0b00_0111_1000_0101)
	yield
	assert (yield dut.wreg) == 0x24
	assert (yield dut.iRead) == 1
	yield
	assert (yield dut.pRead) == 0
	assert (yield dut.iRead) == 0
	yield dut.pData.eq(0x20)
	yield
	assert (yield dut.pRead) == 1
	yield
	assert (yield dut.pRead) == 0
	assert (yield dut.pWrite) == 0
	# Perform SWAPF 8,f
	yield dut.iData.eq(0b00_1110_1000_1000)
	yield
	assert (yield dut.wreg) == 0x24
	assert (yield dut.iRead) == 1
	assert (yield dut.pWrite) == 1
	assert (yield dut.pData) == 0x44
	yield
	assert (yield dut.iRead) == 0
	assert (yield dut.pWrite) == 0
	yield dut.pData.eq(0x0F)
	yield
	assert (yield dut.pRead) == 1
	yield
	assert (yield dut.pRead) == 0
	assert (yield dut.pWrite) == 0

	# Perform RLF 8,w
	yield dut.iData.eq(0b00_1101_0000_1000)
	yield
	assert (yield dut.pWrite) == 1
	assert (yield dut.pData) == 0xF0
	yield
	assert (yield dut.iRead) == 0
	assert (yield dut.pWrite) == 0
	yield dut.pData.eq(0x80)
	yield
	assert (yield dut.pRead) == 1
	yield
	assert (yield dut.pRead) == 0
	assert (yield dut.pWrite) == 0

	# Perform NOP
	yield dut.iData.eq(0b00_0000_0000_0000)
	yield
	assert (yield dut.wreg) == 0
	assert (yield dut.pWrite) == 0
	yield
	assert (yield dut.pWrite) == 0
	yield
	yield

sim = Simulator(dut)
# This defines the sync clock to have a period of 1/25MHz
sim.add_clock(40e-9, domain = 'sync')
sim.add_sync_process(benchSync, domain = 'sync')

with sim.write_vcd('processor.vcd'):
	sim.reset()
	sim.run()
