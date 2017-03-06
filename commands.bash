#!/bin/bash

BINDIR="/home/dst/server_dst/bin"
PREFABBIN="prefabs.py" #should be in BINDIR
PREFABFILE="prefabs.txt" #should be in BINDIR

SCREENCMD='screen -S dst_server1 -p 0 -X stuff '

#Set some defaults
MAXPLAYERS=6
VALUE=100
PERCENT="1.0"

function getPlayer {
echo -n "Enter player number [1]..$MAXPLAYERS: "

read player

if [ -z $player ]; then
	player=1
fi

if [ $player -gt $MAXPLAYERS ] || [ $player -lt 1 ]; then
	echo Invalid player number
	exit 1
else
	PLAYER=$player
fi
return 0
}

function getQty {
echo -n "Enter quantity [1]: "

read qty

if [ -z $qty ] || [ $qty -lt 1 ]; then
	QTY="1"
else
	QTY=$qty
fi
return 0
}

function getItem {
echo -n "Enter item: "
read item

if [ -z $item ]; then
	echo Invalid item
	exit
else
	ITEM=$item
fi

return 0
}

function getPrefabs {
cd $BINDIR

if [ -e $PREFABFILE ]; then
	echo $BINDIR/$PREFABFILE already exists && return 1
	exit
fi

if [ ! -e $PREFABBIN]; then
	echo cannot find $BINDIR/$PREFABBIN && return 1
	exit
fi

$PREFABBIN

return 0
}

function updatePrefabs {
cd $BINDIR 

if [ -e $PREFABFILE ]; then
	rm $PREFABFILE || echo failed to delete $PREFABFILE && return 1
fi

getPrefabs
return 0
}

function give {

getItem
getPlayer
getQty

#echo screen -S dst_server1 -X stuff "c_select(AllPlayers[$PLAYER]) cgive(\"$ITEM\", $QTY)"
$SCREENCMD "c_select(AllPlayers[$PLAYER]) c_give(\"$ITEM\", $QTY)^M"
exit
}

function setSeason {
SEASONS="autumn winter spring summer"
select opt in $SEASONS; do
	if [ "$opt" = "autumn" ]; then
		SEASON="autumn"
	elif [ "$opt" = "winter" ]; then
		SEASON="winter"
	elif [ "$opt" = "spring" ]; then
		SEASON="spring"
	elif [ "$opt" = "summer" ]; then
		SEASON="summer"
	else
		echo invalid season
		exit
	fi
	$SCREENCMD "TheWorld:PushEvent(\"ms_setseason\",\"$SEASON\")^M"
	exit
done
	
return 0
}

function regen {
$SCREENCMD "c_regenerateworld()^M"
return 0
}

function rain {
ONOFF="On Off"
select opt in $ONOFF; do
	if [ "$opt" = "On" ]; then
		$SCREENCMD "TheWorld:PushEvent(\"ms_forceprecipitation\")^M"
		exit
	elif [ "$opt" = "Off" ]; then
		$SCREENCMD "TheWorld:PushEvent(\"ms_forceprecipitation\", false)^M"
		exit
	else
		echo "invalid choice"
		exit
	fi
done
}

function getValue {
read value

if [ -z $value ]; then
	value=100
elif [ $value -gt 100 ] || [ $value -lt 0 ]; then
	echo Invalid value
	exit 1
else
	VALUE=$value
fi
return 0
}

function val2pct {
if [ $VALUE -eq 100 ]; then
	PERCENT="1.0"
else
	PERCENT="0.$VALUE"
fi

return 0
}

function playerStats {
getPlayer

echo Select player attribute to manipulate
STATS="Health Hunger Sanity Moisture Temperature Godmode Supergodmode Speed"
select stat in $STATS; do
	CMD=${stat,,}
	if [ $stat = "Temperature" ]; then
		echo "Enter value 0-[100]: "
		getValue
		$SCREENCMD "c_select(AllPlayers[$PLAYER]) c_set$CMD($VALUE)^M"
		exit
	elif [ $stat = "Godmode" ]; then
		$SCREENCMD "c_select(AllPlayers[$PLAYER]) c_godmode()^M"
		exit
	elif [ $stat = "Supergodmode" ]; then
		$SCREENCMD "c_select(AllPlayers[$PLAYER]) c_supergodmode()^M"
		exit
	elif [ $stat = "Speed" ]; then
		echo "Enter speed multiplier [1] - 10: "
		read speed
		if [ -z $speed ]; then
			speed=1
		elif [ $speed -gt 10 ] || [ $speed -lt 1 ]; then
			echo Invalid speed value
			exit 1
		fi
		$SCREENCMD "c_select(AllPlayers[$PLAYER]) c_speedmult($speed)^M"
		exit
	else # Health, Hunger, Sanity, Moisture (all percents)
		echo "Enter percent 0-[100]: "
		getValue
		val2pct
		$SCREENCMD "c_select(AllPlayers[$PLAYER]) c_set$CMD($PERCENT)^M"
		exit
	fi
	echo $VALUE
	val2pct
	echo $PERCENT
	exit
done
}

function reveal {
$SCREENCMD 'local w,h = TheWorld.Map:GetSize();for _,v in pairs(AllPlayers) do for x=-w*4,w*4,35 do for y=-h*4,h*4,35 do v.player_classified.MapExplorer:RevealArea(x,0,y) end end end^M'

return 0
}

function mainMenu {
OPTIONS="Give Season Regen Rain Player Reveal Quit"
select opt in $OPTIONS; do
	if [ "$opt" = "Give" ]; then
		give
		exit
	elif [ "$opt" = "Season" ]; then
		setSeason
		exit
	elif [ "$opt" = "Regen" ]; then
		regen
		exit
	elif [ "$opt" = "Rain" ]; then
		rain
		exit
	elif [ "$opt" = "Player" ]; then
		reveal
		exit
	elif [ "$opt" = "Reveal" ]; then
		reveal
		exit
	elif [ "$opt" = "Quit" ]; then
		exit 0
	else
		echo invalid option
		exit
	fi
done
}

mainMenu
