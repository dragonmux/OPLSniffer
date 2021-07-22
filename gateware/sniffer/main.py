from .platform import OPLSnifferPlatform
from .oplSniffer import OPLSniffer

def cli():
	from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, FileType
	from nmigen import cli as nmigenCLI

	parser = ArgumentParser(formatter_class = ArgumentDefaultsHelpFormatter,
		description = 'OPLSniffer')
	actions = parser.add_subparsers(dest = 'action', required = True)
	genAction = actions.add_parser(
		'generate', help = 'generate RTLIL, Verilog or CXXRTL from the design'
	)
	genAction.add_argument(
		'-t', '--type', dest = 'generate_type', metavar = 'LANGUAGE', choices = ['il', 'cc', 'v'],
		help = 'generate LANGUAGE (il for RTLIL, v for Verilog, cc for CXXRTL; '+
			'default: file extension of FILE, if given)'
	)
	genAction.add_argument(
		'generate_file', metavar = 'FILE', type = FileType('w'), nargs = '?',
		help = 'write generated code to FILE'
	)
	actions.add_parser('build', help = 'build a bitstream from the design')
	simAction = actions.add_parser('simulate', help = 'run simulations on the design')
	simAction.add_argument(
		'unit', choices = ['alu', 'callStack'],
		help = 'which available unit simulation to run'
	)

	args = parser.parse_args()

	if args.action == 'simulate':
		if args.unit == 'alu':
			from sim.sniffer.pic16.alu import sim
		elif args.unit == 'callStack':
			from sim.sniffer.pic16.callStack import sim

		with sim.write_vcd(f'sim/{args.unit}.vcd'):
			sim.reset()
			sim.run()
		exit(0)

	platform = OPLSnifferPlatform()
	oplSniffer = OPLSniffer()
	if args.action == 'build':
		platform.build(oplSniffer, name = 'OPLSniffer')
	elif args.action == 'generate':
		nmigenCLI.main_runner(parser, args, oplSniffer, platform = platform, name = 'OPLSniffer')
