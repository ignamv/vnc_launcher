import re
import subprocess


def list_displays(hostname):
    """Return list with user's display numbers in remote host"""
    display_re = re.compile(r'^:(\d+)\s+\d+$', re.MULTILINE)
    try:
        raw = subprocess.check_output(['ssh', hostname, 'vncserver', '-list'],
                                      stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        raw = e.output
    return map(int, display_re.findall(raw))


def choose_option_cmdline(options):
    for ii, option in enumerate(options):
        print '{}. :{}'.format(ii + 1, option)
    while True:
        inp = raw_input('Enter a number from 1 to {}: '.format(len(options)))
        inp = int(inp.strip())
        if 0 < inp <= len(options):
            return options[inp - 1]


def choose_display_gui(displays):
    if len(displays) == 1:
        return displays[0]


def choose_display_cmdline(displays):
    """Command-line prompt to choose a display if there's more than 1."""
    if len(displays) == 1:
        'Connecting to display {}'.format(displays[0])
        return displays[0]
    print 'There are several running displays in remote host'
    return choose_option_cmdline(displays)


def create_display(hostname):
    """Run vncserver in remote host, return display number"""
    server_options = ['-autokill']
    success_re = re.compile(r'^New .* desktop is .*:(\d+)$', re.MULTILINE)
    cmd = ['ssh', hostname, 'vncserver'] + server_options
    raw = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    match = success_re.search(raw)
    if not match:
        raise Exception(raw)
    ret = int(match.group(1))
    print 'Created display {}'.format(ret)
    return ret


def connect_viewer(hostname, display):
    """Launch vncviewer to specified hostname and display number"""
    subprocess.check_output(['vncviewer', '{}:{}'.format(hostname, display)],
                            stderr=subprocess.STDOUT)


def main_cmdline():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('hostname', help='Remote host to connect to')
    hostname = parser.parse_args().hostname
    displays = list_displays(hostname)
    if not displays:
        display = create_display(hostname)
    else:
        display = choose_display_cmdline(displays)
    connect_viewer(hostname, display)


def prompt_hostname_gui():
    """Ask user for a hostname, offer recently used values"""
    from qtpy.QtWidgets import QInputDialog
    from qtpy.QtCore import QSettings
    settings = QSettings('allegro', 'allegro_vnc')
    recent = settings.value('recent_hostnames', [])
    hostname, accepted = QInputDialog.getItem(
        None, 'Enter hostname', 'Hostname:', recent)
    if not accepted:
        return
    recent.insert(0, hostname)
    # Remove duplicates without changing order
    recent = sorted(set(recent), key=recent.index)[:10]
    settings.setValue('recent_hostnames', recent)
    return hostname


def main_gui():
    from qtpy.QtWidgets import QInputDialog, QApplication, QMessageBox
    import sys

    QApplication(sys.argv)

    hostname = prompt_hostname_gui()
    if not hostname:
        return
    try:
        displays = list_displays(hostname)
    except subprocess.CalledProcessError as e:
        QMessageBox.critical(None, 'Error listing displays', e.output)
        exit(-1)
    if not displays:
        try:
            display = create_display(hostname)
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(None, 'Error creating display', e.output)
            exit(-1)
    elif len(displays) == 1:
        display = displays[0]
    else:
        display, accepted = QInputDialog.getItem(
            None, 'Select display', 'Display:', map(str, displays),
            editable=False)
        if not accepted:
            return
        display = int(display)
    try:
        print hostname, display
        connect_viewer(hostname, display)
    except subprocess.CalledProcessError as e:
        QMessageBox.critical(None, 'Error connecting to display', e.output)
        exit(-1)


if __name__ == '__main__':
    main_gui()
