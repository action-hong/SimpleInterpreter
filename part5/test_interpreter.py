import unittest


class LexerTestCase(unittest.TestCase):
    def makeLexer(self, text):
        from calc5 import Lexer
        lexer = Lexer(text)
        return lexer

    def test_lexer_integer(self):
        from calc5 import INTEGER
        lexer = self.makeLexer('234')
        token = lexer.get_next_token()
        self.assertEqual(token.type, INTEGER)
        self.assertEqual(token.value, 234)

    def test_lexer_mul(self):
        from calc5 import MUL
        lexer = self.makeLexer('*')
        token = lexer.get_next_token()
        self.assertEqual(token.type, MUL)
        self.assertEqual(token.value, '*')

    def test_lexer_div(self):
        from calc5 import DIV
        lexer = self.makeLexer(' / ')
        token = lexer.get_next_token()
        self.assertEqual(token.type, DIV)
        self.assertEqual(token.value, '/')


class InterpreterTestCase(unittest.TestCase):
    def makeInterpreter(self, text):
        from calc5 import Lexer, Interpreter
        lexer = Lexer(text)
        interpreter = Interpreter(lexer)
        return interpreter

    def test_expression1(self):
        interpreter = self.makeInterpreter('3')
        result = interpreter.expr()
        self.assertEqual(result, 3)

    def test_expression2(self):
        interpreter = self.makeInterpreter('7 + 5 * 2')
        result = interpreter.expr()
        self.assertEqual(result, 17)

    def test_expression3(self):
        interpreter = self.makeInterpreter('7 + 3 * (10 / (12 / (3 + 1) - 1))')
        result = interpreter.expr()
        self.assertEqual(result, 22)

    def test_expression4(self):
        interpreter = self.makeInterpreter('(1 + 2) * 3')
        result = interpreter.expr()
        self.assertEqual(result, 9)

    def test_expression5(self):
        interpreter = self.makeInterpreter('1 - 2 * 2')
        result = interpreter.expr()
        self.assertEqual(result, -3)

    def test_expression6(self):
        interpreter = self.makeInterpreter('(1 + 1) * ((2 - 3) - (4 - 2))')
        result = interpreter.expr()
        self.assertEqual(result, -6)

if __name__ == '__main__':
    unittest.main()
