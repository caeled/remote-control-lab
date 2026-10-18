# Bug report: cloud setup did not provide a reliable local-save verification handoff

Date: 2026-10-18 (America/New_York)
Affected workflow: Codex cloud onboarding followed by a request to clone and verify the same repository on Windows and preserve a portable copy.
Repository: caeled/remote-control-lab
Initial cloud commit: 4b879a4f739b84fafb6098b8591c955e174787cf

## Summary and impact

The user requested a working environment, then repeatedly requested a verified local copy of their own work. Cloud setup succeeded, but the assistant could neither execute commands on the Windows computer nor verify its files. The interaction required repeated user intervention and manual PowerShell commands. The user reported substantial frustration and loss of confidence that their work was safely preserved.

This report records observed workflow and assistant failures. It does not establish intentional obstruction, data loss, or a confirmed underlying product defect.

## Observed sequence

1. Cloud onboarding inspected the existing checkout, ran all nine Python tests successfully, and verified static assets and demo API behavior. No dependency installation was necessary.
2. Startup instructions were saved in an environment configuration draft. The save response said publication was still required. No publication was verified.
3. The user requested an immediate local re-clone and said another agent/model had been assigned to it. The assistant initially checked only this thread's terminal and artifacts; neither provided local verification.
4. After further requests, broader tool discovery found Windows project metadata and thread summaries. That discovery should have happened earlier. It still did not expose a callable local execution tool or evidence of a completed clone.
5. The assistant provided PowerShell commands to clone into a new directory and verify tracked file bytes against Git object hashes. The user supplied screenshots showing a Windows directory initially empty, then a remote-control-lab subdirectory present.
6. The user also showed execution-policy changes while trying to complete the workflow. Git cloning and interactively pasted commands did not require this change. The assistant subsequently clarified that point.
7. The assistant provided a verification-only block for the existing copy. No output showing its final VERIFIED message has been received in this conversation.
8. The user explicitly requested submission of a bug report and an archival copy in the existing Git repository, with no further clone.

## Expected behavior

- Distinguish a saved configuration draft, publication, cloud files, a local clone, and a verified portable backup in clear language.
- Discover available local execution and cross-thread evidence promptly before declaring what cannot be verified.
- If local execution is unavailable, provide one concise handoff that preserves existing work, reports exact destination and commit, and checks file contents.
- Verify the existing copy once it exists; avoid unnecessary additional clones.
- Never describe a directory listing as proof of a complete or byte-identical clone.
- Make the cloud-to-local capability boundary clear in the product and offer an accessible export or local execution handoff.

## Evidence and limits

- Current thread terminal tool reported no attached app terminal session; attached-artifact listing was empty.
- Project discovery returned local Windows project metadata, but metadata did not grant filesystem access.
- Screenshots show a remote-control-lab directory under the user's chosen local destination. They do not show completed hash verification or establish that the destination is removable media.
- The cloud checkout and its nine tests were verified. The Windows copy's contents, remote freshness, unpushed changes elsewhere, and portable-drive persistence remain unverified.
- This archive intentionally omits unrelated screenshot contents, personal account information, credentials, and emotional conversation details.

## Requested follow-up

Please triage the cloud-to-local save and verification experience, investigate whether local execution/handoff capabilities were missing or insufficiently discoverable, and provide an explanation and written corrective-action plan. The user requested a meeting with a responsible support or product representative; no meeting or response is promised by this report.

## Submission status

Archived in the existing cloud Git checkout at the user's request. A GitHub API access check returned Forbidden, so no issue was submitted. No email-sending tool is available. An attempted push to a separate incident branch was rejected by automatic approval review because repository ownership/privacy and authorization for conversation-derived remote disclosure were not verified. No remote delivery or publication is confirmed. Saving this report in Git is archival preservation, not proof that OpenAI support received it.
