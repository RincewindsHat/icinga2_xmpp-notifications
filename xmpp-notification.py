#!/usr/bin/env python3
import sys
import os
import sleekxmpp
import time
import argparse
import ssl

def usage():
    pass
        
class SendMsgBot(sleekxmpp.ClientXMPP):

    def __init__(self, recipient, msg, sender_jid, password):
        super(SendMsgBot, self).__init__(sender_jid, password)

        self.recipient = recipient
        self.msg = msg

        # Service Discovery
        self.register_plugin('xep_0030')
        # XMPP Ping
        self.register_plugin('xep_0199')

        self.add_event_handler('session_start', self.start)

        # my server demands tls1.2. without it, protocol unsupported
        self.ssl_version = ssl.PROTOCOL_TLSv1_2

    def start(self, event):
        self.send_presence()
        self.get_roster()
        self.send_message(mto=self.recipient, mbody=self.msg, mtype='chat')
        # Using wait=True ensures that the send queue will be
        # emptied before ending the session.
        self.disconnect(wait=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        exit(2)

    parser = argparse.ArgumentParser(description="Send XMPP Notifications")

    # Always necessary arguments

    parser.add_argument('-m', '--mode',
                              choices=['host', 'service'],
                              help="Choose if this is a host or service notification",
                              required=True)

    parser.add_argument('-r', '--recipient', 
                        type=str,
                        help="The JID(s) of the recipient(s)",
                        nargs='+',
                        action='append',
                        required=True)

    parser.add_argument('-f', '--sender',
                        type=str,
                        nargs=1,
                        help="The sender address and XMPP JID",
                        required=True)

    parser.add_argument('-p', '--password',
                        type=str,
                        nargs=1,
                        help="XMPP login password",
                        required=True)

    parser.add_argument('-D', '--notification_date',
                        type=str,
                        nargs=1,
                        help="The date of the notification",
                        required=True)

    parser.add_argument('-H', '--hostname',
                        type=str,
                        nargs=1,
                        help="The respective host",
                        required=True)

    parser.add_argument('-d', '--hostdisplayname',
                        type=str,
                        nargs=1,
                        help="Name of the host")

    parser.add_argument('-t', '--notification_type',
                        nargs=1,
                        help="Type of notification",
                        required=True)

    # Optional
    parser.add_argument('-a', '--notification_author',
                        type=str,
                        nargs=1,
                        help="The service sending this")

    parser.add_argument('-c', '--notification_Comment',
                        type=str,
                        nargs=1,
                        help="Some comment")

    parser.add_argument('args',
                        nargs=argparse.REMAINDER)

    parser.add_argument('-S', '--state',
                        type=str, 
                        nargs=1,
                        required=True,
                        help="State of the host/service")
    parser.add_argument('-O', '--output',
                        type=str, 
                        nargs=1,
                        required=True,
                        help="Output of the host/service check")

    parser.add_argument('-e','--servicename',
                        type=str,
                        nargs=1,
                        required=False,
                        help="Name of the service in question")

    parser.add_argument('-u', '--servicedisplayname',
                        type=str,
                        nargs=1,
                        help="Display name of the service")

    args = parser.parse_args(args.args)


    if args.mode == 'service':
        # Service notification
        if args.servicename is None:
            print("No servicename for a service notification")
        if args.servicedisplayname is not None:
            service = args.servicedisplayname[0]
        else:
            service = args.servicename[0]

        if args.hostdisplayname is not None:
            host = args.hostdisplayname[0]
        else:
            host = args.host[0]

        title = f"{service} on {host} is {servicestate[0]}"
        text = f"{title}\nOutput: {ags.serviceoutput[0]}\nTime/Date: {args.notification_date}"

    else:
        # Host notification
        if args.hostdisplayname is not None:
            host = args.hostdisplayname[0]
        else:
            host = args.host[0]

        title = f"Host {host} is {args.hoststate[0]}"
        text = f"{title}:\nOutput: {args.hostoutput[0]}\nTime/Date: {args.notification_date}"

    #print(args)
    for i in args.recipient:
        xmpp = SendMsgBot(recipient=i[0], msg=text, sender_jid=args.sender[0], password=args.password[0])
        if xmpp.connect():
            xmpp.process(block=True)
        else:
            print("Could not connect", file=sys.stderr)
            sys.exit(1)
