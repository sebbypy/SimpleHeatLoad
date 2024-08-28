import json
import pytest

from simpleLoadModel import RoomLoadCalculator


@pytest.fixture
def load_test_data():
    # Load the JSON test data
    with open('test_building_data.json', 'r') as file:
        return json.load(file)

def test_roomload_calculator():
    floorArea = 10
    Uw = 0.24
    Uroof = 0.24
    Uground = 0.7
    v50 = 1
    Tin = 20
    Tout = -7
    vSystem = 'C'

    result = 597.23
    test1 = RoomLoadCalculator(floor_area=floorArea, uw=Uw, u_roof=Uroof, u_ground=Uground, v_system=vSystem, v50=v50,
                               tin=Tin, tout=Tout,
                               neighbour_t=18,
                               lir=0.2,
                               heat_loss_area_estimation='fromFloorArea',
                               exposed_perimeter=0,
                               on_ground=True,
                               under_roof=False,
                               add_neighbour_losses=False,
                               neighbour_perimeter=0,
                               room_type=None).compute()

    assert result == pytest.approx(test1, rel=1e-2)

    result = 506.36
    test2 = RoomLoadCalculator(floor_area=floorArea, uw=Uw, u_roof=Uroof, u_ground=Uground, v_system='D', v50=v50,
                               tin=24, tout=Tout,
                               neighbour_t=18,
                               lir=0.2,
                               heat_loss_area_estimation='fromFloorArea',
                               exposed_perimeter=0,
                               on_ground=False,
                               under_roof=True,
                               add_neighbour_losses=True,
                               neighbour_perimeter=0,
                               room_type='Bathroom').compute()

    assert result == pytest.approx(test2, rel=1e-2)

    result = 576.69
    test3 = RoomLoadCalculator(floor_area=floorArea, uw=Uw, u_roof=Uroof, u_ground=Uground, v_system='D', v50=v50,
                               tin=24, tout=Tout,
                               neighbour_t=18,
                               lir=0.2,
                               heat_loss_area_estimation='fromExposedPerimeter',
                               exposed_perimeter=8,
                               on_ground=False,
                               under_roof=True,
                               add_neighbour_losses=True,
                               neighbour_perimeter=8,
                               room_type='Bathroom').compute()

    assert result == pytest.approx(test3, rel=1e-2)


def test_multiple_room(load_test_data):
    Uw = 0.24
    Uroof = 0.24
    Uground = 0.7
    Un = 2
    v50 = 6
    Tout = -7
    Tneighbour = 18
    vSystem = 'C'

    room_data = load_test_data["building"]["rooms"]
    total_heat_loss = 0
    for room in room_data:
        calculator = RoomLoadCalculator(
            floor_area=room["floor_area"],
            uw=Uw,
            u_roof=Uroof,
            u_ground=Uground,
            v_system=vSystem,
            v50=v50,
            tin=room["tin"],
            tout=Tout,
            neighbour_t=Tneighbour,
            un=Un,
            heat_loss_area_estimation='fromFloorArea',
            on_ground=room["on_ground"],
            under_roof=room["under_roof"],
            room_type=room["room_type"],
        )

        result = calculator.compute()
        total_heat_loss += float(result)
    assert pytest.approx(total_heat_loss, rel=1e-2) == 6400.74


def test_glass_calculator():
    floorArea = 10
    Uw = 0.24
    Uroof = 0.24
    Uground = 0.7
    v50 = 1
    Tin = 20
    Tout = -7
    vSystem = 'C'
    u_glass = 1

    result = 597.23 + (17.07 * 0.1* 1 * 27) - (17.07 * 0.1 * 0.24 *27)
    test1 = RoomLoadCalculator(floor_area=floorArea, uw=Uw, u_roof=Uroof, u_ground=Uground, v_system=vSystem, v50=v50,
                               tin=Tin, tout=Tout,
                               neighbour_t=18,
                               lir=0.2,
                               window=True,
                               u_glass=u_glass,
                               heat_loss_area_estimation='fromFloorArea',
                               exposed_perimeter=0,
                               on_ground=True,
                               under_roof=False,
                               add_neighbour_losses=False,
                               neighbour_perimeter=0,
                               room_type=None).compute()

    assert result == pytest.approx(test1, rel=1e-2)