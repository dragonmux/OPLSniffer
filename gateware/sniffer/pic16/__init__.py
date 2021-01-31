from nmigen import Elaboratable, Module, Signal, unsigned
from .types import Opcodes, ALUOpcode

__all__ = ["PIC16"]

class PIC16(Elaboratable):
	def __init__(self):
		self.iAddr = Signal(12)
		self.iData = Signal(14)
		self.iRead = Signal()
		self.pAddr = Signal(range(128))
		self.pData = Signal(8)

		self.wreg = Signal(8)
		self.pc = Signal(12)

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
		lhs = Signal(8)
		rhs = Signal(8)
		result = Signal(8)

		opcode = Signal(Opcodes)
		aluOpcode = self.mapALUOpcode(m, opcode)
		needsWReg = self.needsWReg(m, opcode)

		with m.Switch(q):
			with m.Case(0):
				m.d.sync += [
					self.iAddr.eq(self.pc),
					self.iRead.eq(1)
				]
			with m.Case(1):
				m.d.sync += [
					instruction.eq(self.iData),
					self.iRead.eq(0),
					decoder.instruction.eq(instruction)
				]
			with m.Case(2):
				m.d.sync += [
					opcode.eq(decoder.opcode),
					alu.operation.eq(aluOpcode)
				]
			with m.Case(3):
				with m.If(aluOpcode != ALUOpcode.NONE):
					m.d.sync += result.eq(alu.result)
				with m.Elif((opcode == Opcodes.CLRF) | (opcode == Opcodes.CLRW)):
					m.d.sync += result.eq(0)

				m.d.sync += self.pc.eq(self.pc + 1)

		with m.If(needsWReg == 1):
			m.d.comb += lhs.eq(self.wreg)

		m.d.comb += [
			alu.lhs.eq(lhs),
			alu.rhs.eq(rhs),
			self.pData.eq(result)
		]
		return m

	def mapALUOpcode(self, m, opcode):
		result = Signal(ALUOpcode)
		with m.Switch(opcode):
			with m.Case(Opcodes.ADDLW, Opcodes.ADDWF):
				m.d.comb += result.eq(ALUOpcode.ADD)
			with m.Case(Opcodes.SUBLW, Opcodes.SUBWF):
				m.d.comb += result.eq(ALUOpcode.SUB)
			with m.Case(Opcodes.INCF):
				m.d.comb += result.eq(ALUOpcode.INC)
			with m.Case(Opcodes.DECF):
				m.d.comb += result.eq(ALUOpcode.DEC)
			with m.Case(Opcodes.ANDLW, Opcodes.ANDWF):
				m.d.comb += result.eq(ALUOpcode.AND)
			with m.Case(Opcodes.IORLW, Opcodes.IORWF):
				m.d.comb += result.eq(ALUOpcode.OR)
			with m.Case(Opcodes.XORLW, Opcodes.XORWF):
				m.d.comb += result.eq(ALUOpcode.XOR)
			with m.Default():
				m.d.comb += result.eq(ALUOpcode.NONE)
		return result

	def needsWReg(self, m, opcode):
		result = Signal(name = "needsWReg")
		with m.Switch(opcode):
			with m.Case(
				Opcodes.MOVWF,
				Opcodes.ADDWF,
				Opcodes.SUBWF,
				Opcodes.ANDWF,
				Opcodes.IORWF,
				Opcodes.XORWF,
				Opcodes.ADDLW,
				Opcodes.SUBLW,
				Opcodes.ANDLW,
				Opcodes.IORLW,
				Opcodes.XORLW
			):
				m.d.comb += result.eq(1)
			with m.Default():
				m.d.comb += result.eq(0)
		return result

	def needsFReg(self, m, opcode):
		result = Signal(name = "needsFReg")
		with m.Switch(opcode):
			with m.Case(
				Opcodes.ADDWF,
				Opcodes.SUBWF,
				Opcodes.ANDWF,
				Opcodes.IORWF,
				Opcodes.XORWF,
				Opcodes.INCF,
				Opcodes.INCFSZ,
				Opcodes.DECF,
				Opcodes.DECFSZ,
				Opcodes.COMF,
				Opcodes.MOVF,
				Opcodes.RLF,
				Opcodes.RRF,
				Opcodes.SWAPF,
				Opcodes.BTFSC,
				Opcodes.BTFSS
			):
				m.d.comb += result.eq(1)
			with m.Default():
				m.d.comb += result.eq(0)
		return result

	def loadsLiteral(self, m, opcode):
		result = Signal(name = "loadsLiteral")
		with m.Switch(opcode):
			with m.Case(
				Opcodes.MOVLW,
				Opcodes.RETLW,
				Opcodes.ADDLW,
				Opcodes.SUBLW,
				Opcodes.ANDLW,
				Opcodes.IORLW,
				Opcodes.XORLW
			):
				m.d.comb += result.eq(1)
			with m.Default():
				m.d.comb += result.eq(0)
		return result

	def storesWReg(self, m, opcode):
		result = Signal(name = "storesWReg")
		with m.Switch(opcode):
			with m.Case(
				Opcodes.CLRW,
				Opcodes.MOVLW,
				Opcodes.RETLW,
				Opcodes.ADDLW,
				Opcodes.SUBLW,
				Opcodes.ANDLW,
				Opcodes.IORLW,
				Opcodes.XORLW
			):
				m.d.comb += result.eq(1)
			with m.Default():
				m.d.comb += result.eq(0)
		return result

	def storesFReg(self, m, opcode, dir):
		result = Signal(name = "storesFReg")
		with m.Switch(opcode):
			with m.Case(
				Opcodes.MOVWF,
				Opcodes.CLRF,
				Opcodes.SUBWF,
				Opcodes.DECF,
				Opcodes.IORWF,
				Opcodes.ANDWF,
				Opcodes.XORWF,
				Opcodes.ADDWF,
				Opcodes.MOVF,
				Opcodes.COMF,
				Opcodes.INCF,
				Opcodes.RRF,
				Opcodes.RLF,
				Opcodes.SWAPF,
				Opcodes.BCF,
				Opcodes.BSF
			):
				m.d.comb += result.eq(dir)
			with m.Default():
				m.d.comb += result.eq(0)
		return result
