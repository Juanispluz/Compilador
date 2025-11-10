import os

class CodeGenerator:
    def __init__(self, ast):
        self.ast = ast

    def generar_codigo(self):
        lineas = [
            "#include <iostream>",
            "using namespace std;",
            "",
            "int main() {"
        ]

        for nodo in self.ast.hijos:
            linea_cpp = self._convertir_nodo(nodo)
            if linea_cpp:
                lineas.append(linea_cpp)

        lineas.append("    return 0;")
        lineas.append("}")
        return "\n".join(lineas)

    # Traduce cada tipo de nodo del AST a código C++
    def _convertir_nodo(self, nodo):
        if nodo.tipo == "Assign":
            expr = self._convertir_expresion(nodo.hijos[0])
            return f"    int {nodo.valor} = {expr};"

        elif nodo.tipo == "Print":
            expr = self._convertir_expresion(nodo.hijos[0])
            return f"    cout << {expr} << endl;"

        elif nodo.tipo == "ExprStmt":
            expr = self._convertir_expresion(nodo.hijos[0])
            return f"    {expr};"

        else:
            return f"    // Nodo no reconocido: {nodo.tipo}"

    # Traduce expresiones recursivamente
    def _convertir_expresion(self, nodo):
        if nodo.tipo == "Literal":
            # Asegura que las cadenas mantengan comillas
            if not (nodo.valor.startswith('"') or nodo.valor.startswith("'")):
                return nodo.valor
            return nodo.valor  

        elif nodo.tipo == "Identifier":
            return nodo.valor

        elif nodo.tipo == "BinaryOp":
            izq = self._convertir_expresion(nodo.hijos[0])
            der = self._convertir_expresion(nodo.hijos[1])
            return f"({izq} {nodo.valor} {der})"

        else:
            return "0"
