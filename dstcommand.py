#!/usr/bin/env python3

'''Don't Starve Together Dedicated Server Interface

Use this program to interface with a dedicated DST server
'''

import subprocess
import sys

def get_qty(user_prompt=None, def_qty=None, min_qty=None, max_qty=None):
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
    if def_qty:
        try:
            int(def_qty)
        except ValueError:
            print('Default value is invalid - expected an integer.')
            sys.exit(1)

    if not user_prompt:
        user_prompt = 'Enter quantity [default=' + def_qty + ']: '

    qty = input(user_prompt)

    if not qty:
        if def_qty:
            qty = def_qty
        else:
            print('No quantity entered')
            sys.exit(1)

    try:
        int(qty)
        if min_qty:
            int(min_qty)
        if max_qty:
            int(max_qty)
    except ValueError:
        print('Invalid value - was expecting an integer.')
        sys.exit(1)

    if min_qty > qty:
        print('Invalid quantity: User-entered {} is greater '
              'than minimum {}'.format(qty, min_qty))
    if max_qty < qty:
        print('Invalid quantity: User-entered {} is less than '
              'than maximum {}'.format(qty, max_qty))

    return qty

def get_item():
    '''Query user for item

    Ask user for item (usually to be given via give_item() function)

    Returns:
        A string item, hopefully a valid DST prefab (although I do not
            validate this
    '''
    item = input('Enter item: ')

    if not item:
        print('Error: Invalid Item: No Item Entered')
        sys.exit(1)

    return item

def give_item(item=None, player_num=None, qty=None):
    '''Give player an item

    Builds command for remote server to give players an item

    Args:
        item: string (optional). item to give (look up DST prefabs for list)
        player_num: string (optional). player number of receiver
        qty: string (optional). number/quantity of items to give

    Returns:
        command: string to be passed to screen session running DST server
    '''

    if not item:
        item = get_item()
    if not player_num:
        player_num = str(get_qty('Enter player number (default=1): ', 1))
    if not qty:
        qty = str(get_qty())

    command = ('c_select(AllPlayers[' + player_num + ']) c_give(\"' + item +
               '\"' + qty + ')^M')

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

def toggle_god_mode(player_num=None):
    '''Toggle god mode for a user

    Args:
        player_num: string (optional). player number of receiver

    Returns:
        command string to toggle god mode for player
    '''
    if not player_num:
        player_num = str(get_qty('Enter player number (default=1): ', 1))

    return 'c_select(AllPlayers[' + player_num + '] c_godmode()^M'

def toggle_super_god_mode(player_num=None):
    '''Toggle super god mode for a user

    Args:
        player_num: string (optional). player number of receiver

    Returns:
        command string to toggle super god mode for player
    '''
    if not player_num:
        player_num = str(get_qty('Enter player number (default=1): '), 1)

    return 'c_select(AllPlayers[' + player_num + '] c_supergodmode()^M'

def get_pct(user_prompt=None, def_pct=1.0, min_pct=None, max_pct=None):
    '''Get percentage from user

    Prompts user to enter a percent and validates it

    Args:
        user_prompt: string (optional) that is displayed to user before prompt
        def_pct: float (optional, default = 1.0) default percent if user
            does not provide input
        min_pct: float (optional) used to validate user input
        max_pct: float (optional) used to validate user input

    Returns:
        percentage as a float, 1.00 represents 100%
    '''
    if not user_prompt:
        user_prompt = 'Enter a percentage (1.0 is 100%, 100 is 1,000%): '

    pct = input(user_prompt)

    if not pct:
        pct = def_pct

    try:
        float(pct)
        if min_pct:
            float(min_pct)
        if max_pct:
            float(max_pct)
    except ValueError:
        print('Invalid entry - was expecting a floating point.')
        sys.exit(1)

    if min_pct > pct:
        print('Invalid percent: User-entered {:2%} is greater than'
              'minimum {:2%}'.format(pct, min_pct))
    if max_pct < pct:
        print('Invalid percent: User-entered {:2%} is less than than'
              'maximum {:2%}'.format(pct, max_pct))

    return pct

def set_health(player_num=None, health_pct=None):
    '''Set player health to given percent of max

    Args:
        player_num: string (optional). player number of receiver
        health_pct: float (optional). percent (between 0 and 1) that
            will be multiplied to player max health stat to determine
            new level of health

    Returns:
        command string to set player health
    '''
    if not player_num:
        player_num = str(get_qty('Enter player number (default=1): '))

    if not health_pct:
        health_pct = str(get_pct('Enter % of max health [1.0 = 100%]: ', 1.0))


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

def test_script():
    '''Test this program

    A bunch of test scripts for these functions
    '''
    pass





