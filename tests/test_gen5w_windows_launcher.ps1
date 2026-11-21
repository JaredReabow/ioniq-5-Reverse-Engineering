# Execute launcher decisions in PowerShell without WSL, elevation or downloads.
$ErrorActionPreference = 'Stop'
$testRoot = Split-Path -Parent $PSScriptRoot
$temporary = Join-Path ([IO.Path]::GetTempPath()) ('gen5w-windows-' + [Guid]::NewGuid().ToString('N'))
[void][IO.Directory]::CreateDirectory($temporary)
$originalSystemRoot = $env:SystemRoot
$count = 0

function Assert-Gen5WEqual($Actual, $Expected, [string] $Label) {
    if ($Actual -cne $Expected) { throw "$Label expected '$Expected', received '$Actual'" }
    $script:count++
}

try {
    # Supply a harmless path on non-Windows PowerShell hosts as well.
    if (!$env:SystemRoot) { $env:SystemRoot = $temporary }
    . (Join-Path $testRoot 'launchers/Gen5W.ps1') -Plan -NoBrowser -Yes
    Assert-Gen5WEqual (Get-Gen5WHostsMapping -Lines @('127.0.0.1 localhost # gen5w.local')) 'missing' 'comment'
    Assert-Gen5WEqual (Get-Gen5WHostsMapping -Lines @('127.0.0.1 Gen5W.LOCAL.', '::1 gen5w.local')) 'loopback' 'dual loopback'
    Assert-Gen5WEqual (Get-Gen5WHostsMapping -Lines @('::1 gen5w.local')) 'loopback' 'IPv6 mapping'
    Assert-Gen5WEqual (Get-Gen5WHostsMapping -Lines @('127.0.0.1 gen5w.local', '192.0.2.5 gen5w.local')) 'conflict' 'conflict'
    Assert-Gen5WEqual (Test-Gen5WResolvedAddresses -Addresses @([Net.IPAddress]::Parse('127.0.0.1'), [Net.IPAddress]::IPv6Loopback)) $true 'dual resolution'
    Assert-Gen5WEqual (Test-Gen5WResolvedAddresses -Addresses @([Net.IPAddress]::IPv6Loopback)) $false 'IPv6-only fallback'
    Assert-Gen5WEqual (Test-Gen5WResolvedAddresses -Addresses @([Net.IPAddress]::Parse('192.0.2.5'))) $false 'external fallback'
    Assert-Gen5WEqual (Get-Gen5WDistributionVersion "* Ubuntu    Stopped    2`r`n  Ubuntu-24.04 Running 1" 'Ubuntu') '2' 'exact distro'
    Assert-Gen5WEqual (Get-Gen5WDistributionVersion '* Ubuntu-24.04 Stopped 2' 'Ubuntu') $null 'missing distro'
    Assert-Gen5WEqual (Get-Gen5WDistributionVersion "* Ubuntu`0 Stopped`0 2`0" 'Ubuntu') '2' 'UTF16 console output'
    Assert-Gen5WEqual (ConvertTo-Gen5WBrowserPath '/mnt/c/Windows/explorer.exe' 0) '/mnt/c/Windows/explorer.exe' 'browser path'
    foreach ($value in @($null, '', ' ', '/mnt/c/Windows/notepad.exe', "/mnt/c/Windows/explorer.exe`nother")) {
        $rejected = $false
        try { [void](ConvertTo-Gen5WBrowserPath $value 0) } catch { $rejected = $true }
        Assert-Gen5WEqual $rejected $true 'invalid browser output'
    }
    $rejected = $false
    try { [void](ConvertTo-Gen5WBrowserPath '/mnt/c/Windows/explorer.exe' 1) } catch { $rejected = $true }
    Assert-Gen5WEqual $rejected $true 'failed wslpath'
    Assert-Gen5WEqual (Test-Gen5WConsent 'Fixture consent') $true 'explicit consent'

    # Invoke the actual launcher in plan mode with bounded WSL/hosts fixtures.
    # No mocks replace distribution parsing or argument construction.
    $script:root = Join-Path $temporary 'checkout with spaces'
    $script:windowsHosts = Join-Path $temporary 'hosts'
    [IO.File]::WriteAllText($windowsHosts, '127.0.0.1 localhost')
    $script:wsl = Join-Path $temporary 'fixture-wsl'
    $script:captured = @()
    $script:messages = @()
    function Write-Gen5WSetup([string] $Message) { $script:messages += $Message }
    function Invoke-Gen5WWsl([string[]] $Arguments) {
        $script:captured += ,$Arguments
        $global:LASTEXITCODE = 0
        if ($Arguments[0] -eq '--list') { return '* Ubuntu Stopped 2' }
    }
    Assert-Gen5WEqual (Invoke-Gen5WLauncher) 0 'absent WSL plan'
    Assert-Gen5WEqual $captured.Count 0 'absent WSL no launch'
    Assert-Gen5WEqual ($messages -join "`n").Contains('7. Ctrl+C') $true 'complete deferred plan'
    Assert-Gen5WEqual ($messages -join "`n").Contains('checks have not run') $true 'deferred disclosure'
    [IO.File]::WriteAllText($wsl, 'fixture')
    Assert-Gen5WEqual (Invoke-Gen5WLauncher) 0 'available WSL plan'
    Assert-Gen5WEqual $captured.Count 2 'list and handoff'
    $handoff = $captured[1]
    foreach ($expected in @('--plan', '--yes', '--no-pause', '--no-browser', $root, './launchers/start.sh')) {
        Assert-Gen5WEqual ($handoff -contains $expected) $true "handoff $expected"
    }
    Assert-Gen5WEqual ([IO.Directory]::Exists($root)) $false 'plan does not create state'
    Write-Output "GEN5W_WINDOWS_LAUNCHER_TESTS_PASS assertions=$count"
} finally {
    $env:SystemRoot = $originalSystemRoot
    # This exact GUID-created fixture directory contains only this test's data.
    [IO.Directory]::Delete($temporary, $true)
}
