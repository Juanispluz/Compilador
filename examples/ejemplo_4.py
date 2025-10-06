for i in range(5):
    print(i)

# El compilador al ser de un diseño simple, este no evalua los bucles y otras palabras reservadas o tokens en el parser, pero si en el lexer 
# Una solucion a este problema, es el codigo del parser insertar un diccionario de las palabras claves