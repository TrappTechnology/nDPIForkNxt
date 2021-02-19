#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.dirname(sys.argv[0]) + '/../../dependencies')
import nDPIsrvd
from nDPIsrvd import nDPIsrvdSocket, TermColor

class Stats:
    lines_processed = 0
    print_dot_every = 10
    next_lines_print = print_dot_every

def onJsonLineRecvd(json_dict, current_flow, global_user_data):
    validation_done = nDPIsrvd.validateAgainstSchema(json_dict)

    global_user_data.lines_processed += 1
    if global_user_data.lines_processed % global_user_data.print_dot_every == 0:
        sys.stdout.write('.')
        sys.stdout.flush()
    if global_user_data.lines_processed == global_user_data.next_lines_print:
        global_user_data.next_lines_print *= 2
        sys.stdout.write(str(global_user_data.lines_processed))
        sys.stdout.flush()

    return validation_done

if __name__ == '__main__':
    argparser = nDPIsrvd.defaultArgumentParser()
    args = argparser.parse_args()
    address = nDPIsrvd.validateAddress(args)

    sys.stderr.write('Recv buffer size: {}\n'.format(nDPIsrvd.NETWORK_BUFFER_MAX_SIZE))
    sys.stderr.write('Connecting to {} ..\n'.format(address[0]+':'+str(address[1]) if type(address) is tuple else address))

    nDPIsrvd.initSchemaValidator(os.path.dirname(sys.argv[0]) + '/../../schema')

    nsock = nDPIsrvdSocket()
    nsock.connect(address)
    nsock.loop(onJsonLineRecvd, Stats())