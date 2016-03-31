# Copyright (c) 2016 Shreyas Kulkarni (shyran@gmail.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


#
# Swalpa Object Model API
#

import re
import string
from utils.annotations import *


########## Exceptions ###############

class SwalpaException(Exception):
    pass


class ContainerTerminated(Exception):
    """
    Terminating character of a container was received and the container
    was terminated
    """
    pass


class InvalidContainerHierarchy(Exception):
    def __init__(self, outer, inner):
        # if a token is passed, rather than a container, we show the line number and such details
        if issubclass(type(inner), Token):
            mesg = "found '%s' inside %s, at line %d" % (inner.get_token(),
                                                         type(outer).__name__,
                                                         inner.get_line_number())
        else:
            mesg = "found '%s' inside %s" % (inner.CONTAINER_START,
                                             type(outer).__name__)

        super(InvalidContainerHierarchy, self).__init__(mesg)


class InvalidTokenInContainer(Exception):
    def __init__(self, token, containerobj):
        mesg = "%s doesn't accept token '%s', at line %d" % (type(containerobj).__name__,
                                                             token.get_token(),
                                                             token.get_line_number())

        super(Exception, self).__init__(mesg)


class PropertyParsingError(SwalpaException):
    def __init__(self, mesg, property_group):
        message = "%s: %s" % (mesg, ' '.join(map(str, property_group)))
        super(SwalpaException, self).__init__(message)


class InvalidClassError(SwalpaException):
    def __init__(self, class_item):
        message = "Invalid class declaration at line %d" % (class_item.get_line_number())
        super(SwalpaException, self).__init__(message)


############# Tokens ###############

class Token(object):
    def __init__(self, token, line_no):
        self.token = token
        self.default_container = None
        self.line_number = line_no

    def get_token(self):
        return self.token

    def get_default_container(self):
        return self.default_container

    def set_default_container(self, container):
        if not container:
            return

        assert issubclass(type(container), Container)

        self.default_container = container

    def get_line_number(self):
        """
        returns line number in the swalpa file, where this token was found
        """
        return self.line_number

    def has_default_container(self):
        return self.default_container is not None

    def __str__(self):
        return self.get_token()

    def get_contents(self):
        return self.get_token()


class TextToken(Token):
    pass


class DelimiterToken(Token):
    pass


############# Containers and ContainerFactory ###############


class ContainerFactory(object):
    def __init__(self):
        self.containers = {}

    def register_container(self, containercls):
        """
        register a container with the factory
        """
        assert issubclass(containercls, Container)

        self.containers[containercls.__name__] = containercls
        # print("is type(%s) == type(Container)")

    def get_container(self, symbol_or_token):
        """
        invokes the factory method on each of the registered container,
        if a match is found, returns an object of the container
        @symbol_or_token the symbol or token to run the factory method regex against (type: Token)
        @return container object for matched container
        """

        assert(issubclass(type(symbol_or_token), Token))

        for value in self.containers.values():
            if value.factory_method(symbol_or_token):
                container = value()
                container.CONTAINER_START = symbol_or_token.get_token()
                container.container_start_line_number = symbol_or_token.get_line_number()

                return container


# module level object as an application level singleton
container_factory = ContainerFactory()


# decorator to register a class with the container factory
def container(cls):
    container_factory.register_container(cls)
    return cls


class Container(object):
    token_regex = r"[\w\-]+"

    @classmethod
    def factory_method(cls, symbol_or_token):
        assert (issubclass(type(symbol_or_token), Token))
        return re.match(cls.token_regex, symbol_or_token.get_token())

    def __init__(self):
        self.children = []
        self.current_token_handler = None

        self.CONTAINER_START = None     # to be set by ContainerFactory when initializing the container
        self.container_start_line_number = -1 # where does the container start
        self.terminator_token = "\W"    # needs to be specified by derived classes
        self.__is_terminated = False    # will be set to true when a terminator token is received

        self.initialize()               # initialize anything that subclasses want to set

    @virtual
    def initialize(self):
        """
        hook for subclasses to inialize themselves
        """
        pass

    def digest_token(self, token):
        """
        passes the token through children till it gets processed
        """
        assert(issubclass(type(token), Token))

        if self.current_token_handler:
            try:
                # if we already have a token handlers, just pass on the token
                self.current_token_handler.digest_token(token)
            except ContainerTerminated:
                self.append_child(self.current_token_handler)
                self.current_token_handler = None
        else:
            # if we are the last link in the token-handling relay race, well process the token
            self.process_token(token)

    @virtual
    def process_token(self, token):
        """
        process the token.
        if it has a default container, set it up, if it's acceptable.
        if it's a delimiter, append it as a child if it's acceptable and not ignored
        if it's text, append it as a child
        """
        if token.has_default_container():
            if self.is_acceptable_container(type(token.get_default_container())):
                self.current_token_handler = token.get_default_container()
            else:
                raise InvalidContainerHierarchy(self, token)
        else:
            if self.is_ignored_token(token):
                return

            if not self.is_acceptable_token(token):
                raise InvalidTokenInContainer(token, self)

            if self.is_terminator(token):
                raise ContainerTerminated

            self.append_child(token)

    @virtual
    def append_child(self, child, **params):
        self.children.append(child)

    def toString(self):
        return " <" + type(self).__name__ + "  " + ' '.join([str(token) for token in self.children]) + "> "

    def __str__(self):
        return self.toString()

    @virtual
    def is_acceptable_token(self, token):
        return True

    @virtual
    def is_terminator(self, token):
        return re.match(self.terminator_token, token.get_token())

    @virtual
    def is_ignored_token(self, token):
        #by default we dont accept spaces
        return not len(token.get_token()) or re.match(r"[\s\n\r]+", token.get_token())

    @virtual
    def is_acceptable_container(self, containercls):
        return True

    @virtual
    def get_contents(self):
        """
        get contents inside the container
        contents will vary for different containers
        """
        pass

    def get_line_number(self):
        return self.container_start_line_number


@container
class StringContainer(Container):
    token_regex = r"[\"']"

    # we dont ignore anything in a string
    @overrides(Container)
    def is_ignored_token(self, token):
        return False

    @overrides(Container)
    def is_terminator(self, token):
        return(re.match(type(self).token_regex, token.get_token()) and
               token.get_token() == self.CONTAINER_START)

    @overrides(Container)
    def process_token(self, token):
        """
        token is processed differently for StringContainer.
        anything and eveything is part of the string until we hit the terminator ["']
        """
        if self.is_terminator(token):
            raise ContainerTerminated

        if self.is_ignored_token(token):
            return

        self.children.append(token)

    @overrides(Container)
    def get_contents(self):
        return '"' + ''.join([str(token) for token in self.children]) + '"'


@container
class ClassContainer(Container):
    token_regex = r"\("

    @overrides(Container)
    def initialize(self):
        self.terminator_token = r"\)"

    @overrides(Container)
    def is_acceptable_container(self, containercls):
        # we dont accept any containers inside class containers
        return False

    @overrides(Container)
    def is_acceptable_token(self, token):
        # no delimiters accepted inside class container
        if type(token) is DelimiterToken:
            # if the token has a default handler, we might ignore it
            # since the container acceptor will decide it
            return any([token.has_default_container(),
                       self.is_terminator(token),
                       self.is_ignored_token(token)])

        return True

    @overrides(Container)
    def get_contents(self):
        classes = []

        for child in self.children:
            # we only entertain Text and Strings inside class containers
            if not type(child) == TextToken or type(child) == StringContainer:
                raise InvalidClassError(child)

            classes.append(child.get_contents())

        return classes


@container
class PropertyContainer(Container):
    token_regex = r"\["

    @overrides(Container)
    def initialize(self):
        self.terminator_token = r"\]"

    @overrides(Container)
    def is_acceptable_container(self, containercls):
        # we dont accept any containers inside properties containers (except StringContainer)
        return containercls is StringContainer

    @overrides(Container)
    def is_acceptable_token(self, token):
        # accepted_tokens_regex = r",|:\s*"
        rejected_tokens_regex = r";"

        if type(token) is DelimiterToken:
            # if the token has a default handler, we might ignore it
            # since the container acceptor will decide it
            return not re.match(rejected_tokens_regex, token.get_token())

        return True

    @overrides(Container)
    def get_contents(self):
        """
        get properties from the container
        """
        properties = {}
        default_property = None

        prop_groups = []
        current = []
        for item in self.children:
            # if it's comma, add __current to property groups
            if type(item) is DelimiterToken:
                if item.get_token().strip() == ',' and len(current) > 0:
                    prop_groups.append(current)
                    current = []
                    continue

            # otherwise just feed the item to __current
            if issubclass(type(item), Container) or type(item) == TextToken:
                current.append(item.get_contents())
            else:
                current.append(item)

        if current and len(current) > 0:
            prop_groups.append(current)

        # basic validation on property groups: all lenghts should be either 1 or 3
        # if 1, it's default property
        # if 3, it's key-value pair property
        for grp in prop_groups:
            if len(grp) == 1:
                default_property = grp[0]
            elif len(grp) == 3:
                if not type(grp[1]) == DelimiterToken:
                    raise PropertyParsingError("Unknwon delimiter '%s'" % grp[1].strip(), grp)
                if grp[1].get_token().strip() != ':':
                    raise PropertyParsingError("Unknown delimiter '%s'" % grp[1].get_token().strip(), grp)
                else:
                    properties[grp[0]] = grp[2]
            else:
                raise PropertyParsingError("Unable to parse", grp)

        return default_property, properties


@container
class ContentContainer(Container):
    token_regex = r"\{"

    @overrides(Container)
    def initialize(self):
        self.terminator_token = r"\}"

    @overrides(Container)
    def get_contents(self):
        # return [x.get_contents() for x in self.children]
        return self.children


############# Swalpa Object Model Builder ###############

class SOMBuilder:
    """
    Swalpa Object Model Builder

    """
    def __init__(self, container_fac=container_factory):
        self.containerFactory = container_fac

        # a little convoluted way of getting SOMRoot element from container factory, but
        # worth it, since container factory can have logic on top of just creating an object
        # so we source our root element - ContentContainer - from the factory
        self.SOMroot = self.containerFactory.get_container(DelimiterToken(re.search(ContentContainer.token_regex,
                                                                                    string.punctuation).group(),
                                                                          0))

    def get_root_element(self):
        return self.SOMroot

    def process_token(self, token):
        # set the default container, if any, on the token
        token.set_default_container(self.containerFactory.get_container(token))

        # then process the token
        try:
            self.SOMroot.digest_token(token)
        except ContainerTerminated:
            print("debug: SOMBuilder complete. File syntax verified. Mandal aabhari aahe.")
