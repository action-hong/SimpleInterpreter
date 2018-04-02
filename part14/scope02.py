from collections import OrderedDict

from spi import (
    Lexer,
    Parser,
    NodeVisitor,
    BuiltinTypeSymbol,
    VarSymbol,
    ProcedureSymbol
)


class ScopedSymbolTable(object):
    def __init__(self, scope_name, scope_level, enclosing_scope):
        self._symbols = OrderedDict()
        self.scope_name = scope_name
        self.scope_level = scope_level
        self.enclosing_scope = enclosing_scope
        self._init_builtins()

    def _init_builtins(self):
        self.insert(BuiltinTypeSymbol('INTEGER'))
        self.insert(BuiltinTypeSymbol('REAL'))

    def __str__(self):
        h1 = 'SCOPE (SCOPED SYMBOL TABLE)'
        lines = ['\n', h1, '=' * len(h1)]
        for header_name, header_value in (
            ('Scope name', self.scope_name),
            ('Scope level', self.scope_level),
            ('Enclosing scope',
             self.enclosing_scope.scope_name if self.enclosing_scope else None
            )
        ):
            lines.append('%-15s: %s' % (header_name, header_value))
        h2 = 'Scope (Scoped symbol table) contents'
        lines.extend([h2, '-' * len(h2)])
        lines.extend(
            ('%7s: %r' % (key, value))
            for key, value in self._symbols.items()
        )
        lines.append('\n')
        s = '\n'.join(lines)
        return s

    __repr__ = __str__

    def insert(self, symbol):
        print('Insert: %s' % symbol.name)
        self._symbols[symbol.name] = symbol

    def lookup(self, name):
        # symbol = None

        # table = self
        # # 寻找最近的
        # while table is not None and symbol is None:
        #     symbol = table._symbols.get(name)
        #     table = table.enclosing_scope
        # # 'symbol' is either an instance of the Symbol class or None
        # return symbol

        # 没必要像上面注释这样做, 本身就可以直接用 lookup做递归
        print('Lookup: %s. (Scope name: %s)' % (name, self.scope_name))
        symbol = self._symbols.get(name)

        if symbol is not None:
            return symbol
        
        if self.enclosing_scope is not None:
            # 无限递归上去
            return self.enclosing_scope.lookup(name)
        else:
            # 递归到 global scope 还是没找到, 说明没有这个变量
            return None


class SemanticAnalyzer(NodeVisitor):
    def __init__(self):
        self.current_scope = None

    def visit_Block(self, node):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_Program(self, node):
        print('ENTER scope: global')
        global_scope = ScopedSymbolTable(
            scope_name='global',
            scope_level=1,
            enclosing_scope = self.current_scope
        )
        self.current_scope = global_scope

        # visit subtree
        self.visit(node.block)

        print(global_scope)

        # 访问完子程序了, 此时的scope还是子程序的scope, 必须要重新变回当前程序的scope
        self.current_scope = self.current_scope.enclosing_scope
        print('LEAVE scope: global')

    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_NoOp(self, node):
        pass

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_ProcedureDecl(self, node):
        proc_name = node.proc_name
        proc_symbol = ProcedureSymbol(proc_name)
        self.current_scope.insert(proc_symbol)

        print('ENTER scope: %s' %  proc_name)
        # Scope for parameters and local variables
        procedure_scope = ScopedSymbolTable(
            scope_name=proc_name,
            scope_level=2,
            enclosing_scope = self.current_scope
        )
        self.current_scope = procedure_scope

        # Insert parameters into the procedure scope
        for param in node.params:
            param_type = self.current_scope.lookup(param.type_node.value)
            param_name = param.var_node.value
            var_symbol = VarSymbol(param_name, param_type)
            self.current_scope.insert(var_symbol)
            proc_symbol.params.append(var_symbol)

        self.visit(node.block_node)

        print(procedure_scope)

        self.current_scope = self.current_scope.enclosing_scope
        print('LEAVE scope: %s' %  proc_name)

    def visit_VarDecl(self, node):
        type_name = node.type_node.value
        type_symbol = self.current_scope.lookup(type_name)

        # We have all the information we need to create a variable symbol.
        # Create the symbol and insert it into the symbol table.
        var_name = node.var_node.value
        var_symbol = VarSymbol(var_name, type_symbol)

        self.current_scope.insert(var_symbol)

    def visit_Assign(self, node):
        # right-hand side
        self.visit(node.right)
        # left-hand side
        self.visit(node.left)

    def visit_Var(self, node):
        var_name = node.value
        var_symbol = self.current_scope.lookup(var_name)
        if var_symbol is None:
            raise Exception(
                "Error: Symbol(identifier) not found '%s'" % var_name
            )

class TranslateAnalyzer(NodeVisitor):
    def __init__(self):
        self.text = ''
        # 缩进单位
        self.tab = 0
        self.level = 0

    def visit_Block(self, node):
        self.tab += 2
        self.level += 1
        for declaration in node.declarations:
            self.visit(declaration)
        self.text += ' ' * self.tab + 'begin\n'
        self.tab += 2
        self.visit(node.compound_statement)
        self.tab -= 2
        self.text += ' ' * self.tab + 'end'
        self.level -= 1
        self.tab -= 2


    def visit_Program(self, node):
        print('ENTER scope: global')
        self.text += 'program ' + node.name + self.level + ';\n'
        global_scope = ScopedSymbolTable(
            scope_name='global',
            scope_level=1,
            enclosing_scope = self.current_scope
        )
        self.current_scope = global_scope

        # visit subtree
        self.visit(node.block)

        print(global_scope)

        # 访问完子程序了, 此时的scope还是子程序的scope, 必须要重新变回当前程序的scope
        self.current_scope = self.current_scope.enclosing_scope
        print('LEAVE scope: global')

        self.text += '. \{END OF ' + node.name + '}'

    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_NoOp(self, node):
        pass

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_ProcedureDecl(self, node):
        proc_name = node.proc_name
        proc_symbol = ProcedureSymbol(proc_name)
        self.current_scope.insert(proc_symbol)

        print('ENTER scope: %s' %  proc_name)
        
        # Scope for parameters and local variables
        procedure_scope = ScopedSymbolTable(
            scope_name=proc_name,
            scope_level=2,
            enclosing_scope = self.current_scope
        )
        self.current_scope = procedure_scope

        self.text += ' ' * self.tab + 'procedure ' + proc_name + self.level + '('
        # Insert parameters into the procedure scope
        self.level += 1
        
        for param in node.params:
            param_type = self.current_scope.lookup(param.type_node.value)
            param_name = param.var_node.value
            var_symbol = VarSymbol(param_name, param_type)
            self.current_scope.insert(var_symbol)
            proc_symbol.params.append(var_symbol)
            self.text += param_name + self.level + ' : ' + param_type.name + ', '

        # 去掉最后一个逗号
        self.text = self.text[0: len(self.text) - 2]
        self.level -= 1
        self.text += ");\n"
        self.visit(node.block_node)

        self.text += '; {END OF ' + proc_name + '}'

        print(procedure_scope)

        self.current_scope = self.current_scope.enclosing_scope
        print('LEAVE scope: %s' %  proc_name)

    def visit_VarDecl(self, node):
        type_name = node.type_node.value
        type_symbol = self.current_scope.lookup(type_name)

        # We have all the information we need to create a variable symbol.
        # Create the symbol and insert it into the symbol table.
        var_name = node.var_node.value
        var_symbol = VarSymbol(var_name, type_symbol)

        self.current_scope.insert(var_symbol)
        self.text += '{} var {} : {};\n'.format(' ' * self.tab, var_name + self.level, type_name)

    def visit_Assign(self, node):
        # right-hand side
        self.visit(node.right)
        # left-hand side
        self.visit(node.left)

    def visit_Var(self, node):
        var_name = node.value
        var_symbol = self.current_scope.lookup(var_name)
        if var_symbol is None:
            raise Exception(
                "Error: Symbol(identifier) not found '%s'" % var_name
            )
        

if __name__ == '__main__':
    text = """
program Main;
   var x, y: real;

   procedure Alpha(a : integer);
      var y : integer;
   begin
      x := a + x + y;
   end;

begin { Main }

end.  { Main }
"""

    lexer = Lexer(text)
    parser = Parser(lexer)
    tree = parser.parse()
    semantic_analyzer = SemanticAnalyzer()
    semantic_analyzer.visit(tree)