import sys
import os
from lexer.lexer import Lexer
from parser.parser import Parser

def compilar_python_a_cpp(archivo_entrada, mostrar_tokens=False, mostrar_ast=False):
    print(f"=== COMPILADOR PYTHON A C++ ===")
    print(f"Archivo de entrada: {archivo_entrada}")
    print("=" * 50)
    
    # 1 - Leer archivo de entrada
    try:
        with open(archivo_entrada, 'r', encoding='utf-8') as f:
            codigo_fuente = f.read()
        print("Archivo leido correctamente")
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return False
    
    # 2 - Analisis lexico
    print("\n--- FASE 1: ANALISIS LEXICO ---")
    lexer = Lexer(codigo_fuente)
    tokens = lexer.analizar()
    
    if lexer.errores:
        print("Se encontraron errores lexicos:")
        lexer.mostrar_errores()
        return False
    else:
        print("Analisis lexico completado sin errores")
        print(f"Tokens encontrados: {len(tokens)}")
    
    # Mostrar tokens si se solicita
    if mostrar_tokens:
        print("\n--- TOKENS ENCONTRADOS ---")
        lexer.mostrar_tokens()
    
    # 3 - Analisis sintactico
    print("\n--- FASE 2: ANALISIS SINTACTICO ---")
    parser = Parser(tokens)
    ast = parser.parsear()
    
    if parser.errores:
        print("Se encontraron errores sintacticos:")
        for error in parser.errores:
            print(f"{error}")
        return False
    else:
        print("Analisis sintactico completado sin errores")
        print("AST generado correctamente")
    
    # Mostrar AST si se solicita
    if mostrar_ast:
        print("\n--- ARBOL DE SINTAXIS ABSTRACTRA (AST) ---")
        parser.mostrar_arbol(ast)
    
    # 4 - Resumen final
    print("\n" + "=" * 50)
    print("COMPILACION EXITOSA")
    print(f"    -   Tokens procesados: {len(tokens)}")
    print(f"    -   Nodos en el AST: {contar_nodos_ast(ast)}")
    print(f"    -   Archivo de salida: {generar_nombre_salida(archivo_entrada)}")
    print("\nProximo paso: Generar codigo C++ desde el AST")
    
    return True

def contar_nodos_ast(nodo):
    """Cuenta todos los nodos en el AST"""
    if not nodo:
        return 0
    count = 1
    for hijo in nodo.hijos:
        count += contar_nodos_ast(hijo)
    return count

def generar_nombre_salida(archivo_entrada):
    """Genera el nombre del archivo de salida C++"""
    nombre_base = os.path.splitext(archivo_entrada)[0]
    return f"{nombre_base}.cpp"

def mostrar_uso():
    print("Uso: python main.py <archivo.py> [opciones]")
    print("\nOpciones:")
    print(" -t, --tokens        Mostrar lista de tokens")
    print(" -a, --ast           Mostrar el arbol de sintaxis abstracta")
    print(" -h, --help          Mostrar ayuda del programa")
    print("\nEjemplos:")
    print(" python main.py programa.py")
    print(" python main.py programa.py --tokens --ast")

def main():
    if len(sys.argv) < 2:
        mostrar_uso()
        return
    
    archivo_entrada = sys.argv[1]
    
    # Procesar opciones
    mostrar_tokens = False
    mostrar_ast = False
    
    for arg in sys.argv[2:]:
        if arg in ['-t', '--tokens']:
            mostrar_tokens = True
        elif arg in ['-a', '--ast']:
            mostrar_ast = True
        elif arg in ['-h', '--help']:
            mostrar_uso()
            return
        else:
            print(f"Opcion desconocida: {arg}")
            mostrar_uso()
            return
    
    # Verificar que el archivo existe
    if not os.path.exists(archivo_entrada):
        print(f"Error: El archivo '{archivo_entrada}' no existe")
        return
    
    # Ejecutar el compilador
    exito = compilar_python_a_cpp(archivo_entrada, mostrar_tokens, mostrar_ast)
    
    # Codigo de salida
    sys.exit(0 if exito else 1)

if __name__ == "__main__":
    main()