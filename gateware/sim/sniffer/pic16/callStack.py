#!/usr/bin/env python3
from nmigen.sim import Simulator
from nmigen import Signal, Const, unsigned

from sys import argv, path
from pathlib import Path

gatewarePath = Path(argv[0]).resolve().parent.parent.parent
if (gatewarePath.parent / 'sniffer').is_dir():
		path.insert(0, str(gatewarePath.parent))

from sniffer.pic16.callStack import CallStack

dut = CallStack()

def benchSync():
	yield
	yield
	yield dut.valueIn.eq(0x713)
	yield dut.push.eq(1)
	assert (yield dut.count) == 0
	yield
	yield dut.push.eq(0)
	assert (yield dut.count) == 0
	yield
	yield dut.valueIn.eq(0xA5F)
	yield dut.push.eq(1)
	assert (yield dut.count) == 1
	yield
	yield dut.push.eq(0)
	assert (yield dut.count) == 1
	yield
	yield dut.pop.eq(1)
	assert (yield dut.count) == 2
	yield
	yield dut.pop.eq(0)
	assert (yield dut.count) == 2
	assert (yield dut.valueOut) == 0xA5F
	yield
	assert (yield dut.count) == 1
	yield
	yield dut.valueIn.eq(0x975)
	yield dut.push.eq(1)
	assert (yield dut.count) == 1
	yield
	yield dut.push.eq(0)
	assert (yield dut.count) == 1
	yield
	yield dut.pop.eq(1)
	assert (yield dut.count) == 2
	yield
	yield dut.pop.eq(0)
	assert (yield dut.count) == 2
	assert (yield dut.valueOut) == 0x975
	yield
	yield dut.pop.eq(1)
	assert (yield dut.count) == 1
	yield
	yield dut.pop.eq(0)
	assert (yield dut.count) == 1
	assert (yield dut.valueOut) == 0x713
	yield
	assert (yield dut.count) == 0
	yield

sim = Simulator(dut)
# This defines the sync clock to have a period of 1/25MHz
sim.add_clock(40e-9, domain = 'sync')
sim.add_sync_process(benchSync, domain = 'sync')

with sim.write_vcd('callStack.vcd'):
	sim.reset()
	sim.run()
