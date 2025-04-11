# cleaner.py

import re

def clean_output(raw_output: str) -> str:
    # Remove ANSI escape sequences
    ansi_escape = re.compile(r'\x1b\[[0-9;?]*[a-zA-Z]')
    cleaned = ansi_escape.sub('', raw_output)

    # Remove OSC (Operating System Command) sequences
    osc_sequence = re.compile(r'\x1b\].*?\x07')
    cleaned = osc_sequence.sub('', cleaned)

    # Remove shell prompts like "user@host:~$"
    prompt_pattern = re.compile(r'\b\w+@\w+[-]?\w*:\~\$')
    cleaned = prompt_pattern.sub('', cleaned)

    # Remove [sudo] password prompts
    sudo_prompt = re.compile(r'\[sudo\] password for \w+:')
    cleaned = sudo_prompt.sub('', cleaned)

    # Strip carriage returns and excess whitespace
    cleaned = cleaned.replace('\r', '').strip()

    return cleaned
