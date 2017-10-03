#!/usr/bin/python2
import sys,os,xmpp,time
import argparse

parser = argparse.ArgumentParser(description="Sending XMPP Messages")

parser.add_argument('-r', '--recipient', 
                type=str, 
                nargs='+', 
                help="The JID of the recipient",
                required=True)

parser.add_argument('-f', '--sender',
                type=str,
                nargs=1,
                help="The sender address and XMPP JID",
                required=True)

parser.add_argument('-p', '--password',
                type=str,
                nargs=1,
                help="XMPP login password")

parser.add_argument('-d', '--notification_date',
                type=str,
                nargs=1,
                help="The date of the notification")

parser.add_argument('-N', '--notification_hostname',
                type=str,
                nargs=1,
                help="The problematic host",
                required=True)

parser.add_argument('-e','--servicename',
                type=str,
                nargs=1,
                help="Name of the service")

parser.add_argument('-o', '--serviceoutput',
                type=str,
                nargs=1,
                help="Result of the service check")

parser.add_argument('-s', '--servicestate',
                type=str, 
                nargs=1,
                help="State of the service")
parser.add_argument('-n', '--hostdisplayname',
                type=str,
                nargs=1,
                help="Name of the host")
parser.add_argument('-t', '--notification_type',
                nargs=1,
                help="Type of notification")
parser.add_argument('-u', '--servicedisplayname',
                type=str,
                nargs=1,
                help="Nice name of the service")
#parser.add_argument('-a', '--notification_author', type=str, nargs=1, help="The service sending this")

args = parser.parse_args()

jidparams={'jid':args.sender[0], 'password':args.password[0]}
text = "{0} {1}: {2} {3}".format(args.servicestate[0],
                args.servicename[0],
                args.notification_hostname[0],
                args.serviceoutput[0])

jid=xmpp.protocol.JID(jidparams['jid'])
cl=xmpp.Client(jid.getDomain(),debug=[])

con=cl.connect()
if not con:
    sys.exit()

auth=cl.auth(jid.getNode(),jidparams['password'],resource=jid.getResource())
if not auth:
    sys.exit()

#cl.SendInitPresence(requestRoster=0)   # you may need to uncomment this for old server

for i in args.recipient:
        message = xmpp.protocol.Message(i, text)
        message.setAttr('type', 'chat')
        id=cl.send(message)

#time.sleep(1)   # some older servers will not send the message if you disconnect immediately after sending

cl.disconnect()
