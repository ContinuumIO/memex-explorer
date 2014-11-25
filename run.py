from __future__ import absolute_import, division, print_function

import argparse

from app import app


def parse_args():
    parser = argparse.ArgumentParser(description="MEMEX VIEWER")

    parser.add_argument("-s", "--show", action="store_true",
                        help="Auto-raise app in a browser window")

    return parser.parse_args()


def main():
    args = parse_args()
    app.config.from_pyfile('config.py')

    if args.show:
        if app.config['DEBUG']:
            url = "http://%s:%s/" % (app.config['HOST'], app.config['PORT'])
            print(url)
        else:
            import webbrowser
            webbrowser.open(url)

    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])


if __name__ == "__main__":
    main()
