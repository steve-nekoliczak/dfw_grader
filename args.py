import argparse

from config import port


def get_args():
    ap = argparse.ArgumentParser('Grader for German exercises from de_exercise.')

    # Add args
    ap.add_argument('-d', '--debug',
                    action='store_true',
                    help="Enable debugging mode.")

    ap.add_argument('-p', '--port', type=int,
                    help="Port number to run this service on.",
                    default=port)

    return ap.parse_args()
