from nmigen import Elaboratable, Module, Signal, unsigned
from .types import Opcodes, ALUOpcode

__all__ = ["PIC16"]

class PIC16(Elaboratable):
	def __init__(self):
		self.iAddr = Signal()# TODO, figure out how wide the instruction bus needs to be
		self.iData = Signal(14)
		self.pAddr = Signal(range(128))
		self.pData = Signal(8)

		self.wreg = Signal(8)

	def elaborate(self, platform):
		from .decoder import Decoder
		from .alu import ALU
		m = Module()
		decoder = Decoder()
		m.submodules.decoder = decoder
		alu = ALU()
		m.submodules.alu = alu

		q = Signal(unsigned(2))
		m.d.sync += q.eq(q + 1)

		instruction = Signal(14)
		result = Signal(8)

		opcode = Signal(Opcodes)
		aluOpcode = self.mapALUOpcode(m, opcode)

		with m.Switch(q):
			with m.Case(0):
				m.d.sync += [
					instruction.eq(self.iData),
					decoder.instruction.eq(instruction)
				]
			with m.Case(1):
				m.d.sync += [
					opcode.eq(decoder.opcode),
					alu.operation.eq(aluOpcode)
				]
			with m.Case(2):
				with m.If(aluOpcode != ALUOpcode.NONE):
					m.d.sync += result.eq(alu.result)

		m.d.comb += self.pData.eq(result)
		return m

	def mapALUOpcode(self, m, opcode):
		result = Signal(ALUOpcode)
		with m.Switch(opcode):
			with m.Case(Opcodes.ADDLW):
				m.d.comb += result.eq(ALUOpcode.ADD)
			with m.Case(Opcodes.ADDWF):
				m.d.comb += result.eq(ALUOpcode.ADD)
			with m.Case(Opcodes.SUBLW):
				m.d.comb += result.eq(ALUOpcode.SUB)
			with m.Case(Opcodes.SUBWF):
				m.d.comb += result.eq(ALUOpcode.SUB)
			with m.Case(Opcodes.INCF):
				m.d.comb += result.eq(ALUOpcode.INC)
			with m.Case(Opcodes.DECF):
				m.d.comb += result.eq(ALUOpcode.DEC)
			with m.Case(Opcodes.ANDLW):
				m.d.comb += result.eq(ALUOpcode.AND)
			with m.Case(Opcodes.ANDWF):
				m.d.comb += result.eq(ALUOpcode.AND)
			with m.Case(Opcodes.IORLW):
				m.d.comb += result.eq(ALUOpcode.OR)
			with m.Case(Opcodes.IORWF):
				m.d.comb += result.eq(ALUOpcode.OR)
			with m.Case(Opcodes.XORLW):
				m.d.comb += result.eq(ALUOpcode.XOR)
			with m.Case(Opcodes.XORWF):
				m.d.comb += result.eq(ALUOpcode.XOR)
			with m.Default():
				m.d.comb += result.eq(ALUOpcode.NONE)
		return result
