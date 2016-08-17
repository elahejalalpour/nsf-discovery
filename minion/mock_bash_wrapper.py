from mock_ovs_driver import MockOVSDriver
import commandwrapper

odriver = MockOVSDriver()

def __execute_pipe_command(pipe_command, pipe_stdin):
    pipe_cmd = commandwrapper.WrapCommand(pipe_command, shell=True)
    pipe_cmd.stdin = pipe_stdin
    pipe_cmd.start()
    pipe_cmd.join()
    return pipe_cmd.results

def execute_bash_command(bash_command):
    ret = 0 
    out = "" 
    err = ""
    tokens = bash_command.split(" ")
    command = tokens[0] 
    if command == "sudo":
        tokens = tokens[1:]
        command = tokens[0]
    tokens = tokens[1:]
    if command == "ovs-vsctl":
        subcommand = tokens[0]
        tokens = tokens[1:]
        if subcommand == "add-br":
            args = tokens[0]
            ret, out, err = odriver.create_bridge(args)
        elif subcommand == "del-br":
            args = tokens[0]
            ret, out, err = odriver.delete_bridge(args)
        elif subcommand == "show":
            pipe_command = ""
            if len(tokens) > 0:
                pipe_command = " ".join(tokens[1:])
            bridges = "\n".join(odriver.get_bridges())
            out, err = __execute_pipe_command(pipe_command, bridges)
            ret = 0
        elif subcommand == "add-port":
            bridge, port = tokens[0], tokens[1]
            ret, out, err = odriver.attach_interface_to_ovs(bridge, port)
        elif subcommand == "del-port":
            bridge, port = tokens[0], tokens[1]
            ret, out, err = odriver.detach_interface_from_ovs(bridge, port)
        elif subcommand == "list-ports":
            bridge = tokens[0]
            tokens = tokens[1:]
            pipe_command = ""
            if len(tokens) > 0:
                pipe_command = " ".join(tokens[1:])
            ret, out, err = odriver.get_ports(bridge)
            if not ret and len(pipe_command) > 0:
                out, err = __execute_pipe_command(pipe_command, out)
    return (ret, out, err)
