import streamlit as st
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="Sistema BASE - Ingeniería Estructural",
    page_icon="🏗️",
    layout="wide"
)

# Estilo personalizado para el entorno de ingeniería
st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #1E3A8A; margin-bottom: 20px; }
    .section-title { font-size: 22px; font-weight: bold; color: #2563EB; margin-top: 15px; }
    .success-text { color: #16A34A; font-weight: bold; }
    .danger-text { color: #DC2626; font-weight: bold; }
    </style>
""", unsafe_allowed_html=True)

st.markdown('<div class="main-title">🏗️ Sistema BASE: Dimensionamiento de Fundaciones Superficiales</div>', unsafe_allowed_html=True)
st.write("Versión Web Modernizada. Cálculo de fundaciones, tensores y armaduras según criterios geotécnicos y estructurales.")

# Sidebar - Selección de Módulo Principal
st.sidebar.title("Módulos de Cálculo")
modulo = st.sidebar.radio(
    "Seleccione el componente a calcular:",
    ["Bases Aisladas (DIMBASE)", "Fundaciones Continuas (DIMSOLE)", "Tensores y Vigas (DIMTENS)"]
)

# Parámetros Globales de Materiales (Comunes a los módulos)
st.sidebar.markdown("---")
st.sidebar.markdown("**Propiedades de Materiales**")
f_ck = st.sidebar.selectbox("Hormigón f'c (MPa)", [20, 25, 30, 35], index=1)
f_yk = st.sidebar.selectbox("Acero f'y (MPa)", [420, 500], index=0)
recubrimiento = st.sidebar.slider("Recubrimiento neto (r) [cm]", 3.0, 7.5, 5.0, 0.5)

# ==============================================================================
# MÓDULO 1: BASES AISLADAS (DIMBASE) + ARMADURAS Y PUNZONADO (BAC-BE)
# ==============================================================================
if modulo == "Bases Aisladas (DIMBASE)":
    st.markdown('<div class="section-title">Módulo: Zapatas Aisladas con Flexión Compuesta</div>', unsafe_allowed_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Solicitaciones de Diseño (Valores de Servicio)**")
        P = st.number_input("Carga Axil P (kN)", min_value=1.0, value=750.0, step=50.0)
        Mx = st.number_input("Momento Mx (kN·m)", min_value=0.0, value=45.0, step=5.0)
        My = st.number_input("Momento My (kN·m)", min_value=0.0, value=20.0, step=5.0)
        
    with col2:
        st.markdown("**Geotecnia y Geometría Inicial**")
        sigma_adm = st.number_input("Tensión Admisible del Suelo (kPa o kN/m²)", min_value=10.0, value=200.0, step=10.0)
        cx = st.number_input("Lado de la columna cx (m)", min_value=0.1, value=0.3, step=0.05)
        cy = st.number_input("Lado de la columna cy (m)", min_value=0.1, value=0.3, step=0.05)

    # Predimensionado automático sugerido
    area_min = (P * 1.10) / sigma_adm
    lado_sug = np.sqrt(area_min)
    st.info(f"💡 **Área mínima estimada en planta (con 10% peso propio):** {area_min:.2f} m² → Lado sugerido (cuadrada): {lado_sug:.2f} m")

    st.markdown("---")
    st.markdown("**Dimensiones Adoptadas para Verificación**")
    col3, col4, col5 = st.columns(3)
    with col3:
        A = st.number_input("Lado A de la Base (m)", min_value=0.5, value=float(round(lado_sug, 1)), step=0.05)
    with col4:
        B = st.number_input("Lado B de la Base (m)", min_value=0.5, value=float(round(lado_sug, 1)), step=0.05)
    with col5:
        H = st.number_input("Altura total H de la Base (m)", min_value=0.2, value=0.5, step=0.05)

    # Cálculos Geotécnicos (Tensiones)
    area = A * B
    Wx = (B * (A**2)) / 6
    Wy = (A * (B**2)) / 6

    sigma_max = (P / area) + (Mx / Wx) + (My / Wy)
    sigma_min = (P / area) - (Mx / Wx) - (My / Wy)

    st.markdown("**1. Verificación Geotécnica del Suelo**")
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.metric("Tensión Máxima Actuante", f"{sigma_max:.2f} kPa", delta=f"{sigma_adm - sigma_max:.2f} kPa disp", delta_color="normal" if sigma_max <= sigma_adm else "inverse")
    with res_col2:
        st.metric("Tensión Mínima Actuante", f"{sigma_min:.2f} kPa", help="Un valor negativo indica despegue de la zapata.")

    if sigma_max <= sigma_adm and sigma_min >= 0:
        st.markdown('<span class="success-text">✅ VERIFICA: Las tensiones se encuentran dentro del rango admisible y no hay despegue.</span>', unsafe_allowed_html=True)
    elif sigma_max <= sigma_adm and sigma_min < 0:
        st.markdown('<span class="danger-text">⚠️ ALERTA: Existe despegue en las esquinas de la fundación (Sigma Mín < 0). Aumente las dimensiones.</span>', unsafe_allowed_html=True)
    else:
        st.markdown('<span class="danger-text">❌ NO VERIFICA: La tensión máxima supera la capacidad portante del terreno.</span>', unsafe_allowed_html=True)

    # Cálculo Integrado de Armaduras Estructurales y Punzonado
    st.markdown("---")
    st.markdown("**2. Módulo Estructural: Armaduras y Cortante (BAC-BE)**")
    
    qu = (P * 1.4) / area 
    vuelo_x = (A - cx) / 2
    vuelo_y = (B - cy) / 2
    
    M_ux = (qu * B * (vuelo_x**2)) / 2
    M_uy = (qu * A * (vuelo_y**2)) / 2
    
    d = H - (recubrimiento / 100)
    
    As_x_req = (M_ux * 10**6) / (0.9 * f_yk * 0.9 * (d * 1000))
    As_y_req = (M_uy * 10**6) / (0.9 * f_yk * 0.9 * (d * 1000))
    
    arm_col1, arm_col2 = st.columns(2)
    with arm_col1:
        st.markdown(f"**Dirección X (Momento Mu: {M_ux:.1f} kN·m)**")
        st.write(f"Refuerzo mínimo requerido: **{As_x_req/100:.2f} cm²**")
        barra_x = st.selectbox("Diámetro de barra X (mm)", [8, 10, 12, 16, 20, 25], index=2)
        area_barra_x = np.pi * (barra_x/2)**2
        cant_barras_x = int(np.ceil(As_x_req / area_barra_x))
        st.success(f"Disponer: **{max(cant_barras_x, 5)} ø {barra_x}**")
        
    with arm_col2:
        st.markdown(f"**Dirección Y (Momento Mu: {M_uy:.1f} kN·m)**")
        st.write(f"Refuerzo mínimo requerido: **{As_y_req/100:.2f} cm²**")
        barra_y = st.selectbox("Diámetro de barra Y (mm)", [8, 10, 12, 16, 20, 25], index=2)
        area_barra_y = np.pi * (barra_y/2)**2
        cant_barras_y = int(np.ceil(As_y_req / area_barra_y))
        st.success(f"Disponer: **{max(cant_barras_y, 5)} ø {barra_y}**")

    st.markdown("**Verificación al Punzonado**")
    bo = 2 * ((cx + d) + (cy + d))
    V_u = P * 1.4 * (1 - ((cx + d) * (cy + d)) / area)
    phi_V_c = 0.75 * (1/3) * np.sqrt(f_ck) * bo * d * 1000
    
    if V_u <= phi_V_c:
        st.markdown(f'<span class="success-text">✅ Verificación al punzonado aprobada. Vu ({V_u:.1f} kN) ≤ ϕVc ({phi_V_c:.1f} kN). No requiere refuerzo por corte.</span>', unsafe_allowed_html=True)
    else:
        st.markdown(f'<span class="danger-text">❌ Falla por punzonado. Vu ({V_u:.1f} kN) > ϕVc ({phi_V_c:.1f} kN). Incremente la altura H de la zapata.</span>', unsafe_allowed_html=True)

# ==============================================================================
# MÓDULO 2: FUNDACIONES CONTINUAS (DIMSOLE)
# ==============================================================================
elif modulo == "Fundaciones Continuas (DIMSOLE)":
    st.markdown('<div class="section-title">Módulo: Fundaciones Continuas y Zapatas Corridas</div>', unsafe_allowed_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Cargas del Muro / Alineación**")
        q_lineal = st.number_input("Carga Lineal de Servicio q (kN/m)", min_value=1.0, value=120.0, step=10.0)
        M_lineal = st.number_input("Momento Volcador Lineal M (kN·m/m)", min_value=0.0, value=10.0, step=2.0)
    with col2:
        st.markdown("**Parámetros Geotécnicos**")
        sigma_adm_c = st.number_input("Tensión Admisible del Terreno (kPa)", min_value=10.0, value=150.0, step=10.0)
        espesor_muro = st.number_input("Espesor del muro soportado (m)", min_value=0.1, value=0.2, step=0.05)

    ancho_min = (q_lineal * 1.05) / sigma_adm_c
    st.info(f"💡 **Ancho mínimo estimado de zapata corrida:** {ancho_min:.2f} m")
    
    st.markdown("---")
    B_corrida = st.number_input("Ancho B adoptado para la zapata corrida (m)", min_value=0.3, value=float(round(max(ancho_min, 0.6), 2)), step=0.05)
    H_corrida = st.number_input("Altura H adoptada para la zapata corrida (m)", min_value=0.15, value=0.30, step=0.05)

    W_lineal = (B_corrida**2) / 6
    sigma_max_c = (q_lineal / B_corrida) + (M_lineal / W_lineal)
    
    st.markdown("**Verificación de Presiones sobre el Terreno**")
    st.write(f"Tensión máxima calculada: **{sigma_max_c:.2f} kPa**")
    if sigma_max_c <= sigma_adm_c:
        st.markdown('<span class="success-text">✅ VERIFICA: Tensión en el suelo menor a la admisible.</span>', unsafe_allowed_html=True)
    else:
        st.markdown('<span class="danger-text">❌ NO VERIFICA: Aumente el ancho B de la zapata corrida.</span>', unsafe_allowed_html=True)

# ==============================================================================
# MÓDULO 3: TENSORES Y VIGAS DE EQUILIBRIO (DIMTENS)
# ==============================================================================
elif modulo == "Tensores y Vigas (DIMTENS)":
    st.markdown('<div class="section-title">Módulo: Vigas de Equilibrio y Tensores Estructurales</div>', unsafe_allowed_html=True)
    st.write("Diseño estructural de elementos que absorben excentricidades críticas de zapatas medianeras.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Datos de la Zapata Excéntrica / Medianera**")
        P_ext = st.number_input("Carga de la columna excéntrica P_ext (kN)", min_value=1.0, value=500.0, step=50.0)
        excentricidad = st.number_input("Excentricidad del eje de carga e (m)", min_value=0.05, value=0.25, step=0.05)
    with col2:
        st.markdown("**Geometría de Vinculación**")
        L_viga = st.number_input("Distancia entre columnas / Longitud de la viga L (m)", min_value=1.0, value=5.0, step=0.5)
        
    F_viga = (P_ext * excentricidad) / L_viga
    
    st.markdown("---")
    st.markdown("**Resultados del Análisis de Equilibrio**")
