#!/usr/bin/env python3
# -*- coding: cp1252 -*-
# vi: ts=4 sw=4 et ai sm

import os, sys, locale
import datetime as tm
import traceback
import codecs as utf
from string import *

def rem_ascii_cc( s ): # Return clean printable s
    rs = ''
    bc = ord( ' ' )
    for c in s:
        
        if ord(c) >= bc:
            # reprc = repr(c)
            # print( "xxxx" )
            # print( "ordinal:", ord(c), "char:", reprc, len(reprc), "\n", end='' )
            rs += c
    return rs
    
def pct_viable( s, chrs ): # Return float percent of chars in s
    nc = 0
    for c in s:
        if c in chrs: nc += 1
    return (float(nc)/float(len(s)))*100.0
    
def verify( s, chrs ): # Return true if all chars in s are in chrs
    for c in s:
        if c not in chrs: return False
    return True

def get_facts(path):
    from traceback import print_exc
    
    enc = locale.getpreferredencoding()
    print( "Scanning", path )
    for path, dirs, files in os.walk(path):
        pth, dir = os.path.split(path)
        # print( "Do directory:", dir )
        error_facts = []
        
        for fn in files:
            filename = os.path.join(path, fn)
            a_file = open(filename, 'rb')
            artist = ''
            title = ''
            dtime = tm.timedelta(seconds=0.0)
            contents = []
            album = {}
            album_name = dir
            tkno = 0
            tnum = ''
            ttags = {}
            atags = {}
            tfo   = False   # True means collecting Track Frame Offsets
            trkoff = []
            tracks = None
            utf  = True
            junk = False            
            
            # Scan file to determine character type
            for rd in a_file:                
                try:
                    d = rd.decode( 'utf-8' )                    
                except:
                    d = rd.decode( 'iso_8859_1' )
                    pv = pct_viable( d, printable )
                    if pv < 85.00:
                        error_facts.append( 'File: ' + filename + "\nUnicode Line: " + rem_ascii_cc(d) + \
                               "\nunlikely real ISO_8859-1 " + '{:2.0f}'.format(pv) + \
                               "% printable -- ignored" )                 
                        junk = True
                        break
                    else:
                        utf = False
            
            # Throwout bad files
            if junk:
                # print( "File:", filename, " ignored" )
                continue
                
            # Process reasonable ones    
            a_file.close()            
            a_file = open(filename, 'rb')            
            raw_file = []                     
            for rd in a_file:
                if utf:
                    d = rd.decode( 'utf-8' )
                else:
                    d = rd.decode( 'iso_8859_1' )

                td = d.strip()
                raw_file.append( td )
                
                td = d.strip()
                # The first half of the data in ccdb all comment
                if td.startswith('#'):
                    if td.startswith( '# xmcd' ):
                        continue
                    elif td.startswith( '# Disc length: ' ):
                        nend = td[15:].find( ' ' )
                        if nend < 0: nend = len(td)
                        tsec = 0.0
                        try:
                            tsec = float( td[15:15+nend] )
                            endtrk = int(tsec) * 75
                            # error_facts.append( 'end is ' + str(nend+15) + '; time is >' + \
                            #   td[15:15+nend] + '< ' + str( tsec ) )
                        except:
                            error_facts.append( 'failed to convert', td[15:15+nend], 'to float seconds' )
                            error_facts.append( '>' + d + '< nend is', 15+nend )
                        dtime = tm.timedelta(seconds=tsec)
                        # error_facts.append( 'dtime is ' + str(dtime) )
                        continue
                    if  d.find( 'Track frame offsets:' ) > 0:
                        tfo = True
                        continue
                    dd = d[1:].strip()
                    if tfo and dd == '':
                        tfo = False
                        continue
                    if tfo and verify( dd, '0123456789' ):
                        trkoff.append(int(dd))
                        continue
                    tfo = False
                    continue
                    
                # The second half of the data in ccdb is comments intermixed with data
                # The first half processing should throw away comments so they never get here.
                if tracks == None:
                    tnum = len(trkoff)+1
                    tracks = tnum * [0,"","", ""]
                    for i in range(0,tnum-1):
                        tracks[i] = [trkoff[i], "", "", ""]
                        # print( i+1, tracks[i] )
                    tracks[tnum-1] = [endtrk, "End of Disk","", ""]
                if tnum < 1: continue
                keyw = ''
                data = ''
                if d.startswith('PLAYORDER='):
                    continue
                try:
                    keyw, data = d.split('=', 1)
                except:
                    error_facts.append( "Missing equal in line:", d )
                    pass
                keyw = keyw.strip()
                data = data.strip()
                
                if   keyw == 'DTITLE':
                    try:
                        artist, title = data.split( ' / ', 1 )
                    except:
                        artist = ''
                        title  = data
                    atags['title'] = title
                    atags['artist'] = artist
                elif keyw == 'DISKID':
                    diskid = data
                    atags['diskid'] = data
                elif keyw == 'DYEAR':
                    date = data
                    atags['pdate'] = data
                elif keyw == 'DGENRE':
                    genre = data
                    atags['genre'] = data
                elif keyw.startswith('TTITLE'):
                    tn = int(keyw[6:])
                    try:
                        tartist, ttitle = data.split( ' / ', 1 )
                    except:
                        tartist = ''
                        ttitle = data
                    if tn < tnum:
                        track = tracks[tn]
                        try:
                            tracks[tn] = [track[0], tartist, ttitle, track[3]]
                        except:
                            error_facts.append( "Track Number error", fn, tn, atags['artist'], atags['title'] )
                        
                    else:
                        error_facts.append( "Track list entry greater than number of tracks", tn, ntracks )
                elif keyw.startswith('EXIT'):
                    tn = int(keyw[4:])
                    if tn <= tnum:
                        track = tracks[tn-1]
                        try:
                            tracks[tn-1] = [track[0], track[1], track[2], track[3] + ' ' + data ]
                        except:
                            error_facts.append( track + ' ' + tartist + ' ' + ttitle + ' ' + data )

                # End of loop collecting data from file

            # Output Album Facts
            try:
                disk_facts = []
                disk_facts.append( ':*       [Album]' )
                if 'title' not in atags:
                    disk_facts.append( ':"       -> No Title' )
                    for item in raw_file:
                        print( "-->", item )
                    atags['title'] = 'None'
                else:
                    disk_facts.append( ':"       -> ' + atags['title'] )
                disk_facts.append( '"        directory: \\(' + path + ')' )
                disk_facts.append( '"        file: ' + fn )
                if utf : enc = "UTF-8 or 7-bit ASCII"
                else   : enc = "ISO8859-1"
                disk_facts.append( '"        file encoding: ' + enc )
                disk_facts.append( '"        number of tracks: ' + str(tnum-1) )
                disk_facts.append( '"        total time: ' + str(dtime))

                for f in atags:
                    disk_facts.append( '"        ' + f + "=" + atags[f] )                
            except:
                error_facts.append( "File:", fn, "Output exception, file eliminated.\n" )
                for item in raw_file:
                    error_facts.append( "-->" + item )
                
            


            # Output Track Facts
            tkno = 0
            track_facts = []
            
            for tkn in range(0,tnum-1):
                track_facts.append( ':*       [Track] # '  + str(tkn + 1)    )      
                track_facts.append( ':        -> ' + atags['title'] + ' --T' + '{:02d}'.format(tkn+1) )
                track_facts.append( '"        track offset: ' + str(tracks[tkn][0]) )
                if tracks[tkn][2] != '':
                    track_facts.append( '"        track title:  ' + tracks[tkn][2] )
                if tracks[tkn][1] != '':
                    track_facts.append( '"        track artist: ' + tracks[tkn][1] )
                if tracks[tkn][3] != '':
                    track_facts.append( '"        track info:   ' + tracks[tkn][3] )
                trk_time = (tracks[tkn+1][0] - tracks[tkn][0]) / 75.0
                fmt_time = str( tm.timedelta(seconds=trk_time) )
                if '.' in fmt_time:
                    fmt_time = fmt_time[0:-7]
                track_facts.append( '"        track length: ' + fmt_time )

            print()
            for outl in track_facts:
                print( outl )
            
            print()
            for outl in disk_facts:
                print( outl )
                
            print()
            for outl in error_facts:
                print( outl )
            error_facts = []
            
            x = input("Next?")
            x = x.strip()
            if x == '': continue
            if x[0] == 'q' or x[0] == 'Q': return


if __name__ == "__main__":
    default_path = './test'
    if len(sys.argv) == 1:
        path = default_path
        print( 'Do default path' )
        get_facts(path)
    else:
        for path in sys.argv[1:]:
            get_facts(path)
