#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import pprint
import logging
import inspect

_logger = None

def log(obj):
    _func = "[%s():%s] " % (inspect.stack()[1][3], inspect.stack()[1][2])
    global _logger
    if not _logger:
        _logger = logging.getLogger()
        s = logging.StreamHandler( sys.stderr )
        _logger.addHandler(s)
        _logger.setLevel(logging.DEBUG)
        s.setFormatter(logging.Formatter( '%(asctime)s %(levelname)s %(message)s' ) )

    _logger.debug(_func + str(obj))

def pp(obj):
    import re
    pp = pprint.PrettyPrinter(indent=4, width=160)
    str = pp.pformat(obj)
    return re.sub(r"\\u([0-9a-f]{4})", lambda x: unichr(eval("0x"+x.group(1))), str)
    
    # return eval("u''' %s '''" % str).strip()

def ppp(*objs):
    for obj in objs:
        print pp(obj)

def optparse(args):
    dict = {}
    prev = None
    for arg in args[1:]:
        if arg[0:1] == "-":
            if prev:
                dict[prev] = True
            prev = arg
        else:
            if prev:
                dict[prev] = arg
                prev = None
            else:
                # error
                pass
    if prev:
        dict[prev] = True

    return dict
