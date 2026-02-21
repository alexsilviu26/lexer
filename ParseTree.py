from __future__ import annotations

class ParseTree:

    def __init__(self, name:str, token: tuple[str, str] = None):
        self.name: str = name
        self.children: list[ParseTree] = []
        self.token: str = token

    def add_children(self, child: ParseTree):
        self.children.append(child)
    
    def to_string(self, indent=0):
        pad = "  " * indent  
        if self.token:
            # Nod terminal
            s = f"{pad}({self.token[0]}: {self.token[1]})"
        else:
            # Nod cu regula intermediara
            if self.name.startswith("int_"):
                s = ""
                for child in self.children:
                    s += "\n" + child.to_string(indent)
                s = s[1:]
            # Nod normal cu o regula principala
            else:
                s = f"{pad}{self.name}"

                for child in self.children:
                    s += "\n" + child.to_string(indent + 1)
        return s

    def __str__(self):
        return self.to_string()
            