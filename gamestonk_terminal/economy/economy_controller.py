""" Econ Controller """
__docformat__ = "numpy"

import argparse
import os
from typing import List

from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.economy import (
    alphavantage_view,
    cnn_view,
    finnhub_view,
    finviz_view,
    fred_view,
    wsj_view,
)
from gamestonk_terminal.economy.report import report_controller
from gamestonk_terminal.helper_funcs import (
    check_positive,
    get_flair,
    parse_known_args_and_warn,
    valid_date,
)
from gamestonk_terminal.menu import session

# pylint: disable=R1710


class EconomyController:
    """Economy Controller"""

    d_GROUPS = {
        "sector": "Sector",
        "industry": "Industry",
        "basic materials": "Industry (Basic Materials)",
        "communication services": "Industry (Communication Services)",
        "consumer cyclical": "Industry (Consumer Cyclical)",
        "consumer defensive": "Industry (Consumer Defensive)",
        "energy": "Industry (Energy)",
        "financial": "Industry (Financial)",
        "healthcare": "Industry (Healthcare)",
        "industrials": "Industry (Industrials)",
        "real Estate": "Industry (Real Estate)",
        "technology": "Industry (Technology)",
        "utilities": "Industry (Utilities)",
        "country": "Country (U.S. listed stocks only)",
        "capitalization": "Capitalization",
    }

    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
    ]

    CHOICES_COMMANDS = [
        "feargreed",
        "events",
        "overview",
        "indices",
        "futures",
        "usbonds",
        "glbonds",
        "futures",
        "currencies",
        "search",
        "series",
        "valuation",
        "performance",
        "spectrum",
        "map",
        "rtps",
        "industry",
    ]

    CHOICES_MENUS = [
        "report",
    ]

    CHOICES += CHOICES_COMMANDS
    CHOICES += CHOICES_MENUS

    def __init__(self):
        """Constructor"""
        self.econ_parser = argparse.ArgumentParser(add_help=False, prog="economy")
        self.econ_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    @staticmethod
    def print_help():
        """Print help"""
        help_text = """https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/economy

>> ECONOMY <<

What do you want to do?
    cls           clear screen
    ?/help        show this menu again
    q             quit this menu, and shows back to main menu
    quit          quit to abandon program

CNN:
    feargreed     CNN Fear and Greed Index
Finnhub:
    events        economic impact events
Wall St. Journal:
    overview      market data overview
    indices       US indices overview
    futures       futures and commodities overview
    usbonds       US bonds overview
    glbonds       global bonds overview
    currencies    currencies overview
Finviz:
    map           S&P500 index stocks map
    valuation     valuation of sectors, industry, country
    performance   performance of sectors, industry, country
    spectrum      spectrum of sectors, industry, country
Alpha Vantage:
    rtps          real-time performance sectors
FRED:
    search        search FRED series notes
    series        plot series from https://fred.stlouisfed.org

>   report        generate automatic report
"""
        print(help_text)

    def switch(self, an_input: str):
        """Process and dispatch input

        Returns
        -------
        True, False or None
            False - quit the menu
            True - quit the program
            None - continue in the menu
        """

        # Empty command
        if not an_input:
            print("")
            return None

        (known_args, other_args) = self.econ_parser.parse_known_args(an_input.split())

        # Help menu again
        if known_args.cmd == "?":
            self.print_help()
            return None

        # Clear screen
        if known_args.cmd == "cls":
            os.system("cls||clear")
            return None

        return getattr(
            self, "call_" + known_args.cmd, lambda: "Command not recognized!"
        )(other_args)

    def call_help(self, _):
        """Process Help command"""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program"""
        return True

    def call_events(self, other_args: List[str]):
        """Process events command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="events",
            description="""
                Output economy impact calendar impact events. [Source: Finnhub]
            """,
        )
        parser.add_argument(
            "-c",
            "--country",
            action="store",
            dest="country",
            type=str,
            default="US",
            choices=["NZ", "AU", "ERL", "CA", "EU", "US", "JP", "CN", "GB", "CH"],
            help="Country from where to get economy calendar impact events",
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_positive,
            default=10,
            help="Number economy calendar impact events to display",
        )
        parser.add_argument(
            "-i",
            "--impact",
            action="store",
            dest="impact",
            type=str,
            default="all",
            choices=["low", "medium", "high", "all"],
            help="Impact of the economy event",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-c")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            finnhub_view.economy_calendar_events(
                country=ns_parser.country,
                num=ns_parser.num,
                impact=ns_parser.impact,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_feargreed(self, other_args: List[str]):
        """Process feargreed command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="feargreed",
            description="""
                Display CNN Fear And Greed Index from https://money.cnn.com/data/fear-and-greed/.
            """,
        )
        parser.add_argument(
            "-i",
            "--indicator",
            dest="indicator",
            required=False,
            type=str,
            choices=["jbd", "mv", "pco", "mm", "sps", "spb", "shd", "index"],
            help="""
                CNN Fear And Greed indicator or index. From Junk Bond Demand, Market Volatility,
                Put and Call Options, Market Momentum Stock Price Strength, Stock Price Breadth,
                Safe Heaven Demand, and Index.
            """,
        )
        parser.add_argument(
            "--export",
            choices=["png", "jpg", "pdf", "svg"],
            default="",
            type=str,
            dest="export",
            help="Export plot to png,jpg,pdf,svg file",
        )
        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-i")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            cnn_view.fear_and_greed_index(
                indicator=ns_parser.indicator,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_overview(self, other_args: List[str]):
        """Process overview command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="overview",
            description="Market overview. [Source: Wall St. Journal]",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            wsj_view.display_overview(
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_indices(self, other_args: List[str]):
        """Process indices command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="indices",
            description="US indices. [Source: Wall St. Journal]",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            wsj_view.display_indices(
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_futures(self, other_args: List[str]):
        """Process futures command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="futures",
            description="Futures/Commodities. [Source: Wall St. Journal]",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            wsj_view.display_futures(
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_usbonds(self, other_args: List[str]):
        """Process usbonds command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="usbonds",
            description="US Bonds. [Source: Wall St. Journal]",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            wsj_view.display_usbonds(
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_glbonds(self, other_args: List[str]):
        """Process glbonds command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="glbonds",
            description="Global Bonds. [Source: Wall St. Journal]",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            wsj_view.display_glbonds(
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_currencies(self, other_args: List[str]):
        """Process currencies command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="currencies",
            description="Currencies. [Source: Wall St. Journal]",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            wsj_view.display_currencies(
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_map(self, other_args: List[str]):
        """Process map command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="map",
            description="""
                Performance index stocks map categorized by sectors and industries.
                Size represents market cap. Opens web-browser. [Source: Finviz]
            """,
        )
        parser.add_argument(
            "-p",
            "--period",
            action="store",
            dest="s_period",
            type=str,
            default="1d",
            choices=["1d", "1w", "1m", "3m", "6m", "1y"],
            help="Performance period.",
        )
        parser.add_argument(
            "-t",
            "--type",
            action="store",
            dest="s_type",
            type=str,
            default="sp500",
            choices=["sp500", "world", "full", "etf"],
            help="Map filter type.",
        )
        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            finviz_view.map_sp500_view(
                period=ns_parser.s_period,
                map_type=ns_parser.s_type,
            )

        except Exception as e:
            print(e, "\n")

    def call_valuation(self, other_args: List[str]):
        """Process valuation command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="valuation",
            description="""
                View group (sectors, industry or country) valuation data. [Source: Finviz]
            """,
        )
        parser.add_argument(
            "-g",
            "--group",
            type=str,
            default="Sector",
            dest="group",
            help="Data group (sector, industry or country)",
            choices=list(self.d_GROUPS.keys()),
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-g")
                other_args = [other_args[0], " ".join(other_args[1:])]

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            finviz_view.view_group_data(
                s_group=self.d_GROUPS[ns_parser.group],
                data_type="valuation",
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_performance(self, other_args: List[str]):
        """Process performance command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="performance",
            description="""
                View group (sectors, industry or country) performance data. [Source: Finviz]
            """,
        )
        parser.add_argument(
            "-g",
            "--group",
            type=str,
            default="Sector",
            dest="group",
            help="Data group (sector, industry or country)",
            choices=list(self.d_GROUPS.keys()),
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-g")
                other_args = [other_args[0], " ".join(other_args[1:])]

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            finviz_view.view_group_data(
                s_group=self.d_GROUPS[ns_parser.group],
                data_type="performance",
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_spectrum(self, other_args: List[str]):
        """Process spectrum command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="spectrum",
            description="""
                View group (sectors, industry or country) spectrum data. [Source: Finviz]
            """,
        )
        parser.add_argument(
            "-g",
            "--group",
            type=str,
            default="sector",
            dest="group",
            help="Data group (sector, industry or country)",
            choices=list(self.d_GROUPS.keys()),
        )
        parser.add_argument(
            "--export",
            choices=["png", "jpg", "pdf", "svg"],
            default="",
            type=str,
            dest="export",
            help="Export plot to png,jpg,pdf,svg file",
        )
        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-g")
                other_args = [other_args[0], " ".join(other_args[1:])]

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            finviz_view.view_group_data(
                s_group=self.d_GROUPS[ns_parser.group],
                data_type="spectrum",
                export="",
            )
            # Due to Finviz implementation of Spectrum, we delete the generated spectrum figure
            # after saving it and displaying it to the user
            os.remove(ns_parser.group + ".jpg")

        except Exception as e:
            print(e, "\n")

    def call_rtps(self, other_args: List[str]):
        """Process rtps command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rtps",
            description="""
                Real-time and historical sector performances calculated from
                S&P500 incumbents. Pops plot in terminal. [Source: Alpha Vantage]
            """,
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            dest="raw",
            help="Only output raw data",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"]
            if "--raw" in other_args
            else ["png", "jpg", "pdf", "svg"],
            default="",
            type=str,
            dest="export",
            help="Export data to csv,json,xlsx or png,jpg,pdf,svg file",
        )
        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            alphavantage_view.realtime_performance_sector(
                raw=ns_parser.raw,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_series(self, other_args: List[str]):
        """Process series command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="series",
            description="""
                Display (multiple) series from https://fred.stlouisfed.org. [Source: FRED]
            """,
        )
        parser.add_argument(
            "-i",
            "--id",
            dest="series_id",
            required="-h" not in other_args,
            type=str,
            help="FRED Series from https://fred.stlouisfed.org. For multiple series use: series1,series2,series3",
        )
        parser.add_argument(
            "-s",
            dest="start_date",
            type=valid_date,
            default="2019-01-01",
            help="Starting date (YYYY-MM-DD) of data",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            dest="raw",
            help="Only output raw data",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"]
            if "--raw" in other_args
            else ["png", "jpg", "pdf", "svg"],
            default="",
            type=str,
            dest="export",
            help="Export data to csv,json,xlsx or png,jpg,pdf,svg file",
        )
        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-i")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            fred_view.display_series(
                series=ns_parser.series_id,
                start_date=ns_parser.start_date,
                raw=ns_parser.raw,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_search(self, other_args: List[str]):
        """Process search command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="search",
            description="Print series notes when searching for series. [Source: FRED]",
        )
        parser.add_argument(
            "-s",
            "--series",
            action="store",
            dest="series_term",
            type=str,
            required="-h" not in other_args,
            help="Search for this series term.",
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_positive,
            default=5,
            help="Maximum number of series notes to display.",
        )
        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-s")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            fred_view.notes(
                series_term=ns_parser.series_term,
                num=ns_parser.num,
            )

        except Exception as e:
            print(e, "\n")

    def call_report(self, _):
        """Process report command"""
        ret = report_controller.menu()

        if ret is False:
            self.print_help()
        else:
            return True


def menu():
    """Econ Menu"""

    econ_controller = EconomyController()
    econ_controller.print_help()

    # Loop forever and ever
    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in econ_controller.CHOICES}
            )

            an_input = session.prompt(
                f"{get_flair()} (economy)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (economy)> ")
        try:
            process_input = econ_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
