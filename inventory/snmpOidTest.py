from pysnmp.hlapi import *

iterator = nextCmd(
    SnmpEngine(),
    CommunityData('mypublic'),
    UdpTransportTarget(('10.32.1.3', 161)),
    ContextData(),
    ObjectType(ObjectIdentity('1.3.6.1.2.1.1')),
    lookupMib=False
)

for errorIndication, errorStatus, errorIndex, varBinds in iterator:

    if errorIndication:
        print(errorIndication)
        break

    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        break

    else:
        for varBind in varBinds:
            print(' = '.join([x.prettyPrint() for x in varBind]))