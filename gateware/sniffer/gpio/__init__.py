from amaranth import Elaboratable, Module, Signal, tracer

__all__ = ('GPIO', )

class GPIO(Elaboratable):
	def __init__(self, *, baseAddress, bus):
		namespace = tracer.get_var_name(depth = 2)
		self.inputs = Signal(8)
		self.outputs = Signal(8)
		self.outputEnables = Signal(8)

		self._registers = (
			bus.add_register(address = baseAddress, name = f'{namespace}.in'),
			bus.add_register(address = baseAddress + 1, name = f'{namespace}.out'),
			bus.add_register(address = baseAddress + 2, name = f'{namespace}.oe'),
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
