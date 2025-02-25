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
    wall_outdoor = 2

    result = 597.23
    test1 = RoomLoadCalculator(floor_area=floorArea, uw=Uw, u_roof=Uroof, u_ground=Uground, v_system=vSystem, v50=v50,
                               tin=Tin, tout=Tout,
                               neighbour_t=18,
                               lir=0.2,
                               wall_outside=wall_outdoor,
                               heat_loss_area_estimation='fromFloorArea',
                               exposed_perimeter=0,
                               on_ground=True,
                               under_roof=False,
                               add_neighbour_losses=False,
                               neighbour_perimeter=0,
                               room_type=None).compute()

    assert result == pytest.approx(test1, rel=1e-2)

    result = 668.81
    test2 = RoomLoadCalculator(floor_area=floorArea, uw=Uw, u_roof=Uroof, u_ground=Uground, v_system='D', v50=v50,
                               tin=24, tout=Tout,
                               neighbour_t=18,
                               lir=0.2,
                               wall_outside=wall_outdoor,
                               heat_loss_area_estimation='fromFloorArea',
                               exposed_perimeter=0,
                               on_ground=False,
                               under_roof=True,
                               add_neighbour_losses=True,
                               neighbour_perimeter=0,
                               room_type='Bathroom').compute()

    assert result == pytest.approx(test2, rel=1e-2)

    result = 766.29
    test3 = RoomLoadCalculator(floor_area=floorArea, uw=Uw, u_roof=Uroof, u_ground=Uground, v_system='D', v50=v50,
                               tin=24, tout=Tout,
                               neighbour_t=18,
                               lir=0.2,
                               wall_outside=wall_outdoor,
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

    result = 667.31
    test1 = RoomLoadCalculator(floor_area=floorArea, uw=Uw, u_roof=Uroof, u_ground=Uground, v_system=vSystem, v50=v50,
                               tin=Tin, tout=Tout,
                               neighbour_t=18,
                               lir=0.2,
                               window=True,
                               u_glass=u_glass,
                               wall_outside=2,
                               heat_loss_area_estimation='fromFloorArea',
                               exposed_perimeter=0,
                               on_ground=True,
                               under_roof=False,
                               add_neighbour_losses=False,
                               neighbour_perimeter=0,
                               room_type=None).compute()

    assert result == pytest.approx(test1, rel=1e-2)


def test_neighbor():
        floorArea = 10
        Uw = 0.24
        Uroof = 0.24
        Uground = 0.7
        v50 = 1
        Tin = 20
        Tout = -7
        vSystem = 'C'
        u_glass = 1
        walls_outside=2

        result = 735.61
        test1 = RoomLoadCalculator(floor_area=floorArea, uw=Uw, u_roof=Uroof, u_ground=Uground, v_system=vSystem,
                                   v50=v50,
                                   tin=Tin, tout=Tout,
                                   neighbour_t=18,
                                   lir=0.2,
                                   window=True,
                                   wall_outside=walls_outside,
                                   u_glass=u_glass,
                                   heat_loss_area_estimation='fromFloorArea',
                                   exposed_perimeter=0,
                                   on_ground=True,
                                   under_roof=False,
                                   add_neighbour_losses=True,
                                   neighbour_perimeter=0,
                                   room_type=None).compute()

        assert result == pytest.approx(test1, rel=1e-2)


def test_insulatedattic():
    floorArea = 10
    Uw = 0.24
    Uroof = 0.24
    Uground = 0.7
    v50 = 1
    Tin = 20
    Tout = -7
    Tattic = 10
    vSystem = 'C'
    u_glass = 1
    walls_outside = 2

    test1 = RoomLoadCalculator(floor_area=floorArea, uw=Uw, u_roof=Uroof, u_ground=Uground, v_system=vSystem,
                               v50=v50,
                               tin=Tin, tout=Tout, tattic=Tattic,
                               neighbour_t=18,
                               lir=0.2,
                               window=True,
                               wall_outside=walls_outside,
                               u_glass=u_glass,
                               heat_loss_area_estimation='fromFloorArea',
                               exposed_perimeter=0,
                               on_ground=False,
                               under_roof=False,
                               under_insulated_attic=True,
                               add_neighbour_losses=True,
                               neighbour_perimeter=0,
                               room_type=None).compute()
    result = 668.25
    assert result == pytest.approx(test1, rel=1e-2)

    test2 = RoomLoadCalculator(floor_area=floorArea, uw=Uw, u_roof=Uroof, u_ground=Uground, v_system=vSystem,
                               v50=v50,
                               tin=18, tout=Tout, tattic=Tattic,
                               neighbour_t=18,
                               lir=0.2,
                               window=True,
                               wall_outside=walls_outside,
                               u_glass=u_glass,
                               heat_loss_area_estimation='fromFloorArea',
                               exposed_perimeter=0,
                               on_ground=False,
                               under_roof=False,
                               under_insulated_attic=True,
                               add_neighbour_losses=True,
                               neighbour_perimeter=0,
                               room_type=None).compute()
    result = 505.87
    assert result == pytest.approx(test2, rel=1e-2)
