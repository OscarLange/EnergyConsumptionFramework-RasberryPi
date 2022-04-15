CC = gcc
CFLAGS = -g -lm
SRCDIR = src
BUILDDIR = build

RM = rm -f

default: Main


Main: Main.o Socket.o Struct.h
	$(CC) $(CFLAGS) Main.o Socket.o -o Main

Socket.o: Socket.c
	$(CC) $(CFLAGS) -c Socket.c -o Socket.o

Main.o: Main.c
	$(CC) $(CFLAGS) -c Main.c -o Main.o

clean cleanall:
	$(RM) *.o
	$(RM) Main
