# -*- coding: utf-8 -*-
"""Functions for creating API rules.

For example usage, see make() or rules_demo/test1.py
"""
__copyright__ = 'Copyright (c) 2019, Utrecht University'
__license__   = 'GPLv3, see LICENSE'

import rule
import log
from error import *

import json
import jsonutil
import error
import inspect
import traceback
from collections import OrderedDict

class Result(object):
    def __init__(self, data=None, status='ok', info=None):
        self.status      = status
        self.status_info = info
        self.data        = data

    @staticmethod
    def ok(data=None):
        return Result('ok', info, data)

    def as_dict(self):
        return OrderedDict([('status',      self.status),
                            ('status_info', self.status_info),
                            ('data',        self.data)])


class Error(Result, UUError):
    """Error with descriptive (user-readable) message.

    Returned/raised by API functions to produce informative error output.
    """
    def __init__(self, name, info, debug_info=None, data=None):
        self.name = name
        self.info = info
        self.debug_info = debug_info

        Result.__init__(self, data, 'error_'+name, info)
        UUError.__init__(self, 'error_'+name)

    def __str__(self):
        return '{}: {}'.format(self.name, self.info)


def _api(f):
    """Turn a Python function into a basic API function.

    By itself, this wrapper is not very useful, as the resulting function is
    not callable by rules. See make() below for a method to turn the
    result into one or two rules, with different calling conventions.

    api() creates a function that takes a JSON string as an argument,
    and translates it to function arguments for `f`. The JSON input is
    automatically validated for required/optional arguments, based on f()'s
    signature.

    f()'s returned vaule may be of any JSON-encodable type, and will be stored
    in the 'data' field of the returned JSON. If f() returns or raises an
    error, the 'status' and 'status_info' fields are populated (non-null)
    instead.
    """
    # Determine required and optional argument names from the function signature.
    a_pos, a_var, a_kw, a_defaults = inspect.getargspec(f)
    a_pos = a_pos[1:] # ignore callback/context param.

    required = set(a_pos if a_defaults is None else a_pos[:-len(a_defaults) ])
    optional = set([]    if a_defaults is None else a_pos[ -len(a_defaults):])

    # If the function accepts **kwargs, we do not forbid extra arguments.
    allow_extra = a_kw is not None

    # XXX Debug {{{
    # print('api-ify   {}'.format(f.__name__))
    # print('spec:     {}'.format(inspect.getargspec(f)))
    # print('required: {}'.format(required))
    # print('optional: {}{}'.format(optional, ' + kwargs' if allow_extra else ''))
    # print('defaults: {}'.format(a_defaults))
    # }}}

    def wrapper(ctx, inp):
        """A function that receives a JSON string and calls a wrapped function with unpacked arguments."""
        # Validate input string: is it a valid JSON object?
        try:
            data = jsonutil.parse(inp)
            if type(data) is not OrderedDict:
                raise jsonutil.ParseError('Argument is not a JSON object')
        except jsonutil.ParseError:
            log._write(ctx, 'Error: API rule <{}> called with invalid JSON argument'
                            .format(f.__name__))
            return Error('badrequest', 'An internal error occurred').as_dict()

        # Check that required arguments are present.
        for param in required:
            if param not in data:
                log._write(ctx, 'Error: API rule <{}> called with missing <{}> argument'
                                .format(f.__name__, param))
                return Error('badrequest', 'An internal error occurred').as_dict()

        # Forbid arguments that are not in the function signature.
        if not allow_extra:
            for param in data:
                if param not in required | optional:
                    log._write(ctx, 'Error: API rule <{}> called with unrecognized <{}> argument'
                                    .format(f.__name__, param))
                    return Error('badrequest', 'An internal error occurred').as_dict()

        # Try to run the function with the supplied arguments,
        # catching any error it throws.
        try:
            log._write(ctx, '-> {}()'.format(f.__name__))
            result = f(ctx, **data)
            if type(result) is Error:
                raise result # Allow api.Errors to be either raised or returned.

            elif not isinstance(result, Result):
                # No error / explicit status info implies 'OK' status.
                result = Result(result)

            return result.as_dict()
        except Error as e:
            # A proper caught error with name and message.
            if e.debug_info is None:
                log._write(ctx, 'Error: API rule <{}> failed with error <{}>'.format(f.__name__, e))
            else:
                log._write(ctx, 'Error: API rule <{}> failed with error <{}> (debug info follows below this line)\n{}'.format(f.__name__, e, e.debug_info))
            return e.as_dict()
        except Exception as e:
            # An uncaught error. Log a trace to aid debugging.
            log._write(ctx, 'Error: API rule <{}> failed with uncaught error (trace follows below this line)\n{}'
                            .format(f.__name__, traceback.format_exc()))
            return Error('internal', 'An internal error occurred').as_dict()

    return wrapper


def make():
    """Create API functions callable as iRODS rules.

    This translate between a Python calling convention and the iRODS rule
    calling convention.

    An iRODS rule is created that receives a JSON string and prints the
    result of f, JSON-encoded to stdout. If an error occurs, the output JSON
    will contain "error" and "error_message" items.

    Synopsis:

        __all__ = ['api_uu_ping']

        @api.make()
        def api_uu_ping(ctx, foo):
            if foo != 42:
                return api.Error('not_allowed', 'Ping is not allowed')
            log.write(ctx, 'ping received')
            return foo

        # this returns {"status": "ok", "status_info": null, "data": 42}
        # when called as api_uu_ping {"foo": 42}
    """

    def deco(f):
        # The "base" API function, that does handling of arguments and errors.
        base = _api(f)

        # The JSON-in, JSON-out rule.
        return rule.make(inputs=[0], outputs=[],
                         transform=json.dumps, handler=rule.Output.STDOUT)(base)

    return deco