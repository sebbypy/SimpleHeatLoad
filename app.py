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

    # Main Screen: Room-Specific Parameters
    room_data = []

    st.header("Room-Specific Parameters")

    for i in range(num_rooms):
        st.subheader(f"Room {i + 1} Settings")

        tin = st.number_input(f"Room {i + 1} - Indoor Temperature (°C)", value=20.0)

        if heat_loss_area_estimation == 'fromFloorArea':
            floor_area = st.number_input(f"Room {i + 1} - Floor Area (m²)", min_value=0.0, value=50.0)
            exposed_perimeter = 0.0
            neighbour_perimeter = 0.0
        else:
            exposed_perimeter = st.number_input(f"Room {i + 1} - Exposed Perimeter (m)", value=0.0)
            neighbour_perimeter = st.number_input(f"Room {i + 1} - Neighbour Perimeter (m)", value=0.0)
            floor_area = 0.0

        room_type = st.selectbox(f"Room {i + 1} - Room Type",
                                 options=[None, "Living", "Kitchen", "Bedroom", "Laundry", "Bathroom", "Toilet"])
        on_ground = st.checkbox(f"Room {i + 1} - On Ground", value=False)
        under_roof = st.checkbox(f"Room {i + 1} - Under Roof", value=False)

        room_data.append({
            "floor_area": floor_area,
            "tin": tin,
            "exposed_perimeter": exposed_perimeter,
            "neighbour_perimeter": neighbour_perimeter,
            "room_type": room_type,
            "on_ground": on_ground,
            "under_roof": under_roof,
        })

    # Calculate Button
    if st.sidebar.button("Calculate Heat Loss for All Rooms"):
        for idx, room in enumerate(room_data):
            st.subheader(f"Room {idx + 1} Heat Loss Calculation")

            calculator = RoomLoadCalculator(
                floor_area=room["floor_area"],
                uw=uw,
                u_roof=u_roof,
                u_ground=u_ground,
                v_system=v_system,
                v50=v50,
                tin=room["tin"],
                tout=tout,
                neighbour_t=neighbour_t,
                un=un,
                lir=lir,
                heat_loss_area_estimation=heat_loss_area_estimation,
                ventilation_calculation_method=ventilation_calculation_method,
                exposed_perimeter=room["exposed_perimeter"],
                on_ground=room["on_ground"],
                under_roof=room["under_roof"],
                add_neighbour_losses=add_neighbour_losses,
                neighbour_perimeter=room["neighbour_perimeter"],
                room_type=room["room_type"],
                wall_height=wall_height,
                return_detail=return_detail
            )
            result = calculator.compute()
            # for the multi-room show in a table for every room the heat loss and give the total heat loss building
            if return_detail:
                st.subheader("Total Heat Loss")
                st.write(f"{result['totalHeatLoss']:.2f} W")
                st.subheader("Detailed Heat Loss Breakdown")
                st.bar_chart(data={
                    'Transmission': result['transmissionHeatLoss'],
                    'Ventilation': result['ventilationHeatLoss'],
                    'Infiltration': result['infiltrationHeatLoss'],
                    'Neighbour': result['neighbourLosses']
                })
            else:
                st.subheader("Total Heat Loss")
                st.write(f"{result:.2f} W")


if __name__ == "__main__":
    main()
