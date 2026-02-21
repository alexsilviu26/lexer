from typing import Any, List
from .NFA import NFA

EPSILON = ''

class Regex:
    # clasa de baza pentru expresii regulate
    COUNTER = 0

    def thompson(self) -> NFA[int]:
        # metoda thompson, implementata de subclase
        raise NotImplementedError("Subclasses should implement this method.")

    def add_transition(self, transitions: dict[tuple[int, str], set[int]],
                       source: int, symbol: str, destinations: set[int]):
        # adauga o tranzitie in dictionarul delta
        key = (source, symbol)
        if key not in transitions:
            transitions[key] = set()
        transitions[key].update(destinations)


# sublclasa pentru epsilon
class Epsilon(Regex):
    def thompson(self) -> NFA[int]:
        start = Regex.COUNTER
        Regex.COUNTER += 1
        end = Regex.COUNTER
        Regex.COUNTER += 1
        d = {}
        self.add_transition(d, start, EPSILON, {end})
        # nfa cu o tranzitie epsilon de la start la end
        return NFA(set(), {start, end}, start, d, {end})


# sublclasa pentru caractere
class Character(Regex):
    def __init__(self, char: str):
        self.char = char

    def thompson(self) -> NFA[int]:
        start = Regex.COUNTER
        Regex.COUNTER += 1
        end = Regex.COUNTER
        Regex.COUNTER += 1
        d = {}
        self.add_transition(d, start, self.char, {end})
        # nfa cu o tranzitie pe caracter de la start la end
        return NFA({self.char}, {start, end}, start, d, {end})


# sublclasa pentru operatorul uniune
class Union(Regex):
    def __init__(self, left: Regex, right: Regex):
        self.right = right
        self.left = left


    def thompson(self) -> NFA[int]:
        # construieste nfa pentru uniune
        right_nfa = self.right.thompson()
        left_nfa = self.left.thompson()

        new_start = Regex.COUNTER
        Regex.COUNTER += 1
        new_end = Regex.COUNTER
        Regex.COUNTER += 1

        S = left_nfa.S.union(right_nfa.S)
        K = left_nfa.K.union(right_nfa.K).union({new_start, new_end})
        q0 = new_start
        F = {new_end}

        delta = left_nfa.d.copy()
        delta.update(right_nfa.d)

        # tranzitii epsilon de la noul start la starturile vechi
        self.add_transition(delta, new_start, EPSILON, {left_nfa.q0, right_nfa.q0})
        # tranzitii epsilon de la starile finale vechi la noul end
        for final_state in left_nfa.F.union(right_nfa.F):
            self.add_transition(delta, final_state, EPSILON, {new_end})

        return NFA(S, K, q0, delta, F)


# sublclasa pentru operatorul concatenare
class Concat(Regex):
    # regex pentru concatenare
    def __init__(self, right: Regex, left: Regex):
        self.right = right
        self.left = left

    def thompson(self) -> NFA[int]:
        # construieste nfa pentru concatenare
        nfa1 = self.right.thompson()
        nfa2 = self.left.thompson()
        S = nfa1.S.union(nfa2.S)
        K = nfa1.K.union(nfa2.K)
        q0 = nfa1.q0
        F = nfa2.F
        d = nfa1.d.copy()
        d.update(nfa2.d)
        # tranzitii epsilon de la starile finale din nfa1 la starea de start din nfa2
        for f1 in nfa1.F:
            self.add_transition(d, f1, EPSILON, {nfa2.q0})

        return NFA(S, K, q0, d, F)


# sublclasa pentru operatorul kleene star
class Star(Regex):
    # regex pentru inchiderea kleene (zero sau mai multe aparitii)
    def __init__(self, regex: Regex):
        self.regex = regex

    def thompson(self) -> NFA[int]:
        # construieste nfa pentru star
        nfa = self.regex.thompson()
        next_start = Regex.COUNTER
        Regex.COUNTER += 1
        next_end = Regex.COUNTER
        Regex.COUNTER += 1

        S = nfa.S
        K = nfa.K.union({next_start, next_end})
        q0 = next_start
        F = {next_end}
        delta = nfa.d.copy()

        # tranzitii de la noul start: la vechiul start si la noul final (pentru zero aparitii)
        self.add_transition(delta, next_start, EPSILON, {nfa.q0, next_end})
        # tranzitii de la vechile finale: la vechiul start (pentru repetare) si la noul final
        for f in nfa.F:
            self.add_transition(delta, f, EPSILON, {nfa.q0, next_end})

        return NFA(S, K, q0, delta, F)


# sublclasa pentru operatorul plus
class Plus(Regex):
    def __init__(self, regex: Regex):
        self.regex = regex

    def thompson(self) -> NFA[int]:
        # plus = regex concatenat cu star(regex)
        return Concat(self.regex, Star(self.regex)).thompson()


# sublclasa pentru optionalitate
class Optional(Regex):
    def __init__(self, regex: Regex):
        self.regex = regex

    def thompson(self) -> NFA[int]:
        # optionalitate = regex uniune cu epsilon
        return Union(self.regex, Epsilon()).thompson()


# funcrii auxiliare pentru parsare
class AuxFunctions:

    @staticmethod
    def is_character(token: str) -> bool:
        # verifica daca token-ul e un caracter/operand
        if token not in ('(', ')', '|', '&', '*', '+', '?'):
            return True  # simbolul pentru epsilon
        return False

    @staticmethod
    def is_operand_end(token: str) -> bool:
        # verifica daca token-ul e sfarsitul unui operand
        if AuxFunctions.is_character(token) or token in (')', '*', '+', '?'):
            return True
        return False

    @staticmethod
    def is_operand_start(token: str) -> bool:
        # verifica daca token-ul e inceputul unui operand
        if AuxFunctions.is_character(token) or token in ('('):
            return True
        return False


def parse_regex(regex_string: str) -> Regex:
    # functie principala de parsare a regex-ului
    Regex.COUNTER = 0  # reseteaza generatorul de stari
    OPERATORS = {'|': 1, '&': 2, '*': 3, '?': 3, '+': 3}

    regex_parts = []
    index = 0
    # preprocesam escaparile, spatiile si syntactic sugar
    while index < len(regex_string):
        char = regex_string[index]
        if char == '\\':
            # caracter escapat
            if index + 1 < len(regex_string):
                regex_parts.append(regex_string[index: index + 2])
                index += 2
            else:
                index += 1
        elif char.isspace():
            if char == '\n':
                regex_parts.append('\\n')
            elif char == '\r':
                regex_parts.append('\\r')
            elif char == '\t':
                regex_parts.append('\\t')
            elif char == ' ':
                index += 1
                continue
            index += 1

        # syntactic sugar
        elif regex_string.startswith('[a-z]', index):
            chars = [chr(j) for j in range(ord('a'), ord('z') + 1)]
            regex_parts.append('(')
            regex_parts.extend(list('|'.join(chars)))
            regex_parts.append(')')
            index += 5
        elif regex_string.startswith('[A-Z]', index):
            chars = [chr(j) for j in range(ord('A'), ord('Z') + 1)]
            regex_parts.append('(')
            regex_parts.extend(list('|'.join(chars)))
            regex_parts.append(')')
            index += 5
        elif regex_string.startswith('[0-9]', index):
            chars = [chr(j) for j in range(ord('0'), ord('9') + 1)]
            regex_parts.append('(')
            regex_parts.extend(list('|'.join(chars)))
            regex_parts.append(')')
            index += 5
        elif regex_string.startswith('eps', index):
            # simbol pentru epsilon
            regex_parts.append('#')
            index += 3
        else:
            regex_parts.append(char)
            index += 1

    # procesam uniunile (|)
    regex_union = []
    for index, value in enumerate(regex_parts):
        if value == '|':
            # inserare epsilon inainte de '|' daca nu e operand
            if regex_union[-1] in ('('):
                regex_union.append('#')
            regex_union.append('|')
            # inserare epsilon dupa '|' daca nu e operand
            if index + 1 >= len(regex_parts) or regex_parts[index + 1] in (')'):
                regex_union.append('#')
        else:
            regex_union.append(value)

    # procesam concatenarile (&)
    regex_concat = []
    for index, value in enumerate(regex_union):
        regex_concat.append(value)
        if index + 1 < len(regex_union):
            next_elem = regex_union[index + 1]
            # adauga concatenare daca se termina un operand si incepe altul
            if AuxFunctions.is_operand_end(value):
                if AuxFunctions.is_operand_start(next_elem):
                    regex_concat.append('&')

    # separam caracterele si operatorii folosind shunting-yard
    char_collecion: List[str] = []
    operator_collecion: List[str] = []
    for value in regex_concat:
        if AuxFunctions.is_character(value):
            char_collecion.append(value)
        elif value == '(':
            operator_collecion.append(value)
        elif value == ')':
            while operator_collecion:
                if operator_collecion[-1] == '(':
                    break
                char_collecion.append(operator_collecion.pop())
            operator_collecion.pop()  # elimina paranteza deschisa
        elif value in OPERATORS:
            # logica de precedenta a operatorilor
            while operator_collecion:
                if operator_collecion[-1] == '(':
                    break
                if OPERATORS.get(operator_collecion[-1], 0) <= OPERATORS[value]:
                    break
                char_collecion.append(operator_collecion.pop())
            operator_collecion.append(value)
    # unim caracterele si operatorii ramasi
    while operator_collecion:
        char_collecion.append(operator_collecion.pop())
    final_collecion = char_collecion
    # construire AST folosind colectia finala
    ast: List[Regex] = []
    for value in final_collecion:
        if AuxFunctions.is_character(value):
            if value == '#':
                ast.append(Epsilon())
            else:
                # gestionare caractere escapate
                if len(value) > 1 and value.startswith('\\'):
                    escaped_char = value[1]
                    if escaped_char == 'n':
                        ast.append(Character('\n'))
                    else:
                        ast.append(Character(escaped_char))
                else:
                    ast.append(Character(value))
        elif value == '&':
            # creeaza nod concatenare
            r2 = ast.pop()
            r1 = ast.pop()
            ast.append(Concat(r1, r2))
        elif value == '|':
            # creeaza nod uniune
            if len(ast) >= 2:
                r2 = ast.pop()
                r1 = ast.pop()
                ast.append(Union(r1, r2))
        elif value in ('*', '+', '?'):
            # creeaza nod operator unar
            if len(ast) >= 1:
                r = ast.pop()
                if value == '*':
                    ast.append(Star(r))
                if value == '?':
                    ast.append(Optional(r))
                if value == '+':
                    ast.append(Plus(r))

    # nodul radacina al ast-ului
    return ast.pop()