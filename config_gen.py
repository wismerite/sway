import json
import logging
from sys import argv

# setup, arg resolution
with open('config_gen.cfg.json') as config:
    config = json.load(config)

logger = logging.getLogger()
logger.debug(config)
#print(config)

# hardcoded filename cause this is what sway expects
output_file = open('config', 'wb')

passed_args = list(argv)

resolved_args = {
    "main_config": 'main.cfg',
    "themes_dir": 'themes.d',
    "cfg_ext": "cfg.json",
    "jobs": {},
    "includes_file": "config.d/includes.cfg"
}

for arg, arg_type in config['accepted_args'].items():
    if arg in passed_args:
        plain_arg = arg.replace('-', '')
        # only supporting one arg per job for now
        arg_value_index = passed_args.index(arg) + 1
        if arg_type == 'job':
            resolved_args['jobs'][plain_arg] = passed_args[arg_value_index]
        elif arg_type == 'config':
            resolved_args[plain_arg] = passed_args[arg_value_index]
        else:
            raise Exception("Uknown arg and arg type: {arg} : {arg_type}")

#print(resolved_args)

# job handlers
# these should each return a list of commands for sway config
def theme(name):
    theme_path = f"{resolved_args['themes_dir']}/{name}.{resolved_args['cfg_ext']}"
    try:
        with open(theme_path, 'r') as theme_config:
            theme_config = json.load(theme_config)
            for var_name, var_value in theme_config['color_vars'].items():
                yield format_sway_command(f"set ${var_name}", [var_value])
                
            for client_class, class_colors in theme_config['window'].items():
                #print(client_class)
                #print(class_colors)
                # cmd = [f"client.{client_class}"]
                # cmd.extend(class_colors)
                #print(cmd)
                yield format_sway_command(f"client.{client_class}", class_colors)
                
    except Exception as e:
        raise e

# short flag functions should just call the long flag functions
def t(name):
    return theme(name)


# core functions
def generate_sway_commands(jobs: dict):
    #print(jobs)
    for job, job_arg in jobs.items():
        for sway_command in globals()[job](job_arg):
            yield sway_command

def format_sway_command(cmd: str, cmd_args: list):
    cmd = [cmd]
    cmd.extend(cmd_args)
    #print(cmd_pieces)
    return f"{' '.join(cmd)}\n"

# core logic
if __name__ == "__main__":
    # first, our main config
    output_file.write(open(resolved_args['main_config'], 'rb').read())

    for command in generate_sway_commands(resolved_args['jobs']):
        #print(command)
        output_file.write(command.encode())

    for command in open(resolved_args['includes_file'], 'r').readlines():
        output_file.write(command.encode())

output_file.close()


