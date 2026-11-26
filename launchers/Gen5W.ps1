param(
    [ValidatePattern('^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$')]
    [string] $Distribution = 'Ubuntu',
    [ValidateRange(1, 65535)]
    [int] $Port = 8765,
    [string] $Assets,
    [switch] $Preview,
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
        throw 'Could not verify the Windows browser handoff path inside WSL (wslpath returned an empty, failed, or unexpected result).'
    }
    return $value
}

function ConvertTo-Gen5WLinuxPath([object] $Output, [int] $ExitCode, [string] $Label) {
    $value = ($Output | Out-String).Trim()
    if ($ExitCode -ne 0 -or [string]::IsNullOrWhiteSpace($value) -or
        !$value.StartsWith('/') -or $value.Contains("`n") -or $value.Contains("`r")) {
        throw "Could not translate the Windows $Label path inside WSL. Move it to a mounted Windows drive or pass a Linux path from inside the distribution."
    }
    return $value
}

function Get-Gen5WConfiguredPython {
    return [Environment]::GetEnvironmentVariable('GEN5W_PYTHON', 'Process')
}

function Get-Gen5WLocalAppData {
    $value = [Environment]::GetEnvironmentVariable('LOCALAPPDATA', 'Process')
    if (![string]::IsNullOrWhiteSpace($value)) { return $value }
    $value = [Environment]::GetFolderPath([Environment+SpecialFolder]::LocalApplicationData)
    if (![string]::IsNullOrWhiteSpace($value)) { return $value }
    $profile = [Environment]::GetEnvironmentVariable('USERPROFILE', 'Process')
    if (![string]::IsNullOrWhiteSpace($profile)) {
        return Join-Path $profile 'AppData\Local'
    }
    return $null
}

function Get-Gen5WPythonPathValue {
    return [Environment]::GetEnvironmentVariable('PYTHONPATH', 'Process')
}

function Set-Gen5WPythonPathValue([AllowNull()][string] $Value) {
    [Environment]::SetEnvironmentVariable('PYTHONPATH', $Value, 'Process')
}

function ConvertTo-Gen5WWindowsPath([string] $Value) {
    if ([string]::IsNullOrWhiteSpace($Value)) { return $null }
    return $Value.Replace('/', '\')
}

function Get-Gen5WCanonicalPath([string] $Value) {
    $path = ConvertTo-Gen5WWindowsPath $Value
    if ([string]::IsNullOrWhiteSpace($path) -or $path.StartsWith('\\')) { return $path }
    try {
        return [IO.Path]::GetFullPath($path)
    } catch {
        return $path
    }
}

function Open-Gen5WFileMetadataHandle([string] $Path, [bool] $NoFollowReparsePoint) {
    $flagsAndAttributes = [uint32]0
    if ($NoFollowReparsePoint) {
        # APPEXECLINK placeholders reject a following zero-access handle, so
        # the trusted package alias must be opened as reparse metadata.
        $flagsAndAttributes = [uint32]0x00200000
    }
    try {
        return [Gen5WFileIdentity]::CreateFileW(
            $Path, [uint32]0, [uint32]7, [IntPtr]::Zero, [uint32]3,
            $flagsAndAttributes, [IntPtr]::Zero
        )
    } catch {
        return [IntPtr](-1)
    }
}

function Resolve-Gen5WFinalFilesystemPath([string] $Value, [switch] $NoFollowReparsePoint) {
    $path = Get-Gen5WCanonicalPath $Value
    if ([string]::IsNullOrWhiteSpace($path)) { return $null }
    if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) {
        if (Test-Path -LiteralPath $path -PathType Leaf) { return $path }
        return $null
    }
    if (!$NoFollowReparsePoint -and !(Test-Path -LiteralPath $path -PathType Leaf)) { return $null }

    if ($null -eq ('Gen5WFileIdentity' -as [type])) {
        try {
            Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using System.Text;

public static class Gen5WFileIdentity {
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    public static extern IntPtr CreateFileW(
        string fileName, uint desiredAccess, uint shareMode,
        IntPtr securityAttributes, uint creationDisposition,
        uint flagsAndAttributes, IntPtr templateFile);

    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern bool CloseHandle(IntPtr handle);

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    public static extern uint GetFinalPathNameByHandleW(
        IntPtr handle, [Out] StringBuilder filePath,
        uint filePathLength, uint flags);
}
'@
        } catch {
            return $null
        }
    }

    # Open for metadata only. Following the handle resolves junctions and
    # symlinks without invoking the candidate or reading its contents.
    $handle = Open-Gen5WFileMetadataHandle $path $NoFollowReparsePoint.IsPresent
    if ($handle.ToInt64() -eq -1) { return $null }
    try {
        # Exact package-family aliases are trusted by their registered identity
        # and canonical path. Validate metadata access without following the
        # APPEXECLINK target or deriving another path from it.
        if ($NoFollowReparsePoint) { return $path }

        $capacity = 1024
        for ($attempt = 0; $attempt -lt 2; $attempt++) {
            $buffer = New-Object Text.StringBuilder $capacity
            $length = [Gen5WFileIdentity]::GetFinalPathNameByHandleW(
                $handle, $buffer, [uint32]$capacity, [uint32]0
            )
            if ($length -eq 0) { return $null }
            if ($length -lt $capacity) {
                $resolved = $buffer.ToString()
                if ($resolved.StartsWith('\\?\UNC\')) { return '\\' + $resolved.Substring(8) }
                if ($resolved.StartsWith('\\?\')) { return $resolved.Substring(4) }
                return $resolved
            }
            if ($length -ge 32768) { return $null }
            $capacity = [int]$length + 1
        }
        return $null
    } catch {
        return $null
    } finally {
        [void][Gen5WFileIdentity]::CloseHandle($handle)
    }
}

function Test-Gen5WWindowsAppsPath([string] $Executable) {
    $path = Resolve-Gen5WFinalFilesystemPath $Executable
    # An unavailable identity is unsafe for the same reason as a known Store
    # alias: both can run through Windows application execution machinery.
    if ([string]::IsNullOrWhiteSpace($path)) { return $true }
    return $path -like '*\Microsoft\WindowsApps\*'
}

function Test-Gen5WNetworkPath([string] $Executable) {
    $path = ConvertTo-Gen5WWindowsPath $Executable
    return (![string]::IsNullOrWhiteSpace($path) -and $path.StartsWith('\\'))
}

function Test-Gen5WInstallManagerExecutionAlias([string] $Executable) {
    $path = Get-Gen5WCanonicalPath $Executable
    if ([string]::IsNullOrWhiteSpace($path) -or $path.StartsWith('\\') -or
        $path -notmatch '(?i)\\Microsoft\\WindowsApps\\PythonSoftwareFoundation\.PythonManager_(3847v3x7pw1km|qbz5n2kfra8p0)\\pymanager\.exe$') {
        return $false
    }
    return $null -ne (Resolve-Gen5WFinalFilesystemPath $path -NoFollowReparsePoint)
}

function Get-Gen5WApplicationCommands([string] $Name) {
    return @(
        Get-Command -Name $Name -CommandType Application -All -ErrorAction SilentlyContinue |
            ForEach-Object { ConvertTo-Gen5WWindowsPath ([string]$_.Source) } |
            Where-Object { ![string]::IsNullOrWhiteSpace($_) }
    )
}

function Resolve-Gen5WConfiguredPython([string] $Configured) {
    $normalized = ConvertTo-Gen5WWindowsPath $Configured
    if ([string]::IsNullOrWhiteSpace($normalized)) { return @() }
    if (Test-Gen5WNetworkPath $normalized) { return @() }
    if ($normalized.Contains('\')) { return @(Get-Gen5WCanonicalPath $normalized) }
    return @(Get-Gen5WApplicationCommands $normalized | ForEach-Object { Get-Gen5WCanonicalPath $_ })
}

function Resolve-Gen5WInstallManagerExecutionAlias([object[]] $Packages, [string] $LocalAppData) {
    $localAppDataPath = ConvertTo-Gen5WWindowsPath $LocalAppData
    if ([string]::IsNullOrWhiteSpace($localAppDataPath)) { return $null }
    foreach ($package in @($Packages)) {
        if ([string]$package.Name -ine 'PythonSoftwareFoundation.PythonManager') { continue }
        $packageFamilyName = [string]$package.PackageFamilyName
        if ($packageFamilyName -notmatch '^PythonSoftwareFoundation\.PythonManager_(3847v3x7pw1km|qbz5n2kfra8p0)$') { continue }
        $manager = Join-Path $localAppDataPath "Microsoft\WindowsApps\$packageFamilyName\pymanager.exe"
        if (Test-Gen5WInstallManagerExecutionAlias $manager) { return $manager }
    }
    return $null
}

function Get-Gen5WInstallManagerExecutionAlias {
    if (!(Get-Command -Name 'Get-AppxPackage' -CommandType Cmdlet -ErrorAction SilentlyContinue)) {
        return $null
    }
    try {
        $packages = @(
            Get-AppxPackage -Name 'PythonSoftwareFoundation.PythonManager' -ErrorAction Stop
        )
    } catch {
        return $null
    }
    return Resolve-Gen5WInstallManagerExecutionAlias $packages (Get-Gen5WLocalAppData)
}

function ConvertFrom-Gen5WPythonPathOutput([object[]] $Output) {
    $paths = New-Object Collections.ArrayList
    foreach ($line in @($Output)) {
        $normalized = ConvertTo-Gen5WWindowsPath ([string]$line).Trim()
        $match = [regex]::Match($normalized, '(?i)([A-Z]:\\.*?\.exe)"?\s*$')
        if (!$match.Success) { continue }
        $path = Get-Gen5WCanonicalPath $match.Groups[1].Value
        if (Test-Gen5WNetworkPath $path) { continue }
        $leaf = [IO.Path]::GetFileName($path)
        if ($leaf -notlike 'python*.exe') { continue }
        if ((Test-Path -LiteralPath $path -PathType Leaf) -and !(Test-Gen5WWindowsAppsPath $path)) {
            if (!$paths.Contains($path)) { [void]$paths.Add($path) }
        }
    }
    return $paths
}

function Invoke-Gen5WInstallManagerEnumeration([string] $Manager) {
    $Manager = Get-Gen5WCanonicalPath $Manager
    if ([string]::IsNullOrWhiteSpace($Manager) -or (Test-Gen5WNetworkPath $Manager)) { return @() }
    if ((Test-Gen5WWindowsAppsPath $Manager) -and !(Test-Gen5WInstallManagerExecutionAlias $Manager)) {
        return @()
    }
    $originalPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $output = @(& $Manager list --format=exe 2>&1)
        $exitCode = $LASTEXITCODE
    } catch {
        return @()
    } finally {
        $ErrorActionPreference = $originalPreference
    }
    if ($exitCode -ne 0) { return @() }
    return @(ConvertFrom-Gen5WPythonPathOutput $output)
}

function Get-Gen5WInstallManagerPythonPaths {
    $Manager = Get-Gen5WInstallManagerExecutionAlias
    if ([string]::IsNullOrWhiteSpace($Manager)) { return @() }
    return @(Invoke-Gen5WInstallManagerEnumeration $Manager)
}

function Get-Gen5WClassicLauncherPythonPaths([string] $Launcher) {
    if ([string]::IsNullOrWhiteSpace($Launcher)) {
        $Launcher = Get-Gen5WApplicationCommands 'py.exe' |
            Where-Object { !(Test-Gen5WWindowsAppsPath $_) } |
            Select-Object -First 1
    }
    $Launcher = Get-Gen5WCanonicalPath $Launcher
    if ([string]::IsNullOrWhiteSpace($Launcher) -or (Test-Gen5WWindowsAppsPath $Launcher)) { return @() }
    if (Test-Gen5WNetworkPath $Launcher) { return @() }
    $originalPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $output = @(& $Launcher -0p 2>&1)
        $exitCode = $LASTEXITCODE
    } catch {
        return @()
    } finally {
        $ErrorActionPreference = $originalPreference
    }
    if ($exitCode -ne 0) { return @() }
    return @(ConvertFrom-Gen5WPythonPathOutput $output)
}

function Get-Gen5WPythonCandidates {
    $candidates = New-Object Collections.ArrayList
    $seen = @{}
    $add = {
        param([string] $Executable, [string[]] $PrefixArguments)
        $Executable = Get-Gen5WCanonicalPath $Executable
        if ([string]::IsNullOrWhiteSpace($Executable)) { return }
        if (Test-Gen5WNetworkPath $Executable) { return }
        # Never probe an executable whose final filesystem target is a
        # WindowsApps alias. Install Manager aliases are enumerated below.
        if (Test-Gen5WWindowsAppsPath $Executable) { return }
        $prefix = @($PrefixArguments)
        $key = $Executable.ToLowerInvariant() + '|' + ($prefix -join '|')
        if ($seen.ContainsKey($key)) { return }
        $seen[$key] = $true
        [void]$candidates.Add([pscustomobject]@{
            Executable = $Executable
            Arguments = $prefix
        })
    }

    $configured = Get-Gen5WConfiguredPython
    $managerRequested = $false
    foreach ($configuredPath in @(Resolve-Gen5WConfiguredPython $configured)) {
        $configuredName = [IO.Path]::GetFileName($configuredPath)
        if ($configuredName -ieq 'pymanager.exe' -or $configuredName -ieq 'pymanager') {
            if (!$managerRequested) {
                foreach ($path in @(Get-Gen5WInstallManagerPythonPaths)) { & $add $path @() }
                $managerRequested = $true
            }
        } elseif ($configuredName -ieq 'py.exe' -or $configuredName -ieq 'py') {
            foreach ($path in @(Get-Gen5WClassicLauncherPythonPaths $configuredPath)) { & $add $path @() }
        } else {
            & $add $configuredPath @()
        }
    }

    foreach ($name in @('python.exe', 'python3.exe', 'python', 'python3')) {
        foreach ($path in @(Get-Gen5WApplicationCommands $name)) { & $add $path @() }
    }

    $localAppData = Get-Gen5WLocalAppData
    if (![string]::IsNullOrWhiteSpace($localAppData)) {
        $pythonRoot = Join-Path $localAppData 'Programs\Python'
        if (Test-Path -LiteralPath $pythonRoot -PathType Container) {
            Get-ChildItem -LiteralPath $pythonRoot -Directory -Filter 'Python*' -ErrorAction SilentlyContinue |
                Sort-Object Name -Descending |
                ForEach-Object { & $add (Join-Path $_.FullName 'python.exe') @() }
        }
    }
    if (!$managerRequested) {
        foreach ($path in @(Get-Gen5WInstallManagerPythonPaths)) { & $add $path @() }
    }
    foreach ($path in @(Get-Gen5WClassicLauncherPythonPaths)) {
        & $add $path @()
    }
    return $candidates
}

function Test-Gen5WPythonVersionSupported([version] $Version) {
    return $Version -ge [version]'3.10'
}

function Get-Gen5WPythonVersion([object] $Candidate) {
    if (!$Candidate -or [string]::IsNullOrWhiteSpace([string]$Candidate.Executable)) { return $null }
    $probeArguments = @($Candidate.Arguments) + @(
        '-B',
        '-c',
        'print(__import__(''sys'').version_info[0]);print(__import__(''sys'').version_info[1])'
    )
    $startInfo = New-Object Diagnostics.ProcessStartInfo
    $startInfo.FileName = [string]$Candidate.Executable
    $startInfo.Arguments = @($probeArguments) -join ' '
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $process = New-Object Diagnostics.Process
    $process.StartInfo = $startInfo
    try {
        if (!$process.Start()) { return $null }
        $stdoutTask = $process.StandardOutput.ReadToEndAsync()
        $stderrTask = $process.StandardError.ReadToEndAsync()
        if (!$process.WaitForExit(30000)) {
            $process.Kill()
            return $null
        }
        $stdout = $stdoutTask.Result
        $stderr = $stderrTask.Result
        $exitCode = $process.ExitCode
    } catch {
        return $null
    } finally {
        $process.Dispose()
    }
    if ($exitCode -ne 0) { return $null }
    $parts = @($stdout -split '\r?\n' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    if ($parts.Count -ne 2 -or $parts[0] -notmatch '^\d+$' -or $parts[1] -notmatch '^\d+$') {
        return $null
    }
    $version = [version]::new([int]$parts[0], [int]$parts[1])
    if (!(Test-Gen5WPythonVersionSupported $version)) { return $null }
    return $version
}

function Find-Gen5WPython {
    foreach ($candidate in @(Get-Gen5WPythonCandidates)) {
        $version = Get-Gen5WPythonVersion $candidate
        if ($null -eq $version) { continue }
        return [pscustomobject]@{
            Executable = $candidate.Executable
            Arguments = @($candidate.Arguments)
            Version = $version
        }
    }
    return $null
}

function Get-Gen5WPreviewArguments([switch] $SkipBrowser) {
    $arguments = @('-B', '-m', 'vm_workbench', '--preview', '--port', [string]$Port)
    if (!$SkipBrowser) { $arguments += '--open-browser' }
    return $arguments
}

function Format-Gen5WCommandArgument([string] $Value) {
    if ($Value -match '\s') { return '"' + $Value.Replace('"', '\"') + '"' }
    return $Value
}

function Format-Gen5WPreviewCommand([object] $Python, [string[]] $Arguments) {
    $allArguments = @($Python.Arguments) + @($Arguments)
    return (@((Format-Gen5WCommandArgument $Python.Executable)) +
        @($allArguments | ForEach-Object { Format-Gen5WCommandArgument ([string]$_) })) -join ' '
}

function Get-Gen5WPreviewPythonPath {
    $projectPath = Join-Path $root 'tools/uk_fw'
    $existing = Get-Gen5WPythonPathValue
    if ([string]::IsNullOrWhiteSpace($existing)) { return $projectPath }
    return $projectPath + [IO.Path]::PathSeparator + $existing
}

function Get-Gen5WPreviewWingetInstallCommand {
    return 'winget install --id Python.Python.3.13 -e --silent --scope user --accept-package-agreements --accept-source-agreements --disable-interactivity'
}

function Write-Gen5WPreviewPythonPlan {
    Write-Gen5WSetup 'Python 3.10 or newer was not found; no preview state has been created.'
    Write-Gen5WSetup 'Required action:'
    Write-Gen5WSetup ('  ' + (Get-Gen5WPreviewWingetInstallCommand))
}

function Test-Gen5WPythonInstallConsent {
    if ($Yes) {
        Write-Gen5WSetup 'Python installation accepted by -Yes using the displayed current-user winget plan.'
        return $true
    }
    if ([Console]::IsInputRedirected) {
        Write-Gen5WSetup 'Python is required. Reopen in a terminal or pass -Yes to accept the displayed current-user install plan.'
        return $false
    }
    return (Read-Host 'Install Python 3.13 for the current user with the displayed winget plan? [y/N]') -match '^(y|yes)$'
}

function Invoke-Gen5WWingetPythonInstall {
    $command = Get-Command -Name 'winget.exe' -CommandType Application -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if (!$command) {
        $command = Get-Command -Name 'winget' -CommandType Application -ErrorAction SilentlyContinue |
            Select-Object -First 1
    }
    if (!$command) {
        return [pscustomobject]@{ ExitCode = 127; Message = 'winget is unavailable. Install App Installer from Microsoft Store, then reopen Gen5W-Preview.cmd.' }
    }
    $arguments = @('install', '--id', 'Python.Python.3.13', '-e', '--silent', '--scope', 'user',
        '--accept-package-agreements', '--accept-source-agreements', '--disable-interactivity')
    & $command.Source @arguments | Out-Host
    $exitCode = $LASTEXITCODE
    if ($null -eq $exitCode) { $exitCode = 0 }
    return [pscustomobject]@{ ExitCode = $exitCode; Message = $null }
}

function Invoke-Gen5WNativePython([object] $Python, [string[]] $Arguments) {
    $allArguments = @($Python.Arguments) + @($Arguments)
    & $Python.Executable @allArguments | Out-Host
    $script:gen5wLastNativeExitCode = $LASTEXITCODE
    if ($null -eq $script:gen5wLastNativeExitCode) { $script:gen5wLastNativeExitCode = 0 }
}

function Invoke-Gen5WWsl([string[]] $Arguments) {
    & $wsl @Arguments
}

function Write-Gen5WDeferredPlan {
    Write-Gen5WSetup 'Deferred setup plan: Ubuntu is not available; downstream checks have not run.'
    Write-Gen5WSetup '1. Enable WSL / Virtual Machine Platform and install Ubuntu (Windows UAC may require the local desktop).'
    Write-Gen5WSetup '2. Restart Windows if requested; open Ubuntu once and create a regular Linux account.'
    Write-Gen5WSetup '3. Reopen this launcher. WSL2 is preferred; WSL1 uses the same QEMU TCG software emulation when nested virtualization is unavailable.'
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

function Invoke-Gen5WPreviewLauncher {
    $python = Find-Gen5WPython
    if (!$python) {
        Write-Gen5WPreviewPythonPlan
        if ($Plan) { return 0 }
        if (!(Test-Gen5WPythonInstallConsent)) { return 1 }
        $install = Invoke-Gen5WWingetPythonInstall
        if ($install.ExitCode -ne 0) {
            if ($install.Message) { Write-Gen5WSetup ("Preview stopped: " + $install.Message) }
            else { Write-Gen5WSetup "Preview stopped: Python installation exited $($install.ExitCode)." }
            return $install.ExitCode
        }
        $python = Find-Gen5WPython
        if (!$python) {
            Write-Gen5WSetup 'Python 3.13 installation finished, but no Python 3.10+ runtime was found in this process.'
            Write-Gen5WSetup 'Reopen Gen5W-Preview.cmd from a new terminal so the user PATH can refresh.'
            return 1
        }
    }

    $pythonArguments = @(Get-Gen5WPreviewArguments -SkipBrowser:([bool]$NoBrowser))
    $commandLine = Format-Gen5WPreviewCommand $python $pythonArguments
    Write-Gen5WSetup "Native preview Python: $($python.Executable) (version $($python.Version))"
    Write-Gen5WSetup "PYTHONPATH: $(Get-Gen5WPreviewPythonPath)"
    Write-Gen5WSetup ('> ' + $commandLine)
    if ($Plan) {
        Write-Gen5WSetup 'Native preview plan complete; no server, browser, WSL check, asset setup, or VM state was created.'
        return 0
    }

    $originalPythonPath = Get-Gen5WPythonPathValue
    $result = 1
    try {
        Set-Gen5WPythonPathValue (Get-Gen5WPreviewPythonPath)
        $script:gen5wLastNativeExitCode = $null
        Invoke-Gen5WNativePython $python $pythonArguments
        if ($null -eq $script:gen5wLastNativeExitCode) { $result = 1 }
        else { $result = $script:gen5wLastNativeExitCode }
    } catch {
        Write-Gen5WSetup "Preview stopped: $_"
        $result = 1
    } finally {
        Set-Gen5WPythonPathValue $originalPythonPath
    }
    Write-Gen5WSetup "Native preview exit: $result"
    return $result
}

function Invoke-Gen5WLauncher {
    if ($Preview -and (![string]::IsNullOrWhiteSpace($Assets) -or $WifiSim -or $SetupHostname)) {
        Write-Gen5WSetup 'Preview stopped: -Preview cannot be combined with -Assets, -WifiSim, or -SetupHostname. No files or VM state were changed.'
        return 1
    }
    if ($Preview) { return Invoke-Gen5WPreviewLauncher }
    return Invoke-Gen5WFullVmLauncher
}

function Invoke-Gen5WFullVmLauncher {
    try {
        if (!$Plan) {
            $logRoot = Join-Path $root '.gen5w\logs'
            [void][IO.Directory]::CreateDirectory($logRoot)
            $log = Join-Path $logRoot ("windows-bootstrap-{0}.log" -f [Guid]::NewGuid().ToString('N'))
            Write-Gen5WSetup "Setup log: $log"
        }
        Write-Gen5WSetup 'Gen5W VM Workbench for Windows uses WSL2, with a WSL1 software-emulation fallback.'
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
                throw "The requested WSL distribution '$Distribution' is unavailable. Install it in WSL or use Ubuntu."
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
        if ($version -eq '1') {
            Write-Gen5WSetup 'WSL1 compatibility mode selected. The VM uses QEMU TCG software emulation; nested virtualization is not used.'
        } elseif ($version -ne '2') {
            throw "Distribution '$Distribution' reports an unsupported WSL version."
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
        $assetsArgument = @()
        if (![string]::IsNullOrWhiteSpace($Assets)) {
            if ($Assets.StartsWith('/')) {
                $linuxAssets = ConvertTo-Gen5WLinuxPath $Assets 0 'asset'
            } else {
                $assetOutput = Invoke-Gen5WWsl -Arguments @('--distribution', $Distribution, '--exec',
                    '/usr/bin/wslpath', '-u', $Assets)
                $linuxAssets = ConvertTo-Gen5WLinuxPath $assetOutput $LASTEXITCODE 'asset'
            }
            Write-Gen5WSetup "Linux asset directory: $linuxAssets"
            $assetsArgument = @('--assets', $linuxAssets)
        }
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
                       '--windows-fallback-port', [string]$fallback) + $assetsArgument
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
