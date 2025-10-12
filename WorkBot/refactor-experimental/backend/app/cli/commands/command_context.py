class CommandContext:
    '''Shared utilities and state for all CLI commands.'''

    def __init__(self, cli=None):
        self.cli = cli