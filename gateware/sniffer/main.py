from .platform import OPLSnifferPlatform
from .oplSniffer import OPLSniffer

def cli():
	from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
	from nmigen import cli as nmigenCLI

	parser = ArgumentParser(formatter_class = ArgumentDefaultsHelpFormatter,
		description = 'OPLSniffer')
	nmigenCLI.main_parser(parser)
	actions = parser._subparsers._group_actions[0]
	buildAction = actions.add_parser('build', help = 'build a bitstream from the design')

	args = parser.parse_args()

	platform = OPLSnifferPlatform()
	oplSniffer = OPLSniffer()
	if args.action == 'build':
		platform.build(oplSniffer, name = 'OPLSniffer')
	else:
		nmigenCLI.main_runner(parser, args, oplSniffer, platform = platform, name = 'OPLSniffer')
			#, ports = oplSniffer.get_ports())
