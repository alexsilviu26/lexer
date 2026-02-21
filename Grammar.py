from .ParseTree import ParseTree
EPSILON = ""

class Grammar:

    @classmethod
    def fromFile(cls, file_name: str):
        with open(file_name, 'r') as f:
            V = set()
            R = set()
            S = None
            line = f.readline().strip()
            while line:
                v, rest = line.split(": ")
                V.add(v)
                if not S:
                    S = v

                alternatives = rest.split("|")
                for alt in alternatives:
                    if " " in alt:
                        n1, n2 = alt.split(" ")
                        V.add(n1)
                        V.add(n2)
                        R.add((v, n1, n2))
                    else: 
                        V.add(alt)
                        R.add((v, alt, None))
            
                line = f.readline().strip()

        return cls(V, R, S)
    
    def __init__(self, V: set[str], R: set[tuple[str, str, str|None]], S: str):
        self.V = V # multimea de neterminali si terminali
        self.R = R # regulile (in FNC)
        self.S = S # simbolul de start
        
    def cykParse(self, w: list[tuple[str, str]]):
        length = len(w)
        #matrice pentru algoritmul CYK
        table = []
        for i in range(length + 1):
            row = []
            for j in range(length):
                row.append({})
            table.append(row)

        #umplerea primei linii
        for i in range(length):
            #tipul token-ului si lexema
            token = w[i][0]
            lexeme = w[i][1]
            #verificam regulile gramaticale
            for rule in self.R:
                x = rule[0]
                y = rule[1]
                z = rule[2]
                #verificam regula sa fie valida
                if z is None:
                    if y == token:
                        #adaugam in tabel
                        table[1][i][x] = ParseTree(x, (token, lexeme))

        #umplerea celorlalte linii
        #j reprezinta lungimea subcuvantului
        for j in range(2, length + 1):
            #i reprezinta pozitia de start a subcuvantului
            for i in range(length - j + 1):
                #k reprezinta pozitia de impartire a subcuvantului
                for k in range(1, j):
                    #verificam regulile gramaticale
                    for rule in self.R:
                        x = rule[0]
                        y = rule[1]
                        z = rule[2]
                        #verificam daca regula este de forma X -> Y Z
                        if z is not None:
                            if y in table[k][i] and z in table[j - k][i + k]:
                                if x not in table[j][i]:
                                    #construim arborele de parsare
                                    tree = ParseTree(x)
                                    tree.add_children(table[k][i][y])
                                    tree.add_children(table[j - k][i + k][z])
                                    table[j][i][x] = tree

        #verificam simbolul de start
        if self.S not in table[length][0]:
            return None
        return table[length][0][self.S]



        

            

