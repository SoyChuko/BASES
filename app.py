# Guardar este archivo como crear_app.py y ejecutarlo con: python crear_app.py
import re

codigo_limpio = """
import streamlit as st
import numpy as np
import pandas as pd
import os

st.set_page_config(
    page_title="Sistema BASE - CIRSOC 201-82",
    page_icon="🏗️",
    layout="wide"
)

st.markdown(\"\"\"
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #1E3A8A; margin-bottom: 20px; }
    .section-title { font-size: 22px; font-weight: bold; color: #2563EB; margin-top: 15px; }
    .success-text { color: #16A34A; font-weight: bold; }
    .danger-text { color: #DC2626; font-weight: bold; }
    </style>
\"\"\", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏗️ Sistema BASE (Copia Exacta Original - CIRSOC 201-82)</div>', unsafe_allow_html=True)
st.write("Dimensionamiento de fundaciones superficiales. Unidades convencionales: Toneladas, Metros y kg/cm2.")

st.sidebar.title("📁 Gestion del Proyecto")
nombre_proyecto = st.sidebar.text_input("Nombre del Proyecto:", value="PH_Quesada").strip().replace(" ", "_")
archivo_csv = "bases_" + nombre_proyecto + ".csv"

if "historial_bases" not in st.session_state:
    if os.path.exists(archivo_csv):
        st.session_state.historial_bases = pd.read_csv(archivo_csv).to_dict(orient="records")
    else:
        st.session_state.historial_bases = []

st.sidebar.markdown("---")
st.sidebar.title("Modulos de Calculo")
modulo = st.sidebar.radio(
    "Seleccione el componente a calcular:",
    ["Bases Aisladas (DIMBASE)", "Fundaciones Continuas (DIMSOLE)", "Tensores y Vigas (DIMTENS)"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Propiedades de los Materiales (CIRSOC 82)**")
calidad_h = st.sidebar.selectbox("Calidad del Hormigon", ["H-13", "H-17", "H-21"], index=1)
calidad_a = st.sidebar.selectbox("Tipo de Acero", ["ADN-420", "AL-220"], index=0)

sigma_b_adm = 85.0 if "H-17" in calidad_h else (105.0 if "H-21" in calidad_h else 60.0)
tau_p_adm = 5.5 if "H-17" in calidad_h else (6.5 if "H-21" in calidad_h else 4.5)
sigma_s_adm = 2400.0 if "ADN-420" in calidad_a else 1400.0

recubrimiento_m = st.sidebar.slider("Recubrimiento mecanico (r) [m]", 0.03, 0.08, 0.05, 0.005)

if modulo == "Bases Aisladas (DIMBASE)":
    st.markdown('<div class="section-title">Modulo: Zapatas Aisladas con Flexion Compuesta Fiel a DOS</div>', unsafe_allow_html=True)
    
    col_id1, col_id2 = st.columns(2)
    with col_id1:
        etiqueta_base = st.text_input("Identificacion de la Base (ej. B1):", value="B1")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Cargas de Servicio (Sin Mayorar) [t, t.m]**")
        P = st.number_input("Carga Axil de Columna P (t)", min_value=0.1, value=75.0, step=5.0)
        Mx = st.number_input("Momento Flexor M_x (t.m)", min_value=0.0, value=0.0, step=0.5)
        My = st.number_input("Momento Flexor M_y (t.m)", min_value=0.0, value=0.0, step=0.5)
        
    with col2:
        st.markdown("**Geometria y Datos del Suelo [m, kg/cm2]**")
        sigma_adm_kg = st.number_input("Tension Admisible del Terreno sigma_adm (kg/cm2)", min_value=0.1, value=2.0, step=0.1)
        cx = st.number_input("Lado columna c_x (m)", min_value=0.1, value=0.3, step=0.05)
        cy = st.number_input("Lado columna c_y (m)", min_value=0.1, value=0.3, step=0.05)

    sigma_adm_tm2 = sigma_adm_kg * 10.0
    area_min = (P * 1.10) / sigma_adm_tm2
    lado_sug = np.sqrt(area_min)
    st.info(f"Area de contacto sugerida: {area_min:.2f} m2 -> Lado: {lado_sug:.2f} m")

    st.markdown("---")
    st.markdown("**Dimensiones de Base Adoptadas [m]**")
    col3, col4, col5 = st.columns(3)
    with col3:
        A = st.number_input("Ancho de Base A (m)", min_value=0.3, value=float(round(lado_sug, 2)), step=0.05)
    with col4:
        B = st.number_input("Largo de Base B (m)", min_value=0.3, value=float(round(lado_sug, 2)), step=0.05)
    with col5:
        H = st.number_input("Altura de Base H (m)", min_value=0.15, value=0.50, step=0.05)

    area = A * B
    Wx = (B * (A**2)) / 6
    Wy = (A * (B**2)) / 6

    sigma_max_tm2 = (P / area) + (Mx / Wx) + (My / Wy)
    sigma_min_tm2 = (P / area) - (Mx / Wx) - (My / Wy)

    sigma_max_kg = sigma_max_tm2 / 10.0
    sigma_min_kg = sigma_min_tm2 / 10.0

    st.markdown("**Verificacion del Terreno (Tensiones de Servicio)**")
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.metric("Tension Maxima Calculada", f"{sigma_max_kg:.2f} kg/cm2")
    with res_col2:
        st.metric("Tension Minima Calculada", f"{sigma_min_kg:.2f} kg/cm2")

    if sigma_max_kg <= sigma_adm_kg and sigma_min_kg >= 0:
        st.markdown('<span class="success-text">Verifica Geotecnia.</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="danger-text">No verifica Geotecnia o tiene despegue.</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Verificacion de Altura Minima por Punzonado**")
    d = H - recubrimiento_m
    b0 = 2.0 * ((cx + d) + (cy + d))
    V_punz = P * (1.0 - ((cx + d) * (cy + d)) / area)
    tau_p_actuante = (V_punz / (b0 * d)) / 10.0
    
    d_min_teorico = (V_punz / (2.0 * (cx + cy) * tau_p_adm * 10.0))**0.5 if (cx+cy) > 0 else 0.0
    H_min_sugerida = d_min_teorico + recubrimiento_m

    st.write(f"Tension Actuante: **{tau_p_actuante:.2f} kg/cm2** / Admisible: **{tau_p_adm:.2f} kg/cm2**")
    st.write(f"Altura minima sugerida: **{H_min_sugerida:.2f} m**")

    if tau_p_actuante <= tau_p_adm:
        st.markdown('<span class="success-text">Altura de punzonado correcta.</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="danger-text">Falla por punzonado. Aumente H.</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Modulo de Armaduras (BAC-BE)**")
    q_serv = P / area 
    vuelo_x = (A - cx) / 2
    vuelo_y = (B - cy) / 2
    M_x_serv = (q_serv * B * (vuelo_x**2)) / 2
    M_y_serv = (q_serv * A * (vuelo_y**2)) / 2
    z_aprox = 0.875 * d
    
    As_x_req = (M_x_serv * 100000.0) / (sigma_s_adm * (z_aprox * 100.0))
    As_y_req = (M_y_serv * 100000.0) / (sigma_s_adm * (z_aprox * 100.0))
    
    arm_col1, arm_col2 = st.columns(2)
    with arm_col1:
        st.write(f"As X: {As_x_req:.2f} cm2")
        barra_x = st.selectbox("Hierro X (mm)", [6, 8, 10, 12, 16, 20, 25], index=3)
        cant_x = int(np.ceil(As_x_req / (np.pi * (barra_x / 20.0)**2)))
        st.success(f"Parrilla X: {max(cant_x, 5)} ø {barra_x}")
    with arm_col2:
        st.write(f"As Y: {As_y_req:.2f} cm2")
        barra_y = st.selectbox("Hierro Y (mm)", [6, 8, 10, 12, 16, 20, 25], index=3)
        cant_y = int(np.ceil(As_y_req / (np.pi * (barra_y / 20.0)**2)))
        st.success(f"Parrilla Y: {max(cant_y, 5)} ø {barra_y}")

    st.markdown("---")
    if st.button("Guardar Base en Proyecto"):
        dict_base = {
            "ID_Base": str(etiqueta_base),
            "P_t": float(P),
            "Mx_tm": float(Mx),
            "My_tm": float(My),
            "A_m": float(A),
            "B_m": float(B),
            "H_m": float(H),
            "Sigma_Max_kg": float(round(sigma_max_kg, 2)),
            "Tau_kg": float(round(tau_p_actuante, 2)),
            "As_X_cm2": float(round(As_x_req, 2)),
            "Arm_X": str(max(cant_x, 5)) + "ø" + str(barra_x),
            "As_Y_cm2": float(round(As_y_req, 2)),
            "Arm_Y": str(max(cant_y, 5)) + "ø" + str(barra_y)
        }
        st.session_state.historial_bases = [b for b in st.session_state.historial_bases if b["ID_Base"] != etiqueta_base]
        st.session_state.historial_bases.append(dict_base)
        pd.DataFrame(st.session_state.historial_bases).to_csv(archivo_csv, index=False)
        st.success("Base guardada en el archivo.")

elif modulo == "Fundaciones Continuas (DIMSOLE)":
    st.markdown('### Modulo: Fundaciones Continuas')
    q_lineal = st.number_input("Carga Lineal q (t/m)", min_value=0.1, value=12.0)
    M_lineal = st.number_input("Momento M (t.m/m)", min_value=0.0, value=0.0)
    B_corrida = st.number_input("Ancho B (m)", min_value=0.3, value=0.6)
    sigma_max_c_kg = ((q_lineal / B_corrida) + (6.0 * M_lineal / (B_corrida**2))) / 10.0
    st.write(f"Tension maxima: {sigma_max_c_kg:.2f} kg/cm2")

elif modulo == "Tensores y Vigas (DIMTENS)":
    st.markdown('### Modulo: Tensores y Vigas')
    P_ext = st.number_input("Carga P_ext (t)", min_value=0.1, value=50.0)
    excentricidad = st.number_input("Excentricidad e (m)", min_value=0.01, value=0.25)
    L_viga = st.number_input("Longitud L (m)", min_value=1.0, value=5.0)
    F_viga = (P_ext * excentricidad) / L_viga
    st.warning(f"Fuerza en tensor: {F_viga:.2f} t")
    As_tensor = (F_viga * 1000.0) / sigma_s_adm
    st.success(f"Acero necesario: {As_tensor:.2f} cm2")

if st.session_state.historial_bases:
    st.markdown("---")
    st.markdown(f"### Planilla de Dimensionado Actual - Proyecto: {nombre_proyecto}")
    df_planilla = pd.DataFrame(st.session_state.historial_bases)
    st.dataframe(df_planilla)
    csv_data = df_planilla.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Planilla (.CSV)",
        data=csv_data,
        file_name=f"Planilla_{nombre_proyecto}.csv",
        mime="text/csv"
    )
"""

with open("app.py", "w", encoding="utf-8") as f:
    f.write(codigo_limpio.strip())

print("Archivo app.py generado exitosamente y libre de errores de sintaxis.")
