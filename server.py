import socket
import sys
import os

# const for buffer
BUFFER_SIZE = 1024


# splitting the data into different messages using '\r\n\r\n' as splitter
def split_data_to_messages(data):
    data_split = data.split('\r\n\r\n')
    data_split.remove('')
    return data_split


# finding the file path and connection status in the data
def find_elements(data):
    # splitting the data to list
    data_to_list = data.split()
    # saving the file path in element array
    elements_list = [data_to_list[1]]
    # finding the connection status and insert to the element array
    index_connection_element = data_to_list.index("Connection:")
    elements_list.append(data_to_list[index_connection_element + 1])
    # return array with path file and connection status
    return elements_list


# handling redirect request
def redirect(client_socket):
    data_back = "HTTP/1.1 301 Moved Permanently\r\nConnection: close\r\nLocation: /result.html\r\n"
    client_socket.send(data_back.encode())
    client_socket.close()


# handling '\'request
def back_slash(client_socket):
    content_read = open(os.path.abspath('files/index.html'), 'rb').read()
    data_back = "HTTP/1.1 200 OK\r\nConnection: close\r\nContent-Length: 11\r\n\r\n"
    data_back_en = data_back.encode()
    client_socket.send(data_back_en + content_read)
    client_socket.close()


# handling not found file request
def not_found_404(client_socket):
    data_back = "HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n"
    client_socket.send(data_back.encode())
    client_socket.close()


# handling file request
def sending_file(data_list, client_socket):
    path = "files" + "".join(data_list[0])
    content_read = open(path, 'rb').read()
    data_back = "HTTP/1.1 200 OK\r\nConnection:" + str(data_list[1]) + "\r\nContent-Length:" + str(len(
        content_read)) + "\r\n\r\n"
    data_byte = data_back.encode()
    client_socket.send(data_byte + content_read)


def main(listen_port):
    # open a socket for communication
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', int(listen_port)))
    server.listen(1)
    while True:
        # accept communication with client
        client_socket, client_address = server.accept()
        # setting timeout for 1 second
        client_socket.settimeout(1.0)
        # try an catch block - try to get data from client, if timeout passed catch and close socket
        try:
            data = client_socket.recv(BUFFER_SIZE)
        except socket.timeout:
            client_socket.close()
            continue
        # print client request
        print('Received: ', data.decode())
        # extracting file path and connection status from data
        data_buffer = split_data_to_messages(data.decode())
        for data in data_buffer:
            data_list = find_elements(data)
            # checking edge case - asking for redirect and '/'
            if data_list[0] == "/redirect":
                redirect(client_socket)
                continue
        if data_list[0] == '/':
            back_slash(client_socket)
            continue
        # else asking for a file
        else:
            # trying to open the file using file path
            try:
                sending_file(data_list, client_socket)
                # checking if connection status is close
                if data_list[1] == 'close':
                    client_socket.close()
            # if file doesn't exist - return 404 and close connection
            except FileNotFoundError:
                not_found_404(client_socket)
                continue


if __name__ == '__main__':
    port = sys.argv[1]
    main(port)
