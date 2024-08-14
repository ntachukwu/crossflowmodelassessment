from abc import ABC, abstractmethod
from collections import namedtuple
from datetime import timedelta
from typing import Optional

import logging

# Configure logging
logging.basicConfig(filename='cross_flow_model.log', 
                    level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define named tuples for ranges
MWCORange = namedtuple('MWCORange', ['min', 'max'])
TMPRange = namedtuple('TMPRange', ['min', 'max'])
ConcentrationFactorRange = namedtuple('ConcentrationFactorRange', ['min', 'max'])

# Define one hour
ONE_HOUR = timedelta(hours=1)

# Define typical ranges using named tuples
TYPICAL_RANGES = {
    'MWCO': MWCORange(1_000, 500_000),  # Da
    'TMP': TMPRange(50_000, 700_000),   # Pa
    'Concentration_factor': ConcentrationFactorRange(2, 20) 
}
CASEIN_MOLECULAR_WEIGHT = 25107.0  # Da
DEFAULT_TIME_STEP = ONE_HOUR

class TerminationCriteria(ABC):
    @abstractmethod
    def check_termination(self, *args, **kwargs) -> bool:
        """Check if the simulation should terminate based on the current state."""
        pass

class MaxSimulationTimeTermination(TerminationCriteria):
    def __init__(self, max_time: timedelta):
        self.max_time = max_time

    def check_termination(self, current_running_time: timedelta) -> bool:
        is_terminatable = current_running_time >= self.max_time
        if is_terminatable:
            logging.info(f"Reached maximum simulation time of {self.max_time} h.")
        return is_terminatable
    
class MembraneResistanceModel(ABC):
    """"
    Abstract base class for membrane resistance models.
    """
    @abstractmethod
    def calculate_resistance(self, *args, **kwargs) -> float:
        """"
        Calculates the membrane resistance.
        Returns:
            float: Membrane resistance in m.
        """
        pass

    
class SimplifiedResistanceModel(MembraneResistanceModel):
    """
    Implements a simplified membrane resistance model.
    """

    TIME_COEFFICIENT_A = 0.13e12
    TIME_COEFFICIENT_B = 1.51e12
    TIME_EXPONENT = 0.4

    def calculate_resistance(self, time: timedelta) -> float:
        if time is not None:
            return self.TIME_COEFFICIENT_A + (self.TIME_COEFFICIENT_B * time.total_seconds()**self.TIME_EXPONENT) 
        # If time is not provided, you might need to handle this case
        # based on the other quantities available in kwargs
        raise NotImplementedError("Resistance calculation without time is not implemented yet.")
    
        

class ViscosityModel(ABC):
    """
    Abstract base class for viscosity models.
    """

    @abstractmethod
    def calculate_viscosity(self, *args, **kwargs) -> float:
        pass

class WaterViscosityModel(ViscosityModel):
    """
    Assumes constant viscosity of water.
    """

    WATER_VISCOSITY = 0.001

    def calculate_viscosity(self) -> float:
        return self.WATER_VISCOSITY
        
class CompletedSimulation:
    def __init__(self, final_permeate_volume, final_retentate_volume, final_concentration, time):
        self.final_permeate_volume = final_permeate_volume
        self.final_retentate_volume = final_retentate_volume
        self.final_concentration = final_concentration
        self.time = time

class CrossFlowFiltrationModel:
    """
    Initializes the CrossFlowModel with input parameters and dependencies.

    Args:
        volume (float): Volume of input mixture (L)
        concentration (float): Concentration of protein (g/L)
        tmp (float): Trans Membrane Pressure (Pa)
        membrane_area (float): Membrane area (m2)
        mwco (float): Molecular Weight Cut Off (Da)
        concentration_factor (float): Target concentration factor
        termination_criteria (Optional[TerminationCriteria]): Termination criteria other than concentration factor
        resistance_model (MembraneResistanceModel): Model for membrane resistance.
        viscosity_model (ViscosityModel): Model for viscosity.
    """

    def __init__(self, 
                 volume: float, 
                 concentration: float,
                 tmp: float,
                 membrane_area: float,
                 mwco: float,
                 concentration_factor: float,
                 termination_criteria: Optional[TerminationCriteria] = None,
                 resistance_model: MembraneResistanceModel = SimplifiedResistanceModel(),
                 viscosity_model: ViscosityModel = WaterViscosityModel()):

        self.initial_volume = validate_parameter('Volume', volume, positive=True)
        self.initial_concentration = validate_parameter('Concentration', concentration, positive=True)
        self.tmp = validate_parameter('TMP', tmp, 
                                         min_value=TYPICAL_RANGES['TMP'].min, 
                                         max_value=TYPICAL_RANGES['TMP'].max) 
        self.mwco = validate_parameter('MWCO', mwco, 
                                         min_value=TYPICAL_RANGES['MWCO'].min, 
                                         max_value=TYPICAL_RANGES['MWCO'].max)
        self.concentration_factor = validate_parameter('Concentration factor', concentration_factor,
                                                            min_value=TYPICAL_RANGES['Concentration_factor'].min, 
                                                            max_value=TYPICAL_RANGES['Concentration_factor'].max)
        
        
        self.membrane_area = membrane_area
        self.resistance_model = resistance_model
        self.viscosity_model = viscosity_model
        self.termination_criteria = termination_criteria


    def calculate_permeate_flow_rate(self, time: timedelta) -> float:
        """
        Calculates the permeate flow rate.

        Returns:
            float: Permeate flow rate (L/h). 
        """
        try:
            flux = self.calculate_flux(time)
            flow_rate = flux * self.membrane_area
            logging.info(f"Time: {time} h, Permeate flow rate: {flow_rate} L/h")
            return flow_rate
        except Exception as e:
            logging.error(f"Error calculating permeate flow rate: {e}")
            raise  e
        
    def calculate_flux(self, time: timedelta) -> float:
        try:
            resistance = self.resistance_model.calculate_resistance(time)
            viscosity = self.viscosity_model.calculate_viscosity()
            flux = self.tmp / (viscosity * resistance)
            logging.info(f"Time: {time}h, Flux: {flux} m3•h-1•m-2")
            return flux
        except Exception as e:
            logging.error(f"Error calculating permeate flux: {e}")
            raise e
    
    def current_concentration(self, current_volume):
        return self.initial_volume / current_volume




    def run_simulation(self, time_step: timedelta = DEFAULT_TIME_STEP) -> CompletedSimulation:
        """
        Args:
            time_step (timedelta, optional): The time step for each simulation iteration in hours.  Defaults to 1 hours. 
                                        A smaller time step results in a more accurate simulation but increases computation time.

        Returns:
            CompletedSimulation
        """

        logging.info("Simulation started with time_step: %s h, initial_volume: %s L, target_concentration_factor: %s",
                     time_step, self.initial_volume, self.concentration_factor)

        current_hold_up_volume = self.initial_volume
        current_concentration = 0
        current_permeate_volume = 0
        current_running_time = timedelta(0)

        while True:
            # Check for termination criteria
            if CASEIN_MOLECULAR_WEIGHT > self.mwco:
                logging.warning("Casein molecular weight exceeds MWCO. Simulation will terminate early.")
                break
            if current_concentration >= self.concentration_factor:
                logging.info(f"Concentration target reached {current_concentration}")
                break
            if self.termination_criteria and self.termination_criteria.check_termination(current_running_time):
                break

            permeate_flow_rate = self.calculate_permeate_flow_rate(current_running_time)

            delta_permeate_volume = permeate_flow_rate * time_step.total_seconds() / ONE_HOUR.total_seconds()
            current_permeate_volume += delta_permeate_volume
            current_hold_up_volume -= delta_permeate_volume
            current_running_time += time_step
            current_concentration = self.current_concentration(current_hold_up_volume)

            

            logging.info(
                "Time: %s, Permeate Volume: %s L, Hold-up Volume: %s L, Concentration: %s",
                current_running_time, current_permeate_volume, current_hold_up_volume, current_concentration
            )

        logging.info("Simulation completed. Final Permeate Volume: %s L, Final Hold-up Volume: %s L, "
                     "Final Concentration: %s, Total Time: %s",
                     current_permeate_volume, current_hold_up_volume, current_concentration, current_running_time)

        return CompletedSimulation(current_permeate_volume, current_hold_up_volume, current_concentration, current_running_time)

def validate_parameter(param_name, value, positive=False, min_value=None, max_value=None):
    """
    Validates a parameter against specified conditions.
    """
    if positive and value <= 0:
        raise ValueError(f"{param_name} must be a positive value.")
    if min_value is not None and value < min_value:
        raise ValueError(f"{param_name} is below the typical range: [{min_value}, {max_value}].")
    if max_value is not None and value > max_value:
        raise ValueError(f"{param_name} is above the typical range: [{min_value}, {max_value}].")
    return value

