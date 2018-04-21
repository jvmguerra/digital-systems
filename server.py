import socket
import configparser
import logging

log = logging.getLogger('udp_server')
config = configparser.ConfigParser()
config.read('./settings.ini')

host = str(config.get('SERVER', 'host'))
port = int(config.get('SERVER', 'port'))

def udp_server(host=host, port=port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    log.info("Listening on udp %s:%s" % (host, port))
    s.bind((host, port))
    while True:
        (data, addr) = s.recvfrom(1400)
        yield data

FORMAT_CONS = '%(asctime)s %(name)-12s %(levelname)8s\t%(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT_CONS)

for data in udp_server():
    print(data)
# def onNewConnection(clientSocket, addr):
#     while 1:
#         msg = raw_input()
#         clientSocket.send(msg)
#     clientSocket.close()

# while True:
#     c, addr = s.recvfrom(1400)
#     print('Got connection from', addr)
#     c.send('Thank you for connecting')
#     thread.start_new_thread(onNewConnection, (c,addr))
# s.close()