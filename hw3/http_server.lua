http_server_port_number = 20000

function start_server()
  printf ('Start server at 0.0.0.0 port %d\n', http_server_port_number)
  simRemoteApi.start(http_server_port_number)
end

function stop_server()
  simRemoteApi.stop(http_server_port_number)
end
