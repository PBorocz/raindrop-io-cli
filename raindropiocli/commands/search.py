"""Create a new Raindrop bookmark."""

from prompt_toolkit.completion import WordCompleter

# from raindropiopy import Collection, CollectionRef, Raindrop
from raindropiocli import PROMPT_STYLE, prompt
from raindropiocli.models.search_state import SearchState
from raindropiocli.commands import get_collection_s
from raindropiocli.commands.help import help_search
from raindropiocli.commands.view_edit import process as process_view_edit
from raindropiocli.models.event_loop import EventLoop
from raindropiocli.models.spinner import Spinner


def __prompt_search_terms(el: EventLoop) -> tuple[bool, str | None]:
    """Prompt for all user response to perform a search, or None if user quits.

    Returns:
    - bool -> True if done with search?
    - str  -> Optional term(s) to search on
    """
    # What tag(s) to do allow for autocomplete?
    search_tags = [f"#{tag}" for tag in el.state.tags]
    completer = WordCompleter(search_tags)
    while True:
        response = el.session.prompt(
            prompt(("search> term(s)?",)),
            completer=completer,
            style=PROMPT_STYLE,
            complete_while_typing=True,
            enable_history_search=False,
        )
        if response == "?":
            help_search(el)
        elif response == ".":
            return True, None
        elif response:
            return False, response

        # Otherwise, we fall through and try again, we need *some* search terms (even if "*" for wildcard)


def _prompt_search(el: EventLoop) -> SearchState | None:
    """Prompt for all responses necessary for a search, ie. terms and collection(s).

    Returns SearchState for a new search to be performed or None if we're done.
    """
    quit, search_term_s = __prompt_search_terms(el)
    if quit:
        return None

    collection_s = get_collection_s(el, ("search", "collection(s)?"))
    if collection_s == ".":
        return None

    # Holds both search request information as well as search *results*
    if collection_s:
        collection_s = collection_s.split()
    return SearchState(search=search_term_s, collection_s=collection_s)


def process(el: EventLoop) -> None:
    """Top-level UI Controller for searching for bookmark(s)."""
    while True:
        search_state: SearchState | None = _prompt_search(el)

        if search_state is None:
            return None  # We're REALLY done..

        ################################################################################
        # Do the query and display the results, transferring control over to view/edit
        ################################################################################
        with Spinner(search_state.spinner_text()):
            search_state.query(el)

        # Display the results of the search, ie, id, title, *tags...
        search_state.display_results(el)

        if search_state.results:
            if not process_view_edit(el, search_state):
                return None

        # Otherwise, we go back an try to do another search..
