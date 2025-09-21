import re
from typing import List, Tuple

class Token:
    def __init__(self, tipo: str, valor: str, linea: int, columna: int):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.columna = columna

    # Retorna una representación del token, por ejemplo:
    # "Token(TIPO='IDENTIFICADOR', VALOR='miVariable', LINEA=5, COLUMNA=10)"
    def __str__(self) -> str:
        return f"Token(tipo='{self.tipo}', valor={repr(self.valor)}, linea={self.linea}, columna={self.columna})"

    # Debugging
    def __repr__(self) -> str:
        return self.__str__()


class Lexer:
    # Recibe el código fuente como cadena
    def __init__(self, codigo_fuente: str):
        self.codigo_fuente = codigo_fuente
        self.tokens: List[Token] = []
        self.linea_actual = 1
        self.columna_actual = 1
        self.posicion_actual = 0
        self.errores: List[str] = []

        # Precompilacion de los patrones de tokens
        self.patrones = self.definir_patrones_compilados()

    # Definicion de los patrones regex para cada tipo de token
    def definir_patrones_compilados(self) -> List[Tuple[str, re.Pattern]]:
        patrones_crudos: List[Tuple[str, str]] = [

            # Comentarios (se ignoran pero deben actualizar posicion)
            ('COMENTARIO', r'#.*'),

            # Docstrings (triple comillas, pueden ser multilinea)
            ('DOCSTRING', r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\''),

            # Saltos de linea (actualizan posicion pero normalmente no generan token)
            ('NEWLINE', r'\n'),

            # Palabras clave de Python
            ('PALABRA_CLAVE', r'\b(?:class|def|return|if|else|while|for|None|True|False)\b'),

            # Operadores logicos
            ('OPERADOR_LOGICO', r'\b(?:and|or|not)\b'),

            # Literales
            ('LITERAL_STRING', r'\"(?:\\.|[^"\\])*\"|\'(?:\\.|[^\'\\])*\''),
            ('LITERAL_FLOAT', r'\b(?:\d+\.\d*|\.\d+)(?:[eE][+-]?\d+)?\b'),
            ('LITERAL_INT', r'\b\d+\b'),

            # Operadores aritmeticos, asignacion y comparacion
            ('OPERADOR_MATEMATICO', r'\*\*|\*|/|\+|-|%'),
            ('OPERADOR_ASIGNACION', r'\+=|-=|\*=|/=|%=|='),
            ('OPERADOR_COMPARACION', r'==|!=|<=|>=|<|>'),

            # Delimitadores
            ('DELIMITADOR', r'[:;,\(\)\[\]\{\}]'),

            # Identificadores
            ('IDENTIFICADOR', r'[A-Za-z_][A-Za-z0-9_]*'),

            # Espacios y tabulaciones
            ('ESPACIO', r'[ \t]+'),

            # Caracter no reconocido
            ('ERROR', r'.'),
        ]

        # Compilar todos patrones para optimizar
        patrones_compilados: List[Tuple[str, re.Pattern]] = []
        for tipo, patron in patrones_crudos:
            patrones_compilados.append((tipo, re.compile(patron, re.MULTILINE)))
        return patrones_compilados

    # Generacion de la lista de tokens del codigo fuente
    def analizar(self) -> List[Token]:
        codigo = self.codigo_fuente
        longitud = len(codigo)

        while self.posicion_actual < longitud:
            coincide = False

            for tipo, regex in self.patrones:
                match = regex.match(codigo, self.posicion_actual)
                if not match:
                    continue

                valor = match.group()
                fin = match.end()

                # Tokens ignorados, pero actualizan posicion
                if tipo in ('COMENTARIO', 'DOCSTRING', 'ESPACIO'):
                    self.actualizar_contadores(valor)
                    self.posicion_actual = fin
                    coincide = True
                    break

                # Actualizar contadores, no generar token
                if tipo == 'NEWLINE':
                    self.actualizar_contadores(valor)
                    self.posicion_actual = fin
                    coincide = True
                    break

                # Error lexico
                if tipo == 'ERROR':
                    self.errores.append(
                        f"Error lexico: Caracter inesperado {repr(valor)} "
                        f"en linea {self.linea_actual}, columna {self.columna_actual}"
                    )
                    self.actualizar_contadores(valor)
                    self.posicion_actual = fin
                    coincide = True
                    break

                # Token valido, se añade a la lista
                token = Token(tipo, valor, self.linea_actual, self.columna_actual)
                self.tokens.append(token)

                # Actualizar posicion
                self.actualizar_contadores(valor)
                self.posicion_actual = fin
                coincide = True
                break

            # Patrones sin match
            if not coincide:
                self.errores.append(
                    f"Error lexico: No se pudo procesar el codigo en posicion {self.posicion_actual}"
                )
                break

        return self.tokens

    # Actualizacion de contadores de linea y columna
    def actualizar_contadores(self, valor: str) -> None:
        if '\n' in valor:
            partes = valor.split('\n')
            num_saltos = len(partes) - 1
            self.linea_actual += num_saltos
            sufijo = partes[-1]
            self.columna_actual = len(sufijo) + 1
        else:
            self.columna_actual += len(valor)

    # Funcion para imprimir tokens encontrados
    def mostrar_tokens(self) -> None:
        for token in self.tokens:
            print(token)

    # Funcion para imprimir errores encontrados
    def mostrar_errores(self) -> None:
        for error in self.errores:
            print(error)