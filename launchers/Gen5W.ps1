param(
    [ValidatePattern('^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$')]
    [string] $Distribution = 'Ubuntu',
    [ValidateRange(1, 65535)]
    [int] $Port = 8765,
    [switch] $Plan,
    [switch] $SetupHostname,
    [switch] $NoBrowser,
    [switch] $WifiSim
)

$ErrorActionPreference = 'Stop'
$root = (Get-Item -LiteralPath $PSScriptRoot).Parent.FullName
$windowsHosts = Join-Path $env:SystemRoot 'System32\drivers\etc\hosts'
$wsl = Join-Path $env:SystemRoot 'System32\wsl.exe'
$started = [Diagnostics.Stopwatch]::StartNew()
$log = $null

function Write-Setup([string] $Message) {
    $line = '[{0,6:F1}s] {1}' -f $started.Elapsed.TotalSeconds, $Message
    Write-Host $line
    if ($log) { Add-Content -LiteralPath $log -Value $line }
}

function Test-Consent([string] $Prompt) {
    return (Read-Host "$Prompt [y/N]") -match '^(y|yes)$'
}

function Get-Gen5WHostsMapping {
    $addresses = @()
    foreach ($line in Get-Content -LiteralPath $windowsHosts) {
        $tokens = (($line -split '#', 2)[0].Trim() -split '\s+')
        if ($tokens.Length -lt 2) { continue }
        for ($i = 1; $i -lt $tokens.Length; $i++) {
            if ($tokens[$i].TrimEnd('.') -ieq 'gen5w.local') { $addresses += $tokens[0] }
        }
    }
    if ($addresses.Count -eq 0) { return 'missing' }
    if (@($addresses | Where-Object { $_ -ne '127.0.0.1' }).Count) { return 'conflict' }
    return 'loopback'
}

function Test-Gen5WWindowsPort([int] $Candidate) {
    $listener = [Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback, $Candidate)
    $listener.ExclusiveAddressUse = $true
    try {
        $listener.Start()
        return $true
    } catch [Net.Sockets.SocketException] {
        return $false
    } finally {
        $listener.Stop()
    }
}

try {
    if (!$Plan) {
        $logRoot = Join-Path $root '.gen5w\logs'
        [void][IO.Directory]::CreateDirectory($logRoot)
        $log = Join-Path $logRoot ("windows-bootstrap-{0}.log" -f [Guid]::NewGuid().ToString('N'))
        Write-Setup "Setup log: $log"
    }
    Write-Setup 'Gen5W VM Workbench for Windows uses WSL2.'
    if (!(Test-Path -LiteralPath $wsl -PathType Leaf)) {
        throw 'WSL is unavailable. See https://learn.microsoft.com/windows/wsl/install, then reopen this launcher.'
    }

    Write-Setup '> wsl.exe --list --verbose'
    try {
        $ErrorActionPreference = 'Continue'
        $list = (& $wsl --list --verbose 2>&1 | Out-String).Replace("`0", '')
    } finally {
        $ErrorActionPreference = 'Stop'
    }
    $match = [regex]::Match($list, "(?im)^\s*(?:\*\s*)?$([regex]::Escape($Distribution))[ \t]+[^\r\n]+?[ \t]+([12])[ \t]*\r?$")
    if (!$match.Success) {
        if ($Distribution -ne 'Ubuntu') {
            throw "The requested WSL distribution '$Distribution' is unavailable. Install it in WSL2 or use Ubuntu."
        }
        Write-Setup '> wsl.exe --install --distribution Ubuntu --no-launch (administrator)'
        Write-Setup 'Windows may require a restart. Reopen this launcher afterward.'
        if ($Plan) { exit 0 }
        if (!(Test-Consent 'Install WSL and the Ubuntu distribution?')) { exit 1 }
        $installer = Start-Process -FilePath $wsl -ArgumentList @('--install', '--distribution', 'Ubuntu', '--no-launch') `
            -Verb RunAs -Wait -PassThru
        Write-Setup "WSL installer exit: $($installer.ExitCode)"
        if ($installer.ExitCode -notin 0, 3010) { exit $installer.ExitCode }
        Write-Setup 'Restart Windows if requested. Open Ubuntu once to create your Linux account, then reopen Gen5W.cmd.'
        [void](Read-Host 'Press Enter to close this launcher')
        exit 0
    }
    if ($match.Groups[1].Value -ne '2') {
        throw "Distribution '$Distribution' uses WSL1. Convert it with Microsoft's WSL2 instructions and reopen this launcher."
    }

    $mapping = Get-Gen5WHostsMapping
    if ($SetupHostname -and $mapping -eq 'missing') {
        Write-Setup "Optional administrator edit: $windowsHosts"
        Write-Host 'Add this separate line, preserving existing entries:'
        Write-Host '127.0.0.1 gen5w.local # Gen5W Workbench'
        if (!$Plan -and (Test-Consent 'Open the Windows hosts file in an administrator editor?')) {
            $editor = Join-Path $env:SystemRoot 'System32\notepad.exe'
            Start-Process -FilePath $editor -ArgumentList "`"$windowsHosts`"" -Verb RunAs
            [void](Read-Host 'Save the exact line in the editor, then press Enter to check the result')
            $mapping = Get-Gen5WHostsMapping
        }
    } elseif ($mapping -eq 'conflict') {
        Write-Setup 'Windows hosts file has a conflicting gen5w.local entry. Using numeric loopback.'
    }
    $aliasVerified = $false
    if ($mapping -eq 'loopback') {
        try {
            $addresses = [Net.Dns]::GetHostAddresses('gen5w.local')
            $aliasVerified = $addresses.Count -gt 0 -and
                @($addresses | Where-Object { $_.IPAddressToString -ne '127.0.0.1' }).Count -eq 0
        } catch [Net.Sockets.SocketException] { }
    }

    $fallback = 8765
    if (!$Plan) {
        $usable = Test-Gen5WWindowsPort $Port
        $fallback = $null
        foreach ($candidate in 8765..8775) {
            if (Test-Gen5WWindowsPort $candidate) { $fallback = $candidate; break }
        }
        if ($null -eq $fallback) {
            if ($usable -and $Port -ge 1024) { $fallback = $Port }
            else { throw 'Windows loopback ports 8765 through 8775 are busy. Pass -Port with a free unprivileged port.' }
        }
        if (!$usable -or ($Port -eq 80 -and !$aliasVerified)) {
            Write-Setup "Using Windows loopback fallback port $fallback."
            $Port = $fallback
        }
    }
    $execCommand = @('/bin/sh')
    if (!$NoBrowser) {
        $windowsBrowser = Join-Path $env:SystemRoot 'explorer.exe'
        $linuxBrowser = (& $wsl --distribution $Distribution --exec /usr/bin/wslpath -u $windowsBrowser).Trim()
        if ($LASTEXITCODE -ne 0 -or !$linuxBrowser.StartsWith('/') -or
            !$linuxBrowser.ToLowerInvariant().EndsWith('/windows/explorer.exe')) {
            throw 'Could not verify the Windows browser handoff path inside WSL2.'
        }
        $execCommand = @('/usr/bin/env', "GEN5W_WINDOWS_BROWSER=$linuxBrowser", '/bin/sh')
    }
    $arguments = @('--distribution', $Distribution, '--cd', $root, '--exec') + $execCommand +
                 @('./launchers/start.sh', '--terminal', '--port', [string]$Port,
                   '--windows-fallback-port', [string]$fallback)
    if ($Plan) { $arguments += '--plan' }
    if ($NoBrowser) { $arguments += '--no-browser' }
    if ($WifiSim) { $arguments += '--wifi-sim' }
    if ($aliasVerified) { $arguments += '--windows-alias' }
    if (!$aliasVerified) { Write-Setup 'Using numeric loopback. Add -SetupHostname to configure gen5w.local.' }
    Write-Setup ('> wsl.exe ' + (($arguments | ForEach-Object { '"{0}"' -f $_ }) -join ' '))
    & $wsl @arguments
    $result = $LASTEXITCODE
    Write-Setup "WSL launcher exit: $result"
    exit $result
} catch {
    Write-Setup "Setup stopped: $_"
    Write-Error $_ -ErrorAction Continue
    exit 1
}
