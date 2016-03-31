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


from utils.annotations import virtual
from ElementExceptions import *
from Parser.BasicElements import ComplexElement

class element(ComplexElement):

    def __init__(self):
        self.classes = set()
        self.properties = {}

        self.__default_property = None
        self.element_id = None

        #a desired parent element chain goes from outside to inside
        #multiple such chains are allowed
        self.__desired_parent_element_chains = []

        #any parent-element specific config for this element
        self.__parent_specific_config = dict()

        #Format: {'templating': { 'begin' : template, 'end': template} }
        self.templates = dict()

        self.construct()
        self.setup_templates()

    def add_classes(self, *classes, **modifiers):
        """
        @classes list of classes to put on the element
        @purge_previous True if we want to purge any previously added classes
        """
        allowed_modifiers = {'purge_previous': lambda value: self.classes.clear() if value else None}

        #process any modifiers that have been specified
        [allowed_modifiers[m](modifiers[m]) for m in modifiers if m in allowed_modifiers]

        self.classes.update(classes)

    def add_properties(self, *default, **properties):
        #if default value is specified, but not default property has been specified
        #for this element, throw an exception
        default = [df for df in default if df is not None]

        if len(default) > 0:
            if not self.__default_property:
                raise NoDefaultPropertyException(self.__class__.__name__)

            #else just set the value on the default property
            self.properties[self.__default_property] = default[0]

        self.properties.update({key.replace('_', '-').replace('--', '_'): value for key, value in properties.items()})

    def set_id(self, element_id):
        """
        this is #id ID to be put on the HTML element, represented by this element
        """
        self.element_id = element_id

    def generate_element_id_str(self):
        if not self.element_id:
            return self.element_id

        return 'id="{0:s}"'.format(self.element_id if self.element_id.startswith('#') else ('#' + self.element_id))

    def generate_classes_str(self):
        return u"class=\"{0:s}\"".format(' '.join(self.classes)) if len(self.classes) > 0 else ""

    def generate_properties_str(self):
        return ' '.join(['%s="%s"' % (key, value) for key, value in self.properties.items()])

    @virtual
    def setup_templates(self):
        """
        used to setup templates for different templating languages.
        for now we will be using Mako for templating.
        so subclasses will use setup_templates to setup their own
        templates for HTML generation.
        """
        pass

    @virtual
    def get_html_template(self, templating='mako'):
        """
        head method to get HTML template of elements
        works as a generator. first it generates top part, yields it, and then
        it generates the bottom part.
        this is so that the child-element-tree contents can be fit inside this element.
        what an idea, sir ji!!
        """
        yield self.templates[templating]['begin']
        yield self.templates[templating]['end']


    @virtual
    def construct(self):
        """
        override for element construction:
        - add classes
        - add properties
        """
        pass

    def set_default_property(self, property_name):
        """
        set default property for the element
        this enables anonymous property definitions, like this -
        element (#id classes) [default_property] [property_name: property_value] { content }
        """
        self.__default_property = property_name.replace('_', '-').replace('--', '_')

    def add_desired_parent_elements_chain(self, *element_chain):
        """
        sets the desired elements under which this element should go
        if the element doesnt have this desired parentage, it will throw exception

        multiple such parent-chains can be specified for a given element, so that
        that element can be allowed to exist multiple parent chains

        @param element_chain: one such desired parent element chain
        """
        for parent_element in element_chain:
            #validate the classes in the chain indeed belong to the 'element' group of classes
            if not self.is_valid_element_class(parent_element):
                raise InvalidParentElement(parent_element)

        self.__desired_parent_element_chains.append(element_chain)

    def validate_parentage(self, parent_chain):
        """
        verify that this element can survive under a given parent_chain
        it will raise an InvalidParentageError otherwise

        @param parent_chain: element chain representing parentage of *this* element
        @return: True if a valid parent chain
        """

        if len(self.__desired_parent_element_chains) == 0:
            return

        for desired_chain in self.__desired_parent_element_chains:
            #if desired chain is longer than this parent chain,
            #we need to look if there is some other desired chain that
            #fits this parent chain
            if len(desired_chain) > len(parent_chain):
                continue

            #this is an interesting technique to determine overlap between two
            #ordered lists, which, by the way, I came up with.
            #first we convert the list into a map with key being the list elements, and
            #value being their position in the list. Complexity: O(n)
            #then we just go over the 2nd list and check if the indexes for its elements as per the
            #map that we created for the first list, are ordered.
            pc_map = {ele: idx for idx, ele in enumerate(parent_chain)}
            max_idx = reduce(lambda idx, elem: pc_map[elem] if elem in pc_map and pc_map[elem] >= idx else len(parent_chain) + 1,
                             desired_chain, 0)

            #max index is within the length of parent element, that means all elements from
            #desired_chain were resolved one after the other within the parent_chain
            #that means we have a match, and the parent_chain is valid
            if max_idx < len(parent_chain):
                return

        #if none of the desired_parent_chains validate the parent_chain
        #well, we have a problem. we throw an exception
        raise InvalidParentage("Element '{0:s}' can't be used under '{1:s}' "
                               "hierarchy".format(type(self).__name__,
                                                  ' -> '.join([pe.__name__
                                                               for pe in parent_chain])))

    @staticmethod
    def is_valid_element_class(elementcls):
        """
        checks if a given class is from the 'element' hierarchy of classes
        inspect.getmro() can throw an exception, that the caller needs to watch out for
        @elementcls class object to be checked for validity
        """
        if not issubclass(elementcls, element):
            raise InvalidParentElement(elementcls)

        return True

    def set_parent_specific_config(self, parent_element, func):
        """
        if this element falls under some specific 'parent_element',
        run this 'func' to do any parent_element specific configuration
        """
        if not self.is_valid_element_class(parent_element):
            raise InvalidParentElement(parent_element)

        if parent_element not in self.__parent_specific_config:
            self.__parent_specific_config[parent_element] = []

        self.__parent_specific_config[parent_element].append(func)


    def configure_for_parent_element(self, parent_element):
        """
        the parser will pass parent elements one by one to *this* function
        if there is any parent_specific_configuration, this is where it will get done
        """
        #only valid 'element' type of classes is what we expect here
        #anything else, and we throw exception
        if not self.is_valid_element_class(parent_element):
            raise InvalidParentElement(parent_element)

        if parent_element in self.__parent_specific_config:
            [func() for func in self.__parent_specific_config[parent_element]]