#!/usr/bin/sh

exec wl-paste -t text --watch clipman store &

swayidle -w \
	timeout 600 'swaylock -c 262626' \
	timeout 900 'swaymsg "output * dpms off"' \
		resume 'swaymsg "output * dpms on"' &

nm-applet --indicator &

# scratchpads
foot -a sterm &
foot -a sncmpcpp ncmpcpp &
foot -a sranger ranger &

pipewire &
wireplumber &
pipewire-pulse &

mpd &
mpDris2 &

$(which eww) daemon
$(which eww) --config ~/.config/eww/whimsy open-many bar notifypopup fakecornerl dock &
