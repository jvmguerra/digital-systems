import crud_pb2
import crud_pb2_grpc

class CrudGrpc(crud_pb2_grpc.CrudGrpcServicer):
    def __init__(self, commandPile):
        self.commandPile = commandPile

    def SendCommand(self, request, context):
        clientData = self.prepareClientData(request)
        self.commandPile.insert(clientData)
        print(self.prepareClientData(request))
        return crud_pb2.Response(message='Comando inserido na pilha!')

    def prepareClientData(self, request):
        return {
            'client': (request.ip, request.port),
            'data': {
                'command': request.command,
                'item': request.item,
                'string': request.message,
                'monitoring': request.monitoring
            }
        }
