# -*- coding: utf-8 -*-
import sys

# Make sure we're running in weechat
try:
    import weechat
except ImportError:
    print('Please run in weechat')
    sys.exit()


# Function for retrieving nick prefix (@, +, etc)
def get_nick_prefix(pointer):
    nick = weechat.buffer_get_string(pointer, "localvar_nick")
    nick_pointer = weechat.nicklist_search_nick(pointer, "", nick)

    prefix = weechat.nicklist_nick_get_string(pointer, nick_pointer, "prefix")

    return prefix

# Main function that builds the list
def build_list(data, item, window):
    # Setup variables
    # First retrieve the `hdata`s, then get relevant lists
    buffer_hdata   = weechat.hdata_get('buffer')
    server_hdata   = weechat.hdata_get('irc_server')
    hotlist_hdata  = weechat.hdata_get('hotlist')
    buffer_pointer = weechat.hdata_get_list(buffer_hdata, 'gui_buffers')
    server_pointer = weechat.hdata_get_list(server_hdata, 'irc_servers')
    buflist        = ''

    # Start looping through the buffers
    while buffer_pointer:
        # Grab the hotlist and priority level for the current buffer
        hotlist_pointer = weechat.hdata_pointer(buffer_hdata, buffer_pointer, "hotlist")
        if hotlist_pointer:
            priority   = weechat.hdata_integer(hotlist_hdata, hotlist_pointer, 'priority')
        else:
            priority   = 0

        # Setup the info variables for the current buffer
        nick           = weechat.buffer_get_string(buffer_pointer, "localvar_nick")
        name           = weechat.buffer_get_string(buffer_pointer, "short_name")
        full_name      = weechat.buffer_get_string(buffer_pointer, "name")
        plugin         = weechat.buffer_get_string(buffer_pointer, "plugin")
        buffer_type    = weechat.buffer_get_string(buffer_pointer, "localvar_type")
        server         = weechat.buffer_get_string(buffer_pointer, 'localvar_server')
        icon_color     = weechat.buffer_get_string(buffer_pointer, "localvar_icon_color") or 0
        current_buffer = 1 if weechat.current_buffer() == buffer_pointer else 0

        # Setup info variables for next buffer
        next_pointer   = weechat.hdata_move(buffer_hdata, buffer_pointer, 1)
        next_type      = weechat.buffer_get_string(next_pointer, "plugin")


        # Start building!

        # Draw icons for non-IRC buffers - core, script, fset, etc
        # You can set an `icon_color` localvar to override the `color.icon` option for a particular buffer when it's active
        # This isn't exactly ideal. Another option would be to use a localvar for each buffer that gets an icon, and then do a check for that
        if plugin != 'irc':
            if current_buffer:
                if icon_color:
                    buflist += weechat.color(icon_color)
                else:
                    buflist += weechat.color(option_values['color.icon'])
            else:
                buflist += weechat.color(option_values['color.default_fg'])

            buflist += "●  "
            buflist += weechat.color(option_values['color.default_fg'])

            # Add a newline if the next buffer is the start of IRC buffers
            if next_type == 'irc':
                buflist += '\n'
        # Start adding other buffers
        else:
            # Print the appropriate color for the current buffer, as well as an icon for the current buffer
            if current_buffer:
                buflist += weechat.color(option_values['color.current_fg'])
                buflist += "●"
            elif priority == 1:
                buflist += weechat.color(option_values['color.hotlist_message'])
            elif priority == 2:
                buflist += weechat.color(option_values['color.hotlist_private'])
            elif priority == 3:
                buflist += weechat.color(option_values['color.hotlist_highlight'])
            else:
                buflist += weechat.color(option_values['color.default_fg'])

            # Spacing between icon and name
            if current_buffer:
                buflist += ' '
            else:
                buflist += '  '
            if buffer_type != 'server':
                buflist += '   '
            if buffer_type == 'private':
                buflist += '  '

            # Add the nick prefix (@, +, etc)
            nick_prefix = get_nick_prefix(buffer_pointer)
            buflist += nick_prefix

            # Add the buffer name
            buflist += name

            # Add nick modes next to server buffers, if any are set
            if buffer_type == 'server':
                # Search for and retrieve a pointer for the server
                pointer    = weechat.hdata_search(server_hdata, server_pointer, "${irc_server.name} == " + server, 1)

                nick_modes = weechat.hdata_string(server_hdata, pointer, "nick_modes")

                if nick_modes:
                    buflist += ' (+{})'.format(nick_modes)
            buflist += '\n'

        # Move to the next buffer
        buffer_pointer = weechat.hdata_move(buffer_hdata, buffer_pointer, 1)

    # All done. Return the list
    return buflist

# Function for updating the bar on certain signals
def signal_handler(data, signal, signal_data):
    weechat.bar_item_update('squigzlist')

    return weechat.WEECHAT_RC_OK

# Function for updating variables and reloading bar when config options change
option_values = {}
def config_handler(data, option, value):
    # Splits the full config option name (plugins.var.python...) to something easier to work with
    option = '.'.join(option.split('.')[-2:])

    option_values[option] = value

    weechat.bar_item_update('squigzlist')

    return weechat.WEECHAT_RC_OK

# Register the script
if weechat.register('squigzlist', 'squigz', '', '', 'Another buffer list script', '', ''):
    # Start configuring options
    options = {
        'display_conditions': (
            '$\{buffer.hidden\} == 0)'
            'Conditions to display buffers (see /help eval)'),
        'color.default_fg': (
            '237',
            'Default foreground color for buffers'),
        'color.default_bg': (
            'default',
            'Default background color for buffers'),
        'color.current_fg': (
            'lightblue',
            'Foreground for currently selected buffer'),
        'color.current_bg': (
            'default',
            'Background for currently selected buffer'),
        'color.hotlist_low': (
            'default',
            'Color for buffers in hotlist with \'low\' level'),
        'color.hotlist_message': (
            'white',
            'Color for buffers in hotlist with \'message\' level'),
        'color.hotlist_private': (
            'red',
            'Color for buffers in hotlist with \'private\' level'),
        'color.hotlist_highlight': (
            'red',
            'Color for buffers in hotlist with \'highlight\' priority'),
        'color.icon': (
            'lightblue',
            'Color for icons in list (non-IRC buffers)'),
    }

    # Loop through and set options with default values and descriptions, and load values into dict to use
    option_values = {}
    for option, values in options.items():
        # First ensure it's not already set
        if not weechat.config_is_set_plugin(option):
            weechat.config_set_plugin(option, values[0])

            weechat.config_set_desc_plugin(option, values[1])

        option_values[option] = weechat.config_get_plugin(option)

    # Setup callback for config option updates
    weechat.hook_config('plugins.var.python.squigzlist.*', 'config_handler', '')

    # Create bar item
    weechat.bar_item_new('squigzlist', 'build_list', '')

    # Hook various signals on which to refresh the list
    signals = ['buffer_opened', 'buffer_closed', 'buffer_merged', 'buffer_unmerged', 'buffer_moved', 'buffer_renamed', 'buffer_switch', 'buffer_hidden', 'buffer_unhidden', 'buffer_localvar_added', 'buffer_localvar_changed', 'hotlist_changed']

    for signal in signals:
        weechat.hook_signal(signal, 'signal_handler', '')