from ..command import Command
import argparse

class GenerateStoreOrderEmails(Command):

    name = 'generate_store_order_emails'

    def arguments(self):
        parser = argparse.ArgumentParser(prog=self.name, description='Create an email to send to stores listing out their orders for the week.')
        parser.add_argument('--stores', nargs='+', required=True, help='List of stores.', default=self.context.get_stores())
        return parser

    def autocomplete(self, flag: str, text: str):
        
        flags = {
            '--stores': self.context.get_stores,
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]

    def command(self, args):
        try:
            parser = self.arguments()
            parsed_args = parser.parse_args(args)
            self.context.workbot.generate_store_order_emails(stores=parsed_args.stores)
            print('\nDisplaying Emails\n')
        except SystemExit:
            pass
        except Exception as e:
            print(e)