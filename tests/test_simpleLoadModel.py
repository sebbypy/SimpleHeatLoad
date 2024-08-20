from simpleLoadModel import RoomLoadCalculator
import pytest


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
    test1 = RoomLoadCalculator(floorArea, Uw, Uroof, Uground, vSystem, v50, Tin, Tout,
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
    test2 = RoomLoadCalculator(floorArea, Uw, Uroof, Uground, v_system='D', v50=v50, tin=24, tout=Tout,
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
    test3 = RoomLoadCalculator(floorArea, Uw, Uroof, Uground, v_system='D', v50=v50, tin=24, tout=Tout,
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
