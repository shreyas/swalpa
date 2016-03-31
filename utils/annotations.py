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


import inspect

class OverrideError(Exception):
    pass


def virtual(func):
    """
    annotation to set a method for override,
    any method, that doesnt have this annotation, cannot be overridden with @overrides(cls) annotation
    """
    # hack to throw exception if the virtual function is not inside a class
    # ref: http://stackoverflow.com/questions/8793233/python-can-a-decorator-determine-if-a-function-is-being-defined-inside-a-class
    frames = inspect.stack()
    if not (len(frames) > 2 and frames[2][4][0].strip().startswith('class ')):
        raise OverrideError("function '%s' should be inside a class to be virtual" % func.__name__);

    func.func_doc = "@virtual available for override\n" + (func.func_doc or '')
    func.__virtual__ = True
    return func


def overrides(cls):
    def overrider(func):
        # hack to throw exception if the function requesting override, is not inside a class
        # ref: http://stackoverflow.com/questions/8793233/python-can-a-decorator-determine-if-a-function-is-being-defined-inside-a-class
        frames = inspect.stack()
        if not (len(frames) > 2 and frames[2][4][0].strip().startswith('class ')):
            raise OverrideError("function '%s' should be inside class" % func.__name__);

        clsmethodname, clsmethod = inspect.getmembers(cls, lambda m: inspect.ismethod(m) and m.__name__ == func.__name__)[0]
        #if not (func.__name__ in map(lambda f: f[0], inspect.getmembers(cls, inspect.ismethod))):
        if not clsmethod:
            raise OverrideError("%s not in %s class" % (func.__name__, cls.__name__))

        #check if the method is declared virtual anywhere in the MRO
        isvirtual = False
        for class_in_mro in inspect.getmro(cls):
            methodname, method = inspect.getmembers(class_in_mro, lambda m: inspect.ismethod(m) and m.__name__ == func.__name__)[0]
            if (hasattr(method, '__virtual__') and method.__virtual__):
                isvirtual = True
                break

        if not isvirtual:
            raise OverrideError("%s::%s is not virtual (hint: use @virtual)" % (cls.__name__, clsmethodname))

        #if all safety checks are passing, then mark the docstring accordingly
        func.func_doc = "@overriding %s::%s" % (cls.__name__, func.__name__)

        return func

    return overrider



##### TEST CODE #######
# class myclass(object):
#     def __init__(self):
#         pass
#
#     @virtual
#     def add(self):
#         pass
#
#     @virtual
#     def delete(self):
#         pass
#
#     def edit(self):
#         pass
#
#
# class anotherclass(myclass):
#     @overrides(myclass)
#     def delete(self):
#         pass
#
#     @overrides(myclass)
#     def add(self):
#         pass
#
#
# @virtual
# def myfunc():
#     """
#     this is the
#     docstring
#     of my func
#     """
#     print("inside myfunc")
#
#
# #@overrides(myclass)
# def add():
#     """i am anotherfunc"""
#     print("inside anotherfunc")
#
#
# if __name__ == "__main__":
#     print(myfunc.func_doc)
#     print(add.func_doc)
#     print(anotherclass.delete.func_doc)
