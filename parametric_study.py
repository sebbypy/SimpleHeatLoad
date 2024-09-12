import json
from typing import Dict, List, Tuple
import plotly.graph_objs as go

from simpleLoadModel import RoomLoadCalculator


with open('buildings.json') as data:
    building_data = json.load(data)


def perform_parametric_study(building: Dict[str, any], room: Dict[str, any], wall_outside_values: List[int]) -> Dict[
    str, List[float]]:
    building_params = building['building_params'][0]
    results = {
        'heat_loss_floor_area': [],
        'heat_loss_exposed_perimeter': [],
        'ventilation_NBN': [],
        'windows': [],
        'neighbor_losses': []
    }

    for wall_outside in wall_outside_values:
        calculator = RoomLoadCalculator(
            floor_area=room['floor_area'],
            uw=building_params['Uw'],
            u_roof=building_params['Uroof'],
            u_ground=building_params['Uground'],
            v_system=building_params['vSystem'],
            wall_outside=wall_outside,
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

        def calculate_heat_loss(heat_loss_area_estimation: str, ventilation_calculation_method: str = None,
                                window: bool = False, add_neighbor_losses: bool = False) -> float:
            calculator.heat_loss_area_estimation = heat_loss_area_estimation
            if ventilation_calculation_method:
                calculator.ventilation_calculation_method = ventilation_calculation_method
            if window:
                calculator.window = True
                calculator.u_glass = building_params['u_glass']
            if add_neighbor_losses:
                calculator.add_neighbour_losses = True
            return calculator.compute()

        results['heat_loss_floor_area'].append(calculate_heat_loss('fromFloorArea'))
        results['heat_loss_exposed_perimeter'].append(calculate_heat_loss('fromExposedPerimeter'))
        results['ventilation_NBN'].append(calculate_heat_loss('fromFloorArea', 'NBN-D-50-001'))
        results['windows'].append(calculate_heat_loss('fromFloorArea', 'simple', True))
        results['neighbor_losses'].append(
            calculate_heat_loss('fromFloorArea', 'simple', window=True, add_neighbor_losses=True))

    return results


def prepare_plot_data(building_data: dict, wall_outside_values: List[int]) -> Tuple[
    List[str], Dict[str, List[List[float]]], List[float], List[float]]:
    room_type_counts = {}
    room_names = []
    all_heat_losses = {
        'heat_loss_floor_area': [],
        'heat_loss_exposed_perimeter': [],
        'ventilation_NBN': [],
        'windows': [],
        'neighbor_losses': []
    }

    for room in building_data['rooms']:
        room_type = room['room_type'].capitalize()
        if room_type not in room_type_counts:
            room_type_counts[room_type] = 1
        else:
            room_type_counts[room_type] += 1
        if room_type_counts[room_type] > 1:
            room_name = f"{room_type} {room_type_counts[room_type]}"
        else:
            room_name = room_type

        room_names.append(room_name)
        heat_losses = perform_parametric_study(building_data, room, wall_outside_values)

        for key in all_heat_losses.keys():
            all_heat_losses[key].append(heat_losses[key])

    detailed_losses18 = [building_data['heat_losses_detailed'][i]['neighbor18'] for i in
                         range(len(building_data['rooms']))]
    detailed_losses10 = [building_data['heat_losses_detailed'][i]['neighbor10'] for i in
                         range(len(building_data['rooms']))]

    return room_names, all_heat_losses, detailed_losses18, detailed_losses10


def generate_plots(building_name: str, building_data: Dict[str, any], wall_outside_values: List[int]):
    room_names, all_heat_losses, detailed_losses18, detailed_losses10 = prepare_plot_data(building_data,
                                                                                          wall_outside_values)
    fig = go.Figure()
    for idx, wall_outside in enumerate(wall_outside_values):
        data = [
            (
            f'From Floor Area (Wall Outside {wall_outside})', [x[idx] for x in all_heat_losses['heat_loss_floor_area']],
            'indianred'),
            (f'From Exposed Perimeter (Wall Outside {wall_outside})',
             [x[idx] for x in all_heat_losses['heat_loss_exposed_perimeter']], 'lightblue'),
            (f'Ventilation NBN (Wall Outside {wall_outside})', [x[idx] for x in all_heat_losses['ventilation_NBN']],
             'purple'),
            (f'Windows (Wall Outside {wall_outside})', [x[idx] for x in all_heat_losses['windows']], 'orange'),
            (f'Neighbor (Wall Outside {wall_outside})', [x[idx] for x in all_heat_losses['neighbor_losses']], 'red')
        ]

        for name, y_values, color in data:
            fig.add_trace(go.Bar(x=room_names, y=y_values, name=name, marker_color=color))

    fig.add_trace(go.Bar(x=room_names, y=detailed_losses18, name='Detailed Heat Loss18', marker_color='green'))
    fig.add_trace(go.Bar(x=room_names, y=detailed_losses10, name='Detailed Heat Loss10', marker_color='yellow'))

    fig.update_layout(
        title=f"Heat Loss Comparison for {building_name.capitalize()}",
        xaxis=dict(title='Rooms'),
        yaxis=dict(title='Heat Loss (W)'),
        barmode='group'
    )

    fig.show()


wall_outside_values = [1, 2, 3]
for building_name, data in building_data.items():
    generate_plots(building_name, data, wall_outside_values)
