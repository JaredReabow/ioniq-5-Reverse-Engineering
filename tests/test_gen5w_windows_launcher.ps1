# Exercise launcher decisions without WSL, a browser, Python, elevation or downloads.
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
    Assert-Gen5WEqual (ConvertTo-Gen5WLinuxPath '/mnt/c/assets' 0 'asset') '/mnt/c/assets' 'asset path'
    $rejected = $false
    try { [void](ConvertTo-Gen5WLinuxPath 'C:\assets' 0 'asset') } catch { $rejected = $true }
    Assert-Gen5WEqual $rejected $true 'invalid Linux asset path'
    foreach ($value in @($null, '', ' ', '/mnt/c/Windows/notepad.exe', "/mnt/c/Windows/explorer.exe`nother")) {
        $rejected = $false
        try { [void](ConvertTo-Gen5WBrowserPath $value 0) } catch { $rejected = $true }
        Assert-Gen5WEqual $rejected $true 'invalid browser output'
    }
    $rejected = $false
    try { [void](ConvertTo-Gen5WBrowserPath '/mnt/c/Windows/explorer.exe' 1) } catch { $rejected = $true }
    Assert-Gen5WEqual $rejected $true 'failed wslpath'
    Assert-Gen5WEqual (Test-Gen5WConsent 'Fixture consent') $true 'explicit consent'
    Assert-Gen5WEqual (Test-Gen5WPythonVersionSupported ([version]'3.9')) $false 'old Python rejected'
    Assert-Gen5WEqual (Test-Gen5WPythonVersionSupported ([version]'3.10')) $true 'Python 3.10 accepted'

    $cmd = [IO.File]::ReadAllText((Join-Path $testRoot 'launchers/Gen5W.cmd'))
    $previewCmd = [IO.File]::ReadAllText((Join-Path $testRoot 'launchers/Gen5W-Preview.cmd'))
    Assert-Gen5WEqual $cmd.Contains('"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"') $true 'full wrapper PowerShell path'
    Assert-Gen5WEqual $cmd.Contains('-File "%~dp0Gen5W.ps1" %*') $true 'full wrapper quoted checkout path'
    Assert-Gen5WEqual $previewCmd.Contains('-File "%~dp0Gen5W.ps1" -Preview %*') $true 'preview wrapper dispatch'
    Assert-Gen5WEqual $previewCmd.Contains('"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"') $true 'preview wrapper PowerShell path'
    Assert-Gen5WEqual $previewCmd.Contains('-NoPause') $true 'preview wrapper no pause'
    Assert-Gen5WEqual $previewCmd.Contains('ExecutionPolicy Bypass') $false 'preview wrapper policy'

    if ($env:OS -eq 'Windows_NT') {
        # Exercise cmd.exe's quoting against a checkout path containing spaces.
        $fixtureCheckout = Join-Path $temporary 'checkout with spaces'
        $fixtureLaunchers = Join-Path $fixtureCheckout 'launchers'
        [void][IO.Directory]::CreateDirectory($fixtureLaunchers)
        Copy-Item -LiteralPath (Join-Path $testRoot 'launchers/Gen5W.ps1') -Destination $fixtureLaunchers
        Copy-Item -LiteralPath (Join-Path $testRoot 'launchers/Gen5W-Preview.cmd') -Destination $fixtureLaunchers
        $fixturePython = Join-Path $fixtureCheckout 'fixture python\python.exe.cmd'
        [void][IO.Directory]::CreateDirectory((Split-Path -Parent $fixturePython))
        $selectedPythonMarker = Join-Path $fixtureCheckout 'selected-python.txt'
        $fixturePythonBody = @(
            '@echo off'
            ('> "{0}" echo {1}^|3.13' -f $selectedPythonMarker, $fixturePython)
            '@echo 3'
            '@echo 13'
        ) -join [Environment]::NewLine
        [IO.File]::WriteAllText($fixturePython, $fixturePythonBody)
        $originalFixturePython = $env:GEN5W_PYTHON
        try {
            $env:GEN5W_PYTHON = $fixturePython
            $wrapper = Join-Path $fixtureLaunchers 'Gen5W-Preview.cmd'
            $wrapperLines = @(& $wrapper -Plan -NoBrowser -Port 9124 -NoPause 2>&1)
            $wrapperExit = $LASTEXITCODE
            $wrapperText = $wrapperLines -join "`n"
            Assert-Gen5WEqual $wrapperExit 0 'preview wrapper dispatch exit'
            Assert-Gen5WEqual $wrapperText.Contains('--preview --port 9124') $true 'preview wrapper plan arguments'
            Assert-Gen5WEqual $wrapperText.Contains('--open-browser') $false 'preview wrapper no browser'
            $selectedPython = [IO.File]::ReadAllText($selectedPythonMarker).Trim()
            Assert-Gen5WEqual $selectedPython ($fixturePython + '|3.13') 'preview wrapper selects supplied interpreter'
        } finally {
            $env:GEN5W_PYTHON = $originalFixturePython
        }
    }

    # Production discovery must prefer an explicitly selected interpreter, fall
    # back when the packaged session has no LOCALAPPDATA, resolve bare names,
    # and filter aliases without hiding later real PATH applications.
    $originalConfiguredPython = $env:GEN5W_PYTHON
    $originalLocalAppData = $env:LOCALAPPDATA
    $originalPath = $env:PATH
    $expectedUserPythonVersion = $env:GEN5W_EXPECTED_USER_PYTHON_VERSION
    try {
        if ($env:OS -eq 'Windows_NT') {
            $configuredPythonFixture = Join-Path $temporary 'fixture checkout\python.exe'
            [void][IO.Directory]::CreateDirectory((Split-Path -Parent $configuredPythonFixture))
            [IO.File]::WriteAllText($configuredPythonFixture, 'fixture interpreter')
            $env:GEN5W_PYTHON = $configuredPythonFixture.Replace('\', '/')
            $candidates = @(Get-Gen5WPythonCandidates)
            Assert-Gen5WEqual $candidates[0].Executable $configuredPythonFixture 'configured Python first'
            Assert-Gen5WEqual ($candidates[0].Arguments -join '|') '' 'configured Python has no launcher selector'
        } else {
            Assert-Gen5WEqual (ConvertTo-Gen5WWindowsPath 'C:/fixture checkout/python.exe') 'C:\fixture checkout\python.exe' 'Windows path conversion'
        }

        $fixtureLocalAppData = Join-Path $temporary 'explicit-local-appdata'
        $env:LOCALAPPDATA = $fixtureLocalAppData
        Assert-Gen5WEqual (Get-Gen5WLocalAppData) $fixtureLocalAppData 'explicit local appdata wins'

        $env:GEN5W_PYTHON = $null
        $env:LOCALAPPDATA = $null
        $fallbackLocalAppData = Get-Gen5WLocalAppData
        Assert-Gen5WEqual (![string]::IsNullOrWhiteSpace($fallbackLocalAppData)) $true 'local appdata fallback'
        Assert-Gen5WEqual ([IO.Path]::IsPathRooted($fallbackLocalAppData)) $true 'local appdata fallback is absolute'
        $fallbackCandidates = @(Get-Gen5WPythonCandidates)
        $userPythonRoot = Join-Path $fallbackLocalAppData 'Programs\Python'
        $installedUserPythons = @(
            Get-ChildItem -LiteralPath $userPythonRoot -Directory -Filter 'Python*' -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -match '^Python\d{3}$' } |
                ForEach-Object { Join-Path $_.FullName 'python.exe' } |
                Where-Object { Test-Path -LiteralPath $_ -PathType Leaf }
        )
        foreach ($installedUserPython in $installedUserPythons) {
            Assert-Gen5WEqual (@($fallbackCandidates | Where-Object { $_.Executable -ieq $installedUserPython }).Count) 1 "fallback candidate $installedUserPython"
        }

        if ($installedUserPythons.Count -gt 0) {
            $foundFallbackPython = Find-Gen5WPython
            if ($foundFallbackPython) {
                Assert-Gen5WEqual (Test-Gen5WWindowsAppsPath $foundFallbackPython.Executable) $false 'resolved Python excludes WindowsApps alias'
            } elseif ($env:GEN5W_REQUIRE_USER_PYTHON -eq '1' -or ![string]::IsNullOrWhiteSpace($expectedUserPythonVersion)) {
                Assert-Gen5WEqual $true $false 'fallback Python resolves with LOCALAPPDATA absent'
            }

            if ($foundFallbackPython -and ![string]::IsNullOrWhiteSpace($expectedUserPythonVersion)) {
                $fullVersion = @(& $foundFallbackPython.Executable @($foundFallbackPython.Arguments) -B -c 'import platform;print(platform.python_version())' 2>&1)
                Assert-Gen5WEqual $LASTEXITCODE 0 'fallback Python full-version probe exit'
                Assert-Gen5WEqual (($fullVersion | Out-String).Trim()) $expectedUserPythonVersion 'fallback Python full version'
            }
        } elseif ($env:GEN5W_REQUIRE_USER_PYTHON -eq '1') {
            Assert-Gen5WEqual ($installedUserPythons.Count -gt 0) $true 'required user Python installation'
        }

        if ($env:OS -eq 'Windows_NT') {
            $aliasDirectory = Join-Path $temporary 'Microsoft\WindowsApps'
            $validPathDirectory = Join-Path $temporary 'valid-python-path'
            [void][IO.Directory]::CreateDirectory($aliasDirectory)
            [void][IO.Directory]::CreateDirectory($validPathDirectory)
            $storePlaceholder = Join-Path $aliasDirectory 'python.exe'
            $validPathPython = Join-Path $validPathDirectory 'python.exe'
            [IO.File]::WriteAllBytes($storePlaceholder, [byte[]]@())
            [IO.File]::WriteAllText($validPathPython, 'fixture interpreter')
            Assert-Gen5WEqual (Test-Gen5WWindowsAppsPath $storePlaceholder) $true 'WindowsApps path classified'
            Assert-Gen5WEqual (Test-Gen5WWindowsAppsPath $validPathPython) $false 'non-alias path accepted'
            Assert-Gen5WEqual (Test-Gen5WNetworkPath '\\server\share\python.exe') $true 'UNC path classified'
            $dotSegmentAlias = Join-Path $aliasDirectory '.\python.exe'
            Assert-Gen5WEqual (Test-Gen5WWindowsAppsPath $dotSegmentAlias) $true 'dot-segment alias canonicalized before filtering'

            $env:GEN5W_PYTHON = $storePlaceholder.Replace('\', '/')
            Assert-Gen5WEqual (Test-Gen5WWindowsAppsPath $env:GEN5W_PYTHON) $true 'forward-slash alias normalized before filtering'
            Assert-Gen5WEqual (@(Get-Gen5WPythonCandidates | Where-Object { $_.Executable -ieq $storePlaceholder }).Count) 0 'configured alias excluded'

            $env:GEN5W_PYTHON = $dotSegmentAlias
            Assert-Gen5WEqual (@(Get-Gen5WPythonCandidates | Where-Object { $_.Executable -ieq $storePlaceholder }).Count) 0 'configured dot-segment alias excluded'

            $junctionParent = Join-Path $temporary 'outside-windowsapps'
            [void][IO.Directory]::CreateDirectory($junctionParent)
            $junctionPath = Join-Path $junctionParent 'store-target'
            New-Item -ItemType Junction -Path $junctionPath -Target $aliasDirectory -ErrorAction Stop | Out-Null
            $junctionPlaceholder = Join-Path $junctionPath 'python.exe'
            Assert-Gen5WEqual (Test-Gen5WWindowsAppsPath $junctionPlaceholder) $true 'junction into WindowsApps excluded'
            $env:GEN5W_PYTHON = $junctionPlaceholder
            Assert-Gen5WEqual (@(Get-Gen5WPythonCandidates | Where-Object { $_.Executable -ieq $junctionPlaceholder }).Count) 0 'configured junction alias excluded'

            $missingConfiguredPython = Join-Path $temporary 'missing-python\python.exe'
            Assert-Gen5WEqual (Test-Gen5WWindowsAppsPath $missingConfiguredPython) $true 'missing path identity fails closed'
            $env:GEN5W_PYTHON = $missingConfiguredPython
            Assert-Gen5WEqual (@(Get-Gen5WPythonCandidates | Where-Object { $_.Executable -ieq $missingConfiguredPython }).Count) 0 'unverifiable configured path excluded'

            $env:GEN5W_PYTHON = $validPathPython.Replace('\', '/')
            $forwardSlashCandidates = @(Get-Gen5WPythonCandidates)
            Assert-Gen5WEqual $forwardSlashCandidates[0].Executable $validPathPython 'forward-slash real interpreter normalized'

            $env:GEN5W_PYTHON = 'python'
            $env:PATH = $aliasDirectory + [IO.Path]::PathSeparator + $validPathDirectory +
                [IO.Path]::PathSeparator + $originalPath
            $pathCandidates = @(Get-Gen5WPythonCandidates)
            Assert-Gen5WEqual (@($pathCandidates | Where-Object { $_.Executable -ieq $storePlaceholder }).Count) 0 'first PATH alias excluded'
            Assert-Gen5WEqual (@($pathCandidates | Where-Object { $_.Executable -ieq $validPathPython }).Count) 1 'later PATH interpreter retained'

            $env:GEN5W_PYTHON = '//server/share/python.exe'
            Assert-Gen5WEqual (@(Get-Gen5WPythonCandidates | Where-Object { $_.Executable -like '\\*' }).Count) 0 'configured UNC interpreter excluded'
            Assert-Gen5WEqual (@(ConvertFrom-Gen5WPythonPathOutput @('\\server\share\python.exe')).Count) 0 'UNC parser output excluded'

            $protectedManagerRoot = Join-Path $temporary 'protected-install'
            [void][IO.Directory]::CreateDirectory($protectedManagerRoot)
            $protectedManager = Join-Path $protectedManagerRoot 'pymanager.exe'
            Copy-Item -LiteralPath (Join-Path $env:SystemRoot 'System32\whoami.exe') -Destination $protectedManager
            $protectedAcl = Get-Acl -LiteralPath $protectedManager
            $protectedRule = [System.Security.AccessControl.FileSystemAccessRule]::new(
                [Security.Principal.WindowsIdentity]::GetCurrent().Name,
                [System.Security.AccessControl.FileSystemRights]::ReadAndExecute,
                [System.Security.AccessControl.AccessControlType]::Deny
            )
            $protectedAcl.AddAccessRule($protectedRule)
            Set-Acl -LiteralPath $protectedManager -AclObject $protectedAcl
            try {
                $protectedExecutionDenied = $false
                try { $null = @(& $protectedManager list --format=exe 2>&1) } catch { $protectedExecutionDenied = $true }
                Assert-Gen5WEqual $protectedExecutionDenied $true 'protected install executable denied'
            } finally {
                $protectedAcl.RemoveAccessRule($protectedRule) | Out-Null
                Set-Acl -LiteralPath $protectedManager -AclObject $protectedAcl
            }

            $packageFamilyName = 'PythonSoftwareFoundation.PythonManager_3847v3x7pw1km'
            $packageAliasDirectory = Join-Path $aliasDirectory $packageFamilyName
            [void][IO.Directory]::CreateDirectory($packageAliasDirectory)
            $managerAlias = Join-Path $packageAliasDirectory 'pymanager.exe'
            $managerRuntime = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
            Assert-Gen5WEqual (Test-Path -LiteralPath $managerRuntime -PathType Leaf) $true 'manager fixture runtime available'
            $installedManagerPython = Join-Path $temporary 'Python Install Manager\python3.13t.exe'
            [void][IO.Directory]::CreateDirectory((Split-Path -Parent $installedManagerPython))
            [IO.File]::WriteAllText($installedManagerPython, 'fixture interpreter')
            # Copy the signed Windows PowerShell host into the protected alias
            # shape. Its list command comes from a controlled fixture PATH.
            Copy-Item -LiteralPath $managerRuntime -Destination $managerAlias
            $managerWorkingDirectory = Join-Path $temporary 'manager-working-directory'
            [void][IO.Directory]::CreateDirectory($managerWorkingDirectory)
            $managerListBody = @('@echo off', ('@echo ' + $installedManagerPython)) -join [Environment]::NewLine
            [IO.File]::WriteAllText((Join-Path $managerWorkingDirectory 'list.cmd'), $managerListBody)
            $wrongPackage = [pscustomobject]@{
                Name = 'Contoso.NotPython'
                PackageFamilyName = $packageFamilyName
                InstallLocation = $protectedManagerRoot
            }
            $managerPackage = [pscustomobject]@{
                Name = 'PythonSoftwareFoundation.PythonManager'
                PackageFamilyName = $packageFamilyName
                InstallLocation = $protectedManagerRoot
            }
            $storeAliasDirectory = Join-Path $aliasDirectory 'PythonSoftwareFoundation.PythonManager_qbz5n2kfra8p0'
            [void][IO.Directory]::CreateDirectory($storeAliasDirectory)
            $storeAlias = Join-Path $storeAliasDirectory 'pymanager.exe'
            Copy-Item -LiteralPath $managerRuntime -Destination $storeAlias

            # APPEXECLINK reparse files reject zero-access handles that follow
            # the link. Emulate that Windows behavior by denying ordinary opens
            # for the two registered aliases while allowing reparse metadata.
            $script:originalMetadataOpen = (Get-Command Open-Gen5WFileMetadataHandle -CommandType Function).ScriptBlock
            $script:managerMetadataCalls = @()
            try {
                function Open-Gen5WFileMetadataHandle([string] $Path, [bool] $NoFollowReparsePoint) {
                    $script:managerMetadataCalls += [pscustomobject]@{
                        Path = $Path
                        NoFollowReparsePoint = $NoFollowReparsePoint
                    }
                    if (!$NoFollowReparsePoint -and ($Path -ieq $managerAlias -or $Path -ieq $storeAlias)) {
                        return [IntPtr](-1)
                    }
                    & $script:originalMetadataOpen -Path $Path -NoFollowReparsePoint:$NoFollowReparsePoint
                }

                Assert-Gen5WEqual (Test-Gen5WWindowsAppsPath $managerAlias) $true 'denied normal handle fails closed for python.org alias'
                Assert-Gen5WEqual (Test-Gen5WWindowsAppsPath $storeAlias) $true 'denied normal handle fails closed for Store alias'
                $resolvedManager = Resolve-Gen5WInstallManagerExecutionAlias @($wrongPackage, $managerPackage) $temporary
                Assert-Gen5WEqual $resolvedManager $managerAlias 'manager resolved through package-family alias'
                Assert-Gen5WEqual ($resolvedManager -ieq $protectedManager) $false 'protected install path not selected'
                Assert-Gen5WEqual (Test-Gen5WInstallManagerExecutionAlias $managerAlias) $true 'python.org package-family alias metadata allowed'
                Assert-Gen5WEqual (Test-Gen5WInstallManagerExecutionAlias $storeAlias) $true 'Store package-family alias metadata allowed'
                Assert-Gen5WEqual (@($script:managerMetadataCalls | Where-Object {
                    $_.Path -ieq $managerAlias -and $_.NoFollowReparsePoint
                }).Count -gt 0) $true 'python.org alias opened without following'
                Assert-Gen5WEqual (@($script:managerMetadataCalls | Where-Object {
                    $_.Path -ieq $storeAlias -and $_.NoFollowReparsePoint
                }).Count -gt 0) $true 'Store alias opened without following'

                $genericManagerAlias = Join-Path $aliasDirectory 'pymanager.exe'
                [IO.File]::WriteAllBytes($genericManagerAlias, [byte[]]@())
                $callsBeforeGeneric = $script:managerMetadataCalls.Count
                Assert-Gen5WEqual (Test-Gen5WInstallManagerExecutionAlias $genericManagerAlias) $false 'generic manager alias rejected'
                Assert-Gen5WEqual $script:managerMetadataCalls.Count $callsBeforeGeneric 'generic manager alias not probed as reparse metadata'
                Assert-Gen5WEqual (@(Invoke-Gen5WInstallManagerEnumeration $genericManagerAlias).Count) 0 'generic manager alias not executed'

                $managerPathBeforeFixture = $env:PATH
                try {
                    $env:PATH = $managerWorkingDirectory + [IO.Path]::PathSeparator + $env:PATH
                    Push-Location $managerWorkingDirectory
                    $managerPaths = @(Invoke-Gen5WInstallManagerEnumeration $resolvedManager)
                } finally {
                    Pop-Location
                    $env:PATH = $managerPathBeforeFixture
                }
            } finally {
                Set-Item Function:\Open-Gen5WFileMetadataHandle -Value $script:originalMetadataOpen
            }
            Assert-Gen5WEqual $managerPaths.Count 1 'pymanager installed path count'
            Assert-Gen5WEqual $managerPaths[0] $installedManagerPython 'versioned free-threaded interpreter parsed'

            $env:GEN5W_PYTHON = $managerAlias
            Assert-Gen5WEqual (@(Get-Gen5WPythonCandidates | Where-Object { $_.Executable -ieq $managerAlias }).Count) 0 'configured manager alias excluded from interpreter candidates'

            $version = Get-Gen5WPythonVersion ([pscustomobject]@{
                Executable = (Join-Path $env:SystemRoot 'System32\cmd.exe')
                Arguments = @('/d', '/c', 'echo 3 & echo 13 & echo benign import timing 1>&2 & exit /b 0 & rem')
            })
            Assert-Gen5WEqual $version ([version]'3.13') 'benign stderr does not poison version probe'
            $stderrOnlyVersion = Get-Gen5WPythonVersion ([pscustomobject]@{
                Executable = (Join-Path $env:SystemRoot 'System32\cmd.exe')
                Arguments = @('/d', '/c', 'echo 3 1>&2 & echo 13 1>&2 & exit /b 0 & rem')
            })
            Assert-Gen5WEqual $stderrOnlyVersion $null 'version probe parses stdout only'

            $forwardSlashManagerOutput = @('  -V:3.13 * ' + $installedManagerPython.Replace('\', '/'))
            $parsedManagerPaths = @(ConvertFrom-Gen5WPythonPathOutput $forwardSlashManagerOutput)
            Assert-Gen5WEqual $parsedManagerPaths.Count 1 'forward-slash manager path count'
            Assert-Gen5WEqual $parsedManagerPaths[0] $installedManagerPython 'forward-slash manager path parsed'

            $missingManagerPython = Join-Path $temporary 'Python Install Manager\python3.14t.exe'
            $parsedMissingPaths = @(ConvertFrom-Gen5WPythonPathOutput @($missingManagerPython))
            Assert-Gen5WEqual $parsedMissingPaths.Count 0 'missing parser leaf excluded'

            $classicFixture = Join-Path $temporary 'py.exe.cmd'
            [IO.File]::WriteAllText($classicFixture, "@echo off`r`n@echo  -V:3.13 * $installedManagerPython`r`n")
            $classicPaths = @(Get-Gen5WClassicLauncherPythonPaths $classicFixture)
            Assert-Gen5WEqual $classicPaths.Count 1 'classic launcher installed path count'
            Assert-Gen5WEqual $classicPaths[0] $installedManagerPython 'classic launcher installed path parsed'
        }
    } finally {
        $env:GEN5W_PYTHON = $originalConfiguredPython
        $env:LOCALAPPDATA = $originalLocalAppData
        $env:PATH = $originalPath
    }
    $script:versionProbes = @()
    function Get-Gen5WPythonCandidates {
        return @(
            [pscustomobject]@{ Executable = 'C:\old\py.exe'; Arguments = @('-3') },
            [pscustomobject]@{ Executable = 'C:\Users\Leo\AppData\Local\Programs\Python\Python313\python.exe'; Arguments = @() }
        )
    }
    function Get-Gen5WPythonVersion([object] $Candidate) {
        $script:versionProbes += $Candidate.Executable
        if ($Candidate.Executable -like '*Python313\python.exe') { return [version]'3.13' }
        return $null
    }
    $foundPython = Find-Gen5WPython
    Assert-Gen5WEqual $foundPython.Executable 'C:\Users\Leo\AppData\Local\Programs\Python\Python313\python.exe' 'user Python discovery'
    Assert-Gen5WEqual $foundPython.Version.ToString(2) '3.13' 'minimum Python version accepted'
    Assert-Gen5WEqual $versionProbes.Count 2 'old Python rejected'

    # Replace process boundaries with deterministic fixtures. The real
    # argument and environment assembly remains under test.
    $previewRoot = Join-Path $temporary 'checkout with spaces'
    $script:messages = @()
    $script:wslCalls = 0
    $script:nativeCalls = 0
    $script:installCalls = 0
    $script:consentCalls = 0
    $script:pythonLookups = 0
    $script:pythonAvailable = $true
    $script:nativeExit = 0
    $script:pythonPathDuring = $null
    $script:nativeExecutable = $null
    $script:nativeArguments = @()
    $script:fixturePython = [pscustomobject]@{
        Executable = 'C:\fixture checkout with spaces\py.exe'
        Arguments = @('-3')
        Version = [version]'3.13'
    }
    function Write-Gen5WSetup([string] $Message) { $script:messages += $Message }
    function Invoke-Gen5WWsl([string[]] $Arguments) {
        $script:wslCalls++
        throw 'Preview fixture attempted WSL'
    }
    function Find-Gen5WPython {
        $script:pythonLookups++
        if ($script:pythonAvailable) { return $script:fixturePython }
        return $null
    }
    function Invoke-Gen5WNativePython([object] $Python, [string[]] $Arguments) {
        $script:nativeCalls++
        $script:nativeExecutable = $Python.Executable
        $script:nativeArguments = @($Python.Arguments) + @($Arguments)
        $script:pythonPathDuring = Get-Gen5WPythonPathValue
        $script:gen5wLastNativeExitCode = $script:nativeExit
    }
    function Invoke-Gen5WWingetPythonInstall {
        $script:installCalls++
        $script:pythonAvailable = $true
        return [pscustomobject]@{ ExitCode = 0; Message = $null }
    }

    $script:root = $previewRoot
    $script:Preview = $true
    $script:Plan = $false
    $script:Yes = $false
    $script:NoPause = $true
    $script:NoBrowser = $false
    $script:Assets = $null
    $script:WifiSim = $false
    $script:SetupHostname = $false
    $script:Port = 9123
    $originalPythonPath = $env:PYTHONPATH
    try {
        $env:PYTHONPATH = 'existing-python-path'
        $script:messages = @()
        Assert-Gen5WEqual (Invoke-Gen5WLauncher) 0 'native preview launch'
        Assert-Gen5WEqual $nativeExecutable $fixturePython.Executable 'native Python executable'
        Assert-Gen5WEqual ($nativeArguments -join '|') '-3|-B|-m|vm_workbench|--preview|--port|9123|--open-browser' 'native preview arguments'
        Assert-Gen5WEqual $wslCalls 0 'preview never invokes WSL'
        Assert-Gen5WEqual ([IO.Directory]::Exists((Join-Path $previewRoot '.gen5w'))) $false 'preview does not create state'
        $expectedPath = (Join-Path $previewRoot 'tools/uk_fw') + [IO.Path]::PathSeparator + 'existing-python-path'
        Assert-Gen5WEqual $pythonPathDuring $expectedPath 'preview PYTHONPATH during launch'
        Assert-Gen5WEqual $env:PYTHONPATH 'existing-python-path' 'preview PYTHONPATH restored'
        Assert-Gen5WEqual (($messages -join "`n").Contains('"C:\fixture checkout with spaces\py.exe" -3 -B')) $true 'quoted preview command'
    } finally {
        $env:PYTHONPATH = $originalPythonPath
    }

    $script:NoBrowser = $true
    $script:nativeCalls = 0
    Assert-Gen5WEqual (Invoke-Gen5WLauncher) 0 'native preview no browser'
    Assert-Gen5WEqual ($nativeArguments -contains '--open-browser') $false 'no browser flag omitted'

    $script:pythonAvailable = $false
    $script:Plan = $true
    $script:Yes = $false
    $script:NoBrowser = $false
    $script:messages = @()
    $script:installCalls = 0
    $script:nativeCalls = 0
    Assert-Gen5WEqual (Invoke-Gen5WLauncher) 0 'missing Python plan'
    Assert-Gen5WEqual (($messages -join "`n").Contains('winget install --id Python.Python.3.13 -e --silent --scope user --accept-package-agreements --accept-source-agreements --disable-interactivity')) $true 'missing Python winget plan'
    Assert-Gen5WEqual $installCalls 0 'plan never installs'
    Assert-Gen5WEqual $nativeCalls 0 'plan never launches server'

    $script:pythonAvailable = $false
    $script:Plan = $false
    $script:Yes = $false
    $script:consentCalls = 0
    function Test-Gen5WPythonInstallConsent {
        $script:consentCalls++
        if ($script:Yes) {
            $script:messages += 'Python installation accepted by -Yes using the displayed current-user winget plan.'
        }
        return [bool]$script:Yes
    }
    $script:installCalls = 0
    $script:nativeCalls = 0
    Assert-Gen5WEqual (Invoke-Gen5WLauncher) 1 'interactive install refusal'
    Assert-Gen5WEqual $consentCalls 1 'interactive install asks'
    Assert-Gen5WEqual $installCalls 0 'interactive refusal does not install'

    $script:pythonAvailable = $false
    $script:Yes = $true
    $script:installCalls = 0
    $script:nativeCalls = 0
    $script:messages = @()
    Assert-Gen5WEqual (Invoke-Gen5WLauncher) 0 'consented Python install and preview'
    Assert-Gen5WEqual $installCalls 1 'explicit yes installs displayed plan'
    Assert-Gen5WEqual $nativeCalls 1 'preview continues after installation'
    Assert-Gen5WEqual (($messages -join "`n").Contains('Required action:') -and ($messages -join "`n").Contains('Python installation accepted by -Yes')) $true 'displayed plan precedes yes install'

    foreach ($mixedFlag in @('Assets', 'WifiSim', 'SetupHostname')) {
        $script:Preview = $true
        $script:Assets = $null
        $script:WifiSim = $false
        $script:SetupHostname = $false
        if ($mixedFlag -eq 'Assets') { $script:Assets = 'C:\private-assets' }
        elseif ($mixedFlag -eq 'WifiSim') { $script:WifiSim = $true }
        else { $script:SetupHostname = $true }
        $script:messages = @()
        $script:nativeCalls = 0
        $script:wslCalls = 0
        Assert-Gen5WEqual (Invoke-Gen5WLauncher) 1 "mixed preview $mixedFlag refusal"
        Assert-Gen5WEqual $nativeCalls 0 "mixed preview $mixedFlag native calls"
        Assert-Gen5WEqual $wslCalls 0 "mixed preview $mixedFlag WSL calls"
        Assert-Gen5WEqual ([IO.Directory]::Exists((Join-Path $previewRoot '.gen5w'))) $false "mixed preview $mixedFlag creates no state"
    }

    $script:Preview = $true
    $script:Assets = $null
    $script:WifiSim = $false
    $script:SetupHostname = $false
    $script:pythonAvailable = $true
    $script:nativeExit = 130
    Assert-Gen5WEqual (Invoke-Gen5WLauncher) 130 'preview stop propagation'
    $script:nativeExit = 0

    # Restore the full-VM fixture state and prove the dispatcher leaves that
    # existing WSL path unchanged.
    $script:Preview = $false
    $script:Plan = $true
    $script:Yes = $true
    $script:NoBrowser = $true
    $script:root = Join-Path $temporary 'checkout with spaces'
    $script:windowsHosts = Join-Path $temporary 'hosts'
    [IO.File]::WriteAllText($windowsHosts, '127.0.0.1 localhost')
    $script:wsl = Join-Path $temporary 'fixture-wsl'
    $script:captured = @()
    $script:messages = @()
    $script:browserPath = '/mnt/c/Windows/explorer.exe'
    $script:browserPathExit = 0
    $script:distributionVersion = '2'
    function Write-Gen5WSetup([string] $Message) { $script:messages += $Message }
    function Invoke-Gen5WWsl([string[]] $Arguments) {
        $script:captured += ,$Arguments
        $global:LASTEXITCODE = 0
        if ($Arguments[0] -eq '--list') { return "* Ubuntu Stopped $script:distributionVersion" }
        if ($Arguments -contains '/usr/bin/wslpath') {
            $global:LASTEXITCODE = $script:browserPathExit
            if ($Arguments[-1] -match 'assets') { return '/mnt/c/assets with spaces' }
            return $script:browserPath
        }
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
    Assert-Gen5WEqual ($messages -join "`n").Contains('browser handoff is unavailable') $false 'explicit no browser'
    $script:Assets = 'C:\assets with spaces'
    $script:captured = @()
    Assert-Gen5WEqual (Invoke-Gen5WLauncher) 0 'explicit asset directory'
    Assert-Gen5WEqual $captured.Count 3 'asset translation and handoff'
    Assert-Gen5WEqual ($captured[2] -contains '--assets') $true 'asset flag'
    Assert-Gen5WEqual ($captured[2] -contains '/mnt/c/assets with spaces') $true 'translated asset path'
    $script:Assets = '/mnt/direct assets'
    $script:captured = @()
    Assert-Gen5WEqual (Invoke-Gen5WLauncher) 0 'direct Linux asset directory'
    Assert-Gen5WEqual $captured.Count 2 'direct Linux asset list and handoff'
    Assert-Gen5WEqual ($captured[1] -contains '--assets') $true 'direct Linux asset flag'
    Assert-Gen5WEqual ($captured[1] -contains '/mnt/direct assets') $true 'direct Linux asset path'
    $script:Assets = $null
    $script:distributionVersion = '1'
    $script:captured = @()
    $script:messages = @()
    Assert-Gen5WEqual (Invoke-Gen5WLauncher) 0 'WSL1 software fallback'
    Assert-Gen5WEqual $captured.Count 2 'WSL1 list and handoff'
    Assert-Gen5WEqual ($captured[1] -contains './launchers/start.sh') $true 'WSL1 reaches setup'
    Assert-Gen5WEqual ($messages -join "`n").Contains('QEMU TCG software emulation') $true 'WSL1 emulation disclosure'
    $script:distributionVersion = '2'
    $script:NoBrowser = $false
    $script:captured = @()
    Assert-Gen5WEqual (Invoke-Gen5WLauncher) 0 'available browser plan'
    Assert-Gen5WEqual $captured.Count 3 'list, path translation and handoff'
    Assert-Gen5WEqual ($captured[2] -contains "GEN5W_WINDOWS_BROWSER=$browserPath") $true 'verified browser forwarding'
    Assert-Gen5WEqual ($captured[2] -contains '--no-browser') $false 'automatic browser enabled'
    foreach ($fixture in @(
        @{ Path = ''; ExitCode = 0; Label = 'missing wslpath output' },
        @{ Path = '/mnt/c/Windows/notepad.exe'; ExitCode = 0; Label = 'unexpected browser path' },
        @{ Path = '/mnt/c/Windows/explorer.exe'; ExitCode = 1; Label = 'wslpath failure' }
    )) {
        $script:browserPath = $fixture.Path
        $script:browserPathExit = $fixture.ExitCode
        $script:captured = @()
        $script:messages = @()
        $label = $fixture.Label
        Assert-Gen5WEqual (Invoke-Gen5WLauncher) 0 "$label keeps launcher available"
        Assert-Gen5WEqual $captured.Count 3 "$label reaches WSL handoff"
        Assert-Gen5WEqual ($captured[2] -contains '--no-browser') $true "$label manual browser"
        Assert-Gen5WEqual ($captured[2] -contains './launchers/start.sh') $true "$label starts setup"
        Assert-Gen5WEqual ($captured[2] -contains '/usr/bin/env') $false "$label drops browser override"
        Assert-Gen5WEqual ($messages -join "`n").Contains('Open the URL printed by the server') $true "$label guidance"
    }
    Assert-Gen5WEqual ([IO.Directory]::Exists((Join-Path $root '.gen5w'))) $false 'plan does not create state'
    Write-Output "GEN5W_WINDOWS_LAUNCHER_TESTS_PASS assertions=$count"
} finally {
    $env:SystemRoot = $originalSystemRoot
    if ($junctionPath -and [IO.Directory]::Exists($junctionPath)) {
        # Remove the reparse point itself without traversing into WindowsApps.
        [IO.Directory]::Delete($junctionPath, $false)
    }
    # This exact GUID-created fixture directory contains only this test's data.
    [IO.Directory]::Delete($temporary, $true)
}
