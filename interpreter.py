INTEGER,PLUS,EOF,MINUS,MULTI,DIV,LPAR,RPAR,ASSIGN,SEMI,DOT,BEGIN,END,ID,PROGRAM,VAR,COLON,COMMA,REAL,INTEGER_CONST,REAL_CONST,INTEGER_DIV,FLOAT_DIV,PROCEDURE = "INTEGER","PLUS","EOF","MINUS","MULTI","DIV","LPAR","RPAR","ASSIGN","SEMI","DOT","BEGIN","END","ID","PROGRAM","VAR","COLON","COMMA","REAL","INTEGER_CONST","REAL_CONST","INTEGER_DIV","FLOAT_DIV","PROCEDURE"
class AST(object):
    pass

class Symbol(object):
    def __init__(self, name, type=None):
        self.name = name
        self.type = type

class BuiltinTypeSymbol(Symbol):
    def __init__(self, name):
        super().__init__(name)

    def __str__(self):
        return self.name

    __repr__ = __str__

class VarSymbol(Symbol):
    def __init__(self, name, type):
        super().__init__(name, type)

    def __str__(self):
        return '<{name}:{type}>'.format(name=self.name, type=self.type)

    __repr__ = __str__

class SymbolTable(object):
    def __init__(self):
        self._symbols = {}
        self._init_builtins()

    def _init_builtins(self):
        self.define(BuiltinTypeSymbol('INTEGER'))
        self.define(BuiltinTypeSymbol('REAL'))

    def __str__(self):
        s = 'Symbols: {symbols}'.format(
            symbols=[value for value in self._symbols.values()]
        )
        return s

    __repr__ = __str__

    def define(self, symbol):
        print('Define: %s' % symbol)
        self._symbols[symbol.name] = symbol

    def lookup(self, name):
        print('Lookup: %s' % name)
        symbol = self._symbols.get(name)
        return symbol

class binOp(AST):
    def __init__(self,left,op,right):
        self.Left = left
        self.Token = self.Op = op
        self.Right = right

class Num(AST):
    def __init__(self,token):
        self.Token = token
        self.Value = token.Value

class UnaryOp(AST):
    def __init__(self, op, expression):
        self.token = self.op = op
        self.expression = expression

class Compound(AST):
    def __init__(self):
        self.Children = []

class Assign(AST):
    def __init__(self,left,op,right):
        self.Left = left
        self.Token = self.Op = op
        self.Right = right 

class Var(AST):
    def __init__(self,token):
        self.Token = token
        self.Value = token.Value

class NoOp(AST):
    pass

class Program(AST):
    def __init__(self, name, block):
        self.name = name
        self.block = block

class Block(AST):
    def __init__(self, declarations, compound_statement):
        self.declarations = declarations
        self.compound_statement = compound_statement

class VarDecl(AST):
    def __init__(self, var_node, type_node):
        self.var_node = var_node
        self.type_node = type_node

class Type(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.Value

class Token:
    def __init__(self,type,value):
        self.Type = type
        self.Value = value

    def __str__(self):
        return f"Token({self.Type},{self.Value})"
    
    def __repr__(self):
        return self.__str__()
    
class ProcedureDecl(AST):
    def __init__(self, proc_name, block_node):
        self.proc_name = proc_name
        self.block_node = block_node
    
RESERVED_KEYWORDS = {
    'PROGRAM': Token('PROGRAM', 'PROGRAM'),
    'VAR': Token('VAR', 'VAR'),
    'DIV': Token('INTEGER_DIV', 'DIV'),
    'INTEGER': Token('INTEGER', 'INTEGER'),
    'REAL': Token('REAL', 'REAL'),
    'BEGIN': Token('BEGIN', 'BEGIN'),
    'END': Token('END', 'END'),
    'PROCEDURE': Token('PROCEDURE', 'PROCEDURE'),
}
    
class lexer(object):
    def __init__(self,text):
        self.Text = text
        self.pos = 0
        self.current_char = self.Text[self.pos]
        
    def error(self):
        raise Exception("the input is invalid")
    
    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.Text) - 1:
            return None
        else:
            return self.Text[peek_pos]
        
    def _id(self):
        result = ''
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.advance()

        token = RESERVED_KEYWORDS.get(result, Token(ID, result))
        return token
        
    def number(self):
        result = ""
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        if self.current_char == ".":
            result += self.current_char
            self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()
            token = Token('REAL_CONST', float(result))
        else:
            token = Token('INTEGER_CONST', int(result))
        return token

    def advance(self):
        self.pos += 1
        if self.pos > len(self.Text) - 1:
            self.current_char = None
        else:
            self.current_char = self.Text[self.pos]

    def whitespace(self):
        if self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        while self.current_char != '}':
            self.advance()
        self.advance()

    def get_token(self):   
        while self.current_char is not None:

            if self.current_char.isspace():
                self.whitespace()
                continue

            elif self.current_char.isalpha():
                return self._id()
            
            elif self.current_char == '{':
                self.advance()
                self.skip_comment()
                continue

            elif self.current_char == ':' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(ASSIGN, ':=')

            elif self.current_char == ';':
                self.advance()
                return Token(SEMI, ';')

            elif self.current_char == '.':
                self.advance()
                return Token(DOT, '.')
            
            elif self.current_char == ':':
                self.advance()
                return Token(COLON, ':')

            elif self.current_char == ',':
                self.advance()
                return Token(COMMA, ',')

            elif self.current_char.isdigit():
                return self.number()
            
            elif self.current_char == "+":
                self.advance()
                return Token(PLUS,"+")
            
            elif self.current_char == "-":
                self.advance()
                return Token(MINUS,"-")
            
            elif self.current_char == "*":
                self.advance()
                return Token(MULTI,"*")

            elif self.current_char == "/":
                self.advance()
                return Token(FLOAT_DIV,"/")
            
            elif self.current_char == "(":
                self.advance()
                return Token(LPAR,"(")
            
            elif self.current_char == ")":
                self.advance()
                return Token(RPAR,")")

            self.error()
            
        return Token(EOF,None)
                            
class Parser(object):

    def __init__(self,lexer):
        self.Lexer = lexer
        self.current_token = self.Lexer.get_token()

    def block(self):
        declaration_nodes = self.declarations()
        compound_statement_node = self.compound_statement()
        node = Block(declaration_nodes, compound_statement_node)
        return node
    
    def declarations(self):
        declarations = []
        if self.current_token.Type == VAR:
            self.eat(VAR)
            while self.current_token.Type == ID:
                var_decl = self.variable_declaration()
                declarations.extend(var_decl)
                self.eat(SEMI)
        while self.current_token.Type == PROCEDURE:
            self.eat(PROCEDURE)
            proc_name = self.current_token.value
            self.eat(ID)
            self.eat(SEMI)
            block_node = self.block()
            proc_decl = ProcedureDecl(proc_name, block_node)
            declarations.append(proc_decl)
            self.eat(SEMI)

        return declarations

    def variable_declaration(self):
        var_nodes = [Var(self.current_token)]  # first ID
        self.eat(ID)

        while self.current_token.Type == COMMA:
            self.eat(COMMA)
            var_nodes.append(Var(self.current_token))
            self.eat(ID)

        self.eat(COLON)

        type_node = self.type_spec()
        var_declarations = [
            VarDecl(var_node, type_node)
            for var_node in var_nodes
        ]
        return var_declarations

    def type_spec(self):
        token = self.current_token
        if self.current_token.Type == INTEGER:
            self.eat(INTEGER)
        else:
            self.eat(REAL)
        node = Type(token)
        return node

    def error(self):
        raise Exception("the input is invalid")

    def eat(self,type):
        if type == self.current_token.Type:
            self.current_token = self.Lexer.get_token()
        else:
            self.error()

    def factor(self):
        if self.current_token.Type == PLUS:
            token = self.current_token
            self.eat(PLUS)
            node = UnaryOp(token, self.factor())
            return node
        elif self.current_token.Type == MINUS:
            token = self.current_token
            self.eat(MINUS)
            node = UnaryOp(token, self.factor())
            return node
        elif self.current_token.Type == INTEGER_CONST:
            token = self.current_token
            self.eat(INTEGER_CONST)
            return Num(token)
        elif self.current_token.Type == REAL_CONST:
            token = self.current_token
            self.eat(REAL_CONST)
            return Num(token)
        elif self.current_token.Type == LPAR:
            token = self.current_token
            self.eat(LPAR)
            node = self.expression()
            self.eat(RPAR)
            return node
        else:
            node = self.variable()
            return node

    def term(self):
        node = self.factor()
        
        while self.current_token.Type in (MULTI,INTEGER_DIV,FLOAT_DIV):
            token = self.current_token
            if token.Type == MULTI:
                self.eat(MULTI)
                
            elif token.Type == INTEGER_DIV:
                self.eat(INTEGER_DIV)

            elif token.Type == FLOAT_DIV:
                self.eat(FLOAT_DIV)

            node = binOp(left=node, op=token, right=self.factor())

        return node 
    
    def expression(self):
        node = self.term()

        while self.current_token.Type in (PLUS,MINUS):
            token = self.current_token
            if token.Type == PLUS:
                self.eat(PLUS)
                
            elif token.Type == MINUS:
                self.eat(MINUS)
                
            node = binOp(left=node, op=token, right=self.term()) 
        return node
    
    def program(self):
        self.eat(PROGRAM)
        var_node = self.variable()
        prog_name = var_node.Value
        self.eat(SEMI)
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
            root.Children.append(node)

        return root

    def statement_list(self):
        node = self.statement()

        results = [node]

        while self.current_token.Type == SEMI:
            self.eat(SEMI)
            results.append(self.statement())

        if self.current_token.Type == ID:
            self.error()

        return results

    def statement(self):
        if self.current_token.Type == BEGIN:
            node = self.compound_statement()
        elif self.current_token.Type == ID:
            node = self.assignment_statement()
        else:
            node = self.empty()
        return node

    def assignment_statement(self):
        left = self.variable()
        token = self.current_token
        self.eat(ASSIGN)
        right = self.expression()
        node = Assign(left, token, right)
        return node

    def variable(self):
        node = Var(self.current_token)
        self.eat(ID)
        return node

    def empty(self): 
        return NoOp()

    def parse(self):
        node = self.program()
        if self.current_token.Type != EOF:
            self.error()
        return node

class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))

class SymbolTableBuilder(NodeVisitor):
    def __init__(self):
        self.symtab = SymbolTable()

    def visit_Block(self, node):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_Program(self, node):
        self.visit(node.block)

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_Num(self, node):
        pass

    def visit_UnaryOp(self, node):
        self.visit(node.expr)

    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_NoOp(self, node):
        pass

    def visit_VarDecl(self, node):
        type_name = node.type_node.value
        type_symbol = self.symtab.lookup(type_name)
        var_name = node.var_node.value
        var_symbol = VarSymbol(var_name, type_symbol)
        self.symtab.define(var_symbol)

    def visit_Assign(self, node):
        var_name = node.left.value
        var_symbol = self.symtab.lookup(var_name)
        if var_symbol is None:
            raise NameError(repr(var_name))

        self.visit(node.right)

    def visit_Var(self, node):
        var_name = node.value
        var_symbol = self.symtab.lookup(var_name)

        if var_symbol is None:
            raise NameError(repr(var_name))
    
    def visit_ProcedureDecl(self, node):
        pass

class Interpreter(NodeVisitor):
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.GLOBAL_SCOPE = {}

    def visit_UnaryOp(self, node):
        op = node.op.Type
        if op == PLUS:
            return +self.visit(node.expression)
        elif op == MINUS:
            return -self.visit(node.expression)

    def visit_binOp(self, node):
        if node.Op.Type == PLUS:
            return self.visit(node.Left) + self.visit(node.Right)
        elif node.Op.Type == MINUS:
            return self.visit(node.Left) - self.visit(node.Right)
        elif node.Op.Type == MULTI:
            return self.visit(node.Left) * self.visit(node.Right)
        elif node.Op.Type == FLOAT_DIV:
            return self.visit(node.Left) / self.visit(node.Right)
        elif node.Op.Type == INTEGER_DIV:
            return float(self.visit(node.Left) // self.visit(node.Right))

    def visit_Num(self, node):
        return node.Value
    
    def visit_Compound(self, node):
        for child in node.Children:
            self.visit(child)

    def visit_NoOp(self, node):
        pass

    def visit_Assign(self, node):
        var_name = node.Left.Value
        self.GLOBAL_SCOPE[var_name] = self.visit(node.Right)

    def visit_Var(self, node):
        var_name = node.Value
        val = self.GLOBAL_SCOPE.get(var_name)
        if val is None:
            raise NameError(repr(var_name))
        else:
            return val
        
    def visit_Program(self,node):
        self.visit(node.block)

    def visit_Block(self, node):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_VarDecl(self, node):
        pass

    def visit_Type(self, node):
        pass

    def visit_ProcedureDecl(self,node):
        pass

    def interpret(self):
        tree = self.interpreter.parse()
        return self.visit(tree)


if __name__ == "__main__":
    text = """
PROGRAM Part10;
VAR
   number     : INTEGER;
   a, b, c, x : INTEGER;
   y          : REAL;

BEGIN
   BEGIN
      number := 2;
      a := number;
      b := 10 * a + 10 * number DIV 4;
      c := a - - b
   END;
   x := 11;
   y := 20 / 7 + 3.14;
   { writeln('a = ', a); }
   { writeln('b = ', b); }
   { writeln('c = ', c); }
   { writeln('number = ', number); }
   { writeln('x = ', x); }
   { writeln('y = ', y); }
END.  {Part10}
"""
    Lexer = lexer(text)
    parser = Parser(Lexer)
    interpreter = Interpreter(parser)
    result = interpreter.interpret() 
    print(interpreter.GLOBAL_SCOPE)
    print(result)