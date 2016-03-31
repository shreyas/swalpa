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


class GenericError(Exception):
    def __init__(self, mesg=None, **kwargs):
        #super(GenericError, self).__init___(mesg)
        self.mesg = mesg
        self.params = kwargs
        self.message = self.get_message()

    def update(self, **kwargs):
        self.params.update(kwargs)
        self.message = self.get_message()

    def get_message(self):
        return self.mesg + " " + ', '.join(["%s: %s" % (key, str(value)) for key, value in self.params.items()])

    def __str__(self):
        return type(self).__name__ + " - " + self.get_message()
