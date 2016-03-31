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


import re
import fileinput

from SwalpaObjectModel import DelimiterToken, TextToken


class Lexer(object):
    def __init__(self):
        self.tokenizer_regex = r"""([()[\]{};,]|(?<!(?<!\\)\\)['"]|[:]\s+|\s+)"""
        self.swalpa_file = None

        self.tokenizer = re.compile(self.tokenizer_regex, re.MULTILINE)


    def tokenize(self, file):
        """
        generates one token at a time from a given swalpa file
        @file filename/path of the swalpa file
        """
        self.swalpa_file = file

        for line_number, line in enumerate(fileinput.input(self.swalpa_file), start=1):
            tokens = self.tokenizer.split(line)
            if not tokens:
                print("info: couldn't tokenize input file - " + file)

            for token in tokens:
                yield (DelimiterToken if self.tokenizer.match(token) else TextToken)(token, line_number)





