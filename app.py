import streamlit as st
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="Sistema BASE - CIRSOC 201-82",
    page_icon="🏗️",
    layout="wide"
)

# Estilo personalizado para el entorno de ingeniería clásica
st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #1E3A8A; margin-bottom: 20px; }
    .section-title { font-size: 22px; font-weight: bold; color: #2563EB; margin-top: 15px; }
    .success-text { color: #16A34A; font-weight: bold; }
    .danger-text { color: #DC2626; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏗️ Sistema BASE (Copia Exacta Original - CIRSOC 201-82)</div>', unsafe_allow_html=True)
st.write("Dimensionamiento de fundaciones superficiales utilizando el Método de las Tensiones Admisibles.")

# Sidebar - Selección de Módulo Principal
st.sidebar.title("Módulos de Cálculo")
modulo = st.sidebar.radio(
    "Seleccione el componente a calcular:",
    ["Bases Aisladas (DIMBASE)", "Fundaciones Continuas (DIMSOLE)", "Tensores y Vigas (DIMTENS)"]
)

# Parámetros Globales de Materiales - Terminología y tensiones típicas de la norma 1982
st.sidebar.markdown("---")
st.sidebar.markdown("**Propiedades de los Materiales (CIRSOC 82)**")
calidad_h = st.sidebar.selectbox("Calidad del Hormigón", ["H-13 (σ_b_adm = 6.0 MPa)", "H-17 (σ_b_adm = 8.5 MPa)", "H-21 (σ_b_adm = 10.5 MPa)"], index=1)
calidad_a = st.sidebar.selectbox("Tipo de Acero", ["ADN-420 (σ_s_adm = 240 MPa)", "AL-220 (σ_s_adm = 140 MPa)"], index=0)

# Asignación manual de tensiones admisibles según CIRSOC 201-82
sigma_b_adm = 8.5 if "H-17" in calidad_h else (10.5 if "H-21" in calidad_h else 6.0)
sigma_s_adm = 240.0 if "ADN-420" in calidad_a else 140.0

recubrimiento = st.sidebar.slider("Recubrimiento mecánico (r) [cm]", 3.0, 7.5, 5.0, 0.5)

# ==============================================================================
# MÓDULO 1: BASES AISLADAS (DIMBASE) + REFUERZO ADMISIBLE (BAC-BE)
# ==============================================================================
if modulo == "Bases Aisladas (DIMBASE)":
    st.markdown('<div class="section-title">Módulo: Zapatas Aisladas en Flexión Compuesta Fiel a DOS</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Cargas de Servicio (Sin Mayorar)**")
        P = st.number_input("Carga Axil de Columna P (kN)", min_value=1.0, value=750.0, step=50.0)
        Mx = st.number_input("Momento Flexor M_x (kN·m)", min_value=0.0, value=45.0, step=5.0)
        My = st.number_input("Momento Flexor M_y (kN·m)", min_value=0.0, value=20.0, step=5.0)
        
    with col2:
        st.markdown("**Geometría y Datos del Suelo**")
        sigma_adm = st.number_input("Tensión Admisible del Terreno σ_adm (kPa)", min_value=10.0, value=200.0, step=10.0)
        cx = st.number_input("Lado columna c_x (m)", min_value=0.1, value=0.3, step=0.05)
        cy = st.number_input("Lado columna c_y (m)", min_value=0.1, value=0.3, step=0.05)

    # Predimensionado original (considerando el peso propio de la base de forma estática)
    area_min = (P * 1.10) / sigma_adm
    lado_sug = np.sqrt(area_min)
    st.info(f"💡 **Área de contacto sugerida en planta (Peso Propio = 10%):** {area_min:.2f} m² → Lado de base cuadrada: {lado_sug:.2f} m")

    st.markdown("---")
    st.markdown("**Dimensiones de Base Adoptadas**")
    col3, col4, col5 = st.columns(3)
    with col3:
        A = st.number_input("Ancho de Base A (m)", min_value=0.5, value=float(round(lado_sug, 1)), step=0.05)
    with col4:
        B = st.number_input("Largo de Base B (m)", min_value=0.5, value=float(round(lado_sug, 1)), step=0.05)
    with col5:
        H = st.number_input("Altura de Base H (m)", min_value=0.2, value=0.5, step=0.05)

    # Tensiones elásticas sobre el plano de fundación
    area = A * B
    Wx = (B * (A**2)) / 6
    Wy = (A * (B**2)) / 6

    sigma_max = (P / area) + (Mx / Wx) + (My / Wy)
    sigma_min = (P / area) - (Mx / Wx) - (My / Wy)

    st.markdown("**Verificación del Terreno (Tensiones de Servicio)**")
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.metric("Tensión Máxima Calculada", f"{sigma_max:.2f} kPa", delta=f"{sigma_adm - sigma_max:.2f} kPa remanente", delta_color="normal" if sigma_max <= sigma_adm else "inverse")
    with res_col2:
        st.metric("Tensión Mínima Calculada", f"{sigma_min:.2f} kPa")

    if sigma_max <= sigma_adm and sigma_min >= 0:
        st.markdown('<span class="success-text">✅ VERIFICA GEOTECNIA: Presiones bajo el límite admisible del suelo.</span>', unsafe_allow_html=True)
    elif sigma_max <= sigma_adm and sigma_min < 0:
        st.markdown('<span class="danger-text">⚠️ ALERTA: Hay zonas con despegue de la zapata (Tensión Mínima < 0). Modifique las dimensiones de la planta.</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="danger-text">❌ RECHAZADO: Se excede la tensión admisible del terreno.</span>', unsafe_allow_html=True)

    # Cálculo Estructural clásico - CIRSOC 201-82 (Método Elástico)
    st.markdown("---")
    st.markdown("**Módulo de Armaduras (Lógica Original BAC-BE - Sin Mayoración)**")
    
    # Presión de servicio media para el cálculo de momentos de flexión de las consolas
    q_serv = P / area 
    vuelo_x = (A - cx) / 2
    vuelo_y = (B - cy) / 2
    
    # Momentos estáticos de servicio en las secciones de referencia de la columna
    M_x_serv = (q_serv * B * (vuelo_x**2)) / 2
    M_y_serv = (q_serv * A * (vuelo_y**2)) / 2
    
    # Altura útil d (m)
    d = H - (recubrimiento / 100)
    
    # Ecuación clásica del método elástico (As = M / (σ_s_adm * z)), aproximando brazo z = 0.875 * d
    z_aprox = 0.875 * d
    As_x_req = (M_x_serv * 10**6) / (sigma_s_adm * (z_aprox * 1000))  # mm²
    As_y_req = (M_y_serv * 10**6) / (sigma_s_adm * (z_aprox * 1000))  # mm²
    
    arm_col1, arm_col2 = st.columns(2)
    with arm_col1:
        st.markdown(f"**Flexión X (Momento M_x: {M_x_serv:.1f} kN·m)**")
        st.write(f"Sección de acero necesaria: **{As_x_req/100:.2f} cm²**")
        barra_x = st.selectbox("Diámetro del hierro X (mm)", [8, 10, 12, 16, 20, 25], index=2)
        area_barra_x = np.pi * (barra_x/2)**2
        cant_barras_x = int(np.ceil(As_x_req / area_barra_x))
        st.success(f"Disponer en parrilla: **{max(cant_barras_x, 5)} ø {barra_x}**")
        
    with arm_col2:
        st.markdown(f"**Flexión Y (Momento M_y: {M_y_serv:.1f} kN·m)**")
        st.write(f"Sección de acero necesaria: **{As_y_req/100:.2f} cm²**")
        barra_y = st.selectbox("Diámetro del hierro Y (mm)", [8, 10, 12, 16, 20, 25], index=2)
        area_barra_y = np.pi * (barra_y/2)**2
        cant_barras_y = int(np.ceil(As_y_req / area_barra_y))
        st.success(f"Disponer en parrilla: **{max(cant_barras_y, 5)} ø {barra_y}**")

# ==============================================================================
# MÓDULO 2: FUNDACIONES CONTINUAS (DIMSOLE)
# ==============================================================================
elif modulo == "Fundaciones Continuas (DIMSOLE)":
    st.markdown('<div class="section-title">Módulo: Fundaciones Continuas por Metro Lineal</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Cargas de Servicio Actuantes**")
        q_lineal = st.number_input("Carga Lineal de Servicio q (kN/m)", min_value=1.0, value=120.0, step=10.0)
        M_lineal = st.number_input("Momento de Servicio M (kN·m/m)", min_value=0.0, value=10.0, step=2.0)
    with col2:
        st.markdown("**Parámetros Geotécnicos**")
        sigma_adm_c = st.number_input("Tensión Admisible del Terreno σ_adm (kPa)", min_value=10.0, value=150.0, step=10.0)
        espesor_muro = st.number_input("Espesor del muro (m)", min_value=0.1, value=0.2, step=0.05)

    ancho_min = (q_lineal * 1.05) / sigma_adm_c
    st.info(f"💡 **Ancho de zapata corrida sugerido:** {ancho_min:.2f} m")
    
    st.markdown("---")
    B_corrida = st.number_input("Ancho Adoptado B (m)", min_value=0.3, value=float(round(max(ancho_min, 0.6), 2)), step=0.05)
    H_corrida = st.number_input("Altura Adoptada H (m)", min_value=0.15, value=0.30, step=0.05)

    W_lineal = (B_corrida**2) / 6
    sigma_max_c = (q_lineal / B_corrida) + (M_lineal / W_lineal)
    
    st.markdown("**Verificación Geotécnica**")
    st.write(f"Tensión máxima sobre el suelo: **{sigma_max_c:.2f} kPa**")
    if sigma_max_c <= sigma_adm_c:
        st.markdown('<span class="success-text">✅ VERIFICA: Tensión admisible del suelo respetada.</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="danger-text">❌ NO VERIFICA: Incremente el ancho B del cimiento corrido.</span>', unsafe_allow_html=True)

# ==============================================================================
# MÓDULO 3: TENSORES Y VIGAS DE EQUILIBRIO (DIMTENS)
# ==============================================================================
elif modulo == "Tensores y Vigas (DIMTENS)":
    st.markdown('<div class="section-title">Módulo: Vigas de Equilibrio y Tensores (CIRSOC 82)</div>', unsafe_allow_html=True)
    st.write("Determinación analítica del esfuerzo de equilibrio puro provocado por columnas excéntricas.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Esfuerzos en Columna Excéntrica**")
        P_ext = st.number_input("Carga de Servicio de la Columna P_ext (kN)", min_value=1.0, value=500.0, step=50.0)
        excentricidad = st.number_input("Excentricidad geométrica de la carga e (m)", min_value=0.05, value=0.25, step=0.05)
    with col2:
        st.markdown("**Geometría de Vinculación**")
        L_viga = st.number_input("Longitud entre ejes de columnas L (m)", min_value=1.0, value=5.0, step=0.5)
        
    # Esfuerzo de tracción axial puro deducido del par estático de servicio
    F_viga = (P_ext * excentricidad) / L_viga
    
    st.markdown("---")
st.markdown("Análisis Estático de Equilibrio de Servicio")
st.warning(f"Fuerza de tracción pura generada en el tensor: {F_viga:.2f} kN")
st.markdown("Dimensionamiento de la Viga de Vínculo/Tensor")
col3, col4 = st.columns(2)
with col3:
b_viga = st.number_input("Ancho de la viga b (m)", min_value=0.15, value=0.25, step=0.05)
with col4:
h_viga = st.number_input("Canto total de la viga h (m)", min_value=0.20, value=0.45, step=0.05)
# Dimensionamiento a tracción simple sin mayoración (As = F / σ_s_adm)
As_tensor = (F_viga * 1000) / sigma_s_adm
st.success(f"Sección de acero necesaria para el tensor: {As_tensor/100:.2f} cm²")
barra_t = st.selectbox("Seleccione diámetro de barra principal (mm)", [10, 12, 16, 20, 25], index=1)
area_b_t = np.pi * (barra_t/2)**2
cant_t = int(np.ceil(As_tensor / area_b_t))
st.write(f"Recomendación: Colocar un mínimo de {max(cant_t, 2)} ø {barra_t} dispuestos simétricamente.")
st.markdown("---")
st.caption("Sistema BASE v2026. Réplica fiel del software original basada exclusivamente en CIRSOC 201-82.")
