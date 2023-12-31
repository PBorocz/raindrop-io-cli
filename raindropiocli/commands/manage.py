"""Add/Create a new file-based bookmark to Raindrop."""
import csv
from datetime import datetime
from pathlib import Path
from typing import Final

from humanize import naturaltime
from prompt_toolkit.completion import WordCompleter
from rich.table import Table

from raindropiopy import Raindrop
from raindropiopy.models import Collection, CollectionRef
from raindropiocli import (
    COLOR_TABLE_COLUMN_1,
    COLOR_TABLE_COLUMN_2,
    PROMPT_STYLE,
    options_as_help,
    prompt,
)
from raindropiocli.models.event_loop import EventLoop
from raindropiocli.models.spinner import Spinner


def get_total_raindrops(collections: list[Collection, CollectionRef]) -> int:
    """Return the total number of Raindrops *associated with named collections*."""
    return sum([collection.count for collection in collections if collection.id > 0])


def _show_status(el: EventLoop) -> None:
    """UI Controller for displaying current status."""
    human_diff = naturaltime(datetime.utcnow() - el.state.refreshed)
    table = Table(title=None, show_header=False)
    table.add_column("parm", style=COLOR_TABLE_COLUMN_1, no_wrap=True)
    table.add_column("data", style=COLOR_TABLE_COLUMN_2, justify="right")
    table.add_row("Active User", f"{el.state.user.full_name}")
    table.add_row("Raindrops", f"{get_total_raindrops(el.state.collections):,d}")
    table.add_row("Collections", f"{len(el.state.collections):,d}")
    table.add_row("Tags", f"{len(el.state.tags):,d}")
    table.add_row("As Of", f"{human_diff}")
    el.console.print(table)


def _show_collections(el: EventLoop) -> None:
    """Displaying current collections."""
    total = get_total_raindrops(el.state.collections)
    table = Table(title=None, show_header=False)
    table.add_column("Collection", style=COLOR_TABLE_COLUMN_1, no_wrap=True)
    table.add_column("Count", style=COLOR_TABLE_COLUMN_2, justify="right")
    for collection in el.state.collections:
        table.add_row(collection.title, f"{collection.count:,d}")
    table.add_section()
    table.add_row("Total Raindrops", f"{total:,d}")
    el.console.print(table)


def _show_tags(el: EventLoop) -> None:
    """Display current tags."""
    total = 0
    table = Table(title=None, show_header=False)
    table.add_column("Tag", style=COLOR_TABLE_COLUMN_1, no_wrap=True)
    for tag in el.state.tags:
        table.add_row(tag)
        total += 1
    table.add_section()
    table.add_row(f"{total:,d}")
    el.console.print(table)


def show_help(el: EventLoop) -> None:
    """Display help about this set of commands."""
    el.console.print("status      : Show current status of Raindrop API connection.")
    el.console.print(
        "collections : Display the Collections currently defined along with count of Raindrops in each.",
    )
    el.console.print("tags        : Display the Tags currently defined.")
    el.console.print(
        "refresh     : Refresh the list of Collections & Tags from Raindrop.",
    )


def _do_export(el: EventLoop) -> None:
    """Export the all the meta-data of the Raindrops."""

    def raindrop_csv_encoder(raindrop: Raindrop) -> dict:
        """Convert a Raindrop instance to a dict suitable for csv export."""
        return_ = dict()
        for attr, _ in raindrop.__annotations__.items():
            return_[attr] = getattr(raindrop, attr)

        # Handle some specific conversions:
        collection = el.state.find_collection_by_id(raindrop.collection.id)
        return_["collection"] = collection.title if collection else raindrop.collection.id
        return_["tags"] = ",".join(raindrop.tags)
        return_["user"] = raindrop.user.id
        print(type(raindrop.collection))
        del return_["media"]

        return return_

    # Export on a collection by collection basis..
    with Spinner("Querying all Raindrops..."):
        raindrops = []
        for collection in el.state.collections:
            for raindrop in Raindrop.search(el.state.api, collection=collection):
                raindrops.append(raindrop)

    with Spinner("Exporting all Raindrops..."):
        fn_export = Path("~/Downloads/raindrop-io-py.csv").expanduser()
        fieldnames = {
            "collection",
            "cover",
            "created",
            "domain",
            "excerpt",
            "id",
            "last_update",
            "link",
            "tags",
            "title",
            "type",
            "user",
        }
        with open(fn_export, "w") as fh_csv:
            writer = csv.DictWriter(
                fh_csv,
                fieldnames=fieldnames,
                extrasaction="ignore",
            )
            writer.writeheader()
            writer.writerows([raindrop_csv_encoder(raindrop) for raindrop in raindrops])
    print(f"Wrote {len(raindrops)} entries to {fn_export}.")


def process(el: EventLoop) -> None:
    """Controller for "manage" portion of the Raindrop CLI."""
    while True:
        options: Final = (
            "status",
            "collections",
            "tags",
            "export",
            "refresh",
            "back/.",
        )
        completer: Final = WordCompleter(options)
        options_title: Final = options_as_help(options)
        while True:
            el.console.print(options_title)
            response = el.session.prompt(
                prompt(("manage",)),
                completer=completer,
                style=PROMPT_STYLE,
                complete_while_typing=True,
                enable_history_search=False,
            )
            # Special cases...
            if response.casefold() in ("back", "b", "."):
                return None
            elif response.casefold() in ("help", "h"):
                show_help(el)

            # Normal cases
            elif response.casefold() in ("?",):
                el.console.print(options_title)
            elif response.casefold() in ("status", "s"):
                _show_status(el)
            elif response.casefold() in ("export", "e"):
                _do_export(el)
            elif response.casefold() in ("collections", "c"):
                _show_collections(el)
            elif response.casefold() in ("tags", "t"):
                _show_tags(el)
            elif response.casefold() in ("refresh", "r"):
                el.state.refresh()
            else:
                el.console.print(
                    f"Sorry, must be one of {options_title}",
                )
