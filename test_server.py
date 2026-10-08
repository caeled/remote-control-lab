import unittest,json,http.client,threading
from unittest.mock import patch
import server
XML=b'<device-info><model-name>Demo Roku</model-name><software-version>15</software-version></device-info>'
class LabTests(unittest.TestCase):
    def test_private_only(self):
        for x in ('192.168.1.2','10.0.0.5','172.16.0.1'):self.assertEqual(server.target_ip(x),x)
        for x in ('127.0.0.1','169.254.1.1','8.8.8.8','http://192.168.1.2','192.168.1.2:80','localhost','::1','01.2.3.4',None):
            with self.assertRaises(ValueError):server.target_ip(x)
    def test_xml(self):
        self.assertEqual(server.device_info(XML)['model-name'],'Demo Roku')
        for x in (b'<bad/>',b'<!DOCTYPE device-info><device-info/>',b'<!ENTITY evil SYSTEM "file:///x">',b'bad'):
            with self.assertRaises(ValueError):server.device_info(x)
    def test_demo(self):
        with patch('server.roku_request') as transport:
            self.assertEqual(server.Lab('test').command('/api/key',{'key':'Home'})['mode'],'demo');transport.assert_not_called()
    def test_real_commands(self):
        lab=server.Lab('test')
        with patch('server.roku_request',return_value=XML) as transport:
            self.assertEqual(lab.command('/api/connect',{'ip':'192.168.1.8'})['mode'],'real')
            transport.assert_called_with('192.168.1.8','GET','/query/device-info')
            lab.command('/api/key',{'key':'Right'});transport.assert_called_with('192.168.1.8','POST','/keypress/Right')
            with self.assertRaises(ValueError):lab.command('/api/key',{'key':'../query/apps'})
            lab.command('/api/demo',{});self.assertIsNone(lab.ip)
    def test_failed_connect(self):
        lab=server.Lab('test');lab.ip='192.168.1.8'
        with self.assertRaises(ValueError):lab.command('/api/connect',{'ip':'8.8.8.8'})
        self.assertIsNone(lab.ip)
    def test_no_redirects(self):
        with patch('server.http.client.HTTPConnection') as cls:
            conn=cls.return_value;response=conn.getresponse.return_value;response.status=302;response.read.return_value=b''
            with self.assertRaises(ValueError):server.roku_request('192.168.1.8','GET','/query/device-info')
            cls.assert_called_once_with('192.168.1.8',8060,timeout=4);conn.close.assert_called_once()
class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.web=server.make_server(port=0,token='test-fixture-key');cls.thread=threading.Thread(target=cls.web.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.web.shutdown();cls.web.server_close();cls.thread.join()
    def request(self,path,body,key='test-fixture-key',origin=None,host=None):
        headers={'Content-Type':'application/json','X-Lab-Key':key}
        if origin:headers['Origin']=origin
        if host:headers['Host']=host
        c=http.client.HTTPConnection('127.0.0.1',self.web.server_port,timeout=3)
        try:c.request('POST',path,json.dumps(body),headers);r=c.getresponse();return r.status,json.loads(r.read())
        finally:c.close()
    def test_auth_origin_host(self):
        self.assertEqual(self.request('/api/demo',{},key='bad')[0],403)
        self.assertEqual(self.request('/api/demo',{},origin='https://evil.example')[0],403)
        self.assertEqual(self.request('/api/demo',{},host='evil.example:%s'%self.web.server_port)[0],403)
        self.assertEqual(self.request('/api/demo',{})[0],200)
    def test_demo_over_http(self):self.assertEqual(self.request('/api/key',{'key':'Home'})[1]['mode'],'demo')
    def test_injection_blocked(self):self.assertEqual(self.request('/api/key',{'key':'../query/apps'})[0],400)
if __name__=='__main__':unittest.main()
