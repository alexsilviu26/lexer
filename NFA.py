from .DFA import DFA

from dataclasses import dataclass
from collections.abc import Callable

EPSILON = ''  # this is how epsilon is represented by the checker in the transition function of NFAs


@dataclass
class NFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], set[STATE]]
    F: set[STATE]

    def epsilon_closure(self, state: STATE) -> set[STATE]:
        # definim inchiderea
        closure = {state}
        #lista de stari urmatoare
        states = [state]
        #cat timp avem stari urmatorare
        while states:
            #efectuam epsilon tranzitii din prima stare din lista
            for elem in self.d.get((states.pop(),    EPSILON), set()):
                #daca tranzitia nu e in inchidere o adaugam
                if elem not in closure:
                    closure.add(elem)
                    states.append(elem)
                else:
                    continue

        #returnam inchiderea
        return closure

    def subset_construction(self) -> DFA[frozenset[STATE]]:
        epsilon = self.epsilon_closure(self.q0)
        # starea initiala dfa = epsilon closure din q0 nfa
        start_states = frozenset(epsilon)
        # multimea starilor dfa (fiecare e un frozenset de stari nfa)
        dfa_states = {start_states}
        # tranzitii dfa: (stare_dfa, simbol) -> stare_dfa
        dfa_trans: dict[tuple[frozenset[STATE], str], frozenset[STATE]] = {}
        # stari care asteapta procesare
        unprocessed = [start_states]
        # stari finale dfa = orice contine o stare finala nfa
        dfa_final_states = set()
        if self.F.intersection(start_states):
            dfa_final_states.add(start_states)
        while unprocessed:
            current = unprocessed.pop()
            # pentru fiecare simbol din alfabet, fara epsilon
            for elem in self.S:
                if elem == EPSILON:
                    continue
                # move: stari nfa accesibile pe elem
                next_states = set()
                for state in current:
                    next_states.update(self.d.get((state, elem), set()))
                # aplicam epsilon closure pe next_states
                closure = set()
                for s in next_states:
                    closure.update(self.epsilon_closure(s))
                # forma finala a noii stari dfa
                next_frozen = frozenset(closure)
                # inregistram tranzitia
                dfa_trans[(current, elem)] = next_frozen
                # daca e stare noua dfa, o adaugam
                if next_frozen not in dfa_states:
                    #1
                    unprocessed.append(next_frozen)
                    #2
                    dfa_states.add(next_frozen)
                    #3
                    if next_frozen.intersection(self.F):
                    #4
                        dfa_final_states.add(next_frozen)
        # returnam dfa complet
        return DFA(self.S, dfa_states, start_states, dfa_trans, dfa_final_states)

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
            new_targets = set()
            for t in target:
                new_targets.add(f(t))
            d[(f(state), char)] = new_targets

        return NFA(self.S, k, q0, d, F)
