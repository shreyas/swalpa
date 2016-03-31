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
# Swalpa
#
# This is the orchestrator
#
# It receives the file name as command line arg
# Passes that file to the Lexer for tokenizing
# The tokens received from the Lexer are then passed on to the SOMBuilder for building SOM
# The SOM thus built, is then passed to ElementTreeBuilder to process it further and build and ElementTree
# Then some basic structural and validation rules are run atop the ElementTree
# Once those rules are run, and the tree is clean, it then juices the HTML milk out of it.
# SWEET!!!
#


from optparse import OptionParser

from Parser import Lexer
from Parser import SOMBuilder
from Parser import ElementTree
from Parser.ElementProcessors import VerifyParentageAndConfigure, PrintElementName


def main():
    # parse command line args
    parser = OptionParser()
    parser.add_option("-o", "--output", dest="outputfile", help="output file")
    cmd_opts, cmd_args = parser.parse_args()

    lexer = Lexer()
    somBuilder = SOMBuilder()

    # try:
    for token in lexer.tokenize(cmd_args[0]):
        # print("processing %s: '%s'" %(type(token).__name__, token.get_token()))
        somBuilder.process_token(token)

    elementTree = ElementTree(somBuilder.get_root_element().get_contents())
    elementTree.grant_visit(PrintElementName())
    # elementTree.grant_visit(VerifyParentageAndConfigure())
    # except Exception as e:
    #     print("error: " + str(e))


if __name__ == "__main__":
    main()
