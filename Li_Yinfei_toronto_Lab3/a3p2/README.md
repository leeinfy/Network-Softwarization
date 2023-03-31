I use wireshark to check the flow of the packets. I find out it keeps broadcast a ARP packets. However the switch does not implement any flow to take care of ARP protocol.
I realize that the `h1 ping h2` means h1 ping h2's ip address. Then i manually input the command `arp -s 10.0.1.2 00:00:00:00:01:02` and `arp -s 10.0.1.1 00:00:00:01:01` in h1 and h2 terminal to setup a static arp. Then `pingall` command works.

