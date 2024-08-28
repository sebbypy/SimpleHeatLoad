import pandas as pd
import streamlit as st

from simpleLoadModel import RoomLoadCalculator


def main():
    st.title("Multi-Room Heat Loss Calculator")

    st.sidebar.header("Building-Level Parameters")
    with st.sidebar.expander("Building Settings"):
        uw = st.number_input("Wall U-value (W/m²K)", min_value=0.0, value=1.0, help="U-value of the walls.")
        u_roof = st.number_input("Roof U-value (W/m²K)", min_value=0.0, value=0.2, help="U-value of the roof.")
        u_ground = st.number_input("Ground U-value (W/m²K)", min_value=0.0, value=0.3,
                                   help="U-value of the ground floor.")
        tout = st.number_input("Outdoor Temperature (°C)", value=-7.0,
                               help="Outdoor temperature during heating season.")
        heat_loss_area_estimation = st.selectbox("Heat Loss Area Estimation",
                                                 options=["fromFloorArea", "fromExposedPerimeter"],
                                                 help="Method for estimating the heat losses.")
    with st.sidebar.expander("Ventilation Settings"):
        ventilation_calculation_method = st.selectbox("Ventilation Calculation Method",
                                                      options=["simple", "NBN-D-50-001"],
                                                      help="Method used for calculating ventilation heat losses.")
        v_system = st.selectbox("Ventilation System", options=["C", "D"], help="Type of ventilation system.")
        v50 = st.number_input("Air Tightness (v50)", min_value=0.0, value=6.0,
                              help="Air leakage rate at 50 Pa (ACH).")
    with st.sidebar.expander("Advanced Settings"):
        neighbour_t = st.number_input("Neighbour Temperature (°C)", value=18.0,
                                      help="Temperature of the neighbouring space.")
        un = st.number_input("Neighbour Loss Coefficient (un)", value=1.0,
                             help="Coefficient for heat loss to neighbours.")
        lir = st.number_input("Infiltration Rate (lir)", value=0.2, help="Infiltration rate.")
        wall_height = st.number_input("Wall Height (m)", value=2.7, help="Height of the walls.")
        return_detail = st.checkbox("Return Detailed Results", value=False,
                                    help="Return detailed heat loss breakdown.")
        add_neighbour_losses = st.checkbox("Add Neighbour Losses", value=False,
                                           help="Include heat loss to neighbours.")

    num_rooms = st.sidebar.number_input("Number of Rooms", min_value=1, value=1)
    room_type = ['Living', 'Kitchen', 'Bedroom', 'Laundry', 'Bathroom', 'Toilet', None]

    if heat_loss_area_estimation == 'fromFloorArea':
        room_data = pd.DataFrame({
            "Room #": [i + 1 for i in range(num_rooms)],
            "Indoor Temp (°C)": [20.0] * num_rooms,
            "Floor Area (m²)": [50.0] * num_rooms,
            "Walls external": [2] * num_rooms,
            "Room Type": ["Living"] * num_rooms,
            "On Ground": [False] * num_rooms,
            "Under Roof": [False] * num_rooms
        })
    else:
        room_data = pd.DataFrame({
            "Room #": [i + 1 for i in range(num_rooms)],
            "Indoor Temp (°C)": [20.0] * num_rooms,
            "Exposed Perimeter (m)": [20.0] * num_rooms,
            "Neighbour Perimeter (m)": [10.0] * num_rooms,
            "Room Type": ["Living"] * num_rooms,
            "On Ground": [False] * num_rooms,
            "Under Roof": [False] * num_rooms
        })

    st.header("Room-Specific Parameters")

    edited_room_data = st.data_editor(
        room_data,
        key='editable_table',
        use_container_width=True,
        hide_index=True,
        column_config={
            'Room #': st.column_config.NumberColumn("Room", format="%d", width="small"),
            'Indoor Temp (°C)': st.column_config.NumberColumn('T indoor (°C)', format="%.1f"),
            'Floor Area (m²)': st.column_config.NumberColumn('Floor A (m²)', format="%.2f"),
            'Exposed Perimeter (m)': st.column_config.NumberColumn("Exposed Perimeter (m)", format="%.2f"),
            'Neighbour Perimeter (m)': st.column_config.NumberColumn("Neighbour Perimeter (m)", format="%.2f"),
            'Room Type': st.column_config.SelectboxColumn("Type",
                                                          options=room_type),
            'On Ground': st.column_config.CheckboxColumn("On Ground"),
            'Under Roof': st.column_config.CheckboxColumn("Under Roof"),
            'Walls external': st.column_config.NumberColumn("Walls outdoor", format="%.2f",
                                                            min_value=0.0, max_value=4.0, step=1.0),
        }
    )
    if st.sidebar.button("Calculate Heat Loss for All Rooms"):
        room_results = []
        for idx, row in edited_room_data.iterrows():
            calculator = RoomLoadCalculator(
                floor_area=row.get("Floor Area (m²)", 0.0),
                uw=uw,
                u_roof=u_roof,
                u_ground=u_ground,
                v_system=v_system,
                v50=v50,
                tin=row["Indoor Temp (°C)"],
                tout=tout,
                neighbour_t=neighbour_t,
                un=un,
                lir=lir,
                heat_loss_area_estimation=heat_loss_area_estimation,
                ventilation_calculation_method=ventilation_calculation_method,
                exposed_perimeter=row.get("Exposed Perimeter (m)", 0.0),
                on_ground=row["On Ground"],
                under_roof=row["Under Roof"],
                add_neighbour_losses=add_neighbour_losses,
                neighbour_perimeter=row.get("Neighbour Perimeter (m)", 0.0),
                room_type=row["Room Type"],
                wall_height=wall_height,
                wall_outside=row.get("Walls external", 0),
                return_detail=return_detail
            )
            result = calculator.compute()
            if return_detail:
                room_results.append({
                    "Room": row["Room #"],
                    "Total Heat Loss (W)": result['totalHeatLoss'],
                    "Transmission Loss (W)": result['transmissionHeatLoss'],
                    "Ventilation Loss (W)": result['ventilationHeatLoss'],
                    "Infiltration Loss (W)": result['infiltrationHeatLoss'],
                    "Neighbour Loss (W)": result['neighbourLosses']
                })
            else:
                room_results.append({
                    "Room": row["Room #"],
                    "Total Heat Loss (W)": result
                })

        df_results = pd.DataFrame(room_results)
        st.subheader("Heat Loss Results")
        st.dataframe(df_results, hide_index=True)


if __name__ == "__main__":
    main()