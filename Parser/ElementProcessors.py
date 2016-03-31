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


from ElementTree import ElementTreeVisitor
from utils.annotations import virtual, overrides
from Elements.element import element


class ElementProcessor(ElementTreeVisitor):
    """
    templatizes all element processors that run on element tree as visitors
    """
    @overrides(ElementTreeVisitor)
    def visit(self, element):
        return self.process(element)

    @virtual
    def process(self, element):
        """
        @param element: element to visit and process
        """
        pass


class PrintElementName(ElementProcessor):
    """
    test ElementProcessor to print the element hierarchy and
    verify the visitor infrastructure works correctly
    """
    @overrides(ElementProcessor)
    def initialize(self):
        self.tabbing = 0

    @overrides(ElementProcessor)
    def going_deeper(self):
        self.tabbing += 1

    @overrides(ElementProcessor)
    def coming_back_up(self):
        self.tabbing -= 1 if self.tabbing > 0 else 0

    @overrides(ElementProcessor)
    def process(self, element):
        print("\t" * self.tabbing + type(element).__name__)


class VerifyParentageAndConfigure(ElementProcessor):
    """
    verify that each element is residing under a desired parentage
    and then configures the element if there is any parent specific configuration
    """
    @overrides(ElementProcessor)
    def initialize(self):
        # a chain of parent elements
        self.parentage = [element]  #start with a root element as a placeholder
        self.last_processed_element = None

    @overrides(ElementProcessor)
    def going_deeper(self):
        if self.last_processed_element is not None:
            self.parentage.append(type(self.last_processed_element))

    @overrides(ElementProcessor)
    def coming_back_up(self):
        self.parentage.pop()

    @overrides(ElementProcessor)
    def process(self, elem):
        self.last_processed_element = elem

        #if len(self.parentage) > 0:
        if issubclass(type(elem), element):
            elem.validate_parentage(self.parentage[1:]) #avoid sending in the root element
            elem.configure_for_parent_element(self.parentage[-1])


