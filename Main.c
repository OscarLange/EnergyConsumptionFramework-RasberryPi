#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <math.h>
#include "Struct.h"
#include "Socket.h"


/*
 * Small helper function for debugging
 */
void print_cpu_usage(struct Cpu_usage cpu_usage){
	printf("Idle: %ld, Working %ld, Wait on IO: %ld, interrupt: %ld \n", 
			cpu_usage.idle, cpu_usage.working, 
			cpu_usage.wait_io, cpu_usage.interrupt);
}


/*
 * Helper function to remove whitespaces
 */
void remove_whitespace(char* s) {
	char* d = s;
	do {
		while(*d == '\t' || *d == ' ') {
			++d;
		}
	} while (*s++ = *d++);
}

/*
 * Helper function to remove newlines
 */
void remove_newline(char* s) {
	char* d = s;
	do {
		while(*d == '\n') {
			++d;
		}
	} while (*s++ = *d++);
}

/*
 * Not currently in use but reads output of top
 */
void read_top_cmd() {
	system("top -bn 1 | awk '{print $9,$10,$NF}' >> topOutput.txt");
	system("echo '---------- END OF OUTPUT -----------' >> topOutput.txt");
}

/*
 * Read the ip adress and port from file
 */
struct Server_info *read_server_info(){
	char* token;
	const char divisor[2] = ":";
	char str [100];
	//create struct for server adress
	struct Server_info *server_info = malloc(sizeof(struct Server_info));

	//open proc stat file:
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
				remove_newline(token);
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
 * Read the proc file and get the release date id to identify rasberry
 */
char *read_release_id(){
	char* token;
	//return value
	char* serial = malloc(max_revision);
	const char divisor[2] = ":";
	char str [200];

	//open proc stat file
	FILE* proc_cpuinfo = fopen("/proc/cpuinfo","r");
	
	//loop through every line in file
	int line = 0;
	while(fgets(str, sizeof(str), proc_cpuinfo)){
		//remove whitespace
		remove_whitespace(str);
		//first word is category
		token = strtok(str,divisor);
		//if the first word is revision then retrieve number
		if(token != NULL && strcmp(token, "Revision") == 0){	
			//retrieve release number
			token = strtok(NULL, divisor);
			remove_newline(token);
			strncpy(serial, token, max_revision);
		}
	}
	fclose(proc_cpuinfo);
	return serial;
}

/*
 * Read the proc file and retrieve relevant information
 */
struct Cpu_usage *read_proc_stat(struct Cpu_usage *cpu_usages){
	char* token;
	const char divisor[2] = " ";
	char str [100];

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
void collect_statistics(int time_span, long num_of_proc, 
		struct Cpu_usage *cpu_usage_old, struct Cpu_usage *cpu_usage_new,
		long double *cpu_utilization) {

	cpu_usage_old = read_proc_stat(cpu_usage_old);
	sleep(time_span);
	cpu_usage_new = read_proc_stat(cpu_usage_new);

	for(int i = 0; i <= num_of_proc; i++){
		cpu_utilization[i] = calculate_cpu_utilization(cpu_usage_old[i], 
					cpu_usage_new[i]);
	}
}

/*
 * Small helper function to calculate the size needed
 * for combining a string with a long int in literal form
 */
size_t calculate_char_length(char* string, long int value) {
	size_t size = 0;
	if(value == 0){
		size += strlen(string) + 1;
	} else {
		size += strlen(string) + (int)(ceil(log10(value)) + 1);
	}
	return size;
}

/*
 * Create a json to send from cpu usage
 */
char *create_cpu_json(
		struct Cpu_usage old, struct Cpu_usage new, 
		long double cpu_utils, int index){	
	size_t size = 0;
	char *json1 = "{ Cpu: ";
	if(index == 0){
		size += strlen(json1) + 1;
	} else {
		size += strlen(json1) + (int)(ceil(log10(index)) + 1);
	}
	
	char *json2 = ", Utilization: ";
	//TODO replace max double long size == 50 to more accurate value
	size += strlen(json2) + 30;
	
	char *json3 = ", Idle: ";
	long int idle = new.idle - old.idle;
	size += calculate_char_length(json3, idle);

	char *json4 = ", Working: ";
	long int working = new.working - old.working;
	size += calculate_char_length(json4, working);
	
	char *json5 = ", Wait Io: ";
	long int wait_io = new.wait_io - old.wait_io;
	size += calculate_char_length(json5, wait_io);
	
	char *json6 = ", Interrupt: ";
	long int interrupt = new.interrupt - old.interrupt;
	size += calculate_char_length(json6, interrupt);
	
	char *json7 = "}";
	size += strlen(json7);

	char *buffer = malloc(size);
	sprintf(buffer, "%s%d%s%lf%s%ld%s%ld%s%ld%s%ld%s", 
			json1, index, 
			json2, cpu_utils, 
			json3, idle,
			json4, working,
			json5, wait_io,
			json6, interrupt,
			json7);
	return buffer;
}

/*
 * Wrapper for send info function
 */
void send_msg(char *msg){
	struct Server_info *server_info = read_server_info();
	printf("Server ip: %s | Server port %d \n", server_info->server_ip, server_info->port);
	send_info(server_info, msg);
}

/*
 * Create the msg with the cpu utilization
 */
void create_cpu_info_msg(){
	long number_of_processors = get_number_of_processors();
	
	//create array of struct per 1 cpu and one for overall
	struct Cpu_usage *cpu_usage_old = 
		malloc(sizeof(struct Cpu_usage) * (number_of_processors+1));
	
	//create array of struct per 1 cpu and one for overall
	struct Cpu_usage *cpu_usage_new = 
		malloc(sizeof(struct Cpu_usage) * (number_of_processors+1));
	
	// collect the statistic in the given time intervall
	long double cpu_utilization[number_of_processors+1];
	collect_statistics(10, number_of_processors, 
			cpu_usage_old, cpu_usage_new, 
			cpu_utilization);


	for(int i = 0; i < number_of_processors + 1; i++) {
		//TODO create 1 json instead of adding every json on its own
		 send_msg(create_cpu_json(cpu_usage_old[i],
					 cpu_usage_new[i],
				 	 cpu_utilization[i],
				 	 i));
	}
}

/*
 * Create the initial msg to send to the server
 */
char *create_initial_msg() {
	char *release_id = read_release_id();
	printf("Release %s \n", release_id);
	char *init_json_front = "{ MsgType: 'Init' , ReleaseId: '";
	char *init_json_end = "'}";
	char *buffer = malloc(strlen(init_json_front) + strlen(release_id) + strlen(init_json_end));
	sprintf(buffer, "%s%s%s", init_json_front, release_id, init_json_end);
	return buffer;
}

/*
 * Send the initial msg to the server to register this device
 */
void send_initial_msg() {
	char *msg = create_initial_msg(); 
	struct Server_info *server_info = read_server_info();
	printf("Server ip: %s | Server port %d \n", server_info->server_ip, server_info->port);
	send_info(server_info, msg);
}

/*
 * Main function to be called
 */
int main(void)
{
	//send_initial_msg();
	create_cpu_info_msg();
	return 0;
}
