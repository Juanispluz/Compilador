class Checker:
    def __init__(self):
        self.tabla_simbolos = {}  # Nombre_variable: tipo
        self.errores = []
        self.funciones_std = {
            'print': ['any']  # Print acepte cualquier tipo
        }

    # Metodo verificar AST
    def verificar(self, ast):
        self.errores = []
        self._verificar_nodo(ast)
        return self.errores

    # Metodo verificar recursivo nodo AST
    def _verificar_nodo(self, nodo, contexto=None):
        if nodo is None:
            return 'unknown'

        tipo_resultado = 'unknown'

        try:
            if nodo.tipo == "Program":
                for hijo in nodo.hijos:
                    self._verificar_nodo(hijo)

            # Asignacion: variable = expresion
            elif nodo.tipo == "Assign":
                
                if len(nodo.hijos) == 1:
                    tipo_expresion = self._verificar_nodo(nodo.hijos[0])

                    # Guardar/actualizar tipo variable tabla simbolos
                    self.tabla_simbolos[nodo.valor] = tipo_expresion
                    tipo_resultado = tipo_expresion

            # Verificar  expresion dentro de print valida
            elif nodo.tipo == "Print":
                if len(nodo.hijos) == 1:
                    tipo_expresion = self._verificar_nodo(nodo.hijos[0])
                    
                    # print aceptar cualquier tipo
                    tipo_resultado = 'void'

            elif nodo.tipo == "BinaryOp":
                # Operaciones binarias: +, -, *, /, %
                if len(nodo.hijos) == 2:
                    tipo_izq = self._verificar_nodo(nodo.hijos[0])
                    tipo_der = self._verificar_nodo(nodo.hijos[1])
                    
                    tipo_resultado = self._verificar_operacion_binaria(nodo.valor, tipo_izq, tipo_der, nodo)
                    
            # Uso variable - verificar existencia
            elif nodo.tipo == "Identifier":
                # No marcar "print" como variable no definida
                if nodo.valor in self.funciones_std:
                    tipo_resultado = 'funcion'
                elif nodo.valor in self.tabla_simbolos:
                    tipo_resultado = self.tabla_simbolos[nodo.valor]
                else:
                    self._agregar_error(f"Variable no definida '{nodo.valor}'", nodo)
                    tipo_resultado = 'unknown'

            # Determinar tipo literal
            elif nodo.tipo == "Literal":
                if nodo.valor is not None:
                    if isinstance(nodo.valor, str):
                        if nodo.valor.startswith(('"', "'")):
                            tipo_resultado = 'string'
                        elif nodo.valor.isdigit() or (nodo.valor.startswith('-') and nodo.valor[1:].isdigit()):
                            tipo_resultado = 'int'
                        elif '.' in nodo.valor or 'e' in nodo.valor.lower():
                            try:
                                float(nodo.valor)
                                tipo_resultado = 'float'
                            except ValueError:
                                tipo_resultado = 'unknown'
                    
                    # Valor tipo Python
                    else:
                        if isinstance(nodo.valor, int):
                            tipo_resultado = 'int'
                        elif isinstance(nodo.valor, float):
                            tipo_resultado = 'float'
                        elif isinstance(nodo.valor, str):
                            tipo_resultado = 'string'
                
                if tipo_resultado == 'unknown':
                    self._agregar_error(f"Tipo de literal no reconocido '{nodo.valor}'", nodo)

            # Expresion statement
            elif nodo.tipo == "ExprStmt":
                if len(nodo.hijos) == 1:
                    tipo_resultado = self._verificar_nodo(nodo.hijos[0])

        except Exception as e:
            self._agregar_error(f"Error durante verificacion semantica: {str(e)}", nodo)

        return tipo_resultado

    # Metodo verificar compatibilidad tipo operaciones binarias
    def _verificar_operacion_binaria(self, operador, tipo_izq, tipo_der, nodo):
        # Operaciones aritmeticas
        operadores_aritmeticos = ['+', '-', '*', '/', '%']
        
        # Verificar ambos operandos sean numericos
        if operador in operadores_aritmeticos:

            # Verificar 1 operando float, resultado = float
            if tipo_izq in ['int', 'float'] and tipo_der in ['int', 'float']:
                if 'float' in [tipo_izq, tipo_der]:
                    return 'float'
                return 'int'
            else:
                self._agregar_error(f"Operacion aritmetica '{operador}' no valida entre {tipo_izq} y {tipo_der}", nodo)
                return 'unknown'

        # Operaciones comparacion
        operadores_comparacion = ['==', '!=', '<', '>', '<=', '>=']
        if operador in operadores_comparacion:
            
            # Compatibles para comparacion
            if tipo_izq == tipo_der and tipo_izq != 'unknown':
                return 'bool'
            elif tipo_izq in ['int', 'float'] and tipo_der in ['int', 'float']:
                return 'bool'
            else:
                self._agregar_error(
                    f"Comparacion '{operador}' no valida entre {tipo_izq} y {tipo_der}",
                    nodo
                )
                return 'unknown'

        return 'unknown'

    # Metodo agregar error a lista de errores
    def _agregar_error(self, mensaje, nodo=None):
        if nodo and hasattr(nodo, 'linea') and hasattr(nodo, 'columna'):
            self.errores.append(f"Error semantico: {mensaje} en linea {nodo.linea}, columna {nodo.columna}")
        elif nodo and hasattr(nodo, 'linea'):
            self.errores.append(f"Error semantico: {mensaje} en linea {nodo.linea}")
        else:
            self.errores.append(f"Error semantico: {mensaje}")

    # Metodo mostrar errores semanticos
    def mostrar_errores(self):
        for error in self.errores:
            print(error)

    # Retorna tabla simbolos actual (Debugging)
    def obtener_tabla_simbolos(self):
        return self.tabla_simbolos.copy()
