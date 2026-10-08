# Remote Control Lab

Roku-first local remote and teaching bench. Phone-friendly directional/media controls, supported-device volume/power-off, and a visible message log. A fictional demo works by opening index.html directly. Real control uses a local Python helper and manual device IP entry. No framework, pip packages, cloud services, telemetry, discovery scans, or saved credentials.

## Start

1. Download and extract [remote-control-lab.zip](https://github.com/caeled/remote-control-lab/raw/refs/heads/main/remote-control-lab.zip).
2. With Python 3.9+ already installed, run **Start-PC.cmd** (Windows), or **python3 server.py** (macOS/Linux).
3. Open **http://127.0.0.1:8070/**. Enter the session key printed in the helper window. It changes on every restart.
4. Find your Roku address under Settings → Network → About and Connect.
5. Check the REAL/DEMO badge before pressing buttons. Ctrl+C stops the helper.

For a phone, run **Start-Phone.cmd** or **python3 server.py --phone**. Open a PC LAN address printed by the helper, from the same trusted private network. Keep the PC awake. A firewall, VPN, or client isolation can block access; this app changes none of those settings. Do not disable your firewall or forward port 8070 to the Internet.

## Device support

Basic control uses Roku ECP. Inspect Settings → System → Advanced system settings → Control by mobile apps → Network access. Current firmware may require Enabled. Choose whether to permit control on your trusted network. Developer mode is not required for these basic commands. Volume/power support varies; power-on is not implemented.

Discovery, text entry, app launching, LG, and Samsung adapters are future extensions, not features of this initial version. They need device-specific protocol and pairing tests. No universal-remote compatibility is implied.

## Local helper

The helper accepts literal RFC1918 IPv4 destinations on fixed port 8060, only device-info and a fixed key whitelist, four-second device timeouts, bounded request/response sizes, no redirects or proxies, and a random session key for API requests. Host/Origin checks reject unrelated web pages. The key remains only in page memory. Phone mode uses unencrypted HTTP; anyone with the key and LAN access can control the selected device. Use a trusted private LAN and stop the helper when finished. It is not an Internet-facing production server.

Opening index.html by itself gives the no-network demo. Use the page served by the helper for real control. GET asks for information, POST requests an action, IP chooses a destination, and port/path choose a service and operation. The lesson explains pairing, WebSockets, automation, and model differences.

## Verification

Run **python -m unittest -v test_server.py**. Tests use fictional device XML and a mocked Roku transport, contacting no real TV. Live Roku behavior still needs testing on your device. The app displays only name/model/version from device information; it does not display or log serial numbers, MAC addresses, or profiles.

MIT code; CC BY 4.0 original lessons. Sources in SOURCES.md. The original discussion is in **Build A Game**, under **Remote Control Lab**.
