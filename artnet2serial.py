#!/usr/bin/python3

import sys
from serial import Serial
import socket
import time

UNIVERSE_ID = 1

# Serial device settings
device = '/dev/ttyACM0'
baud   = 115200

globalPixelBuffer = bytearray(512)

# Helper: coerce integer to 0..255
def coerce_int( value ): return max( 0, min( 255, int(value) ) )

def send_serial(channelvalues):
    # Make byte string
    data = b''
    for decimal in channelvalues: data += chr(coerce_int(decimal)).encode('raw_unicode_escape')

    # Send to device and wait for response
    serial.write( data )
    serial.flush()
    status = serial.readline()

    #print( "Sent", len(channelvalues), "channels:", status.strip() )

def handleArtnetPacket( packetBytes ):
    # Unpack Art-Net data and store in global buffer
    if packetBytes[8:8+2] == b"\x00\x50": # ArtDMX
        universeInfo = int.from_bytes( packetBytes[14:14+2], "little" )
        universeId = universeInfo % 1000
        if universeId == UNIVERSE_ID:
            dmxData = packetBytes[18:]
            if len(dmxData) > 0:
               if fillDmxDataInPixelBuffer(dmxData):
                   return
            print( f"Ignoring bad Art-Net packet" )
            
def fillDmxDataInPixelBuffer(dataBuffer):
    for index in range( min( len(globalPixelBuffer), len(dataBuffer) ) ):
        globalPixelBuffer[index] = dataBuffer[index]
    return True

# Check command line arguments
if len(sys.argv) >= 2:
    if sys.argv[1] == '-h' or sys.argv[1] == '--help' or sys.argv[1] == '-?':
        print()
        print( "Usage:", sys.argv[0], " [DEVICE] [UNIVERSE_ID]" )
        print()
        print( "Reads Art-Net data in the specified universe and sends it to a serial device for DMX output." )
        print()
        print( "DEVICE        Serial block device identifier (default: "+device+")" )
        print( "UNIVERSE_ID   Art-Net universe (default: "+str(UNIVERSE_ID)+")" )
        print()
        exit(1)
    device = sys.argv[1]
if len(sys.argv) >= 3:
    UNIVERSE_ID = int(sys.argv[2])

# Bind ArtNet socket
artnetUdpPort = 6454
artnetSocket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
artnetSocket.setblocking( True )
artnetSocket.bind( ( "0.0.0.0", artnetUdpPort ) )
print( f"Listening for Art-Net packets in universe {UNIVERSE_ID} on UDP port {artnetUdpPort}" )


# Open serial device and get ArtNet data
with Serial( device, baud, bytesize=8, parity='N', timeout=1 ) as serial:
    print( "Serial device", device, "opened" )

    receiveBuffer = bytearray( 2048 )
    receiveBufferView = memoryview( receiveBuffer ).toreadonly()

    while True:
        numBytesRead = 0
        try:
            numBytesRead = artnetSocket.recv_into( receiveBuffer )
            if numBytesRead > 0:
                handleArtnetPacket( receiveBufferView[:numBytesRead] )
        except BlockingIOError as e:
            print("BlockingIOError: {}".format(e))
            pass
        except Exception as e:
            print(e)
            exit(1)
        except KeyboardInterrupt:  # quit with Ctrl+C
            exit(0)

        if not numBytesRead:
            time.sleep( 100e-6 )

        send_serial(globalPixelBuffer)

