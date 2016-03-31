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


import sys
import inspect

from BasicElements import *
from SwalpaObjectModel import TextToken, DelimiterToken
from SwalpaObjectModel import ClassContainer, PropertyContainer, ContentContainer, StringContainer
from utils.annotations import virtual
from Elements import *


class ElementFactory():
    """
    the element factory keeps a cache of element names and their objects

    it prepares the element cache dynamically from Elements package via reflection

    it doesn't need any element registration as such; as long as a class derives from
    'element' class, it's in the business, and will get picked by element factory

    the factory generates BasicElement s based on the input
    """
    def __init__(self):
        #setup the elements cache first
        self.ElementsCache = {}
        self.setup_elements_cache()

    def setup_elements_cache(self):
        """
        this is the magic behind automatic preparation of elements cache
        it picks up all classes from Elements package, that are derived from
        'element' class
        """
        #iterate over modules from the Elements package
        for mod in filter(lambda x: x.startswith('Elements.'), sys.modules):
            #iterate over classes from the modules from the Elements package
            for name, obj in inspect.getmembers(sys.modules[mod], inspect.isclass):
                #if the class is derived from, but not equal to, 'element' class, we pick it
                if 'element' in [x.__name__ for x in inspect.getmro(obj)][1:]:
                    self.ElementsCache[name] = obj

    def get_element(self, item):
        """
        return a BasicElement derivative, based on the type of item
        @param item: either a TextToken or a StringContainer (comes from the SOM)
        @returns:   ComplexElement if item is a TextToken and element by that name is defined.
                    raises an UnknownElementError otherwise.
                    StringElement if item is a StringContainer
                    Raises a RuntimeError if item's type is none of these.
        """
        if type(item) is TextToken:
            try:
                return self.ElementsCache[item.get_contents()]()
            except KeyError:
                raise UnknownElementError(item.get_contents())

        elif type(item) is StringContainer:
                return StringElement(item.get_contents())

        raise RuntimeError("ElementFactory cannot create element from '%s(%s) at %d'" % (
                    item.get_contents() if hasattr(item, 'get_content') else str(item),
                    type(item).__name__, item.get_line_number() if hasattr(item, 'get_line_number') else -1))


#global singleton for element factory
elementFactory = ElementFactory()


class ElementTree(object):
    """
    the element tree which will be a recursive tree strcuture to represent the
    swalpa file in terms of BasicElement nodes
    """
    def __init__(self, items):
        """
        element tree kick-off point
        this is where the element-tree buildup starts

        you collect the root SOM node from the SOMBuilder, and pass its
        contents to initialize an element tree.

        it kicks off the build and parse cycle of the element tree from SOM root

        @param items: list of items that are to be children of the root element
        """

        assert(type(items) is list)

        self.root = []  # root element
        self.__current = None
        self.add_element(items[0])

        map(self.parse, items[1:])

        if self.__current is not None:
            self.root.append(self.__current)
            self.__current = None

    def add_element(self, item):
        """
        adds a new BasicElement derivative to the ElementTree

        sources the BasicElement from ElementFactory by sending over the item.

        if it's currently processing any BasicElement that hasn't terminated yet,
        then it's a structural integrity issue, and results into an InvalidStructureError
        """
        element = elementFactory.get_element(item)
        if self.__current is not None:
            # we are not yet done with previous element to deal with a new one
            raise InvalidStructureError("attempt to create a new element, before completing previous one.",
                                        incomplete_element=type(self.__current).__name__,
                                        new_element=type(element).__name__,
                                        line_number=item.get_line_number())
        self.__current = element

    def parse(self, item):
        """
        the meat and potato of the element tree
        this method decides what to do based on the type of item that's been sent to parse
        @param item: item to parse (comes from SOM)
        """
        try:
            #TextToken and StringContainer begets a 'BasicElement' creation
            if type(item) is TextToken or type(item) is StringContainer:
                self.add_element(item)

            # a delimiter on the other hand, can be ignored, or used to terminate an element
            elif type(item) is DelimiterToken:
                if self.__current is None:
                    return

                self.__current.parse_delimiter(item.get_contents())

            # if current is null, and we are trying to add secondary items,
            # we cannot digest those, so raise errors
            if self.__current is None:
                raise InvalidStructureError("Attempt to add structure without specifying element",
                                            line_number=item.get_line_number(),
                                            structure=type(item).__name__)

            # a class container brings in classes and IDs for the element
            elif type(item) is ClassContainer:
                self.__current.parse_classes(item.get_contents())

            # properties container brings in properties
            elif type(item) is PropertyContainer:
                defprop, properties = item.get_contents()
                self.__current.parse_properties(defprop, properties)

            # a container represents a child element tree
            elif type(item) is ContentContainer:
                if len(item.get_contents()) > 0:
                    child_elem_tree = ElementTree(item.get_contents())
                    self.__current.setup_child_element_tree(child_elem_tree.root)
                raise ElementTerminated

        except ElementTerminated:
            self.root.append(self.__current)
            self.__current = None

    def grant_visit(self, visitor):
        """
        grants visit to a ElementTreeVisitor class

        allows ElementTree traversal for any class, without it having to know
        the internal structure of ElementTree

        precaution: the element tree construction should be over before we can grant
            visit to a visitor. otherwise, the results may not be correct.

        @param visitor: visitor class - must be derived from ElementTreeVisitor
        """
        assert(issubclass(type(visitor), ElementTreeVisitor))

        #visitor.going_deeper()

        for basicElement in self.root:
            #this is just a safety catch. all elements in ElementTree have to be
            #some derivatives of BasicElement. any aberration indicates bug
            assert(issubclass(type(basicElement), BasicElement))

            basicElement.grant_visit(visitor)

        #visitor.coming_back_up()


class ElementTreeVisitor(object):
    """
    this class defines a visitor template to the element tree
    """
    def __init__(self):
        self.initialize()

    @virtual
    def initialize(self):
        """
        visitor initialization. dont override __init__. use this instead
        """
        pass

    @virtual
    def visit(self, element):
        """
        what do you want to do on visit
        """
        pass

    @virtual
    def going_deeper(self):
        """
        going one level deeper into the hierarchy
        """
        pass

    @virtual
    def coming_back_up(self):
        """
        coming back one level up in the hierarchy
        """
        pass
