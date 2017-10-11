import argparse


def parse_arguments(argv):
    p = argparse.ArgumentParser(description='achihuo_mini')

    p.add_argument('xxx', type=str, nargs='*', help='command and args')
    p.add_argument('-s', '--slave', action='store_true', help='slave')
    p.add_argument('-o', '--others', nargs='*', action='store', help='other arguments')

    args = p.parse_args(argv)

    return args
