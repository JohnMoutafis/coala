import re
import sys
from importlib import import_module
from inspect import getmembers
from pkgutil import iter_modules
from types import ModuleType

from .base import aspectbase
from .exceptions import (AspectTypeError, AspectNotFoundError,
                         MultipleAspectFoundError)
from .meta import aspectclass
from .taste import Taste, TasteError

# already import Root here to make it available in submodules that define
# `Root.subaspect`s, which get imported in wrapper `aspectsModule.__init__`
# before this module gets replaced with that wrapper in sys.modules
from .root import Root


__all__ = ['Root', 'Taste', 'TasteError',
           'aspectclass', 'aspectbase', 'AspectTypeError',
           'AspectNotFoundError', 'MultipleAspectFoundError']


class aspectsModule(ModuleType):
    """
    A special module wrapper for ``coalib.bearlib.aspects``, allowing
    case-insensitive aspect lookup by name via direct indexing :)

    >>> import coalib.bearlib.aspects

    >>> coalib.bearlib.aspects['Metadata']
    <aspectclass 'Root.Metadata'>

    >>> coalib.bearlib.aspects['commitmessage']
    <aspectclass 'Root.Metadata.CommitMessage'>

    >>> coalib.bearlib.aspects['shortlog.colonExistence']
    <aspectclass 'Root.Metadata.CommitMessage.Shortlog.ColonExistence'>
    """

    def __init__(self, module):
        """
        Take over all members from original `module` object and load all
        direct ``Root.subaspect`` classes from their corresponding submodules
        (all submodules starting with uppercase letters), and add them as
        members to this wrapper module.
        """
        super().__init__(module.__name__)
        self.__dict__.update(getmembers(module))
        for _, submodname, _ in iter_modules(module.__path__):
            if submodname[0].isupper():
                submod = import_module('.' + submodname, module.__name__)
                subaspect = getattr(submod, submodname)
                setattr(self, submodname, subaspect)

    def get(self, aspectname):
        """
        Search and get an aspectclass from string of full or partial
        qualified name of the aspect. Similiar to ``__getitem__``, but doesn't
        raise exception for trying to search non existing aspect.

        :param aspectname:
            Name of the aspect that should be searched.
        :raise MultipleAspectFoundError:
            When multiple aspects with same name was found.
        :return:
            An aspectclass or None.
        """
        try:
            return self[aspectname]
        except AspectNotFoundError:
            return None

    def __getitem__(self, aspectname):
        regex = re.compile('(^|\.)%s$' % aspectname.lower())
        matches = []

        def search(aspects):
            """
            Recursively search in `aspects` for those matching
            case-insensitively the given ``aspectname``.
            """
            for aspect in aspects:
                if regex.search(aspect.__qualname__.lower()):
                    matches.append(aspect)
                if aspect.subaspects:
                    search(aspect.subaspects.values())

        search([Root])
        if not matches:
            raise AspectNotFoundError(aspectname)

        if len(matches) > 1:
            raise MultipleAspectFoundError(aspectname, matches)

        return matches[0]


# replace original module with wrapper
sys.modules[__name__] = aspectsModule(sys.modules[__name__])
