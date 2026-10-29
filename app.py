
import streamlit as st
import pandas as pd

import database
import services
from services import ServiceError

import matplotlib.pyplot as plt
import networkx as nx

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="LibNova | Library Operations",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

database.initialize_database()

# --------------------------------------------------
# PROFESSIONAL STYLING
# --------------------------------------------------

st.markdown(
    """
    
    <style>
        
    /* ==========================================
    LIBNOVA — MIDNIGHT GLASS DESIGN SYSTEM
    Electric Violet | Balanced Layout
    ========================================== */

    :root {
        --ln-bg: #0b1020;
        --ln-bg-deep: #080c18;
        --ln-glass: rgba(255, 255, 255, 0.065);
        --ln-glass-strong: rgba(255, 255, 255, 0.095);
        --ln-border: rgba(255, 255, 255, 0.13);
        --ln-ink: #f3f4ff;
        --ln-heading: #ffffff;
        --ln-muted: #b4bdd2;
        --ln-violet: #a78bfa;
        --ln-violet-bright: #8b5cf6;
        --ln-violet-dark: #6d28d9;
        --ln-success: #6ee7b7;
        --ln-danger: #fda4af;
        --ln-radius: 18px;
        --ln-shadow: 0 12px 36px rgba(0, 0, 0, 0.20);
    }

    /* Main application background */
    .stApp {
        color: var(--ln-ink);
        background:
            radial-gradient(
                ellipse at 12% 5%,
                rgba(109, 40, 217, 0.24),
                transparent 38%
            ),
            radial-gradient(
                ellipse at 90% 30%,
                rgba(79, 70, 229, 0.16),
                transparent 34%
            ),
            linear-gradient(
                135deg,
                var(--ln-bg-deep) 0%,
                var(--ln-bg) 55%,
                #11152b 100%
            );
    }

    /* Main content spacing */
    .main .block-container {
        max-width: 1440px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Main text and headings */
    .stApp,
    .stApp p,
    .stApp li,
    .stApp label,
    .stApp span,
    .stApp small {
        color: var(--ln-ink);
    }

    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4 {
        color: var(--ln-heading) !important;
        letter-spacing: -0.025em;
        font-weight: 700;
    }

    .stApp h1 {
        line-height: 1.2;
    }

    .stCaption,
    [data-testid="stCaptionContainer"] {
        color: var(--ln-muted) !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background:
            radial-gradient(
                ellipse at top left,
                rgba(124, 58, 237, 0.20),
                transparent 55%
            ),
            linear-gradient(
                180deg,
                rgba(14, 18, 38, 0.98),
                rgba(8, 12, 25, 0.98)
            );
        border-right: 1px solid var(--ln-border);
    }

    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #dce2f3;
    }

    [data-testid="stSidebar"] hr {
        border-color: var(--ln-border);
    }

    /* Glass containers, cards and bordered sections */
    [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stExpander"],
    [data-testid="stForm"],
    div[data-testid="stMetric"] {
        background: var(--ln-glass);
        border: 1px solid var(--ln-border);
        border-radius: var(--ln-radius);
        box-shadow: var(--ln-shadow);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
    }

    /* Keep bordered containers from becoming too opaque */
    [data-testid="stVerticalBlockBorderWrapper"] {
        overflow: hidden;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        padding: 20px 20px 16px;
        transition:
            transform 180ms ease,
            border-color 180ms ease,
            background 180ms ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        border-color: rgba(167, 139, 250, 0.48);
        background: var(--ln-glass-strong);
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p {
        color: var(--ln-muted) !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }

    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] div {
        color: var(--ln-heading) !important;
        font-weight: 750 !important;
        letter-spacing: -0.04em;
    }

    [data-testid="stMetricDelta"] {
        font-weight: 600;
    }

    /* Forms */
    [data-testid="stForm"] {
        padding: 1.15rem;
    }

    .stApp [data-testid="stWidgetLabel"] p,
    .stApp [data-testid="stWidgetLabel"] label,
    .stApp .stRadio label,
    .stApp .stCheckbox label {
        color: #e6e9f5 !important;
        font-weight: 500;
    }

    /* Text inputs, number inputs and date inputs */
    .stApp input,
    .stApp textarea,
    .stApp [data-baseweb="input"] input,
    .stApp [data-baseweb="textarea"] textarea {
        color: #ffffff !important;
        background-color: rgba(8, 12, 27, 0.70) !important;
        border-color: rgba(255, 255, 255, 0.17) !important;
        border-radius: 11px !important;
        caret-color: var(--ln-violet);
    }

    .stApp input::placeholder,
    .stApp textarea::placeholder {
        color: #929db6 !important;
        opacity: 1;
    }

    .stApp [data-baseweb="input"]:focus-within,
    .stApp [data-baseweb="textarea"]:focus-within {
        border-color: var(--ln-violet) !important;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.20);
    }

    /* Select boxes and dropdowns */
    .stApp [data-baseweb="select"] > div {
        color: #ffffff !important;
        background-color: rgba(15, 20, 40, 0.88);
        border-color: rgba(255, 255, 255, 0.17);
        border-radius: 11px;
    }

    .stApp [data-baseweb="select"] span {
        color: #ffffff !important;
    }

    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [data-baseweb="listbox"] {
        background-color: #171b32 !important;
        border: 1px solid var(--ln-border) !important;
        border-radius: 12px !important;
    }

    [data-baseweb="menu"] li,
    [data-baseweb="listbox"] li,
    [data-baseweb="option"] {
        color: #f3f4ff !important;
    }

    [data-baseweb="option"]:hover {
        background-color: rgba(139, 92, 246, 0.25) !important;
    }

    /* Buttons */
    .stApp .stButton > button,
    .stApp .stFormSubmitButton > button,
    .stApp button[kind="primary"] {
        color: #ffffff !important;
        background: linear-gradient(
            135deg,
            #8b5cf6 0%,
            #6d28d9 100%
        ) !important;
        border: 1px solid rgba(196, 181, 253, 0.42) !important;
        border-radius: 11px !important;
        font-weight: 650 !important;
        min-height: 2.55rem;
        box-shadow: 0 5px 18px rgba(109, 40, 217, 0.23);
        transition:
            transform 160ms ease,
            box-shadow 160ms ease,
            filter 160ms ease;
    }

    .stApp .stButton > button:hover,
    .stApp .stFormSubmitButton > button:hover {
        color: #ffffff !important;
        filter: brightness(1.12);
        transform: translateY(-1px);
        box-shadow: 0 8px 24px rgba(139, 92, 246, 0.34);
        border-color: rgba(221, 214, 254, 0.65) !important;
    }

    .stApp .stButton > button:focus-visible,
    .stApp .stFormSubmitButton > button:focus-visible {
        outline: 2px solid #c4b5fd;
        outline-offset: 3px;
    }

    /* Tabs */
    .stApp [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.035);
        border: 1px solid var(--ln-border);
        border-radius: 14px;
        padding: 6px;
    }

    .stApp [data-baseweb="tab"] {
        color: var(--ln-muted) !important;
        border-radius: 9px;
        padding: 8px 15px;
    }

    .stApp [data-baseweb="tab"][aria-selected="true"] {
        color: #ffffff !important;
        background: rgba(139, 92, 246, 0.25);
    }

    .stApp [data-baseweb="tab-highlight"] {
        background-color: var(--ln-violet) !important;
    }

    .stApp [data-baseweb="tab-border"] {
        background-color: transparent !important;
    }

    /* Dataframes and tables */
    .stApp [data-testid="stDataFrame"],
    .stApp [data-testid="stTable"] {
        border: 1px solid var(--ln-border);
        border-radius: 14px;
        overflow: hidden;
        background: rgba(255, 255, 255, 0.035);
    }

    .stApp [data-testid="stDataFrame"] * {
        scrollbar-color: #6d5a9c transparent;
    }

    /* Expanders */
    .stApp [data-testid="stExpander"] {
        overflow: hidden;
    }

    .stApp [data-testid="stExpander"] summary {
        color: #f3f4ff !important;
        font-weight: 600;
    }

    .stApp [data-testid="stExpander"] summary:hover {
        color: var(--ln-violet) !important;
    }

    /* Alerts and status messages */
    .stApp [data-testid="stAlert"] {
        background: rgba(255, 255, 255, 0.055);
        border: 1px solid var(--ln-border);
        border-radius: 13px;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
    }

    .stApp [data-testid="stAlert"] p {
        color: var(--ln-ink) !important;
    }

    /* Progress indicators */
    .stApp [data-testid="stProgress"] > div {
        background: rgba(255, 255, 255, 0.10);
        border-radius: 20px;
        overflow: hidden;
    }

    .stApp [data-testid="stProgress"] > div > div {
        background: linear-gradient(
            90deg,
            #7c3aed,
            #c4b5fd
        );
        border-radius: 20px;
    }

    /* Dividers and links */
    .stApp hr {
        border-color: rgba(255, 255, 255, 0.11);
    }

    .stApp a {
        color: #c4b5fd;
        text-decoration-color: rgba(196, 181, 253, 0.45);
    }

    .stApp a:hover {
        color: #ddd6fe;
    }

    /* Scrollbars */
    ::-webkit-scrollbar {
        width: 9px;
        height: 9px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.025);
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(167, 139, 250, 0.40);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(167, 139, 250, 0.70);
    }

    /* Reduce animation for accessibility */
    @media (prefers-reduced-motion: reduce) {
        *,
        *::before,
        *::after {
            transition-duration: 0.01ms !important;
            animation-duration: 0.01ms !important;
            scroll-behavior: auto !important;
        }
    }

    /* Smaller screens */
    @media (max-width: 768px) {
        .main .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        div[data-testid="stMetric"] {
            padding: 14px;
        }
    }

    /* Fallback: retain translucent cards without blur
    on browsers that do not support backdrop-filter. */
    @supports not (backdrop-filter: blur(18px)) {
        [data-testid="stVerticalBlockBorderWrapper"],
        [data-testid="stExpander"],
        [data-testid="stForm"],
        div[data-testid="stMetric"] {
            background: rgba(24, 27, 52, 0.96);
        }
    }

    
    /* ===== LibNova: Glass refinement layer ===== */

    /* A richer, more atmospheric midnight background */
    .stApp {
        background:
            radial-gradient(
                circle at 18% 8%,
                rgba(124, 58, 237, 0.19),
                transparent 34%
            ),
            radial-gradient(
                circle at 85% 45%,
                rgba(91, 33, 182, 0.12),
                transparent 38%
            ),
            linear-gradient(
                145deg,
                #080b18 0%,
                #101329 52%,
                #090e1d 100%
            );
        background-attachment: fixed;
    }

    /* More transparent frosted panels */
    [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stExpander"],
    [data-testid="stForm"] {
        background: rgba(22, 25, 48, 0.48) !important;
        border: 1px solid rgba(196, 181, 253, 0.15) !important;
        border-radius: 20px !important;
        box-shadow:
            0 12px 36px rgba(0, 0, 0, 0.16),
            inset 0 1px 0 rgba(255, 255, 255, 0.045) !important;
        backdrop-filter: blur(24px) saturate(135%);
        -webkit-backdrop-filter: blur(24px) saturate(135%);
    }

    /* Metric cards with a subtle violet glass edge */
    div[data-testid="stMetric"] {
        background:
            linear-gradient(
                135deg,
                rgba(139, 92, 246, 0.10),
                rgba(255, 255, 255, 0.035) 65%
            ) !important;
        border: 1px solid rgba(196, 181, 253, 0.19) !important;
        border-radius: 19px !important;
        box-shadow:
            0 10px 30px rgba(0, 0, 0, 0.14),
            inset 0 1px 0 rgba(255, 255, 255, 0.055) !important;
        backdrop-filter: blur(22px) saturate(140%);
        -webkit-backdrop-filter: blur(22px) saturate(140%);
    }

    div[data-testid="stMetric"]:hover {
        background:
            linear-gradient(
                135deg,
                rgba(139, 92, 246, 0.17),
                rgba(255, 255, 255, 0.045)
            ) !important;
        border-color: rgba(196, 181, 253, 0.38) !important;
        box-shadow:
            0 14px 36px rgba(76, 29, 149, 0.16),
            inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
    }

    /* Slightly more breathing room in the dashboard */
    .main .block-container {
        padding-top: 2.4rem;
        padding-bottom: 3rem;
    }

    /* Elegant section headings */
    .stApp h2,
    .stApp h3 {
        letter-spacing: -0.035em;
        text-shadow: 0 2px 18px rgba(139, 92, 246, 0.08);
    }

    /* Integrate the data table with the dark glass theme */
    .stApp [data-testid="stDataFrame"],
    .stApp [data-testid="stTable"] {
        border: 1px solid rgba(196, 181, 253, 0.14) !important;
        border-radius: 15px !important;
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.12);
    }

    /* Subtler sidebar divider */
    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(196, 181, 253, 0.12);
        box-shadow: 8px 0 32px rgba(0, 0, 0, 0.08);
    }

    /* More restrained interactive glow */
    .stApp .stButton > button:hover,
    .stApp .stFormSubmitButton > button:hover {
        box-shadow:
            0 0 0 1px rgba(196, 181, 253, 0.16),
            0 8px 24px rgba(109, 40, 217, 0.25) !important;
    }

    /* Preserve readable panels on browsers without blur */
    @supports not (backdrop-filter: blur(24px)) {
        [data-testid="stVerticalBlockBorderWrapper"],
        [data-testid="stExpander"],
        [data-testid="stForm"],
        div[data-testid="stMetric"] {
            background: rgba(24, 27, 52, 0.96) !important;
        }
    }


/* ===== LibNova chart styling refinement ===== */

/* Blend chart containers into the midnight glass theme */
.stApp [data-testid="stVegaLiteChart"],
.stApp [data-testid="stArrowVegaLiteChart"],
.stApp [data-testid="stVegaLiteChart"] > div {
    background: rgba(19, 22, 43, 0.52) !important;
    border: 1px solid rgba(196, 181, 253, 0.14);
    border-radius: 16px;
    overflow: hidden;
}

/* Give chart panels consistent spacing */
.stApp [data-testid="stVegaLiteChart"] {
    padding: 8px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
}

/* Keep chart captions readable */
.stApp [data-testid="stCaptionContainer"] p {
    color: #b4bdd2 !important;
}


    </style>

    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# DATA HELPERS
# --------------------------------------------------

def load_dashboard_data():
    books = services.list_books()

    with services.read_connection() as conn:
        members = conn.execute(
            "SELECT * FROM members ORDER BY full_name"
        ).fetchall()

        loans = conn.execute(
            """
            SELECT l.*, b.title, m.full_name, m.member_code
            FROM loans l
            JOIN books b ON b.id = l.book_id
            JOIN members m ON m.id = l.member_id
            ORDER BY l.id DESC
            """
        ).fetchall()

        reservations = conn.execute(
            """
            SELECT * FROM reservations
            WHERE status = 'WAITING'
            """
        ).fetchall()

    return books, members, loans, reservations


def show_error(error):
    st.error(str(error))


def show_success(result):
    st.success(result["message"])


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

with st.sidebar:
    st.markdown("# 📚 LibNova")
    st.caption("INTELLIGENT LIBRARY PLATFORM")
    st.divider()

    page = st.radio(
    "WORKSPACE",
    [
        "Overview",
        "Mathematical Model",
        "Book Catalog",
        "Members",
        "Circulation",
        "Reservations",
        "Activity Log",
    ],
    )

    st.divider()
    st.caption("LIBRARY OPERATIONS")
    st.caption("Discrete Structures · AI Optimization")

# Load current data for the dashboard and tables.
books, members, loans, reservations = load_dashboard_data()

active_loans = [loan for loan in loans if loan["returned_at"] is None]
today = pd.Timestamp.today().date()

overdue_loans = [
    loan for loan in active_loans
    if pd.Timestamp(loan["due_at"]).date() < today
]

total_titles = len(books)
total_copies = sum(book["total_copies"] for book in books)
available_copies = sum(book["available_copies"] for book in books)

# --------------------------------------------------
# OVERVIEW — INTELLIGENT ANALYTICS DASHBOARD
# --------------------------------------------------

if page == "Overview":
    st.markdown(
        """
        <div class="hero">
            <h1>LibNova Analytics</h1>
            <p>
                Data-driven insights into collection health,
                borrowing patterns and library operations.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Prepare data from the existing SQLite records.
    books_df = pd.DataFrame([dict(book) for book in books])
    loans_df = pd.DataFrame([dict(loan) for loan in loans])

    # Ensure expected columns exist even when the database is empty.
    for column in [
        "title", "author", "category",
        "total_copies", "available_copies"
    ]:
        if column not in books_df.columns:
            books_df[column] = pd.Series(dtype="object")

    for column in [
        "title", "full_name", "issued_at",
        "due_at", "returned_at"
    ]:
        if column not in loans_df.columns:
            loans_df[column] = pd.Series(dtype="object")

    # Parse dates safely.
    loans_df["issued_at"] = pd.to_datetime(
        loans_df["issued_at"], errors="coerce"
    )
    loans_df["due_at"] = pd.to_datetime(
        loans_df["due_at"], errors="coerce"
    )

    today = pd.Timestamp.today().normalize()

    # Calculate current operational metrics.
    active_df = loans_df[loans_df["returned_at"].isna()].copy()

    overdue_df = active_df[
        active_df["due_at"].notna()
        & (active_df["due_at"] < today)
    ].copy()

    total_titles = len(books_df)
    total_copies = int(
        pd.to_numeric(
            books_df["total_copies"], errors="coerce"
        ).fillna(0).sum()
    )
    available_copies = int(
        pd.to_numeric(
            books_df["available_copies"], errors="coerce"
        ).fillna(0).sum()
    )

    # ------------------------------
    # KPI CARDS
    # ------------------------------

    st.subheader("Library at a glance")

    k1, k2, k3, k4 = st.columns(4)

    k1.metric("Book Titles", total_titles)
    k2.metric("Total Copies", total_copies)
    k3.metric("Active Loans", len(active_df))
    k4.metric("Overdue Loans", len(overdue_df))

    st.write("")

    # ------------------------------
    # INVENTORY HEALTH
    # ------------------------------

    inventory_col, utilization_col = st.columns([1.15, 1])

    with inventory_col:
        st.subheader("Inventory health")

        st.metric("Available Copies", available_copies)
        st.metric("Registered Members", len(members))
        st.metric("Waiting Reservations", len(reservations))

    with utilization_col:
        st.subheader("Collection utilization")

        if total_copies > 0:
            borrowed_copies = max(
                0, total_copies - available_copies
            )
            utilization = (
                borrowed_copies / total_copies
            ) * 100

            st.progress(
                min(100, max(0, int(utilization)))
            )

            st.markdown(
                f"### {utilization:.1f}%"
            )
            st.caption(
                f"{borrowed_copies} of {total_copies} copies "
                "are currently unavailable."
            )
        else:
            st.info("Add books to calculate collection utilization.")

        st.markdown("---")

        if len(overdue_df) > 0:
            st.warning(
                f"{len(overdue_df)} active loan(s) are overdue."
            )
        else:
            st.success("No overdue loans detected.")

    st.divider()

    # ------------------------------
    # BORROWING TREND — LAST 6 MONTHS
    # ------------------------------

    st.subheader("Borrowing trends")
    st.caption(
        "Number of recorded book issues by month. "
        "This measures circulation activity, not unique readers."
    )

    current_month = today.to_period("M")

    last_six_months = pd.period_range(
        end=current_month,
        periods=6,
        freq="M",
    )

    monthly_counts = pd.Series(
        0,
        index=last_six_months.astype(str),
        dtype="int64",
    )

    valid_issue_dates = loans_df[
        loans_df["issued_at"].notna()
    ].copy()

    if not valid_issue_dates.empty:
        valid_issue_dates["Month"] = (
            valid_issue_dates["issued_at"]
            .dt.to_period("M")
            .astype(str)
        )

        observed_counts = (
            valid_issue_dates["Month"]
            .value_counts()
        )

        for month in monthly_counts.index:
            monthly_counts.loc[month] = int(
                observed_counts.get(month, 0)
            )

    trend_df = monthly_counts.rename(
        "Books Issued"
    ).rename_axis("Month").reset_index()

    st.line_chart(
        trend_df.set_index("Month"),
        use_container_width=True,
    )

    st.divider()

    # ------------------------------
    # POPULAR BOOKS AND CATEGORIES
    # ------------------------------

    popular_col, category_col = st.columns(2)

    with popular_col:
        st.subheader("Most borrowed books")
        st.caption("Ranked by recorded loan transactions.")

        if not loans_df.empty and loans_df["title"].notna().any():
            popular_books = (
                loans_df["title"]
                .dropna()
                .value_counts()
                .head(7)
                .rename_axis("Book")
                .reset_index(name="Borrow Count")
            )

            st.bar_chart(
                popular_books.set_index("Book"),
                use_container_width=True,
            )

            st.dataframe(
                popular_books,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info(
                "Borrowing rankings will appear after books are issued."
            )

    with category_col:
        st.subheader("Collection by category")
        st.caption("Total physical copies grouped by category.")

        if not books_df.empty:
            category_data = books_df[
                ["category", "total_copies"]
            ].copy()

            category_data["total_copies"] = pd.to_numeric(
                category_data["total_copies"],
                errors="coerce",
            ).fillna(0)

            category_data["category"] = (
                category_data["category"]
                .fillna("Uncategorized")
                .replace("", "Uncategorized")
            )

            category_summary = (
                category_data
                .groupby("category")["total_copies"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
                .rename_axis("Category")
                .reset_index(name="Copies")
            )

            st.bar_chart(
                category_summary.set_index("Category"),
                use_container_width=True,
            )

            st.dataframe(
                category_summary,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info(
                "Category analysis will appear after books are added."
            )

    st.divider()

    # ------------------------------
    # RECENT CIRCULATION
    # ------------------------------

    st.subheader("Recent circulation")

    if not loans_df.empty:
        recent_df = loans_df.head(8).copy()

        recent_df["Status"] = recent_df.apply(
            lambda loan: (
                "Returned"
                if pd.notna(loan["returned_at"])
                else (
                    "Overdue"
                    if pd.notna(loan["due_at"])
                    and loan["due_at"] < today
                    else "Active"
                )
            ),
            axis=1,
        )

        display_columns = [
            column for column in [
                "id", "title", "full_name",
                "issued_at", "due_at", "Status"
            ]
            if column in recent_df.columns
        ]

        recent_df = recent_df[display_columns].rename(
            columns={
                "id": "Loan ID",
                "title": "Book",
                "full_name": "Member",
                "issued_at": "Issue Date",
                "due_at": "Due Date",
            }
        )

        st.dataframe(
            recent_df,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info(
            "No circulation records yet. Issue a book to start "
            "building your analytics."
        )

    # ------------------------------
    # OVERDUE MONITOR
    # ------------------------------

    if not overdue_df.empty:
        with st.expander("View overdue loan details"):
            overdue_columns = [
                column for column in [
                    "id", "title", "full_name", "due_at"
                ]
                if column in overdue_df.columns
            ]

            overdue_table = overdue_df[
                overdue_columns
            ].rename(
                columns={
                    "id": "Loan ID",
                    "title": "Book",
                    "full_name": "Member",
                    "due_at": "Due Date",
                }
            )

            st.dataframe(
                overdue_table,
                use_container_width=True,
                hide_index=True,
            )



# --------------------------------------------------
# MATHEMATICAL MODEL — DISCRETE STRUCTURES ENGINE
# --------------------------------------------------

elif page == "Mathematical Model":
    st.title("Discrete Mathematics Engine")
    st.caption(
        "Explore set theory, relations, graph theory, "
        "and Boolean decision logic using library records."
    )

    # Convert existing database records into mathematical sets.
    book_ids = {book["id"] for book in books}
    member_ids = {member["id"] for member in members}

    active_loans = [
        loan for loan in loans
        if loan["returned_at"] is None
    ]

    today = pd.Timestamp.today().date()

    overdue_loans = [
        loan for loan in active_loans
        if pd.Timestamp(loan["due_at"]).date() < today
    ]

    # Relation: member ID is connected to book ID.
    borrowing_relation = {
        (loan["member_id"], loan["book_id"])
        for loan in loans
    }

    active_relation = {
        (loan["member_id"], loan["book_id"])
        for loan in active_loans
    }

    overdue_relation = {
        (loan["member_id"], loan["book_id"])
        for loan in overdue_loans
    }

    # ------------------------------
    # SET THEORY
    # ------------------------------

    st.subheader("1. Set Theory")
    st.markdown(
        "Represent the library as sets of books, members, "
        "and borrowing records."
    )

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("|B| — Book titles", len(book_ids))
    s2.metric("|M| — Members", len(member_ids))
    s3.metric("|A| — Active loans", len(active_relation))
    s4.metric("|O| — Overdue loans", len(overdue_relation))

    st.markdown("#### Set definitions")

    st.latex(r"B = \{b_1, b_2, \ldots, b_n\}")
    st.caption("B = the set of registered book titles/records.")

    st.latex(r"M = \{m_1, m_2, \ldots, m_k\}")
    st.caption("M = the set of registered library members.")

    st.latex(r"O \subseteq A")
    st.caption(
        "O is a subset of A: every overdue loan is an active loan."
    )

    if overdue_relation.issubset(active_relation):
        st.success(
            "Set property verified: every overdue loan "
            "also belongs to the active-loan set."
        )
    else:
        st.error(
            "The overdue and active loan sets are inconsistent. "
            "Check the source records."
        )

    with st.expander("Inspect the sets"):
        st.write("Book IDs (B):", sorted(book_ids))
        st.write("Member IDs (M):", sorted(member_ids))
        st.write("Active member-book pairs (A):", sorted(active_relation))
        st.write("Overdue member-book pairs (O):", sorted(overdue_relation))

    st.divider()

    # ------------------------------
    # RELATIONS
    # ------------------------------

    st.subheader("2. Borrowing Relation")

    st.markdown(
        "A borrowing relation connects members to books. "
        "Each pair (member ID, book ID) represents a recorded loan."
    )

    st.latex(r"R \subseteq M \times B")

    st.write(f"Total distinct member-book pairs: {len(borrowing_relation)}")

    relation_rows = []

    for member_id, book_id in sorted(borrowing_relation):
        member = next(
            (m for m in members if m["id"] == member_id),
            None,
        )
        book = next(
            (b for b in books if b["id"] == book_id),
            None,
        )

        relation_rows.append(
            {
                "Member ID": member_id,
                "Member": member["full_name"] if member else "Unknown",
                "Book ID": book_id,
                "Book": book["title"] if book else "Unknown",
            }
        )

    if relation_rows:
        st.dataframe(
            pd.DataFrame(relation_rows),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info(
            "No borrowing relations exist yet. Issue a book to "
            "create the first member-book relationship."
        )

    st.caption(
        "This relation uses distinct member-book pairs. "
        "If the same member borrows the same book multiple times, "
        "the pair appears once in R."
    )

    st.divider()

    # ------------------------------
    # GRAPH THEORY
    # ------------------------------

    st.subheader("3. Graph Theory — Library Network")

    st.markdown(
        "Model the library as a bipartite graph: member nodes "
        "on one side, book nodes on the other, and edges "
        "representing borrowing relationships."
    )

    st.latex(r"G = (V, E), \quad V = M \cup B")

    if borrowing_relation:
        # Limit the drawing to the latest 30 distinct pairs
        # so large datasets remain readable.
        visible_pairs = sorted(borrowing_relation)[-30:]

        graph = nx.Graph()

        member_labels = {
            m["id"]: m["full_name"]
            for m in members
        }
        book_labels = {
            b["id"]: b["title"]
            for b in books
        }

        for member_id, book_id in visible_pairs:
            member_node = f"M:{member_id}"
            book_node = f"B:{book_id}"

            graph.add_node(
                member_node,
                node_type="member",
                label=member_labels.get(member_id, str(member_id)),
            )
            graph.add_node(
                book_node,
                node_type="book",
                label=book_labels.get(book_id, str(book_id)),
            )
            graph.add_edge(member_node, book_node)

        positions = nx.bipartite_layout(
            graph,
            [node for node, data in graph.nodes(data=True)
             if data["node_type"] == "member"],
        )

        fig, ax = plt.subplots(figsize=(12, 7))
        fig.patch.set_facecolor("#111329")
        ax.set_facecolor("#111329")

        member_nodes = [
            node for node, data in graph.nodes(data=True)
            if data["node_type"] == "member"
        ]
        book_nodes = [
            node for node, data in graph.nodes(data=True)
            if data["node_type"] == "book"
        ]

        nx.draw_networkx_edges(
            graph,
            positions,
            ax=ax,
            edge_color="#9b8afc",
            width=1.5,
            alpha=0.75,
        )

        nx.draw_networkx_nodes(
            graph,
            positions,
            nodelist=member_nodes,
            node_color="#8b5cf6",
            node_size=1100,
            ax=ax,
        )

        nx.draw_networkx_nodes(
            graph,
            positions,
            nodelist=book_nodes,
            node_color="#38bdf8",
            node_size=1100,
            ax=ax,
        )

        labels = {
            node: (
                data["label"][:18]
                if len(data["label"]) > 18
                else data["label"]
            )
            for node, data in graph.nodes(data=True)
        }

        nx.draw_networkx_labels(
            graph,
            positions,
            labels=labels,
            font_size=8,
            font_color="white",
            ax=ax,
        )

        ax.set_title(
            "Member–Book Borrowing Network",
            color="white",
            fontsize=14,
            pad=18,
        )
        ax.axis("off")
        fig.tight_layout()

        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

        st.caption(
            f"Showing {len(visible_pairs)} distinct member-book "
            "relationships at most. This is a visualization sample "
            "when the library has more than 30 pairs."
        )

        st.write(f"Graph vertices: {graph.number_of_nodes()}")
        st.write(f"Graph edges: {graph.number_of_edges()}")

    else:
        st.info(
            "The graph will appear after the first book is issued."
        )

    st.divider()

    # ------------------------------
    # BOOLEAN DECISION LOGIC
    # ------------------------------

    st.subheader("4. Boolean Logic — Borrowing Eligibility")

    st.markdown(
        "Select a member and a book to inspect the decision conditions. "
        "This is an explanatory preview; the existing service remains "
        "responsible for authorizing actual transactions."
    )

    active_members = [
        member for member in members
        if member["active"] == 1
    ]

    available_books = [
        book for book in books
        if book["available_copies"] > 0
    ]

    if not members or not books:
        st.info("Add at least one member and one book first.")

    else:
        chosen_member_label = st.selectbox(
            "Choose member",
            [
                f'{m["member_code"]} — {m["full_name"]}'
                for m in members
            ],
            key="math_member",
        )

        chosen_member = next(
            m for m in members
            if f'{m["member_code"]} — {m["full_name"]}'
            == chosen_member_label
        )

        chosen_book_label = st.selectbox(
            "Choose book",
            [
                f'{b["title"]} — {b["available_copies"]} available'
                for b in books
            ],
            key="math_book",
        )

        chosen_book = next(
            b for b in books
            if f'{b["title"]} — {b["available_copies"]} available'
            == chosen_book_label
        )

        member_active = chosen_member["active"] == 1

        member_active_loans = [
            loan for loan in active_loans
            if loan["member_id"] == chosen_member["id"]
        ]

        member_has_overdue = any(
            loan["member_id"] == chosen_member["id"]
            for loan in overdue_loans
        )

        within_limit = len(member_active_loans) < 3
        book_available = chosen_book["available_copies"] > 0

        # Same core policy conditions described by the app's
        # current service rules: active member, available copy,
        # fewer than 3 active loans, and no overdue active loan.
        eligible = (
            member_active
            and book_available
            and within_limit
            and not member_has_overdue
        )

        logic_df = pd.DataFrame(
            [
                {
                    "Condition": "Member is active",
                    "Boolean": member_active,
                },
                {
                    "Condition": "Book has an available copy",
                    "Boolean": book_available,
                },
                {
                    "Condition": "Member has fewer than 3 active loans",
                    "Boolean": within_limit,
                },
                {
                    "Condition": "Member has no overdue active loan",
                    "Boolean": not member_has_overdue,
                },
            ]
        )

        st.dataframe(
            logic_df,
            use_container_width=True,
            hide_index=True,
        )

        st.latex(
            r"E = M_a \land B_a \land L_{<3} "
            r"\land \neg O_m"
        )

        st.caption(
            "E = eligibility; Mₐ = active member; Bₐ = available book; "
            "L<3 = fewer than three active loans; Oₘ = member has an "
            "overdue active loan."
        )

        if eligible:
            st.success(
                "All displayed conditions pass. The member appears "
                "eligible under these checks."
            )
        else:
            st.warning(
                "At least one condition fails. The member is not "
                "eligible under the displayed policy checks."
            )

        st.caption(
            "This page does not issue books or modify records. "
            "The circulation service is still the authority for "
            "actual borrowing decisions."
        )


# --------------------------------------------------
# BOOK CATALOG
# --------------------------------------------------

elif page == "Book Catalog":
    st.title("Book Catalog")
    st.caption("Manage your collection and track copy availability.")

    search = st.text_input(
        "Search collection",
        placeholder="Search title, author, ISBN or category...",
    )

    if search:
        displayed_books = services.list_books(search)
    else:
        displayed_books = books

    if displayed_books:
        st.dataframe(
            pd.DataFrame([
                {
                    "ID": b["id"],
                    "ISBN": b["isbn"] or "—",
                    "Title": b["title"],
                    "Author": b["author"],
                    "Category": b["category"],
                    "Total Copies": b["total_copies"],
                    "Available": b["available_copies"],
                }
                for b in displayed_books
            ]),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No books found. Add your first book below.")

    with st.expander("＋ Add a new book", expanded=not bool(books)):
        with st.form("add_book_form", clear_on_submit=True):
            title = st.text_input("Book title *")
            author = st.text_input("Author *")
            category = st.text_input("Category *")
            isbn = st.text_input("ISBN (optional)")
            publisher = st.text_input("Publisher (optional)")
            year = st.number_input(
                "Publication year (0 = unknown)",
                min_value=0,
                max_value=9999,
                value=0,
            )
            copies = st.number_input(
                "Number of copies",
                min_value=0,
                max_value=10000,
                value=1,
            )

            submitted = st.form_submit_button(
                "Add book",
                type="primary",
                use_container_width=True,
            )

            if submitted:
                try:
                    book_id = services.add_book(
                        title=title,
                        author=author,
                        category=category,
                        total_copies=int(copies),
                        isbn=isbn or None,
                        publisher=publisher or None,
                        publication_year=int(year) if year else None,
                    )
                    st.success(f"Book added successfully. ID: {book_id}")
                    st.rerun()
                except (ServiceError, ValueError) as error:
                    show_error(error)

# --------------------------------------------------
# MEMBERS
# --------------------------------------------------

elif page == "Members":
    st.title("Member Management")
    st.caption("Register and view library members.")

    if members:
        st.dataframe(
            pd.DataFrame([
                {
                    "ID": m["id"],
                    "Member Code": m["member_code"],
                    "Full Name": m["full_name"],
                    "Email": m["email"] or "—",
                    "Department": m["department"] or "—",
                    "Status": "Active" if m["active"] else "Inactive",
                }
                for m in members
            ]),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No members registered yet.")

    with st.expander("＋ Register a member", expanded=not bool(members)):
        with st.form("add_member_form", clear_on_submit=True):
            code = st.text_input("Member code *")
            name = st.text_input("Full name *")
            email = st.text_input("Email (optional)")
            department = st.text_input("Department (optional)")

            submitted = st.form_submit_button(
                "Register member",
                type="primary",
                use_container_width=True,
            )

            if submitted:
                try:
                    member_id = services.add_member(
                        member_code=code,
                        full_name=name,
                        email=email or None,
                        department=department or None,
                    )
                    st.success(f"Member registered. ID: {member_id}")
                    st.rerun()
                except (ServiceError, ValueError) as error:
                    show_error(error)

# --------------------------------------------------
# CIRCULATION
# --------------------------------------------------

elif page == "Circulation":
    st.title("Circulation Desk")
    st.caption("Issue books, process returns and enforce borrowing policies.")

    st.info(
        "Policy: maximum 3 active loans per member · "
        "14-day loan period · ₹5 per overdue day · "
        "overdue members cannot borrow."
    )

    active_members = [m for m in members if m["active"] == 1]

    issue_tab, return_tab = st.tabs(["Issue a book", "Return a book"])

    with issue_tab:
        available_books = [
            b for b in books if b["available_copies"] > 0
        ]

        if not active_members:
            st.warning("Register an active member first.")
        elif not available_books:
            st.warning("No copies are available to issue.")
        else:
            with st.form("issue_book_form"):
                member_options = {
                    f"{m['member_code']} — {m['full_name']}": m["id"]
                    for m in active_members
                }
                book_options = {
                    f"{b['title']} — {b['author']} "
                    f"({b['available_copies']} available)": b["id"]
                    for b in available_books
                }

                selected_member = st.selectbox(
                    "Select member",
                    list(member_options.keys()),
                )
                selected_book = st.selectbox(
                    "Select book",
                    list(book_options.keys()),
                )

                submitted = st.form_submit_button(
                    "Issue book",
                    type="primary",
                    use_container_width=True,
                )

                if submitted:
                    try:
                        result = services.issue_book(
                            book_id=book_options[selected_book],
                            member_id=member_options[selected_member],
                        )
                        show_success(result)
                        st.rerun()
                    except ServiceError as error:
                        show_error(error)

    with return_tab:
        if not active_loans:
            st.info("There are no active loans to return.")
        else:
            loan_options = {
                f"Loan #{l['id']} — {l['title']} / "
                f"{l['full_name']} (due {l['due_at']})": l["id"]
                for l in active_loans
            }

            with st.form("return_book_form"):
                selected_loan = st.selectbox(
                    "Select active loan",
                    list(loan_options.keys()),
                )

                submitted = st.form_submit_button(
                    "Process return",
                    type="primary",
                    use_container_width=True,
                )

                if submitted:
                    try:
                        result = services.return_book(
                            loan_options[selected_loan]
                        )
                        show_success(result)

                        if result["fine_amount"] > 0:
                            st.warning(
                                f"Overdue fine: ₹{result['fine_amount']:.2f}"
                            )

                        st.rerun()
                    except ServiceError as error:
                        show_error(error)

    st.subheader("Current active loans")

    if active_loans:
        st.dataframe(
            pd.DataFrame([
                {
                    "Loan ID": l["id"],
                    "Book": l["title"],
                    "Member": l["full_name"],
                    "Member Code": l["member_code"],
                    "Issue Date": l["issued_at"],
                    "Due Date": l["due_at"],
                    "Status": (
                        "Overdue" if l["due_at"] < today.isoformat()
                        else "Active"
                    ),
                }
                for l in active_loans
            ]),
            use_container_width=True,
            hide_index=True,
        )

# --------------------------------------------------
# RESERVATIONS
# --------------------------------------------------

elif page == "Reservations":
    st.title("Reservations & Waitlist")
    st.caption("Manage the waiting list for unavailable books.")

    waiting = services.list_reservations()

    if waiting:
        st.dataframe(
            pd.DataFrame([
                {
                    "Reservation ID": r["id"],
                    "Book": r["title"],
                    "Member": r["full_name"],
                    "Member Code": r["member_code"],
                    "Status": r["status"],
                    "Created": r["created_at"],
                }
                for r in waiting
            ]),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("There are no reservations yet.")

    unavailable_books = [
        b for b in books if b["available_copies"] <= 0
    ]
    active_members = [m for m in members if m["active"] == 1]

    with st.expander("＋ Create a reservation"):
        if not unavailable_books:
            st.info("No books are currently out of stock.")
        elif not active_members:
            st.info("Register a member first.")
        else:
            with st.form("reservation_form"):
                book_options = {
                    b["title"]: b["id"] for b in unavailable_books
                }
                member_options = {
                    f"{m['member_code']} — {m['full_name']}": m["id"]
                    for m in active_members
                }

                selected_book = st.selectbox(
                    "Book", list(book_options.keys())
                )
                selected_member = st.selectbox(
                    "Member", list(member_options.keys())
                )

                submitted = st.form_submit_button(
                    "Reserve book",
                    type="primary",
                )

                if submitted:
                    try:
                        result = services.reserve_book(
                            book_options[selected_book],
                            member_options[selected_member],
                        )
                        show_success(result)
                        st.rerun()
                    except ServiceError as error:
                        show_error(error)

# --------------------------------------------------
# AUDIT LOG
# --------------------------------------------------

elif page == "Activity Log":
    st.title("Activity Log")
    st.caption("Review recent library operations.")

    logs = services.list_audit_logs(limit=200)

    if logs:
        st.dataframe(
            pd.DataFrame([
                {
                    "ID": log["id"],
                    "Action": log["action"],
                    "Entity": log["entity_type"],
                    "Entity ID": log["entity_id"],
                    "Details": log["details"],
                    "Timestamp": log["created_at"],
                }
                for log in logs
            ]),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No activity recorded yet.")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()
st.caption(
    "LibNova · Intelligent Library Operations · "
    "Academic prototype"
)
