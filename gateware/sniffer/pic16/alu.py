from nmigen import Elaboratable, Module, Signal
from .types import ArithOpcode, LogicOpcode

__all__ = ('ArithUnit', 'LogicUnit')

class ArithUnit(Elaboratable):
	def __init__(self):
		self.lhs = Signal(8)
		self.rhs = Signal(8)
		self.result = Signal(8)
		self.carry = Signal()

		self.enable = Signal()
		self.operation = Signal(ArithOpcode)

	def elaborate(self, platform):
		m = Module()
		lhs = self.lhs
		rhs = self.rhs
		rhs_n = Signal(9)
		result = Signal(9, name = 'answer')

		with m.If(self.enable):
			with m.Switch(self.operation):
				with m.Case(ArithOpcode.ADD):
					m.d.comb += result.eq(lhs + rhs)
				with m.Case(ArithOpcode.SUB):
					m.d.comb += result.eq(lhs + rhs_n)
				with m.Case(ArithOpcode.INC):
					m.d.comb += result.eq(rhs + 1)
				with m.Case(ArithOpcode.DEC):
					m.d.comb += result.eq(rhs + 0x1FF)

		m.d.sync += rhs_n.eq((~rhs) + 1)
		m.d.comb += [
			self.result.eq(result[0:8]),
			self.carry.eq(result[8])
		]
		return m

class LogicUnit(Elaboratable):
	def __init__(self):
		self.lhs = Signal(8)
		self.rhs = Signal(8)
		self.result = Signal(8)

		self.enable = Signal()
		self.operation = Signal(LogicOpcode)

	def elaborate(self, platform):
		m = Module()
		lhs = self.lhs
		rhs = self.rhs
		result = self.result

		with m.If(self.enable):
			with m.Switch(self.operation):
				with m.Case(LogicOpcode.AND):
					m.d.comb += result.eq(lhs & rhs)
				with m.Case(LogicOpcode.OR):
					m.d.comb += result.eq(lhs | rhs)
				with m.Case(LogicOpcode.XOR):
					m.d.comb += result.eq(lhs ^ rhs)

		return m
