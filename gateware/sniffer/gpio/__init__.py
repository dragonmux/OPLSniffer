from nmigen import Elaboratable, Module, Signal

__all__ = ('GPIO', )

class GPIO(Elaboratable):
	def __init__(self, *, baseAddress, bus):
		self.inputs = Signal(8)
		self.outputs = Signal(8)
		self.outputEnables = Signal(8)

		self._registers = (
			bus.add_register(address = baseAddress),
			bus.add_register(address = baseAddress + 1),
			bus.add_register(address = baseAddress + 2),
		)
		self._baseAddress = baseAddress

	def next_address_after(self):
		return self._baseAddress + 3

	def elaborate(self, platform):
		m = Module()
		inputReg, outputReg, directionReg = self._registers
		inputs = self.inputs
		outputs = self.outputs
		directions = self.outputEnables

		with m.If(inputReg.read):
			m.d.comb += inputReg.readData.eq(inputs)

		with m.If(outputReg.read):
			m.d.comb += outputReg.readData.eq(outputs)
		with m.If(outputReg.write):
			m.d.sync += outputs.eq(outputReg.writeData)

		with m.If(directionReg.read):
			m.d.comb += directionReg.readData.eq(directions)
		with m.If(directionReg.write):
			m.d.sync += directions.eq(directionReg.writeData)
		return m
