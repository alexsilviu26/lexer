from .Lexer import Lexer
from .Grammar import Grammar

class Parser():
    def __init__(self, lexer: Lexer, grammar: Grammar) -> None:
        self.lexer = lexer
        self.grammar = grammar

    
    def parse(self, input_str: str) -> str:
        #preluam tokenii folosind lexer-ul
        tokens = self.lexer.lex(input_str)
        #eliminam tokenii de tip SPACE
        filtered = []
        for token in tokens:
            if token[0] != "SPACE":
                filtered.append(token)
        #formam arborele de parsare folosind CYK
        tree = self.grammar.cykParse(filtered)
        #returnam arborele daca exista sau daca nu un mesaj de eroare
        if tree:
            return tree.to_string()
        return "Input string is not valid according to the grammar."


        
        
