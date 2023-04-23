import argparse

# We want to override the error and exit methods of ArgumentParser
# to prevent it exiting unexpectedly or spewing error data over the air

class BBSArgumentParser(argparse.ArgumentParser):
    # Override the error handler to prevent exiting on error
    def error(self, message):
        print(message)
        raise Exception(message)

    def exit(self):
        pass


class Parser(BBSArgumentParser):

    def __init__(self, commands):
        self.parser = self.init_parser(commands)

    def init_parser(self, commands):
        # Root parser for BBS commands
        parser = BBSArgumentParser(
            description='BBS Main Menu',
            prog='',
            add_help=False,
            usage=argparse.SUPPRESS,
        )

        # We will create a subparser for each individual command
        subparsers = parser.add_subparsers(title='Commands', dest='command')

        # Loop through the commands and add each as a subparser
        for name, aliases, help_msg, func, arguments in commands:
            subparser = subparsers.add_parser(
                name,
                aliases=aliases,
                help=help_msg,
            )
            for arg_name, options in arguments.items():
                subparser.add_argument(arg_name, **options)
            subparser.set_defaults(func=func)

        return parser    
