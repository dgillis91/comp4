from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import argparse
from fsa import initialize_scanner
from parser import parser_func
from tree import print_tree
from staticsem import semantic_analysis
from generator import code_generator
from writer import StandardOutTargetWriter, FileTargetWriter


parser = argparse.ArgumentParser()
parser.add_argument('--path', '-p', help='path to file. do not include ext.',
                    dest='path', type=str, default=None)
parser.add_argument('--std-out', '-s', help='Will print to std-out if specified',
                    dest='is_std_out', action='store_true')
parser.add_argument('--target', '-t', help='path to the target file. '
                    'if --std-out is used, this argument is ignored.',
                    dest='target', type=str, default=None)
parser.add_argument('--debug', '-d', help='if specified, will print tree',
                    dest='debug', action='store_true')
args = parser.parse_args()

scanner = initialize_scanner(args.path)

tree = parser_func(scanner)

if args.debug:
    print_tree(tree)

if semantic_analysis(tree):
    pass

if args.is_std_out:
    writer = StandardOutTargetWriter()
else:
    if args.target is None:
        if args.path is None:
            filepath = 'kb.asm'
        else:
            filepath = '{}.asm'.format(args.path)
    else:
        filepath = args.target
    writer = FileTargetWriter(filepath)

code_generator(writer, tree)
