import string
import random

def generar_sscc_local():
    """
    Simula de forma local la asignación de un código SSCC de 8 caracteres
    alfanuméricos en mayúsculas, imitando la respuesta de liquidación de SAP.
    """
    # Definimos el universo de caracteres válidos: Letras mayúsculas (A-Z) y Números (0-9)
    caracteres_validos = string.ascii_uppercase + string.digits
    
    # Seleccionamos 8 caracteres de forma aleatoria
    codigo_aleatorio = "".join(random.choice(caracteres_validos) for _ in range(8))
    
    # Retornamos el formato final para el pallet
    return f"SSCC-{codigo_aleatorio}"