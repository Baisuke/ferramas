# utils.py

import bcchapi

def obtener_valores_monedas(fecha='2024-10-28'):
    siete = bcchapi.Siete(file="credenciales.txt")

    # Series de monedas disponibles
    series_monedas = {
        "dolar": "F073.TCO.PRE.Z.D",
        "euro": "F072.CLP.EUR.N.O.D",
        "libra": "F072.CLP.GBP.N.O.D",
        "yen": "F072.CLP.JPY.N.O.D"
    }

    valores_monedas = {}

    for moneda, serie in series_monedas.items():
        try:
            retcuadro = siete.cuadro(series=[serie], nombres=[moneda], desde=fecha, hasta=fecha)
            if not retcuadro.empty:
                valor_moneda = retcuadro.iloc[0, 0]
                if valor_moneda is None or valor_moneda <= 0:
                    raise ValueError(f"El valor de {moneda} no es válido.")
                valores_monedas[moneda] = valor_moneda
            else:
                print(f"No se encontraron datos para {moneda} en la fecha {fecha}")
                valores_monedas[moneda] = 1  # Valor predeterminado si no hay datos
        except Exception as e:
            print(f"Error al obtener el valor de {moneda}: {e}")
            valores_monedas[moneda] = 1  # Valor predeterminado en caso de error

    return valores_monedas
