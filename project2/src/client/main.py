""" Main entry point for Simple Echo Server Client application.
Client attempts to connect to server on IP Address and Port.
Default values are set to 127.0.0.1 (localhost) and 5500.
Server must be running and listening on that IP and Port before
the client can connect. Client program runs until either user
enters 'quit' or 'shutdown server'.
"""
from client import Client


def main():
    c1 = Client("127.0.0.1", 5500)

    c1.login()

    continue_session = True
    while continue_session is True:
        c1.display_menu()
        menu_option = input("Please input an option listed above:")
        continue_session = c1.process_message(menu_option)


if __name__ == '__main__':
    main()
