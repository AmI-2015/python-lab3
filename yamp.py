'''
Yet Another Music Player

Created on Mar 23, 2015

@author: Dario Bonino <dario.bonino@gmail.com>

Copyright (c) 2015 Dario Bonino

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License
'''
from mutagen import flac, mp3
from subprocess import Popen, PIPE

import os

#----- Classes -------------

class Track:
    '''
    A class representing a music file
    '''

    def __init__(self, path=None):

        # the track id
        self.id = None

        #the file to which the track points (full path)
        self.path = path

        #extract the track description from file tags
        self.data = self.metadata()


    def metadata(self):

        track_data = {}

        # default name
        track_data['title'] = self.path[:self.path.rfind('.')]
        track_data['album'] = None
        track_data['genre'] = None
        track_data['artist'] = None

        #detect the current file type
        file_type = self.path[self.path.rfind('.'):]

        # handle FLAC files
        if file_type == ".flac":
            metadata = flac.FLAC(self.path)
            # print metadata
            try:
                track_data['title'] = metadata['title'][0]
                track_data['album'] = metadata['album'][0]
                track_data['genre'] = metadata['genre'][0]
                track_data['artist'] = metadata['artist'][0]
            except:
                pass
        #handle MP3 files
        if file_type == ".mp3":
            metadata = mp3.MP3(self.path)
            # print metadata
            try:
                if(metadata.has_key('TIT2')):
                    track_data['title'] = metadata['TIT2'].text[0]
                if(metadata.has_key('TALB')):
                    track_data['album'] = metadata['TALB'].text[0]
                if(metadata.has_key('TCON')):
                    track_data['genre'] = metadata['TCON'].text[0]
                if(metadata.has_key('TPE2')):
                    track_data['artist'] = metadata['TPE2'].text[0]
            except:
                pass

        return track_data


class TrackList:
    '''
    A class representing a "list" of music files
    '''
    def __init__(self):
        self.init()


    def scan(self, root_folder):
        '''
        Walks the given directory to find mp3 and flac music files
        '''
        #the tracks in the given (root) folder...
        tracks_in_folder = []

        # track counter
        i = 0

        #iterate over subdirectories, following symlinks
        for directory in os.walk(root_folder, followlinks=True):
            #for each file in the current directory
            for filename in directory[2]:
                # check the file extension
                if filename.endswith('.mp3') or filename.endswith('.flac'):
                    #set the track file path
                    current_track = Track(os.path.join(directory[0], filename))

                    #debug
                    print (current_track.path)

                    #set the track id, not unique:may change between different runs
                    current_track.id = i;

                    #append the current track
                    tracks_in_folder.append(current_track)

                    #increment the track id
                    i+=1
        return tracks_in_folder

    def addTracks(self, tracks):
        '''
        Adds the given (set) of tracks.
        '''
        for track in tracks:
            #reset the track id
            track.id = self.lastId
            #append the track
            self.tracks.append(track)
            #update the last track id
            self.lastId += 1

    def init(self):
        '''
        Init (clear) the tracks list.
        '''
        #the list
        self.tracks = []

        #the last index
        self.lastId = 0

    def search(self, tag_name = None, value= None):
        '''
        Searches for tracks having / containing the given value in the given tag
        '''

        #check if parameters are available
        if (tag_name != None) and (value != None):

            #the list of matching tracks
            matching_tracks = []

            #iterate over all available tracks
            for track in self.tracks:

                #apply filter
                if (track.data[tag_name] != None) and ((track.data[tag_name].lower() == value.lower()) or (track.data[tag_name].lower().find(value.lower()) > -1)):

                    #if the filter matches, add the track
                    matching_tracks.append(track)

        #return the set of matching tracks
        return matching_tracks

class Player:
    def __init__(self):
        #build the player
        self.player = Popen("mplayer -slave -quiet -nolirc -msglevel all=-1 -idle", stdin=PIPE, stdout=PIPE, shell=True)

    def play(self,filename):
        #play the file
        self.player.stdin.write("loadfile \"%s\"\n"%filename)

    def stop(self):
        #stop playing
        self.player.stdin.write("stop\n")

def main():
    # create a track list
    track_list = TrackList()
    player = Player()

    #prepare the command line holder
    cmd = ""

    #start the main loop cycle
    while(cmd != 'exit'):

        #read the command
        cmd_string = raw_input("cmd:\>");
        cmd_and_params = cmd_string.split();
        cmd = cmd_and_params[0].strip().lower()
        print cmd

        #handle commands
        if(cmd == "index"):
            #handle index command
            if(cmd_and_params[1]!=None):
                track_list.addTracks(track_list.scan(cmd_and_params[1].strip()))

        elif(cmd == "search"):
            #handle search
            if((len(cmd_and_params) == 3)and(cmd_and_params[1].strip()!=None)and(cmd_and_params[2].strip()!=None)):
                matching_tracks = track_list.search(cmd_and_params[1].strip(), cmd_and_params[2].strip())
                for track in matching_tracks:
                    print ("%d - %s"%(track.id,track.path))
                print("Found %d matching tracks"%len(matching_tracks))

        elif(cmd == "list"):
            #handle list
            for track in track_list.tracks:
                print ("%d - %s"%(track.id,track.data['title']))

        elif(cmd == "show"):
            #handle show tracks
            if(len(cmd_and_params) == 2):
                #get the track
                track = track_list.tracks[int(cmd_and_params[1].strip())]

                #check not None
                if(track!=None):
                    #print track details
                    print("###################################")
                    print("# track : %s"%track.path)
                    for key in track.data:
                        print ("# %s : %s"%(key, track.data[key]))
                    print("###################################")
                else:
                    print("Unknown track")


            pass
        elif(cmd == "exit"):
            #handle exit
            print ("Goodbye")
        elif(cmd == "play"):
            #handle play
            #check number of parameters
            if(len(cmd_and_params) == 2):
                #get the track
                track = track_list.tracks[int(cmd_and_params[1].strip())]

                #check not None
                if(track!=None):
                    player.play(track.path)
        elif(cmd == "stop"):
            player.stop()
        else:
            print("Unsupported command\n")
            pass # continue
#---------------------------
if __name__ == '__main__':
    main()
