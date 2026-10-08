"""Local Roku helper. Standard library, explicit IP, no discovery."""
import argparse,hmac,http.client,ipaddress,json,secrets,socket,threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
ROOT=Path(__file__).parent
KEYS=set("Home Back Up Down Left Right Select Play Rev Fwd InstantReplay Info VolumeDown VolumeUp VolumeMute PowerOff".split())
PRIVATE=tuple(ipaddress.ip_network(x) for x in ("10.0.0.0/8","172.16.0.0/12","192.168.0.0/16"))
def target_ip(text):
    try: value=ipaddress.IPv4Address(text)
    except (ValueError,TypeError): raise ValueError("Enter a private IPv4 address without a URL or port.")
    if not any(value in n for n in PRIVATE): raise ValueError("Only private home-network IPv4 addresses are supported.")
    return str(value)
def roku_request(ip,method,path):
    conn=http.client.HTTPConnection(target_ip(ip),8060,timeout=4)
    try:
        conn.request(method,path,body=b"" if method=="POST" else None)
        response=conn.getresponse();data=response.read(262145)
        if len(data)>262144: raise ValueError("Device response too large.")
        if response.status not in (200,202,204): raise ValueError("Roku returned HTTP %s. Check its network-control setting and command support."%response.status)
        return data
    finally: conn.close()
def device_info(data):
    if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper(): raise ValueError("Unexpected XML declaration.")
    try: root=ET.fromstring(data)
    except ET.ParseError: raise ValueError("Invalid device XML.")
    if root.tag!="device-info": raise ValueError("This address did not return Roku device-info.")
    return {k:(root.findtext(k) or "")[:120] for k in ("model-name","friendly-device-name","software-version","is-tv","supports-tv-power-control","supports-audio-volume-control")}
class Lab:
    def __init__(self,token=None): self.token=token or secrets.token_urlsafe(24);self.ip=None;self.lock=threading.Lock()
    def command(self,path,body):
        with self.lock:
            if path=="/api/demo": self.ip=None;return {"mode":"demo"}
            if path=="/api/connect":
                self.ip=None;ip=target_ip(body.get("ip"));info=device_info(roku_request(ip,"GET","/query/device-info"))
                self.ip=ip;return {"mode":"real","ip":ip,"info":info}
            if path=="/api/key":
                key=body.get("key")
                if not isinstance(key,str) or key not in KEYS: raise ValueError("Unsupported key.")
                if self.ip is None: return {"mode":"demo","key":key}
                roku_request(self.ip,"POST","/keypress/"+key);return {"mode":"real","key":key}
            raise ValueError("Unknown action.")
class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup();self.connection.settimeout(8)
    def log_message(self,*args): pass
    def host_ok(self):
        host=self.headers.get("Host","")
        if not host or any(c in host for c in "/\\@"): return False
        try:
            parsed=urlsplit("http://"+host)
            return parsed.hostname in self.server.allowed_hosts and parsed.port==self.server.server_port
        except ValueError: return False
    def reply(self,status,data,kind="application/json"):
        raw=json.dumps(data).encode() if kind=="application/json" else data
        self.send_response(status);self.send_header("Content-Type",kind);self.send_header("Content-Length",str(len(raw)))
        self.send_header("Cache-Control","no-store");self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("Content-Security-Policy","default-src 'self'; connect-src 'self'; style-src 'self'; script-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        self.end_headers();self.wfile.write(raw)
    def do_GET(self):
        if not self.host_ok(): return self.reply(403,{"error":"Unrecognized host."})
        files={"/":("index.html","text/html; charset=utf-8"),"/index.html":("index.html","text/html; charset=utf-8"),"/app.js":("app.js","text/javascript; charset=utf-8"),"/style.css":("style.css","text/css; charset=utf-8")}
        if self.path not in files: return self.reply(404,{"error":"Not found."})
        name,kind=files[self.path];self.reply(200,(ROOT/name).read_bytes(),kind)
    def do_POST(self):
        if not self.host_ok(): return self.reply(403,{"error":"Unrecognized host."})
        origin=self.headers.get("Origin")
        if origin and origin!="http://"+self.headers.get("Host"): return self.reply(403,{"error":"Use the helper's own page."})
        if not hmac.compare_digest(self.headers.get("X-Lab-Key","").encode(),self.server.lab.token.encode()): return self.reply(403,{"error":"Enter the session key shown in the helper window."})
        if self.headers.get("Content-Type","").split(";")[0]!="application/json": return self.reply(415,{"error":"JSON required."})
        try:
            length=int(self.headers.get("Content-Length","0"))
            if not 0<length<=2048: raise ValueError("Invalid request size.")
            body=json.loads(self.rfile.read(length))
            if not isinstance(body,dict): raise ValueError("Expected an object.")
            self.reply(200,self.server.lab.command(self.path,body))
        except (ValueError,TypeError) as e: self.reply(400,{"error":str(e)})
        except (OSError,http.client.HTTPException): self.reply(502,{"error":"No usable Roku response. Check IP, power, same LAN, client isolation, and network-control setting."})
def make_server(host="127.0.0.1",port=8070,token=None):
    server=ThreadingHTTPServer((host,port),Handler);server.daemon_threads=True;server.lab=Lab(token)
    hosts={"127.0.0.1","localhost"}
    if host=="0.0.0.0":
        hosts.update(ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if any(ipaddress.ip_address(ip) in n for n in PRIVATE))
    else: hosts.add(host)
    server.allowed_hosts=hosts;return server
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--phone",action="store_true");parser.add_argument("--port",type=int,default=8070)
    args=parser.parse_args();server=make_server("0.0.0.0" if args.phone else "127.0.0.1",args.port)
    print("Remote Control Lab - starts in DEMO. No device contacted until Connect.")
    for host in sorted(server.allowed_hosts): print("Open: http://%s:%s/"%(host,server.server_port))
    print("Session key:",server.lab.token)
    print("Keep this window open. Enter the key in the page. Ctrl+C stops the helper.")
    if args.phone: print("PHONE MODE: trusted private LAN only. HTTP is unencrypted. Do not forward this port to the Internet.")
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
