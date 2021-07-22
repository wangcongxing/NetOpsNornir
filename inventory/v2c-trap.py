# Notification Originator Application (TRAP)
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram import udp
from pyasn1.codec.ber import encoder
from pysnmp.proto import api

# Protocol version to use
verID = api.protoVersion2c
pMod = api.protoModules[verID]

# Build PDU
trapPDU = pMod.TrapPDU()
pMod.apiTrapPDU.setDefaults(trapPDU)

# Traps have quite different semantics among proto versions
if verID == api.protoVersion2c:
    var = []
    oid = (1, 3, 6, 1, 4, 1, 2014516, 1, 1, 1, 2, 0)
    val = pMod.Integer(1)
    var.append((oid, val))
    pMod.apiTrapPDU.setVarBinds(trapPDU, var)

# Build message
trapMsg = pMod.Message()
pMod.apiMessage.setDefaults(trapMsg)
pMod.apiMessage.setCommunity(trapMsg, 'public')
pMod.apiMessage.setPDU(trapMsg, trapPDU)

transportDispatcher = AsynsockDispatcher()
transportDispatcher.registerTransport(
    udp.domainName, udp.UdpSocketTransport().openClientMode()
)
transportDispatcher.sendMessage(
    encoder.encode(trapMsg), udp.domainName, ('127.0.0.1', 162)
)
transportDispatcher.runDispatcher()
transportDispatcher.closeDispatcher()
