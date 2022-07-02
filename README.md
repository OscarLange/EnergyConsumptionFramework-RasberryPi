# EnergyConsumptionFramework-RasberryPi
The rasberry pi code for the energy consumption framework

Execute command like this:
python3 sample_power.py {Work} {Freq} {CPU_UTIL}

{Work} => SPIN_WORK 0 ADD_WORK 1 SUB_WORK 2 MUL_WORK 3 DIV_WORK 4
	            ADD_WORK_F 5 SUB_WORK_F 6 MUL_WORK_F 7 DIV_WORK_F 8

{Freq} => 240 160 80

{CPU_UTIL} => 0 1 2 3 4 5 ... 95 96 97 98 99 100
