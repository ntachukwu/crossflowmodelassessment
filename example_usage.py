from cross_flow_model.core import CrossFlowFiltrationModel, CompletedSimulation



def print_result(completed_simulation: CompletedSimulation):
    """
    Prints the simulation results.
    """
    print("Simulation Results:")
    print(f"  Total time in hours: {completed_simulation.time} h")
    print(f"  Final permeate volume: {completed_simulation.final_permeate_volume} L")
    print(f"  Final retentate volume: {completed_simulation.final_retentate_volume} L")
    print(f"  Concentration factor: {completed_simulation.final_concentration}")

def main():

    data = {
    "volume": 1.0,
    "concentration": 10.0,
    "tmp": 100000.0,
    "membrane_area": 222222222.0,
    "mwco": 10000.0,
    "concentration_factor": 5.0
}
    model = CrossFlowFiltrationModel(**data)
    sim = model.run_simulation()
    print_result(sim)

if __name__ == "__main__":
    main()