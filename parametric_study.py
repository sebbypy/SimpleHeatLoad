import json
from typing import Dict
import plotly.graph_objs as go

from simpleLoadModel import RoomLoadCalculator

with open('buildings.json') as data:
    building_data = json.load(data)


# Function to perform heat loss calculation for each room
def perform_parametric_study(building: Dict[str, any], room: Dict[str, any]) -> Dict[str, float]:
    building_params = building['building_params'][0]
    calculator = RoomLoadCalculator(
        floor_area=room['floor_area'],
        uw=building_params['Uw'],
        u_roof=building_params['Uroof'],
        u_ground=building_params['Uground'],
        v_system=building_params['vSystem'],
        wall_outside=room['wall_outside'],
        v50=building_params['v50'],
        tin=room['tin'],
        tout=building_params['Tout'],
        neighbour_t=building_params['Tneighbour'],
        un=building_params['Un'],
        exposed_perimeter=room['exposed_perimeter'],
        on_ground=room['on_ground'],
        under_roof=room['under_roof'],
        room_type=room.get('room_type', None)
    )

    # Calculate heat loss using 'fromFloorArea'
    calculator.heat_loss_area_estimation = 'fromFloorArea'
    heat_loss_floor_area = calculator.compute()

    # Calculate heat loss using 'fromExposedPerimeter'
    calculator.heat_loss_area_estimation = 'fromExposedPerimeter'
    heat_loss_exposed_perimeter = calculator.compute()

    calculator.heat_loss_area_estimation = 'fromFloorArea'
    calculator.ventilation_calculation_method = 'NBN-D-50-001'
    ventilation_nbn = calculator.compute()

    calculator.window = True
    calculator.heat_loss_area_estimation = 'fromFloorArea'
    calculator.u_glass = building_params['u_glass']
    calculator.ventilation_calculation_method = 'simple'
    window = calculator.compute()

    return {
        'heat_loss_floor_area': heat_loss_floor_area,
        'heat_loss_exposed_perimeter': heat_loss_exposed_perimeter,
        'ventilation_NBN': ventilation_nbn,
        'windows': window

    }


# Prepare data for plotting
def prepare_plot_data(building_name, building_data):
    floor_area_losses = []
    exposed_perimeter_losses = []
    detailed_losses18 = []
    detailed_losses10 = []
    ventilation_nbn = []
    windows = []
    room_names = []

    for i, room in enumerate(building_data['rooms']):
        heat_losses = perform_parametric_study(building_data, room)
        room_name = f"{room['room_type'].capitalize()} {i + 1}"

        floor_area_losses.append(heat_losses['heat_loss_floor_area'])
        exposed_perimeter_losses.append(heat_losses['heat_loss_exposed_perimeter'])
        detailed_losses18.append(
            building_data['heat_losses_detailed'][i]['neighbor18'])
        detailed_losses10.append(
            building_data['heat_losses_detailed'][i]['neighbor10'])
        room_names.append(room_name)
        ventilation_nbn.append(heat_losses["ventilation_NBN"])
        windows.append(heat_losses["windows"])

    return room_names, floor_area_losses, exposed_perimeter_losses, detailed_losses18, detailed_losses10, ventilation_nbn, windows


# Generate plots for each building
for building_name, building_data in building_data.items():
    room_names, floor_area_losses, exposed_perimeter_losses, detailed_losses18, detailed_losses10, ventilation_nbn, windows = prepare_plot_data(building_name,
                                                                                                 building_data)

    # Create the bar plot
    fig = go.Figure()

    # Add bars for each heat loss estimation method
    fig.add_trace(go.Bar(
        x=room_names,
        y=floor_area_losses,
        name='From Floor Area',
        marker_color='indianred'
    ))

    fig.add_trace(go.Bar(
        x=room_names,
        y=exposed_perimeter_losses,
        name='From Exposed Perimeter',
        marker_color='lightblue'
    ))

    fig.add_trace(go.Bar(
        x=room_names,
        y=detailed_losses18,
        name='Detailed Heat Loss18',
        marker_color='green'
    ))

    fig.add_trace(go.Bar(
        x=room_names,
        y=detailed_losses10,
        name='Detailed Heat Loss10',
        marker_color='yellow'
    ))

    fig.add_trace(go.Bar(
        x=room_names,
        y=ventilation_nbn,
        name='ventilation_NBN',
        marker_color='purple'
    ))

    fig.add_trace(go.Bar(
        x=room_names,
        y=windows,
        name='windows',
        marker_color='orange'
    ))

    # Update layout
    fig.update_layout(
        title=f"Heat Loss Comparison for {building_name.capitalize()}",
        xaxis=dict(title='Rooms'),
        yaxis=dict(title='Heat Loss (W)'),
        barmode='group'
    )

    # Show plot
    fig.show()