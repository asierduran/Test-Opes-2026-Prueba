import pandas as pd
import streamlit as st

st.set_page_config(page_title="Test Fisio", layout="centered")

@st.cache_data
def cargar_preguntas():
    df = pd.read_excel("Banco de preguntas.xlsx")
    df.columns = df.columns.str.strip()

    df = df.rename(columns={
        "Opción 1": "A",
        "Opción 2": "B",
        "Opción 3": "C",
        "Opción 4": "D",
        "Respuesta": "Correcta",
        "Apreciacion": "Apreciación"
    })

    df["Correcta"] = df["Correcta"].astype(str).str.strip().str.upper()
    return df

df = cargar_preguntas()

st.title("🧠 Test Fisio")

if "preguntas" not in st.session_state:
    st.session_state.preguntas = []
    st.session_state.indice = 0
    st.session_state.aciertos = 0
    st.session_state.fallos = []
    st.session_state.respondida = False

bloques = ["Todos"] + list(df["Bloque"].dropna().unique())

modo = st.selectbox(
    "Modo de test",
    ["Por bloque / aleatorio", "Preguntas por rango de ID"]
)

bloque = st.selectbox("Selecciona bloque", bloques)

cantidad = st.number_input(
    "Número de preguntas",
    min_value=1,
    max_value=len(df),
    value=10
)

col1, col2 = st.columns(2)

with col1:
    id_inicio = st.number_input("ID inicial", min_value=1, value=1)

with col2:
    id_fin = st.number_input("ID final", min_value=1, value=10)

if st.button("Iniciar test"):
    df_filtrado = df.copy()

    if modo == "Preguntas por rango de ID":
        df_filtrado = df_filtrado[
            (df_filtrado["ID"] >= id_inicio) &
            (df_filtrado["ID"] <= id_fin)
        ]

        df_filtrado = df_filtrado.sort_values("ID")

        st.session_state.preguntas = df_filtrado.to_dict("records")

    else:
        if bloque != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Bloque"] == bloque]

        cantidad_real = min(cantidad, len(df_filtrado))

        st.session_state.preguntas = df_filtrado.sample(n=cantidad_real).to_dict("records")    st.session_state.indice = 0
    st.session_state.aciertos = 0
    st.session_state.fallos = []
    st.session_state.respondida = False

if st.session_state.preguntas:
    if st.session_state.indice < len(st.session_state.preguntas):
        p = st.session_state.preguntas[st.session_state.indice]

        st.subheader(f"Pregunta {st.session_state.indice + 1} de {len(st.session_state.preguntas)}")
        st.caption(f"ID: {p['ID']}")

        st.write(p["Pregunta"])

        opciones = {
            "A": p["A"],
            "B": p["B"],
            "C": p["C"],
            "D": p["D"]
        }

        respuesta = st.radio(
            "Elige una respuesta:",
            ["A", "B", "C", "D"],
            format_func=lambda x: f"{x}) {opciones[x]}",
            key=f"respuesta_{st.session_state.indice}"
        )

        if st.button("Responder", disabled=st.session_state.respondida):
            st.session_state.respondida = True

            if respuesta == p["Correcta"]:
                st.session_state.aciertos += 1
                st.success("✅ Correcto")
            else:
                st.session_state.fallos.append(p["ID"])
                st.error(f"❌ Incorrecto. Correcta: {p['Correcta']}")

            if "Apreciación" in p and pd.notna(p["Apreciación"]) and str(p["Apreciación"]).strip() != "":
                st.info(f"📝 Apreciación: {p['Apreciación']}")

        if st.session_state.respondida:
            if st.button("Siguiente pregunta"):
                st.session_state.indice += 1
                st.session_state.respondida = False
                st.rerun()

    else:
        st.success("Test terminado")
        st.write(f"✅ Aciertos: {st.session_state.aciertos} / {len(st.session_state.preguntas)}")
        st.write(f"❌ Fallos: {len(st.session_state.fallos)}")

        if st.session_state.fallos:
            fallos_df = pd.DataFrame(st.session_state.fallos, columns=["ID"])
            st.download_button(
                "Descargar fallos",
                fallos_df.to_csv(index=False).encode("utf-8"),
                "fallos.csv",
                "text/csv"
            )
