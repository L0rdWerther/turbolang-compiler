import sys
import os
from compiler import compile_file, compile_string

def print_usage():
    print('TurboLang: The High-Performance Compiler')
    print('Usage: python main.py [OPTIONS] [FILE]')
    print('\nOptions:')
    print('  -h, --help          Show this help message')
    print('  -v, --verbose       Enable verbose output')
    print('  -o, --output FILE   Write output to file')
    print('\nExamples:')
    print('  python main.py race_track.turbo')
    print('  python main.py -v race_track.turbo -o race_track.sam')

def main():
    verbose = False
    output_file = None
    input_file = None
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ['-h', '--help']:
            print_usage()
            return 0
        elif arg in ['-v', '--verbose']:
            verbose = True
        elif arg in ['-o', '--output']:
            if i + 1 < len(sys.argv):
                output_file = sys.argv[i + 1]
                i += 1
            else:
                print('Error: -o requires an argument')
                return 1
        elif not arg.startswith('-'):
            input_file = arg
        else:
            print(f'Unknown option: {arg}')
            return 1
        i += 1
    if not input_file:
        print('Error: No input file specified')
        print_usage()
        return 1
    if not os.path.exists(input_file):
        print(f'Error: File not found: {input_file}')
        return 1
    print(f'Warming up engine for {input_file}...')
    result = compile_file(input_file, verbose=verbose)
    if result.success:
        print('\n[CHECKERED FLAG] Compilation successful!')
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    f.write(result.output)
                print(f'Output written to {output_file}')
            except IOError as e:
                print(f'Error writing output file: {str(e)}')
                return 1
        else:
            print('\nGenerated Assembly:')
            print('=' * 60)
            print(result.output)
            print('=' * 60)
        return 0
    else:
        print(f'\nError: {result.error}')
        return 1
if __name__ == '__main__':
    sys.exit(main())
