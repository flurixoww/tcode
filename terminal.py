import blessed

term = blessed.Terminal()


def system_offline_message():
    return term.white_on_firebrick3("SYSTEM OFFLINE")
