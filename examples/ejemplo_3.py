2variable = 10

# El lexer reconocerá el 2 como LITERAL_INT,
# pero después el texto variable se interpretará como un identificador separado;
# no existe un token válido que combine ambos, por lo tanto esto es un error léxico-sintáctico, 
# ya que el parser esperara la asignacion de un identificador valido