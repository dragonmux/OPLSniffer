from nmigen import Elaboratable, Module
from nmigen_soc.memory import MemoryMap
from .types import *

__all__ = ('PICBus')

class PICBus(Elaboratable):
	def __init__(self):
		self.processor = None
		self.memoryMap = MemoryMap(addr_width = 7, data_width = 8)
		self.registers = {}

	def add_processor(self, processor):
		assert self.processor == None, "Cannot add more than one processor to the bus"
		self.processor = processor

	def add_register(self, *, address):
		register = Register()
		self.memoryMap.add_resource(register, size = 1, addr = address)
		self.registers[address] = register
		return register

	def add_memory(self, *, address, size):
		#memory = Memory()
		pass

	def elaborate(self, platform):
		assert self.processor != None, "Must provide a processor for PICBus to connect to"
		self.memoryMap.freeze()

		m = Module()
		processor = Processor()

		m.d.comb += self.processor.pBus.eq(processor)

		for address, register in self.registers.items():
			with m.If(processor.address == address):
				m.d.comb += [
					register.read.eq(processor.read),
					processor.readData.eq(register.readData),
					register.write.eq(processor.write),
					register.writeData.eq(processor.writeData),
				]

		return m
