import argparse

from config import connex_app


def get_args():
    ap = argparse.ArgumentParser('Process human language sentences into JSON.')

    # Add args
    ap.add_argument('-p', '--port', type=int,
                    help="Port number to run this service on.",
                    default=5013)

    a = ap.parse_args()

    return a


if __name__ == "__main__":
    args = get_args()

    connex_app.run(debug=True, port=args.port)

