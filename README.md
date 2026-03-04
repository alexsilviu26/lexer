# Lexer – Python Project (2026)

A Python lexer built using **regular expressions + automata theory**:
- parses regex into an AST (Shunting-Yard)
- builds an **NFA** using **Thompson construction**
- converts NFA → **DFA** using **subset construction**
- tokenizes input using **longest-match** + **priority** (spec order)

GitHub: https://github.com/alexsilviu26/lexer

---

## Features

-  Regex parsing into an AST
-  Thompson construction for NFA generation
-  Combine multiple token NFAs into a single NFA (one global start state)
-  NFA → DFA via subset construction
-  Longest prefix matching (maximal munch)
-  Token priority resolution (earlier rules in `spec` win)
-  Line/column error reporting (`No viable alternative ...`)

---

## Supported Regex Syntax

Operators:
- `|` : union
- concatenation : implicit (internally inserted as `&`)
- `*` : Kleene star
- `+` : one or more
- `?` : optional

Special:
- `eps` : epsilon transition (internally represented as `#`)
- escaped characters: `\\n`, `\\t`, `\\r`, `\\x` (general escaping supported)
- syntactic sugar:
  - `[a-z]`, `[A-Z]`, `[0-9]` expanded into explicit unions

---

## How It Works

### 1) Regex → AST
`parse_regex()`:
- preprocesses escapes, spaces, and syntactic sugar
- inserts explicit concatenation operator (`&`)
- uses **Shunting-Yard** to convert to postfix
- builds an AST with nodes like:
  - `Character`, `Epsilon`
  - `Concat`, `Union`
  - `Star`, `Plus`, `Optional`

### 2) AST → NFA (Thompson)
Each AST node implements `thompson()` and returns an `NFA[int]`.

Examples:
- `Character(c)` creates a 2-state NFA with one `c` transition
- `Union(a, b)` creates a new start/end with epsilon edges
- `Concat(a, b)` epsilon-links final states of `a` to start of `b`
- `Star(r)` adds looping epsilon edges for repetition

### 3) Build a Global Lexer Automaton
`Lexer(spec)`:
- builds one NFA per token regex
- **remaps states** to avoid collisions: `(token_index, state)`
- creates a new start state `LEXER_START` and adds epsilon transitions to each token NFA start
- records final states as `(priority, token_name)`

### 4) NFA → DFA
The combined NFA is transformed into a DFA using **subset construction**.

### 5) Tokenization
`lex(word)`:
- scans input and finds the **longest valid prefix**
- when multiple tokens match, chooses the one with the **smallest priority** (earliest in spec)
- tracks `line_number` and `column` for precise error messages

---
