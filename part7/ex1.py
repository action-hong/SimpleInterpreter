INTEGER, PLUS, MINUS, MUL, DIV, EOF, LPAREN, RPAREN = {
    "INTEGER", "PLUS", "MINUS", "MUL", "DIV", "EOF", "LPAREN", "RPAREN"
}

from calc7 import Token, Lexer, Parser, AST, BinOp, Num, NodeVisitor, Interpreter
import unittest
class RPNInterpreter(Interpreter):
  def visit_BinOp(self, node):
    return str(self.visit(node.left)) + ' ' + str(self.visit(node.right)) + ' ' + node.op.value

def infix2postfix(s):
    lexer = Lexer(s)
    parser = Parser(lexer)
    translator = RPNInterpreter(parser)
    translation = translator.interpret()
    return translation

# input:  (5 + 3) * 12 / 3
# output: 5 3 + 12 * 3 /
class Infix2PostfixTestCase(unittest.TestCase):

    def test_1(self):
        self.assertEqual(infix2postfix('2 + 3'), '2 3 +')

    def test_2(self):
        self.assertEqual(infix2postfix('2 + 3 * 5'), '2 3 5 * +')

    def test_3(self):
        self.assertEqual(
            infix2postfix('5 + ((1 + 2) * 4) - 3'),
            '5 1 2 + 4 * + 3 -',
        )

    def test_4(self):
        self.assertEqual(
            infix2postfix('(5 + 3) * 12 / 3'),
            '5 3 + 12 * 3 /',
        )


if __name__ == '__main__':
    unittest.main()