#!/usr/bin/env python3
import sys
import os
import sleekxmpp
import time
import argparse

parser = argparse.ArgumentParser(description="Sending XMPP Messages")

def usage():
    print("XMPP Notification sender for icinga2\n\n" +
            "Usage:\n" +
            "xmpp-notification.py\n" +
            "   -h | --help   Prints this help\n" +
            "   -r | --recipient    JID of the recipient"
            )
        


class SendMsgBot(sleekxmpp.ClientXMPP):

    def __init__(self, recipient, msg, sender_jid, password):
        super(SendMsgBot, self).__init__(jid, password)

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
    # Always necesary

    parser.add_argument('-r', '--recipient', 
                        type=str, 
                        help="The JID(s) of the recipient(s)",
                        nargs=1,
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

    parser.add_argument('-d', '--notification_date',
                        type=str,
                        nargs=1,
                        help="The date of the notification",
                        required=True)

    parser.add_argument('-N', '--host',
                        type=str,
                        nargs=1,
                        help="The respective host",
                        required=True)

    parser.add_argument('-n', '--hostdisplayname',
                        type=str,
                        nargs='*',
                        help="Name of the host")

    parser.add_argument('-t', '--notification_type',
                        nargs=1,
                        help="Type of notification",
                        required=True)

    parser.add_argument('-a', '--notification_author',
                        type=str,
                        nargs='*',
                        help="The service sending this")

    if sys.argv[1] == "--host":
        # Host notification
        parser.add_argument('-h', '--hoststate',
                            type=str, 
                            nargs=1,
                            help="State of the service")

    elif sys.argv[1] == "--service":
        parser.add_argument('-e','--servicename',
                            type=str,
                            nargs='*',
                            help="Name of the service in question")

        parser.add_argument('-o', '--serviceoutput',
                            type=str,
                            nargs='*',
                            help="Result of the service check")

        parser.add_argument('-s', '--servicestate',
                            type=str, 
                            nargs=1,
                            help="State of the service")


        parser.add_argument('-u', '--servicedisplayname',
                            type=str,
                            nargs='*',
                            help="Display name of the service")
    else:
        usage()
        sys.exit(2)
        
    args = parser.parse_args()

    if args.servicename:
        # Service notification
        if args.servicedisplayname:
            service = args.servicedisplayname[0]
        else:
            service = args.servicename[0]

        text = "{0} {1}: {2} {3}".format(args.servicestate[0],
                                        service,
                                        args.notification_hostname[0],
                                        args.serviceoutput[0]
                                        )
    else:
        # Host notification
        if args.hostdisplayname[0]:
            host = args.hostdisplayname[0]
        else:
            host = args.host[0]

        text = "{0}: {1} is {3}".format(args.notification_type[0],
                                        host,
                                        args.hoststate[0]                                    
                                        )

    for i in args.recipient:
        xmpp = SendMsgBot(i, text, args.sender[0], sys.password[0])
        if xmpp.connect():
            xmpp.process(block=True)
        else:
            print("Could not connect", file=sys.stderr)
            sys.exit(1)
