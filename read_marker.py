# -*- coding: utf-8 -*-
import sys

try:
	import weechat
except ImportError:
	print('Please run in weechat')
	sys.exit()

def refresh():
    width = weechat.window_get_integer(weechat.current_window(), 'win_chat_width')
    string = option_values['marker']

    marker = string + ' ' * (width - (len(string.decode('utf-8')) * 2)) + string

    config = weechat.config_get('weechat.look.read_marker_string')
    weechat.config_option_set(config, marker, 0)

def config_handler(data, option, value):
    option = option.split('.')[-1]
    option_values[option] = value

    refresh()

    return weechat.WEECHAT_RC_OK

def signal_handler(data, signal, signal_data):
    refresh()

    return weechat.WEECHAT_RC_OK

if weechat.register('read_marker', 'squigz', '', '', '', '', ''):
    options = {
        'marker': (
            '─────────────────',
            'String to use to generate read marker'),
    }

    option_values = {}
    for option, values in options.items():
        if not weechat.config_is_set_plugin(option):
        	weechat.config_set_plugin(option, values[0])

        	weechat.config_set_desc_plugin(option, values[1])

        option_values[option] = weechat.config_get_plugin(option)

    weechat.hook_config('plugins.var.python.read_marker.*', 'config_handler', '')

    signals = ['signal_sigwinch']
    for signal in signals:
        weechat.hook_signal(signal, 'signal_handler', '')