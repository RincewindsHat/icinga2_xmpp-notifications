#!/usr/bin/env python3
import sys
import os
import sleekxmpp
import time
import argparse
import ssl

def usage():
    print("XMPP Notification sender for icinga2\n\n"
            "Usage:\n"
            "xmpp-notification.py\n"
            "   -h|--help   (Prints this help)\n"
            "   --service|--host (MUST be first argument and decides, whether this "
            "is a host or a service notification)\n\n"

            "Obligatory arguments:\n"
            "   -r|--recipient RECIPIENT ...    (JID of the recipient)\n"
            "   -f|--sender SENDER     (XMPP-Account (JID) to send from)\n"
            "   -p|--password PASSWORD   (Login password for the sending XMPP account)\n"
            "   -d|--notification_date DATE (Date of the occuring event ($icinga.long_date_time$))\n"
            "   -N|--host HOST   (The host object to which the event is attached ($host.name$))\n"
            "   -t|--notification_type TYPE\n"
            "   [-n|--hostdisplayname HOSTDISPLAYNAME] Pretty name for the host ($host.display_name$)\n\n"
            "Host notification options:\n"
            "   -h|--hoststate STATE ($host.state$)\n\n"
            "Service notification options:\n"
            "   -e|--servicename SERVICE    ($service.name$)\n"
            "   [-o|--serviceoutput]  OUTPUT (Check result or something like that($service.output$))\n"
            "   -s|--servicestate STATE ($service.state$)\n"
            "   [-u|--servicedisplayname SERVICEDISPLAYNAME] ($service.display_name$)"
            )
        


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

    # Optional
    parser.add_argument('-a', '--notification_author',
                        type=str,
                        nargs='*',
                        help="The service sending this")

    if sys.argv[1] == "--host":
        is_host_notification = True
        # Host notification
        parser.add_argument('-S', '--hoststate',
                            type=str, 
                            nargs=1,
                            required=True,
                            help="State of the service")

    elif sys.argv[1] == "--service":
        is_host_notification = False
        parser.add_argument('-e','--servicename',
                            type=str,
                            nargs='*',
                            required=True,
                            help="Name of the service in question")

        parser.add_argument('-o', '--serviceoutput',
                            type=str,
                            nargs='*',
                            required=True,
                            help="Result of the service check")

        parser.add_argument('-S', '--servicestate',
                            type=str, 
                            nargs=1,
                            required=True,
                            help="State of the service")


        parser.add_argument('-u', '--servicedisplayname',
                            type=str,
                            nargs='*',
                            help="Display name of the service")
    else:
        usage()
        sys.exit(2)
        
    args = parser.parse_args(sys.argv[2:])

    if is_host_notification == False:
        # Service notification
        if args.servicedisplayname is not None:
            service = args.servicedisplayname[0]
        else:
            service = args.servicename[0]

        if args.hostdisplayname is not None:
            host = args.hostdisplayname[0]
        else:
            host = args.host[0]

        text = "{0} {1}\n{2}: {3}\n{4}".format(args.servicestate[0],
                                         service,
                                         host,
                                         args.serviceoutput[0],
                                         args.notification_date[0]
                                        )
    else:
        # Host notification
        if args.hostdisplayname is not None:
            host = args.hostdisplayname[0]
        else:
            host = args.host[0]

        text = "{0}:\nHost {1} is {2}\n{3}".format(args.notification_type[0],
                                        host,
                                        args.hoststate[0],                                    
                                        args.notification_date[0]
                                        )

    #print(args)
    for i in args.recipient:
        xmpp = SendMsgBot(recipient=i[0], msg=text, sender_jid=args.sender[0], password=args.password[0])
        if xmpp.connect():
            xmpp.process(block=True)
        else:
            print("Could not connect", file=sys.stderr)
            sys.exit(1)
