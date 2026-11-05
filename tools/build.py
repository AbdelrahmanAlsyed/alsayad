# Usage: python3 tools/build.py <artifact index.html> <repo root>
# Turns the Claude artifact of «الصياد» into the installable web app (PWA) served on Vercel.
import json,sys,os
src,out=sys.argv[1],sys.argv[2]
s=open(src).read()
d=out.rstrip('/')+'/'
head='''<link rel="manifest" href="/manifest.webmanifest">
<meta name="theme-color" content="#0b2e4f">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="192x192" href="/icon-192.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="الصياد">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="description" content="الصياد — فيديوهات وملازم ومواعيد حصص الرياضيات">'''
assert s.find('</head>')<1000
s=s.replace('<html>','<html lang="ar" dir="rtl">',1).replace('</head>',head+'</head>',1)
old="""    const dl = await window.claude?.use?.('downloads');
    if(!dl){ regMsg='التنزيل غير متاح من هذا العرض؛ استخدم «نسخ الكشف» والصقه في Excel.'; return render(); }"""
new="""    let dl = null; try{ dl = await window.claude?.use?.('downloads'); }catch(e){}
    if(!dl){ dl={save:async({filename,data})=>{ const u=URL.createObjectURL(data); const a=document.createElement('a'); a.href=u; a.download=filename; document.body.appendChild(a); a.click(); a.remove(); setTimeout(()=>URL.revokeObjectURL(u),4000); }}; }"""
assert s.count(old)==1; s=s.replace(old,new)
sw="<script>if('serviceWorker' in navigator&&!window.claude){addEventListener('load',()=>navigator.serviceWorker.register('/sw.js').catch(()=>{}));}</script>"
s=s.rstrip(); assert s.endswith('</body></html>')
s=s[:-len('</body></html>')]+sw+'</body></html>'
open(d+'index.html','w').write(s)
open(d+'manifest.webmanifest','w').write(json.dumps({"name":"الصياد","short_name":"الصياد","description":"فيديوهات وملازم ومواعيد حصص الرياضيات","lang":"ar","dir":"rtl","start_url":"/","scope":"/","display":"standalone","background_color":"#f2f7fb","theme_color":"#0b2e4f","icons":[{"src":"/icon-192.png","sizes":"192x192","type":"image/png","purpose":"any maskable"},{"src":"/icon-512.png","sizes":"512x512","type":"image/png","purpose":"any maskable"}]},ensure_ascii=False,indent=1))
open(d+'sw.js','w').write("""const C='alsayad-v1';
const SHELL=['/','/manifest.webmanifest','/icon-192.png','/icon-512.png','/apple-touch-icon.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(SHELL)));self.skipWaiting();});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x)))).then(()=>self.clients.claim()));});
self.addEventListener('fetch',e=>{const r=e.request; if(r.method!=='GET')return; const u=new URL(r.url);
 if(r.mode==='navigate'){e.respondWith(fetch(r).then(res=>{const cp=res.clone();caches.open(C).then(c=>c.put('/',cp));return res;}).catch(()=>caches.match('/')));return;}
 if(u.origin===location.origin||u.hostname.endsWith('gstatic.com')||u.hostname.endsWith('googleapis.com')||u.hostname==='cdnjs.cloudflare.com'){
  e.respondWith(caches.match(r).then(hit=>{const net=fetch(r).then(res=>{if(res.ok||res.type==='opaque'){const cp=res.clone();caches.open(C).then(c=>c.put(r,cp));}return res;}).catch(()=>hit);return hit||net;}));}
});
""")
open(d+'vercel.json','w').write(json.dumps({"headers":[{"source":"/sw.js","headers":[{"key":"Cache-Control","value":"no-cache"}]},{"source":"/","headers":[{"key":"Cache-Control","value":"no-cache"}]}]},indent=1))
print('ok')
