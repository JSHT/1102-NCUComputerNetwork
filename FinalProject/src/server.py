import socket
import threading
import pickle
# import json


class whiteBoardServer:
    clients_list = []
    last_received_data = ""
    preX, preY = None, None

    def __init__(self):
        self.server_socket = None
        self.create_server()

    def create_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        local_ip = '127.0.0.1'
        local_port = 48763
        self.server_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((local_ip, local_port))
        print("listening for incoming details")
        self.server_socket.listen(20)
        self.receive_data_in_new_thread()

    def receive_data_in_new_thread(self):
        t = None
        while 1:
            client = so, (ip, port) = self.server_socket.accept()
            self.add_to_clients_list(client)
            print("connected to ", ip, ":", str(port))
            t = threading.Thread(target=self.receive_data, args=(so,))
            t.start()

    def add_to_clients_list(self, client):
        if client not in self.clients_list:
            self.clients_list.append(client)

    def receive_data(self, so):
        while 1:
            incoming_buffer = so.recv(2048)
            if not incoming_buffer:
                break
            r_data = pickle.loads(incoming_buffer)
            if r_data == 'close':
                for client in self.clients_list:
                    if client[0] == so:
                        self.clients_list.remove(client)

                break
            # self.last_received_data = json.loads(
            #     incoming_buffer.decode('utf-8'))
            self.last_received_data = r_data
            # print(self.last_received_data)
            self.broadcast_to_all_clients(so)
        so.close()

    def broadcast_to_all_clients(self, so):
        for client in self.clients_list:
            sock, (ip, port) = client
            # print(ip, port)
            if sock is not so:
                # print('in')
                # sock.send(json.dumps(self.last_received_data).encode('utf-8'))
                sock.send(pickle.dumps(self.last_received_data))


if __name__ == "__main__":
    whiteBoardServer()
