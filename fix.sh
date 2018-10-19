#!/bin/sh
echo "Fixing ElectrumX server..."
USERNAME=$(envdir /path/to/electrumx/env printenv USERNAME)
ELECTRUMX=$(envdir /path/to/electrumx/env printenv ELECTRUMXFIX)
exec 2>&1 envdir /path/to/electrumx/env envuidgid $USERNAME python3 $ELECTRUMX
