import logging.config
import os
import subprocess
import sys
import yaml

from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session

from rsbbs.message import Message, Base
from rsbbs.parser import Parser


# Main BBS class

class BBS():

    def __init__(self, sysv_args):

        self.sysv_args = sysv_args

        self.config = self.load_config(sysv_args.config_file)

        self.calling_station = sysv_args.calling_station

        self.engine = self.init_engine()
        self.parser = self.init_parser()

        logging.config.dictConfig(self.config['logging'])

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    # Load the config file
    def load_config(self, config_file):

        try:
            with open(config_file, 'r') as stream:
                config = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            print("Could not load configuration file. Error: {}".format(e))
            exit(1)
        except FileNotFoundError as e:
            print('Configuration file full path: {}'.format(os.path.abspath(config_file)))
            print("Configuration file {} could not be found. Error: {}".format(config_file, e))
            exit(1)
        except Exception as msg:
            print("Error while loading configuration file {}. Error: {}".format(config_file))
            exit(1)

        logging.info("Configuration file was successfully loaded. File name: {}".format(config_file))

        return config
    

    # Set up the BBS command parser

    def init_parser(self):
        commands = [
            # (name, aliases, helpmsg, function, {arg: {arg attributes}, ...})
            ('bye', ['b', 'q'], 'Sign off and disconnect', self.bye, {}),
            ('delete', ['d', 'k'], 'Delete a message', self.delete,
                {'number': {'help': 'The numeric index of the message to delete'}},
            ),
            ('deletem', ['dm', 'km'], 'Delete all your messages', self.delete_mine, {}),
            ('help', ['h', '?'], 'Show help', self.help, {}),
            ('heard', ['j'], 'Show heard stations log', self.heard, {}),
            ('list', ['l'], 'List all messages', self.list, {}),
            ('listm', ['lm'], 'List only messages addressed to you', self.list_mine, {}),
            ('read', ['r'], 'Read messages', self.read, 
                {'number': {'help': 'Message number to read'}}
            ),
            ('readm', ['rm'], 'Read only messages addressed to you', self.read_mine, {}),
            ('send', ['s'], 'Send a new message to a user', self.send,
                {
                    'callsign': {'help': 'Message recipient callsign'},
                    '--subject': {'help': 'Message subject'},
                    '--message': {'help': 'Message'},
                },
            ),
            ('sendp', ['sp'], 'Send a private message to a user', self.send_private,
                {
                    'callsign': {'help': 'Message recipient callsign'},
                    '--subject': {'help': 'Message subject'},
                    '--message': {'help': 'Message'},
                },
            ),
        ]
        return Parser(commands).parser


    # Database

    def init_engine(self):
        engine = create_engine('sqlite:///messages.db', echo=self.sysv_args.debug)
        Base.metadata.create_all(engine)
        return engine
    

    # Input and output
    
    def read_line(self, prompt):
        output = None
        while output == None:
            if prompt:
                self.write_output(prompt)
            input = sys.stdin.readline().strip()
            if input != "":
                output = input
        return output

    def read_multiline(self, prompt):
        output = []
        if prompt:
            self.write_output(prompt)
        while True:
            line = sys.stdin.readline()
            if line.lower().strip() == "/ex":
                break
            else:
                output.append(line)
        return ''.join(output)

    def write_output(self, output):
        sys.stdout.write(output + '\r\n')

    def print_message_list(self, results):
        self.write_output(f"{'MSG#': <{5}} {'TO': <{9}} {'FROM': <{9}} {'DATE': <{10}}  SUBJECT")
        for result in results:
            self.write_output(f"{result.Message.id: <{5}} {result.Message.recipient: <{9}} {result.Message.sender: <{9}} {result.Message.datetime.strftime('%Y-%m-%d')}  {result.Message.subject}")

    def print_message(self, message):
        self.write_output(f"")
        self.write_output(f"Message: {message.Message.id}")
        self.write_output(f"Date:    {message.Message.datetime.strftime('%A, %B %-d, %Y at %-H:%M %p UTC')}")
        # self.write_output(f"Date:    {message.Message.datetime.strftime('%Y-%m-%dT%H:%M:%S+0000')}")
        self.write_output(f"From:    {message.Message.sender}")
        self.write_output(f"To:      {message.Message.recipient}")
        self.write_output(f"Subject: {message.Message.subject}")
        self.write_output(f"\r\n{message.Message.message}")


    # BBS command functions

    def bye(self, args):
        '''Disconnect and exit'''
        self.write_output("Bye!")
        exit(0)

    def delete(self, args):
        '''Delete message specified by numeric index'''
        with Session(self.engine) as session:
            try:
                message = session.get(Message, args.number)
                session.delete(message)
                session.commit()
                self.write_output(f"Deleted message #{args.number}")
            except Exception as e:
                self.write_output(f"Unable to delete message #{args.number}")

    def delete_mine(self, args):
        '''Delete all messages addressed to user'''
        self.write_output("Delete all messages addressed to you? Y/N:")
        response = sys.stdin.readline().strip()
        if response.lower() != "y":
            return
        else:
            with Session(self.engine) as session:
                try:
                    statement = delete(Message).where(Message.recipient == self.calling_station).returning(Message)
                    results = session.execute(statement)
                    count = len(results.all())
                    if count > 0:
                        self.write_output(f"Deleted {count} messages")
                        session.commit()
                    else:
                        self.write_output(f"No messages to delete.")
                except Exception as e:
                    self.write_output(f"Unable to delete messages: {e}")

    def heard(self, args):
        '''Show heard stations log'''
        self.write_output(f"Heard stations:")
        result = subprocess.run(['mheard'], capture_output=True, text=True)
        self.write_output(result.stdout)

    def help(self, args):
        '''Print help'''
        self.parser.print_help()

    def list(self, args):
        '''List all messages'''
        with Session(self.engine) as session:
            statement = select(Message).where((Message.is_private == False) | (Message.recipient == self.calling_station))
            results = session.execute(statement)
            self.print_message_list(results)

    def list_mine(self, args):
        '''List only messages addressed to user'''
        with Session(self.engine) as session:
            statement = select(Message).where(Message.recipient == self.calling_station)
            results = session.execute(statement)
            self.print_message_list(results)

    def read(self, args):
        '''Read messages'''
        with Session(self.engine) as session:
            statement = select(Message).where(Message.id == args.number)
            result = session.execute(statement).one()
            self.print_message(result)

    def read_mine(self, args):
        '''Read only messages addressed to user'''
        with Session(self.engine) as session:
            statement = select(Message).where(Message.recipient == self.calling_station)
            result = session.execute(statement)
            messages = result.all()
            count = len(messages)
            if count > 0:
                self.write_output(f"Reading {count} messages:")
                for message in messages:
                    self.print_message(message)
                    self.write_output("Enter to continue...")
                    sys.stdin.readline()
            else:
                self.write_output(f"No messages to read.")

    def send(self, args, is_private=False):
        '''Create a message addressed to another user'''
        if not args.callsign:
            args.callsign = self.read_line("Callsign:")
        if not args.subject:
            args.subject = self.read_line("Subject:")
        if not args.message:
            args.message = self.read_multiline("Message - end with /ex on a single line:")
        with Session(self.engine) as session:
            session.add(Message(
                sender=self.calling_station.upper(),
                recipient=args.callsign.upper(),
                subject=args.subject,
                message=args.message,
                is_private=is_private
            ))
            try:
                session.commit()
                self.write_output("Message saved!")
            except Exception as e:
                session.rollback()
                self.write_output("Error saving message. Contact the sysop for assistance.")

    def send_private(self, args):
        self.send(args, is_private=True)

    # Main loop

    def main(self):
        # Show greeting
        self.write_output(f"[RSBBS-1.0.0] listening on {self.config['callsign']} ")
        self.write_output(f"Welcome to {self.config['bbs_name']}, {self.calling_station}")
        self.write_output(self.config['banner_message'])
        self.write_output("For help, enter 'h'")

        # Show initial prompt to the calling user
        self.write_output(self.config['command_prompt'])

        # Parse the BBS interactive commands for the rest of time
        for line in sys.stdin:
            try:
                args = self.parser.parse_args(line.split())
                args.func(args)
            except Exception as msg:
                pass

            # Show our prompt to the calling user again
            self.write_output(self.config['command_prompt'])
