import streamlit as st
import numpy as np
import pandas as pd
import os

# Configuracion de la pagina
st.set_page_config(
    page_title="Sistema BASE - CIRSOC 201-82",
    page_icon="🏗️",
    layout="wide"
)

# Estilo personalizado para el entorno de ingenieria clasica
st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #1E3A8A; margin-bottom: 20px; }
    .section-title { font-size: 22px; font-weight: bold; color: #2563EB; margin-top: 15px; }
    .success-text { color: #16A34A; font-weight: bold; }
    .danger-text { color: #DC2626; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏗️ Sistema BASE (Copia Exacta Original - CIRSOC 201-82)</div>', unsafe_allow_html=True)
st.write("Dimensionamiento de fundaciones superficiales. Unidades convencionales: Toneladas, Metros y kg/cm2.")

# ==============================================================================
# GESTION DE PROYECTOS Y ALMACENAMIENTO DE BASES
# ==============================================================================
st.sidebar.title("📁 Gestion del Proyecto")
nombre_proyecto = st.sidebar.text_input("Nombre del Proyecto:", value="PH_Quesada").strip().replace(" ", "_")
archivo_csv = f"bases_{nombre_proyecto}.csv"

# Inicializar sesion o cargar archivo existente
if "historial_bases" not in st.session_state:
    if os.path.exists(archivo_csv):
        st.session_state.historial_bases = pd.read_csv(archivo_csv).to_dict(orient="records")
    else:
        st.session_state.historial_bases = []

# Seleccion de Modulo Principal
st.sidebar.markdown("---")
st.sidebar.title("Modulos de Calculo")
modulo = st.sidebar.radio(
    "Seleccione el componente a calcular:",
    ["Bases Aisladas (DIMBASE)", "Fundaciones Continuas (DIMSOLE)", "Tensores y Vigas (DIMTENS)"]
)

# Parametros Globales de Materiales - Unidades en kg/cm2 segun CIRSOC 82
st.sidebar.markdown("---")
st.sidebar.markdown("**Propiedades de los Materiales (CIRSOC 82)**")
calidad_h = st.sidebar.selectbox("Calidad del Hormigon", ["H-13 (sigma_b_adm = 60 kg/cm2)", "H-17 (sigma_b_adm = 85 kg/cm2)", "H-21 (sigma_b_adm = 105 kg/cm2)"], index=1)
calidad_a = st.sidebar.selectbox("Tipo de Acero", ["ADN-420 (sigma_s_adm = 2400 kg/cm2)", "AL-220 (sigma_s_adm = 1400 kg/cm2)"], index=0)

# Asignacion manual de tensiones admisibles en kg/cm2 y punzonado admisible en kg/cm2
sigma_b_adm = 85.0 if "H-17" in calidad_h else (105.0 if "H-21" in calidad_h else 60.0)
tau_p_adm = 5.5 if "H-17" in calidad_h else (6.5 if "H-21" in calidad_h else 4.5)
sigma_s_adm = 2400.0 if "ADN-420" in calidad_a else 1400.0

recubrimiento_m = st.sidebar.slider("Recubrimiento mecanico (r) [m]", 0.03, 0.08, 0.05, 0.005)

# ==============================================================================
# MÓDULO 1: BASES AISLADAS (DIMBASE) + REFUERZO ADMISIBLE (BAC-BE)
# ==============================================================================
if modulo == "Bases Aisladas (DIMBASE)":
    st.markdown('<div class="section-title">Modulo: Zapatas Aisladas con Flexion Compuesta Fiel a DOS</div>', unsafe_allow_html=True)
    
    col_id1, col_id2 = st.columns(2)
    with col_id1:
        etiqueta_base = st.text_input("Identificacion de la Base (ej. B1, Zapata_Eje3):", value="B1")

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

    # Conversion interna del suelo: kg/cm2 a t/m2 -> multiplicamos por 10
    sigma_adm_tm2 = sigma_adm_kg * 10.0

    # Predimensionado original estatico (10% peso propio de la zapata)
    area_min = (P * 1.10) / sigma_adm_tm2
    lado_sug = np.sqrt(area_min)
    st.info(f"💡 **Area de contacto sugerida en planta (Peso Propio = 10%):** {area_min:.2f} m2 -> Lado de base cuadrada: {lado_sug:.2f} m")

    st.markdown("---")
    st.markdown("**Dimensiones de Base Adoptadas [m]**")
    col3, col4, col5 = st.columns(3)
    with col3:
        A = st.number_input("Ancho de Base A (m)", min_value=0.3, value=float(round(lado_sug, 2)), step=0.05)
    with col4:
        B = st.number_input("Largo de Base B (m)", min_value=0.3, value=float(round(lado_sug, 2)), step=0.05)
    with col5:
        H = st.number_input("Altura de Base H (m)", min_value=0.15, value=0.50, step=0.05)

    # Calculo Elastico de Presiones sobre el terreno (en t/m2)
    area = A * B
    Wx = (B * (A**2)) / 6
    Wy = (A * (B**2)) / 6

    sigma_max_tm2 = (P / area) + (Mx / Wx) + (My / Wy)
    sigma_min_tm2 = (P / area) - (Mx / Wx) - (My / Wy)

    # Conversion de tensiones de salida a kg/cm2 (dividimos por 10)
    sigma_max_kg = sigma_max_tm2 / 10.0
    sigma_min_kg = sigma_min_tm2 / 10.0

    st.markdown("**Verificacion del Terreno (Tensiones de Servicio)**")
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.metric("Tension Maxima Calculada", f"{sigma_max_kg:.2f} kg/cm2", delta=f"{sigma_adm_kg - sigma_max_kg:.2f} kg/cm2 remanente", delta_color="normal" if sigma_max_kg <= sigma_adm_kg else "inverse")
    with res_col2:
        st.metric("Tension Minima Calculada", f"{sigma_min_kg:.2f} kg/cm2")

    if sigma_max_kg <= sigma_adm_kg and sigma_min_kg >= 0:
        st.markdown('<span class="success-text">✅ VERIFICA GEOTECNIA: Presiones bajo el limite admisible del suelo.</span>', unsafe_allow_html=True)
    elif sigma_max_kg <= sigma_adm_kg and sigma_min_kg < 0:
        st.markdown('<span class="danger-text">⚠️ ALERTA: Hay zonas con despegue de la zapata (Tension Minima < 0). Modifique las dimensiones de la planta.</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="danger-text">❌ RECHAZADO: Se excede la tension admisible del terreno.</span>', unsafe_allow_html=True)

    # Verificacion de Altura Minima por Punzonado
    st.markdown("---")
    st.markdown("**📐 Apartado: Verificacion de Altura Mínima por Punzonado (CIRSOC 82)**")
    
    d = H - recubrimiento_m
    b0 = 2.0 * ((cx + d) + (cy + d))
    V_punz = P * (1.0 - ((cx + d) * (cy + d)) / area)
    tau_p_actuante = (V_punz / (b0 * d)) / 10.0
    
    d_min_teorico = (V_punz / (2.0 * (cx + cy) * tau_p_adm * 10.0))**0.5 if (cx+cy) > 0 else 0.0
    H_min_sugerida = d_min_teorico + recubrimiento_m

    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.metric("Tension Actuante de Punzonado", f"{tau_p_actuante:.2f} kg/cm2")
        st.write(f"Tension Admisible del Hormigon (tau_p_adm): **{tau_p_adm:.2f} kg/cm2**")
    with col_h2:
        st.metric("Altura Total Minima Estruct. Sugerida", f"{H_min_sugerida:.2f} m")

    if tau_p_actuante <= tau_p_adm:
        st.markdown(f'<span class="success-text">✅ ALTURA CORRECTA: H = {H:.2f} m es suficiente. No hay riesgo de punzonado estructural.</span>', unsafe_allow_html=True)
    else:
        st.markdown(f'<span class="danger-text">❌ ESPESOR INSUFICIENTE: H = {H:.2f} m falla por punzonado. Incremente la altura inmediatamente (Minimo sugerido: {H_min_sugerida:.2f} m).</span>', unsafe_allow_html=True)

    # Calculo Estructural de Armaduras - Metodo Elastico CIRSOC 82
    st.markdown("---")
    st.markdown("**Modulo de Armaduras (Logica Original BAC-BE - Sin Mayoracion)**")
    
    q_serv = P / area 
    vuelo_x = (A - cx) / 2
    vuelo_y = (B - cy) / 2
    
    M_x_serv = (q_serv * B * (vuelo_x**2)) / 2
    M_y_serv = (q_serv * A * (vuelo_y**2)) / 2
    
    z_aprox = 0.875 * d
    As_x_req = (M_x_serv * 100000.0) / (sigma_s_adm * (z_aprox * 100.0))
    As_y_req = (M_y_serv * 100000.0) / (sigma_s_adm * (z_aprox * 100.0))
    
    listado_diametros = [6, 8, 10, 12, 16, 20, 25]
    
    arm_col1, arm_col2 = st.columns(2)
    with arm_col1:
        st.markdown(f"**Flexion X (Momento M_x: {M_x_serv:.2f} t.m)**")
        st.write(f"Seccion de acero necesaria: **{As_x_req:.2f} cm2**")
        barra_x = st.selectbox("Diametro del hierro X (mm)", listado_diametros, index=3)
        area_barra_x = np.pi * (barra_x / 20.0)**2
        cant_barras_x = int(np.ceil(As_x_req / area_barra_x))
        st.success(f"Disponer en parrilla: **{max(cant_barras_x, 5)} o {barra_x}**")
        
    with arm_col2:
        st.markdown(f"**Flexion Y (Momento M_y: {M_y_serv:.2f} t.m)**")
        st.write(f"Seccion de acero necesaria: **{As_y_req:.2f} cm2**")
        barra_y = st.selectbox("Diametro del hierro Y (mm)", listado_diametros, index=3)
        area_barra_y = np.pi * (barra_y / 20.0)**2
        cant_barras_y = int(np.ceil(As_y_req / area_barra_y))
        st.success(f"Disponer en parrilla: **{max(cant_barras_y, 5)} o {barra_y}**")

    st.markdown("---")
    st.markdown("**💾 Registro y Almacenamiento de Datos (Spreadsheet Link)**")
    
    if st.button("Guardar / Actualizar Base en el Historial del Proyecto"):
        as_x_val = round(As_x_req, 2)
        as_y_val = round(As_y_req, 2)
        txt_arm_x = f"{max(cant_barras_x, 5)}o{barra_x}"
        txt_arm_y = f"{max(cant_barras_y, 5)}o{barra_y}"
        
        nueva_base = {
            "ID_Base": etiqueta_base,
            "Modulo": "Aislada",
            "P_t": P, "Mx_tm": Mx, "My_tm": My,
            "Sigma_Suelo_kgcm2": sigma_adm_kg,
            "A_m": A, "B_m": B, "H_m": H,
            "Sigma_Max_kgcm2": round(sigma_max_kg, 2),
            "Tau_Punz_kgcm2": round(tau_p_actuante, 2),
            "As_X_cm2": as_x_val, "Armadura_X": txt_arm_x,
