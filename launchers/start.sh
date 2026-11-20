#!/bin/sh
# The same launcher runs in Terminal, Linux desktops, and the Windows WSL terminal.
set -eu
launcher_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
cd -- "$launcher_dir/.."

if [ "${1:-}" = --terminal ]; then
    shift
elif [ ! -t 0 ]; then
    if command -v x-terminal-emulator >/dev/null 2>&1; then
        exec x-terminal-emulator -e /bin/sh "$launcher_dir/start.sh" --terminal "$@"
    elif command -v gnome-terminal >/dev/null 2>&1; then
        exec gnome-terminal -- /bin/sh "$launcher_dir/start.sh" --terminal "$@"
    elif command -v konsole >/dev/null 2>&1; then
        exec konsole -e /bin/sh "$launcher_dir/start.sh" --terminal "$@"
    elif command -v xfce4-terminal >/dev/null 2>&1; then
        exec xfce4-terminal -x /bin/sh "$launcher_dir/start.sh" --terminal "$@"
    elif command -v xterm >/dev/null 2>&1; then
        exec xterm -e /bin/sh "$launcher_dir/start.sh" --terminal "$@"
    fi
    printf '%s\n' 'Open a terminal in the checkout and run: sh launchers/start.sh' >&2
    exit 1
fi

find_python() {
    for candidate in python3 python3.15 python3.14 python3.13 python3.12 python3.11 python3.10; do
        if command -v "$candidate" >/dev/null 2>&1 &&
            "$candidate" -I -c 'import sys; sys.exit(sys.version_info < (3, 10))' 2>/dev/null; then
            command -v "$candidate"
            return 0
        fi
    done
    return 1
}

run_setup() {
    case "$(uname -s)" in
        Darwin)
            # Finder terminals may start before the shell has added Homebrew to PATH.
            PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
            export PATH
            ;;
        Linux) ;;
        *) printf '%s\n' 'Use Gen5W.cmd on Windows.' >&2; return 1 ;;
    esac
    if ! python=$(find_python); then
        printf '%s\n' 'Gen5W needs Python 3.10 or newer to run the dependency planner.'
        case "$(uname -s)" in
            Darwin)
                install_manager=brew
                if ! command -v brew >/dev/null 2>&1; then
                    printf '%s\n' 'Install Homebrew from https://brew.sh/ or Python from https://www.python.org/downloads/.'
                    return 1
                fi
                printf '%s\n' '  brew install python'
                ;;
            Linux)
                if command -v apt-get >/dev/null 2>&1; then
                    install_manager=apt
                    printf '%s\n' '  sudo apt-get update' '  sudo apt-get install python3 python3-venv'
                elif command -v dnf >/dev/null 2>&1; then
                    install_manager=dnf
                    printf '%s\n' '  sudo dnf install python3'
                elif command -v pacman >/dev/null 2>&1; then
                    install_manager=pacman
                    printf '%s\n' '  sudo pacman -S --needed python'
                else
                    printf '%s\n' 'Install Python 3.10 or newer with your system package manager.'
                    return 1
                fi
                ;;
        esac
        for option do
            [ "$option" != --plan ] || return 0
        done
        printf '%s' 'Install Python with the listed command? [y/N] '
        IFS= read -r answer
        case "$answer" in
            y|Y|yes|YES) ;;
            *) return 1 ;;
        esac
        case "$install_manager" in
            brew) brew install python || return "$?" ;;
            apt) sudo apt-get update && sudo apt-get install python3 python3-venv || return "$?" ;;
            dnf) sudo dnf install python3 || return "$?" ;;
            pacman) sudo pacman -S --needed python || return "$?" ;;
        esac
        python=$(find_python) || {
            printf '%s\n' 'The installed Python is too old. Install Python 3.10 or newer and reopen the launcher.'
            return 1
        }
    fi
    PYTHONPATH="$PWD/tools/uk_fw" "$python" -s -B -m vm_workbench.bootstrap "$@"
}

code=0
run_setup "$@" || code=$?
if [ "$code" -ne 0 ] && [ "$code" -ne 130 ] && [ -t 0 ]; then
    printf '%s' 'Press Enter to close this launcher. '
    IFS= read -r unused || :
fi
exit "$code"
