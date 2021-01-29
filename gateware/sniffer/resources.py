from nmigen.build import Resource, Subsignal, Pins, Clock

__all__ = ['OPLResource']

def OPLResource(*args, load, data, oplClk, conn = None, attrs = None):
	io = []
	io.append(Subsignal('load', Pins(load, dir = 'i', invert = True, conn = conn, assert_width = 1)))
	io.append(Subsignal('data', Pins(data, dir = 'i', conn = conn, assert_width = 1)))
	io.append(Subsignal('oplClk', Pins(oplClk, dir = 'i', conn = conn, assert_width = 1), Clock(2e6)))
	if attrs is not None:
		io.append(attrs)
	return Resource.family(*args, default_name = 'opl', ios = io)
