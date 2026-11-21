
"""
Personal Carbon Footprint Calculator
Built using Streamlit

Run using:
streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from docx import Document
from io import BytesIO


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Carbon Footprint Calculator",
    page_icon="🌱",
    layout="wide"
)


# ==========================================
# EMISSION FACTORS
# ==========================================

ELECTRICITY_FACTOR = 0.727
LPG_FACTOR = 42.6
FLIGHT_FACTOR = 300
SHOPPING_FACTOR = 0.012

INDIA_AVERAGE = 2000
TREE_ABSORBS = 21


TRANSPORT = {
    "Car (petrol)": 0.17,
    "Motorbike / scooter": 0.07,
    "Bus": 0.09,
    "Train / metro": 0.04,
    "Walk / cycle": 0.0,
}

DIETS = {
    "Vegetarian": 1.7,
    "Mixed (some non-veg)": 2.5,
    "Non-veg most days": 3.3,
}

RECYCLING = {
    "Almost nothing": 1.0,
    "Some of it": 0.8,
    "Most of it": 0.6,
}


# ==========================================
# RECOMMENDATIONS
# ==========================================

TIPS = {
    "Electricity":
        "Use LED bulbs, energy-efficient appliances and switch off unused devices.",

    "Cooking gas":
        "Use pressure cookers, cover cooking pots and avoid unnecessary gas consumption.",

    "Commute":
        "Prefer public transport, carpooling, cycling or walking.",

    "Flights":
        "Prefer trains for shorter journeys and combine trips whenever possible.",

    "Food":
        "Eat more plant-based meals, buy seasonal food and avoid food wastage.",

    "Shopping":
        "Purchase durable products, repair old items and avoid unnecessary shopping."
}


# ==========================================
# SESSION STATE
# ==========================================

if "results" not in st.session_state:
    st.session_state.results = None


# ==========================================
# SIDEBAR NAVIGATION
# ==========================================

st.sidebar.title("🌱 Eco Calculator")

st.sidebar.write("Personal Carbon Footprint Calculator")

page = st.sidebar.radio(
    "Navigation",
    [
        "Calculator",
        "Results & Reports",
        "Methodology"
    ]
)

st.sidebar.divider()

st.sidebar.caption(
    "Small changes today create a greener tomorrow. 🌍"
)


# ==========================================
# CALCULATOR PAGE
# ==========================================

if page == "Calculator":

    st.title("🌱 Personal Carbon Footprint Calculator")

    st.write(
        "Calculate your yearly carbon emissions "
        "and discover ways to reduce your environmental impact."
    )

    st.divider()

    with st.form("footprint_form"):

        # HOME ENERGY

        st.subheader("🏠 Home Energy")

        col1, col2, col3 = st.columns(3)

        kwh = col1.number_input(
            "Electricity per month (kWh)",
            min_value=0.0,
            value=150.0,
            step=10.0
        )

        cylinders = col2.number_input(
            "LPG cylinders per month",
            min_value=0.0,
            value=1.0,
            step=0.5
        )

        people = col3.number_input(
            "People in household",
            min_value=1,
            value=4,
            step=1
        )

        st.divider()

        # TRANSPORT

        st.subheader("🚗 Transportation")

        col4, col5, col6 = st.columns(3)

        mode = col4.selectbox(
            "Main daily transport mode",
            list(TRANSPORT.keys()),
            index=1
        )

        km_per_week = col5.number_input(
            "Distance per week (km)",
            min_value=0.0,
            value=80.0,
            step=5.0
        )

        flights = col6.number_input(
            "Flights per year (round trips)",
            min_value=0,
            value=1,
            step=1
        )

        st.divider()

        # FOOD AND SHOPPING

        st.subheader("🍽️ Food and Shopping")

        col7, col8, col9 = st.columns(3)

        diet = col7.selectbox(
            "Diet type",
            list(DIETS.keys()),
            index=1
        )

        recycle = col8.selectbox(
            "Waste you recycle",
            list(RECYCLING.keys()),
            index=1
        )

        shopping_rs = col9.number_input(
            "New clothes/gadgets per month (Rs)",
            min_value=0.0,
            value=1500.0,
            step=100.0
        )

        submitted = st.form_submit_button(
            "🌍 Calculate My Footprint",
            use_container_width=True
        )


    # ======================================
    # CALCULATIONS
    # ======================================

    if submitted:

        categories = {

            "Electricity":
                kwh * ELECTRICITY_FACTOR * 12 / people,

            "Cooking gas":
                cylinders * LPG_FACTOR * 12 / people,

            "Commute":
                km_per_week * TRANSPORT[mode] * 52,

            "Flights":
                flights * FLIGHT_FACTOR,

            "Food":
                DIETS[diet] * 365,

            "Shopping":
                shopping_rs * SHOPPING_FACTOR * 12 * RECYCLING[recycle],

        }

        total = sum(categories.values())

        # SUSTAINABILITY SCORE

        score = max(
            0,
            min(100, 100 * (1 - total / INDIA_AVERAGE))
        )

        # TOP THREE PRIORITIES

        sorted_categories = sorted(
            categories.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # SAVE RESULTS

        st.session_state.results = {

            "categories": categories,
            "total": total,
            "score": score,
            "sorted_categories": sorted_categories

        }

        st.success(
            "Your carbon footprint has been calculated successfully!"
        )

        st.info(
            "Open 'Results & Reports' from the sidebar "
            "to explore your results."
        )


# ==========================================
# RESULTS AND REPORTS PAGE
# ==========================================

elif page == "Results & Reports":

    st.title("📊 Your Carbon Footprint Results")

    if st.session_state.results is None:

        st.warning(
            "Please calculate your carbon footprint first."
        )

    else:

        results = st.session_state.results

        categories = results["categories"]

        total = results["total"]

        score = results["score"]

        sorted_categories = results["sorted_categories"]


        # ----------------------------------
        # MAIN METRICS
        # ----------------------------------

        st.subheader("📌 Dashboard Overview")

        diff = (total / INDIA_AVERAGE - 1) * 100

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Yearly Carbon Footprint",
            f"{total / 1000:.2f} tonnes"
        )

        col2.metric(
            "Compared to India Benchmark",
            f"{total / INDIA_AVERAGE:.2f}x",
            f"{diff:+.1f}%",
            delta_color="inverse"
        )

        col3.metric(
            "Trees Needed",
            f"{round(total / TREE_ABSORBS)}"
        )

        st.divider()


        # ==================================
        # SUSTAINABILITY SCORE
        # ==================================

        st.header("🌿 Sustainability Score")

        st.metric(
            "Your Score",
            f"{score:.1f}/100"
        )

        st.progress(int(score))

        if score >= 75:

            st.success(
                "Excellent! Your estimated carbon footprint "
                "is relatively low compared with the project benchmark."
            )

        elif score >= 50:

            st.info(
                "Good progress! There is still room "
                "to improve your environmental impact."
            )

        elif score >= 25:

            st.warning(
                "Your carbon footprint needs attention. "
                "Consider adopting greener habits."
            )

        else:

            st.error(
                "Your estimated carbon footprint is high "
                "compared with the project benchmark."
            )

        st.caption(
            "This is an educational score based on a 2000 kg "
            "CO2e annual reference benchmark, not an official rating."
        )

        st.divider()


        # ==================================
        # INTERACTIVE GRAPH
        # ==================================

        st.header("📊 Emission Breakdown")

        df = pd.DataFrame({

            "Category": list(categories.keys(),

            ),

            "Emissions": list(categories.values())

        })

        fig = px.pie(

            df,

            names="Category",

            values="Emissions",

            title="Carbon Emissions by Category",

            hole=0.4

        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


        # BAR GRAPH

        st.subheader("Category-wise Comparison")

        bar_fig = px.bar(

            df,

            x="Category",

            y="Emissions",

            title="Annual Emissions by Category",

            labels={
                "Emissions": "kg CO2e per year"
            }

        )

        st.plotly_chart(
            bar_fig,
            use_container_width=True
        )


        st.divider()


        # ==================================
        # EMISSION TABLE
        # ==================================

        st.header("📋 Detailed Emission Report")

        table = pd.DataFrame({

            "Category": list(categories.keys()),

            "kg CO2e/year": [
                round(v, 2)
                for v in categories.values()
            ],

            "Share (%)": [
                round(v / total * 100, 2) if total > 0 else 0
                for v in categories.values()
            ]

        })

        st.dataframe(
            table,
            hide_index=True,
            use_container_width=True
        )


        st.divider()


        # ==================================
        # TOP PRIORITIES
        # ==================================

        st.header("🎯 Your Top Priorities")

        st.write(
            "These are the three categories contributing "
            "the most to your carbon footprint."
        )

        for index, (name, emission) in enumerate(
            sorted_categories[:3],
            start=1
        ):

            if emission > 0:

                st.subheader(
                    f"{index}. {name}"
                )

                st.write(
                    f"Annual emissions: {emission:.2f} kg CO2e"
                )

                st.success(
                    f"💡 Recommendation: {TIPS[name]}"
                )


        st.divider()


        # ==================================
        # DOWNLOADABLE WORD REPORT
        # ==================================

        st.header("📄 Download Your Carbon Report")

        def generate_report():

            doc = Document()

            doc.add_heading(
                "Personal Carbon Footprint Report",
                0
            )

            doc.add_paragraph(
                "Annual Carbon Footprint Analysis"
            )

            doc.add_heading(
                "1. Overall Results",
                level=1
            )

            doc.add_paragraph(
                f"Total Emissions: {total:.2f} kg CO2e/year"
            )

            doc.add_paragraph(
                f"Sustainability Score: {score:.1f}/100"
            )

            doc.add_paragraph(
                f"Trees Needed: {round(total / TREE_ABSORBS)}"
            )

            doc.add_heading(
                "2. Category Breakdown",
                level=1
            )

            report_table = doc.add_table(
                rows=1,
                cols=3
            )

            report_table.style = "Table Grid"

            headers = report_table.rows[0].cells

            headers[0].text = "Category"

            headers[1].text = "Emissions (kg CO2e)"

            headers[2].text = "Share (%)"

            for category, emission in categories.items():

                row = report_table.add_row().cells

                row[0].text = category

                row[1].text = f"{emission:.2f}"

                share = (
                    emission / total * 100
                    if total > 0 else 0
                )

                row[2].text = f"{share:.2f}%"

            doc.add_heading(
                "3. Top Three Priorities",
                level=1
            )

            for name, emission in sorted_categories[:3]:

                if emission > 0:

                    doc.add_heading(
                        name,
                        level=2
                    )

                    doc.add_paragraph(
                        TIPS[name]
                    )

            doc.add_heading(
                "4. Methodology",
                level=1
            )

            doc.add_paragraph(
                "Carbon emissions are estimated by multiplying "
                "activity data by the corresponding emission factor."
            )

            doc.add_paragraph(
                "Results are estimates and depend on the emission "
                "factors and assumptions used in this application."
            )

            doc.add_paragraph(
                "The sustainability score is a simplified educational "
                "model using 2000 kg CO2e/year as its reference benchmark."
            )

            file = BytesIO()

            doc.save(file)

            file.seek(0)

            return file


        report = generate_report()

        st.download_button(

            label="⬇️ Download My Report (DOCX)",

            data=report,

            file_name="Carbon_Footprint_Report.docx",

            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",

            use_container_width=True

        )


        st.caption(
            "Emission factors are estimates. "
            "Results should not be treated as a certified carbon audit."
        )


# ==========================================
# METHODOLOGY PAGE
# ==========================================

elif page == "Methodology":

    st.title("📚 Calculation Methodology")

    st.write(
        "This page explains how the Personal Carbon Footprint "
        "Calculator estimates annual carbon emissions."
    )

    st.divider()


    # GENERAL FORMULA

    st.header("1. Basic Calculation Formula")

    st.latex(
        r"CO_2e = Activity\ Data \times Emission\ Factor"
    )

    st.write(
        "Activity data represents the amount of electricity, "
        "fuel, distance or consumption. The emission factor "
        "converts that activity into estimated emissions."
    )


    # ELECTRICITY

    st.header("2. Electricity Emissions")

    st.latex(
        r"E = kWh \times 0.727 \times 12"
    )

    st.write(
        "Electricity consumption is multiplied by the "
        "electricity emission factor of 0.727 kg CO2e/kWh. "
        "Annual household emissions are divided by household size."
    )


    # LPG

    st.header("3. Cooking Gas Emissions")

    st.latex(
        r"E = Cylinders \times 42.6 \times 12"
    )

    st.write(
        "Monthly LPG cylinder consumption is multiplied by "
        "the LPG emission factor and 12 months. "
        "The household result is divided by household size."
    )


    # TRANSPORT

    st.header("4. Transportation Emissions")

    st.latex(
        r"E = Distance\ per\ week \times Factor \times 52"
    )

    st.write(
        "Weekly travel distance is multiplied by the "
        "emission factor of the selected transport mode "
        "and 52 weeks."
    )


    # FLIGHTS

    st.header("5. Flight Emissions")

    st.latex(
        r"E = Annual\ Flights \times 300"
    )

    st.write(
        "The number of annual round-trip flights is multiplied "
        "by the approximate flight emission factor."
    )


    # FOOD

    st.header("6. Food Emissions")

    st.latex(
        r"E = Diet\ Factor \times 365"
    )

    st.write(
        "Daily estimated dietary emissions are multiplied "
        "by 365 days based on the selected diet type."
    )


    # SHOPPING

    st.header("7. Shopping Emissions")

    st.latex(
        r"E = Monthly\ Spending \times 0.012 \times 12"
    )

    st.write(
        "Monthly spending on new clothes and gadgets is "
        "multiplied by the shopping emission factor and 12 months."
    )

    st.write(
        "The selected recycling multiplier is also applied "
        "in this project's shopping calculation."
    )


    # TOTAL

    st.header("8. Total Carbon Footprint")

    st.latex(
        r"Total\ Emissions = \sum E_i"
    )

    st.write(
        "All category emissions are added to calculate "
        "the estimated annual carbon footprint."
    )


    # SUSTAINABILITY SCORE

    st.header("9. Sustainability Score")

    st.latex(
        r"Score = 100 \times \left(1-\frac{Total}{2000}\right)"
    )

    st.write(
        "The score is restricted to a range of 0 to 100. "
        "A lower estimated footprint produces a higher score."
    )


    # TREE EQUIVALENT

    st.header("10. Tree Equivalents")

    st.latex(
        r"Trees = \frac{Total\ Emissions}{21}"
    )

    st.write(
        "This estimates the number of trees required to absorb "
        "an equivalent amount of CO2 over one year, using "
        "the project's assumed absorption factor."
    )


    # EMISSION FACTORS TABLE

    st.divider()

    st.header("📋 Emission Factors Used")

    factors = pd.DataFrame({

        "Category": [
            "Electricity",
            "LPG",
            "Flights",
            "Shopping",
            "Car (petrol)",
            "Motorbike",
            "Bus",
            "Train / Metro",
            "Walk / Cycle"
        ],

        "Emission Factor": [
            0.727,
            42.6,
            300,
            0.012,
            0.17,
            0.07,
            0.09,
            0.04,
            0.0
        ],

        "Unit": [
            "kg CO2e/kWh",
            "kg CO2e/cylinder",
            "kg CO2e/round trip",
            "kg CO2e/rupee",
            "kg CO2e/km",
            "kg CO2e/km",
            "kg CO2e/km",
            "kg CO2e/km",
            "kg CO2e/km"
        ]

    })

    st.dataframe(
        factors,
        hide_index=True,
        use_container_width=True
    )


    # DISCLAIMER

    st.divider()

    st.header("⚠️ Important Information")

    st.info(
        """
        This calculator provides approximate carbon emission estimates.

        Actual emissions may vary depending on geographical location,
        electricity sources, vehicle efficiency, travel conditions,
        consumption patterns and other environmental factors.

        The emission factors and sustainability benchmark should be
        verified against reliable published sources before using
        the results for formal environmental reporting.
        """
    )


# ==========================================
# FOOTER
# ==========================================

st.sidebar.divider()

st.sidebar.caption(
    "🌍 Personal Carbon Footprint Calculator"
)

st.sidebar.caption(
    "Building a sustainable future."
)