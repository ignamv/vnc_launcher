from vnc_launcher import list_displays


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='List all displays in specified hosts')
    parser.add_argument('host', nargs='+')
    hostnames = parser.parse_args().host
    displays = ((host, display)
                for host in hostnames
                for display in list_displays(host))
    for display in displays:
        print('{}:{}'.format(*display))


if __name__ == '__main__':
    main()
