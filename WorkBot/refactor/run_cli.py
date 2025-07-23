from cli.workbot_cli import WorkBotCLI
import subprocess
import sys
import platform
from pathlib import Path

from backend.exporters.load_exporters import load_exporters

LOG_FILE = Path('./logs/master.log').absolute().as_posix()
GIT_BASH_PATH = Path('C:/Program Files/Git/bin/bash.exe')


def open_log_terminal():
    """Open a new terminal window and follow the master.logs file."""
    system = platform.system()
    # print(str(LOG_FILE))
    if system == "Windows":
        # Open a new CMD window and redirect output away from Git Bash
        subprocess.Popen([
            'start', '', str(GIT_BASH_PATH), 
            '-c', f'tail -F {str(LOG_FILE)}'
        ], shell=True)

    elif system in ["Linux", "Darwin"]:  # Darwin = macOS
        #o Open a new terminal and run 'tail -f' on the log file
        subprocess.Popen([
            "x-terminal-emulator", "-e", f"bash -c 'tail -f {LOG_FILE}'"
        ])
    else:

        print("Unsupported OS. Unable to open log terminal.")

if __name__ == '__main__':
    # open_log_terminal()
    load_exporters()
    workbot_cli = WorkBotCLI()
    work_bot = workbot_cli.workbot


    welcome_screen = rf'''
    
 ██╗    ██╗ ██████╗ ██████╗ ██╗  ██╗██████╗  ██████╗ ████████╗
 ██║    ██║██╔═══██╗██╔══██╗██║ ██╔╝██╔══██╗██╔═══██╗╚══██╔══╝
 ██║ █╗ ██║██║   ██║██████╔╝█████╔╝ ██████╔╝██║   ██║   ██║   
 ██║███╗██║██║   ██║██╔══██╗██╔═██╗ ██╔══██╗██║   ██║   ██║   
 ╚███╔███╔╝╚██████╔╝██║  ██║██║  ██╗██████╔╝╚██████╔╝   ██║   
  ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝    ╚═╝   

                  Welcome to WorkBot CLI
            Automate Orders. Eliminate Tedium.

{work_bot.welcome_to_work()}
'''

    workbot_cli.start(welcome_screen)
