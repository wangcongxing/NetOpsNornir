from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram import udp, udp6
from pyasn1.codec.ber import decoder
from pysnmp.proto import api


def cbFun(transportDispatcher, transportDomain, transportAddress, wholeMsg):
    while wholeMsg:
        msgVer = int(api.decodeMessageVersion(wholeMsg))
        print("msgVer=========", msgVer)
        if msgVer in api.protoModules:
            pMod = api.protoModules[msgVer]
        else:
            print('Unsupported SNMP version %s' % msgVer)
            return
        reqMsg, wholeMsg = decoder.decode(
            wholeMsg, asn1Spec=pMod.Message(),
        )
        print('Notification message from %s:%s: ' % (
            transportDomain, transportAddress
        )
              )
        reqPDU = pMod.apiMessage.getPDU(reqMsg)
        if reqPDU.isSameTypeWith(pMod.TrapPDU()):
            print("api.protoVersion1=",api.protoVersion1)
            if msgVer == api.protoVersion1:
                print('Enterprise: %s' % (
                    pMod.apiTrapPDU.getEnterprise(reqPDU).prettyPrint()
                )
                      )
                print('Agent Address: %s' % (
                    pMod.apiTrapPDU.getAgentAddr(reqPDU).prettyPrint()
                )
                      )
                print('Generic Trap: %s' % (
                    pMod.apiTrapPDU.getGenericTrap(reqPDU).prettyPrint()
                )
                      )
                print('Specific Trap: %s' % (
                    pMod.apiTrapPDU.getSpecificTrap(reqPDU).prettyPrint()
                )
                      )
                print('Uptime: %s' % (
                    pMod.apiTrapPDU.getTimeStamp(reqPDU).prettyPrint()
                )
                      )
                varBinds = pMod.apiTrapPDU.getVarBindList(reqPDU)
            else:
                varBinds = pMod.apiPDU.getVarBindList(reqPDU)
            print('Var-binds:')
            for oid, val in varBinds:
                a = oid  # oid.prettyPrint().strip()
                b = val.strip().split('\n')  # val.prettyPrint().strip().split('\n')
                #print("a==",a)
                #print("b==",b)

                for line in b:
                    item = line.strip()
                    if item.startswith('string-value'):
                        print('string-value=' + item.replace('string-value=0x', '').decode('hex'))
                    else:
                        print(item)
    return wholeMsg


if __name__ == '__main__':
    print("??????")
    transportDispatcher = AsynsockDispatcher()

    transportDispatcher.registerRecvCbFun(cbFun)

    # UDP/IPv4
    transportDispatcher.registerTransport(
        udp.domainName, udp.UdpSocketTransport().openServerMode(('0.0.0.0', 162))
    )

    # UDP/IPv6
    transportDispatcher.registerTransport(
        udp6.domainName, udp6.Udp6SocketTransport().openServerMode(('::1', 162))
    )

    transportDispatcher.jobStarted(1)

    try:
        # Dispatcher will never finish as job#1 never reaches zero
        transportDispatcher.runDispatcher()
    except:
        transportDispatcher.closeDispatcher()
        raise
