INTEGER       = 'INTEGER'
REAL          = 'REAL'
INTEGER_CONST = 'INTEGER_CONST'
REAL_CONST    = 'REAL_CONST'
PLUS          = 'PLUS'
MINUS         = 'MINUS'
MUL           = 'MUL'
INTEGER_DIV   = 'INTEGER_DIV'
FLOAT_DIV     = 'FLOAT_DIV'
LPAREN        = 'LPAREN'
RPAREN        = 'RPAREN'
ID            = 'ID'
ASSIGN        = 'ASSIGN'
BEGIN         = 'BEGIN'
END           = 'END'
SEMI          = 'SEMI'
DOT           = 'DOT'
PROGRAM       = 'PROGRAM'
VAR           = 'VAR'
COLON         = 'COLON'
COMMA         = 'COMMA'
EOF           = 'EOF'

class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        """String representation of the class instance.
        Examples:
            Token(INTEGER, 3)
            Token(PLUS, '+')
            Token(MUL, '*')
        """
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()

RESERVED_KEYWORDS = {
    'PROGRAM': Token('PROGRAM', 'PROGRAM'),
    'VAR': Token('VAR', 'VAR'),
    'DIV': Token('INTEGER_DIV', 'DIV'),
    'INTEGER': Token('INTEGER', 'INTEGER'),
    'REAL': Token('REAL', 'REAL'),
    'BEGIN': Token('BEGIN', 'BEGIN'),
    'END': Token('END', 'END'),
}

class Lexer(object):
  def __init__(self, text):
    self.text = text
    self.pos = 0
    self.current_char = self.text[self.pos]

  def error(self):
    raise Exception('Invalid character')

  def advance(self):
    self.pos += 1
    if self.pos > len(self.text) - 1:
      self.current_char = None
    else:
      self.current_char = self.text[self.pos]

  def peek(self, num = 1):
    peek_pos = self.pos + num
    if peek_pos > len(self.text) - 1:
      return None
    return self.text[peek_pos]

  def skip_whitespace(self):
    while self.current_char is not None and self.current_char.isspace():
      self.advance()

  def skip_comment(self):
    while self.current_char != '}':
      self.advance()
    self.advance()

  def number(self):
    result = ''
    while self.current_char is not None and self.current_char.isdigit():
      result += self.current_char
      self.advance()

    if self.current_char == '.':
      result += self.current_char
      self.advance()
      while self.current_char is not None and self.current_char.isdigit():
        result += self.current_char
        self.advance()

      token = Token('REAL_CONST', float(result))
    
    else:
      token = Token('INTEGER_CONST', int(result))
    
    return token

  def integer(self):
    result = ''
    while self.current_char is not None and self.current_char.isdigit():
      result += self.current_char
      self.advance()
    return int(result)

  def _id(self):
    result = ''
    while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
      result += self.current_char
      self.advance()
    
    # variables 和 reserved keywords 都是大小写不敏感的
    result = result.upper()
    token = RESERVED_KEYWORDS.get(result, Token(ID, result))
    return token
  
  def get_next_token(self):
    while self.current_char is not None:
      
      if self.current_char.isspace():
        self.skip_whitespace()
        continue

      if self.current_char == '{':
        self.advance()
        self.skip_comment()
        continue

      if self.current_char == ';':
          self.advance()
          return Token(SEMI, ';')

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
          return Token(FLOAT_DIV, '/')

      # pascal 使用div来做触发
      # if self.current_char == 'd' and self.peek() == 'i' and self.peek(2) == 'v':
      #     self.advance()
      #     self.advance()
      #     self.advance()
      #     return Token(DIV, 'div')

      if self.current_char == '(':
          self.advance()
          return Token(LPAREN, '(')

      if self.current_char == ')':
          self.advance()
          return Token(RPAREN, ')')

      if self.current_char == '.':
          self.advance()
          return Token(DOT, '.')

      # 变量名可以以_ 下划线开始
      # 由于 除法是div, 这部分逻辑必须放在下面, 否则可能吧div当成 变量了
      if self.current_char.isalpha() or self.current_char == '_':
        return self._id()

      if self.current_char.isdigit():
        return self.number()

      if self.current_char == ':' and self.peek() == '=':
        self.advance()
        self.advance()
        return Token(ASSIGN, ':=')

      if self.current_char == ':':
        self.advance()
        return Token(COLON, ':')

      if self.current_char == ',':
        self.advance()
        return Token(COMMA, ',')
      
      self.error()
    
    return Token(EOF, None)

class AST(object):
  pass

class Program(AST):
  def __init__(self, name, block):
    self.name = name
    self.block = block

class Block(AST):
  def __init__(self, declarations, compound_statement):
    self.declarations = declarations
    self.compound_statement = compound_statement

# 一个定义语句, 定义个变量
class VarDecl(AST):
  def __init__(self, var_node, type_node):
    self.var_node = var_node
    self.type_node = type_node

class Type(AST):
  def __init__(self, token):
    self.token = token
    self.value = token.value

class BinOp(AST):
  def __init__(self, left, op, right):
    self.left = left
    self.op = op
    self.right = right
  
class Num(AST):
  def __init__(self, token):
    self.token = token
    self.value = token.value

class UnaryOp(AST):
  def __init__(self, op, expr):
    self.token = self.op = op
    self.expr = expr
  
class Compound(AST):
  def __init__(self):
    self.children = []

class Assign(AST):
  def __init__(self, left, op, right):
    self.left = left
    self.token = self.op = op
    self.right = right
  
class Var(AST):
  def __init__(self, token):
    self.token = token
    self.value = token.value

class NoOp(AST):
  pass

class Parser(object):
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

  def block(self):
    declarations = self.declarations()
    compound_statement_node = self.compound_statement()
    node = Block(declarations, compound_statement_node)
    return node

  def declarations(self):
    declarations = []
    if self.current_token.type == VAR:
      self.eat(VAR)
      while self.current_token.type == ID:
        var_decl = self.variable_declarations()
        declarations.extend(var_decl)
        self.eat(SEMI)
    return declarations

  def variable_declarations(self):
    # ID (COMMA ID)* COLON type_spec
    var_nodes = [Var(self.current_token)]
    self.eat(ID)

    while self.current_token.type == COMMA:
      self.eat(COMMA)
      var_nodes.append(Var(self.current_token))
      self.eat(ID)

    # 冒号
    self.eat(COLON)

    type_node = self.type_spec()
    var_declarations = [
      VarDecl(var_node, type_node) for var_node in var_nodes
    ]

    return var_declarations

  def type_spec(self):
    """type_spec : INTEGER | REAL
    """
    token = self.current_token
    if token.type == INTEGER:
      self.eat(INTEGER)
    else:
      self.eat(REAL)
    node = Type(token)
    return node


  def program(self):
    self.eat(PROGRAM)
    var_node = self.variable()
    self.eat(SEMI)
    prog_name = var_node.value
    block_node = self.block()
    program_node = Program(prog_name, block_node)
    self.eat(DOT)
    return program_node
  
  def compound_statement(self):
    self.eat(BEGIN)
    nodes = self.statement_list()
    self.eat(END)

    root = Compound()

    for node in nodes:
      root.children.append(node)

    return root
  
  def statement_list(self):

    node = self.statement()

    results = [node]

    while self.current_token.type == SEMI:
      self.eat(SEMI)
      results.append(self.statement())

    # 为毛这里要加这个判断?
    # 该statement_list 都结束了, 再去赋值肯定错了吧 ? 是这样吗
    if self.current_token.type == ID:
      self.error()

    return results

  def statement(self):
    
    if self.current_token.type == BEGIN:
      node = self.compound_statement()
    elif self.current_token.type == ID:
      node = self.assginment_statement()
    else:
      node = self.empty()
    return node

  def assginment_statement(self):
    left = self.variable()
    token = self.current_token
    self.eat(ASSIGN)
    right = self.expr()
    node = Assign(left, token, right)
    return node
  
  def variable(self):
    node = Var(self.current_token)
    self.eat(ID)
    return node
  
  def empty(self):
    return NoOp()

  def expr(self):

    node = self.term()

    while self.current_token.type in [PLUS, MINUS]:
      token = self.current_token
      if token.type == PLUS:
        self.eat(PLUS)
      elif token.type == MINUS:
        self.eat(MINUS)
      
      node = BinOp(left=node, op=token, right=self.term())
    
    return node
  
  def term(self):

    node = self.factor()

    while self.current_token.type in (MUL, INTEGER_DIV, FLOAT_DIV):
      token = self.current_token
      if token.type == MUL:
          self.eat(MUL)
      elif token.type == INTEGER_DIV:
          self.eat(INTEGER_DIV)
      elif token.type == FLOAT_DIV:
          self.eat(FLOAT_DIV)

      node = BinOp(left=node, op=token, right=self.factor())

    return node

  
  def factor(self):

    token = self.current_token

    if token.type == PLUS:
      self.eat(PLUS)
      return UnaryOp(token, self.factor())
    elif token.type == MINUS:
      self.eat(MINUS)
      return UnaryOp(token, self.factor())
    elif token.type == INTEGER_CONST:
      self.eat(INTEGER_CONST)
      return Num(token)
    elif token.type == REAL_CONST:
      self.eat(REAL_CONST)
      return Num(token)
    elif token.type == LPAREN:
      self.eat(LPAREN)
      node = self.expr()
      self.eat(RPAREN)
      return node
    else:
      node = self.variable()
      return node

  def parse(self):
    node = self.program()
    if self.current_token.type != EOF:
      self.error()
    
    return node

class NodeVisitor(object):
  def visit(self, node):
    method_name = 'visit_' + type(node).__name__
    visitor = getattr(self, method_name, self.generic_visit)
    return visitor(node)
  
  def generic_visit(self, node):
    raise Exception('No visit_{name} method'.format(name=type(node).__name__))

class Interpreter(NodeVisitor):
  
  GLOBAL_SCOPE = {}

  def __init__(self, parser):
    self.parser = parser
  
  def visit_Program(self, node):
    self.visit(node.block)
  
  def visit_Block(self, node):
    for declaration in node.declarations:
      self.visit(declaration)
    self.visit(node.compound_statement)
  
  def visit_VarDecl(self, node):
    # do nothing
    pass
  
  def visit_Type(self, node):
    # do nothing
    pass

  def visit_BinOp(self, node):
    if node.op.type == PLUS:
        return self.visit(node.left) + self.visit(node.right)
    elif node.op.type == MINUS:
        return self.visit(node.left) - self.visit(node.right)
    elif node.op.type == MUL:
        return self.visit(node.left) * self.visit(node.right)
    elif node.op.type == INTEGER_DIV:
        return self.visit(node.left) // self.visit(node.right)
    elif node.op.type == FLOAT_DIV:
      return self.visit(node.left) / self.visit(node.right)


  def visit_Num(self, node):
    return node.value

  def visit_UnaryOp(self, node):
    op = node.op.type
    if op == PLUS:
        return +self.visit(node.expr)
    elif op == MINUS:
        return -self.visit(node.expr)

  def visit_Compound(self, node):
    for child in node.children:
      self.visit(child)
  
  def visit_Assign(self, node):
    var_name = node.left.value
    self.GLOBAL_SCOPE[var_name] = self.visit(node.right)
  
  def visit_Var(self, node):
    var_name = node.value
    val = self.GLOBAL_SCOPE[var_name]
    if val is None:
      raise NameError(repr(var_name))
    return val
  
  def visit_NoOp(self, node):
    pass
  
  def interpret(self):
    tree = self.parser.parse()
    if tree is None:
      return ''
    return self.visit(tree)

def main():
  import sys
  text = open(sys.argv[1], 'r').read()
  lexer = Lexer(text)
  parser = Parser(lexer)
  interpreter = Interpreter(parser)
  result = interpreter.interpret()
  print(interpreter.GLOBAL_SCOPE)

if __name__ == '__main__':
  main()
