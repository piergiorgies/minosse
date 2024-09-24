#!/bin/sh

# Apply the iptables rule (to block the user from accessing the network)
iptables -A OUTPUT -m owner --uid-owner nonetwork -j DROP

exec "$@"  # This will execute CMD from Dockerfile
