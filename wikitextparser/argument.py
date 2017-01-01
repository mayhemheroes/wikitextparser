﻿"""Define the Argument class."""


from .wikitext import SubWikiText


class Argument(SubWikiText):

    """Create a new Argument Object.

    Note that in mediawiki documentation `arguments` are (also) called
    parameters. In this module the convention is like this:
    {{{parameter}}}, {{t|argument}}.
    See https://www.mediawiki.org/wiki/Help:Templates for more information.
    """

    @property
    def name(self) -> str:
        """Return argument's name.

        For positional arguments return the position as a string.

        """
        pipename, equal, value = self._atomic_partition(b'=')
        if equal:
            return pipename[1:].decode()
        # positional argument
        position = 1
        _bytearray = self._bytearray
        for ss, se in self._type_to_spans[self._type][:self._index]:
            # Make sure the span is not closed.
            if ss < se:
                # Todo: Which one is better: ord('=') or b'='?
                equal_index = _bytearray.find(b'=', ss, se)
                if equal_index == -1:
                    # A preceding positional argument is detected.
                    position += 1
                    continue
                # Todo: cache the results of the following code?
                in_subspans = self._in_atomic_subspans_factory(ss, se)
                while equal_index != -1:
                    if not in_subspans(equal_index):
                        # This is a keyword argument
                        break
                    # We don't care for this kind of equal sign.
                    # Look for the next one.
                    equal_index = _bytearray.find(b'=', equal_index + 1, se)
                else:
                    # All the equal signs where inside a subspan.
                    position += 1
        return str(position)

    @name.setter
    def name(self, newname: str) -> None:
        """Set the name for this argument.

        If this is a positional argument, convert it to keyword argument.

        """
        oldname = self.name
        if self.positional:
            self[0:1] = b'|' + newname.encode() + b'='
        else:
            # Todo: old name should be converted to bytes
            self[1:1 + len(oldname)] = newname.encode()

    @property
    def positional(self) -> bool:
        """Return True if there is an equal sign in the argument else False."""
        if self._atomic_partition(b'=')[1]:
            return False
        else:
            return True

    @positional.setter
    def positional(self, to_positional: bool) -> None:
        """Change to keyword or positional accordingly.

        Raise ValueError if setting positional argument to keyword argument.

        """
        pipename, equal, value = self._atomic_partition(b'=')
        if equal:
            # Keyword argument
            if to_positional:
                del self[1:len(pipename + b'=')]
            else:
                return
        elif to_positional:
            # Positional argument. to_positional is True.
            return
        else:
            # Positional argument. to_positional is False.
            raise ValueError(
                'Converting positional argument to keyword argument is not '
                'possible without knowing the new name. '
                'You can use `self.name = somename` instead.'
            )

    @property
    def value(self) -> str:
        """Return value of a keyword argument."""
        pipename, equal, value = self._atomic_partition(b'=')
        if equal:
            return value.decode()
        # Anonymous parameter
        return pipename[1:].decode()

    @value.setter
    def value(self, newvalue: str) -> None:
        """Assign the newvalue to self."""
        pipename, equal, value = self._atomic_partition(b'=')
        if equal:
            pnel = len(pipename + equal)
            self[pnel:pnel + len(value)] = newvalue.encode()
        else:
            self[1:len(pipename)] = newvalue.encode()
