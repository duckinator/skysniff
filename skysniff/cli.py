from dataclasses import dataclass
from enum import StrEnum, auto
from pathlib import Path
from typing import Annotated
import logging
import os
import sys

import dykes

from . import NWSApi

class ForecastPeriod(StrEnum):
    DAILY = auto()
    HOURLY = auto()

@dataclass
class SkysniffCli:
    """
    Fetch and display an hourly or daily forecast for a given address.
    """
    period: Annotated[ForecastPeriod, ', '.join([e.value for e in ForecastPeriod])]
    ask: Annotated[dykes.StoreTrue, "ask for address"]
    verbose: dykes.Count


def get_config_file():
    xdg_config = os.environ.get("XDG_CONFIG_HOME", Path.home().joinpath('.config'))
    return Path(xdg_config).joinpath('skysniff', 'address.txt')

def get_address(ask: bool) -> str:
    config_file = get_config_file()
    if not ask and config_file.exists():
        return config_file.read_text()

    return input("Address: ")


def main(argv=None):
    """Entrypoint for the script."""
    if argv is None:
        argv = sys.argv

    args = dykes.parse_args(SkysniffCli, args=argv[1:])
    period = args.period
    ask = args.ask

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    address = get_address(ask)

    nws = NWSApi()
    forecast_fn = getattr(nws, period)

    print(forecast_fn(address).render_text())
