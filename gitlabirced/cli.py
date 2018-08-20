# -*- coding: utf-8 -*-

"""Console script for gitlabirced."""
import signal
import sys
import click

import yaml

from .irc_client import connect_networks
from .http_server import MyHTTPServer, RequestHandler


@click.command()
@click.argument('config-file', nargs=1)
def main(config_file):
    """Console script for gitlabirced."""
    click.echo(config_file)

    try:
        with open(config_file, 'r') as stream:
            config = yaml.load(stream)
            print("Configuration loaded %s" % config)
    except yaml.YAMLError as exc:
        print(exc)
        sys.exit(1)
    except IOError:
        print("File %s not found" % config_file)
        sys.exit(3)

    all_bots = connect_networks(config['networks'])

    hooks = parse_hooks(config['hooks'])
    token = config['token']

    def run_server(addr, port):
        """Start a HTTPServer which waits for requests."""
        httpd = MyHTTPServer(token, hooks, all_bots, (addr, port),
                             RequestHandler)
        httpd.serve_forever()
        print('serving')

    print('going to execute server')
    run_server('0.0.0.0', 1337)

    def signal_handler(sig, frame):
        print('You pressed Ctrl+C!')
        for b in all_bots:
            all_bots[b]['bot'].reactor.disconnect_all()
            all_bots[b]['process'].terminate()
        click.Abort()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    print('Press Ctrl+C')

    return 0


def parse_hooks(hooks):
    print('parsing hooks')
    print(hooks)
    return hooks


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
