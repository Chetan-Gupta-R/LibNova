
import streamlit as st
import pandas as pd
import numpy as np
import sympy as sp
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations, product
from math import comb, factorial

st.set_page_config(page_title="Intelligent Library PBL",
                   page_icon="📚", layout="wide")

st.title("📚 Intelligent Library Management System")
st.caption("Discrete Structures for Computing | Project-Based Learning")

# ---------------- SAMPLE DATA ----------------
if "books" not in st.session_state:
    st.session_state.books = [
        {"id": "B101", "title": "Python Programming",
         "category": "Computer Science", "copies": 3},
        {"id": "B102", "title": "Discrete Mathematics",
         "category": "Mathematics", "copies": 2},
        {"id": "B103", "title": "Machine Learning",
         "category": "Computer Science", "copies": 1},
        {"id": "B104", "title": "Linear Algebra",
         "category": "Mathematics", "copies": 2},
    ]

if "loans" not in st.session_state:
    st.session_state.loans = []

if "reservations" not in st.session_state:
    st.session_state.reservations = []

books = st.session_state.books

tabs = st.tabs([
    "Library Dashboard",
    "1. Logic",
    "2. Counting",
    "3. Relations",
    "4. Recurrence",
    "5. Graph Theory",
    "6. AI Optimization"
])

# ---------------- DASHBOARD ----------------
with tabs[0]:
    st.header("Library Dashboard")

    c1, c2, c3 = st.columns(3)
    c1.metric("Book titles", len(books))
    c2.metric("Available copies", sum(b["copies"] for b in books))
    c3.metric("Active loans", len(st.session_state.loans))

    st.subheader("Book inventory")
    st.dataframe(pd.DataFrame(books), use_container_width=True)

    st.subheader("Issue or return a book")
    with st.form("issue_form"):
        student = st.text_input("Student ID", "S101")
        book_id = st.selectbox("Book", [b["id"] for b in books])
        eligible = st.checkbox("Student is eligible", value=True)
        not_overdue = st.checkbox("No overdue books", value=True)
        action = st.radio("Action", ["Issue", "Return"])
        submitted = st.form_submit_button("Submit")

    if submitted:
        book = next(b for b in books if b["id"] == book_id)
        loan = next(
            (x for x in st.session_state.loans
             if x["student"] == student and x["book"] == book_id),
            None
        )

        if action == "Issue":
            # Logic rule: eligible AND available AND not overdue
            approved = eligible and book["copies"] > 0 and not_overdue
            if approved:
                book["copies"] -= 1
                st.session_state.loans.append(
                    {"student": student, "book": book_id}
                )
                st.success("Issue approved.")
            else:
                st.error(
                    "Issue rejected: check eligibility, availability "
                    "and overdue status."
                )
        else:
            if loan:
                st.session_state.loans.remove(loan)
                book["copies"] += 1
                st.success("Book returned successfully.")
            else:
                st.warning("No matching active loan was found.")

    st.subheader("Reservation")
    with st.form("reserve_form"):
        rs_student = st.text_input("Reservation student ID", "S102")
        rs_book = st.selectbox(
            "Reserve book",
            [b["id"] for b in books],
            key="reserve_book"
        )
        rs_submit = st.form_submit_button("Reserve")
    if rs_submit:
        st.session_state.reservations.append(
            {"student": rs_student, "book": rs_book}
        )
        st.success("Reservation recorded in the demo queue.")

    st.write("Active loans")
    st.dataframe(pd.DataFrame(st.session_state.loans))
    st.write("Reservations")
    st.dataframe(pd.DataFrame(st.session_state.reservations))

# ---------------- UNIT 1: LOGIC ----------------
with tabs[1]:
    st.header("Unit 1 — Logic and Eligibility")
    st.write("Issue rule: E AND A AND N")
    st.write("E = eligible, A = book available, N = no overdue books.")

    truth_rows = []
    for E, A, N in product([False, True], repeat=3):
        truth_rows.append({
            "Eligible (E)": E,
            "Available (A)": A,
            "No overdue (N)": N,
            "Issue approved": E and A and N
        })
    st.dataframe(pd.DataFrame(truth_rows), use_container_width=True)

    st.subheader("Evaluate a decision")
    E = st.checkbox("Eligible", value=True, key="logic_e")
    A = st.checkbox("Book available", value=True, key="logic_a")
    N = st.checkbox("No overdue books", value=True, key="logic_n")
    st.write("**Decision:**",
             "APPROVE" if E and A and N else "REJECT")

    st.latex(r"I = E \\land A \\land N")
    st.write("Inference example: if E, A and N are true, then I is true.")

# ---------------- UNIT 2: COUNTING ----------------
with tabs[2]:
    st.header("Unit 2 — Counting and Combinatorics")
    n = st.number_input("Number of distinct books (n)", 1, 30, 5)
    r = st.number_input("Books selected (r)", 0, int(n), 2)

    st.metric("Ways to select r books",
              f"{comb(int(n), int(r)):,}")
    st.latex(r"\\binom{n}{r}=\\frac{n!}{r!(n-r)!}")

    st.subheader("Ordered selections")
    st.metric("Ways to arrange r distinct books",
              f"{factorial(int(n)) // factorial(int(n-r)):,}")

    st.subheader("Selection demonstration")
    labels = [f"Book {i}" for i in range(1, int(n) + 1)]
    selections = list(combinations(labels, int(r)))
    st.write(f"Number of combinations: {len(selections)}")
    st.write(selections[:20])
    if len(selections) > 20:
        st.caption("Showing the first 20 combinations.")

    st.subheader("Mathematical induction example")
    k = st.number_input("Verify sum formula up to n =", 1, 100, 5,
                        key="induction_n")
    lhs = sum(range(1, int(k) + 1))
    rhs = int(k) * (int(k) + 1) // 2
    st.latex(r"1+2+\\cdots+n=\\frac{n(n+1)}{2}")
    st.write(f"Left side = {lhs}; right side = {rhs}")
    st.success("Formula holds for this n." if lhs == rhs
               else "Check the calculation.")

    st.info(
        "Well Ordering Principle: every non-empty set of positive "
        "integers has a least element. For example, a non-empty set "
        "of reservation positions has a first position."
    )

# ---------------- UNIT 3: RELATIONS ----------------
with tabs[3]:
    st.header("Unit 3 — Relations and Functions")

    student_ids = ["S1", "S2", "S3"]
    book_ids = ["B1", "B2", "B3"]
    relation = [("S1", "B1"), ("S1", "B2"),
                ("S2", "B2"), ("S3", "B3")]

    st.write("Student-book relation:", relation)
    matrix = pd.DataFrame(
        [[int((s, b) in relation) for b in book_ids]
         for s in student_ids],
        index=student_ids, columns=book_ids
    )
    st.write("Zero-one matrix (1 means related):")
    st.dataframe(matrix)

    st.subheader("Relation properties")
    R = st.selectbox("Example relation",
                     ["Equality", "Less than or equal to",
                      "Less than"])
    if R == "Equality":
        st.write("Reflexive, symmetric, antisymmetric and transitive.")
    elif R == "Less than or equal to":
        st.write("Reflexive, antisymmetric and transitive; not symmetric.")
    else:
        st.write("Irreflexive and transitive; not symmetric.")

    st.subheader("Pigeonhole Principle")
    students = st.number_input("Students", 1, 500, 11)
    categories = st.number_input("Categories", 1, 100, 5)
    st.write(
        f"At least one category contains at least "
        f"{(int(students) + int(categories) - 1) // int(categories)} "
        "student(s), if every student belongs to one category."
    )

    st.subheader("Equivalence classes")
    parity = st.selectbox("Group integers by", ["Parity", "Remainder mod 3"])
    values = list(range(12))
    if parity == "Parity":
        classes = {
            "Even": [x for x in values if x % 2 == 0],
            "Odd": [x for x in values if x % 2 == 1]
        }
    else:
        classes = {
            f"Remainder {i}": [x for x in values if x % 3 == i]
            for i in range(3)
        }
    st.write(classes)

    st.subheader("Partial order / Hasse diagram")
    H = nx.DiGraph()
    H.add_edges_from([
        ("Book", "CS Book"),
        ("Book", "Math Book"),
        ("CS Book", "Python"),
        ("CS Book", "ML"),
        ("Math Book", "Discrete Math")
    ])
    pos = {
        "Book": (0, 0),
        "CS Book": (-1, 1), "Math Book": (1, 1),
        "Python": (-1.5, 2), "ML": (-0.5, 2),
        "Discrete Math": (1, 2)
    }
    fig, ax = plt.subplots()
    nx.draw(H, pos, with_labels=True, arrows=False,
            node_size=2400, font_size=8, ax=ax)
    st.pyplot(fig)
    st.caption(
        "Illustrative hierarchy. A formal Hasse diagram omits "
        "self-loops and edges implied by transitivity."
    )

    st.info(
        "Function example: each student ID maps to one student record. "
        "A function is bijective only if it is both one-to-one and onto."
    )

# ---------------- UNIT 4: RECURRENCE ----------------
with tabs[4]:
    st.header("Unit 4 — Recurrence Relations")

    st.subheader("First-order inventory model")
    initial = st.number_input("Initial copies", 0, 1000, 20)
    additions = st.number_input("Copies added per week", 0, 100, 3)
    demand = st.number_input("Copies issued per week", 0, 100, 4)
    weeks = st.slider("Number of weeks", 0, 20, 10)

    stock = [int(initial)]
    for _ in range(int(weeks)):
        stock.append(max(0, stock[-1] + int(additions) - int(demand)))
    st.latex(r"I_{t+1}=\\max(0,I_t+a-d)")
    st.dataframe(pd.DataFrame({
        "Week": range(len(stock)), "Inventory": stock
    }))
    fig, ax = plt.subplots()
    ax.plot(range(len(stock)), stock, marker="o")
    ax.set_xlabel("Week")
    ax.set_ylabel("Available copies")
    ax.grid(True)
    st.pyplot(fig)

    st.subheader("Second-order demand model")
    st.write("Example recurrence: Dₙ = Dₙ₋₁ + Dₙ₋₂")
    d1 = st.number_input("D₀", 0, 10000, 1)
    d2 = st.number_input("D₁", 0, 10000, 1)
    count = st.slider("Terms to generate", 2, 20, 10)
    seq = [int(d1), int(d2)]
    for _ in range(int(count) - 2):
        seq.append(seq[-1] + seq[-2])
    st.write(seq)
    st.latex(r"D_n=D_{n-1}+D_{n-2}")
    st.caption(
        "This is a Fibonacci-type illustrative model, not a validated "
        "real-world demand forecast."
    )

# ---------------- UNIT 5: GRAPH THEORY ----------------
with tabs[5]:
    st.header("Unit 5 — Graph Theory")
    G = nx.Graph()
    G.add_edges_from([
        ("Entrance", "CS Section"),
        ("Entrance", "Math Section"),
        ("CS Section", "Python Shelf"),
        ("CS Section", "ML Shelf"),
        ("Math Section", "Discrete Math Shelf"),
        ("ML Shelf", "Discrete Math Shelf")
    ])

    fig, ax = plt.subplots()
    pos = nx.spring_layout(G, seed=7)
    nx.draw(G, pos, with_labels=True, node_size=2200,
            font_size=8, ax=ax)
    st.pyplot(fig)

    st.write("Degree sequence:", sorted(
        [d for _, d in G.degree()], reverse=True
    ))
    st.write("Connected:", nx.is_connected(G))
    st.write("Articulation points:", list(nx.articulation_points(G)))
    st.write("Bridges:", list(nx.bridges(G)))

    source = st.selectbox("Path start", list(G.nodes), key="path_start")
    target = st.selectbox("Path end", list(G.nodes), index=3,
                          key="path_end")
    try:
        path = nx.shortest_path(G, source, target)
        st.write("Shortest path:", " → ".join(path))
        st.write("Distance:", len(path) - 1, "edges")
    except nx.NetworkXNoPath:
        st.warning("No path exists.")

    st.subheader("Directed borrowing graph")
    DG = nx.DiGraph()
    DG.add_edges_from([
        ("S1", "B1"), ("S2", "B1"), ("S2", "B2")
    ])
    st.write("Directed edges:", list(DG.edges))

    st.subheader("Prefix code example")
    codes = {
        "Python": "00", "Math": "01",
        "AI": "10", "Logic": "11"
    }
    st.dataframe(pd.DataFrame(
        [{"Category": k, "Code": v} for k, v in codes.items()]
    ))
    st.caption(
        "These equal-length codes are prefix-free: no code is a prefix "
        "of another. They are an illustrative encoding."
    )

# ---------------- UNIT 6: AI & OPTIMIZATION ----------------
with tabs[6]:
    st.header("Unit 6 — Mathematics for AI and Optimization")
    st.write(
        "Example loss function: L(x,y) = (x - 3)² + 2(y - 2)²"
    )
    x = sp.symbols("x")
    y = sp.symbols("y")
    loss = (x - 3)**2 + 2*(y - 2)**2
    grad = [sp.diff(loss, x), sp.diff(loss, y)]
    hessian = sp.hessian(loss, (x, y))

    st.write("Loss:", loss)
    st.write("Gradient:", grad)
    st.write("Hessian:")
    st.latex(sp.latex(hessian))
    st.write("Hessian eigenvalues:", list(hessian.eigenvals().keys()))
    st.info(
        "The Hessian is positive definite, so this quadratic loss "
        "is strictly convex and has a unique minimum at (3, 2)."
    )

    st.subheader("Gradient descent")
    start_x = st.number_input("Starting x", -20.0, 20.0, 10.0)
    start_y = st.number_input("Starting y", -20.0, 20.0, -5.0)
    lr = st.select_slider(
        "Learning rate",
        options=[0.01, 0.05, 0.1, 0.2, 0.4],
        value=0.1
    )
    steps = st.slider("Iterations", 1, 200, 50)

    xx, yy = float(start_x), float(start_y)
    history = []
    for i in range(int(steps)):
        L = (xx - 3)**2 + 2*(yy - 2)**2
        history.append({"Step": i, "x": xx, "y": yy, "Loss": L})
        gx, gy = 2*(xx - 3), 4*(yy - 2)
        xx -= lr * gx
        yy -= lr * gy

    st.write(f"Final x = {xx:.4f}, y = {yy:.4f}")
    st.write(f"Final loss = {(xx-3)**2 + 2*(yy-2)**2:.6f}")
    st.line_chart(pd.DataFrame(history).set_index("Step")["Loss"])

    st.subheader("Constrained allocation — Lagrange multipliers")
    st.write("Maximize xy subject to x + y = 10, where x, y ≥ 0.")
    st.latex(r"\\mathcal{L}(x,y,\\lambda)=xy-\\lambda(x+y-10)")
    st.write(
        "Stationary equations give y = λ, x = λ and x + y = 10. "
        "Therefore x = 5, y = 5, and the maximum product is 25."
    )
    st.caption(
        "Interpret x and y as two resource allocations. The numerical "
        "example is a mathematical demonstration, not a trained AI model."
    )

st.divider()
st.caption(
    "Academic prototype with sample data. Restarting the app resets "
    "demo data. Use fictional student records for demonstrations."
)
