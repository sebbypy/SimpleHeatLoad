import numpy as np
from typing import Dict, Union, Optional


class RoomLoadCalculator:
    def __init__(self,
                 floor_area: float,
                 uw: float,
                 u_roof: float,
                 u_ground: float,
                 v_system: str,
                 v50: float = 6,
                 tin: float = 20,
                 tout: float = -7,
                 neighbour_t: float = 18,
                 un: float = 1.0,
                 lir: float = 0.2,
                 heat_loss_area_estimation: str = 'fromFloorArea',
                 ventilation_calculation_method: str = 'simple',
                 exposed_perimeter: float = 0,
                 on_ground: bool = False,
                 under_roof: bool = False,
                 add_neighbour_losses: bool = False,
                 neighbour_perimeter: float = 0,
                 room_type: Optional[str] = None,
                 wall_height: float = 2.7,
                 return_detail: bool = False):
        self.floor_area = floor_area
        self.uw = uw
        self.u_roof = u_roof
        self.u_ground = u_ground
        self.v_system = v_system
        self.v50 = v50
        self.tin = tin
        self.tout = tout
        self.neighbour_t = neighbour_t
        self.un = un
        self.lir = lir
        self.heat_loss_area_estimation = heat_loss_area_estimation
        self.ventilation_calculation_method = ventilation_calculation_method
        self.exposed_perimeter = exposed_perimeter
        self.on_ground = on_ground
        self.under_roof = under_roof
        self.add_neighbour_losses = add_neighbour_losses
        self.neighbour_perimeter = neighbour_perimeter
        self.room_type = room_type
        self.wall_height = wall_height
        self.return_detail = return_detail

    def compute(self) -> Union[float, Dict[str, float]]:
        delta_t = self.tin - self.tout
        heat_loss_areas = self.compute_heat_loss_areas()

        wall_heat_loss_area = heat_loss_areas['walls']
        neighbour_wall_area = heat_loss_areas['neighbours']
        ground_heat_loss_area = heat_loss_areas['ground']
        roof_heat_loss_area = heat_loss_areas['roof']
        neighbour_floor_area = heat_loss_areas['neighbourfloor']

        neighbour_losses = self.compute_neighbour_losses(neighbour_wall_area, neighbour_floor_area)

        ventilation_flows = self.get_ventilation_flows()
        ventilation_heat_loss = self.compute_ventilation_heat_loss(ventilation_flows, delta_t)

        infiltration_heat_loss = 0.34 * self.lir * self.v50 * (
                wall_heat_loss_area + roof_heat_loss_area + ground_heat_loss_area
        ) * delta_t

        transmission_heat_loss = (
                                         wall_heat_loss_area * self.uw + roof_heat_loss_area * self.u_roof +
                                         ground_heat_loss_area * self.u_ground
                                 ) * delta_t

        total_heat_loss = transmission_heat_loss + ventilation_heat_loss + infiltration_heat_loss + neighbour_losses

        return self.prepare_return(total_heat_loss, transmission_heat_loss, ventilation_heat_loss,
                                   infiltration_heat_loss, neighbour_losses)

    def compute_neighbour_losses(self, neighbour_wall_area: float, neighbour_floor_area: float) -> float:
        if self.add_neighbour_losses:
            return self.un * (self.tin - self.neighbour_t) * (neighbour_wall_area + neighbour_floor_area)
        return 0

    def compute_ventilation_heat_loss(self, ventilation_flows: Dict[str, float], delta_t: float) -> float:
        inside_delta_t = max(0, self.tin - self.neighbour_t)
        return 0.34 * (ventilation_flows['flow from outside'] * delta_t +
                       ventilation_flows['flow from neighbour zones'] * inside_delta_t)

    def prepare_return(self, total_heat_loss: float, transmission_heat_loss: float,
                       ventilation_heat_loss: float, infiltration_heat_loss: float,
                       neighbour_losses: float) -> Union[float, Dict[str, float]]:
        if self.return_detail:
            return {
                'totalHeatLoss': total_heat_loss,
                'transmissionHeatLoss': transmission_heat_loss,
                'ventilationHeatLoss': ventilation_heat_loss,
                'infiltrationHeatLoss': infiltration_heat_loss,
                'neighbourLosses': neighbour_losses,
            }
        return total_heat_loss

    def compute_heat_loss_areas(self) -> Dict[str, float]:
        if self.heat_loss_area_estimation == 'fromFloorArea':
            side = np.sqrt(self.floor_area)
            # maybe we should make the * 2  an input parameter depending on the room type like row house *1
            # towards outside while in detached house typically *2
            wall_heat_loss_area = side * self.wall_height * 2  # 2 walls toward outside
            neighbour_wall_area = side * self.wall_height * 2  # 2 neighbour walls
        elif self.heat_loss_area_estimation == 'fromExposedPerimeter':
            wall_heat_loss_area = self.exposed_perimeter * self.wall_height
            neighbour_wall_area = self.neighbour_perimeter * self.wall_height
        else:
            wall_heat_loss_area = neighbour_wall_area = 0

        ground_heat_loss_area = self.floor_area if self.on_ground else 0
        roof_heat_loss_area = self.floor_area if self.under_roof else 0
        neighbour_floor_area = 0 if ground_heat_loss_area else self.floor_area

        return {
            'walls': wall_heat_loss_area,
            'neighbours': neighbour_wall_area,
            'ground': ground_heat_loss_area,
            'roof': roof_heat_loss_area,
            'neighbourfloor': neighbour_floor_area,
        }

    def get_ventilation_flows(self) -> Dict[str, float]:
        if self.ventilation_calculation_method == 'simple':
            return self.simple_ventilation_flows()
        if self.ventilation_calculation_method == 'NBN-D-50-001':
            return self.detailed_ventilation_flows()
        return {'flow from outside': 0, 'flow from neighbour zones': 0}

    def simple_ventilation_flows(self) -> Dict[str, float]:
        ventilation_ach = {'C': 1, 'D': 0.3}
        volume = self.floor_area * self.wall_height
        flow = volume * ventilation_ach[self.v_system]
        return {'flow from outside': flow, 'flow from neighbour zones': 0}

    def detailed_ventilation_flows(self) -> Dict[str, float]:
        bounds = {
            'Living': {'min': 75, 'max': 150},
            'Kitchen': {'min': 50, 'max': 75},
            'Bedroom': {'min': 25, 'max': 72},
            'Laundry': {'min': 50, 'max': 75},
            'Bathroom': {'min': 50, 'max': 150},
            'Toilet': {'min': 25, 'max': 25},
            None: {'min': 0, 'max': 150},
        }

        nom_flow = 3.6 * self.floor_area
        nom_flow = max(min(nom_flow, bounds[self.room_type]['max']), bounds[self.room_type]['min'])

        if self.room_type in ['Living', 'Bedroom', 'Bureau', None]:
            flow_from_outside = nom_flow
            if self.v_system == 'D':
                flow_from_outside *= 0.3
            return {'flow from outside': flow_from_outside, 'flow from neighbour zones': 0}
        return {'flow from outside': 0, 'flow from neighbour zones': nom_flow}