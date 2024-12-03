#!/bin/bash

EWW_DIR="$HOME/.config/eww/whimsy"

update_eww_vol() {
    eww -c $EWW_DIR update volume=$(pamixer --get-volume) &
    eww -c $EWW_DIR update volumemute=$(pamixer --get-mute) &
}

update_eww_bri() {
    eww -c $EWW_DIR update brightness=$(brightnessctl -m | awk -F, '{print substr($4, 0, length($4)-1)}' | tr -d '%') &
}

popup() {
    eww -c $EWW_DIR update revealchangemode=$1
    count=$(eww -c $EWW_DIR get changeindcount)

    if [[ $count == 0 ]]; then 
        $EWW_DIR/scripts/hackslide changeindicate revealchange &
    fi

    eww -c $EWW_DIR update changeindcount=$((count+1))

    sleep 2 

    count=$(eww -c $EWW_DIR get changeindcount)
    eww -c $EWW_DIR update changeindcount=$((count-1))
    if [[ $count == 1 ]]; then 
        $EWW_DIR/scripts/hackslide changeindicate revealchange &
    fi
}

if [[ $1 == "incvol" ]]; then
    pamixer -i 5
    update_eww_vol
    popup "0"
elif [[ $1 == "decvol" ]]; then 
    pamixer -d 5
    update_eww_vol
    popup "0"
elif [[ $1 == "togvol" ]]; then 
    pamixer --toggle-mute
    update_eww_vol
    popup "0"
elif [[ $1 == "incbri" ]]; then 
    light -A 5
    update_eww_bri
    popup "1"
elif [[ $1 == "decbri" ]]; then 
    light -U 5
    update_eww_bri
    popup "1"
else 
    echo "???"
fi
