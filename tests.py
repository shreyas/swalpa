from __future__ import print_function

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
from Elements import *


ElementsCache = {}
# iterate over modules from the Elements package
for mod in filter(lambda x: x.startswith('Elements.'), sys.modules):
    # iterate over classes from the modules from the Elements package
    for name, obj in inspect.getmembers(sys.modules[mod], inspect.isclass):
        # if the class is derived from, but not equal to, 'element' class, we pick it
        if 'element' in [x.__name__ for x in inspect.getmro(obj)][1:]:
            ElementsCache[name] = obj

map(lambda x: print(x, ElementsCache[x]()), ElementsCache.keys())
