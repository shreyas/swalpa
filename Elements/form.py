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


from element import element
from utils.annotations import overrides
from navbar import navbar

class form(element):
    @overrides(element)
    def construct(self):
        #add navbar-form class if form is setup inside a navbar
        self.set_parent_specific_config(navbar, lambda: self.add_classes('navbar-form'))

#     @overrides(element)
#     def setup_templates(self):
#         html_begin = r"""\
# <li ${element.generate_element_id_str()} ${element.generate_classes_str()}\
#  ${element.generate_properties_str()}>"""
#         html_end = r"""</li>"""
#
#         self.templates['mako']['begin'] = html_begin
#         self.templates['mako']['begin'] = html_end
