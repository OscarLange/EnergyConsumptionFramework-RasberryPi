#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "Struct.h"


/*
 * Small helper function for debugging
 */
void print_cpu_usage(struct Cpu_usage cpu_usage){
	printf("Idle: %ld, Working %ld, Wait on IO: %ld, interrupt: %ld \n", 
			cpu_usage.idle, cpu_usage.working, 
			cpu_usage.wait_io, cpu_usage.interrupt);
}

//int read_top_cmd()
//{
//	system("top -bn 1 | awk '{print $9,$10,$NF}' >> topOutput.txt");
//	system("echo '---------- END OF OUTPUT -----------' >> topOutput.txt");
//	return 0;
//}

/*
 * Read the ip adress and port from file
 */
struct Server_info *read_server_info(){
	char* token;
	const char divisor[2] = ":";
	char str [100];
	//create struct for server adress
	struct Server_info *server_info = malloc(sizeof(struct Server_info));

	//open proc stat file
	FILE* config = fopen("config","r");
	
	//loop through every line in file
	int line = 0;
	while(fgets(str, sizeof(str), config)){
		//first word is category
		token = strtok(str,divisor);
		//save ip and port
		if(token != NULL){
			if(strcmp(token, "ip") == 0){
				token = strtok(NULL, divisor);
				server_info->server_ip = malloc(max_ipv4_length);
				strncpy(server_info->server_ip, token, max_ipv4_length);
			}
			if(strcmp(token, "port") == 0){
				token = strtok(NULL, divisor);
				server_info->port = atoi(token);
			}
		}
	}
	fclose(config);
	return server_info;
}

/*
 * Read the proc file and get the release date number to identify rasberry
 */
char *read_release_number(){
	char* token;
	//return value
	char* serial = malloc(max_revision);
	const char divisor[2] = " \t";
	char str [100];

	//open proc stat file
	FILE* proc_cpuinfo = fopen("/proc/cpuinfo","r");
	
	//loop through every line in file
	int line = 0;
	while(fgets(str, sizeof(str), proc_cpuinfo)){
		//first word is category
		token = strtok(str,divisor);
		//if the first word is revision then retrieve number
		if(token != NULL && strcmp(token, "Revision") == 0){	
			//retrieve release number
			token = strtok(NULL, divisor);
			token = strtok(NULL, divisor);
			strncpy(serial, token, max_revision);
		}
	}
	fclose(proc_cpuinfo);
	return serial;
}

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

/*
 * Calculating the cpu utilization from to measurements
 */
long double calculate_cpu_utilization(struct Cpu_usage old, struct Cpu_usage new){
	//calculate difference of time measurements
	long working_time = new.working - old.working;
	long non_working_time = (new.idle - old.idle) + (new.wait_io - old.wait_io) + (new.interrupt -old.interrupt);
	// return (working time / time overall) 
	printf("working time: %ld, waiting time: %ld \n", working_time, non_working_time);
	return ((long double) working_time / (working_time + non_working_time)) * 100;
}

/*
 * Return the number of processors on the chip
 */
long get_number_of_processors(){
	return sysconf(_SC_NPROCESSORS_ONLN);
}

/*
 * Main function to collect statistic
 * time_span in s for linux and ms for windows
 */
void collect_statistics(int time_span, long num_of_proc) {
	
	struct Cpu_usage *cpu_usage_old = read_proc_stat(num_of_proc);
	sleep(time_span);
	struct Cpu_usage *cpu_usage_new = read_proc_stat(num_of_proc);

	for(int i = 0; i <= num_of_proc; i++){
		print_cpu_usage(cpu_usage_old[i]);
		print_cpu_usage(cpu_usage_new[i]);
		printf("cpu utilization: %lf", calculate_cpu_utilization(cpu_usage_old[i], cpu_usage_new[i]));
	}
}

int main(void)
{
	//long number_of_processors = get_number_of_processors();
	//collect_statistics(10, number_of_processors);
	//printf("Revision: %s",read_release_number());
	struct Server_info *server_info = read_server_info();
	printf("Server ip: %s | Server port %d", server_info->server_ip, server_info->port);
	return 0;
}
