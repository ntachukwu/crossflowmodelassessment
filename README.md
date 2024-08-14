# Cross Flow Filtration Model

This Python package provides a cross-flow filtration model, simulating the filtration process using configurable parameters and models for membrane resistance and viscosity. It includes functionality for calculating permeate flow rates, flux, and running simulations with logging and validation of parameters. 

## Components

### Modules

- **MembraneResistanceModel**: Abstract base class for membrane resistance models.
- **SimplifiedResistanceModel**: Concrete implementation of a simplified membrane resistance model.
- **ViscosityModel**: Abstract base class for viscosity models.
- **WaterViscosityModel**: Concrete implementation assuming constant viscosity of water.
- **CrossFlowFiltrationModel**: Core class for simulating the cross-flow filtration process.
- **CompletedSimulation**: Data class representing the results of a simulation.

### Key Classes


#### `SimplifiedResistanceModel`
Implements a simplified membrane resistance model using predefined coefficients.

**Methods:**
- `calculate_resistance(time: timedelta) -> float`: Calculates resistance based on time.

#### `WaterViscosityModel`
Assumes constant viscosity of water.

**Methods:**
- `calculate_viscosity() -> float`: Returns the constant viscosity of water.

#### `CompletedSimulation`
Data class holding the results of the simulation.

**Attributes:**
- `final_permeate_volume`: The final volume of permeate collected (L).
- `final_retentate_volume`: The final volume of retentate (L).
- `final_concentration`: The final concentration of the retentate.
- `time`: The total simulation time (hours).

#### `CrossFlowFiltrationModel`
Simulates the cross-flow filtration process.

**Initialization Arguments:**
- `volume` (float): Initial volume of the input mixture (L).
- `concentration` (float): Initial concentration of the protein (g/L).
- `tmp` (float): Trans Membrane Pressure (Pa).
- `membrane_area` (float): Membrane area (m²).
- `mwco` (float): Molecular Weight Cut Off (Da).
- `concentration_factor` (float): Target concentration factor.
- `termination_criteria` (Optional[TerminationCriteria]): Termination criteria other than concentration factor
- `resistance_model` (MembraneResistanceModel, optional): Model for membrane resistance (default: `SimplifiedResistanceModel`).
- `viscosity_model` (ViscosityModel, optional): Model for viscosity (default: `WaterViscosityModel`).

**Methods:**
- `calculate_permeate_flow_rate(time: timedelta) -> float`: Calculates the permeate flow rate.
- `calculate_flux(time: timedelta) -> float`: Calculates the flux through the membrane.
- `current_concentration(current_volume: float) -> float`: Calculates the concentration based on the current volume.
- `run_simulation(time_step: timedelta = DEFAULT_TIME_STEP) -> CompletedSimulation`: Runs the simulation and returns the results.

**Termination Criteria:**
- Concentration factor is reached.
- Casein molecular weight exceeds MWCO.
- Custom termination conditions like maximum simulation time.

## Limitations and Future Work
This model provides a basic simulation of cross-flow filtration but includes some simplifications.
- **Membrane Resistance:** The current model uses a simplified representation of membrane resistance based solely on time. A more realistic model would consider factors like membrane fouling.
- **Concentration Dynamics:** The model simplifies concentration dynamics by assuming a sharp molecular weight cut-off. Future improvements could incorporate concentration polarization and membrane selectivity curves.
- **Mixture Complexity:** Currently, the model only handles water and a single solute (bovine casein). Expanding to multiple solutes and more complex mixtures (e.g., with suspended solids) would enhance the model's applicability.
- **Viscosity Changes**:** The model does not currently account for changes in viscosity due to changing solute concentrations.
- **Mixing:** Perfect mixing is assumed in the hold-up tank. Incorporating more realistic mixing models would improve accuracy.

## Installation

Clone repository and run test.

```bash
git clone git@github.com:ntachukwu/crossflowmodelassessment.git
cd crossflowmodelassessment
python3 test_cross_flow_model.py
cat cross_flow_model.log
```

## Usage

Here's an example of how to use the `CrossFlowFiltrationModel`:

```python
from core import CrossFlowFiltrationModel, CompletedSimulation

# Initialize the model
model = CrossFlowFiltrationModel(
    volume=1000.0,
    concentration=10.0,
    tmp=500000.0,
    membrane_area=5.0,
    mwco=10000.0,
    concentration_factor=5.0
)

# Run the simulation
simulation_result = model.run_simulation()

# Access results
print(f"Final Permeate Volume: {simulation_result.final_permeate_volume} L")
print(f"Final Retentate Volume: {simulation_result.final_retentate_volume} L")
print(f"Final Concentration: {simulation_result.final_concentration}")
print(f"Total Time: {simulation_result.time} hours")
```

## Logging

The script logs detailed information about the simulation process and any errors encountered. Logs are saved in `cross_flow_model.log`.

## Assumptions

Several assumptions were made while developing this solution. Some of them includes,
- All the assumptions made in the assessment document
- All equations in the document were assumed to be correct
- Some logging capabilities were added to demonstrate a good understanding of the concept and how crucial they can be to getting the best out of any automated system.
- Efforts where made to use modern design patterns to make the solution more adaptable, extensible, robost, and testable.
- All constants and variables were treated as python generic types and it was also assumed that all the variables can fit in memory.
- In the test, maximum time was used as termination criteria as the concentration factor might take a long time to run. 
- The test supplied with this implementation is very limited. But enough was done to show their importance in maintaining the solution in the long run.
- Comments and docstrings were added to explain some of the assumptions and show good documentation skills.
