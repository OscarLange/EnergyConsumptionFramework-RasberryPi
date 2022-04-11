#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

// struct for the information relating to the utilization of a cpu
struct Cpu_usage {
	long int idle, working, wait_io, interrupt;
};

void print_cpu_usage(struct Cpu_usage cpu_usage){
	printf("Idle: %ld, Working %ld, Wait on IO: %ld, interrupt: %ld \n", cpu_usage.idle, cpu_usage.working, cpu_usage.wait_io, cpu_usage.interrupt);
}

//int read_top_cmd()
//{
//	system("top -bn 1 | awk '{print $9,$10,$NF}' >> topOutput.txt");
//	system("echo '---------- END OF OUTPUT -----------' >> topOutput.txt");
//	return 0;
//}

/*
 * Read the proc file and retrieve relevant information
 */
struct Cpu_usage *read_proc_stat(long num_proc){
	char* token;
	const char divisor[2] = " ";
	char str [100];
	//create array of struct per 1 cpu and one for overall
	struct Cpu_usage *cpu_usages = malloc(sizeof(struct Cpu_usage) * (num_proc+1));

	//open proc stat file
	FILE* proc_stats = fopen("/proc/stat","r");
	
	//loop through every line in file
	int line = 0;
	while(fgets(str, sizeof(str), proc_stats)){
		//first word is just cpu enumeration
		token = strtok(str,divisor);
		
		//if the first word is not intr and not NULL then retrieve values
		if(token != NULL && strcmp(token, "intr") != 0){	
			//store usage statistics

			//user processes time
			token = strtok(NULL, divisor);
			cpu_usages[line].working = atoi(token);
			
			//nice processes time
			token = strtok(NULL, divisor);
			cpu_usages[line].working += atoi(token);

			//system processes time
			token = strtok(NULL, divisor);
			cpu_usages[line].working += atoi(token);
			
			//idle time
			token = strtok(NULL, divisor);
			cpu_usages[line].idle = atoi(token);
			
			//iowait time
			token = strtok(NULL, divisor);
			cpu_usages[line].wait_io = atoi(token);
			
			//interrupts time
			token = strtok(NULL, divisor);
			cpu_usages[line].interrupt = atoi(token);
			
			//soft interrupts time
			token = strtok(NULL, divisor);
			cpu_usages[line].interrupt += atoi(token);
			line++;		
		} else {
			break;
		}
	}
	fclose(proc_stats);
	return cpu_usages;
}

long get_number_of_processors(){
	return sysconf(_SC_NPROCESSORS_ONLN);
}

int main(void)
{
	long number_of_processors = get_number_of_processors();
	struct Cpu_usage *cpu_usage = read_proc_stat(number_of_processors);
	for(int i = 0; i <= number_of_processors; i++){
		print_cpu_usage(cpu_usage[i]);
	}
	return 0;
}
