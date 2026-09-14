import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Cálculo de Proteção (51, 67, 32, 27, 59, 87, 49)", layout="wide"
)

# 1. Carrega o arquivo style.css que está na mesma pasta
with open("style.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- INJEÇÃO DE ESTILO CSS GLOBAL E JAVASCRIPT ---
st.markdown("""
<style>
    /* Grid Flexbox para os cartões ficarem lado a lado */
    .card-container {
        display: flex;
        flex-wrap: wrap;
        gap: 14px;
        margin-bottom: 20px;
    }
    
    /* Cartões de Parâmetros e Métricas */
    .card-protecao {
        background-color: #f8f9fa;
        border-left: 5px solid #007BFF;
        border-radius: 6px;
        padding: 14px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        flex: 1;
        min-width: 160px;
    }
    .card-protecao h4 {
        margin: 0 0 4px 0;
        color: #495057;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .card-protecao p {
        margin: 0;
        color: #212529;
        font-size: 22px;
        font-weight: 700;
    }
    .card-protecao span {
        font-size: 12px;
        color: #6c757d;
        font-weight: normal;
    }

    /* Alerta de Trip com Animação Pulsante */
    .trip-alert {
        background-color: #fff5f5;
        border: 2px solid #dc3545;
        border-radius: 8px;
        padding: 166px;
        padding: 16px;
        color: #a81c1c;
        margin-top: 10px;
        margin-bottom: 15px;
        transition: background-color 0.3s ease;
    }
    .trip-alert h3 { margin: 0 0 4px 0; color: #dc3545; font-size: 18px; font-weight: bold; }
    .trip-alert p { margin: 0; font-size: 14px; color: #5c1111; font-weight: 500; }

    /* Badge de Direção */
    .badge-direcional {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 4px;
        font-size: 13px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .badge-success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .badge-error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
</style>

<script>
    // Efeito JavaScript para alternar a cor do painel de Trip imitando um LED piscante
    setInterval(function() {
        var alerts = document.getElementsByClassName('trip-alert');
        for(var i = 0; i < alerts.length; i++) {
            if (alerts[i].style.backgroundColor === 'rgb(255, 245, 245)' || alerts[i].style.backgroundColor === '') {
                alerts[i].style.backgroundColor = '#ffdddd';
            } else {
                alerts[i].style.backgroundColor = '#fff5f5';
            }
        }
    }, 500);
</script>
""", unsafe_allow_html=True)

# Título e Subtítulo customizados com HTML e CSS interno
st.markdown(
    """
    <div class="header-protecao">
        <h1 class="titulo-simulador">⚡ Simulador e Cálculo de Proteção de Sistemas Elétricos</h1>
        <p class="subtitulo-simulador">Interface para parametrização, cálculo e visualização gráfica de funções de proteção.</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# --- DICIONÁRIOS DE CURVAS ---
CURVAS_IEC = {
    "IEC Normalmente Inversa (SI)": {"alpha": 0.02, "beta": 0.14},
    "IEC Muito Inversa (VI)": {"alpha": 1.0, "beta": 13.5},
    "IEC Extremamente Inversa (EI)": {"alpha": 2.0, "beta": 80.0},
    "IEC Longo Tempo Inversa": {"alpha": 1.0, "beta": 120.0},
}

CURVAS_ANSI = {
    "ANSI/IEEE Moderadamente Inversa": {"A": 0.0515, "B": 0.1140, "P": 0.02},
    "ANSI/IEEE Muito Inversa": {"A": 19.61, "B": 0.491, "P": 2.0},
    "ANSI/IEEE Extremamente Inversa": {"A": 28.2, "B": 0.1217, "P": 2.0},
}

CURVAS_IAC = {
    "IAC Inversa (IAC 51)": {"A": 0.208, "B": 0.83, "C": 0.8, "D": 0.195, "E": -0.0122},
    "IAC Muito Inversa (IAC 53)": {"A": 0.09, "B": 0.795, "C": 0.1, "D": 1.288, "E": 7.958},
    "IAC Extremamente Inversa (IAC 77)": {"A": 0.004, "B": 0.638, "C": 0.62, "D": 1.787, "E": 0.246},
}

CURVAS_TENSAO_ANSI = {
    "ANSI/IEEE Tensão Moderadamente Inversa": {"A": 0.0515, "B": 0.1140, "P": 0.02},
    "ANSI/IEEE Tensão Muito Inversa": {"A": 19.61, "B": 0.491, "P": 2.0},
    "ANSI/IEEE Tensão Extremamente Inversa": {"A": 28.2, "B": 0.1217, "P": 2.0},
}

# --- MENUS IF INTERFACE ---
st.sidebar.header("⚙️ Parâmetros de Entrada")

funcao = st.sidebar.radio(
    "Selecione a Função para Ajuste:",
    [
        "ANSI 51 (Sobrecorrente Temporizada)",
        "ANSI 67 (Sobrecorrente Direcional)",
        "ANSI 32 (Potência Inversa)",
        "ANSI 27 (Subtensão)",
        "ANSI 59 (Sobretensão)",
        "ANSI 87 (Proteção Diferencial Percentual)",
        "ANSI 49 (Sobrecarga Térmica)",
    ],
)

col1, col2 = st.columns([1, 1.3])

# --- LÓGICA DAS FUNÇÕES DE CORRENTE (51 / 67) ---
if funcao in ["ANSI 51 (Sobrecorrente Temporizada)", "ANSI 67 (Sobrecorrente Direcional)"]:
    padrao_curva = st.sidebar.selectbox("Norma da Curva:", ["IEC", "IEEE/ANSI", "IAC"])
    if padrao_curva == "IEC":
        tipo_curva = st.sidebar.selectbox("Tipo de Curva (IEC):", list(CURVAS_IEC.keys()))
        tms = st.sidebar.number_input("Dial de Tempo (TMS):", min_value=0.01, max_value=1.5, value=0.10, step=0.01)
    elif padrao_curva == "IEEE/ANSI":
        tipo_curva = st.sidebar.selectbox("Tipo de Curva (ANSI/IEEE):", list(CURVAS_ANSI.keys()))
        tms = st.sidebar.number_input("Dial de Tempo (TD):", min_value=0.1, max_value=15.0, value=1.0, step=0.01)
    else:
        tipo_curva = st.sidebar.selectbox("Tipo de Curva (IAC):", list(CURVAS_IAC.keys()))
        tms = st.sidebar.number_input("Dial de Tempo (TD):", min_value=0.1, max_value=15.0, value=1.0, step=0.01)

    i_set = st.sidebar.number_input("Corrente de Partida (A):", min_value=0.1, value=3.00, step=0.5)
    i_curto = st.sidebar.number_input("Corrente de Curto Simulado (A):", min_value=0.1, value=6.00, step=0.01)
    i_inst = st.sidebar.number_input("Corrente do Instantâneo (A) [0=Off]:", min_value=0.0, value=15.00, step=1.0)
    
    if funcao == "ANSI 67 (Sobrecorrente Direcional)":
        st.sidebar.subheader("📐 Parâmetros Direcionais (67)")
        mta = st.sidebar.slider("Ângulo de Máximo Torque - MTA (°):", -180, 180, 45)
        angulo_falha = st.sidebar.slider("Ângulo da Corrente de Falha (°):", -180, 180, 30)

    multiplo = i_curto / i_set
    zona_operacao = True
    if funcao == "ANSI 67 (Sobrecorrente Direcional)":
        diff_angulo = (angulo_falha - mta + 180) % 360 - 180
        if not (-90 <= diff_angulo <= 90):
            zona_operacao = False

    with col1:
        st.subheader(f"📊 Resultados da {funcao[:7]}")
        st.info("Fórmula Utilizada:")
        if padrao_curva == "IEC":
            st.latex(r"t = TMS \cdot \left[ \frac{k}{(I_{medida}/I_{partida})^{\alpha} - 1} \right]")
        else:
            st.latex(r"t = TD \cdot \left[ \frac{A}{(I_{medida}/I_{partida})^{P} - 1} + B \right]")

        # Grid HTML/CSS para substituição dos st.metric tradicionais
        st.markdown(f"""
        <div class='card-container'>
            <div class='card-protecao'>
                <h4>Ajuste de Partida</h4>
                <p>{i_set:.2f} <span>A</span></p>
            </div>
            <div class='card-container' style='flex: 1; margin: 0;'>
                <div class='card-protecao' style='border-left-color: #6c757d;'>
                    <h4>Múltiplo (I / I_set)</h4>
                    <p>{multiplo:.2f} <span>x</span></p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if funcao == "ANSI 67 (Sobrecorrente Direcional)":
            if zona_operacao:
                st.markdown("<div class='badge-direcional badge-success'>🎯 Direção de AVANÇO (Forward) - Falha na Zona de Operação</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='badge-direcional badge-error'>🔒 Direção de RECUO (Reverse) - Relé Bloqueado</div>", unsafe_allow_html=True)

        tempo_calculado = None
        if multiplo <= 1.0:
            st.warning("⚠️ Corrente abaixo do ajuste de partida. Sem atuação.")
        elif not zona_operacao:
            st.info("ℹ️ Relé direcional bloqueado por ângulo. Atuação infinita.")
        elif i_inst > 0 and i_curto >= i_inst:
            tempo_calculado = 0.015
            st.markdown(f"""
            <div class='trip-alert'>
                <h3>💥 ATUADO POR INSTANTÂNEO ({funcao[:4].replace('67','67I').replace('51','50')})</h3>
                <p>O nível de curto superou o limite do elemento instantâneo. Disparo disparado em {tempo_calculado*1000:.0f} ms.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            if padrao_curva == "IEC":
                tempo_calculado = tms * (CURVAS_IEC[tipo_curva]["beta"] / (multiplo**CURVAS_IEC[tipo_curva]["alpha"] - 1))
            elif padrao_curva == "IEEE/ANSI":
                p = CURVAS_ANSI[tipo_curva]["P"]
                tempo_calculado = tms * (CURVAS_ANSI[tipo_curva]["A"] / (multiplo**p - 1) + CURVAS_ANSI[tipo_curva]["B"])
            else:
                p = CURVAS_IAC[tipo_curva].get("P", 1.0)
                a, b, c, d, e = CURVAS_IAC[tipo_curva]["A"], CURVAS_IAC[tipo_curva]["B"], CURVAS_IAC[tipo_curva]["C"], CURVAS_IAC[tipo_curva]["D"], CURVAS_IAC[tipo_curva]["E"]
                base_val = multiplo**p - c
                if base_val > 0:
                    tempo_calculado = tms * (a + b / base_val + d / (base_val**2) + e / (base_val**3))

            if tempo_calculado is not None and multiplo > 1.0 and zona_operacao:
                st.markdown(f"""
                <div class='trip-alert' style='border-color: #fd7e14; color: #a04e00; background-color: #fffaf5;'>
                    <h3>⏳ DISPARO TEMPORIZADO EM CURVA</h3>
                    <p>Tempo estimado de atuação: <strong>{tempo_calculado:.4f} segundos</strong>.</p>
                </div>
                """, unsafe_allow_html=True)

    with col2:
        st.subheader("📈 Curva de Tempo de Atuação (Tempo Inverso)")
        multiplos_eixo = np.linspace(1.1, 20, 200)
        plt.figure(figsize=(7, 4.5))
        if padrao_curva == "IEC":
            tempos_eixo = tms * (CURVAS_IEC[tipo_curva]["beta"] / (multiplos_eixo**CURVAS_IEC[tipo_curva]["alpha"] - 1))
        elif padrao_curva == "IEEE/ANSI":
            p = CURVAS_ANSI[tipo_curva]["P"]
            tempos_eixo = tms * (CURVAS_ANSI[tipo_curva]["A"] / (multiplos_eixo**p - 1) + CURVAS_ANSI[tipo_curva]["B"])
        else:
            p = CURVAS_IAC[tipo_curva].get("P", 1.0)
            a, b, c, d, e = CURVAS_IAC[tipo_curva]["A"], CURVAS_IAC[tipo_curva]["B"], CURVAS_IAC[tipo_curva]["C"], CURVAS_IAC[tipo_curva]["D"], CURVAS_IAC[tipo_curva]["E"]
            base_eixo = multiplos_eixo**p - c
            tempos_eixo = tms * (a + b / base_eixo + d / (base_eixo**2) + e / (base_eixo**3))

        plt.plot(multiplos_eixo, tempos_eixo, label=tipo_curva, color="#007BFF", lw=2)
        if multiplo > 1.0 and zona_operacao:
            plt.scatter([multiplo], [tempo_calculado], color="red", zorder=5, s=100, label=f"Ponto de Falha ({multiplo:.2f}x, {tempo_calculado:.3f}s)")
        plt.xlabel("Múltiplo de Partida (I / I_set)")
        plt.ylabel("Tempo de Atuação (segundos)")
        plt.yscale("log")
        plt.grid(True, which="both", ls="--", alpha=0.5)
        plt.legend()
        st.pyplot(plt.gcf())

# --- LÓGICA DA FUNÇÃO DE POTÊNCIA (32) ---
elif funcao == "ANSI 32 (Potência Inversa)":
    st.sidebar.subheader("🔌 Parâmetros de Potência")
    p_pick = st.sidebar.number_input("Potência de Partida Reversa (kW):", min_value=1.0, value=50.0, step=5.0)
    p_falha = st.sidebar.number_input("Potência Reversa Medida (kW):", min_value=0.0, value=120.0, step=5.0)
    t_atp = st.sidebar.number_input("Tempo de Atuação Definido (s):", min_value=0.1, value=2.0, step=0.5)

    with col1:
        st.subheader("📊 Resultados da ANSI 32")
        
        st.markdown(f"""
        <div class='card-container'>
            <div class='card-protecao'>
                <h4>Potência de Partida</h4>
                <p>{p_pick:.2f} <span>kW</span></p>
            </div>
            <div class='card-protecao' style='border-left-color: #6c757d;'>
                <h4>Potência Reversa Medida</h4>
                <p style='color: {"#dc3545" if p_falha >= p_pick else "#28a745"};'>{p_falha:.2f} <span>kW</span></p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if p_falha >= p_pick:
            st.markdown(f"""
            <div class='trip-alert'>
                <h3>🚨 FALHA DETECTADA! Fluxo Reverso Violado</h3>
                <p>O sistema identificou regime de motorização indesejada. O relé comandará o trip em: <strong>{t_atp:.2f} s</strong>.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<div class='badge-status badge-success'>✅ Sistema Seguro. Fluxo de potência reversa dentro dos limites normais.</div>", unsafe_allow_html=True)

    with col2:
        st.subheader("📊 Diagrama de Operação da Potência")
        categorias = ["Ajuste (Pick-up)", "Potência Medida"]
        valores = [p_pick, p_falha]
        plt.figure(figsize=(6, 4))
        cores = ["#FFA000", "#D32F2F" if p_falha >= p_pick else "#388E3C"]
        plt.bar(categorias, valores, color=cores, width=0.5)
        plt.ylabel("Potência Reversa (kW)")
        plt.grid(axis='y', ls="--", alpha=0.5)
        st.pyplot(plt.gcf())

# --- LÓGICA DE PROTEÇÃO DE TENSÃO (27 / 59) ---
elif funcao in ["ANSI 27 (Subtensão)", "ANSI 59 (Sobretensão)"]:
    st.sidebar.subheader("⚡ Parâmetros do TP e Sistema")
    v_nom_pri = st.sidebar.number_input("Tensão Nominal Primária (V):", min_value=1.0, value=13800.0, step=100.0)
    v_nom_sec = st.sidebar.number_input("Tensão Nominal Secundária (V):", min_value=1.0, value=115.0, step=5.0)
    label_porcentagem = "Queda de Tensão Permitida (%)" if funcao == "ANSI 27 (Subtensão)" else "Elevação de Tensão Permitida (%)"
    v_ajuste_porcentagem = st.sidebar.number_input(label_porcentagem, min_value=1.0, max_value=50.0, value=10.0, step=1.0)
    st.sidebar.subheader("📉 Falha Simulada")
    v_medida_pri = st.sidebar.number_input("Tensão de Rede Medida Primária (V):", min_value=0.0, value=11000.0 if funcao == "ANSI 27 (Subtensão)" else 15000.0, step=100.0)
    tipo_tempo_v = st.sidebar.selectbox("Tipo de Atuação Temporal:", ["Tempo Definido", "Curva Inversa (ANSI/IEEE)"])
    if tipo_tempo_v == "Tempo Definido":
        t_definido_v = st.sidebar.number_input("Tempo Definido de Trip (s):", min_value=0.05, value=2.0, step=0.5)
    else:
        tipo_curva = st.sidebar.selectbox("Tipo de Curva de Tensão:", list(CURVAS_TENSAO_ANSI.keys()))
        tms = st.sidebar.number_input("Dial de Tempo (TD):", min_value=0.1, max_value=15.0, value=1.0, step=0.1)

    v_ajuste_pri = v_nom_pri * (1 - v_ajuste_porcentagem/100) if funcao == "ANSI 27 (Subtensão)" else v_nom_pri * (1 + v_ajuste_porcentagem/100)
    falha_detectada = v_medida_pri <= v_ajuste_pri if funcao == "ANSI 27 (Subtensão)" else v_medida_pri >= v_ajuste_pri
    
    with col1:
        st.subheader(f"📊 Resultados da {funcao[:7]}")
        
        st.markdown(f"""
        <div class='card-container'>
            <div class='card-protecao'>
                <h4>Tensão Nominal</h4>
                <p>{v_nom_pri:.1f} <span>V</span></p>
            </div>
            <div class='card-protecao'>
                <h4>Limiar de Ajuste</h4>
                <p>{v_ajuste_pri:.1f} <span>V</span></p>
            </div>
            <div class='card-protecao' style='border-left-color: #6c757d;'>
                <h4>Tensão Medida</h4>
                <p style='color: {"#dc3545" if falha_detectada else "#28a745"};'>{v_medida_pri:.1f} <span>V</span></p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if falha_detectada:
            if tipo_tempo_v == "Tempo Definido":
                st.markdown(f"""
                <div class='trip-alert'>
                    <h3>🚨 TRIP DE TENSÃO CRÍTICO ATIVADO</h3>
                    <p>Violação dos limites operacionais seguros. Disparo em tempo definido configurado para: <strong>{t_definido_v:.2f} s</strong>.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                m = abs(v_medida_pri - v_ajuste_pri) / v_ajuste_pri
                if m == 0: m = 0.001
                p = CURVAS_TENSAO_ANSI[tipo_curva]["P"]
                t_inv = tms * (CURVAS_TENSAO_ANSI[tipo_curva]["A"] / (m**p) + CURVAS_TENSAO_ANSI[tipo_curva]["B"])
                st.markdown(f"""
                <div class='trip-alert'>
                    <h3>🚨 TRIP POR CURVA INVERSA DE TENSÃO</h3>
                    <p>Tempo de coordenação dinâmico calculado em: <strong>{t_inv:.4f} segundos</strong>.</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div class='badge-status badge-success'>✅ Níveis de tensão dentro da faixa operacional segura.</div>", unsafe_allow_html=True)

    with col2:
        st.subheader("📈 Perfil de Monitoramento de Tensão")
        plt.figure(figsize=(6, 4))
        plt.axhline(v_nom_pri, color="gray", ls="--", label="Nominal")
        plt.axhline(v_ajuste_pri, color="orange", ls="-", lw=2, label="Limiar Ajuste")
        plt.bar(["Tensão Medida"], [v_medida_pri], color="#D32F2F" if falha_detectada else "#388E3C", width=0.4)
        plt.ylabel("Tensão Primária (V)")
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        st.pyplot(plt.gcf())

# --- LÓGICA PARA PROTEÇÃO DIFERENCIAL (87) ---
elif funcao == "ANSI 87 (Proteção Diferencial Percentual)":
    st.sidebar.subheader("🎯 Parâmetros de Slope Diferencial")
    i_pick_87 = st.sidebar.number_input("Corrente Mínima de Partida (I_pick) [pu]:", min_value=0.05, max_value=1.0, value=0.30, step=0.05)
    slope_1 = st.sidebar.number_input("Slope 1 (%):", min_value=5.0, max_value=100.0, value=25.0, step=5.0)
    i_break = st.sidebar.number_input("Ponto de Transição (I_break) [pu]:", min_value=0.5, max_value=5.0, value=2.0, step=0.5)
    slope_2 = st.sidebar.number_input("Slope 2 (%):", min_value=10.0, max_value=150.0, value=50.0, step=5.0)
    st.sidebar.subheader("📉 Correntes Injetadas Simuladas")
    i1_sim = st.sidebar.number_input("Corrente Terminal 1 - I1 (pu):", min_value=0.0, value=3.0, step=0.1)
    i2_sim = st.sidebar.number_input("Corrente Terminal 2 - I2 (pu):", min_value=0.0, value=2.5, step=0.1)

    i_diff = abs(i1_sim - i2_sim)
    i_rest = (abs(i1_sim) + abs(i2_sim)) / 2.0
    if i_rest <= i_break:
        i_diff_limiar = i_pick_87 + (slope_1 / 100.0) * i_rest
    else:
        i_diff_limiar = i_pick_87 + (slope_1 / 100.0) * i_break + (slope_2 / 100.0) * (i_rest - i_break)
    disparo_87 = i_diff >= i_diff_limiar and i_diff >= i_pick_87

    with col1:
        st.subheader("📊 Grandezas Calculadas (87)")
        
        st.markdown(f"""
        <div class='card-container'>
            <div class='card-protecao'>
                <h4>Diferencial (I_diff)</h4>
                <p style='color: {"#dc3545" if disparo_87 else "#212529"};'>{i_diff:.2f} <span>pu</span></p>
            </div>
            <div class='card-protecao'>
                <h4>Restrição (I_rest)</h4>
                <p>{i_rest:.2f} <span>pu</span></p>
            </div>
            <div class='card-protecao' style='border-left-color: #6c757d;'>
                <h4>Limiar Mínimo</h4>
                <p>{i_diff_limiar:.2f} <span>pu</span></p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if disparo_87:
            st.markdown("""
            <div class='trip-alert'>
                <h3>🚨 TRIP DIFERENCIAL DETECTADO</h3>
                <p>Diferença intolerável de correntes mapeada. Falha de caráter interno severo dentro da zona protegida.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<div class='badge-status badge-success'>✅ Zona Interna Estável. Corrente diferencial dentro do slope de restrição.</div>", unsafe_allow_html=True)

    with col2:
        st.subheader("📈 Plano Alfa / Característica de Disparo da Função 87")
        ir_eixo = np.linspace(0, max(5.0, i_rest + 1.0), 300)
        id_curva = []
        for r in ir_eixo:
            if r <= i_break:
                val = i_pick_87 + (slope_1 / 100.0) * r
            else:
                val = i_pick_87 + (slope_1 / 100.0) * i_break + (slope_2 / 100.0) * (r - i_break)
            id_curva.append(max(val, i_pick_87))
        plt.figure(figsize=(7, 4.5))
        plt.plot(ir_eixo, id_curva, color="red", lw=2, label="Limiar de Disparo (Slope)")
        plt.fill_between(ir_eixo, id_curva, 10, color="red", alpha=0.1, label="Zona de Operação (Trip)")
        plt.fill_between(ir_eixo, 0, id_curva, color="green", alpha=0.05, label="Zona de Bloqueio (Restrição)")
        cor_ponto = "red" if disparo_87 else "green"
        plt.scatter([i_rest], [i_diff], color=cor_ponto, s=120, zorder=5, edgecolors='black', label=f"Ponto Injetado (Ir={i_rest:.2f}, Id={i_diff:.2f})")
        plt.xlabel("Corrente de Restrição - I_rest (pu)")
        plt.ylabel("Corrente Diferencial - I_diff (pu)")
        plt.xlim(0, max(4.0, i_rest + 0.5))
        plt.ylim(0, max(3.0, i_diff + 0.5))
        plt.grid(True, ls="--", alpha=0.5)
        plt.legend(loc="upper left")
        st.pyplot(plt.gcf())

# --- LÓGICA PARA PROTEÇÃO DE SOBRECARGA TÉRMICA (49) ---
elif funcao == "ANSI 49 (Sobrecarga Térmica)":
    st.sidebar.subheader("🔥 Parâmetros de Imagem Térmica (49)")
    
    fabricante = st.sidebar.selectbox("Modelo/Fabricante do Relé:", ["Schneider Sepam", "Siemens (Siprotec/Reyrolle)", "GE Multilin", "Pextron (Réplica IEC)"])
    
    i_b = st.sidebar.number_input("Corrente de Base / Nominal (I_b) [A]:", min_value=0.1, value=3.0, step=0.5)
    tau = st.sidebar.number_input("Constante de Tempo de Aquecimento (τ) [segundos]:", min_value=1.0, value=1200.0, step=10.0)
    es = st.sidebar.number_input("Capacidade Térmica de Disparo (Es) [%]:", min_value=1.0, max_value=200.0, value=50.0, step=5.0) / 100.0
    e_inicial = st.sidebar.number_input("Estado Térmico Inicial (E_inicial) [%]:", min_value=0.0, max_value=100.0, value=0.0, step=5.0) / 100.0

    if fabricante == "Schneider Sepam":
        st.sidebar.markdown("**Abordagem Sepam:** Utiliza a maior corrente RMS medida entre as fases.")
        i_eq_medida = st.sidebar.number_input("Corrente RMS Máxima Medida (I_eq) [A]:", min_value=0.1, value=6.0, step=0.5)
        razao_corrente = i_eq_medida / i_b
        
    elif fabricante == "Siemens (Siprotec/Reyrolle)":
        st.sidebar.markdown("**Abordagem Siemens:** Permite calcular o efeito térmico do desequilíbrio (Rotor).")
        i1 = st.sidebar.number_input("Corrente de Sequência Positiva (I1) [A]:", min_value=0.0, value=5.8, step=0.1)
        i2 = st.sidebar.number_input("Corrente de Sequência Negativa (I2) [A]:", min_value=0.0, value=0.5, step=0.1)
        k2 = st.sidebar.number_input("Fator de Ponderação do Rotor (k2):", min_value=0.0, max_value=10.0, value=3.0, step=0.5)
        
        i_eq_calculada = np.sqrt(i1**2 + (k2 * (i2**2)))
        st.sidebar.info(f"I_eq Térmica Calculada (Siemens): {i_eq_calculada:.2f} A")
        razao_corrente = i_eq_calculada / i_b
        
    elif fabricante == "GE Multilin":
        st.sidebar.markdown("**Abordagem GE Multilin:** Ponderação do desequilíbrio via fator K do motor.")
        i1_ge = st.sidebar.number_input("Corrente de Sequência Positiva (I1) [A]:", min_value=0.1, value=5.8, step=0.1)
        i2_ge = st.sidebar.number_input("Corrente de Sequência Negativa (I2) [A]:", min_value=0.0, value=0.5, step=0.1)
        k_ge = st.sidebar.number_input("Fator K de Desequilíbrio (Unbalance Bias K):", min_value=1.0, max_value=15.0, value=4.0, step=1.0)
        
        if i1_ge == 0: i1_ge = 0.001
        i_eq_ge = i1_ge * np.sqrt(1.0 + k_ge * ((i2_ge / i1_ge) ** 2))
        st.sidebar.info(f"I_eq Térmica Calculada (GE Multilin): {i_eq_ge:.2f} A")
        razao_corrente = i_eq_ge / i_b

    else:
        st.sidebar.markdown("**Abordagem Pextron:** Modelo de imagem térmica baseado na norma IEC 60255-149.")
        i_pextron = st.sidebar.number_input("Corrente Equivalente de Fase Medida (I) [A]:", min_value=0.1, value=6.0, step=0.5)
        razao_corrente = i_pextron / i_b

    with col1:
        st.subheader(f"📊 Resultados da ANSI 49 ({fabricante})")
        st.info("Fórmula de Imagem Térmica Utilizada:")
        if fabricante in ["Schneider Sepam", "Pextron (Réplica IEC)"]:
            st.latex(r"t = \tau \cdot \ln\left( \frac{(I_{eq}/I_b)^2 - E_{inicial}}{(I_{eq}/I_b)^2 - Es} \right)")
        elif fabricante == "Siemens (Siprotec/Reyrolle)":
            st.latex(r"I_{eq}^2 = I_1^2 + (k_2 \cdot I_2^2)")
            st.latex(r"t = \tau \cdot \ln\left( \frac{(I_{eq}/I_b)^2 - E_{inicial}}{(I_{eq}/I_b)^2 - Es} \right)")
        elif fabricante == "GE Multilin":
            st.latex(r"I_{eq} = I_1 \cdot \sqrt{1 + k \cdot (I_2/I_1)^2}")
            st.latex(r"t = \tau \cdot \ln\left( \frac{(I_{eq}/I_b)^2 - E_{inicial}}{(I_{eq}/I_b)^2 - Es} \right)")

        st.markdown(f"""
        <div class='card-container'>
            <div class='card-protecao'>
                <h4>Razão Equivalente</h4>
                <p>{razao_corrente:.2f} <span>x</span></p>
            </div>
            <div class='card-protecao' style='border-left-color: #6c757d;'>
                <h4>Capacidade Limite (Es)</h4>
                <p>{es*100:.1f} <span>%</span></p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if (razao_corrente)**2 <= es:
            st.markdown("<div class='badge-status badge-success'>✅ Estável: A corrente medida não causará aquecimento suficiente para atingir o limite Es.</div>", unsafe_allow_html=True)
        else:
            numerador = (razao_corrente)**2 - e_inicial
            denominador = (razao_corrente)**2 - es
            t_trip = tau * np.log(numerador / denominador)
            
            st.markdown(f"""
            <div class='trip-alert'>
                <h3>🚨 TRIP TÉRMICO DETECTADO</h3>
                <p>Estágio crítico de carregamento acumulado. Atuação em: <strong>{t_trip:.2f} s</strong> (~{t_trip/60:.2f} min).</p>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.subheader("📈 Evolução do Estado Térmico pelo Modelo de Imagem")
        t_max = tau * 3 if (razao_corrente)**2 <= es else t_trip * 1.5
        tempo_eixo = np.linspace(0, t_max, 500)
        
        estado_termico = (e_inicial - (razao_corrente)**2) * np.exp(-tempo_eixo / tau) + (razao_corrente)**2
        estado_termico_porcento = estado_termico * 100.0
        
        plt.figure(figsize=(7, 4.5))
        plt.plot(tempo_eixo, estado_termico_porcento, color="#FF5722", lw=2, label=f"Evolução Térmica E(t) - {fabricante}")
        plt.axhline(es * 100.0, color="red", ls="--", lw=1.5, label=f"Limiar de Trip Es ({es*100:.0f}%)")
        
        if (razao_corrente)**2 > es:
            plt.scatter([t_trip], [es * 100.0], color="red", s=100, zorder=5, label=f"Ponto de Trip ({t_trip:.1f}s)")
            
        plt.xlabel("Tempo (segundos)")
        plt.ylabel("Capacidade Térmica Acumulada (%)")
        plt.ylim(0, min(200.0, (razao_corrente)**2 * 110.0))
        plt.grid(True, ls="--", alpha=0.5)
        plt.legend()
        st.pyplot(plt.gcf())
