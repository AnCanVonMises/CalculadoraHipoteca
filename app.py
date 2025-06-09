import numpy as np
import numpy_financial as npf
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(layout="wide")
st.title("Calculadora Hipoteca y Ahorro")

# Texto explicativo
col_text, col_inputs = st.columns([1, 2])

with col_text:
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
        ">
        <strong>Nota importante:</strong> En un Excel puede poner lo que uno quiera y uno nunca sabe qué pasará en 10 años, menos aún en 30, pero a todos nos gusta jugar con los números.
        <br><br>
        <em style="color:#388e3c;">No he incorporado datos de inflación y ajustes de sueldo porque dejo para el ejemplo que los gastos y el sueldo suban al mismo ritmo. Para reflejar rentabilidad real sumamos la ganancia o pérdida a la rentabilidad esperada.</em>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_inputs:
    c1, c2, c3 = st.columns(3)
    with c1:
        sueldo_mensual = st.number_input("Sueldo mensual (€)", min_value=0, value=3200, step=100)
        ahorros_iniciales = st.number_input("Ahorros iniciales (€)", min_value=0, value=40000, step=1000)
    with c2:
        hipoteca_total = st.number_input("Hipoteca total (€)", min_value=0, value=135000, step=1000)
        interes_anual_pct = st.number_input("Interés anual (%)", min_value=0.0, max_value=100.0, value=3.6, step=0.1)
    with c3:
        plazo_anos = st.number_input("Plazo (años)", min_value=1, value=30, step=1)
        rentabilidad_anual_pct = st.number_input("Rentabilidad anual (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1)

# Variables transformadas
interes_anual = interes_anual_pct / 100
rentabilidad_anual = rentabilidad_anual_pct / 100

# Gastos fijos (podrías añadir inputs si quieres)
gastos_vivienda = 600
gastos_comida = 400
gastos_transporte = 500
gastos_otros = 100

if st.button("Calcular"):

    n_meses = plazo_anos * 12
    interes_mensual = interes_anual / 12
    rentabilidad_mensual = (1 + rentabilidad_anual)**(1/12) - 1

    cuota_mensual = npf.pmt(interes_mensual, n_meses, -hipoteca_total)

    ahorro_acumulado = ahorros_iniciales
    ahorros_por_anio = []
    deuda_real_restante_anual = []
    deuda_vp_restante_anual = []
    punto_muerto_ano = None

    st.write(f"### Cuota mensual de hipoteca: {cuota_mensual:.2f} €")
    st.write(f"Ahorros iniciales: {ahorros_iniciales:.2f} €")

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
        st.success(f"Punto muerto financiero en el año {punto_muerto_ano}. Puedes liquidar la hipoteca con tus ahorros.")
    else:
        st.warning("No se alcanza el punto muerto financiero en el plazo indicado.")

    # Gráfico
    fig, ax = plt.subplots(figsize=(10,5))
    anios = list(range(1, plazo_anos + 1))
    ax.plot(anios, ahorros_por_anio, label='Ahorro acumulado (€)', color='green')
    ax.plot(anios, deuda_real_restante_anual, label='Deuda real restante (€)', color='blue')
    ax.plot(anios, deuda_vp_restante_anual, label='Valor presente deuda (€)', color='orange', linestyle='--')
    if punto_muerto_ano:
        ax.axvline(punto_muerto_ano, color='gray', linestyle='--', label=f'Punto muerto: año {punto_muerto_ano}')
    ax.set_xlabel('Año')
    ax.set_ylabel('Euros')
    ax.set_title('Ahorro acumulado vs. deuda hipotecaria (real y valor presente)')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
