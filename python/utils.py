from __future__ import print_function
import sys

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    forward = dict(enums)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    enums['iteritems'] = forward.iteritems
    return type('Enum', (), enums)

def exit_with_error(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)
