
def obtener_bd():
    host = "localhost"
    puerto = "27017"
    usuario = "parzibyte"
    palabra_secreta = "hunter2"
    base_de_datos = "tienda"
    cliente = MongoClient("mongodb://{}:{}@{}:{}".format(usuario, palabra_secreta, host, puerto))
    return cliente[base_de_datos]