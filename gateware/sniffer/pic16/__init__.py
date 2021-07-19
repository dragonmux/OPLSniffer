from nmigen import Elaboratable, Module, Signal, unsigned
from .types import Opcodes, ALUOpcode, BitOpcode

__all__ = ["PIC16"]

class PIC16(Elaboratable):
	def __init__(self):
		self.iAddr = Signal(12)
		self.iData = Signal(14)
		self.iRead = Signal()
		self.pAddr = Signal(7)
		self.pReadData = Signal(8)
		self.pRead = Signal()
		self.pWriteData = Signal(8)
		self.pWrite = Signal()

		self.pcLatchHigh = Signal(8)

		self.wreg = Signal(8)
		self.pc = Signal(12)
		self.flags = Signal(8)

	def elaborate(self, platform):
		from .decoder import Decoder
		from .alu import ALU
		from .bitmanip import Bitmanip
		from .callStack import CallStack
		m = Module()
		decoder = Decoder()
		m.submodules.decoder = decoder
		alu = ALU()
		m.submodules.alu = alu
		bitmanip = Bitmanip()
		m.submodules.bitmanip = bitmanip
		callStack = CallStack()
		m.submodules.callStack = callStack

		q = Signal(unsigned(2))
		m.d.sync += q.eq(q + 1)

		instruction = Signal(14)
		lhs = Signal(8)
		rhs = Signal(8)
		result = Signal(8)
		targetBit = Signal(3)
		opEnable = Signal()

		carry = self.flags[0]

		opcode = Signal(Opcodes)
		aluOpcode = self.mapALUOpcode(m, opcode)
		bitOpcode = self.mapBitmanipOpcode(m, opcode)

		loadsWReg = self.loadsWReg(m, opcode)
		loadsFReg = self.loadsFReg(m, opcode)
		loadsLiteral = self.loadsLiteral(m, opcode)
		storesWReg = self.storesWReg(m, opcode, instruction[7])
		storesFReg = self.storesFReg(m, opcode, instruction[7])
		changesFlow = self.changesFlow(m, opcode)
		loadPCLatchHigh = self.loadPCLatchHigh(m, opcode)
		isReturn = self.isReturn(m, opcode)

		with m.Switch(q):
			with m.Case(0):
				with m.If(storesWReg):
					m.d.sync += self.wreg.eq(result)
				with m.Elif(storesFReg):
					m.d.sync += [
						self.pAddr.eq(instruction[0:7]),
						self.pWriteData.eq(result),
						self.pWrite.eq(1)
					]

				with m.If(aluOpcode != ALUOpcode.NONE):
					m.d.sync += carry.eq(alu.carry)
				with m.If(bitOpcode != BitOpcode.NONE):
					m.d.sync += carry.eq(bitmanip.carryOut)

				m.d.sync += [
					self.iAddr.eq(self.pc),
					self.iRead.eq(1)
				]
			with m.Case(1):
				m.d.sync += [
					self.pWrite.eq(0),
					self.iRead.eq(0),
					instruction.eq(self.iData),
					self.pAddr.eq(self.iData[0:7])
				]
			with m.Case(2):
				with m.If(loadsFReg):
					m.d.comb += self.pRead.eq(1)

				m.d.sync += opEnable.eq(1)
				with m.If(opcode == Opcodes.CALL):
					m.d.sync += [
						callStack.valueIn.eq(self.pc + 1),
						callStack.push.eq(1)
					]
				with m.Elif(isReturn):
					m.d.sync += [
						self.pc.eq(callStack.valueOut),
						callStack.pop.eq(1)
					]

				with m.If(loadPCLatchHigh):
					m.d.sync += [
						self.pc[0:11].eq(instruction[0:11]),
						self.pc[11:].eq(self.pcLatchHigh[3:5])
					]
			with m.Case(3):
				m.d.sync += opEnable.eq(0)
				with m.If(~changesFlow):
					m.d.sync += self.pc.eq(self.pc + 1)
				with m.Elif(opcode == Opcodes.CALL):
					m.d.sync += callStack.push.eq(0)
				with m.Elif(isReturn):
					m.d.sync += callStack.pop.eq(0)

		with m.If(loadsWReg):
			m.d.comb += lhs.eq(self.wreg)
		with m.Else():
			m.d.comb += lhs.eq(0)

		with m.If(loadsFReg):
			m.d.comb += rhs.eq(self.pReadData)
		with m.Elif(loadsLiteral):
			m.d.comb += rhs.eq(instruction[0:8])

		with m.If((opcode == Opcodes.BCF) | (opcode == Opcodes.BSF)):
			m.d.comb += targetBit.eq(instruction[7:10])

		with m.If(aluOpcode != ALUOpcode.NONE):
			m.d.comb += result.eq(alu.result)
		with m.If(bitOpcode != BitOpcode.NONE):
			m.d.comb += result.eq(bitmanip.result)
		with m.Elif((opcode == Opcodes.CLRF) | (opcode == Opcodes.CLRW)):
			m.d.comb += result.eq(0)
		with m.Elif(opcode == Opcodes.MOVLW):
			m.d.comb += result.eq(rhs)
		with m.Elif(opcode == Opcodes.MOVWF):
			m.d.comb += result.eq(self.wreg)

		m.d.comb += [
			decoder.instruction.eq(instruction),
			opcode.eq(decoder.opcode),
			alu.operation.eq(aluOpcode),
			alu.enable.eq(opEnable),
			alu.lhs.eq(lhs),
			alu.rhs.eq(rhs),
			bitmanip.operation.eq(bitOpcode),
			bitmanip.targetBit.eq(targetBit),
			bitmanip.enable.eq(opEnable),
			bitmanip.carryIn.eq(carry),
			bitmanip.value.eq(rhs)
		]
		return m

	def mapALUOpcode(self, m, opcode):
		result = Signal(ALUOpcode, name = "aluOpcode")
		with m.Switch(opcode):
			with m.Case(Opcodes.ADDLW, Opcodes.ADDWF):
				m.d.comb += result.eq(ALUOpcode.ADD)
			with m.Case(Opcodes.SUBLW, Opcodes.SUBWF):
				m.d.comb += result.eq(ALUOpcode.SUB)
			with m.Case(Opcodes.INCF, Opcodes.INCFSZ):
				m.d.comb += result.eq(ALUOpcode.INC)
			with m.Case(Opcodes.DECF, Opcodes.DECFSZ):
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

	def mapBitmanipOpcode(self, m, opcode):
		result = Signal(BitOpcode, name = "bitOpcode")
		with m.Switch(opcode):
			with m.Case(Opcodes.RRF):
				m.d.comb += result.eq(BitOpcode.ROTR)
			with m.Case(Opcodes.RLF):
				m.d.comb += result.eq(BitOpcode.ROTL)
			with m.Case(Opcodes.SWAPF):
				m.d.comb += result.eq(BitOpcode.SWAP)
			with m.Case(Opcodes.BCF):
				m.d.comb += result.eq(BitOpcode.BITCLR)
			with m.Case(Opcodes.BSF):
				m.d.comb += result.eq(BitOpcode.BITSET)
			with m.Default():
				m.d.comb += result.eq(BitOpcode.NONE)
		return result

	def loadsWReg(self, m, opcode):
		result = Signal(name = "loadsWReg")
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

	def loadsFReg(self, m, opcode):
		result = Signal(name = "loadsFReg")
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
				Opcodes.BCF,
				Opcodes.BSF,
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

	def storesWReg(self, m, opcode, dir):
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
			with m.Case(
				Opcodes.CLRF,
				Opcodes.DECF,
				Opcodes.MOVF,
				Opcodes.COMF,
				Opcodes.INCF,
				Opcodes.RRF,
				Opcodes.RLF,
				Opcodes.SWAPF,
				Opcodes.BCF,
				Opcodes.BSF
			):
				m.d.comb += result.eq(~dir)
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
				Opcodes.SWAPF
			):
				m.d.comb += result.eq(dir)
			with m.Case(
				Opcodes.BCF,
				Opcodes.BSF
			):
				m.d.comb += result.eq(1)
			with m.Default():
				m.d.comb += result.eq(0)
		return result

	def changesFlow(self, m, opcode):
		result = Signal(name = "changesFlow")
		with m.Switch(opcode):
			# Need to handle bit test f skip if <condition>..?
			with m.Case(
				Opcodes.CALL,
				Opcodes.GOTO,
				Opcodes.RETFIE,
				Opcodes.RETLW,
				Opcodes.RETURN
			):
				m.d.comb += result.eq(1)
			with m.Default():
				m.d.comb += result.eq(0)
		return result

	def isReturn(self, m, opcode):
		result = Signal(name = "isReturn")
		with m.Switch(opcode):
			with m.Case(
				Opcodes.RETFIE,
				Opcodes.RETLW,
				Opcodes.RETURN
			):
				m.d.comb += result.eq(1)
			with m.Default():
				m.d.comb += result.eq(0)
		return result

	def loadPCLatchHigh(self, m, opcode):
		result = Signal(name = "loadPCLatch")
		with m.Switch(opcode):
			with m.Case(
				Opcodes.CALL,
				Opcodes.GOTO
			):
				m.d.comb += result.eq(1)
			with m.Default():
				m.d.comb += result.eq(0)
		return result
