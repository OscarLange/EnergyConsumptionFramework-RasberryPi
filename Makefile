CC = gcc
CFLAGS = -g
RM = rm -f

default: main socket

main: Main

socket: Socket

MAIN: Main.c Struct.h
	$(CC) $(CFLAGS) -o Main Main.c

SOCKET: Socket.c
	$(CC) $(CFLAGS) -o Socket Socket.c

clean cleanall:
	$(RM) Main
