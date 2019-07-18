# -*- coding: utf-8 -*-
import sys

try:
	import weechat
except ImportError:
	print('Please run in weechat')
	sys.exit()

SCRIPT_NAME = ''
SCRIPT_DESCRIPTION = ''
SCRIPT_AUTHOR = ''

def config_handler(data, option, value):
    # Load updated options into memory, call other functions, etc

    return weechat.WEECHAT_RC_OK

if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, '', '', SCRIPT_DESCRIPTION, '', ''):
    options = {
        # 'option_name': (
        #     'value',
        #     'description'),
    }

    option_values = {}
    for option, values in options.items():
        if not weechat.config_is_set_plugin(option):
        	weechat.config_set_plugin(option, values[0])

        	weechat.config_set_desc_plugin(option, values[1])

    weechat.hook_config('plugins.var.python.' + SCRIPT_NAME + '.*', 'config_handler', '')

    # Main stuff here