from amaranth.sim import Simulator
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
