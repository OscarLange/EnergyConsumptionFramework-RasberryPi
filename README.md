# EnergyConsumptionFramework-RasberryPi
The rasberry pi code for the energy consumption framework

## Measure Consumption
Execute command like this to collect stats:
python3 sample_power.py {num_iterations} {mode}

How often per configuration do you collect data
{num_iterations} => 0 1 2 3 4 5 ... 95 96 97 98 99 100

Just changes which files are written to
{mode} => training 0 test 1 debug 2 

{Freq} => 240 160 80

## Graph data
Use the functions described in graph.py 

## Data
First Try, test and training hold the collected metrics
Pictures holds the evaluation resullts visualized