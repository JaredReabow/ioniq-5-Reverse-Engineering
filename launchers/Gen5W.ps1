param(
    [ValidatePattern('^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$')]
    [string] $Distribution = 'Ubuntu',
    [ValidateRange(1, 65535)]
    [int] $Port = 8765,
    [switch] $Plan,
    [switch] $Yes,
    [switch] $NoPause,
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

function Write-Gen5WSetup([string] $Message) {
    $line = '[{0,6:F1}s] {1}' -f $started.Elapsed.TotalSeconds, $Message
    Write-Host $line
    if ($log) { Add-Content -LiteralPath $log -Value $line }
}

function Test-Gen5WConsent([string] $Prompt) {
    if ($Yes) {
        Write-Gen5WSetup "$Prompt Accepted by -Yes. Administrator permission is still required where shown."
        return $true
    }
    if ([Console]::IsInputRedirected) {
        Write-Gen5WSetup "$Prompt No interactive input. Reopen in a terminal or pass -Yes."
        return $false
    }
    return (Read-Host "$Prompt [y/N]") -match '^(y|yes)$'
}

function Get-Gen5WHostsMapping([string[]] $Lines = (Get-Content -LiteralPath $windowsHosts)) {
    $addresses = @()
    foreach ($line in $Lines) {
        $tokens = (($line -split '#', 2)[0].Trim() -split '\s+')
        if ($tokens.Length -lt 2) { continue }
        for ($i = 1; $i -lt $tokens.Length; $i++) {
            if ($tokens[$i].TrimEnd('.') -ieq 'gen5w.local') { $addresses += $tokens[0] }
        }
    }
    if ($addresses.Count -eq 0) { return 'missing' }
    if (@($addresses | Where-Object { $_ -notin '127.0.0.1', '::1' }).Count) { return 'conflict' }
    return 'loopback'
}

function Test-Gen5WResolvedAddresses([Net.IPAddress[]] $Addresses) {
    # The listener is IPv4-only. An additional IPv6 loopback is harmless, but
    # an IPv6-only alias still needs numeric IPv4 fallback to reach the server.
    return $Addresses.Count -gt 0 -and
        @($Addresses | Where-Object { $_.IPAddressToString -eq '127.0.0.1' }).Count -gt 0 -and
        @($Addresses | Where-Object { $_.IPAddressToString -notin '127.0.0.1', '::1' }).Count -eq 0
}

function Get-Gen5WDistributionVersion([string] $List, [string] $Name) {
    $match = [regex]::Match($List.Replace("`0", ''), "(?im)^\s*(?:\*\s*)?$([regex]::Escape($Name))[ \t]+[^\r\n]+?[ \t]+([12])[ \t]*\r?$")
    if ($match.Success) { return $match.Groups[1].Value }
    return $null
}

function ConvertTo-Gen5WBrowserPath([object] $Output, [int] $ExitCode) {
    $value = ($Output | Out-String).Trim()
    if ($ExitCode -ne 0 -or [string]::IsNullOrWhiteSpace($value) -or
        !$value.StartsWith('/') -or !$value.ToLowerInvariant().EndsWith('/windows/explorer.exe') -or
        $value.Contains("`n") -or $value.Contains("`r")) {
        throw 'Could not verify the Windows browser handoff path inside WSL2 (wslpath returned an empty, failed, or unexpected result).'
    }
    return $value
}

function Invoke-Gen5WWsl([string[]] $Arguments) {
    & $wsl @Arguments
}

function Write-Gen5WDeferredPlan {
    Write-Gen5WSetup 'Deferred setup plan: Ubuntu is not available; downstream checks have not run.'
    Write-Gen5WSetup '1. Enable WSL2 / Virtual Machine Platform and install Ubuntu (Windows UAC may require the local desktop).'
    Write-Gen5WSetup '2. Restart Windows if requested; open Ubuntu once and create a regular Linux account.'
    Write-Gen5WSetup '3. Reopen this launcher. Check WSL2 and /dev/kvm; the Gen5W guest still uses QEMU TCG software emulation.'
    Write-Gen5WSetup '4. Run launchers/start.sh --plan in Ubuntu to resolve missing Python/system packages, pinned Zig and the local Python environment.'
    Write-Gen5WSetup '5. Require local gen5w-assets.json before installing dependencies; verify exact prepared asset hashes before VM admission.'
    Write-Gen5WSetup '6. Validate the optional Windows hosts alias and browser path, select a loopback URL and start the browser service.'
    Write-Gen5WSetup '7. Ctrl+C stops the foreground service; browser Stop VM requests bounded owned-process cleanup.'
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

function Invoke-Gen5WLauncher {
    try {
        if (!$Plan) {
            $logRoot = Join-Path $root '.gen5w\logs'
            [void][IO.Directory]::CreateDirectory($logRoot)
            $log = Join-Path $logRoot ("windows-bootstrap-{0}.log" -f [Guid]::NewGuid().ToString('N'))
            Write-Gen5WSetup "Setup log: $log"
        }
        Write-Gen5WSetup 'Gen5W VM Workbench for Windows uses WSL2.'
        if (!(Test-Path -LiteralPath $wsl -PathType Leaf)) {
            if ($Plan) { Write-Gen5WDeferredPlan; return 0 }
            throw 'WSL is unavailable. See https://learn.microsoft.com/windows/wsl/install, then reopen this launcher.'
        }

        Write-Gen5WSetup '> wsl.exe --list --verbose'
        try {
            $ErrorActionPreference = 'Continue'
            $list = (Invoke-Gen5WWsl -Arguments @('--list', '--verbose') 2>&1 | Out-String).Replace("`0", '')
        } finally {
            $ErrorActionPreference = 'Stop'
        }
        $version = Get-Gen5WDistributionVersion $list $Distribution
        if (!$version) {
            if ($Distribution -ne 'Ubuntu') {
                throw "The requested WSL distribution '$Distribution' is unavailable. Install it in WSL2 or use Ubuntu."
            }
            Write-Gen5WSetup '> wsl.exe --install --distribution Ubuntu --no-launch (administrator)'
            Write-Gen5WSetup 'Windows may require a restart. Reopen this launcher afterward.'
            if ($Plan) { Write-Gen5WDeferredPlan; return 0 }
            if (!(Test-Gen5WConsent 'Install WSL and the Ubuntu distribution?')) { return 1 }
            $installer = Start-Process -FilePath $wsl -ArgumentList @('--install', '--distribution', 'Ubuntu', '--no-launch') `
                -Verb RunAs -Wait -PassThru
            Write-Gen5WSetup "WSL installer exit: $($installer.ExitCode)"
            if ($installer.ExitCode -notin 0, 3010) { return $installer.ExitCode }
            Write-Gen5WSetup 'Restart Windows if requested. Open Ubuntu once to create your Linux account, then reopen Gen5W.cmd.'
            Write-Gen5WSetup 'Prerequisite installation finished; the Gen5W service has not started.'
            if (!$Yes -and !$NoPause -and ![Console]::IsInputRedirected) {
                [void](Read-Host 'Press Enter to close this launcher')
            }
            return 3010
        }
        if ($version -ne '2') {
            throw "Distribution '$Distribution' uses WSL1. Convert it with Microsoft's WSL2 instructions and reopen this launcher."
        }

        $mapping = Get-Gen5WHostsMapping
        if ($SetupHostname -and $mapping -eq 'missing') {
            Write-Gen5WSetup "Optional administrator edit: $windowsHosts"
            Write-Host 'Add this separate line, preserving existing entries:'
            Write-Host '127.0.0.1 gen5w.local # Gen5W Workbench'
            if ($Yes) {
                Write-Gen5WSetup '-Yes leaves a missing Windows hosts alias unchanged. Configure it once with an interactive -SetupHostname launch.'
            } elseif (!$Plan -and (Test-Gen5WConsent 'Open the Windows hosts file in an administrator editor?')) {
                $editor = Join-Path $env:SystemRoot 'System32\notepad.exe'
                Start-Process -FilePath $editor -ArgumentList "`"$windowsHosts`"" -Verb RunAs
                [void](Read-Host 'Save the exact line in the editor, then press Enter to check the result')
                $mapping = Get-Gen5WHostsMapping
            }
        } elseif ($mapping -eq 'conflict') {
            Write-Gen5WSetup 'Windows hosts file has a conflicting gen5w.local entry. Using numeric loopback.'
        }
        $aliasVerified = $false
        if ($mapping -eq 'loopback') {
            try {
                $aliasVerified = Test-Gen5WResolvedAddresses ([Net.Dns]::GetHostAddresses('gen5w.local'))
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
                # A free, verified port 80 does not need an available fallback.
                if ($usable -and $Port -eq 80 -and $aliasVerified) { $fallback = 8765 }
                elseif ($usable -and $Port -ge 1024) { $fallback = $Port }
                else { throw 'Windows loopback ports 8765 through 8775 are busy. Pass -Port with a free unprivileged port.' }
            }
            if (!$usable -or ($Port -eq 80 -and !$aliasVerified)) {
                Write-Gen5WSetup "Using Windows loopback fallback port $fallback."
                $Port = $fallback
            }
        }
        $execCommand = @('/bin/sh')
        $skipBrowser = [bool]$NoBrowser
        if (!$skipBrowser) {
            try {
                $windowsBrowser = Join-Path $env:SystemRoot 'explorer.exe'
                $pathOutput = Invoke-Gen5WWsl -Arguments @('--distribution', $Distribution, '--exec', '/usr/bin/wslpath', '-u', $windowsBrowser)
                $linuxBrowser = ConvertTo-Gen5WBrowserPath $pathOutput $LASTEXITCODE
                $execCommand = @('/usr/bin/env', "GEN5W_WINDOWS_BROWSER=$linuxBrowser", '/bin/sh')
            } catch {
                $skipBrowser = $true
                Write-Gen5WSetup 'Warning: Windows browser handoff is unavailable. Open the URL printed by the server once it starts.'
            }
        }
        $arguments = @('--distribution', $Distribution, '--cd', $root, '--exec') + $execCommand +
                     @('./launchers/start.sh', '--terminal', '--port', [string]$Port,
                       '--windows-fallback-port', [string]$fallback)
        if ($Plan) { $arguments += '--plan' }
        if ($Yes) { $arguments += '--yes' }
        if ($Yes -or $NoPause) { $arguments += '--no-pause' }
        if ($skipBrowser) { $arguments += '--no-browser' }
        if ($WifiSim) { $arguments += '--wifi-sim' }
        if ($aliasVerified) { $arguments += '--windows-alias' }
        if (!$aliasVerified) { Write-Gen5WSetup 'Using numeric loopback. Add -SetupHostname to configure gen5w.local.' }
        Write-Gen5WSetup ('> wsl.exe ' + (($arguments | ForEach-Object { '"{0}"' -f $_ }) -join ' '))
        Invoke-Gen5WWsl -Arguments $arguments | ForEach-Object { Write-Host $_ }
        $result = $LASTEXITCODE
        Write-Gen5WSetup "WSL launcher exit: $result"
        return $result
    } catch {
        Write-Gen5WSetup "Setup stopped: $_"
        Write-Error $_ -ErrorAction Continue
        return 1
    }
}

# Dot-sourcing loads the module functions for the native PowerShell harness.
if ($MyInvocation.InvocationName -ne '.') {
    exit (Invoke-Gen5WLauncher)
}
