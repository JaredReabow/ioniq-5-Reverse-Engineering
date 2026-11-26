#!/bin/sh
# The same launcher runs in Terminal, Linux desktops, and the Windows WSL terminal.
set -eu
launcher_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
cd -- "$launcher_dir/.."
assume_yes=false
no_pause=false
for option do
    case "$option" in
        --yes) assume_yes=true; no_pause=true ;;
        --no-pause) no_pause=true ;;
    esac
done

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

preview_requested() {
    for option do
        case "$option" in
            --preview|--preview=*) return 0 ;;
        esac
    done
    return 1
}

preview_error() {
    printf '%s\n' "Gen5W preview error: $*" >&2
    printf '%s\n' 'Preview accepts --port, --host-name, --no-browser, and --open-browser only.' >&2
}

preview_port_valid() {
    case "$1" in
        ''|*[!0-9]*) return 1 ;;
    esac
    [ "$1" -ge 0 ] 2>/dev/null && [ "$1" -le 65535 ] 2>/dev/null
}

preview_validate() {
    saw_preview=false
    no_browser=false
    open_browser=false
    while [ "$#" -gt 0 ]; do
        case "$1" in
            --preview) saw_preview=true ;;
            --no-browser) no_browser=true ;;
            --open-browser) open_browser=true ;;
            --no-pause) ;;
            --port|--host-name)
                option=$1
                if [ "$#" -lt 2 ]; then
                    preview_error "$option requires a value."
                    return 1
                fi
                value=$2
                case "$value" in
                    --*)
                        preview_error "$option requires a value."
                        return 1
                        ;;
                esac
                if [ "$option" = --port ]; then
                    preview_port_valid "$value" || {
                        preview_error "--port must be an integer from 0 to 65535."
                        return 1
                    }
                elif [ "$value" != 127.0.0.1 ] && [ "$value" != gen5w.local ]; then
                    preview_error "--host-name must be exactly 127.0.0.1 or gen5w.local."
                    return 1
                fi
                shift
                ;;
            --port=*)
                value=${1#*=}
                preview_port_valid "$value" || {
                    preview_error "--port must be an integer from 0 to 65535."
                    return 1
                }
                ;;
            --host-name=*)
                value=${1#*=}
                if [ "$value" != 127.0.0.1 ] && [ "$value" != gen5w.local ]; then
                    preview_error "--host-name must be exactly 127.0.0.1 or gen5w.local."
                    return 1
                fi
                ;;
            --assets|--assets=*|--workspace|--workspace=*)
                preview_error "$1 is unavailable because preview uses no VM assets or workspace."
                return 1
                ;;
            --wifi-sim|--wifi-sim-assets|--wifi-sim-assets=*)
                preview_error "$1 is unavailable because preview does not start the simulated Wi-Fi VM."
                return 1
                ;;
            --diagnostic-*)
                preview_error "$1 is unavailable because preview does not start a VM diagnostic session."
                return 1
                ;;
            --plan|--yes|--setup-hostname|--windows-alias|--windows-fallback-port|--windows-fallback-port=*|--print-asset-manifest)
                preview_error "$1 is a VM setup or installation option; preview never installs the VM stack."
                return 1
                ;;
            --server)
                preview_error '--server is unavailable in preview mode; launch without --preview for the full VM.'
                return 1
                ;;
            *)
                preview_error "unsupported argument: $1"
                return 1
                ;;
        esac
        shift
    done
    if [ "$saw_preview" = false ]; then
        preview_error '--preview is required.'
        return 1
    fi
    if [ "$no_browser" = true ] && [ "$open_browser" = true ]; then
        preview_error 'choose either --no-browser or --open-browser.'
        return 1
    fi
}

preview_python_guidance() {
    printf '%s\n' 'Gen5W preview needs Python 3.10 or newer; no VM tools or assets are required.' >&2
    case "$(uname -s 2>/dev/null || :)" in
        Darwin)
            if command -v brew >/dev/null 2>&1; then
                printf '%s\n' 'Install it with: brew install python (or use https://www.python.org/downloads/).' >&2
            else
                printf '%s\n' 'Install Python 3.10 or newer from https://www.python.org/downloads/ or install Homebrew from https://brew.sh/.' >&2
            fi
            ;;
        Linux)
            if command -v apt-get >/dev/null 2>&1; then
                printf '%s\n' 'On Ubuntu/Debian, install Python 3.10 or newer with: sudo apt-get install python3' >&2
            elif command -v dnf >/dev/null 2>&1; then
                printf '%s\n' 'On Fedora, install Python 3.10 or newer with: sudo dnf install python3' >&2
            elif command -v pacman >/dev/null 2>&1; then
                printf '%s\n' 'On Arch Linux, install Python 3.10 or newer with: sudo pacman -S --needed python' >&2
            else
                printf '%s\n' 'Install Python 3.10 or newer with your system package manager.' >&2
            fi
            ;;
        *)
            printf '%s\n' 'Install Python 3.10 or newer from https://www.python.org/downloads/. Use Gen5W.cmd on Windows.' >&2
            ;;
    esac
    printf '%s\n' 'The preview launcher does not install packages, request administrator access, or download VM dependencies.' >&2
}

run_preview() {
    preview_validate "$@" || return 1
    case "$(uname -s)" in
        Darwin)
            # Finder terminals may start before the shell has added Homebrew to PATH.
            PATH="$PATH:/opt/homebrew/bin:/usr/local/bin"
            export PATH
            ;;
        Linux) ;;
        *) preview_python_guidance; return 1 ;;
    esac
    if ! python=$(find_python); then
        preview_python_guidance
        return 1
    fi
    original_count=$#
    option_count=0
    no_browser=false
    open_browser=false
    while [ "$option_count" -lt "$original_count" ]; do
        option=$1
        shift
        option_count=$((option_count + 1))
        case "$option" in
            --no-pause) ;;
            --port|--host-name)
                value=$1
                shift
                option_count=$((option_count + 1))
                set -- "$@" "$option" "$value"
                ;;
            --no-browser)
                no_browser=true
                ;;
            --open-browser)
                open_browser=true
                set -- "$@" "$option"
                ;;
            *) set -- "$@" "$option" ;;
        esac
    done
    if [ "$no_browser" = false ] && [ "$open_browser" = false ]; then
        set -- "$@" --open-browser
    fi
    PYTHONPATH="$PWD/tools/uk_fw" exec "$python" -s -B -m vm_workbench "$@"
}

launcher_run() {
    if preview_requested "$@"; then
        run_preview "$@"
    else
        run_setup "$@"
    fi
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
        if [ "$assume_yes" = false ]; then
            printf '%s' 'Install Python with the listed command? [y/N] '
            IFS= read -r answer
            case "$answer" in
                y|Y|yes|YES) ;;
                *) return 1 ;;
            esac
        else
            printf '%s\n' 'Accepting displayed Python setup with --yes. sudo credentials must already be authorized.'
        fi
        case "$install_manager" in
            brew) brew install python || return "$?" ;;
            apt)
                if [ "$assume_yes" = true ]; then
                    sudo -n apt-get update && sudo -n apt-get install -y python3 python3-venv || return "$?"
                else
                    sudo apt-get update && sudo apt-get install python3 python3-venv || return "$?"
                fi ;;
            dnf)
                if [ "$assume_yes" = true ]; then sudo -n dnf install -y python3 || return "$?"
                else sudo dnf install python3 || return "$?"; fi ;;
            pacman)
                if [ "$assume_yes" = true ]; then sudo -n pacman -S --needed --noconfirm python || return "$?"
                else sudo pacman -S --needed python || return "$?"; fi ;;
        esac
        python=$(find_python) || {
            printf '%s\n' 'The installed Python is too old. Install Python 3.10 or newer and reopen the launcher.'
            return 1
        }
    fi
    PYTHONPATH="$PWD/tools/uk_fw" "$python" -s -B -m vm_workbench.bootstrap "$@"
}

code=0
launcher_run "$@" || code=$?
if [ "$code" -ne 0 ] && [ "$code" -ne 130 ] && [ "$no_pause" = false ] && [ -t 0 ]; then
    printf '%s' 'Press Enter to close this launcher. '
    IFS= read -r unused || :
fi
exit "$code"
