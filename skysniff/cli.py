import sys
from . import NWSApi


def main(argv=None):
    """Entrypoint for the script."""
    if argv is None:
        argv = sys.argv

    if len(argv) < 2 or len(argv) > 3:
        print("Usage: ./weather.py daily [ADDRESS]", file=sys.stderr)
        print("       ./weather.py hourly [ADDRESS]", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]
    if len(sys.argv) == 3:
        address = sys.argv[2]
    else:
        address = input("Address: ")

    nws = NWSApi()
    if command == 'daily':
        print(nws.forecast(address).render_text())
    elif command == 'hourly':
        print(nws.hourly(address).render_text())
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)
