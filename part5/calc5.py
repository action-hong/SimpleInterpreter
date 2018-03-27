INTEGER, PLUS, MINUS, MUL, DIV, EOF, LEFT_PAREN, RIGHT_PAREN = {
  "INTEGER", "PLUS", "MINUS", "MUL", "DIV", "EOF", "LEFT_PAREN", "RIGHT_PAREN"
}


class Token(object):
  def __init__(self, type, value):
    self.type = type
    self.value = value

  def __str__(self):
    return 'Token({type}, {value})'.format(
      type=self.type,
      value=self.value
    )

  def __repr__(self):
    return self.__str__()


class Lexer(object):
  def __init__(self, text):
    self.text = text
    self.pos = 0
    self.current_char = self.text[self.pos]

  def error(self):
    raise Exception('Invalid character')

  def advance(self):
    self.pos += 1
    if self.pos <= len(self.text) - 1:
      self.current_char = self.text[self.pos]
    else:
      self.current_char = None

  def skip_whitespace(self):
    while self.current_char is not None and self.current_char.isspace():
      self.advance()

  def integer(self):
    result = ''
    while self.current_char is not None and self.current_char.isdigit():
      result += self.current_char
      self.advance()
    return int(result)

  def get_next_token(self):
    while self.current_char is not None:

      if self.current_char.isspace():
        self.skip_whitespace()
        continue

      if self.current_char.isdigit():
        return Token(INTEGER, self.integer())

      if self.current_char == '+':
        self.advance()
        return Token(PLUS, '+')

      if self.current_char == '-':
        self.advance()
        return Token(MINUS, '-')

      if self.current_char == '*':
        self.advance()
        return Token(MUL, '*')

      if self.current_char == '/':
        self.advance()
        return Token(DIV, '/')

      if self.current_char == '(':
        self.advance()
        return Token(LEFT_PAREN, "(")
      
      if self.current_char == ')':
        self.advance()
        return Token(RIGHT_PAREN, ')')

      self.error()
    
    return Token(EOF, None)

class Interpreter(object):
  def __init__(self, lexer):
    self.lexer = lexer
    self.current_token = self.lexer.get_next_token()

  def error(self):
    raise Exception('Invalid syntax')

  def eat(self, token_type):
    if self.current_token.type == token_type:
      self.current_token = self.lexer.get_next_token()
    else:
      self.error()

  def factor(self):
    token = self.current_token
    if token.type == LEFT_PAREN:
      # 等式开始了, 必然当前这个符号是左括号
      self.eat(LEFT_PAREN)
      # 每一个括号内又是一个等式
      num = self.expr()
      # 等式结束了, 必然当前这个符号是右括号
      self.eat(RIGHT_PAREN)
      return num
    elif token.type == INTEGER:
      self.eat(INTEGER)
      return token.value
  
  def term(self):
    result = self.factor()
    while self.current_token.type in [MUL, DIV]:
      if self.current_token.type == MUL:
        self.eat(MUL)
        result = result * self.factor()
      elif self.current_token.type == DIV:
        self.eat(DIV)
        result = result / self.factor()
    
    return result

  def expr(self):

    result = self.term()
    while self.current_token.type in [PLUS, MINUS]:
      if self.current_token.type == PLUS:
        self.eat(PLUS)
        result = result + self.term()
      elif self.current_token.type == MINUS:
        self.eat(MINUS)
        result = result - self.term()
    
    return result

def main():
  while True:
    try:
      text = input('calc> ')
    except EOFError:
      break
    if not text:
      continue
    # text = '(1 + 2) * 3'
    lexer = Lexer(text)
    interpreter = Interpreter(lexer)
    result = interpreter.expr()
    print(result)

if __name__ == '__main__':
  main()