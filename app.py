import matplotlib.pyplot as plt

import numpy as np

import pandas as pd

import streamlit as st

st.set_page_config( page_title="Cálculo de Proteção (51, 67, 32, 27, 59, 87, 49)",
layout="wide",
initial_sidebar_state="expanded")

# 1. Carrega o arquivo style.css que está na mesma pasta
with open("style.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- INJEÇÃO EXCLUSIVA DE JAVASCRIPT ---

st.markdown("""
<script>
// Efeito JavaScript para alternar a cor do painel de Trip imitando um LED piscante
    setInterval(function() {
    var alerts = document.getElementsByClassName('trip-alert');
        for(var i = 0; i < alerts.length; i++) {if (alerts[i].style.backgroundColor === 'rgb(255, 245, 245)' || alerts[i].style.backgroundColor === '') {
            alerts[i].style.backgroundColor = '#ffdddd';} else {alerts[i].style.backgroundColor = '#fff5f5';
        }
        }
     },
          500);
</script>
""", unsafe_allow_html=True)

# Título e Subtítulo customizados com HTML (Estilizados pelo style.css externo)

st.markdown(
    """
    <div class="header-protecao">
        <h1 class="titulo-simulador">⚡ Simulador e Cálculo de Proteção de Sistemas Elétricos</h1>
        <p class="subtitulo-simulador">Interface para parametrização, cálculo e visualização gráfica de funções de proteção.</p>
    </div>
    """,unsafe_allow_html=True)

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
     "ANSI 67N (Sobrecorrente Direcional de Terra)",
     "ANSI 32 (Potência Inversa)",
     "ANSI 21 (Proteção de Distância)",
     "ANSI 27 (Subtensão)",
     "ANSI 59 (Sobretensão)",
     "ANSI 87 (Proteção Diferencial Percentual)",
     "ANSI 49 (Sobrecarga Térmica)",
    ],
)
col1, col2 = st.columns([1, 1.3])

# --- LÓGICA DAS FUNÇÕES DE CORRENTE (51 / 67) ---
if funcao in [
"ANSI 51 (Sobrecorrente Temporizada)",
"ANSI 67 (Sobrecorrente Direcional)",
"ANSI 67N (Sobrecorrente Direcional de Terra)",
]:
    padrao_curva = st.sidebar.selectbox("Norma da Curva:", ["IEC", "IEEE/ANSI", "IAC"]
    )
    if padrao_curva == "IEC":
        tipo_curva = st.sidebar.selectbox(
            "Tipo de Curva (IEC):", list(CURVAS_IEC.keys())
        )
        tms = st.sidebar.number_input(
            "Dial de Tempo (TMS):",
            min_value=0.01,
            max_value=1.5,
            value=0.10,
            step=0.01,
        )
    elif padrao_curva == "IEEE/ANSI":
        tipo_curva = st.sidebar.selectbox(
            "Tipo de Curva (ANSI/IEEE):", list(CURVAS_ANSI.keys())
        )
        tms = st.sidebar.number_input(
            "Dial de Tempo (TD):",
            min_value=0.1,
            max_value=15.0,
            value=1.0,
            step=0.01,
        )
    else:
        tipo_curva = st.sidebar.selectbox(
            "Tipo de Curva (IAC):", list(CURVAS_IAC.keys())
        )
        tms = st.sidebar.number_input(
            "Dial de Tempo (TD):",
            min_value=0.1,
            max_value=15.0,
            value=1.0,
            step=0.01,
        )
    i_set = st.sidebar.number_input(
        "Corrente de Partida (A):", min_value=0.1, value=3.00, step=0.5
    )
    i_curto = st.sidebar.number_input(
        "Corrente de Curto Simulado (A):", min_value=0.1, value=6.00, step=0.01
    )
    i_inst = st.sidebar.number_input(
        "Corrente do Instantâneo (A) [0=Off]:",
        min_value=0.0,
        value=15.00,
        step=1.0,
    )
    # Parâmetros específicos dos elementos direcionais 67 e 67N
    if funcao == "ANSI 67 (Sobrecorrente Direcional)":
        st.sidebar.subheader("📐 Parâmetros Direcionais (67)")
        mta = st.sidebar.slider(
            "Ângulo de Máximo Torque - MTA (°):", -180, 180, 45
        )
        angulo_falha = st.sidebar.slider(
            "Ângulo da Corrente de Falha (°):", -180, 180, 30
        )
    elif funcao == "ANSI 67N (Sobrecorrente Direcional de Terra)":
        st.sidebar.subheader("🌎 Parâmetros Direcionais de Terra (67N)")
        mta = st.sidebar.slider(
            "MTA / Ângulo Característico (°):", -180, 180, 45
        )
        i0_set = st.sidebar.number_input(
            "Partida de Corrente Residual 3I0 (A):", min_value=0.01, value=1.00, step=0.10
        )
        i0_curto = st.sidebar.number_input(
            "Corrente Residual de Falta 3I0 (A):", min_value=0.0, value=5.00, step=0.10
        )
        angulo_i0 = st.sidebar.slider(
            "Ângulo de 3I0 (°):", -180, 180, 30
        )
        angulo_v0 = st.sidebar.slider(
            "Ângulo de 3V0 / Polarização (°):", -180, 180, 0
        )
        i0_inst = st.sidebar.number_input(
            "3I0 Instantâneo (A) [0=Off]:", min_value=0.0, value=0.0, step=0.10
        )
        i_set = i0_set
        i_curto = i0_curto
        i_inst = i0_inst
        angulo_falha = angulo_i0
    multiplo = i_curto / i_set
    zona_operacao = True
    if funcao in ["ANSI 67 (Sobrecorrente Direcional)", "ANSI 67N (Sobrecorrente Direcional de Terra)"]:
        if funcao == "ANSI 67N (Sobrecorrente Direcional de Terra)":
            diff_angulo = (angulo_i0 - angulo_v0 - mta + 180) % 360 - 180
        else:
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

        st.markdown(
            f"""
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
        """,
            unsafe_allow_html=True,
        )

        if funcao in ["ANSI 67 (Sobrecorrente Direcional)", "ANSI 67N (Sobrecorrente Direcional de Terra)"]:
            if zona_operacao:
                st.markdown(
                    "<div class='badge-direcional badge-success'>🎯 Direção de AVANÇO (Forward) - Falha na Zona de Operação</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    "<div class='badge-direcional badge-error'>🔒 Direção de RECUO (Reverse) - Relé Bloqueado</div>",
                    unsafe_allow_html=True,
                )
        tempo_calculado = None
        if multiplo <= 1.0:
            st.warning("⚠️ Corrente abaixo do ajuste de partida. Sem atuação.")
        elif not zona_operacao:
            st.info(
                "ℹ️ Relé direcional bloqueado por ângulo. Atuação infinita."
            )
        elif i_inst > 0 and i_curto >= i_inst:
            tempo_calculado = 0.015
            st.markdown(
                f"""
            <div class='trip-alert'>
                <h3>💥 ATUADO POR INSTANTÂNEO ({funcao[:4].replace('67','67I').replace('51','50')})</h3>
                <p>O nível de curto superou o limite do elemento instantâneo. Disparo disparado em {tempo_calculado*1000:.0f} ms.</p>
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            if padrao_curva == "IEC":
                tempo_calculado = tms * (
                    CURVAS_IEC[tipo_curva]["beta"]
                    / (multiplo ** CURVAS_IEC[tipo_curva]["alpha"] - 1)
                )
            elif padrao_curva == "IEEE/ANSI":
                p = CURVAS_ANSI[tipo_curva]["P"]
                tempo_calculado = tms * (
                    CURVAS_ANSI[tipo_curva]["A"] / (multiplo ** p - 1)
                    + CURVAS_ANSI[tipo_curva]["B"]
                )
            else:
                p = CURVAS_IAC[tipo_curva].get("P", 1.0)
                a, b, c, d, e = (
                    CURVAS_IAC[tipo_curva]["A"],
                    CURVAS_IAC[tipo_curva]["B"],
                    CURVAS_IAC[tipo_curva]["C"],
                    CURVAS_IAC[tipo_curva]["D"],
                    CURVAS_IAC[tipo_curva]["E"],
                )
                base_val = multiplo ** p - c
                if base_val > 0:
                    tempo_calculado = tms * (
                        a
                        + b / base_val
                        + d / (base_val ** 2)
                        + e / (base_val ** 3)
                    )
            if tempo_calculado is not None and multiplo > 1.0 and zona_operacao:
                st.markdown(
                    f"""
                <div class='trip-alert' style='border-color: #fd7e14; color: #a04e00; background-color: #fffaf5;'>
                    <h3>⏳ DISPARO TEMPORIZADO EM CURVA</h3>
                    <p>Tempo estimado de atuação: <strong>{tempo_calculado:.4f} segundos</strong>.</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )
    with col2:
        st.subheader("📈 Curva de Tempo de Atuação (Tempo Inverso)")
        multiplos_eixo = np.linspace(1.1, 20, 200)
        plt.figure(figsize=(7, 4.5))
        if padrao_curva == "IEC":
            tempos_eixo = tms * (
                CURVAS_IEC[tipo_curva]["beta"]
                / (multiplos_eixo ** CURVAS_IEC[tipo_curva]["alpha"] - 1)
            )
        elif padrao_curva == "IEEE/ANSI":
            p = CURVAS_ANSI[tipo_curva]["P"]
            tempos_eixo = tms * (
                CURVAS_ANSI[tipo_curva]["A"] / (multiplos_eixo ** p - 1)
                + CURVAS_ANSI[tipo_curva]["B"]
            )
        else:
            p = CURVAS_IAC[tipo_curva].get("P", 1.0)
            a, b, c, d, e = (
                CURVAS_IAC[tipo_curva]["A"],
                CURVAS_IAC[tipo_curva]["B"],
                CURVAS_IAC[tipo_curva]["C"],
                CURVAS_IAC[tipo_curva]["D"],
                CURVAS_IAC[tipo_curva]["E"],
            )
            base_eixo = multiplos_eixo ** p - c
            tempos_eixo = tms * (a+ b / base_eixo + d / (base_eixo ** 2)+ e / (base_eixo ** 3)
            )
        plt.plot(multiplos_eixo, tempos_eixo, label=tipo_curva, color="#007BFF", lw=2)
        if multiplo > 1.0 and zona_operacao:
            plt.scatter(
                [multiplo],
                [tempo_calculado],
                color="red",
                zorder=5,
                s=100,
                label=f"Ponto de Falha ({multiplo:.2f}x, {tempo_calculado:.3f}s)",
            )
        plt.xlabel("Múltiplo de Partida (I / I_set)")
        plt.ylabel("Tempo de Atuação (segundos)")
        plt.yscale("log")
        plt.grid(True, which="both", ls="--", alpha=0.5)
        plt.legend()
        st.pyplot(plt.gcf())
        plt.close()
# --- DIAGRAMA POLAR EXCLUSIVO DA FUNÇÃO ANSI 67 ---
    if funcao == "ANSI 67 (Sobrecorrente Direcional)":
        st.write("---")
        st.subheader("📐 Diagrama Fasorial com Lógica Direcional Integrada")
        # Layout em duas colunas: Gráfico à esquerda, parâmetros à direita
        col_grafico, col_controles = st.columns([1.2, 1])
        with col_controles:
            st.markdown("### ⚙️ Parâmetros de Ajuste (MTA)")
            # Ângulo de Torque Máximo para definir a inclinação das zonas direcionais
            mta = st.number_input("Ângulo de Torque Máximo (MTA °)", min_value=-180.0, max_value=180.0, value=45.0, step=5.0)
            st.markdown("### ⚡ Parâmetros da Falta (Curto)")
            isc_mag = st.number_input("Magnitude do Curto (Isc)", min_value=0.0, value=120.0, step=10.0)
            isc_ang = st.number_input("Ângulo do Curto (°)", min_value=-360.0, max_value=360.0, value=-45.0, step=5.0)
            st.markdown("---")
            st.markdown("### 🎛️ Seleção de Visibilidade")
            st.write("**Zonas de Proteção**")
            exibir_zonas = st.checkbox("🎨 Exibir Fundo Direto/Reverso",value=True)
            # Valores de regime baseados no seu sistema
            st.write("**Tensões**")
            exibir_va = st.checkbox("🟠 Exibir Va",
    value=True)

            if exibir_va:
                col1, col2 = st.columns(2)
                with col1:
                        va_mag = st.number_input(
                            "Va (V)",
                            min_value=0.0,
                            value=66.4,
                            step=0.1,
                            format="%.2f",
                            key="va_mag_input"
        )
                with col2:
                        va_ang = st.number_input(
                        "Ângulo Va (°)",
                        min_value=-360.0,
                        max_value=360.0,
                        value=0.0,
                        step=1.0,
                        format="%.1f",
                        key="va_ang_input"
        )
            else:
                va_mag = 0.0
                va_ang = 0.0
            exibir_vb = st.checkbox("🟣 Exibir Vb", value=True)
            if exibir_vb:
                col1, col2 = st.columns(2)
                with col1:
                    vb_mag = st.number_input(
                    "Vb (V)",
                    min_value=0.0,
                    value=66.4,
                    step=0.1,
                    format="%.2f",
                    key="vb_mag_input"
            )
                    with col2:
                        vb_ang = st.number_input(
                        "Ângulo Vb (°)",
                        min_value=-360.0,
                        max_value=360.0,
                        value=-120.0,
                        step=1.0,
                        format="%.1f",
                        key="vb_ang_input"
        )
            else:
                vb_mag = 0.0
                vb_ang = 0.0
            exibir_vc = st.checkbox("🟢 Exibir Vc",value=True)
            if exibir_vc:
                col1, col2 = st.columns(2)
                with col1:
                    vc_mag = st.number_input(
                    "Vc (V)",
                    min_value=0.0,
                    value=66.4,
                    step=0.1,
                    format="%.2f",
                    key="vc_mag_input"
        )
                with col2:
                    vc_ang = st.number_input("Ângulo Vc (°)", min_value=-360.0,
                    max_value=360.0,

                    value=120.0,

                    step=1.0,

                    format="%.1f",

                    key="vc_ang_input"

        )

            else:
                vc_mag = 0.0
                vc_ang = 0.0
             # ============================================================

# CORRENTES

# ============================================================
            st.write("**Correntes Nominais**")
# ---------- Ia ----------
            exibir_ia = st.checkbox( "🔴 Exibir Ia",
    value=True
)

            if exibir_ia:
                col1, col2 = st.columns(2)
                with col1:
                     ia_mag = st.number_input(
                    "Ia (A)",
                    min_value=0.0,
                    value=40.0,
                    step=0.1,
                    format="%.2f",
                    key="ia_mag_input"
        )

                with col2:
                    ia_ang = st.number_input(
                    "Ângulo Ia (°)",
                    min_value=-360.0,
                    max_value=360.0,
                    value=-30.0,
                    step=1.0,
                    format="%.1f",
                    key="ia_ang_input"
        )

            else:
                ia_mag = 0.0
                ia_ang = 0.0
                # ---------- Ib ----------
            exibir_ib = st.checkbox("🟢 Exibir Ib",
    value=True

)

            if exibir_ib:
                col1, col2 = st.columns(2)
                with col1:
                    ib_mag = st.number_input(
                    "Ib (A)",
                    min_value=0.0,
                    value=40.0,
                    step=0.1,
                    format="%.2f",
                    key="ib_mag_input"
        )

                with col2:
                    ib_ang = st.number_input(
                    "Ângulo Ib (°)",
                     min_value=-360.0,
                    max_value=360.0,
                    value=-150.0,
                    step=1.0,
                    format="%.1f",
                    key="ib_ang_input"
        )

            else:

                    ib_mag = 0.0

                    ib_ang = 0.0

# ---------- Ic ----------

            exibir_ic = st.checkbox("🔵 Exibir Ic",

    value=True

)

            if exibir_ic:

                col1, col2 = st.columns(2)

                with col1:

                    ic_mag = st.number_input(

                    "Ic (A)",

                    min_value=0.0,

                    value=40.0,

                    step=0.1,

                    format="%.2f",

                    key="ic_mag_input"

        )

                with col2:

                    ic_ang = st.number_input(

                    "Ângulo Ic (°)",

                    min_value=-360.0,

                    max_value=360.0,

                    value=90.0,

                    step=1.0,

                    format="%.1f",

                    key="ic_ang_input"

        )

            else:

                ic_mag = 0.0

                ic_ang = 0.0

            # ============================================================

# FALTA / CORRENTE DE CURTO-CIRCUITO

# ============================================================

            st.write("**Falta**")

            exibir_isc = st.checkbox("🔥 Exibir Corrente de Curto (Isc)", value=True)

            if exibir_isc:

                col1, col2 = st.columns(2)

                with col1:

                    isc_mag = st.number_input(

                    "Isc (A)",

                    min_value=0.0,

                    value=120.0,

                    step=10.0,

                    format="%.2f",

                    key="isc_mag_input"

        )

                with col2:

                    isc_ang = st.number_input(

                    "Ângulo Isc (°)",

                    min_value=-360.0,

                    max_value=360.0,

                    value=-45.0,

                    step=5.0,

                    format="%.1f",

                    key="isc_ang_input"

        )

            else:

                    isc_mag = 0.0

                    isc_ang = 0.0

        with col_grafico:

            # 1. Configuração Inicial do Gráfico Polar

            fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"projection": "polar"})

            ax.set_theta_zero_location("E")  # 0° na horizontal direita (Leste)

            # Converte ângulos importantes para radianos

            mta_rad = np.radians(mta)

            falha_rad = np.radians(isc_ang)

            # 2. Definição Dinâmica da Escala do Raio Máximo

            valores_ativos = [

                va_mag if exibir_va else 0, vb_mag if exibir_vb else 0, vc_mag if exibir_vc else 0,

                ia_mag if exibir_ia else 0, ib_mag if exibir_ib else 0, ic_mag if exibir_ic else 0,

                isc_mag if exibir_isc else 0

            ]

            raio_max = max(valores_ativos) if max(valores_ativos) > 0 else 1.0

            r_limite = raio_max * 1.25

            ax.set_rmax(r_limite)

            # 3. Renderização de Fundo: Zonas Direta, Reversa e Linhas de Fronteira (Quadratura)

            if exibir_zonas:

                # Constrói os arcos de 180° que dividem as duas metades do gráfico

                abertura_direta = np.linspace(mta_rad - np.pi / 2, mta_rad + np.pi / 2, 100)

                abertura_reversa = np.linspace(mta_rad + np.pi / 2, mta_rad + 3 * np.pi / 2, 100)

                r_fundo = np.ones(100) * r_limite

                # Preenche o fundo com transparência suave (alpha) para não sumir com as setas

                ax.fill_between(abertura_direta, 0, r_fundo, color="green", alpha=0.08, label="Zona Direta (Forward)")

                ax.fill_between(abertura_reversa, 0, r_fundo, color="red", alpha=0.04, label="Zona Reversa (Reverse)")

                # Linha tracejada do Ângulo de Torque Máximo (MTA)

                ax.plot([mta_rad, mta_rad], [0, r_limite], color="darkgreen", lw=2.0, ls="--", label=f"Linha MTA ({mta}°)")

                # Linha ortogonal pontilhada representando a Fronteira Direcional da Quadratura

                ax.plot([mta_rad - np.pi/2, mta_rad + np.pi/2], [r_limite, r_limite], color="black", lw=1.5, ls=":", label="Fronteira 90°")

            # 4. Paleta de Cores Mapeada do seu Software de Referência

            cores_tensoes = {"a": "#E67E22", "b": "#9B59B6", "c": "#1ABC9C"}  # Laranja, Roxo, Verde Água

            cores_correntes = {"a": "#C0392B", "b": "#27AE60", "c": "#2980B9"} # Vermelho, Verde, Azul

            cor_curto = "#FF5722"  # Laranja Elétrico para destacar o vetor de falta

            # Função interna para desenhar os fasores

            def desenhar_vetor(magnitude, angulo_graus, cor, nome,unidade, largura=2.5):

                rad = np.radians(angulo_graus)

                ax.annotate(

                    "",

                    xy=(rad, magnitude),

                    xytext=(0, 0),

                    arrowprops=dict(

                        facecolor=cor,

                        edgecolor=cor,

                        arrowstyle="->",

                        lw=largura,

                        shrinkA=0,

                        shrinkB=0

                    ),

                )

                texto =(

                 f"{nome}\n"

                f"{magnitude:.1f} {unidade} ∠ {angulo_graus:.0f}°"

                )

    # Posiciona o texto um pouco além da ponta

                ax.text(

                    rad,

                    magnitude * 1.10,

                    texto,

                    color=cor,

                    weight="bold",

                    fontsize=8,

                    ha="center",

                     va="center",

                    bbox=dict(

                        boxstyle="round,pad=0.25",

                        facecolor="white",

                        edgecolor=cor,

                        alpha=0.85

                    )

                )

            # 5. Plotagem das Tensões (Va, Vb, Vc) de acordo com a seleção

            if exibir_va and va_mag > 0: desenhar_vetor(va_mag, va_ang, cores_tensoes["a"], "Va","V")

            if exibir_vb and vb_mag > 0: desenhar_vetor(vb_mag, vb_ang, cores_tensoes["b"], "Vb","V")

            if exibir_vc and vc_mag > 0: desenhar_vetor(vc_mag, vc_ang, cores_tensoes["c"], "Vc","V")

            # 6. Plotagem das Correntes Nominais (Ia, Ib, Ic) de acordo com a seleção

            if exibir_ia and ia_mag > 0: desenhar_vetor(ia_mag, ia_ang, cores_correntes["a"], "Ia","A")

            if exibir_ib and ib_mag > 0: desenhar_vetor(ib_mag, ib_ang, cores_correntes["b"], "Ib","A")

            if exibir_ic and ic_mag > 0: desenhar_vetor(ic_mag, ic_ang, cores_correntes["c"], "Ic","A")

            # 7. Plotagem da Corrente de Curto Simulada (Vetor mais espesso)

            if exibir_isc and isc_mag > 0:

                desenhar_vetor(isc_mag, isc_ang, cor_curto,"Isc","A)", largura=4.0)

            # 8. Limpeza Visual e Ajustes Estéticos Finais

            ax.set_yticklabels([])

            ax.set_xticks(np.radians([0, 90, 180, 270]))

            ax.set_xticklabels(["0°", "90°", "180°", "270°"], color="gray", fontsize=9)

            ax.grid(True, alpha=0.3, color="#BDC3C7", ls="--")

            # Reposiciona a legenda para baixo do gráfico de forma organizada

            ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.35), ncol=2, fontsize=8)

            # Renderização no Streamlit

            st.pyplot(fig)

            plt.close()

            # 9. Lógica de Diagnóstico Automatizada por Texto

            diff_angular = np.arctan2(np.sin(falha_rad - mta_rad), np.cos(falha_rad - mta_rad))

            if np.abs(diff_angular) <= np.pi / 2:

                st.success(f"✅ **Análise Direcional:** O vetor de curto-circuito (Isc) está posicionado na **Zona Direta (Forward)**.")

            else:

                st.error(f"❌ **Análise Direcional:** O vetor de curto-circuito (Isc) está posicionado na **Zona Reversa (Reverse)**. Função 67 bloqueada.")

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

        # --- LÓGICA PARA FUNÇÃO ANSI 21 (PROTEÇÃO DE DISTÂNCIA / SUBIMPEDÂNCIA) ---

elif funcao == "ANSI 21 (Proteção de Distância)":
    st.sidebar.subheader("📐 Parâmetros de Distância (ANSI 21)")
    # Parâmetros de ajuste de alcance da Linha (Zonas de Proteção)
    st.sidebar.markdown("**Ajustes de Zona (Mho)**")
    z1_reach = st.sidebar.number_input("Alcance da Zona 1 (Z1) [Ω]:", min_value=0.1, value=4.0, step=0.5, help="Instantânea (geralmente cobrindo 80% da linha)")
    z2_reach = st.sidebar.number_input("Alcance da Zona 2 (Z2) [Ω]:", min_value=0.1, value=6.0, step=0.5, help="Temporizada (geralmente cobrindo 120% da linha)")
    t_z2 = st.sidebar.number_input("Tempo de Atraso da Zona 2 (t_Z2) [s]:", min_value=0.0, value=0.4, step=0.1)
    # Inputs de medição em tempo real fornecidos pelos TCs e TPs do sistema
    st.sidebar.markdown("---")
    st.sidebar.markdown("**⚡ Medições em Tempo Real**")
    v_medido = st.sidebar.number_input("Tensão de Fase Medida (V RMS) [V]:", min_value=1.0, value=65.0, step=5.0)
    i_medido = st.sidebar.number_input("Corrente de Fase Medida (I RMS) [A]:", min_value=0.1, value=15.0, step=1.0)
    angulo_graus = st.sidebar.number_input("Ângulo entre V e I (Fase) [°]:", min_value=-180.0, max_value=180.0, value=30.0, step=5.0)
    # --- PROCESSAMENTO MATEMÁTICO DA IMPEDÂNCIA APARENTE ---
    # Conversão do ângulo para radianos para aplicar na decomposição complexa
    angulo_rad = np.radians(angulo_graus)
    # Cálculo do módulo da impedância (Z = V / I)
    z_modulo = v_medido / i_medido
    # Decomposição cartesiana (R + jX) para plotagem no plano R-X
    r_medido = z_modulo * np.cos(angulo_rad)
    x_medido = z_modulo * np.sin(angulo_rad)
    # --- PROCESSAMENTO LOGICO NA TELA PRINCIPAL (COL1 E COL2) ---
    with col1:
        st.subheader("📊 Resultados da Proteção de Distância (ANSI 21)")
        st.info("Princípio de Medição de Impedância de Linha:")
        st.latex(r"Z\_{aparente} =\frac{V\_{fase}}{I\_{fase}} = R + jX")
        # Lógica de Trip por Zona (Característica Mho Circular)
        # Uma impedância está dentro de uma zona Mho se Z_medido <= Z_alcance * cos(theta_medido - theta_linha)
        # Para fins didáticos e visuais diretos no plano complexo, avaliamos o módulo frente ao círculo centrado na origem:
        if z_modulo <= z1_reach:
            status_trip = "🚨 TRIP INSTANTÂNEO (ZONA 1)"
            detalhe_status = "Curto-circuito severo detectado no trecho principal da linha protegido."
            badge_html = f"<div class='trip-alert'><h3>🚨 TRIP INSTANTÂNEO TRIGERADO</h3><p>Falha crítica dentro do alcance da Zona 1. Atuação em: <strong>0.00 s</strong></p></div>"
            cor_borda = "#d9534f"
        elif z_modulo <= z2_reach:
            status_trip = "⏳ TRIP TEMPORIZADO (ZONA 2)"
            detalhe_status = f"Falha na zona de retaguarda. Temporizador ativo aguardando coordenação."
            badge_html = f"<div class='trip-alert' style='background-color: #FF9800;'><h3>⏳ DISPARO TEMPORIZADO ATIVO</h3><p>Falha detectada na Zona 2. Coordenação em: <strong>{t_z2:.2f} s</strong></p></div>"
            cor_borda = "#FF9800"
        else:
            status_trip = "✅ OPERAÇÃO ESTÁVEL"
            detalhe_status = "Impedância vista pelo relé está na zona de carga normal (Região Segura)."
            badge_html = "<div class='badge-status badge-success'>✅ Sistema Seguro: A impedância calculada está fora das zonas de falta.</div>"
            cor_borda = "#4CAF50"
        # Exibição nos cartões estruturados HTML do seu sistema
        st.markdown(f"""
        <div class='card-container'>
            <div class='card-protecao' style='border-left-color: {cor_borda};'>
                <h4>Impedância Calculada</h4>
                <p>{z_modulo:.2f} <span>Ω</span></p>
            </div>
            <div class='card-protecao' style='border-left-color: #00bcd4;'>
                <h4>Ponto Cartesiano</h4>
                <p style='font-size: 1.05rem;'>{r_medido:.2f} + j{x_medido:.2f} <span>Ω</span></p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(badge_html, unsafe_allow_html=True)
    with col2:
        st.subheader("📈 Diagrama de Impedância (Plano R-X)")
        plt.figure(figsize=(7, 4.5))
        # Desenha as características circulares (Zonas Mho simplificadas centradas na origem para exibição limpa)
        theta_corte = np.linspace(0, 2 * np.pi, 200)
        # Zona 1
        r_z1 = z1_reach * np.cos(theta_corte)
        x_z1 = z1_reach * np.sin(theta_corte)
        plt.plot(r_z1, x_z1, color="#d9534f", ls="--", lw=1.5, label=f"Zona 1 ({z1_reach}Ω)")
        plt.fill(r_z1, x_z1, color="#d9534f", alpha=0.08)
        # Zona 2
        r_z2 = z2_reach * np.cos(theta_corte)
        x_z2 = z2_reach * np.sin(theta_corte)
        plt.plot(r_z2, x_z2, color="#FF9800", ls="-.", lw=1.5, label=f"Zona 2 ({z2_reach}Ω)")
        plt.fill(r_z2, x_z2, color="#FF9800", alpha=0.04)
        # Plota o ponto de operação medido em tempo real
        plt.scatter([r_medido], [x_medido], color="blue", s=120, zorder=5, label=f"Z_aparente Medido")
        # Linha vetorial (fasor) da origem até a impedância medida
        plt.plot([0, r_medido], [0, x_medido], color="blue", lw=2, alpha=0.7)
        # Configurações do gráfico cartesiano elétrico R-X
        plt.axhline(0, color="black", lw=1)
        plt.axvline(0, color="black", lw=1)
        plt.xlabel("Resistência - R (Ohms)")
        plt.ylabel("Reatância - X (Ohms)")
        # Define limites dinâmicos para manter o ponto medido sempre visível
        limite_grafico = max(z2_reach * 1.5, z_modulo * 1.3)
        plt.xlim(-limite_grafico, limite_grafico)
        plt.ylim(-limite_grafico, limite_grafico)
        plt.grid(True, ls="--", alpha=0.5)
        plt.gca().set_aspect('equal', adjustable='box') # Mantém o círculo perfeitamente redondo
        plt.legend(loc="upper left")
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
    # Atualizado para incluir o modelo Inepar PM II no seu padrão de selectbox
    fabricante = st.sidebar.selectbox("Modelo/Fabricante do Relé:", ["Schneider Sepam", "Siemens (Siprotec/Reyrolle)", "GE Multilin", "Pextron (Réplica IEC)", "BBC Brown Boveri (Tipo ST)", "Inepar PM II (Proteção de Motores)"])
    i_b = st.sidebar.number_input("Corrente de Base / Nominal (I_b) [A]:", min_value=0.1, value=3.0, step=0.5)
    # Configuração de constantes default para o modelo Inepar PM II (Constantes de motor costumam ser longas)
    val_tau_padrao = 2400.0 if fabricante == "Inepar PM II (Proteção de Motores)" else 1200.0
    if fabricante == "BBC Brown Boveri (Tipo ST)": val_tau_padrao = 2400.0
    tau = st.sidebar.number_input("Constante de Tempo de Aquecimento (τ) [segundos]:", min_value=1.0, value=val_tau_padrao, step=10.0)
    val_es_padrao = 100.0 if fabricante in ["BBC Brown Boveri (Tipo ST)", "Inepar PM II (Proteção de Motores)"] else 50.0
    es = st.sidebar.number_input("Capacidade Térmica de Disparo (Es) [%]:", min_value=1.0, max_value=200.0, value=val_es_padrao, step=5.0) / 100.0
    e_inicial = st.sidebar.number_input("Estado Térmico Inicial (E_inicial) [%]:", min_value=0.0, max_value=100.0, value=0.0, step=5.0) / 100.0
    # --- CONDICIONAIS DE REGIME DE CADA FABRICANTE ---
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
    elif fabricante == "BBC Brown Boveri (Tipo ST)":
        st.sidebar.markdown("**Abordagem BBC ST:** Modelo clássico baseado na constante térmica bimetálica com correção opcional.")
        i_bbc = st.sidebar.number_input("Corrente RMS Medida de Carga (I) [A]:", min_value=0.1, value=5.0, step=0.5)
        correcao_ferro = st.sidebar.checkbox("Aplicar Correção por Perdas no Ferro (Fig. 15)", value=True)
        if correcao_ferro and e_inicial < 0.20:
            e_inicial = 0.20
            st.sidebar.caption("💡 *E_inicial ajustado automaticamente para 20% devido às perdas no ferro.*")
        razao_corrente = i_bbc / i_b
    elif fabricante == "Inepar PM II (Proteção de Motores)":
        st.sidebar.markdown("**Abordagem Inepar PM II:** Modelo para motores térmicos. Pondera o aquecimento assimétrico severo do rotor via corrente I2.")
        i_fase_max = st.sidebar.number_input("Maior Corrente de Fase (I_fase) [A]:", min_value=0.1, value=6.0, step=0.5)
        i2_deseq = st.sidebar.number_input("Corrente de Sequência Negativa (I2) [A]:", min_value=0.0, value=0.5, step=0.1)
        k_rotor = st.sidebar.number_input("Fator de Ponderação do Rotor (K_rotor):", min_value=1.0, max_value=6.0, value=3.5, step=0.5)
        # Equação oficial do estresse térmico composto do rotor Inepar PM II
        i_eq_inepar = np.sqrt(i_fase_max**2 + (k_rotor * (i2_deseq**2)))
        st.sidebar.info(f"I_eq Térmica Calculada (Inepar PM II): {i_eq_inepar:.2f} A")
        razao_corrente = i_eq_inepar / i_b
    else:
        st.sidebar.markdown("**Abordagem Pextron:** Modelo de imagem térmica baseado na norma IEC 60255-149.")
        i_pextron = st.sidebar.number_input("Corrente Equivalente de Fase Medida (I) [A]:", min_value=0.1, value=6.0, step=0.5)
        razao_corrente = i_pextron / i_b
    # --- BLOCO DE RESULTADOS (COL1 E COL2 MANTIDOS INTEGRALMENTE NO SEU PADRÃO) ---
    with col1:
        st.subheader(f"📊 Resultados da ANSI 49 ({fabricante})")
        st.info("Fórmula de Imagem Térmica Utilizada:")
        if fabricante in ["Schneider Sepam", "Pextron (Réplica IEC)", "BBC Brown Boveri (Tipo ST)", "Inepar PM II (Proteção de Motores)"]:
            st.latex(r"t =\tau\cdot\ln\left(\frac{(I\_{eq}/I_b)^2 - E\_{inicial}}{(I\_{eq}/I_b)^2 - Es}\right)")
        elif fabricante == "Siemens (Siprotec/Reyrolle)":
            st.latex(r"I\_{eq}^2 = I_1^2 + (k_2\cdot I_2^2)")
            st.latex(r"t = \tau\cdot\ln\left(\frac{(I\_{eq}/I_b)^2 - E\_{inicial}}{(I\_{eq}/I_b)^2 - Es} \right)")
        elif fabricante == "GE Multilin":
            st.latex(r"I\_{eq} = I_1 \cdot \sqrt{1 + k\cdot (I_2/I_1)^2}")
            st.latex(r"t = \tau\cdot\ln\left(\frac{(I\_{eq}/I_b)^2 - E\_{inicial}}{(I\_{eq}/I_b)^2 - Es} \right)")
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
                <p>Estágio crítico de carregamento acumulado. Atuação em: <strong>{t_trip:.2f} s</strong> (\~{t_trip/60:.2f} min).</p>
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

# --- SEÇÃO DE CONTATO NO FINAL DA BARRA LATERAL ---

st.sidebar.markdown("""
<div class='card-contato'>
    <h4>📬 Dúvidas ou Suporte?</h4>
    <p>Entre em contato com o desenvolvedor:</p>
    <p class='nome'>Edson Silva</p>
    <p><a class='email' href='mailto:edsn_silva@outlook.com'>edsn_silva@outlook.com</a></p>
    <p><a class='telefone' href='https://wa.me' target='_blank'>+55 (19) 98360-1032</a></p>
</div>
""", unsafe_allow_html=True)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Cálculo de Proteção (51, 67, 32, 27, 59, 87, 49)",
    layout="wide",
    initial_sidebar_state="expanded"
)
# 1. Carrega o arquivo style.css que está na mesma pasta
with open("style.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- INJEÇÃO EXCLUSIVA DE JAVASCRIPT ---
st.markdown("""
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

# Título e Subtítulo customizados com HTML (Estilizados pelo style.css externo)
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
        "ANSI 67N (Sobrecorrente Direcional de Terra)",
        "ANSI 32 (Potência Inversa)",
        "ANSI 21 (Proteção de Distância)",
        "ANSI 27 (Subtensão)",
        "ANSI 59 (Sobretensão)",
        "ANSI 87 (Proteção Diferencial Percentual)",
        "ANSI 49 (Sobrecarga Térmica)",
    ],
)

col1, col2 = st.columns([1, 1.3])

# --- LÓGICA DAS FUNÇÕES DE CORRENTE (51 / 67) ---
if funcao in [
    "ANSI 51 (Sobrecorrente Temporizada)",
    "ANSI 67 (Sobrecorrente Direcional)",
    "ANSI 67N (Sobrecorrente Direcional de Terra)",
]:
    padrao_curva = st.sidebar.selectbox(
        "Norma da Curva:", ["IEC", "IEEE/ANSI", "IAC"]
    )
    if padrao_curva == "IEC":
        tipo_curva = st.sidebar.selectbox(
            "Tipo de Curva (IEC):", list(CURVAS_IEC.keys())
        )
        tms = st.sidebar.number_input(
            "Dial de Tempo (TMS):",
            min_value=0.01,
            max_value=1.5,
            value=0.10,
            step=0.01,
        )
    elif padrao_curva == "IEEE/ANSI":
        tipo_curva = st.sidebar.selectbox(
            "Tipo de Curva (ANSI/IEEE):", list(CURVAS_ANSI.keys())
        )
        tms = st.sidebar.number_input(
            "Dial de Tempo (TD):",
            min_value=0.1,
            max_value=15.0,
            value=1.0,
            step=0.01,
        )
    else:
        tipo_curva = st.sidebar.selectbox(
            "Tipo de Curva (IAC):", list(CURVAS_IAC.keys())
        )
        tms = st.sidebar.number_input(
            "Dial de Tempo (TD):",
            min_value=0.1,
            max_value=15.0,
            value=1.0,
            step=0.01,
        )

    i_set = st.sidebar.number_input(
        "Corrente de Partida (A):", min_value=0.1, value=3.00, step=0.5
    )
    i_curto = st.sidebar.number_input(
        "Corrente de Curto Simulado (A):", min_value=0.1, value=6.00, step=0.01
    )
    i_inst = st.sidebar.number_input(
        "Corrente do Instantâneo (A) [0=Off]:",
        min_value=0.0,
        value=15.00,
        step=1.0,
    )
    
    # Parâmetros específicos dos elementos direcionais 67 e 67N
    if funcao == "ANSI 67 (Sobrecorrente Direcional)":
        st.sidebar.subheader("📐 Parâmetros Direcionais (67)")
        mta = st.sidebar.slider(
            "Ângulo de Máximo Torque - MTA (°):", -180, 180, 45
        )
        angulo_falha = st.sidebar.slider(
            "Ângulo da Corrente de Falha (°):", -180, 180, 30
        )
    elif funcao == "ANSI 67N (Sobrecorrente Direcional de Terra)":
        st.sidebar.subheader("🌎 Parâmetros Direcionais de Terra (67N)")
        mta = st.sidebar.slider(
            "MTA / Ângulo Característico (°):", -180, 180, 45
        )
        i0_set = st.sidebar.number_input(
            "Partida de Corrente Residual 3I0 (A):", min_value=0.01, value=1.00, step=0.10
        )
        i0_curto = st.sidebar.number_input(
            "Corrente Residual de Falta 3I0 (A):", min_value=0.0, value=5.00, step=0.10
        )
        angulo_i0 = st.sidebar.slider(
            "Ângulo de 3I0 (°):", -180, 180, 30
        )
        angulo_v0 = st.sidebar.slider(
            "Ângulo de 3V0 / Polarização (°):", -180, 180, 0
        )
        i0_inst = st.sidebar.number_input(
            "3I0 Instantâneo (A) [0=Off]:", min_value=0.0, value=0.0, step=0.10
        )
        i_set = i0_set
        i_curto = i0_curto
        i_inst = i0_inst
        angulo_falha = angulo_i0

    multiplo = i_curto / i_set
    zona_operacao = True
    if funcao in ["ANSI 67 (Sobrecorrente Direcional)", "ANSI 67N (Sobrecorrente Direcional de Terra)"]:
        if funcao == "ANSI 67N (Sobrecorrente Direcional de Terra)":
            diff_angulo = (angulo_i0 - angulo_v0 - mta + 180) % 360 - 180
        else:
            diff_angulo = (angulo_falha - mta + 180) % 360 - 180
        if not (-90 <= diff_angulo <= 90):
            zona_operacao = False

    with col1:
        st.subheader(f"📊 Resultados da {funcao[:7]}")
        st.info("Fórmula Utilizada:")
        if padrao_curva == "IEC":
            st.latex(
                r"t = TMS \cdot \left[ \frac{k}{(I_{medida}/I_{partida})^{\alpha} - 1} \right]"
            )
        else:
            st.latex(
                r"t = TD \cdot \left[ \frac{A}{(I_{medida}/I_{partida})^{P} - 1} + B \right]"
            )

        # Grid HTML/CSS para substituição dos st.metric tradicionais
        st.markdown(
            f"""
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
        """,
            unsafe_allow_html=True,
        )

        if funcao in ["ANSI 67 (Sobrecorrente Direcional)", "ANSI 67N (Sobrecorrente Direcional de Terra)"]:
            if zona_operacao:
                st.markdown(
                    "<div class='badge-direcional badge-success'>🎯 Direção de AVANÇO (Forward) - Falha na Zona de Operação</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    "<div class='badge-direcional badge-error'>🔒 Direção de RECUO (Reverse) - Relé Bloqueado</div>",
                    unsafe_allow_html=True,
                )

        tempo_calculado = None
        if multiplo <= 1.0:
            st.warning("⚠️ Corrente abaixo do ajuste de partida. Sem atuação.")
        elif not zona_operacao:
            st.info(
                "ℹ️ Relé direcional bloqueado por ângulo. Atuação infinita."
            )
        elif i_inst > 0 and i_curto >= i_inst:
            tempo_calculado = 0.015
            st.markdown(
                f"""
            <div class='trip-alert'>
                <h3>💥 ATUADO POR INSTANTÂNEO ({funcao[:4].replace('67','67I').replace('51','50')})</h3>
                <p>O nível de curto superou o limite do elemento instantâneo. Disparo disparado em {tempo_calculado*1000:.0f} ms.</p>
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            if padrao_curva == "IEC":
                tempo_calculado = tms * (
                    CURVAS_IEC[tipo_curva]["beta"]
                    / (multiplo ** CURVAS_IEC[tipo_curva]["alpha"] - 1)
                )
            elif padrao_curva == "IEEE/ANSI":
                p = CURVAS_ANSI[tipo_curva]["P"]
                tempo_calculado = tms * (
                    CURVAS_ANSI[tipo_curva]["A"] / (multiplo ** p - 1)
                    + CURVAS_ANSI[tipo_curva]["B"]
                )
            else:
                p = CURVAS_IAC[tipo_curva].get("P", 1.0)
                a, b, c, d, e = (
                    CURVAS_IAC[tipo_curva]["A"],
                    CURVAS_IAC[tipo_curva]["B"],
                    CURVAS_IAC[tipo_curva]["C"],
                    CURVAS_IAC[tipo_curva]["D"],
                    CURVAS_IAC[tipo_curva]["E"],
                )
                base_val = multiplo ** p - c
                if base_val > 0:
                    tempo_calculado = tms * (
                        a
                        + b / base_val
                        + d / (base_val ** 2)
                        + e / (base_val ** 3)
                    )

            if tempo_calculado is not None and multiplo > 1.0 and zona_operacao:
                st.markdown(
                    f"""
                <div class='trip-alert' style='border-color: #fd7e14; color: #a04e00; background-color: #fffaf5;'>
                    <h3>⏳ DISPARO TEMPORIZADO EM CURVA</h3>
                    <p>Tempo estimado de atuação: <strong>{tempo_calculado:.4f} segundos</strong>.</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    with col2:
        st.subheader("📈 Curva de Tempo de Atuação (Tempo Inverso)")
        multiplos_eixo = np.linspace(1.1, 20, 200)
        plt.figure(figsize=(7, 4.5))
        if padrao_curva == "IEC":
            tempos_eixo = tms * (
                CURVAS_IEC[tipo_curva]["beta"]
                / (multiplos_eixo ** CURVAS_IEC[tipo_curva]["alpha"] - 1)
            )
        elif padrao_curva == "IEEE/ANSI":
            p = CURVAS_ANSI[tipo_curva]["P"]
            tempos_eixo = tms * (
                CURVAS_ANSI[tipo_curva]["A"] / (multiplos_eixo ** p - 1)
                + CURVAS_ANSI[tipo_curva]["B"]
            )
        else:
            p = CURVAS_IAC[tipo_curva].get("P", 1.0)
            a, b, c, d, e = (
                CURVAS_IAC[tipo_curva]["A"],
                CURVAS_IAC[tipo_curva]["B"],
                CURVAS_IAC[tipo_curva]["C"],
                CURVAS_IAC[tipo_curva]["D"],
                CURVAS_IAC[tipo_curva]["E"],
            )
            base_eixo = multiplos_eixo ** p - c
            tempos_eixo = tms * (
                a
                + b / base_eixo
                + d / (base_eixo ** 2)
                + e / (base_eixo ** 3)
            )

        plt.plot(multiplos_eixo, tempos_eixo, label=tipo_curva, color="#007BFF", lw=2)
        if multiplo > 1.0 and zona_operacao:
            plt.scatter(
                [multiplo],
                [tempo_calculado],
                color="red",
                zorder=5,
                s=100,
                label=f"Ponto de Falha ({multiplo:.2f}x, {tempo_calculado:.3f}s)",
            )
        plt.xlabel("Múltiplo de Partida (I / I_set)")
        plt.ylabel("Tempo de Atuação (segundos)")
        plt.yscale("log")
        plt.grid(True, which="both", ls="--", alpha=0.5)
        plt.legend()
        st.pyplot(plt.gcf())
        plt.close() 
# --- DIAGRAMA POLAR EXCLUSIVO DA FUNÇÃO ANSI 67 ---
    if funcao == "ANSI 67 (Sobrecorrente Direcional)":
        st.write("---")
        st.subheader("📐 Diagrama Fasorial com Lógica Direcional Integrada")

        # Layout em duas colunas: Gráfico à esquerda, parâmetros à direita
        col_grafico, col_controles = st.columns([1.2, 1])
        

        with col_controles:
            st.markdown("### ⚙️ Parâmetros de Ajuste (MTA)")
            # Ângulo de Torque Máximo para definir a inclinação das zonas direcionais
            mta = st.number_input("Ângulo de Torque Máximo (MTA °)", min_value=-180.0, max_value=180.0, value=45.0, step=5.0)
        
            st.markdown("### ⚡ Parâmetros da Falta (Curto)")
            isc_mag = st.number_input("Magnitude do Curto (Isc)", min_value=0.0, value=120.0, step=10.0)
            isc_ang = st.number_input("Ângulo do Curto (°)", min_value=-360.0, max_value=360.0, value=-45.0, step=5.0)
        
            st.markdown("---")
            st.markdown("### 🎛️ Seleção de Visibilidade")
            st.write("**Zonas de Proteção**")
            exibir_zonas = st.checkbox("🎨 Exibir Fundo Direto/Reverso",value=True)

            # Valores de regime baseados no seu sistema
            st.write("**Tensões**")
            exibir_va = st.checkbox("🟠 Exibir Va",
    value=True
)
            if exibir_va:
                col1, col2 = st.columns(2)
                with col1:
                        va_mag = st.number_input(
                            "Va (V)",
                            min_value=0.0,
                            value=66.4,
                            step=0.1,
                            format="%.2f",
                            key="va_mag_input"
        )
                with col2:
                        va_ang = st.number_input(
                        "Ângulo Va (°)",
                        min_value=-360.0,
                        max_value=360.0,
                        value=0.0,
                        step=1.0,
                        format="%.1f",
                        key="va_ang_input"
        )
            else:
                va_mag = 0.0
                va_ang = 0.0
            exibir_vb = st.checkbox("🟣 Exibir Vb", value=True)   
            if exibir_vb:
                col1, col2 = st.columns(2)

                with col1:
                    vb_mag = st.number_input(
                    "Vb (V)",
                    min_value=0.0,
                    value=66.4,
                    step=0.1,
                    format="%.2f",
                    key="vb_mag_input"
            )

                    with col2:
                        vb_ang = st.number_input(
                        "Ângulo Vb (°)",
                        min_value=-360.0,
                        max_value=360.0,
                        value=-120.0,
                        step=1.0,
                        format="%.1f",
                        key="vb_ang_input"
        )
            else:
                vb_mag = 0.0
                vb_ang = 0.0


            exibir_vc = st.checkbox("🟢 Exibir Vc",value=True)

            if exibir_vc:
                col1, col2 = st.columns(2)

                with col1:
                    vc_mag = st.number_input(
                    "Vc (V)",
                    min_value=0.0,
                    value=66.4,
                    step=0.1,
                    format="%.2f",
                    key="vc_mag_input"
        )

                with col2:
                    vc_ang = st.number_input("Ângulo Vc (°)", min_value=-360.0,
                    max_value=360.0,
                    value=120.0,
                    step=1.0,
                    format="%.1f",
                    key="vc_ang_input"
        )
            else:
                vc_mag = 0.0
                vc_ang = 0.0

             # ============================================================
# CORRENTES
# ============================================================

            st.write("**Correntes Nominais**")

# ---------- Ia ----------
            exibir_ia = st.checkbox( "🔴 Exibir Ia",
    value=True
)

            if exibir_ia:  
                col1, col2 = st.columns(2)

                with col1:
                     ia_mag = st.number_input(
                    "Ia (A)",
                    min_value=0.0,
                    value=40.0,
                    step=0.1,
                    format="%.2f",
                    key="ia_mag_input"
        )

                with col2:
                    ia_ang = st.number_input(
                    "Ângulo Ia (°)",
                    min_value=-360.0,
                    max_value=360.0,
                    value=-30.0,
                    step=1.0,
                    format="%.1f",
                    key="ia_ang_input"
        )
            else:
                ia_mag = 0.0
                ia_ang = 0.0
                # ---------- Ib ----------
            exibir_ib = st.checkbox("🟢 Exibir Ib",
    value=True
)

            if exibir_ib:
                col1, col2 = st.columns(2)

                with col1:
                    ib_mag = st.number_input(
                    "Ib (A)",
                    min_value=0.0,
                    value=40.0,
                    step=0.1,
                    format="%.2f",
                    key="ib_mag_input"
        )

                with col2:
                    ib_ang = st.number_input(
                    "Ângulo Ib (°)",
                     min_value=-360.0,
                    max_value=360.0,
                    value=-150.0,
                    step=1.0,
                    format="%.1f",
                    key="ib_ang_input"
        )
            else:
                    ib_mag = 0.0
                    ib_ang = 0.0
# ---------- Ic ----------
            exibir_ic = st.checkbox("🔵 Exibir Ic",
    value=True
)

            if exibir_ic:
                col1, col2 = st.columns(2)

                with col1:
                    ic_mag = st.number_input(
                    "Ic (A)",
                    min_value=0.0,
                    value=40.0,
                    step=0.1,
                    format="%.2f",
                    key="ic_mag_input"
        )

                with col2:
                    ic_ang = st.number_input(
                    "Ângulo Ic (°)",
                    min_value=-360.0,
                    max_value=360.0,
                    value=90.0,
                    step=1.0,
                    format="%.1f",
                    key="ic_ang_input"
        )
            else:
                ic_mag = 0.0
                ic_ang = 0.0

            # ============================================================
# FALTA / CORRENTE DE CURTO-CIRCUITO
# ============================================================

            st.write("**Falta**")

            exibir_isc = st.checkbox("🔥 Exibir Corrente de Curto (Isc)", value=True)

            if exibir_isc:
                col1, col2 = st.columns(2)

                with col1:
                    isc_mag = st.number_input(
                    "Isc (A)",
                    min_value=0.0,
                    value=120.0,
                    step=10.0,
                    format="%.2f",
                    key="isc_mag_input"
        )

                with col2:
                    isc_ang = st.number_input(
                    "Ângulo Isc (°)",
                    min_value=-360.0,
                    max_value=360.0,
                    value=-45.0,
                    step=5.0,
                    format="%.1f",
                    key="isc_ang_input"
        )

            else:
                    isc_mag = 0.0
                    isc_ang = 0.0

        with col_grafico:
            # 1. Configuração Inicial do Gráfico Polar
            fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"projection": "polar"})
            ax.set_theta_zero_location("E")  # 0° na horizontal direita (Leste)
        
            # Converte ângulos importantes para radianos
            mta_rad = np.radians(mta)
            falha_rad = np.radians(isc_ang)

            # 2. Definição Dinâmica da Escala do Raio Máximo
            valores_ativos = [
                va_mag if exibir_va else 0, vb_mag if exibir_vb else 0, vc_mag if exibir_vc else 0,
                ia_mag if exibir_ia else 0, ib_mag if exibir_ib else 0, ic_mag if exibir_ic else 0,
                isc_mag if exibir_isc else 0
            ]
            raio_max = max(valores_ativos) if max(valores_ativos) > 0 else 1.0
            r_limite = raio_max * 1.25
            ax.set_rmax(r_limite)

            # 3. Renderização de Fundo: Zonas Direta, Reversa e Linhas de Fronteira (Quadratura)
            if exibir_zonas:
                # Constrói os arcos de 180° que dividem as duas metades do gráfico
                abertura_direta = np.linspace(mta_rad - np.pi / 2, mta_rad + np.pi / 2, 100)
                abertura_reversa = np.linspace(mta_rad + np.pi / 2, mta_rad + 3 * np.pi / 2, 100)
                r_fundo = np.ones(100) * r_limite

                # Preenche o fundo com transparência suave (alpha) para não sumir com as setas
                ax.fill_between(abertura_direta, 0, r_fundo, color="green", alpha=0.08, label="Zona Direta (Forward)")
                ax.fill_between(abertura_reversa, 0, r_fundo, color="red", alpha=0.04, label="Zona Reversa (Reverse)")

                # Linha tracejada do Ângulo de Torque Máximo (MTA)
                ax.plot([mta_rad, mta_rad], [0, r_limite], color="darkgreen", lw=2.0, ls="--", label=f"Linha MTA ({mta}°)")
                # Linha ortogonal pontilhada representando a Fronteira Direcional da Quadratura
                ax.plot([mta_rad - np.pi/2, mta_rad + np.pi/2], [r_limite, r_limite], color="black", lw=1.5, ls=":", label="Fronteira 90°")

            # 4. Paleta de Cores Mapeada do seu Software de Referência
            cores_tensoes = {"a": "#E67E22", "b": "#9B59B6", "c": "#1ABC9C"}  # Laranja, Roxo, Verde Água
            cores_correntes = {"a": "#C0392B", "b": "#27AE60", "c": "#2980B9"} # Vermelho, Verde, Azul
            cor_curto = "#FF5722"  # Laranja Elétrico para destacar o vetor de falta

            # Função interna para desenhar os fasores
            def desenhar_vetor(magnitude, angulo_graus, cor, nome,unidade, largura=2.5):
                rad = np.radians(angulo_graus)
                ax.annotate(
                    "",
                    xy=(rad, magnitude),
                    xytext=(0, 0),
                    arrowprops=dict(
                        facecolor=cor, 
                        edgecolor=cor, 
                        arrowstyle="->", 
                        lw=largura, 
                        shrinkA=0, 
                        shrinkB=0
                    ),
                )
                texto =(
                 f"{nome}\n"
                f"{magnitude:.1f} {unidade} ∠ {angulo_graus:.0f}°"
                )
    # Posiciona o texto um pouco além da ponta
                ax.text(
                    rad,
                    magnitude * 1.10,
                    texto,
                    color=cor,
                    weight="bold",
                    fontsize=8,
                    ha="center",
                     va="center",
                    bbox=dict(
                        boxstyle="round,pad=0.25",
                        facecolor="white",
                        edgecolor=cor,
                        alpha=0.85
                    )
                )
            # 5. Plotagem das Tensões (Va, Vb, Vc) de acordo com a seleção
            if exibir_va and va_mag > 0: desenhar_vetor(va_mag, va_ang, cores_tensoes["a"], "Va","V")
            if exibir_vb and vb_mag > 0: desenhar_vetor(vb_mag, vb_ang, cores_tensoes["b"], "Vb","V")
            if exibir_vc and vc_mag > 0: desenhar_vetor(vc_mag, vc_ang, cores_tensoes["c"], "Vc","V")

            # 6. Plotagem das Correntes Nominais (Ia, Ib, Ic) de acordo com a seleção
            if exibir_ia and ia_mag > 0: desenhar_vetor(ia_mag, ia_ang, cores_correntes["a"], "Ia","A")
            if exibir_ib and ib_mag > 0: desenhar_vetor(ib_mag, ib_ang, cores_correntes["b"], "Ib","A")
            if exibir_ic and ic_mag > 0: desenhar_vetor(ic_mag, ic_ang, cores_correntes["c"], "Ic","A")

            # 7. Plotagem da Corrente de Curto Simulada (Vetor mais espesso)
            if exibir_isc and isc_mag > 0:
                desenhar_vetor(isc_mag, isc_ang, cor_curto,"Isc","A)", largura=4.0)

            # 8. Limpeza Visual e Ajustes Estéticos Finais
            ax.set_yticklabels([]) 
            ax.set_xticks(np.radians([0, 90, 180, 270]))
            ax.set_xticklabels(["0°", "90°", "180°", "270°"], color="gray", fontsize=9)
            ax.grid(True, alpha=0.3, color="#BDC3C7", ls="--")
        
            # Reposiciona a legenda para baixo do gráfico de forma organizada
            ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.35), ncol=2, fontsize=8)

            # Renderização no Streamlit
            st.pyplot(fig)
            plt.close()

            # 9. Lógica de Diagnóstico Automatizada por Texto
            diff_angular = np.arctan2(np.sin(falha_rad - mta_rad), np.cos(falha_rad - mta_rad))
            if np.abs(diff_angular) <= np.pi / 2:
                st.success(f"✅ **Análise Direcional:** O vetor de curto-circuito (Isc) está posicionado na **Zona Direta (Forward)**.")
            else:
                st.error(f"❌ **Análise Direcional:** O vetor de curto-circuito (Isc) está posicionado na **Zona Reversa (Reverse)**. Função 67 bloqueada.")

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

        # --- LÓGICA PARA FUNÇÃO ANSI 21 (PROTEÇÃO DE DISTÂNCIA / SUBIMPEDÂNCIA) ---
elif funcao == "ANSI 21 (Proteção de Distância)":
    st.sidebar.subheader("📐 Parâmetros de Distância (ANSI 21)")
    
    # Parâmetros de ajuste de alcance da Linha (Zonas de Proteção)
    st.sidebar.markdown("**Ajustes de Zona (Mho)**")
    z1_reach = st.sidebar.number_input("Alcance da Zona 1 (Z1) [Ω]:", min_value=0.1, value=4.0, step=0.5, help="Instantânea (geralmente cobrindo 80% da linha)")
    z2_reach = st.sidebar.number_input("Alcance da Zona 2 (Z2) [Ω]:", min_value=0.1, value=6.0, step=0.5, help="Temporizada (geralmente cobrindo 120% da linha)")
    
    t_z2 = st.sidebar.number_input("Tempo de Atraso da Zona 2 (t_Z2) [s]:", min_value=0.0, value=0.4, step=0.1)
    
    # Inputs de medição em tempo real fornecidos pelos TCs e TPs do sistema
    st.sidebar.markdown("---")
    st.sidebar.markdown("**⚡ Medições em Tempo Real**")
    v_medido = st.sidebar.number_input("Tensão de Fase Medida (V RMS) [V]:", min_value=1.0, value=65.0, step=5.0)
    i_medido = st.sidebar.number_input("Corrente de Fase Medida (I RMS) [A]:", min_value=0.1, value=15.0, step=1.0)
    angulo_graus = st.sidebar.number_input("Ângulo entre V e I (Fase) [°]:", min_value=-180.0, max_value=180.0, value=30.0, step=5.0)

    # --- PROCESSAMENTO MATEMÁTICO DA IMPEDÂNCIA APARENTE ---
    # Conversão do ângulo para radianos para aplicar na decomposição complexa
    angulo_rad = np.radians(angulo_graus)
    
    # Cálculo do módulo da impedância (Z = V / I)
    z_modulo = v_medido / i_medido
    
    # Decomposição cartesiana (R + jX) para plotagem no plano R-X
    r_medido = z_modulo * np.cos(angulo_rad)
    x_medido = z_modulo * np.sin(angulo_rad)

    # --- PROCESSAMENTO LOGICO NA TELA PRINCIPAL (COL1 E COL2) ---
    with col1:
        st.subheader("📊 Resultados da Proteção de Distância (ANSI 21)")
        st.info("Princípio de Medição de Impedância de Linha:")
        st.latex(r"Z_{aparente} = \frac{V_{fase}}{I_{fase}} = R + jX")
        
        # Lógica de Trip por Zona (Característica Mho Circular)
        # Uma impedância está dentro de uma zona Mho se Z_medido <= Z_alcance * cos(theta_medido - theta_linha)
        # Para fins didáticos e visuais diretos no plano complexo, avaliamos o módulo frente ao círculo centrado na origem:
        if z_modulo <= z1_reach:
            status_trip = "🚨 TRIP INSTANTÂNEO (ZONA 1)"
            detalhe_status = "Curto-circuito severo detectado no trecho principal da linha protegido."
            badge_html = f"<div class='trip-alert'><h3>🚨 TRIP INSTANTÂNEO TRIGERADO</h3><p>Falha crítica dentro do alcance da Zona 1. Atuação em: <strong>0.00 s</strong></p></div>"
            cor_borda = "#d9534f"
        elif z_modulo <= z2_reach:
            status_trip = "⏳ TRIP TEMPORIZADO (ZONA 2)"
            detalhe_status = f"Falha na zona de retaguarda. Temporizador ativo aguardando coordenação."
            badge_html = f"<div class='trip-alert' style='background-color: #FF9800;'><h3>⏳ DISPARO TEMPORIZADO ATIVO</h3><p>Falha detectada na Zona 2. Coordenação em: <strong>{t_z2:.2f} s</strong></p></div>"
            cor_borda = "#FF9800"
        else:
            status_trip = "✅ OPERAÇÃO ESTÁVEL"
            detalhe_status = "Impedância vista pelo relé está na zona de carga normal (Região Segura)."
            badge_html = "<div class='badge-status badge-success'>✅ Sistema Seguro: A impedância calculada está fora das zonas de falta.</div>"
            cor_borda = "#4CAF50"

        # Exibição nos cartões estruturados HTML do seu sistema
        st.markdown(f"""
        <div class='card-container'>
            <div class='card-protecao' style='border-left-color: {cor_borda};'>
                <h4>Impedância Calculada</h4>
                <p>{z_modulo:.2f} <span>Ω</span></p>
            </div>
            <div class='card-protecao' style='border-left-color: #00bcd4;'>
                <h4>Ponto Cartesiano</h4>
                <p style='font-size: 1.05rem;'>{r_medido:.2f} + j{x_medido:.2f} <span>Ω</span></p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(badge_html, unsafe_allow_html=True)

    with col2:
        st.subheader("📈 Diagrama de Impedância (Plano R-X)")
        
        plt.figure(figsize=(7, 4.5))
        
        # Desenha as características circulares (Zonas Mho simplificadas centradas na origem para exibição limpa)
        theta_corte = np.linspace(0, 2 * np.pi, 200)
        
        # Zona 1
        r_z1 = z1_reach * np.cos(theta_corte)
        x_z1 = z1_reach * np.sin(theta_corte)
        plt.plot(r_z1, x_z1, color="#d9534f", ls="--", lw=1.5, label=f"Zona 1 ({z1_reach}Ω)")
        plt.fill(r_z1, x_z1, color="#d9534f", alpha=0.08)
        
        # Zona 2
        r_z2 = z2_reach * np.cos(theta_corte)
        x_z2 = z2_reach * np.sin(theta_corte)
        plt.plot(r_z2, x_z2, color="#FF9800", ls="-.", lw=1.5, label=f"Zona 2 ({z2_reach}Ω)")
        plt.fill(r_z2, x_z2, color="#FF9800", alpha=0.04)
        
        # Plota o ponto de operação medido em tempo real
        plt.scatter([r_medido], [x_medido], color="blue", s=120, zorder=5, label=f"Z_aparente Medido")
        # Linha vetorial (fasor) da origem até a impedância medida
        plt.plot([0, r_medido], [0, x_medido], color="blue", lw=2, alpha=0.7)
        
        # Configurações do gráfico cartesiano elétrico R-X
        plt.axhline(0, color="black", lw=1)
        plt.axvline(0, color="black", lw=1)
        plt.xlabel("Resistência - R (Ohms)")
        plt.ylabel("Reatância - X (Ohms)")
        
        # Define limites dinâmicos para manter o ponto medido sempre visível
        limite_grafico = max(z2_reach * 1.5, z_modulo * 1.3)
        plt.xlim(-limite_grafico, limite_grafico)
        plt.ylim(-limite_grafico, limite_grafico)
        
        plt.grid(True, ls="--", alpha=0.5)
        plt.gca().set_aspect('equal', adjustable='box') # Mantém o círculo perfeitamente redondo
        plt.legend(loc="upper left")
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
    
    # Atualizado para incluir o modelo Inepar PM II no seu padrão de selectbox
    fabricante = st.sidebar.selectbox("Modelo/Fabricante do Relé:", ["Schneider Sepam", "Siemens (Siprotec/Reyrolle)", "GE Multilin", "Pextron (Réplica IEC)", "BBC Brown Boveri (Tipo ST)", "Inepar PM II (Proteção de Motores)"])
    
    i_b = st.sidebar.number_input("Corrente de Base / Nominal (I_b) [A]:", min_value=0.1, value=3.0, step=0.5)
    
    # Configuração de constantes default para o modelo Inepar PM II (Constantes de motor costumam ser longas)
    val_tau_padrao = 2400.0 if fabricante == "Inepar PM II (Proteção de Motores)" else 1200.0
    if fabricante == "BBC Brown Boveri (Tipo ST)": val_tau_padrao = 2400.0
        
    tau = st.sidebar.number_input("Constante de Tempo de Aquecimento (τ) [segundos]:", min_value=1.0, value=val_tau_padrao, step=10.0)
    
    val_es_padrao = 100.0 if fabricante in ["BBC Brown Boveri (Tipo ST)", "Inepar PM II (Proteção de Motores)"] else 50.0
    es = st.sidebar.number_input("Capacidade Térmica de Disparo (Es) [%]:", min_value=1.0, max_value=200.0, value=val_es_padrao, step=5.0) / 100.0
    
    e_inicial = st.sidebar.number_input("Estado Térmico Inicial (E_inicial) [%]:", min_value=0.0, max_value=100.0, value=0.0, step=5.0) / 100.0

    # --- CONDICIONAIS DE REGIME DE CADA FABRICANTE ---
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

    elif fabricante == "BBC Brown Boveri (Tipo ST)":
        st.sidebar.markdown("**Abordagem BBC ST:** Modelo clássico baseado na constante térmica bimetálica com correção opcional.")
        i_bbc = st.sidebar.number_input("Corrente RMS Medida de Carga (I) [A]:", min_value=0.1, value=5.0, step=0.5)
        correcao_ferro = st.sidebar.checkbox("Aplicar Correção por Perdas no Ferro (Fig. 15)", value=True)
        if correcao_ferro and e_inicial < 0.20:
            e_inicial = 0.20
            st.sidebar.caption("💡 *E_inicial ajustado automaticamente para 20% devido às perdas no ferro.*")
        razao_corrente = i_bbc / i_b

    elif fabricante == "Inepar PM II (Proteção de Motores)":
        st.sidebar.markdown("**Abordagem Inepar PM II:** Modelo para motores térmicos. Pondera o aquecimento assimétrico severo do rotor via corrente I2.")
        i_fase_max = st.sidebar.number_input("Maior Corrente de Fase (I_fase) [A]:", min_value=0.1, value=6.0, step=0.5)
        i2_deseq = st.sidebar.number_input("Corrente de Sequência Negativa (I2) [A]:", min_value=0.0, value=0.5, step=0.1)
        k_rotor = st.sidebar.number_input("Fator de Ponderação do Rotor (K_rotor):", min_value=1.0, max_value=6.0, value=3.5, step=0.5)
        
        # Equação oficial do estresse térmico composto do rotor Inepar PM II
        i_eq_inepar = np.sqrt(i_fase_max**2 + (k_rotor * (i2_deseq**2)))
        st.sidebar.info(f"I_eq Térmica Calculada (Inepar PM II): {i_eq_inepar:.2f} A")
        razao_corrente = i_eq_inepar / i_b

    else:
        st.sidebar.markdown("**Abordagem Pextron:** Modelo de imagem térmica baseado na norma IEC 60255-149.")
        i_pextron = st.sidebar.number_input("Corrente Equivalente de Fase Medida (I) [A]:", min_value=0.1, value=6.0, step=0.5)
        razao_corrente = i_pextron / i_b

    # --- BLOCO DE RESULTADOS (COL1 E COL2 MANTIDOS INTEGRALMENTE NO SEU PADRÃO) ---
    with col1:
        st.subheader(f"📊 Resultados da ANSI 49 ({fabricante})")
        st.info("Fórmula de Imagem Térmica Utilizada:")
        if fabricante in ["Schneider Sepam", "Pextron (Réplica IEC)", "BBC Brown Boveri (Tipo ST)", "Inepar PM II (Proteção de Motores)"]:
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


# --- SEÇÃO DE CONTATO NO FINAL DA BARRA LATERAL ---
#st.markdown(
   # """
   # <div class="header-contato">
      #  <h4 class="titulo-suporte">Dúvidas ou Suporte</h4>
      #  <p class="subtitulo-info">Entre em contato com o desenvolvedor</p>
      #  <p class="subtitulo-info subtitulo-destaque">Edson Silva</p>
      #  <p class="subtitulo-info">edsn_silva@outlook.com</p>
      #  <p class="subtitulo-info">+55 (19) 98360-1032</p>
   #</div>
   # """, 
  # unsafe_allow_html=True
#)

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style='background-color: #1E1E1E; padding: 15px; border-radius: 8px; border: 1px solid #4F4F4F; text-align: center;'>
    <h4 style='margin: 0; color: #FF5722;'>📬 Dúvidas ou Suporte?</h4>
   <p style='font-size: 0.9rem; color: #CCCCCC; margin: 10px 0 5px 0;'>Entre em contato com o desenvolvedor:</p>
    <p style='font-size: 1rem; font-weight: bold; margin: 0; color: #FFFFFF;'>Edson Silva</p>
    <p style='font-size: 0.85rem; margin: 5px 0 0 0; color: #00bcd4;'>edsn_silva@outlook.com</p>
   <p style='font-size: 0.85rem; margin: 2px 0 0 0; color: #4CAF50;'>+55 (19) 98360-1032</p>
</div>
""", unsafe_allow_html=True)
