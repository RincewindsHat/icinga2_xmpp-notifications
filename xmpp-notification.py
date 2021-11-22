#!/usr/bin/env python3
import sys
import slixmpp
import argparse
import ssl


class SendMsgBot(slixmpp.ClientXMPP):

    def __init__(self, recipient, msg, sender_jid, password, muc):
        super().__init__(sender_jid, password)

        self.recipient = recipient
        self.msg = msg

        # Service Discovery
        self.register_plugin('xep_0030')
        # XMPP Ping
        self.register_plugin('xep_0199')

        if muc:
            self.register_plugin('xep_0045')
            self.room = muc
            self.add_event_handler('session_start', self.start_muc)
        else:
            self.add_event_handler('session_start', self.start)

    def start_muc(self, event):
        self.get_roster()
        self.send_presence()
        self.plugin['xep_0045'].join_muc(self.room, "icinga2")
        self.send_message(mto=self.room, mbody=self.msg, mtype='groupchat')
        # Using wait=True ensures that the send queue will be
        # emptied before ending the session.
        self.disconnect(wait=True)


    def start(self, event):
        self.send_presence()
        self.get_roster()
        self.send_message(mto=self.recipient, mbody=self.msg)
        # Using wait=True ensures that the send queue will be
        # emptied before ending the session.
        self.disconnect(wait=True)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Send XMPP Notifications")

    # Always necessary arguments
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
    parser.add_argument('-r', '--recipient',
                        type=str,
                        help="The JID of a recipient (can be repeated)",
                        nargs='+',
                        action='append')

    parser.add_argument('--muc',
                        type=str,
                        nargs='+',
                        help="The JID of a MUC to send to",
                        action='append')

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

    args = parser.parse_args()


    # Hostname
    if args.hostdisplayname is None:
        host = args.hostname[0]
    else:
        host = args.hostdisplayname[0]

    # Date
    date = args.notification_date[0]

    # State
    state = args.state[0]

    # Output
    output = args.output[0]

    if args.servicename :
        # Service notification
        if args.servicedisplayname is None:
            service = args.servicename[0]
        else:
            service = args.servicedisplayname[0]

        title = f"Service {service} on {host} is {state}"
        text = f"{title}\nOutput: {output}\nTime/Date: {date}"

    else:
        # Host notification
        title = f"Host {host} is {state}"
        text = f"{title}:\nOutput: {output}\nTime/Date: {date}"

    # Recipients
    if args.recipient == None and args.muc == None:
        print("At least one recipient (may be a MUC) is necessary")
        os.exit(1)



    #print(args)
    if args.muc != None:
        for i in args.muc:
            muc = i[0]
            #print(i)
            xmpp = SendMsgBot(recipient=i[0], msg=text, sender_jid=args.sender[0], password=args.password[0], muc=muc)
            xmpp.connect()
            xmpp.process(forever=False)

    if args.recipient != None:
        for i in args.recipient:
            #print(i)
            xmpp = SendMsgBot(recipient=i[0], msg=text, sender_jid=args.sender[0], password=args.password[0], muc=None)
            xmpp.connect()
            xmpp.process(forever=False)
