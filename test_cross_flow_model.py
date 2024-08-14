import unittest
from core import CrossFlowFiltrationModel, SimplifiedResistanceModel, WaterViscosityModel, CompletedSimulation, MaxSimulationTimeTermination
from core import validate_parameter

from datetime import timedelta

ONE_HOUR = timedelta(hours=1)
TERMINATION_CRITERIA_FOR_TEST = MaxSimulationTimeTermination(5*ONE_HOUR)


class TestCrossFlowFiltrationModel(unittest.TestCase):
    
    def setUp(self):
        """
        This method runs before each test. We use it to set up the environment
        needed for each test, including creating instances of the objects we're testing.
        """
        self.volume = 1 
        self.concentration = 10.0
        self.tmp = 100000.0
        self.membrane_area = 5.0 
        self.mwco = 40000.0
        self.concentration_factor = 2
        self.termination_criteria = TERMINATION_CRITERIA_FOR_TEST
        self.model = CrossFlowFiltrationModel(
            volume=self.volume,
            concentration=self.concentration,
            tmp=self.tmp,
            membrane_area=self.membrane_area,
            mwco=self.mwco,
            concentration_factor=self.concentration_factor,
            termination_criteria=self.termination_criteria,
            resistance_model=SimplifiedResistanceModel(),
            viscosity_model=WaterViscosityModel()
        )

    def test_calculate_permeate_flow_rate_with_time_in_hours(self):
        """
        Test the calculation of the permeate flow rate.
        """
        time = 2*ONE_HOUR  # Arbitrary time step of 2 hours
        flow_rate = self.model.calculate_permeate_flow_rate(time)
        self.assertGreater(flow_rate, 0, "Permeate flow rate should be positive")


    def test_run_simulation(self):
        """
        Test the entire simulation to check if it runs without errors and returns expected results.
        """
        simulation_result = self.model.run_simulation(time_step=ONE_HOUR)
        self.assertIsInstance(simulation_result, CompletedSimulation)
        self.assertGreater(simulation_result.final_permeate_volume, 0, "Permeate volume should be positive")
        self.assertGreater(simulation_result.final_retentate_volume, 0, "Retentate volume should be positive")
        self.assertGreater(simulation_result.final_concentration, 0, "Final concentration should be positive")
        self.assertGreater(simulation_result.time, timedelta(0), "Simulation time should be positive")
    
    def test_validate_parameter(self):
        """
        Test the validate_parameter function.
        """
        # Test a valid parameter
        result = validate_parameter('Test Parameter', 10, positive=True)
        self.assertEqual(result, 10, "Valid parameter did not pass validation.")

        # Test a negative parameter where positive is required
        with self.assertRaises(ValueError):
            validate_parameter('Test Parameter', -10, positive=True)

        # Test a parameter below the minimum range
        with self.assertRaises(ValueError):
            validate_parameter('Test Parameter', 5, min_value=10, max_value=20)
        
        # Test a parameter above the maximum range
        with self.assertRaises(ValueError):
            validate_parameter('Test Parameter', 25, min_value=10, max_value=20)

    def test_resistance_model_without_time(self):
        with self.assertRaises(TypeError):
            self.model.resistance_model.calculate_resistance()

    def test_viscosity_model(self):
        viscosity = self.model.viscosity_model.calculate_viscosity()
        self.assertEqual(viscosity, 0.001, "Viscosity model returned incorrect value")

if __name__ == '__main__':
    unittest.main()
