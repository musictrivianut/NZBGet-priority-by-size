#!/usr/bin/env python3
#
##############################################################################
### NZBGET QUEUE SCRIPT                                                    ###

# Automatic priority setting based on minimum size. Only sets priority 
# of a nzb when added to queue.
#
# Further discussion and updates at: 
# http://nzbget.net/forum/viewtopic.php?f=8&t=1957
# Script version: 1.0.
#
# Original found at https://forum.nzbget.net/viewtopic.php?f=8&t=3755
# This version modified by musictrivianut on 30 Aug 2022
# Script version 1.0.1.

##############################################################################
### OPTIONS                                                                ###

# VerySmallSize less than in MB
VerySmallSize=100
# Priority very high.
PriorityVerySmall='100'

# SmallSize less than in MB
SmallSize=1024
# Priority high.
PrioritySmall='50'

# Normal less than in MB
NormalSize=3072
# Priority normal.
PriorityNormal='0'

# BigSize less than in MB
BigSize=8192
# Priority low.
PriorityBig='-50'

# VeryBigSize less than in MB
VeryBigSize=16384
# Priority very low
PriorityVeryBig='-100'

### NZBGET QUEUE SCRIPT
### QUEUE EVENTS: NZB_ADDED
##############################################################################

import os
import sys
from xmlrpc.client import ServerProxy
import time

# Exit codes used by NZBGet for post-processing scripts.
# Queue-scripts don't have any special exit codes.
POSTPROCESS_SUCCESS=93
POSTPROCESS_NONE=95
POSTPROCESS_ERROR=94

verbose = False

# Start up checks
def start_check():
        # Check if the script is called from a compatible NZBGet version (as queue-script or as pp-script)
        if not 'NZBOP_UNPACKPASSFILE' in os.environ:
                print('*** NZBGet queue script ***')
                print('This script is supposed to be called from nzbget (15.0 or later).')
                sys.exit(1)

        # This script processes only certain queue events.
        if os.environ.get('NZBNA_EVENT') not in ['NZB_ADDED']:
                sys.exit(0)

# Establish connection to NZBGet via RPC-API
def connect_to_nzbget():
        # First we need to know connection info: host, port and password of NZBGet server.
        # NZBGet passes all configuration options to scripts as environment variables.
        host = os.environ['NZBOP_CONTROLIP']
        if host == '0.0.0.0': host = '127.0.0.1'
        port = os.environ['NZBOP_CONTROLPORT']
        username = os.environ['NZBOP_CONTROLUSERNAME']
        password = os.environ['NZBOP_CONTROLPASSWORD']
        
        # Build an URL for XML-RPC requests
        # TODO: encode username and password in URL-format
        xmlRpcUrl = 'http://%s:%s@%s:%s/xmlrpc' % (username, password, host, port);
        # Create remote server object
        nzbget = ServerProxy(xmlRpcUrl)
        return nzbget

def checkSizeSetPriority(fileSize, nzb):

        Priority  = 'off'
        
        if fileSize < VerySmallSize:
                Priority = PriorityVerySmall
        elif fileSize < SmallSize:
                Priority = PrioritySmall
        elif fileSize < NormalSize:
                Priority = PriorityNormal
        elif fileSize < BigSize:
                Priority = PriorityBig
        else:
                Priority = PriorityVeryBig

        print ('[DETAIL] Set priority of ' + nzb['NZBName'] + ' to: ' + Priority)
        nzbget.editqueue('GroupSetPriority', Priority, nzb['NZBID'])
        return

# Script body
def main():
        # Do start up check
    print ('Hello')
    start_check()
    sys.stdout.flush()
        
    global nzbget
    nzbget = connect_to_nzbget()
    # Using RPC-method "editqueue" of XML-RPC-object "nzbget".
    nzbs = nzbget.listgroups(0) 
        
    for nzb in nzbs:
            # find the just added NZB in queue
            if int(nzb['NZBID']) == int(os.environ.get('NZBNA_NZBID')):
                    break
    fileSize = nzb['FileSizeMB']
    print ('[DETAIL] Size of ' + nzb['NZBName'] + ' is %.2f MB' % fileSize)

    return checkSizeSetPriority(fileSize, nzb)
                

# Execute main script function
main()        

# All OK, returning exit status 'POSTPROCESS_SUCCESS' (int <93>) to let NZBGet know
# that our script has successfully completed (only for pp-script mode).
sys.exit(POSTPROCESS_SUCCESS)
