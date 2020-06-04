#	name=Korg nanoKONTROL
# url=

# Version = 1.0

LONG_PRESS_TIME = 0.5 # Change how long a long press needs to be held for

ENABLE_SNAPPING = True # Change to False to prevent faders and knobs from snapping to default values
SNAP_RANGE = 0.03 # Will snap if within this disatnce of snap value

# Mixer snap values
MIXER_VOLUME_SNAP_TO = 0.8 # Snap mixer track volumes to 100%
MIXER_PAN_SNAP_TO = 0.0 # Snap mixer track pannings to Centred
MIXER_STEREO_SEP_SNAP_TO = 0.0 # Snap mixer track stereo separation to Original

# Channel rack snap values
CHANNEL_VOLUME_SNAP_TO = 0.78125 # Snap channel volumes to ~= 78% (FL Default)
CHANNEL_PAN_SNAP_TO = 0.0

#
# MAKE EDITS BELOW THIS POINT AT YOUR OWN RISK
#

import time

import patterns
import channels
import mixer
import device
import transport
import arrangement
import general
import launchMapPages
import playlist
import ui
import screen

import midi
import utils

EventNameT = ['Note Off', 'Note On ', 'Key Aftertouch', 'Control Change','Program Change',  'Channel Aftertouch', 'Pitch Bend', 'System Message' ]


# Function for outputting output
def handleOutput(str):
	if str is not "": 
		print(str)
		ui.setHintMsg(str)

# Functions for mixer

# Returns name of mixer track
def getMixerTrackName(trackNum):
	if trackNum < 0: trackNum = 126
	if trackNum > 126: trackNum = 0
	return mixer.getTrackName(trackNum)  + " (" + str(trackNum) + ")"

# Toggles solo on mixer track
def mixerToggleSolo(selectedTrackNum):
	mixer.soloTrack(selectedTrackNum)
	if mixer.isTrackSolo(selectedTrackNum) is 1: return "Mixer: Solo track: " + getMixerTrackName(selectedTrackNum)
	else: return "Mixer: Unsolo track: " + getMixerTrackName(selectedTrackNum)

# Toggles mute on mixer track
def mixerToggleMute(selectedTrackNum):
	mixer.muteTrack(selectedTrackNum)
	if mixer.isTrackMuted(selectedTrackNum) is 1: return "Mixer: Mute track: " + getMixerTrackName(selectedTrackNum)
	else: return "Mixer: Unmute track: " + getMixerTrackName(selectedTrackNum)

# Adjusts fader on mixer track
def mixerAdjustFader(selectedTrackNum, data):
	parameter = float(data)/127.0
	hasSnapped = False
	if ENABLE_SNAPPING is True:
		if parameter >= (MIXER_VOLUME_SNAP_TO - SNAP_RANGE) and parameter <= (MIXER_VOLUME_SNAP_TO + SNAP_RANGE):
			parameter = MIXER_VOLUME_SNAP_TO
			hasSnapped = True
	mixer.setTrackVolume(selectedTrackNum, parameter)
	ret = "Mixer: Adjust " + getMixerTrackName(selectedTrackNum) + " volume to " + str(round(parameter / 0.8 * 100, 0)) + "%"
	if hasSnapped is True: ret += " [Snapped]"
	return ret

# Adjusts panning on mixer track
def mixerAdjustPan(selectedTrackNum, data):
	parameter = float(data - 63.5)/63.5
	hasSnapped = False
	if ENABLE_SNAPPING is True:
		if parameter >= (MIXER_PAN_SNAP_TO - SNAP_RANGE) and parameter <= (MIXER_PAN_SNAP_TO + SNAP_RANGE):
			parameter = MIXER_PAN_SNAP_TO
			hasSnapped = True
	mixer.setTrackPan(selectedTrackNum, parameter)
	ret ="Mixer: Adjust " + getMixerTrackName(selectedTrackNum) + " panning to "
	if parameter < 0: ret += str(-round(parameter * 100, 0)) + "% Left"
	elif parameter > 0: ret += str(round(parameter * 100, 0)) + "% Right"
	else: ret += "Centred"

	if hasSnapped is True: ret += " [Snapped]"
	return ret

# Adjusts stereo separation on mixer track - Currently doesn't work
def mixerAdjustStereoSep(selectedTrackNum, data):
	parameter = float(data - 63.5)/63.5
	hasSnapped = False
	if ENABLE_SNAPPING is True:
		if parameter >= (MIXER_STEREO_SEP_SNAP_TO - SNAP_RANGE) and parameter <= (MIXER_STEREO_SEP_SNAP_TO + SNAP_RANGE):
			parameter = MIXER_STEREO_SEP_SNAP_TO
			hasSnapped = True
	mixer.setTrackStereoSeparation(selectedTrackNum, parameter)
	ret ="Mixer: Adjust " + getMixerTrackName(selectedTrackNum) + " stereo separation to "
	if parameter < 0: ret += str(-round(parameter * 100, 0)) + "% Separated"
	elif parameter > 0: ret += str(round(parameter * 100, 0)) + "% Merged"
	else: ret += "Original"

	if hasSnapped is True: ret += " [Snapped]"
	return ret

# Select mixer track given channel
def mixerTrackSelect(channelNum):
	mixer.deselectAll()
	mixer.selectTrack(channels.getTargetFxTrack(channelNum))

# Functions for channel rack

# Returns name of channel
def getChannelName(channelNum):
	return channels.getChannelName(channelNum)

# Toggles solo on channel
def channelToggleSolo(selectedChannelNum):
	channels.soloChannel(selectedChannelNum)
	if channels.isChannelSolo(selectedChannelNum) is 1: return "Channel rack: Solo channel: " + getChannelName(selectedChannelNum)
	else: return "Channel rack: Unsolo channel: " + getChannelName(selectedChannelNum)

# Toggles mute on channel
def channelToggleMute(selectedChannelNum):
	channels.muteChannel(selectedChannelNum)
	if channels.isChannelMuted(selectedChannelNum) is 1: return "Channel rack: Mute track: " + getChannelName(selectedChannelNum)
	else: return "Channel rack: Unmute track: " + getChannelName(selectedChannelNum)

# Adjusts volume on channel
def channelAdjustVolume(selectedChannelNum, data):
	parameter = float(data)/127.0
	hasSnapped = False
	if ENABLE_SNAPPING is True:
		if parameter >= (CHANNEL_VOLUME_SNAP_TO - SNAP_RANGE) and parameter <= (CHANNEL_VOLUME_SNAP_TO + SNAP_RANGE):
			parameter = CHANNEL_VOLUME_SNAP_TO
			hasSnapped = True
	channels.setChannelVolume(selectedChannelNum, parameter)
	ret = "Channel rack: Adjust " + getChannelName(selectedChannelNum) + " volume to " + str(round(parameter * 100, 0)) + "%"
	if hasSnapped is True: ret += " [Snapped]"
	return ret

# Adjusts panning on mixer track
def channelAdjustPan(selectedChannelNum, data):
	parameter = float(data - 63.5)/63.5
	hasSnapped = False
	if ENABLE_SNAPPING is True:
		if parameter >= (CHANNEL_PAN_SNAP_TO - SNAP_RANGE) and parameter <= (CHANNEL_PAN_SNAP_TO + SNAP_RANGE):
			parameter = CHANNEL_PAN_SNAP_TO
			hasSnapped = True
	channels.setChannelPan(selectedChannelNum, parameter)
	ret ="Channel rack: Adjust " + getChannelName(selectedChannelNum) + " panning to "
	if parameter < 0: ret += str(-round(parameter * 100, 0)) + "% Left"
	elif parameter > 0: ret += str(round(parameter * 100, 0)) + "% Right"
	else: ret += "Centred"

	if hasSnapped is True: ret += " [Snapped]"
	return ret

# Select channel given mixer track - currently doesn't work
def channelSelect(MixerTrackNum):
	return

class TGeneric():
	def __init__(self):
		return

	def OnInit(self):

		global scene
		global loopDown
		global loopInterrupt

		# Set scene to 1
		# device.midiOutMsg(0xF0 + (0 << 8) + (0 << 16))
		scene = 1

		# set loop modifiers
		loopDown = False
		loopInterrupt = False

		handleOutput("Controller initialised")
		

	def OnDeInit(self):
		handleOutput("Controller deinitialised")

	def OnMidiIn(self, event):
		# print ("Event: {:X} {:X} {:2X} {} {:2X}".format(event.status, event.data1, event.data2,  EventNameT[(event.status - 0x80) // 16] + ': '+  utils.GetNoteName(event.data1), int(hex(event.data2), 16)))
		
		# Create output string
		output = ""

		event.handled = False
		global loopDown
		global loopInterrupt

		# Set has snapped flag
		hasSnapped = False

		# Process Long Presses:

		# Stop Button
		if (event.status is 0xB0 and event.data1 is 0x2E):
			global stop_PressTime
			global stop_LiftTime

			# Press - Start timer
			if event.data2 is 0x7F:
				stop_PressTime = time.perf_counter()
			# Lift - Stop timer
			elif event.data2 is 0x00:
				stop_LiftTime = time.perf_counter()
				if (stop_LiftTime - stop_PressTime) >= LONG_PRESS_TIME: 
					ui.escape()
					output += "UI: Escape"
					event.handled = True

		if event.handled is True: 
			handleOutput(output)
			return

		# In popup
		if ui.isInPopupMenu() is 1 and loopDown is False:
			output += "[In popup menu] "
			# Currently this is always inactive?
		
		if event.handled is True: 
			handleOutput(output)
			return

		# In Playlist
		if ui.getFocused(2) is 1 and loopDown is False:
			
			# Forward Button
			if (event.status is 0xB0 and event.data1 is 0x30):
				# Press - No action if markers exist
				if event.data2 is 0x7F and arrangement.getMarkerName(0) is not "":
					event.handled = True
				# Lift - Skip to next marker, only if markers exist
				elif event.data2 is 0x00 and arrangement.getMarkerName(0) is not "":
					transport.markerJumpJog(1)
					output += "Transport: Jump to next marker"
					event.handled = True

			# Back Button
			if (event.status is 0xB0 and event.data1 is 0x2F):
				# Press - No action if markers exist
				if event.data2 is 0x7F and arrangement.getMarkerName(0) is not "":
					event.handled = True
				# Lift - Skip to previous marker, only if markers exist
				elif event.data2 is 0x00 and arrangement.getMarkerName(0) is not "":
					transport.markerJumpJog(-1)
					output += "Transport: Jump to previous marker"
					event.handled = True

		if event.handled is True: 
			handleOutput(output)
			return

		# In Mixer
		if ui.getFocused(0) is 1 and loopDown is False:
			selectedTrack = mixer.trackNumber()

			# Record Button
			if (event.status is 0xB0 and event.data1 is 0x2C):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Toggle track arm
				elif event.data2 is 0x00:
					mixer.armTrack(selectedTrack)
					if mixer.isTrackArmed(selectedTrack) is 1: output += "Mixer: Armed track: " + getMixerTrackName(selectedTrack)
					else: output += "Mixer: Disarmed track: " + getMixerTrackName(selectedTrack)
					event.handled = True

			# Forward Button
			if (event.status is 0xB0 and event.data1 is 0x30):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Next track
				elif event.data2 is 0x00:
					ui.next()
					output += "Mixer: Selected next track: " + getMixerTrackName(selectedTrack + 1)

					event.handled = True

			# Back Button
			if (event.status is 0xB0 and event.data1 is 0x2F):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Previous track
				elif event.data2 is 0x00:
					ui.previous()
					output += "Mixer: Selected previous track: " + getMixerTrackName(selectedTrack - 1)

					event.handled = True

			# Fader, knob and buttons #9 act on the selected track

			# Upper button 9
			if (event.status is 0xB0 and (event.data1 is 0x1F or event.data1 is 0x4B or event.data1 is 0x73)) or (event.status is 0xB8 and event.data1 is 0x10):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Solo track (in scene 4, the buttons toggle automatically)
				if event.data2 is 0x00 or event.status is 0xB8:
					output += mixerToggleSolo(selectedTrack)
					event.handled = True

			# Lower button 9
			if (event.status is 0xB0 and (event.data1 is 0x29 or event.data1 is 0x54 or event.data1 is 0x7C)) or (event.status is 0xB8 and event.data1 is 0x11):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Mute track (in scene 4, the buttons toggle automatically)
				if event.data2 is 0x00 or event.status is 0xB8:
					output += mixerToggleMute(selectedTrack)
					event.handled = True

			# Fader 9 - Selected volume
			if (event.status is 0xB0 and (event.data1 is 0x0D or event.data1 is 0x38 or event.data1 is 0x5D)) or (event.status is 0xB8 and event.data1 is 0x07):
				output += mixerAdjustFader(selectedTrack, event.data2)
				event.handled = True

			# Knob 9 - Selected pan
			if (event.status is 0xB0 and (event.data1 is 0x16 or event.data1 is 0x42 or event.data1 is 0x6A)) or (event.status is 0xB8 and event.data1 is 0x0A):
				output += mixerAdjustPan(selectedTrack, event.data2)
				event.handled = True

			# Faders, knobs and buttons #1-8 act on tracks 1-8 respectively

			# Upper button 1
			if (event.status is 0xB0 and (event.data1 is 0x17 or event.data1 is 0x43 or event.data1 is 0x6B)) or (event.status is 0xB0 and event.data1 is 0x10):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Solo track (in scene 4, the buttons toggle automatically)
				if event.data2 is 0x00 or (event.status is 0xB0 and event.data1 is 0x10 and event.data2 is 0x7F):
					output += mixerToggleSolo(1)
					event.handled = True

			# Lower button 1
			if (event.status is 0xB0 and (event.data1 is 0x21 or event.data1 is 0x4C or event.data1 is 0x74)) or (event.status is 0xB0 and event.data1 is 0x11):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Mute track (in scene 4, the buttons toggle automatically)
				if event.data2 is 0x00 or (event.status is 0xB0 and event.data1 is 0x11 and event.data2 is 0x7F):
					output += mixerToggleMute(1)
					event.handled = True

			# Upper button 2
			if (event.status is 0xB0 and (event.data1 is 0x18 or event.data1 is 0x44 or event.data1 is 0x6C)) or (event.status is 0xB1 and event.data1 is 0x10):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Solo track (in scene 4, the buttons toggle automatically)
				if event.data2 is 0x00 or (event.status is 0xB1 and event.data1 is 0x10):
					output += mixerToggleSolo(2)
					event.handled = True

			# Lower button 2
			if (event.status is 0xB0 and (event.data1 is 0x22 or event.data1 is 0x4D or event.data1 is 0x75)) or (event.status is 0xB1 and event.data1 is 0x11):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Mute track (in scene 4, the buttons toggle automatically)
				if event.data2 is 0x00 or (event.status is 0xB2 and event.data1 is 0x11):
					output += mixerToggleMute(2)
					event.handled = True

			# Upper button 3
			if (event.status is 0xB0 and (event.data1 is 0x19 or event.data1 is 0x45 or event.data1 is 0x6D)) or (event.status is 0xB2 and event.data1 is 0x10):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Solo track (in scene 4, the buttons toggle automatically)
				if event.data2 is 0x00 or (event.status is 0xB2 and event.data1 is 0x10):
					output += mixerToggleSolo(3)
					event.handled = True

			# Lower button 3
			if (event.status is 0xB0 and (event.data1 is 0x23 or event.data1 is 0x4E or event.data1 is 0x76)) or (event.status is 0xB2 and event.data1 is 0x11):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Mute track (in scene 4, the buttons toggle automatically)
				if event.data2 is 0x00 or (event.status is 0xB2 and event.data1 is 0x11):
					output += mixerToggleMute(3)
					event.handled = True

			# Upper button 4
			if (event.status is 0xB0 and (event.data1 is 0x1A or event.data1 is 0x46 or event.data1 is 0x6E)) or (event.status is 0xB3 and event.data1 is 0x10):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Solo track (in scene 4, the buttons toggle automatically)
				if event.data2 is 0x00 or (event.status is 0xB3 and event.data1 is 0x10):
					output += mixerToggleSolo(4)
					event.handled = True

			# Lower button 4
			if (event.status is 0xB0 and (event.data1 is 0x24 or event.data1 is 0x4F or event.data1 is 0x77)) or (event.status is 0xB3 and event.data1 is 0x11):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Mute track (in scene 4, the buttons toggle automatically)
				if event.data2 is 0x00 or (event.status is 0xB3 and event.data1 is 0x11):
					output += mixerToggleMute(4)
					event.handled = True

			# Upper button 5
			if (event.status is 0xB0 and (event.data1 is 0x1B or event.data1 is 0x47 or event.data1 is 0x6F)) or (event.status is 0xB4 and event.data1 is 0x10):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Solo track (in scene 4, the buttons toggle automatically)
				if event.data2 is 0x00 or (event.status is 0xB4 and event.data1 is 0x10):
					output += mixerToggleSolo(5)
					event.handled = True

			# Lower button 5
			if (event.status is 0xB0 and (event.data1 is 0x25 or event.data1 is 0x50 or event.data1 is 0x78)) or (event.status is 0xB4 and event.data1 is 0x11):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Mute track (in scene 4, the buttons toggle automatically)
				if event.data2 is 0x00 or (event.status is 0xB4 and event.data1 is 0x11):
					output += mixerToggleMute(5)
					event.handled = True

			# Upper button 6
			if (event.status is 0xB0 and (event.data1 is 0x1C or event.data1 is 0x48 or event.data1 is 0x70)) or (event.status is 0xB5 and event.data1 is 0x10):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Solo track (in scene 4, the buttons toggle automatically)
				if event.data2 is 0x00 or (event.status is 0xB5 and event.data1 is 0x10):
					output += mixerToggleSolo(6)
					event.handled = True

			# Lower button 6
			if (event.status is 0xB0 and (event.data1 is 0x26 or event.data1 is 0x51 or event.data1 is 0x79)) or (event.status is 0xB5 and event.data1 is 0x11):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Mute track (in scene 4, the buttons toggle automatically)
				if event.data2 is 0x00 or (event.status is 0xB5 and event.data1 is 0x11):
					output += mixerToggleMute(6)
					event.handled = True

			# Upper button 7
			if (event.status is 0xB0 and (event.data1 is 0x1D or event.data1 is 0x49 or event.data1 is 0x71)) or (event.status is 0xB6 and event.data1 is 0x10):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Solo track (in scene 4, the buttons toggle automatically)
				if event.data2 is 0x00 or (event.status is 0xB6 and event.data1 is 0x10):
					output += mixerToggleSolo(7)
					event.handled = True

			# Lower button 7
			if (event.status is 0xB0 and (event.data1 is 0x27 or event.data1 is 0x52 or event.data1 is 0x7A)) or (event.status is 0xB6 and event.data1 is 0x11):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Mute track (in scene 4, the buttons toggle automatically)
				if event.data2 is 0x00 or (event.status is 0xB6 and event.data1 is 0x11):
					output += mixerToggleMute(7)
					event.handled = True

			# Upper button 8
			if (event.status is 0xB0 and (event.data1 is 0x1E or event.data1 is 0x4A or event.data1 is 0x72)) or (event.status is 0xB7 and event.data1 is 0x10):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Solo track (in scene 4, the buttons toggle automatically)
				if event.data2 is 0x00 or (event.status is 0xB7 and event.data1 is 0x10):
					output += mixerToggleSolo(8)
					event.handled = True

			# Lower button 8
			if (event.status is 0xB0 and (event.data1 is 0x28 or event.data1 is 0x53 or event.data1 is 0x7B)) or (event.status is 0xB7 and event.data1 is 0x11):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Mute track (in scene 4, the buttons toggle automatically)
				if event.data2 is 0x00 or (event.status is 0xB7 and event.data1 is 0x11):
					output += mixerToggleMute(8)
					event.handled = True

			# Fader 1 - Track 1 volume
			if event.status is 0xB0 and (event.data1 is 0x02 or event.data1 is 0x2A or event.data1 is 0x55 or event.data1 is 0x07):
				output += mixerAdjustFader(1, event.data2)
				event.handled = True

			# Knob 1 - Track 1 pan
			if event.status is 0xB0 and (event.data1 is 0x0E or event.data1 is 0x39 or event.data1 is 0x5E or event.data1 is 0x0A):
				output += mixerAdjustPan(1, event.data2)
				event.handled = True

			# Fader 2 - Track 2 volume
			if (event.status is 0xB0 and (event.data1 is 0x03 or event.data1 is 0x2B or event.data1 is 0x56)) or (event.status is 0xB1 and event.data1 is 0x07):
				output += mixerAdjustFader(2, event.data2)
				event.handled = True

			# Knob 2 - Track 2 pan
			if (event.status is 0xB0 and (event.data1 is 0x0F or event.data1 is 0x3A or event.data1 is 0x5F)) or (event.status is 0xB1 and event.data1 is 0x0A):
				output += mixerAdjustPan(2, event.data2)
				event.handled = True

			# Fader 3 - Track 3 volume
			if (event.status is 0xB0 and (event.data1 is 0x04 or event.data1 is 0x32 or event.data1 is 0x57)) or (event.status is 0xB2 and event.data1 is 0x07):
				output += mixerAdjustFader(3, event.data2)
				event.handled = True

			# Knob 3 - Track 3 pan
			if ((event.status is 0xB0 and (event.data1 is 0x10 or event.data1 is 0x3B or event.data1 is 0x60)) or (event.status is 0xB2 and event.data1 is 0x0A)) and event.handled is False:
				output += mixerAdjustPan(3, event.data2)
				event.handled = True

			# Fader 4 - Track 4 volume
			if (event.status is 0xB0 and (event.data1 is 0x05 or event.data1 is 0x33 or event.data1 is 0x58)) or (event.status is 0xB3 and event.data1 is 0x07):
				output += mixerAdjustFader(4, event.data2)
				event.handled = True

			# Knob 4 - Track 4 pan
			if ((event.status is 0xB0 and (event.data1 is 0x11 or event.data1 is 0x3C or event.data1 is 0x61)) or (event.status is 0xB3 and event.data1 is 0x0A)) and event.handled is False:
				output += mixerAdjustPan(4, event.data2)
				event.handled = True

			# Fader 5 - Track 5 volume
			if (event.status is 0xB0 and (event.data1 is 0x06 or event.data1 is 0x34 or event.data1 is 0x59)) or (event.status is 0xB4 and event.data1 is 0x07):
				output += mixerAdjustFader(5, event.data2)
				event.handled = True

			# Knob 5 - Track 5 pan
			if (event.status is 0xB0 and (event.data1 is 0x12 or event.data1 is 0x3D or event.data1 is 0x66)) or (event.status is 0xB4 and event.data1 is 0x0A):
				output += mixerAdjustPan(5, event.data2)
				event.handled = True

			# Fader 6 - Track 6 volume
			if (event.status is 0xB0 and (event.data1 is 0x08 or event.data1 is 0x35 or event.data1 is 0x5A)) or (event.status is 0xB5 and event.data1 is 0x07):
				output += mixerAdjustFader(1, event.data2)
				event.handled = True

			# Knob 6 - Track 6 pan
			if (event.status is 0xB0 and (event.data1 is 0x13 or event.data1 is 0x3E or event.data1 is 0x67)) or (event.status is 0xB5 and event.data1 is 0x0A):
				output += mixerAdjustPan(6, event.data2)
				event.handled = True

			# Fader 7 - Track 7 volume
			if (event.status is 0xB0 and (event.data1 is 0x09 or event.data1 is 0x36 or event.data1 is 0x5B)) or (event.status is 0xB6 and event.data1 is 0x07):
				output += mixerAdjustFader(1, event.data2)
				event.handled = True

			# Knob 7 - Track 7 pan
			if (event.status is 0xB0 and (event.data1 is 0x14 or event.data1 is 0x3F or event.data1 is 0x68)) or (event.status is 0xB6 and event.data1 is 0x0A):
				output += mixerAdjustPan(7, event.data2)
				event.handled = True

			# Fader 8 - Track 8 volume
			if (event.status is 0xB0 and (event.data1 is 0x0C or event.data1 is 0x37 or event.data1 is 0x5C)) or (event.status is 0xB7 and event.data1 is 0x07):
				output += mixerAdjustFader(1, event.data2)
				event.handled = True

			# Knob 8 - Track 8 pan
			if (event.status is 0xB0 and (event.data1 is 0x15 or event.data1 is 0x41 or event.data1 is 0x69)) or (event.status is 0xB7 and event.data1 is 0x0A):
				output += mixerAdjustPan(8, event.data2)
				event.handled = True

		if event.handled is True: 
			handleOutput(output)
			return

		# In Channel rack
		if ui.getFocused(1) is 1 and loopDown is False:
			selectedChannel = channels.channelNumber()

			# Forward Button
			if (event.status is 0xB0 and event.data1 is 0x30):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Next track
				elif event.data2 is 0x00:
					ui.next()
					mixerTrackSelect(channels.channelNumber())
					output += "Channel rack: Select next track: " + getChannelName(channels.channelNumber())

					event.handled = True

			# Back Button
			if (event.status is 0xB0 and event.data1 is 0x2F):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Previous track
				elif event.data2 is 0x00:
					ui.previous()
					mixerTrackSelect(channels.channelNumber())
					output += "Channel rack: Select previous track: " + getChannelName(channels.channelNumber())

					event.handled = True
			
			# Fader, knob and buttons #9 act on the selected channel

			# Upper button 9
			if (event.status is 0xB0 and (event.data1 is 0x1F or event.data1 is 0x4B or event.data1 is 0x73)) or (event.status is 0xB8 and event.data1 is 0x10):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Solo channel (in scene 4, the buttons toggle automatically)
				if event.data2 is 0x00 or event.status is 0xB8:
					output += channelToggleSolo(selectedChannel)
					event.handled = True

			# Lower button 9
			if (event.status is 0xB0 and (event.data1 is 0x29 or event.data1 is 0x54 or event.data1 is 0x7C)) or (event.status is 0xB8 and event.data1 is 0x11):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Mute track (in scene 4, the buttons toggle automatically)
				if event.data2 is 0x00 or event.status is 0xB8:
					output += channelToggleMute(selectedChannel)
					event.handled = True

			# Fader 9 - Selected volume
			if (event.status is 0xB0 and (event.data1 is 0x0D or event.data1 is 0x38 or event.data1 is 0x5D)) or (event.status is 0xB8 and event.data1 is 0x07):
				output += channelAdjustVolume(selectedChannel, event.data2)
				event.handled = True

			# Knob 9 - Selected pan
			if (event.status is 0xB0 and (event.data1 is 0x16 or event.data1 is 0x42 or event.data1 is 0x6A)) or (event.status is 0xB8 and event.data1 is 0x0A):
				output += channelAdjustPan(selectedChannel, event.data2)
				event.handled = True

			# Maybe include step editor here (when I figure out lights)

		if event.handled is True: 
			handleOutput(output)
			return

		# In Browser
		if ui.getFocused(4) is 1 and loopDown is False:

			# Play Button
			if (event.status is 0xB0 and event.data1 is 0x2D):
				# Press - Play sample/expand menu
				if event.data2 is 0x7F:
					ui.next()
					ui.previous()
					ui.right()
					output += "Browser: Select"
					event.handled = True
				# Lift - No action
				elif event.data2 is 0x00:
					event.handled = True
			
			# Forward Button
			if (event.status is 0xB0 and event.data1 is 0x30):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Next item
				elif event.data2 is 0x00:
					ui.next()
					output += "Browser: Next"

					event.handled = True

			# Back Button
			if (event.status is 0xB0 and event.data1 is 0x2F):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Previous item
				elif event.data2 is 0x00:
					ui.previous()
					output += "Browser: Previous"

					event.handled = True

			# Stop Button
			if (event.status is 0xB0 and event.data1 is 0x2E):
				# Press - No action
				if event.data2 is 0x7F:
					event.handled = True
				# Lift - Collapse menu
				elif event.data2 is 0x00:
					ui.left()
					output += "Browser: Collapse"

					event.handled = True

		if event.handled is True: 
			handleOutput(output)
			return

		# Default Actions:

		# Play Button
		if (event.status is 0xB0 and event.data1 is 0x2D):
			loopInterrupt = True
			# Press - No action
			if event.data2 is 0x7F:
				event.handled = True
			# Lift - Play/Pause
			elif event.data2 is 0x00:
				transport.start()
				if transport.isPlaying() is 1: output += "Transport: Play"
				else: output += "Transport: Pause"

				event.handled = True
			
		# Stop Button
		if (event.status is 0xB0 and event.data1 is 0x2E):
			loopInterrupt = True
			# Press - No action
			if event.data2 is 0x7F:
				event.handled = True
			# Lift - Stop
			elif event.data2 is 0x00:
				transport.stop()
				output += "Transport: Stop"

				event.handled = True

		# Forward Button
		if (event.status is 0xB0 and event.data1 is 0x30):
			loopInterrupt = True
			# Press - Start FF
			if event.data2 is 0x7F:
				transport.fastForward(2)
				event.handled = True
				output += "Transport: Fast Forward: Begin"
			# Lift - End FF
			elif event.data2 is 0x00:
				transport.fastForward(0)
				output += "Transport: Fast Forward: End"
				event.handled = True

		# Back Button
		if (event.status is 0xB0 and event.data1 is 0x2F):
			# Press - Start Rew
			if event.data2 is 0x7F:
				transport.rewind(2)
				event.handled = True
				output += "Transport: Rewind: Begin"
			# Lift - End Rew
			elif event.data2 is 0x00:
				transport.rewind(0)
				output += "Transport: Rewind: End"
				event.handled = True

		# Record Button
		if (event.status is 0xB0 and event.data1 is 0x2C):
			loopInterrupt = True
			# Press - No action
			if event.data2 is 0x7F:
				event.handled = True
			# Lift - Toggle Recording
			elif event.data2 is 0x00:
				transport.record()
				if transport.isRecording() is 1: output += "Transport: Recording Enabled"
				else: output += "Transport: Recording Disabled"
				event.handled = True

		# Loop Button
		if (event.status is 0xB0 and event.data1 is 0x31):
			# Press - Set Loop flags
			if event.data2 is 0x7F:
				# Set flags for loop modifier commands
				loopDown = True
				loopInterrupt = False
				event.handled = True

			# Lift - Toggle Loop if no action taken
			elif event.data2 is 0x00: 
				event.handled = True
				loopDown = False
				if loopInterrupt is False:
					transport.setLoopMode()
					if transport.getLoopMode() is 1: output += "Transport: Loop Mode: Song"
					else: output += "Transport: Loop Mode: Pattern"

		# Scene Change
		"""
		if event.status is 0xF0:
			global scene
			scene += 1
			if scene is 5:
				scene = 1

			windowToShow = -1
			if scene is 1: 
				windowToShow = 2 # Playlist
				output += "Scene: Playlist"
			if scene is 2: 
				windowToShow = 1 # Channel Rack
				output += "Scene: Channel Rack"
			if scene is 3: 
				windowToShow = 3 # Piano roll
				output += "Scene: Piano Roll"
			if scene is 4: 
				windowToShow = 0 # Mixer
				output += "Scene: Mixer"

			ui.showWindow(windowToShow)
			event.handled = True
		"""

		if event.handled is True: 
			handleOutput(output)
			return

		# Event not recognised
		if event.handled is False:
			print ("Unknown Event: {:X} {:X} {:2X} {} {:2X}".format(event.status, event.data1, event.data2,  EventNameT[(event.status - 0x80) // 16] + ': '+  utils.GetNoteName(event.data1), int(hex(event.data2), 16)))



Generic = TGeneric()

def OnInit():
	Generic.OnInit()
	

def OnDeInit():
	Generic.OnDeInit()


def OnMidiIn(event):
	Generic.OnMidiIn(event)