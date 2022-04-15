#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include "Struct.h"


/*
 * Create socket and send msg
 */
void send_info(struct Server_info *server_info, char* msg) {

	int sockfd;
	//char buffer[msg_size];
	
	struct sockaddr_in servaddr;

	// Socket file descriptor
	if (( sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
		perror("socket creation failed");
		exit(EXIT_FAILURE);
	}

	memset(&servaddr, 0, sizeof(servaddr));

	// Server information
	servaddr.sin_family = AF_INET;
	servaddr.sin_port = htons((int) server_info->port);
	servaddr.sin_addr.s_addr = inet_addr((char*) server_info->server_ip);

	int n, len;

	sendto(sockfd, (const char *)msg, strlen(msg),
			MSG_CONFIRM, (const struct sockaddr *) &servaddr,
			sizeof(servaddr));
	printf("Hello message sent. \n");

	/*n = recvfrom(sockfd, (char *)buffer, MAXLINE,
			MSG_WAITALL, (struct sockaddr *) &servaddr,
			&len);
	buffer[n] = '\0';
	printf("Server : %s\n", buffer);*/

	close(sockfd);
}
