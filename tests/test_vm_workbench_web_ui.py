"""Run the actual WEB_UI script in a deterministic host-only DOM fixture."""

import shutil
import subprocess
import unittest
from pathlib import Path


PAGE = Path(__file__).resolve().parents[1] / "tools" / "uk_fw" / "vm_workbench" / "WEB_UI.html"

# A small DOM and fake fetch exercise the shipped script, not a reimplementation
# of the coordinate or keyboard logic. Timers are suppressed deterministically.
NODE_TEST = r'''
const fs = require('fs');
const vm = require('vm');
const html = fs.readFileSync(process.argv[1], 'utf8');
const script = html.match(/<script>([\s\S]*)<\/script>/)[1].replace('__WORKBENCH_WIFI_SIM__', 'false');
class Element {
  constructor(id='') { this.id=id; this.handlers={}; this.children=[]; this.value=''; this.textContent=''; this.className=''; }
  addEventListener(name, fn) { this.handlers[name]=fn; }
  dispatch(name, fields={}) { if (this.handlers[name]) this.handlers[name]({preventDefault(){}, ...fields}); }
  append(...children) { this.children.push(...children); }
  replaceChildren() { this.children=[]; }
  setPointerCapture() {} focus() {}
  getBoundingClientRect() { return {left:100, top:50, width:960, height:360}; }
}
const names=['screen','frameSource','frameInfo','session','message','modules','events','filter','shutdown','confirmOnce',
  'startupProgress','startupPercent','startupMessage','startupDetail'];
const elements=Object.fromEntries(names.map(id => [id,new Element(id)]));
const document={getElementById:id=>elements[id],createElement:tag=>new Element(tag)};
const posts=[];
let observed=null, configured=5, acknowledged=4, moduleGets=0, failObserve=false, hmiObserved=false;
const headers = new Map([['X-Frame-Sequence','7'],['X-Frame-Captured-Ns',String(Date.now()*1000000)],
  ['X-Frame-Width','1920'],['X-Frame-Height','720'],['X-Frame-Source','host-fixture'],['X-Frame-Stale','false']]);
async function fetch(path, options) {
  if (options.method === 'POST') {
    const body=JSON.parse(options.body); posts.push([path, body]);
    if (path.endsWith('/hmi/observe')) { hmiObserved=true; }
    if (path.endsWith('/micom/observe')) {
      if (failObserve) return {ok:false,status:503,json:async()=>({error:{message:'fixture observation failed'}})};
      observed=9;
    }
    if (path.endsWith('/micom/debug_count')) { configured=body.value; acknowledged=body.value; }
    return {ok:true,json:async()=>({state:'completed',message:'fixture',command_id:'id'})};
  }
  if (path.endsWith('/frame')) return {ok:true,headers,blob:async()=>({})};
  if (path.endsWith('/modules')) { moduleGets++; return {ok:true,json:async()=>({modules:[
    {label:'MICOM',module_id:'micom',observe_label:'Observe guest D-Bus',integration:'host-fixture',transport:'fake',fields:[
      {name:'debug_count',value:acknowledged,value_type:'integer',writable:true,evidence:'guest-mailbox-acknowledged'},
      {name:'debug_count_configured',value:configured,value_type:'integer',writable:false,evidence:'operator-requested'},
      {name:'parking_status',value:null,value_type:'boolean',writable:true,evidence:'simulator receipt'},
      {name:'debug_count_dbus_observed',value:observed,value_type:'integer',writable:false,evidence:'guest-system-bus AskDebuggingMode reply byte0'}]},
    {label:'HMI',module_id:'hmi',observe_label:'Observe Confirm state',diagnose_label:'Diagnose Confirm observation',integration:'host-fixture',transport:'fake',fields:
      ['buttonRoot','enabled','visible','driving','calling'].map((name,i)=>({name,value:hmiObserved ? [[479,629,690,63],true,true,false,false][i] : null,value_type:'string',writable:false,evidence:'last QML log record'}))},
    {label:'Other',module_id:'other',integration:'host-fixture',transport:'fake',fields:[]}
  ]})}; }
  if (path.endsWith('/status')) return {ok:true,json:async()=>({state:'fixture'})};
  return {ok:true,json:async()=>({events:[{event_id:1,correlation_id:'id',event:'ack'}]})};
}
let frameTimer=null;
const sandbox={document,fetch,URL:{createObjectURL:()=> 'blob:fixture',revokeObjectURL(){}},
  setTimeout(fn,ms){if(ms===800 || ms===400) frameTimer=fn;},setInterval(){}, Date, Promise, JSON, Number, Math, String, Array, Object};
vm.runInNewContext(script, sandbox);
const flush=()=>new Promise(resolve=>setImmediate(resolve));
(async()=>{
  await flush(); await flush();
  await frameTimer(); await flush();
  if (!elements.frameSource.textContent.includes('host-fixture')) throw Error('fixture provenance missing');
  if (!elements.frameInfo.textContent.includes('1920 × 720')) throw Error('frame metadata missing');
  elements.screen.onload();
  if (!elements.confirmOnce.disabled) throw Error('fixture frame allowed as approval');
  elements.confirmOnce.dispatch('click'); await flush();
  if (posts.length) throw Error('fixture frame sent a Confirm action');
  headers.set('X-Frame-Source','guest-compositor');
  await frameTimer(); await flush();
  if (!elements.confirmOnce.disabled) throw Error('unloaded frame allowed as approval');
  elements.screen.onload();
  if (elements.confirmOnce.disabled) throw Error('loaded live frame not available for approval');
  elements.confirmOnce.dispatch('click'); await flush(); await flush();
  if (!elements.events.textContent.includes('ack')) throw Error('event log missing');
  if (!elements.modules.children.length) throw Error('module controls missing');
  const allText = node => [node.textContent, ...node.children.flatMap(child => allText(child))];
  let rendered = allText(elements.modules).join('|');
  for (const value of ['Configured: 5', 'Mailbox-acknowledged: 4', 'Last successful guest D-Bus observation: not yet available', 'operator-requested', 'guest-mailbox-acknowledged', 'guest-system-bus']) {
    if (!rendered.includes(value)) throw Error('missing separate value/evidence '+value);
  }
  if (!rendered.includes('IHU parking status (simulated): not yet available')) throw Error('unknown parking status mislabeled');
  const parking=elements.modules.children[0].children.find(child=>child.children[0]?.textContent==='IHU parking status (simulated)');
  parking.children[1].checked=true; parking.children[2].dispatch('click');
  await flush(); await flush();
  const micom=elements.modules.children[0], other=elements.modules.children[2];
  const observe=micom.children.find(child=>child.textContent==='Observe guest D-Bus');
  if (!observe || other.children.some(child=>child.textContent==='Observe guest D-Bus')) throw Error('observe action scope incorrect');
  elements.modules.children[1].children.find(child=>child.textContent==='Observe Confirm state').dispatch('click');
  await flush(); await flush();
  rendered=allText(elements.modules).join('|');
  for (const value of ['buttonRoot: [479,629,690,63]','enabled: true','visible: true','driving: false','calling: false']) {
    if (!rendered.includes(value)) throw Error('missing HMI observation '+value);
  }
  elements.modules.children[1].children.find(child=>child.textContent==='Diagnose Confirm observation').dispatch('click');
  await flush(); await flush();
  observe.dispatch('click');
  await flush(); await flush();
  rendered = allText(elements.modules).join('|');
  if (moduleGets < 2 || !rendered.includes('Last successful guest D-Bus observation: 9')) throw Error('last observation refresh missing');
  const field=elements.modules.children[0].children.find(child=>child.className==='field');
  field.children[1].value='12'; field.children[2].dispatch('click');
  await flush(); await flush();
  rendered=allText(elements.modules).join('|');
  for (const value of ['Configured: 12', 'Mailbox-acknowledged: 12', 'Last successful guest D-Bus observation: 9']) {
    if (!rendered.includes(value)) throw Error('configuration change misrepresented observation: '+value);
  }
  failObserve=true;
  elements.modules.children[0].children.find(child=>child.textContent==='Observe guest D-Bus').dispatch('click');
  await flush(); await flush();
  rendered=allText(elements.modules).join('|');
  if (!rendered.includes('Last successful guest D-Bus observation: 9')) throw Error('failed observation did not preserve last-successful label and value');
  if (!elements.message.textContent.includes('fixture observation failed')) throw Error('failed observation not reported');
  const screen=elements.screen;
  screen.dispatch('pointerdown',{button:0,pointerId:1,clientX:580,clientY:230});
  screen.dispatch('pointerup',{clientX:580,clientY:230});
  screen.dispatch('pointerdown',{button:0,pointerId:2,clientX:100,clientY:50});
  screen.dispatch('pointerup',{clientX:1060,clientY:410});
  screen.dispatch('keydown',{code:'KeyA',repeat:false});
  screen.dispatch('keydown',{code:'KeyA',repeat:true});
  screen.dispatch('keyup',{code:'KeyA'});
  screen.dispatch('keydown',{code:'Shell',repeat:false});
  let blocked = false;
  screen.dispatch('keydown',{code:'Home',repeat:false,preventDefault(){blocked=true;}});
  if (blocked) throw Error('unmapped browser key intercepted');
  await flush(); await flush();
  const expected=[
    ['/api/v1/input/confirm-once',{frame_sequence:7}],
    ['/api/v1/modules/micom/parking_status',{value:true}],
    ['/api/v1/modules/hmi/observe',{}],
    ['/api/v1/modules/hmi/diagnose',{}],
    ['/api/v1/modules/micom/observe',{}],
    ['/api/v1/modules/micom/debug_count',{value:12}],
    ['/api/v1/modules/micom/observe',{}],
    ['/api/v1/input/pointer',{action:'click',x1:960,y1:360}],
    ['/api/v1/input/pointer',{action:'drag',x1:0,y1:0,x2:1919,y2:719}],
    ['/api/v1/input/key',{action:'tap',key:'KeyA'}]
  ];
  if (JSON.stringify(posts)!==JSON.stringify(expected)) throw Error('incorrect inputs '+JSON.stringify(posts));
  console.log('fixture DOM interaction passed');
})().catch(error=>{console.error(error);process.exitCode=1});
'''

NODE_SIMULATION_TEST = r'''
const fs = require('fs');
const vm = require('vm');
const html = fs.readFileSync(process.argv[1], 'utf8');
const script = html.match(/<script>([\s\S]*)<\/script>/)[1].replace('__WORKBENCH_WIFI_SIM__', 'true');
class Element {
  constructor(id='') { this.id=id; this.handlers={}; this.children=[]; this.value=''; this.textContent=''; }
  addEventListener(name, fn) { this.handlers[name]=fn; }
  dispatch(name, fields={}) { return this.handlers[name]?.({preventDefault(){}, ...fields}); }
  append(...children) { this.children.push(...children); }
  replaceChildren() { this.children=[]; }
  setPointerCapture() {} focus() {}
  getBoundingClientRect() { return {left:100, top:50, width:960, height:360}; }
}
const names=['screen','frameSource','frameInfo','session','message','modules','events','filter','shutdown','confirmOnce',
  'startupProgress','startupPercent','startupMessage','startupDetail'];
const elements=Object.fromEntries(names.map(id => [id,new Element(id)]));
const document={getElementById:id=>elements[id],createElement:tag=>new Element(tag)};
const headers = new Map([['X-Frame-Sequence','7'],['X-Frame-Captured-Ns',String(Date.now()*1000000)],
  ['X-Frame-Width','1920'],['X-Frame-Height','720'],['X-Frame-Source','guest-compositor'],['X-Frame-Stale','false']]);
let frameGets=0, pointerResolve=null, frameTimer=null, holdTimer=null;
async function fetch(path, options={}) {
  if (options.method === 'POST') {
    if (!path.endsWith('/input/pointer')) return {ok:true,json:async()=>({state:'completed',message:'fixture',command_id:'other'})};
    return new Promise(resolve => { pointerResolve=()=>resolve({ok:true,json:async()=>({state:'completed',message:'fixture',command_id:'pointer'})}); });
  }
  if (path.endsWith('/frame')) { frameGets++; return {ok:true,headers,blob:async()=>({})}; }
  if (path.endsWith('/modules')) return {ok:true,json:async()=>({modules:[]})};
  if (path.endsWith('/status')) return {ok:true,json:async()=>({state:'fixture'})};
  return {ok:true,json:async()=>({events:[]})};
}
const sandbox={document,fetch,URL:{createObjectURL:()=> 'blob:'+frameGets,revokeObjectURL(){}},
  setTimeout(fn,ms){if(ms===800 || ms===400) frameTimer=fn; if(ms===100) holdTimer=fn;},setInterval(){},
  Date,Promise,JSON,Number,Math,String,Array,Object,encodeURIComponent};
vm.runInNewContext(script, sandbox);
const flush=()=>new Promise(resolve=>setImmediate(resolve));
(async()=>{
  await flush(); await flush();
  await frameTimer(); await flush();
  elements.screen.onload();
  elements.screen.dispatch('pointerdown',{button:0,pointerId:1,clientX:275,clientY:268});
  elements.screen.dispatch('pointerup',{clientX:275,clientY:268});
  await flush();
  if (!pointerResolve) throw Error('simulated pointer was not posted');
  const before=frameGets;
  await frameTimer(); await flush();
  if (frameGets!==before || !holdTimer) throw Error('pending input did not hold frame polling');
  pointerResolve(); await flush(); await flush();
  await holdTimer(); await flush();
  if (frameGets!==before+1) throw Error('frame polling did not resume after receipt');
  elements.screen.onload();
  elements.screen.dispatch('pointerdown',{button:0,pointerId:2,clientX:275,clientY:268});
  elements.screen.dispatch('pointercancel');
  await frameTimer(); await flush();
  if (frameGets!==before+2) throw Error('pointer cancellation did not release frame polling');
  console.log('simulation frame hold passed');
})().catch(error=>{console.error(error);process.exitCode=1});
'''


class WorkbenchUITests(unittest.TestCase):
    def test_frame_provenance_mouse_keyboard_and_logs(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node is required to execute the browser script fixture")
        result = subprocess.run([node, "-e", NODE_TEST, str(PAGE)], text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("fixture DOM interaction passed", result.stdout)

    def test_simulation_input_holds_and_releases_frame_polling(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node is required to execute the browser script fixture")
        result = subprocess.run([node, "-e", NODE_SIMULATION_TEST, str(PAGE)], text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("simulation frame hold passed", result.stdout)


if __name__ == "__main__":
    unittest.main()
