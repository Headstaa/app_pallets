import string
import random

def generar_sscc_local():
    """
    Simula de forma local la asignación de un código SSCC de 8 digitos, 
    imitando la respuesta de liquidación de SAP.
    """
    
    # Seleccionamos 8 digitos de forma aleatoria
    codigo_aleatorio = "".join(random.choice(string.digits) for _ in range(8))
    
    # Retornamos el código final para el pallet
    return codigo_aleatorio
