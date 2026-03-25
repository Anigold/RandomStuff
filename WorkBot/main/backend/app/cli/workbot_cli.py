from backend.infra.logger import Logger
from backend.bots.workbot.work_bot import WorkBot
from .panel_cli import CLI
from .commands.workbot.workbot_context import WorkBotCommandContext


@Logger.attach_logger
class WorkBotCLI(CLI):
    ''' Interactive CLI for WorkBot '''
    
    def __init__(self, workbot = None):

        self.workbot = workbot or WorkBot()
        super().__init__()
        self._context = WorkBotCommandContext(workbot=self.workbot)
        self.load_commands_from_package('backend.app.cli.commands.workbot', self._context)
