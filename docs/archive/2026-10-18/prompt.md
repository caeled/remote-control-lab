# Prompts and original clone instructions

## Original setup request (verbatim)

```text
{"repositories":[{"name":"caeled/remote-control-lab","ref":"main"}]}

## My request:
```

## Archival request (verbatim)

```text
give me the fucking .md of the article, the prompt and the transcript put on git and command to reclone
```

## Reusable preservation prompt

Save the incident article, this prompt, and the available user/assistant conversation transcript as separate Markdown files in caeled/remote-control-lab. Preserve existing files and local changes. Commit and push to incident/cloud-local-save-2026-10-18, verify the remote commit, and supply a Windows PowerShell command to clone that exact branch into a new directory under D:\iamdonebeingjobe. Verify the downloaded Markdown files against the Git commit. Do not claim local-drive verification until local checks execute successfully. Clearly state transcript omissions and do not invent missing article content.

## Original PowerShell response (historical)

This earlier response targets main and predates the archive branch. For the newly archived documents, use the branch-specific command in the final handoff instead.

Paste this entire block into PowerShell. It creates a fresh clone **inside your current `IAmDoneBeingJObe` directory**, preserves existing folders, and verifies every tracked file’s bytes against the Git commit.

```powershell
$ErrorActionPreference = 'Stop'

function Git-Checked {
    & git @args
    if ($LASTEXITCODE -ne 0) {
        throw "Git failed: $args"
    }
}

Get-Command git -ErrorAction Stop | Out-Null

$destination = Join-Path (Get-Location).Path 'remote-control-lab'
if (Test-Path -LiteralPath $destination) {
    $destination += '-' + [guid]::NewGuid().ToString('N').Substring(0, 12)
}

Git-Checked clone -c core.autocrlf=false --branch main `
    https://github.com/caeled/remote-control-lab.git $destination

Push-Location -LiteralPath $destination
try {
    Git-Checked fsck --full
    $commit = Git-Checked rev-parse HEAD
    $entries = @(Git-Checked -c core.quotePath=false ls-tree -r HEAD)
    $count = 0

    foreach ($entry in $entries) {
        if ($entry -notmatch '^100[0-7]{3} blob ([0-9a-f]+)\t(.+)$') {
            throw "Entry requires additional verification: $entry"
        }

        $expected = $Matches[1]
        $file = $Matches[2]
        if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
            throw "MISSING FILE: $file"
        }

        $actual = Git-Checked hash-object --no-filters -- $file
        if ($actual -ne $expected) {
            throw "BYTE MISMATCH: $file"
        }
        $count++
    }

    if ($count -eq 0) { throw 'No files were verified.' }

    Write-Host "`nVERIFIED: $count files match the Git commit byte-for-byte." -ForegroundColor Green
    Write-Host "Commit: $commit"
    Write-Host "Saved at: $destination"
}
finally {
    Pop-Location
}
```

Wait for the green **VERIFIED** message. This verifies the GitHub `main` copy; work never pushed to GitHub is separate. The copy is on your pocket drive only if the current directory is on that drive.

