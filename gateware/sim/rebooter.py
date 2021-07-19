#!/usr/bin/env python3
from nmigen.sim import Simulator
from nmigen import Signal, Const, unsigned

from sys import argv, path
from pathlib import Path

gatewarePath = Path(argv[0]).resolve().parent
if (gatewarePath.parent / 'sniffer').is_dir():
		path.insert(0, str(gatewarePath.parent))

from bitsy import Rebooter

dut = Rebooter(sampleCounterWidth = 2, longCounterWidth = 5)

def benchSync():
	yield dut.buttonInput.eq(1)
	yield
	yield
	assert (yield dut.willReboot) == 0
	yield dut.buttonInput.eq(0)
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	assert (yield dut.buttonValue) == 1
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	assert (yield dut.willReboot) == 1
	yield
	yield
	yield
	yield
	yield
	yield
	yield dut.buttonInput.eq(1)
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	yield
	assert (yield dut.buttonValue) == 0
	yield
	yield
	yield
	yield
	yield
	yield

sim = Simulator(dut)
# This defines the sync clock to have a period of 1/12MHz
sim.add_clock(83.3333e-9, domain = 'sync')
sim.add_sync_process(benchSync, domain = 'sync')

with sim.write_vcd('rebooter.vcd'):
	sim.reset()
	sim.run()
