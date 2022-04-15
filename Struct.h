#ifndef STRUCT_H_
#define STRUCT_H_

// current max length of rasberry identifier
#define max_revision 6
// max length of ipv4 255.255.255.255 => 15
#define max_ipv4_length 15
// max length of ipv6 255.255.255.255.255.255 => 23
#define max_ipv6_length 23

// struct for the information relating to the utilization of a cpu
struct Cpu_usage {
	long int idle, working, wait_io, interrupt;
};

//structure for ip and port
struct Server_info {
	char* server_ip;
	int port;	
};

#endif // STRUCT_H_
