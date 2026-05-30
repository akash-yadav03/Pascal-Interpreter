INTERGER,PLUS,EOF,MINUS,MULTI,DIV,LPAR,RPAR,ASSIGN,SEMI,DOT,BEGIN,END,ID = "INTERGER","PLUS","EOF","MINUS","MULTI","DIV","LPAR","RPAR","ASSIGN","SEMI","DOT","BEGIN","END","ID"
class AST(object):
    pass

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

class Token:
    def __init__(self,type,value):
        self.Type = type
        self.Value = value

    def __str__(self):
        return f"Token({self.Type},{self.Value})"
    
    def __repr__(self):
        return self.__str__()
    
RESERVED_KEYWORDS = {
    'BEGIN': Token('BEGIN', 'BEGIN'),
    'END': Token('END', 'END'),
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
        
    def Interger(self):
        result = ""
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def advance(self):
        self.pos += 1
        if self.pos > len(self.Text) - 1:
            self.current_char = None
        else:
            self.current_char = self.Text[self.pos]

    def whitespace(self):
        if self.current_char is not None and self.current_char.isspace():
            self.advance()

    def get_token(self):   
        while self.current_char is not None:

            if self.current_char.isspace():
                self.whitespace()
                continue

            if self.current_char.isalpha():
                return self._id()

            if self.current_char == ':' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(ASSIGN, ':=')

            if self.current_char == ';':
                self.advance()
                return Token(SEMI, ';')

            if self.current_char == '.':
                self.advance()
                return Token(DOT, '.')

            if self.current_char.isdigit():
                return Token(INTERGER,self.Interger())
            
            if self.current_char == "+":
                self.advance()
                return Token(PLUS,"+")
            
            if self.current_char == "-":
                self.advance()
                return Token(MINUS,"-")
            
            if self.current_char == "*":
                self.advance()
                return Token(MULTI,"*")

            if self.current_char == "/":
                self.advance()
                return Token(DIV,"/")
            
            if self.current_char == "(":
                self.advance()
                return Token(LPAR,"(")
            
            if self.current_char == ")":
                self.advance()
                return Token(RPAR,")")

            self.error()
            
        return Token(EOF,None)
                            
class Parser(object):

    def __init__(self,lexer):
        self.Lexer = lexer
        self.current_token = self.Lexer.get_token()

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
        elif self.current_token.Type == INTERGER:
            token = self.current_token
            self.eat(INTERGER)
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
        
        while self.current_token.Type in (MULTI,DIV):
            token = self.current_token
            if token.Type == MULTI:
                self.eat(MULTI)
                
            elif token.Type == DIV:
                self.eat(DIV)
                
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
        node = self.compound_statement()
        self.eat(DOT)
        return node

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
        elif node.Op.Type == DIV:
            return self.visit(node.Left) / self.visit(node.Right)

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

    def interpret(self):
        tree = self.interpreter.parse()
        return self.visit(tree)


if __name__ == "__main__":
    text = """
BEGIN
    BEGIN
        number := 2;
        a := number;
        b := 10 * a + 10 * number / 4;
        c := a - - b
    END;
    x := 11;
END.
"""
    Lexer = lexer(text)
    parser = Parser(Lexer)
    interpreter = Interpreter(parser)
    result = interpreter.interpret() 
    print(interpreter.GLOBAL_SCOPE)
    print(result)