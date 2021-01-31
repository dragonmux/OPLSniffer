#!/usr/bin/env python3
from nmigen.sim import Simulator
from nmigen import Signal, Const, unsigned

from sys import argv, path
from pathlib import Path

gatewarePath = Path(argv[0]).resolve().parent.parent.parent
if (gatewarePath.parent / 'sniffer').is_dir():
		path.insert(0, str(gatewarePath.parent))

from sniffer.pic16.types import ALUOpcode
from sniffer.pic16.alu import ALU

dut = ALU()

def perform(opcode, lhs, rhs):
	yield dut.operation.eq(opcode)
	yield dut.lhs.eq(lhs)
	yield dut.rhs.eq(rhs)

def checkResult(result, carry):
	assert (yield dut.result) == result
	assert (yield dut.carry) == carry

def benchSync():
	yield dut.enable.eq(1)
	yield from perform(ALUOpcode.NONE, 0, 0)
	yield
	yield from checkResult(0, 0)
	yield from perform(ALUOpcode.ADD, 5, 10)
	yield
	yield from checkResult(0, 0)
	yield from perform(ALUOpcode.NONE, 0, 0)
	yield
	yield from checkResult(15, 0)
	yield from perform(ALUOpcode.SUB, 35, 10)
	yield
	yield from checkResult(15, 0)
	yield from perform(ALUOpcode.NONE, 255, 112)
	yield
	yield from checkResult(25, 0)
	yield from perform(ALUOpcode.INC, 35, 0)
	yield
	yield from checkResult(25, 0)
	yield from perform(ALUOpcode.NONE, 0, 112)
	yield
	yield from checkResult(1, 0)
	yield from perform(ALUOpcode.DEC, 196, 254)
	yield
	yield from checkResult(1, 0)
	yield from perform(ALUOpcode.NONE, 0, 0)
	yield
	yield from checkResult(253, 0)
	yield from perform(ALUOpcode.AND, 154, 196)
	yield
	yield from checkResult(253, 0)
	yield from perform(ALUOpcode.NONE, 100, 5)
	yield
	yield from checkResult(128, 0)
	yield from perform(ALUOpcode.OR, 0xF0, 0x0F)
	yield
	yield from checkResult(128, 0)
	yield from perform(ALUOpcode.NONE, 100, 5)
	yield
	yield from checkResult(255, 0)
	yield from perform(ALUOpcode.XOR, 0xA5, 0x57)
	yield
	yield from checkResult(255, 0)
	yield from perform(ALUOpcode.NONE, 0, 5)
	yield
	yield from checkResult(0xF2, 0)
	yield from perform(ALUOpcode.ADD, 254, 5)
	yield
	yield from checkResult(0xF2, 0)
	yield from perform(ALUOpcode.SUB, 1, 5)
	yield
	yield from checkResult(3, 1)
	yield from perform(ALUOpcode.OR, 0xA0, 0x05)
	yield
	yield from checkResult(252, 1)
	yield from perform(ALUOpcode.INC, 66, 255)
	yield
	yield from checkResult(0xA5, 0)
	yield from perform(ALUOpcode.DEC, 66, 0)
	yield
	yield from checkResult(0, 1)
	yield from perform(ALUOpcode.ADD, 66, 54)
	yield
	yield from checkResult(255, 1)
	yield
	yield from checkResult(120, 0)

sim = Simulator(dut)
# This defines the sync clock to have a period of 1/25MHz
sim.add_clock(40e-9, domain = 'sync')
sim.add_sync_process(benchSync, domain = 'sync')

with sim.write_vcd('alu.vcd'):
	sim.reset()
	sim.run()
