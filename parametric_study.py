import json
from typing import Dict, List, Tuple
import plotly.graph_objs as go

from simpleLoadModel import RoomLoadCalculator

# Load building data
with open('buildings.json') as data:
    building_data = json.load(data)


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

    # Helper function to calculate heat loss
    def calculate_heat_loss(heat_loss_area_estimation: str, ventilation_calculation_method: str = None, window: bool = False) -> float:
        calculator.heat_loss_area_estimation = heat_loss_area_estimation
        if ventilation_calculation_method:
            calculator.ventilation_calculation_method = ventilation_calculation_method
        if window:
            calculator.window = True
            calculator.u_glass = building_params['u_glass']
        return calculator.compute()

    return {
        'heat_loss_floor_area': calculate_heat_loss('fromFloorArea'),
        'heat_loss_exposed_perimeter': calculate_heat_loss('fromExposedPerimeter'),
        'ventilation_NBN': calculate_heat_loss('fromFloorArea', 'NBN-D-50-001'),
        'windows': calculate_heat_loss('fromFloorArea', 'simple', True)
    }


def prepare_plot_data(building_data: dict) -> Tuple[List[str], List[float], List[float], List[float], List[float], List[float], List[float]]:
    room_names = [f"{room['room_type'].capitalize()} {i + 1}" for i, room in enumerate(building_data['rooms'])]
    heat_losses = [perform_parametric_study(building_data, room) for room in building_data['rooms']]

    floor_area_losses = [losses['heat_loss_floor_area'] for losses in heat_losses]
    exposed_perimeter_losses = [losses['heat_loss_exposed_perimeter'] for losses in heat_losses]
    ventilation_nbn = [losses['ventilation_NBN'] for losses in heat_losses]
    windows = [losses['windows'] for losses in heat_losses]

    detailed_losses18 = [building_data['heat_losses_detailed'][i]['neighbor18'] for i in range(len(building_data['rooms']))]
    detailed_losses10 = [building_data['heat_losses_detailed'][i]['neighbor10'] for i in range(len(building_data['rooms']))]

    return room_names, floor_area_losses, exposed_perimeter_losses, detailed_losses18, detailed_losses10, ventilation_nbn, windows


def generate_plots(building_name: str, building_data: Dict[str, any]):
    room_names, floor_area_losses, exposed_perimeter_losses, detailed_losses18, detailed_losses10, ventilation_nbn, windows = prepare_plot_data(building_data)

    fig = go.Figure()

    data = [
        ('From Floor Area', floor_area_losses, 'indianred'),
        ('From Exposed Perimeter', exposed_perimeter_losses, 'lightblue'),
        ('Detailed Heat Loss18', detailed_losses18, 'green'),
        ('Detailed Heat Loss10', detailed_losses10, 'yellow'),
        ('Ventilation NBN', ventilation_nbn, 'purple'),
        ('Windows', windows, 'orange')
    ]

    for name, y_values, color in data:
        fig.add_trace(go.Bar(x=room_names, y=y_values, name=name, marker_color=color))

    fig.update_layout(
        title=f"Heat Loss Comparison for {building_name.capitalize()}",
        xaxis=dict(title='Rooms'),
        yaxis=dict(title='Heat Loss (W)'),
        barmode='group'
    )

    fig.show()


for building_name, data in building_data.items():
    generate_plots(building_name, data)
