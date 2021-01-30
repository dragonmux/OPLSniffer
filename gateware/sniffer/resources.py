from nmigen.build import Resource, Subsignal, Pins, Clock

__all__ = ['OPLResource', 'GPIOResources']

def OPLResource(*args, load, data, oplClk, conn = None, attrs = None):
	io = []
	io.append(Subsignal('load', Pins(load, dir = 'i', invert = True, conn = conn, assert_width = 1)))
	io.append(Subsignal('data', Pins(data, dir = 'i', conn = conn, assert_width = 1)))
	io.append(Subsignal('oplClk', Pins(oplClk, dir = 'i', conn = conn, assert_width = 1), Clock(2e6)))
	if attrs is not None:
		io.append(attrs)
	return Resource.family(*args, default_name = 'opl', ios = io)

def GPIOResources(*args, pins, default_name = 'gpio', conn = None, attrs = None):
	assert isinstance(pins, (str, list, dict))

	if isinstance(pins, str):
		pins = pins.split()
	if isinstance(pins, list):
		pins = dict(enumerate(pins))

	resources = []
	for number, pin in pins.items():
		ios = [Pins(pin, dir = 'io', conn = conn)]
		if attrs is not None:
			ios.append(attrs)
		resources.append(Resource.family(*args, number, default_name = default_name, ios = ios))
	return resources
