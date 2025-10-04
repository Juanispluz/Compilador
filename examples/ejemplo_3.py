2variable = 10

# l lexer reconocerá el 2 como LITERAL_INT,
# pero después el texto variable se interpretará como IDENTIFICADOR separado →
# no existe un token válido que combine ambos, por lo tanto esto es un error léxico-sintáctico, ya que el parser esperará que la asignación comience con un identificador válido.