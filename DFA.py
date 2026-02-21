from collections.abc import Callable
from dataclasses import dataclass
from itertools import product
import pandas as pd
from typing import TypeVar
from functools import reduce

STATE = TypeVar('STATE')


@dataclass
class DFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], STATE]
    F: set[STATE]

    def accept(self, word: str) -> bool:
        #preluam starea intitala
        q = self.q0
        #parcurgem caracter cu caracter din cuvant
        for char in word:
            #realizam tranzitiile
            q = self.d[(q, char)]
        #daca starea in care am ajuns e finala acceptam
        if q in self.F:
            return True
        #altfel nu
        else:
            return False


    def minimize(self) -> 'DFA[STATE]':
        #Hopcroft

        P = [set(self.F), set(self.K) - set(self.F)]
        W = [set(self.F)]

        while W:
            A = W.pop(0)
            for c in self.S:
                X_c = set()
                for q in self.K:
                    if  self.d[(q, c)] in A:
                        X_c.add(q)
                P_second = []
                for Y in P:
                    Y1 = Y.intersection(X_c)
                    Y2 = Y.difference(X_c)
                    if Y1 and Y2:
                        P_second.extend([Y1, Y2])
                        if Y not in W:
                            if len(Y1) >= len(Y2):
                                W.append(Y2)
                            else:
                                W.append(Y1)
                        else:
                            W.remove(Y)
                            W.extend([Y1, Y2])
                    else:
                        P_second.append(Y)
                P = P_second
        #construim mappingul starilor vechi catre starile noi
        state_map = {}
        for c in P:
            if c:
                representative = next(iter(c))
                for q in c:
                    state_map[q] = representative
        #adaugam starile noi
        new_start = state_map[self.q0]
        new_states = set(state_map.values())
        new_final = set()
        for q in self.F:
            if q in state_map:
                new_final.add(state_map[q])
        # reconstruim functia de tranzitie
        new_transitions = {}
        for (q, a), target in self.d.items():
            if q in state_map:
                new_q = state_map[q]
                new_target_mapped = state_map[target]
                new_transitions[(new_q, a)] = new_target_mapped

        return DFA(self.S, new_states, new_start, new_transitions, new_final)


    def remap_states[OTHER_STATE](self, f: 'Callable[[STATE], OTHER_STATE]') -> 'NFA[OTHER_STATE]':
        #multimea starilor
        k = set()
        for q in self.K:
            k.add(f(q))
        #starea initiala
        q0 = f(self.q0)
        #starile finale
        F = set()
        for q in self.F:
            F.add(f(q))
        #functia de tranzitie
        d = {}
        for (state, char), target in self.d.items():
            d[(f(state), char)] = f(target)

        return DFA(self.S, k, q0, d, F)