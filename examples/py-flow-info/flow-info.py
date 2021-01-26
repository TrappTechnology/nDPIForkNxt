#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.dirname(sys.argv[0]) + '/../../dependencies')
import nDPIsrvd
from nDPIsrvd import nDPIsrvdSocket, TermColor


def parse_json_str(json_str):

    j = nDPIsrvd.JsonParseBytes(json_str[0])
    nDPIdEvent = nDPIsrvd.nDPIdEvent.validateJsonEventTypes(j)
    if nDPIdEvent.isValid is False:
        raise RuntimeError('Missing event id or event name invalid in the JSON string: {}'.format(j))
    if nDPIdEvent.BasicEventID != -1:
        print('{:>21}: {}'.format(TermColor.WARNING + TermColor.BLINK + 'BASIC-EVENT' + TermColor.END,
                                  nDPIdEvent.BasicEventPrettyName))
        return
    elif nDPIdEvent.FlowEventID == -1:
        return

    ndpi_proto_categ = ''
    ndpi_frisk = ''

    if 'ndpi' in j:
        if 'proto' in j['ndpi']:
            ndpi_proto_categ += '[' + str(j['ndpi']['proto']) + ']'

        if 'category' in j['ndpi']:
            ndpi_proto_categ += '[' + str(j['ndpi']['category']) + ']'

        if 'flow_risk' in j['ndpi']:
            cnt = 0
            for key in j['ndpi']['flow_risk']:
                ndpi_frisk += str(j['ndpi']['flow_risk'][key]) + ', '
                cnt += 1
            ndpi_frisk = '{}: {}'.format(
                TermColor.WARNING + TermColor.BOLD + 'RISK' + TermColor.END if cnt < 2
                else TermColor.FAIL + TermColor.BOLD + TermColor.BLINK + 'RISK' + TermColor.END,
                ndpi_frisk[:-2])

    instance_and_source = ''
    instance_and_source += '[{}]'.format(TermColor.setColorByString(j['alias']))
    instance_and_source += '[{}]'.format(TermColor.setColorByString(j['source']))

    flow_event_name = ''
    if nDPIdEvent.FlowEventName == 'guessed' or nDPIdEvent.FlowEventName == 'undetected':
        flow_event_name += '{}{:>16}{}'.format(TermColor.HINT, nDPIdEvent.FlowEventPrettyName, TermColor.END)
    else:
        flow_event_name += '{:>16}'.format(nDPIdEvent.FlowEventPrettyName)

    if j['l3_proto'] == 'ip4':
        print('{} {}: [{:.>6}] [{}][{:.>5}] [{:.>15}]{} -> [{:.>15}]{} {}' \
              ''.format(instance_and_source, flow_event_name, 
              j['flow_id'], j['l3_proto'], j['l4_proto'],
              j['src_ip'].lower(),
              '[{:.>5}]'.format(j['src_port']) if 'src_port' in j else '',
              j['dst_ip'].lower(),
              '[{:.>5}]'.format(j['dst_port']) if 'dst_port' in j else '',
              ndpi_proto_categ))
    elif j['l3_proto'] == 'ip6':
        print('{} {}: [{:.>6}] [{}][{:.>5}] [{:.>39}]{} -> [{:.>39}]{} {}' \
                ''.format(instance_and_source, flow_event_name,
              j['flow_id'], j['l3_proto'], j['l4_proto'],
              j['src_ip'].lower(),
              '[{:.>5}]'.format(j['src_port']) if 'src_port' in j else '',
              j['dst_ip'].lower(),
              '[{:.>5}]'.format(j['dst_port']) if 'dst_port' in j else '',
              ndpi_proto_categ))
    else:
        raise RuntimeError('unsupported l3 protocol: {}'.format(j['l3_proto']))

    if len(ndpi_frisk) > 0:
        print('{} {:>18}{}'.format(instance_and_source, '', ndpi_frisk))


if __name__ == '__main__':
    argparser = nDPIsrvd.defaultArgumentParser()
    args = argparser.parse_args()
    address = nDPIsrvd.validateAddress(args)

    sys.stderr.write('Recv buffer size: {}\n'.format(nDPIsrvd.NETWORK_BUFFER_MAX_SIZE))
    sys.stderr.write('Connecting to {} ..\n'.format(address[0]+':'+str(address[1]) if type(address) is tuple else address))

    nsock = nDPIsrvdSocket()
    nsock.connect(address)

    while True:
        received = nsock.receive()
        for received_json_pkt in received:
            parse_json_str(received_json_pkt)

