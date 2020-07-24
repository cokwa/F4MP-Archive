import F4MP

server = F4MP.Server("localhost", 7779)


@server.listener()
def on_connection_request(event):
    print(event.type)
    print(event.ctx.mode)


server.run()
