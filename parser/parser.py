# Clase NodoAST
class NodoAST:
    def __init__(self, tipo, valor=None, linea=None, columna=None):
        self.tipo = tipo        # Ej: "Program", "Assign", "BinaryOp", "Identifier", "Print"
        self.valor = valor      # Valor literal o nombre (si aplica)
        self.hijos = []         # Lista de nodos hijos
        self.linea = linea      # Línea en el código (para errores)
        self.columna = columna  # Columna en el código (para errores)

    def agregar_hijo(self, nodo):
        self.hijos.append(nodo)

    def mostrar(self, nivel=0):
        prefix = "  " * nivel
        if self.valor is not None:
            print(f"{prefix}{self.tipo}: {self.valor}")
        else:
            print(f"{prefix}{self.tipo}")
        for hijo in self.hijos:
            hijo.mostrar(nivel + 1)


# --- Parser ---
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errores = []

    # Helpers
    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self):
        tok = self.peek()
        if tok:
            self.pos += 1
        return tok

    def expect(self, tipo=None, valor=None):
        """Consume el token si coincide con tipo y/o valor, sino registra error."""
        tok = self.peek()
        if tok is None:
            self.errores.append("Error sintáctico: fin inesperado de archivo (EOF)")
            return None
        if tipo and tok.tipo != tipo:
            self.errores.append(
                f"Error sintáctico: se esperaba tipo {tipo}, "
                f"pero se encontró {tok.tipo} ('{tok.valor}') en línea {tok.linea}"
            )
            return None
        if valor and tok.valor != valor:
            self.errores.append(
                f"Error sintáctico: se esperaba '{valor}', "
                f"pero se encontró '{tok.valor}' en línea {tok.linea}"
            )
            return None
        return self.advance()

    # Entrada principal
    def parsear(self):
        """Parsea la lista de tokens y devuelve un nodo raíz tipo 'Program'."""
        raiz = NodoAST("Program")
        while self.peek() is not None:
            # Saltar saltos de línea
            if self.peek().tipo == "NEWLINE":
                self.advance()
                continue
            stmt = self.parsear_sentencia()
            if stmt:
                raiz.agregar_hijo(stmt)
            else:
                # Recuperar para evitar bucle infinito
                self.advance()
        return raiz

    # Detecta qué tipo de sentencia se está leyendo
    def parsear_sentencia(self):
        tok = self.peek()
        if tok is None:
            return None

        # --- print(expr) ---
        if tok.tipo == "IDENTIFICADOR" and tok.valor == "print":
            return self.parsear_print()

        # --- asignación: IDENTIFICADOR = EXPRESION ---
        if tok.tipo == "IDENTIFICADOR":
            siguiente = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if siguiente and siguiente.tipo == "OPERADOR_ASIGNACION" and siguiente.valor == "=":
                return self.parsear_asignacion()

            # Expresión suelta
            expr = self.parsear_expresion()
            nodo_expr_stmt = NodoAST("ExprStmt", linea=tok.linea, columna=tok.columna)
            if expr:
                nodo_expr_stmt.agregar_hijo(expr)
                return nodo_expr_stmt
            else:
                self.errores.append(f"Error sintáctico cerca de '{tok.valor}' en línea {tok.linea}")
                return None

        # --- otros casos: literales o expresiones entre paréntesis ---
        if tok.tipo in ("LITERAL_INT", "LITERAL_FLOAT", "LITERAL_STRING") or \
           (tok.tipo == "DELIMITADOR" and tok.valor == "("):
            expr = self.parsear_expresion()
            nodo_expr_stmt = NodoAST("ExprStmt", linea=tok.linea, columna=tok.columna)
            if expr:
                nodo_expr_stmt.agregar_hijo(expr)
                return nodo_expr_stmt
            return None

        self.errores.append(f"Error sintáctico: inicio de sentencia inválido '{tok.valor}' en línea {tok.linea}")
        return None

    # --- print(expr) ---
    def parsear_print(self):
        tok_print = self.expect("IDENTIFICADOR", "print")
        if tok_print is None:
            return None

        if not (self.peek() and self.peek().tipo == "DELIMITADOR" and self.peek().valor == "("):
            self.errores.append(f"Error sintáctico: se esperaba '(' después de 'print' en línea {tok_print.linea}")
            return None
        self.advance()  # consumir '('

        expr = self.parsear_expresion()
        if expr is None:
            self.errores.append(f"Error sintáctico: expresión inválida dentro de print en línea {tok_print.linea}")
            return None

        if not (self.peek() and self.peek().tipo == "DELIMITADOR" and self.peek().valor == ")"):
            self.errores.append(f"Error sintáctico: se esperaba ')' después de print en línea {tok_print.linea}")
            return None
        self.advance()  # consumir ')'

        nodo = NodoAST("Print", linea=tok_print.linea, columna=tok_print.columna)
        nodo.agregar_hijo(expr)
        return nodo

    # --- asignaciones ---
    def parsear_asignacion(self):
        id_tok = self.expect("IDENTIFICADOR")
        if id_tok is None:
            return None
        eq_tok = self.expect("OPERADOR_ASIGNACION", "=")
        if eq_tok is None:
            return None
        expr = self.parsear_expresion()
        if expr is None:
            self.errores.append(f"Error sintáctico: expresión esperada después de '=' en línea {id_tok.linea}")
            return None
        nodo = NodoAST("Assign", id_tok.valor, linea=id_tok.linea, columna=id_tok.columna)
        nodo.agregar_hijo(expr)
        return nodo

    # --- expresiones ---
    def parsear_expresion(self):
        nodo = self.parsear_term()
        if nodo is None:
            return None
        while True:
            tok = self.peek()
            if tok and tok.tipo == "OPERADOR_MATEMATICO" and tok.valor in ("+", "-"):
                op = self.advance()
                derecha = self.parsear_term()
                if derecha is None:
                    self.errores.append(f"Error sintáctico: operando derecho esperado para '{op.valor}' en línea {op.linea}")
                    return None
                nodo_bin = NodoAST("BinaryOp", op.valor, linea=op.linea, columna=op.columna)
                nodo_bin.agregar_hijo(nodo)
                nodo_bin.agregar_hijo(derecha)
                nodo = nodo_bin
            else:
                break
        return nodo

    def parsear_term(self):
        nodo = self.parsear_factor()
        if nodo is None:
            return None
        while True:
            tok = self.peek()
            if tok and tok.tipo == "OPERADOR_MATEMATICO" and tok.valor in ("*", "/", "%"):
                op = self.advance()
                derecha = self.parsear_factor()
                if derecha is None:
                    self.errores.append(f"Error sintáctico: operando derecho esperado para '{op.valor}' en línea {op.linea}")
                    return None
                nodo_bin = NodoAST("BinaryOp", op.valor, linea=op.linea, columna=op.columna)
                nodo_bin.agregar_hijo(nodo)
                nodo_bin.agregar_hijo(derecha)
                nodo = nodo_bin
            else:
                break
        return nodo

    def parsear_factor(self):
        tok = self.peek()
        if tok is None:
            return None
        if tok.tipo in ("LITERAL_INT", "LITERAL_FLOAT", "LITERAL_STRING"):
            self.advance()
            return NodoAST("Literal", tok.valor, linea=tok.linea, columna=tok.columna)
        if tok.tipo == "IDENTIFICADOR":
            self.advance()
            return NodoAST("Identifier", tok.valor, linea=tok.linea, columna=tok.columna)
        if tok.tipo == "DELIMITADOR" and tok.valor == "(":
            self.advance()
            expr = self.parsear_expresion()
            if expr is None:
                self.errores.append(f"Error sintáctico: expresión esperada después de '(' en línea {tok.linea}")
                return None
            if not (self.peek() and self.peek().tipo == "DELIMITADOR" and self.peek().valor == ")"):
                self.errores.append(f"Error sintáctico: se esperaba ')' en línea {tok.linea}")
                return None
            self.advance()
            return expr
        self.errores.append(f"Error sintáctico: token inesperado '{tok.valor}' tipo {tok.tipo} en línea {tok.linea}")
        return None

    def detectar_errores(self):
        return self.errores

    def mostrar_arbol(self, raiz):
        if raiz:
            raiz.mostrar()
        else:
            print("No se generó árbol.")
