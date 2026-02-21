from .Regex import Regex, parse_regex
from .NFA import NFA, EPSILON


def remap_func_factory(idx):
    def remap(state):
        return idx, state
    return remap

class Lexer:
    def __init__(self, spec: list[tuple[str, str]]) -> None:
        self.spec = spec
        nfas = []
        #construim NFA-urile pentru fiecare specificație
        for i, (token_type, regex_str) in enumerate(spec):
            nfa = parse_regex(regex_str).thompson()
            nfa_remap = nfa.remap_states(remap_func_factory(i))
            nfas.append((nfa_remap, i, token_type))
        #combinam NFA-urile intr-unul singur
        new_start = "LEXER_START"
        #setam starile de start ale NFA-urilor individuale
        start_states = set()
        for nfa, _, _ in nfas:
            start_states.add(nfa.q0)
        #construim dicționarul într-un mod clasic
        combined_d = {}
        combined_d[(new_start, EPSILON)] = start_states
        #combinam starile de start si finale
        combined_K = {new_start}
        combined_S = set()
        self.finals = {}
        #combinam toate NFA-urile
        for nfa, priority, name in nfas:
            combined_K.update(nfa.K)
            combined_S.update(nfa.S)
            combined_d.update(nfa.d)
            for f_state in nfa.F:
                self.finals[f_state] = (priority, name)
        #construim NFA-ul combinat si apoi DFA-ul prin subset construction
        nfa= NFA(combined_S, combined_K, new_start, combined_d, set(self.finals.keys()))
        self.dfa = nfa.subset_construction()

    def lex(self, word: str) -> list[tuple[str, str]]:
        #initializam variabilele necesare
        result = []
        index = 0
        line_number = 0
        line_start_index = 0
        length = len(word)
        #parcurgem sirul de intrare
        while index < length:
            current_state = self.dfa.q0
            last_final_pos = -1
            best_token = None
            #punctul cel mai departat de inceputul liniei la care ajungem
            max_distance = index
            #incercam sa gasim cel mai lung prefix valid
            for i in range(index, len(word)):
                #simbolul curent
                symbol = word[i]
                #daca nu exista tranzitie pentru simbolul curent, iesim din bucla
                if (current_state, symbol) not in self.dfa.d:
                    break
                #starea urmatoare

                next_state = self.dfa.d[(current_state, symbol)]
                #verificam daca am ajuns in synk state
                if not next_state:
                    break
                #actualizam starea curenta
                current_state = next_state
                #actualizam pozitia cea mai departata
                max_distance = i + 1
                #formam nfa-ul final
                nfa = []
                for s in current_state:
                    if s in self.finals:
                        nfa.append(s)
                if nfa:
                    #alegem starea finala cu proiritatea cea mai mare
                    best_nfa_state = min(nfa, key=lambda s: self.finals[s][0])
                    #actualizam token-ul corespunzator si ultima pozitie finala
                    best_token = self.finals[best_nfa_state][1]
                    last_final_pos = i

            #gestionam erorile
            if last_final_pos == -1:
                #veficam daca am ajuns la sfarsitul cuvantului
                if max_distance == len(word):
                    return [("", f"No viable alternative at character EOF, line {line_number}")]
                else:
                    #daca nu,, afisam eroarea cu pozitia exacta
                    colloumn = max_distance - line_start_index
                    return [("", f"No viable alternative at character {colloumn}, line {line_number}")]

            #lexemul gasit de la index la last_final_pos
            lexem = word[index:last_final_pos + 1]
            result.append((best_token, lexem))

            #actualizam numarul liniei si indexul de start al liniei
            #doar daca lexemul accontine caractere de newline
            newlines_count = lexem.count('\n')
            if newlines_count > 0:
                line_number += newlines_count
                #actualizam indexul de start al liniei
                line_start_index = index + lexem.rfind('\n') + 1

            index = last_final_pos + 1

        return result