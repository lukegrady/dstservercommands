#!/usr/bin/env python3

'''Don't Starve Together Dedicated Server Interface

Use this program to interface with a dedicated DST server
'''

import subprocess
import sys
import re
import requests

def get_prefabs():
    '''Scrape Don't Starve wiki for prefab codes

    Returns:
        List of prefab tuples (link, name, spawn_code)
    '''
    url = 'http://dontstarve.wikia.com/wiki/Console/Prefab_List'

    response = requests.get(url)
    raw_text = response.text

    # This regex isn't perfect but it works for most everything
    # A notable place where it DOESN'T work is for Shipwrecked prefabs
    pattern = (r'^<td class="xl65" style="height: 20px; height:15.0pt">'
               r'(?:<a href="(.+)" title.+>)?([\s\w]+)(?:</a>)?\n</td>'
               r'<td>(\w+)$')
    matches = re.findall(pattern, raw_text, flags=re.MULTILINE)

    prefabs = []
    for match in matches:
        prefabs.append(match)

    return prefabs


def get_val(user_prompt=None, def_val=None, min_val=None, max_val=None):
    '''Query user for quantity (integer)

    Ask user for quantity

    Args:
        user_prompt: string (optional) that is displayed to user before prompt
        def_qty: int (optional, default = 1) default value for quantity used
            if user does not input one
        min_qty: int (optional) used to validate user input
        max_qty: int (optional) used to validate user input

    Returns:
        An integer quantity

    Raises:
        ValueError: If value entered is not an integer representation
    '''
    if not user_prompt:
        if def_val:
            user_prompt = 'Enter quantity [default=' + def_val + ']: '
        else:
            user_prompt = 'Enter quantity: '

    val = input(user_prompt)

    if not val:
        if def_val:
            val = def_val

    if min_val > val:
        print('Invalid value: User-entered {} is greater '
              'than minimum {}'.format(val, min_val))
    if max_val < val:
        print('Invalid quantity: User-entered {} is less than '
              'than maximum {}'.format(val, max_val))

    return val


def give_item(item=None, qty=None):
    '''Give player an item

    Builds command for remote server to give players an item

    Args:
        item: string (optional). item to give (look up DST prefabs for list)
        qty: string (optional). number/quantity of items to give

    Returns:
        command: string to be passed to screen session running DST server
    '''
    if not item:
        item = get_val()
    if not qty:
        qty = str(int(get_val()))

    command = ('c_give(\"' + item + '\"' + qty + ')^M')

    return command


def set_season(season=None):
    '''Set season

    Build server-side command to change season

    Args:
        season: string (optional). season to change to

    Returns:
        command: string to be passed to screen session running DST server
    '''
    if not season:
        season = input('Enter season to change to: ')

    valid_seasons = ['autumn', 'winter', 'spring', 'summer']

    if season not in valid_seasons:
        print('Invalid Entry: Season [{}] not found'.format(season))
        sys.exit(1)

    command = 'TheWorld:PushEvent(\"ms_setseason\",\"' + season + '\")^M'

    return command


def regenerate():
    '''Regenerate world

    Returns: command string to reset world
    '''
    return 'c_regenerateworld()^M'


def turn_rain_on():
    '''Make it start raining

    Returns: command string to make it start raining
    '''
    return 'TheWorld:PushEvent(\"ms_forceprecipitation\")^M'


def turn_rain_off():
    '''Make it stop raining

    Returns: command string to make it stop raining
    '''
    return 'TheWorld:PushEvent(\"ms_forceprecipitation\", false)^M'


def toggle_god_mode():
    '''Toggle god mode for selected player

    Returns:
        command string to toggle god mode for player
    '''
    return 'c_godmode()^M'


def toggle_super_god_mode():
    '''Toggle super god mode for selected user

    Returns:
        command string to toggle super god mode for player
    '''
    return 'c_supergodmode()^M'


def set_health(health_pct=None):
    '''Set player health to given percent of max

    Args:
        health_pct: float (optional). percent (between 0 and 1) that
            will be multiplied to player max health stat to determine
            new level of health

    Returns:
        command string to set player health
    '''
    if not health_pct:
        health_pct = str(float(get_val('Enter % of max health',
                                       '[1.0 = 100%]: ', 1.0)))
    return 'c_sethealth(' + health_pct + ')^M')

def set_speedmult(multiplier=None):
    '''Set player speed multiplier

    Args:
        multiplier: int (optional). multiplier (between 1 and 10) that
            will be applied to player speed

    Returns:
        command string to set player speed multiplier
    '''
    if not multiplier:
        multiplier = str(int(get_val('Enter speed multiplier [1 - 20]'
                                     '(default=1): ', 1)))

    return ('c_speedmult(' + multiplier + ')^M')

def kill_player(player_name):
    '''Kill specified player

    Args:
        player_name: string (optional). player name to kill

    Returns:
        command string to kill player
    '''
    return "UserToPlayer('" + player_name + "'):PushEvent('death')^M"

def despawn_player(player_name):
    '''Despawn specified player

    Args:
        player_name: string (optional). player to despawn

    Returns:
        command string to despawn player (and return them to character select
        screen
    '''
    return "c_despawn(UserToPlayer('" + player_name + "')^M"

def main():
    '''Main function

    Interpret arguments or display menu-driven options
    '''
    if len(sys.argv[1:]) < 1:
        print('usage: {} command'.format(sys.argv[0]))
        sys.exit(1)

    session_name = 'dst_server1'
    player = '1'

    args = ['screen', '-S', session_name, '-X', 'stuff']

    command = 'c_select(AllPlayers[' + player + '])^M'
    args.append(command)

    subprocess.call(args)

if __name__ == '__main__':
    main()

