"""Top level command-line interface controller."""
import importlib
import os
from pathlib import Path
from typing import Final

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from rich.console import Console

from raindropiocli import (
    PROMPT_STYLE,
    goodbye,
    make_bold,
    options_as_help,
    prompt,
)
from raindropiocli.models.raindrop_state import RaindropState


# Utility method to return the command-history file path for the user
# (creating directories if necessary)
def _get_user_history_path() -> Path:
    history_path = Path("~/.config/raindropiopy").expanduser()
    history_path.mkdir(parents=True, exist_ok=True)

    history_file = history_path / Path(".cli_history")
    if not history_file.exists():
        open(history_file, "a").close()
    return history_file


class EventLoop:
    """Top-level command-line interface controller/command-loop."""

    def _display_startup_banner(self) -> None:
        banner: str = "Welcome to Raindrop-io-py\n"
        welcome: str = (
            f"""{make_bold('<tab>')} to show options/complete | """
            f"""{make_bold('help')} for help | """
            f"""{make_bold('Ctrl-D')}, {make_bold('exit')} or '{make_bold('.')}' to exit."""
        )
        # We can't use self.console.print here as any the special
        # characters figlet creates will be interpreted by Rich.
        # print(Figlet(font="thin").renderText(banner))
        self.console.print(banner)
        self.console.print(welcome)

    def __init__(
        self,
        args,
        input_=None,
        output=None,
    ) -> None:
        """Configure our interface components and display our startup banner."""
        # Setup our outgoing Rich console.
        args_console = {"record": True}

        if args.testing:
            # Turn *off* our special terminal handling..
            args_console["color_system"] = None
            os.environ["TERM"] = "dumb"

        self.console = Console(**args_console)

        # Setup our prompt_toolkit session (with optional overrides for intput and output obo testing):
        if input_ is None and output is None:
            args_session = dict(history=FileHistory(_get_user_history_path()))
        else:
            args_session = dict(input=input_, output=output)
        self.session = PromptSession(**args_session)

        self.state: None  # Will be populated when we start our event loop.

        self._display_startup_banner()

    def get_console_output(self):
        """For testing purposes, when we have output going to a StringIO, we need a way of getting it back out."""
        return self.console.file.getvalue()

    def iteration(self):
        """Run a single iteration of our command/event-loop."""
        options: Final = ("search", "create", "manage", "exit/.")
        options_title: Final = options_as_help(options)
        self.console.print(options_title)

        response = self.session.prompt(
            prompt(),
            completer=WordCompleter(options),
            style=PROMPT_STYLE,
            complete_while_typing=True,
            enable_history_search=False,
        )

        if response.casefold() in ("exit", "e", "quit", "q", "."):
            raise KeyboardInterrupt  # Quick way out...

        elif response.casefold() in ("?",):
            # FIXME: This should be a longer help text here
            # (since we print the options at the top of each
            # iteration already)
            self.console.print(options_title)
            return

        # We have a valid command, bring in the right module (yes, statically)
        # and dispatch appropriately.
        process_method = None
        if response.casefold() in ("help", "h"):
            module = "raindropiocli.commands.help"

        elif response.casefold() in ("search", "s"):
            module = "raindropiocli.commands.search"

        elif response.casefold() in ("create", "c"):
            module = "raindropiocli.commands.create"

        elif response.casefold() in ("manage", "m"):
            module = "raindropiocli.commands.manage"

        else:
            # Else case here doesn't matter as if process_method isn't set,
            # we'll simply show the list of commands at the top of the next
            # iteration.
            return

        module_ = importlib.import_module(module)
        method_name = "process"
        process_method = getattr(module_, method_name)
        process_method(self)

    def go(self, state: RaindropState) -> None:
        """Save state and run the top-level menu/event loop prompts."""
        self.state = state

        while True:
            try:
                self.iteration()
            except (KeyboardInterrupt, EOFError):
                goodbye(self.console)
                return
