import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(page_title="Моделювання DoS-атаки", layout="wide")

st.title("Моделювання DoS-атаки на вузли мережі")
st.write("Програма моделює перевантаження вузлів мережі та аналізує наслідки DoS-атаки.")

uploaded_file = st.file_uploader("Завантажте CSV-файл із ребрами мережі", type=["csv"])

attack_power = st.slider("Інтенсивність атакуючого трафіку", 10, 1000, 300)
node_capacity = st.slider("Гранична пропускна здатність вузла", 50, 1000, 250)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    if df.shape[1] < 2:
        st.error("CSV-файл повинен містити мінімум два стовпці: початковий та кінцевий вузол.")
    else:
        df = df.iloc[:, :2]
        df.columns = ["source", "target"]

        G = nx.Graph()
        for _, row in df.iterrows():
            G.add_edge(str(row["source"]), str(row["target"]))

        nodes = list(G.nodes())

        st.subheader("Вхідні дані")
        st.dataframe(df)

        attacked_node = st.selectbox("Оберіть вузол для DoS-атаки", nodes)

        loads = {}
        statuses = {}

        for node in nodes:
            normal_load = G.degree[node] * 30
            if node == attacked_node:
                total_load = normal_load + attack_power
            else:
                total_load = normal_load

            loads[node] = total_load
            statuses[node] = "Перевантажений" if total_load > node_capacity else "Нормальний"

        result_df = pd.DataFrame({
            "Вузол": list(loads.keys()),
            "Навантаження": list(loads.values()),
            "Стан": list(statuses.values())
        })

        st.subheader("Результати моделювання")
        st.dataframe(result_df)

        overloaded = result_df[result_df["Стан"] == "Перевантажений"]

        st.write(f"Кількість вузлів у мережі: {G.number_of_nodes()}")
        st.write(f"Кількість з’єднань у мережі: {G.number_of_edges()}")
        st.write(f"Кількість перевантажених вузлів: {len(overloaded)}")

        availability = round((1 - len(overloaded) / len(nodes)) * 100, 2)
        st.write(f"Орієнтовна доступність мережі: {availability}%")

        st.subheader("Графічне подання мережі")

        pos = nx.spring_layout(G, seed=42)
        colors = ["red" if statuses[node] == "Перевантажений" else "lightgreen" for node in G.nodes()]

        fig, ax = plt.subplots(figsize=(9, 6))
        nx.draw(
            G,
            pos,
            with_labels=True,
            node_color=colors,
            node_size=1200,
            edge_color="gray",
            font_size=10,
            ax=ax
        )
        st.pyplot(fig)

        st.subheader("Аналітичний висновок")

        if len(overloaded) == 0:
            st.success("Мережа працює стабільно, перевантажених вузлів не виявлено.")
        else:
            st.warning(
                "Під час моделювання DoS-атаки виявлено перевантажені вузли. "
                "Це свідчить про зниження доступності мережі та можливу відмову "
                "в обслуговуванні для частини користувачів."
            )

else:
    st.info("Завантажте CSV-файл, щоб розпочати моделювання.")