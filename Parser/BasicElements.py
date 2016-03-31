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


from utils.exceptions import GenericError
from utils.annotations import virtual, overrides

import re

########## exceptions ############


class ElementTerminated(Exception):
    pass


class InvalidStructureError(GenericError):
    pass


class DelimiterError(GenericError):
    pass


class UnknownElementError(GenericError):
    def __init__(self, element_name):
        mesg = "Element '%s' is not defined" % (element_name)
        super(UnknownElementError, self).__init__(mesg)


######### Elements and ElementTree ############


class BasicElement(object):
    @virtual
    def parse_delimiter(self, delimiter):
        accepted_delims = r";"
        matches = re.match(accepted_delims, delimiter)
        if matches:
            raise ElementTerminated
        else:
            raise DelimiterError("don't know how to process delimiter",
                                 element=type(self).__name__, delimiter=delimiter)
    @virtual
    def parse_classes(self, classes):
        pass

    @virtual
    def parse_properties(self, defaultprop, properties):
        pass

    @virtual
    def setup_child_element_tree(self, children):
        pass


class ComplexElement(BasicElement):
    def __init__(self):
        self._child_element_tree = None

    @overrides(BasicElement)
    def parse_classes(self, classes):
        #check if ID is part of the classes
        ids = []
        classes = [cls for cls in classes if (lambda x: ids.append(x) and False if re.match(r"#[\w]+", cls) else True)(cls)]

        if len(ids) > 0:
            self.set_id(ids[-1])    # set the last ID of IDs

        self.add_classes(*classes)

    @overrides(BasicElement)
    def parse_properties(self, defaultprop, properties):
        self.add_properties(defaultprop, **properties)

    @overrides(BasicElement)
    def setup_child_element_tree(self, etree):
        """
        sets the list of children elements of this element.
        if one is already set, it throws an exception
        also, this marks the termination of element
        @param etree: child element-tree
        """
        if self._child_element_tree is not None:
            raise InvalidStructureError("element already has children elements set",
                                        element=type(self).__name__)

        assert(type(etree) is list)

        self._child_element_tree = etree
        raise ElementTerminated(self)

    @virtual
    def grant_visit(self, visitor):
        """
        allows a visitor class to visit the node/element and do its processing
        @param visitor: the visitor class (should be derived from ElementTreeVisitor)
        """
        #assert(issubclass(type(visitor), ElementTreeVisitor))

        #visit the contained element
        visitor.visit(self)

        #and then visit the child element tree, if there is one
        if self._child_element_tree is not None:
            visitor.going_deeper()

            for elm in self._child_element_tree:
                elm.grant_visit(visitor)

            visitor.coming_back_up()


class StringElement(BasicElement):
    """
    StringElement is just that - a string.
    it doesnt have classes or properties or child element tree
    """
    def __init__(self, content):
        assert(content is not None)

        self.content = content

    @overrides(BasicElement)
    def parse_classes(self, classes):
        assert(type(classes) is list)
        raise InvalidStructureError("strings cannot have classes",
                                    string=self.content,
                                    classes="(%s)" % ', '.join(classes or ['']))

    @overrides(BasicElement)
    def parse_properties(self, defaultprop, properties):
        assert(type(properties) is dict)
        props = "[%s]" % ', '.join([defaultprop or ''] +
                                   ["%s: %s" % (key, value)
                                    for key, value in (properties or {}).items()])
        raise InvalidStructureError("strings cannot have properties",
                                    string=self.content, properties=props)

    @overrides(BasicElement)
    def setup_child_element_tree(self, children):
        raise InvalidStructureError("strings cannot have children elements",
                                    string=self.content)