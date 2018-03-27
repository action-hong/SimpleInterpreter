INTEGER, PLUS, MINUS, MUL, DIV, EOF, LEFT_PAREN, RIGHT_PAREN = {
  "INTEGER", "PLUS", "MINUS", "MUL", "DIV", "EOF", "LEFT_PAREN", "RIGHT_PAREN"
}

DICT = {
  '+': PLUS,
  '-': MINUS,
  '*': MUL,
  '/': DIV,
  '(': LEFT_PAREN,
  ')': RIGHT_PAREN
}

class Token(object):
  def __init__(self, type, value):
    self.type = type
    self.value = value

  def __str__(self):
    return 'Token({type}, {value})'.format(
      type=self.type,
      value=repr(self.value)
    )

  def __repr__(self):
    return self.__str__()

class Lexer(object):
  def __init__(self, text):
    self.text = text
    self.pos = 0
    self.current_char = self.text[self.pos]

  def error(self):
    raise Exception('invalid character')

  def advance(self):
    self.pos += 1
    if self.pos > len(self.text) - 1:
      self.current_char = None
    else:
      self.current_char =  self.text[self.pos]

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
      c = self.current_char

      if c.isspace():
        self.skip_whitespace()
        continue
      
      if c.isdigit():
        return Token(INTEGER, self.integer())

      if c in DICT.keys():
        self.advance()
        return Token(DICT[c], c)
      
      self.error()
    
    return Token(EOF, None)

class Interpreter(object):
  def __init__(self, lexer):
    self.lexer = lexer
    self.current_token = self.lexer.get_next_token()

  def error(self):
    raise Exception('invalid token')
  
  def eat(self, token_type):
    if self.current_token.type == token_type:
      self.current_token = self.lexer.get_next_token()
    else:
      self.error()
  
  def factor(self):
    if self.current_token.type == INTEGER:
      result = self.current_token
      self.eat(INTEGER)
      return result.value
    elif self.current_token.type == LEFT_PAREN:
      self.eat(LEFT_PAREN)
      result = self.expr()
      self.eat(RIGHT_PAREN)
      return result
    self.error()

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


      