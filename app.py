

import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display
from pathlib import Path
from datetime import datetime

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="GradeFlow",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. SESSION STATE
# ==========================================

if "subjects" not in st.session_state:
    st.session_state.subjects = [
        {"name": "Computer Networks", "grade": 0.0, "credit": 1},
        {"name": "Mathematics", "grade": 0.0, "credit": 1},
        {"name": "Python", "grade": 0.0, "credit": 1}
    ]

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

if "student_name" not in st.session_state:
    st.session_state.student_name = "Student"

if "student_department" not in st.session_state:
    st.session_state.student_department = "AI Technologies"

if "student_stage" not in st.session_state:
    st.session_state.student_stage = "Stage 2"

# ==========================================
# 3. COLORS AND DESIGN
# ==========================================

dark = st.session_state.dark_mode

if dark:
    BG = "#101010"
    CARD = "#1C1C1C"
    TEXT = "#F5F5F5"
    MUTED = "#A8A8A8"
    GOLD = "#D5B56A"
    BORDER = "#333333"
else:
    BG = "#F3F3F3"
    CARD = "#FFFFFF"
    TEXT = "#202020"
    MUTED = "#666666"
    GOLD = "#98732D"
    BORDER = "#DDDDDD"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {{
    background: {BG};
    color: {TEXT};
    font-family: 'Inter', sans-serif;
}}

header[data-testid="stHeader"] {{
    background: {BG};
}}

section[data-testid="stSidebar"] {{
    background: {CARD};
    border-right: 1px solid {BORDER};
}}

h1, h2, h3, h4, p, label, span {{
    color: {TEXT};
}}

.brand {{
    color: {GOLD};
    font-size: 36px;
    font-weight: 800;
    letter-spacing: 2px;
}}

.subtitle {{
    color: {MUTED};
    font-size: 13px;
    letter-spacing: 1px;
}}

.section-title {{
    font-size: 23px;
    font-weight: 700;
    color: {TEXT};
    margin-top: 20px;
    margin-bottom: 15px;
}}

.metric-card {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 22px;
    min-height: 120px;
}}

.metric-label {{
    color: {GOLD};
    font-size: 13px;
    font-weight: 600;
}}

.metric-value {{
    color: {TEXT};
    font-size: 31px;
    font-weight: 800;
    margin-top: 12px;
}}

div.stButton > button {{
    background: {GOLD};
    color: #111111;
    border: none;
    border-radius: 9px;
    font-weight: 700;
    padding: 9px 18px;
}}

div.stButton > button:hover {{
    background: #E6C77F;
    color: #111111;
    border: none;
}}

div[data-testid="stDownloadButton"] button {{
    background: {GOLD};
    color: #111111;
    border-radius: 9px;
    font-weight: 700;
}}

input, textarea {{
    border-radius: 8px !important;
}}

div[data-testid="stPlotlyChart"] {{
    background: {CARD};
    border-radius: 12px;
    padding: 10px;
}}

hr {{
    border-color: {BORDER};
}}

</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. CALCULATIONS
# ==========================================

subjects = st.session_state.subjects

completed = [
    s for s in subjects
    if s["grade"] > 0
]

total_credits = sum(s["credit"] for s in completed)

average = (
    sum(s["grade"] * s["credit"] for s in completed)
    / total_credits
    if total_credits > 0 else 0
)

highest = (
    max([s["grade"] for s in completed])
    if completed else 0
)

# ==========================================
# 5. SIDEBAR NAVIGATION
# ==========================================

with st.sidebar:

    st.markdown(
        f'<div class="brand">GF.</div>',
        unsafe_allow_html=True
    )

    st.caption("GRADE FLOW | ACADEMIC SYSTEM")

    st.divider()

    page = st.radio(
        "MAIN MENU",
        [
            "Dashboard",
            "Subjects",
            "Charts",
            "Target",
            "PDF Report",
            "Profile"
        ],
        index=0
    )

    st.divider()

    st.markdown("### Appearance")

    st.session_state.dark_mode = st.toggle(
        "Dark Mode",
        value=st.session_state.dark_mode
    )

    st.divider()

    st.caption("GRADE FLOW © 2026")

# ==========================================
# 6. HEADER
# ==========================================

st.markdown(
    '<div class="brand">GRADE FLOW</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">ACADEMIC PERFORMANCE SYSTEM</div>',
    unsafe_allow_html=True
)

st.write("")

# ==========================================
# 7. DASHBOARD
# ==========================================

if page == "Dashboard":

    st.markdown(
        '<div class="section-title">لوحة التحكم الرئيسية</div>',
        unsafe_allow_html=True
    )

    st.caption(
        f"Welcome, {st.session_state.student_name} | "
        "Your academic overview"
    )

    c1, c2, c3, c4 = st.columns(4)

    metrics = [
        ("المعدل العام", f"{average:.2f}"),
        ("عدد المواد", str(len(subjects))),
        ("أعلى درجة", f"{highest:.1f}"),
        ("المواد المسجلة", str(len(completed)))
    ]

    for col, (label, value) in zip(
        [c1, c2, c3, c4], metrics
    ):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.write("")

    left, right = st.columns([1.5, 1])

    with left:

        st.markdown(
            '<div class="section-title">درجات المواد</div>',
            unsafe_allow_html=True
        )

        if completed:

            df = pd.DataFrame(completed)

            fig = px.bar(
                df,
                x="name",
                y="grade",
                text="grade",
                color_discrete_sequence=[GOLD]
            )

            fig.update_traces(
                texttemplate="%{text:.1f}",
                textposition="outside",
                marker_line_width=0
            )

            fig.update_layout(
                paper_bgcolor=CARD,
                plot_bgcolor=CARD,
                font_color=TEXT,
                showlegend=False,
                yaxis=dict(
                    range=[0, 110],
                    title="Grade",
                    gridcolor=BORDER
                ),
                xaxis=dict(
                    title="Subject",
                    gridcolor=BORDER
                ),
                margin=dict(l=20, r=20, t=35, b=50)
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:
            st.info("أضيفي درجات المواد حتى يظهر الرسم البياني.")

    with right:

        st.markdown(
            '<div class="section-title">ملخص الأداء</div>',
            unsafe_allow_html=True
        )

        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">المعدل الحالي</div>
            <div class="metric-value">{average:.2f}%</div>
            <hr>
            <div class="metric-label">الحالة الأكاديمية</div>
            <h3>{'ناجح' if average >= 50 else 'لم يكتمل التقييم' if average == 0 else 'دون درجة النجاح'}</h3>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 8. SUBJECTS MANAGEMENT
# ==========================================

elif page == "Subjects":

    st.markdown(
        '<div class="section-title">إدارة المواد والدرجات</div>',
        unsafe_allow_html=True
    )

    st.caption("Add, edit and manage your academic subjects.")

    for i, subject in enumerate(subjects):

        with st.container(border=True):

            col1, col2, col3, col4 = st.columns(
                [2, 1.5, 1, 0.8]
            )

            with col1:
                st.write(f"**{subject['name']}**")

            with col2:
                new_grade = st.number_input(
                    "الدرجة",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(subject["grade"]),
                    step=1.0,
                    key=f"grade_{i}"
                )

                st.session_state.subjects[i]["grade"] = new_grade

            with col3:
                new_credit = st.number_input(
                    "الوحدات",
                    min_value=1,
                    max_value=10,
                    value=int(subject["credit"]),
                    key=f"credit_{i}"
                )

                st.session_state.subjects[i]["credit"] = new_credit

            with col4:
                if st.button("حذف", key=f"delete_{i}"):
                    st.session_state.subjects.pop(i)
                    st.rerun()

    st.divider()

    st.markdown("### إضافة مادة جديدة")

    with st.form("add_subject"):

        name = st.text_input("اسم المادة")

        grade = st.number_input(
            "الدرجة",
            min_value=0.0,
            max_value=100.0,
            value=0.0
        )

        credit = st.number_input(
            "عدد الوحدات",
            min_value=1,
            max_value=10,
            value=1
        )

        submitted = st.form_submit_button(
            "إضافة المادة"
        )

        if submitted:

            if name.strip():

                st.session_state.subjects.append({
                    "name": name.strip(),
                    "grade": grade,
                    "credit": credit
                })

                st.success("تمت إضافة المادة بنجاح!")
                st.rerun()

            else:
                st.error("يرجى كتابة اسم المادة.")

# ==========================================
# 9. CHARTS
# ==========================================

elif page == "Charts":

    st.markdown(
        '<div class="section-title">تحليل الأداء الأكاديمي</div>',
        unsafe_allow_html=True
    )

    if completed:

        df = pd.DataFrame(completed)

        fig = px.bar(
            df,
            x="name",
            y="grade",
            text="grade",
            color_discrete_sequence=[GOLD]
        )

        fig.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside"
        )

        fig.update_layout(
            paper_bgcolor=BG,
            plot_bgcolor=CARD,
            font_color=TEXT,
            yaxis=dict(
                range=[0, 110],
                gridcolor=BORDER
            ),
            xaxis=dict(
                gridcolor=BORDER
            ),
            margin=dict(l=30, r=30, t=35, b=50)
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        fig2 = px.pie(
            df,
            names="name",
            values="grade",
            hole=0.55,
            color_discrete_sequence=[
                "#D5B56A",
                "#A98743",
                "#75613C",
                "#E8D5A5",
                "#8B8B8B"
            ]
        )

        fig2.update_layout(
            paper_bgcolor=BG,
            font_color=TEXT,
            legend_title_text="Subjects"
        )

        st.markdown("### توزيع الدرجات")

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    else:
        st.info("لا توجد درجات لتحليلها حالياً.")

# ==========================================
# 10. TARGET CALCULATOR
# ==========================================

elif page == "Target":

    st.markdown(
        '<div class="section-title">حاسبة المعدل المستهدف</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Discover the grades you need to reach your academic goal."
    )

    target = st.number_input(
        "المعدل الذي تريد الوصول إليه",
        min_value=0.0,
        max_value=100.0,
        value=85.0
    )

    remaining = st.number_input(
        "عدد المواد المتبقية",
        min_value=1,
        max_value=30,
        value=3
    )

    if st.button("احسب الدرجة المطلوبة"):

        if completed:

            current_sum = sum(
                s["grade"] * s["credit"]
                for s in completed
            )

            current_count = sum(
                s["credit"] for s in completed
            )

            required = (
                target * (current_count + remaining)
                - current_sum
            ) / remaining

            if required > 100:
                st.error(
                    f"الوصول لهذا المعدل غير ممكن حسابياً "
                    f"ضمن الدرجات المتبقية. تحتاجين {required:.2f}."
                )

            elif required <= 0:
                st.success(
                    "وصلتِ إلى المعدل المستهدف وفق هذه الفرضيات."
                )

            else:
                st.success(
                    f"تحتاجين إلى معدل {required:.2f} "
                    "في كل مادة متبقية."
                )

        else:
            st.warning(
                "أدخلي درجات المواد المكتملة أولاً."
            )

    st.caption(
        "الحساب يفترض تساوي وحدات المواد المتبقية."
    )

# ==========================================
# 11. PDF REPORT
# ==========================================

elif page == "PDF Report":

    st.markdown(
        '<div class="section-title">تصدير التقرير الأكاديمي</div>',
        unsafe_allow_html=True
    )

    st.write(
        "أنشئي تقريراً يتضمن اسم الطالب والمواد والدرجات والمعدل."
    )

    def make_rtl(text):
        return get_display(
            arabic_reshaper.reshape(str(text))
        )

    def create_pdf():

        pdf = FPDF()
        pdf.add_page()

        font_path = Path("C:/Windows/Fonts/arial.ttf")

        if not font_path.exists():
            raise FileNotFoundError(
                "لم يتم العثور على خط Arial في Windows."
            )

        pdf.add_font(
            "Arial",
            "",
            str(font_path)
        )

        pdf.set_font("Arial", size=18)

        pdf.set_text_color(170, 130, 55)

        pdf.cell(
            0, 15,
            "GRADE FLOW",
            align="C",
            new_x="LMARGIN",
            new_y="NEXT"
        )

        pdf.set_text_color(30, 30, 30)
        pdf.set_font("Arial", size=13)

        pdf.cell(
            0, 12,
            make_rtl("التقرير الأكاديمي"),
            align="C",
            new_x="LMARGIN",
            new_y="NEXT"
        )

        pdf.ln(5)

        pdf.set_font("Arial", size=11)

        info = [
            f"Student: {st.session_state.student_name}",
            f"Department: {st.session_state.student_department}",
            f"Stage: {st.session_state.student_stage}",
            f"Date: {datetime.now().strftime('%Y-%m-%d')}"
        ]

        for item in info:
            pdf.cell(
                0, 9,
                item,
                new_x="LMARGIN",
                new_y="NEXT"
            )

        pdf.ln(5)

        pdf.set_font("Arial", size=11)

        for subject in subjects:

            line = (
                f"{subject['name']} | "
                f"Grade: {subject['grade']:.1f} | "
                f"Credits: {subject['credit']}"
            )

            pdf.cell(
                0, 10,
                line,
                new_x="LMARGIN",
                new_y="NEXT"
            )

        pdf.ln(8)

        pdf.set_font("Arial", size=15)

        pdf.set_text_color(170, 130, 55)

        pdf.cell(
            0, 12,
            f"Overall Average: {average:.2f}%",
            new_x="LMARGIN",
            new_y="NEXT"
        )

        return bytes(pdf.output())

    if st.button("إنشاء تقرير PDF"):

        try:

            pdf_data = create_pdf()

            st.download_button(
                label="تحميل التقرير",
                data=pdf_data,
                file_name="GradeFlow_Report.pdf",
                mime="application/pdf"
            )

            st.success("تم إنشاء التقرير بنجاح!")

        except Exception as e:

            st.error(f"حدث خطأ أثناء إنشاء PDF: {e}")

# ==========================================
# 12. PROFILE
# ==========================================

elif page == "Profile":

    st.markdown(
        '<div class="section-title">الملف الشخصي</div>',
        unsafe_allow_html=True
    )

    st.caption("Manage your academic information.")

    with st.form("profile_form"):

        student_name = st.text_input(
            "اسم الطالب",
            value=st.session_state.student_name
        )

        department = st.text_input(
            "القسم",
            value=st.session_state.student_department
        )

        stage = st.selectbox(
            "المرحلة",
            ["Stage 1", "Stage 2", "Stage 3", "Stage 4"],
            index=[
                "Stage 1",
                "Stage 2",
                "Stage 3",
                "Stage 4"
            ].index(st.session_state.student_stage)
            if st.session_state.student_stage in [
                "Stage 1",
                "Stage 2",
                "Stage 3",
                "Stage 4"
            ] else 1
        )

        save = st.form_submit_button(
            "حفظ الملف الشخصي"
        )

        if save:

            st.session_state.student_name = student_name
            st.session_state.student_department = department
            st.session_state.student_stage = stage

            st.success("تم تحديث الملف الشخصي!")

# ==========================================
# 13. FOOTER
# ==========================================

st.divider()

st.markdown(
    f"""
    <div style="text-align:center; padding:15px;">
        <span style="color:{GOLD}; font-weight:800;">
            GRADE FLOW
        </span>
        <br>
        <span style="color:{MUTED}; font-size:12px;">
            Academic Performance System | 2026
        </span>
    </div>
    """,
    unsafe_allow_html=True
)
