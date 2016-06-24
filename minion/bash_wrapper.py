import shlex
from subprocess import Popen, PIPE

def execute_bash_command(bash_command):
    print bash_command
    command_parts = []
    if "|" in bash_command:    
        command_parts = bash_command.split('|')
    else:
        command_parts.append(bash_command)
    i = 0
    processes = {}
    for command_part in command_parts:
        command_part = command_part.strip()
        if i == 0:
            processes[i]=Popen(shlex.split(command_part),
                    stdin=None, stdout=PIPE, stderr=PIPE)
        else:
            processes[i]=Popen(shlex.split(command_part),
                    stdin=processes[i - 1].stdout, stdout=PIPE, stderr=PIPE)
        i = i + 1
    (output, errput) = processes[i - 1].communicate()
    return_code = processes[0].wait()
    return (return_code, output, errput)
