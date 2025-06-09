

import streamlit as st
import numpy as np
import numpy_financial as npf
import matplotlib.pyplot as plt

st.title("Calculadora Hipoteca y Ahorro")


st.markdown(
    """
    <div style="
        border: 1.5px solid #4CAF50;
        padding: 20px;
        border-radius: 12px;
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #2e7d32;
        font-size: 18px;
        line-height: 1.6;
        transition: transform 0.3s ease;
    "
    onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'"
    >
    <strong>Nota importante:</strong> En un Excel puede poner lo que uno quiera y uno nunca sabe qué pasará en 10 años, menos aún en 30, pero a todos nos gusta jugar con los números.
    <br><br>
    <em style="color:#388e3c;">No he incorporado datos de inflación y ajustes de sueldo porque dejo para el ejemplo que los gastos y el sueldo suban al mismo ritmo. Para reflejar rentabilidad real sumamos la ganancia o pérdida a la rentabilidad esperada.</em>
    </div>
    
    
    <div>   
    
    <div>
    """,
    unsafe_allow_html=True
)


# Entrada de datos sin valores por defecto y con instrucciones claras
hipoteca_total = st.number_input("Importe hipoteca (€)", min_value=0.0, format="%.2f")
interes_anual = st.number_input("Interés anual (%)", min_value=0.0, format="%.4f") / 100  # Convertimos a decimal
plazo_anos = st.number_input("Plazo hipoteca (años)", min_value=1, step=1)
sueldo_mensual = st.number_input("Sueldo mensual (€)", min_value=0.0, format="%.2f")
ahorros_iniciales = st.number_input("Ahorros iniciales (€)", min_value=0.0, format="%.2f")

st.markdown("### Gastos mensuales (€)")
gastos_vivienda = st.number_input("Gastos vivienda", min_value=0.0, format="%.2f")
gastos_comida = st.number_input("Gastos comida", min_value=0.0, format="%.2f")
gastos_transporte = st.number_input("Gastos transporte", min_value=0.0, format="%.2f")
gastos_otros = st.number_input("Otros gastos", min_value=0.0, format="%.2f")

rentabilidad_anual = st.number_input("Rentabilidad anual esperada (%)", min_value=0.0, format="%.4f") / 100

# Botón para ejecutar el cálculo solo si todos los valores son válidos
if st.button("Calcular"):

    # Validación básica de entrada
    if hipoteca_total <= 0 or interes_anual <= 0 or plazo_anos <= 0 or sueldo_mensual <= 0:
        st.error("Por favor, introduce valores positivos y mayores que cero en hipoteca, interés, plazo y sueldo.")
    else:
        n_meses = int(plazo_anos * 12)
        interes_mensual = interes_anual / 12
        rentabilidad_mensual = (1 + rentabilidad_anual)**(1/12) - 1

        cuota_mensual = npf.pmt(interes_mensual, n_meses, -hipoteca_total)

        ahorro_acumulado = ahorros_iniciales
        ahorros_por_anio = []
        deuda_real_restante_anual = []
        deuda_vp_restante_anual = []
        punto_muerto_ano = None

        st.write(f"### Cuota mensual de hipoteca: {cuota_mensual:.2f} €")

        for anio in range(1, plazo_anos + 1):
            meses_restantes = n_meses - (anio - 1) * 12

            for mes in range(12):
                ahorro_acumulado *= (1 + rentabilidad_mensual)
                gastos_totales = gastos_vivienda + gastos_comida + gastos_transporte + gastos_otros + cuota_mensual
                ahorro_mes = sueldo_mensual - gastos_totales
                ahorro_acumulado += ahorro_mes

            deuda_real_restante = cuota_mensual * meses_restantes
            deuda_vp_restante = -npf.pv(interes_mensual, meses_restantes, cuota_mensual)

            ahorros_por_anio.append(ahorro_acumulado)
            deuda_real_restante_anual.append(deuda_real_restante)
            deuda_vp_restante_anual.append(deuda_vp_restante)

            if ahorro_acumulado >= deuda_real_restante and punto_muerto_ano is None:
                punto_muerto_ano = anio

        if punto_muerto_ano:
            st.success(f"✅ Punto muerto financiero en el año {punto_muerto_ano}. Podrías liquidar la hipoteca con tus ahorros.")
        else:
            st.warning("❌ No se alcanza el punto muerto financiero en 30 años.")

        # Gráfico
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(range(1, plazo_anos + 1), ahorros_por_anio, label='Ahorro acumulado (€)', color='green')
        ax.plot(range(1, plazo_anos + 1), deuda_real_restante_anual, label='Deuda real restante (€)', color='blue')
        ax.plot(range(1, plazo_anos + 1), deuda_vp_restante_anual, label='Valor presente deuda (€)', color='orange', linestyle='--')

        if punto_muerto_ano:
            ax.axvline(punto_muerto_ano, color='gray', linestyle='--', label=f'Punto muerto: año {punto_muerto_ano}')

        ax.set_xlabel('Año')
        ax.set_ylabel('Euros')
        ax.set_title('Ahorro acumulado vs. deuda hipotecaria (real y valor presente)')
        ax.legend()
        ax.grid(True)

        st.pyplot(fig)
