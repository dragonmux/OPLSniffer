#!/usr/bin/env python3
from nmigen.sim import Simulator
from nmigen import Const, unsigned

from sys import argv, path
from pathlib import Path

gatewarePath = Path(argv[0]).resolve().parent.parent.parent
if (gatewarePath.parent / 'sniffer').is_dir():
		path.insert(0, str(gatewarePath.parent))

from sniffer.opl2Sniffer.sniffer import Sniffer

dut = Sniffer()
opl = dut.opl

def benchSync():
	yield

def loadConst(value):
	for (i, bit) in enumerate(Const(value, unsigned(16))):
		yield opl.data.eq(bit)
		if i == 7:
			yield opl.load.eq(1)
		elif i == 15:
			yield opl.load.eq(0)
		yield

def benchOPL():
	yield
	yield opl.load.eq(0)
	for value in loadConst(0x2DC7):
		yield value
	for value in loadConst(0xB968):
		yield value
	yield
	yield

sim = Simulator(dut)
# This defines the sync clock to have a period of 1/25MHz
sim.add_clock(40e-6, domain = 'sync')
# This defines the OPL clock to have a period of 1/2MHz
sim.add_clock(500e-6, domain = 'opl')
sim.add_sync_process(benchSync, domain = 'sync')
sim.add_sync_process(benchOPL, domain = 'opl')

with sim.write_vcd('sniffer.vcd'):
	sim.run()
