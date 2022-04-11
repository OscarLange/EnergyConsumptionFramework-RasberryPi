CC = gcc
CFLAGS = -g
RM = rm -f

default: main

main: Main

MAIN: Main.c
	$(CC) $(CFLAGS) -o Main Main.c

clean cleanall:
	$(RM) Main
