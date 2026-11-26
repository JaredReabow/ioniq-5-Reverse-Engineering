"""Exercise the shipped Workbench browser lane in deterministic host-only DOM fixtures."""

import shutil
import subprocess
import unittest
from pathlib import Path


PAGE = Path(__file__).resolve().parents[1] / "tools" / "uk_fw" / "vm_workbench" / "WEB_UI.html"


NODE_TEST = r'''
const fs = require('fs');
const vm = require('vm');
const html = fs.readFileSync(process.argv[1], 'utf8');
const script = html.match(/<script>([\s\S]*)<\/script>/)[1].replace('__WORKBENCH_WIFI_SIM__', 'false');
class Element {
  constructor(id='') {
    this.id=id; this.handlers={}; this.children=[]; this.value=''; this.textContent='';
    this.className=''; this.hidden=false; this.attributes={}; this.disabled=false;
  }
  addEventListener(name, fn) { this.handlers[name]=fn; }
  dispatch(name, fields={}) { return this.handlers[name]?.({preventDefault(){}, ...fields}); }
  append(...children) { this.children.push(...children); }
  replaceChildren() { this.children=[]; }
  setPointerCapture() {} focus() {}
  setAttribute(name, value) { this.attributes[name]=String(value); }
  getBoundingClientRect() { return {left:100, top:50, width:960, height:360}; }
}
const names=['screen','frameSource','frameInfo','session','message','modules','events','filter','shutdown','confirmOnce',
  'startupProgress','startupPercent','startupMessage','startupDetail','shell','leftPanel','rightPanel','toggleLeft',
  'toggleRight','syntheticBanner','scopeLabel'];
const elements=Object.fromEntries(names.map(id => [id,new Element(id)]));
const document={getElementById:id=>elements[id],createElement:tag=>new Element(tag)};
const stored=new Map();
const localStorage={getItem:key=>stored.get(key) ?? null,setItem:(key,value)=>stored.set(key,String(value))};
const location={origin:'http://127.0.0.1:8765'};
const posts=[];
let observed=null, configured=5, acknowledged=4, moduleGets=0, failObserve=false, hmiObserved=false;
const headers=new Map([['X-Frame-Sequence','7'],['X-Frame-Captured-Ns',String(Date.now()*1000000)],
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
  if (path.endsWith('/status')) return {ok:true,json:async()=>({
    state:'fixture',service_state:'ready',scope:'host-fixture',progress:100,stage:'ready',snapshot:true,guest_network:false
  })};
  return {ok:true,json:async()=>({events:[{event_id:1,correlation_id:'id',event:'ack'}]})};
}
let frameTimer=null;
const sandbox={document,fetch,localStorage,location,URL:{createObjectURL:()=> 'blob:fixture',revokeObjectURL(){}},
  setTimeout(fn,ms){if(ms===800 || ms===400) frameTimer=fn;},setInterval(){},Date,Promise,JSON,Number,Math,String,Array,Object};
vm.runInNewContext(script, sandbox);
const flush=()=>new Promise(resolve=>setImmediate(resolve));
(async()=>{
  await flush(); await flush();
  await frameTimer(); await flush();
  if (!elements.frameSource.textContent.includes('host-fixture')) throw Error('fixture provenance missing');
  if (!elements.frameInfo.textContent.includes('1920 × 720')) throw Error('frame metadata missing');
  elements.screen.onload();
  if (elements.syntheticBanner.hidden) throw Error('host fixture was not visibly labelled synthetic');
  if (!elements.scopeLabel.textContent.includes('synthetic preview')) throw Error('scope label omitted preview status');
  if (!elements.leftPanel || !elements.rightPanel || elements.shell.hidden) throw Error('layout panels missing');
  if (elements.leftPanel.hidden || elements.rightPanel.hidden) throw Error('default panel recovery failed');
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
  if (parking.children[1].disabled || parking.children[2].disabled) throw Error('host fixture input was disabled');
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
  screen.dispatch('pointerdown',{button:0,pointerId:1,isPrimary:true,clientX:580,clientY:230});
  screen.dispatch('pointerup',{pointerId:1,isPrimary:true,clientX:580,clientY:230});
  screen.dispatch('pointerdown',{button:0,pointerId:2,isPrimary:true,clientX:100,clientY:50});
  screen.dispatch('pointerup',{pointerId:2,isPrimary:true,clientX:1060,clientY:410});
  screen.dispatch('keydown',{code:'KeyA',repeat:false});
  screen.dispatch('keydown',{code:'KeyA',repeat:true});
  screen.dispatch('keyup',{code:'KeyA'});
  screen.dispatch('keydown',{code:'Escape',repeat:false});
  screen.dispatch('keydown',{code:'Shell',repeat:false});
  let blocked = false;
  screen.dispatch('keydown',{code:'Home',repeat:false,preventDefault(){blocked=true;}});
  if (blocked) throw Error('unmapped browser key intercepted');
  blocked=false;
  screen.dispatch('keydown',{code:'Tab',repeat:false,preventDefault(){blocked=true;}});
  if (blocked) throw Error('Tab did not retain normal browser focus movement');
  await flush(); await flush();
  const expected=[
    ['/api/v1/input/confirm-once',{frame_sequence:7}],
    ['/api/v1/modules/micom/parking_status',{value:true}],
    ['/api/v1/modules/hmi/observe',{}],
    ['/api/v1/modules/hmi/diagnose',{}],
    ['/api/v1/modules/micom/observe',{}],
    ['/api/v1/modules/micom/debug_count',{value:12}],
    ['/api/v1/modules/micom/observe',{}],
    ['/api/v1/input/pointer',{action:'click',x1:960,y1:360,frame_sequence:7}],
    ['/api/v1/input/pointer',{action:'drag',x1:0,y1:0,x2:1919,y2:719,frame_sequence:7}],
    ['/api/v1/input/key',{action:'tap',key:'KeyA'}],
    ['/api/v1/input/key',{action:'tap',key:'Escape'}]
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
  constructor(id='') {
    this.id=id; this.handlers={}; this.children=[]; this.value=''; this.textContent='';
    this.className=''; this.hidden=false; this.attributes={};
  }
  addEventListener(name, fn) { this.handlers[name]=fn; }
  dispatch(name, fields={}) { return this.handlers[name]?.({preventDefault(){}, ...fields}); }
  append(...children) { this.children.push(...children); }
  replaceChildren() { this.children=[]; }
  setPointerCapture() {} focus() {}
  setAttribute(name, value) { this.attributes[name]=String(value); }
  getBoundingClientRect() { return {left:100, top:50, width:960, height:360}; }
}
const names=['screen','frameSource','frameInfo','session','message','modules','events','filter','shutdown','confirmOnce',
  'startupProgress','startupPercent','startupMessage','startupDetail','shell','leftPanel','rightPanel','toggleLeft',
  'toggleRight','syntheticBanner','scopeLabel'];
const elements=Object.fromEntries(names.map(id => [id,new Element(id)]));
const document={getElementById:id=>elements[id],createElement:tag=>new Element(tag)};
const localStorage={getItem:()=>null,setItem(){}};
const location={origin:'http://127.0.0.1:8765'};
const headers=new Map([['X-Frame-Sequence','7'],['X-Frame-Captured-Ns',String(Date.now()*1000000)],
  ['X-Frame-Width','1920'],['X-Frame-Height','720'],['X-Frame-Source','guest-compositor'],['X-Frame-Stale','false']]);
let frameGets=0, pointerResolve=null, frameTimer=null, holdTimer=null, posts=0;
async function fetch(path, options={}) {
  if (options.method === 'POST') {
    if (!path.endsWith('/input/pointer')) return {ok:true,json:async()=>({state:'completed',message:'fixture',command_id:'other'})};
    posts++;
    return new Promise(resolve => { pointerResolve=()=>resolve({ok:true,json:async()=>({state:'completed',message:'fixture',command_id:'pointer'})}); });
  }
  if (path.endsWith('/frame')) { frameGets++; return {ok:true,headers,blob:async()=>({})}; }
  if (path.endsWith('/modules')) return {ok:true,json:async()=>({modules:[]})};
  if (path.endsWith('/status')) return {ok:true,json:async()=>({state:'fixture',service_state:'ready',scope:'local-vm',progress:100})};
  return {ok:true,json:async()=>({events:[]})};
}
const sandbox={document,fetch,localStorage,location,URL:{createObjectURL:()=> 'blob:'+frameGets,revokeObjectURL(){}},
  setTimeout(fn,ms){if(ms===800 || ms===400) frameTimer=fn; if(ms===100) holdTimer=fn;},setInterval(){},
  Date,Promise,JSON,Number,Math,String,Array,Object,encodeURIComponent};
vm.runInNewContext(script, sandbox);
const flush=()=>new Promise(resolve=>setImmediate(resolve));
(async()=>{
  await flush(); await flush();
  await frameTimer(); await flush();
  elements.screen.onload();
  let blocked=false;
  elements.screen.dispatch('keydown',{code:'Tab',repeat:false,preventDefault(){blocked=true;}});
  if (blocked) throw Error('Wi-Fi lane intercepted Tab');
  blocked=false;
  elements.screen.dispatch('keydown',{code:'KeyA',repeat:false,preventDefault(){blocked=true;}});
  if (!blocked) throw Error('Wi-Fi lane stopped enforcing key policy');
  elements.screen.dispatch('pointerdown',{button:0,pointerId:1,isPrimary:true,clientX:275,clientY:268});
  elements.screen.dispatch('pointerup',{pointerId:1,isPrimary:true,clientX:275,clientY:268});
  await flush();
  if (!pointerResolve || posts !== 1) throw Error('simulated pointer was not posted exactly once');
  const before=frameGets;
  await frameTimer(); await flush();
  if (frameGets!==before || !holdTimer) throw Error('pending input did not hold frame polling');
  pointerResolve(); await flush(); await flush();
  if (!elements.message.textContent.includes('(pointer)')) throw Error('pointer receipt was not correlated');
  await holdTimer(); await flush();
  if (frameGets!==before+1) throw Error('frame polling did not resume after receipt');
  elements.screen.onload();
  elements.screen.dispatch('pointerdown',{button:0,pointerId:2,isPrimary:true,clientX:275,clientY:268});
  elements.screen.dispatch('pointercancel',{pointerId:2,isPrimary:true});
  await frameTimer(); await flush();
  if (frameGets!==before+2 || posts !== 1) throw Error('pointer cancellation released or posted input');
  console.log('simulation frame hold passed');
})().catch(error=>{console.error(error);process.exitCode=1});
'''


NODE_LAYOUT_TEST = r'''
const fs=require('fs');
const vm=require('vm');
const html=fs.readFileSync(process.argv[1],'utf8');
const script=html.match(/<script>([\s\S]*)<\/script>/)[1].replace('__WORKBENCH_WIFI_SIM__','false');
const names=['screen','frameSource','frameInfo','session','message','modules','events','filter','shutdown','confirmOnce',
  'startupProgress','startupPercent','startupMessage','startupDetail','shell','leftPanel','rightPanel','toggleLeft',
  'toggleRight','syntheticBanner','scopeLabel'];
class Element {
  constructor(id='') { this.id=id; this.handlers={}; this.children=[]; this.value=''; this.textContent=''; this.className=''; this.hidden=false; this.attributes={}; }
  addEventListener(name,fn){this.handlers[name]=fn;}
  dispatch(name,fields={}){return this.handlers[name]?.({preventDefault(){},...fields});}
  append(...children){this.children.push(...children);} replaceChildren(){this.children=[];}
  setPointerCapture(){} focus(){} setAttribute(name,value){this.attributes[name]=String(value);}
  getBoundingClientRect(){return {left:0,top:0,width:960,height:360};}
}
function boot(origin, storage, storageThrows=false) {
  const elements=Object.fromEntries(names.map(id=>[id,new Element(id)]));
  const document={getElementById:id=>elements[id],createElement:tag=>new Element(tag)};
  const activeStorage=storageThrows ? {getItem(){throw Error('unavailable')},setItem(){throw Error('unavailable')}} : storage;
  const fetch=async path=>({ok:true,json:async()=>path.endsWith('/status') ? {state:'fixture',service_state:'starting',scope:'local-vm'} : (path.endsWith('/modules') ? {modules:[]} : {events:[]})});
  const sandbox={document,fetch,localStorage:activeStorage,location:{origin},URL:{createObjectURL:()=> 'blob:fixture',revokeObjectURL(){}},
    setTimeout(){},setInterval(){},Date,Promise,JSON,Number,Math,String,Array,Object,encodeURIComponent};
  vm.runInNewContext(script,sandbox);
  return elements;
}
const origin='http://127.0.0.1:8765';
const key='gen5w-workbench:panels:v1:'+encodeURIComponent(origin);
const store=new Map([[key,'{"left":false,"right":true}'],[key+':sentinel-key','unrelated']]);
let elements=boot(origin,{getItem:key=>store.get(key) ?? null,setItem:(key,value)=>store.set(key,String(value))});
if (!elements.leftPanel.hidden || elements.rightPanel.hidden) throw Error('valid panel recovery failed');
if (elements.toggleLeft.attributes['aria-expanded']!=='false' || !elements.shell.className.includes('left-collapsed')) throw Error('collapsed shell state missing');
elements.toggleLeft.dispatch('click');
const saved=JSON.parse(store.get(key));
if (JSON.stringify(saved)!=='{"left":true,"right":true}') throw Error('panel persistence added non-boolean state '+JSON.stringify(saved));
if (elements.leftPanel.hidden) throw Error('panel toggle did not restore the panel');
const isolatedStore=new Map([[key,'{"left":false,"right":false}']]);
elements=boot('http://127.0.0.1:9998',{getItem:key=>isolatedStore.get(key) ?? null,setItem:(key,value)=>isolatedStore.set(key,String(value))});
if (elements.leftPanel.hidden || elements.rightPanel.hidden) throw Error('another origin reused panel preferences');
const extraKey='gen5w-workbench:panels:v1:'+encodeURIComponent('http://127.0.0.1:9999');
const extraStore=new Map([[extraKey,'{"left":false,"right":false,"command":"do not store"}']]);
elements=boot('http://127.0.0.1:9999',{getItem:key=>extraStore.get(key) ?? null,setItem:(key,value)=>extraStore.set(key,String(value))});
if (elements.leftPanel.hidden || elements.rightPanel.hidden) throw Error('extra stored fields were not rejected');
const malformedStore=new Map([[extraKey,'{broken']]);
elements=boot('http://127.0.0.1:9999',{getItem:key=>malformedStore.get(key) ?? null,setItem:(key,value)=>malformedStore.set(key,String(value))});
if (elements.leftPanel.hidden || elements.rightPanel.hidden) throw Error('malformed storage was not harmless');
elements.toggleRight.dispatch('click');
const repaired=JSON.parse(malformedStore.get(extraKey));
if (JSON.stringify(repaired)!=='{"left":true,"right":false}') throw Error('repaired preferences are not exact booleans');
elements=boot(origin,new Map(),true);
if (elements.leftPanel.hidden || elements.rightPanel.hidden) throw Error('unavailable storage changed defaults');
elements.toggleLeft.dispatch('click');
console.log('panel preference recovery passed');
'''


NODE_GESTURE_TEST = r'''
const fs=require('fs');
const vm=require('vm');
const html=fs.readFileSync(process.argv[1],'utf8');
const sourceScript=html.match(/<script>([\s\S]*)<\/script>/)[1];
const names=['screen','frameSource','frameInfo','session','message','modules','events','filter','shutdown','confirmOnce',
  'startupProgress','startupPercent','startupMessage','startupDetail','shell','leftPanel','rightPanel','toggleLeft',
  'toggleRight','syntheticBanner','scopeLabel'];
const flush=()=>new Promise(resolve=>setImmediate(resolve));
class Element {
  constructor(id='', rect=null) { this.id=id; this.rect=rect; this.handlers={}; this.children=[]; this.value=''; this.textContent=''; this.className=''; this.hidden=false; this.attributes={}; }
  addEventListener(name,fn){this.handlers[name]=fn;}
  dispatch(name,fields={}){return this.handlers[name]?.({preventDefault(){},...fields});}
  append(...children){this.children.push(...children);} replaceChildren(){this.children=[];}
  setPointerCapture(){} focus(){} setAttribute(name,value){this.attributes[name]=String(value);}
  getBoundingClientRect(){return this.rect;}
}
function boot({wifi=false, source='host-fixture', rect={left:100,top:50,width:960,height:360}}) {
  const elements=Object.fromEntries(names.map(id=>[id,new Element(id,rect)]));
  const document={getElementById:id=>elements[id],createElement:tag=>new Element(tag,rect)};
  const posts=[]; let frameTimer=null; let frameGets=0;
  const headers=new Map([['X-Frame-Sequence','7'],['X-Frame-Captured-Ns',String(Date.now()*1000000)],
    ['X-Frame-Width','1920'],['X-Frame-Height','720'],['X-Frame-Source',source],['X-Frame-Stale','false']]);
  const fetch=async (path,options={})=>{
    if(options.method==='POST') {
      if(path.endsWith('/input/pointer')) posts.push(JSON.parse(options.body));
      return {ok:true,json:async()=>({state:'completed',message:'accepted',command_id:'pointer-'+posts.length})};
    }
    if(path.endsWith('/frame')) { frameGets++; return {ok:true,headers,blob:async()=>({})}; }
    if(path.endsWith('/modules')) return {ok:true,json:async()=>({modules:[]})};
    if(path.endsWith('/status')) return {ok:true,json:async()=>({state:'fixture',service_state:'ready',scope:'host-fixture',progress:100})};
    return {ok:true,json:async()=>({events:[]})};
  };
  const sandbox={document,fetch,localStorage:{getItem:()=>null,setItem(){}},location:{origin:'http://127.0.0.1:8765'},
    URL:{createObjectURL:()=> 'blob:'+frameGets,revokeObjectURL(){}},setTimeout(fn,ms){if(ms===400||ms===800)frameTimer=fn;},
    setInterval(){},Date,Promise,JSON,Number,Math,String,Array,Object,encodeURIComponent};
  const script=sourceScript.replace('__WORKBENCH_WIFI_SIM__',String(wifi));
  vm.runInNewContext(script,sandbox);
  return {
    elements,posts,headers,
    async ready(){await flush();await flush();if(frameTimer){const timer=frameTimer;frameTimer=null;await timer();await flush();}elements.screen.onload();await flush();},
    async refresh(load=true){if(!frameTimer)throw Error('frame timer missing');const timer=frameTimer;frameTimer=null;await timer();await flush();if(load)elements.screen.onload();await flush();},
    screen(){return elements.screen;}
  };
}
(async()=>{
  const viewports=[
    {rect:{left:100,top:50,width:960,height:360},click:{x:580,y:230},drag:{start:{x:100,y:50},end:{x:1060,y:410}}},
    {rect:{left:0,top:0,width:480,height:270},click:{x:240,y:135},drag:{start:{x:0,y:0},end:{x:480,y:270}}}
  ];
  for(const viewport of viewports) {
    const h=boot({rect:viewport.rect}); await h.ready();
    const screen=h.screen();
    screen.dispatch('pointerdown',{button:0,pointerId:1,isPrimary:true,clientX:viewport.click.x,clientY:viewport.click.y});
    screen.dispatch('pointerup',{pointerId:1,isPrimary:true,clientX:viewport.click.x,clientY:viewport.click.y});
    screen.dispatch('pointerdown',{button:0,pointerId:2,isPrimary:true,clientX:viewport.drag.start.x,clientY:viewport.drag.start.y});
    screen.dispatch('pointerup',{pointerId:2,isPrimary:true,clientX:viewport.drag.end.x,clientY:viewport.drag.end.y});
    await flush();await flush();
    const expected=[{action:'click',x1:960,y1:360,frame_sequence:7},
      {action:'drag',x1:0,y1:0,x2:1919,y2:719,frame_sequence:7}];
    if(JSON.stringify(h.posts)!==JSON.stringify(expected)) throw Error('coordinate scaling failed at '+viewport.rect.width+'px '+JSON.stringify(h.posts));
    if(!h.elements.message.textContent.includes('(pointer-2)')) throw Error('gesture receipt was not correlated exactly once');
  }
  let h=boot({}); await h.ready(); let screen=h.screen();
  screen.dispatch('pointerdown',{button:0,pointerId:1,isPrimary:true,clientX:580,clientY:230});
  screen.dispatch('pointercancel',{pointerId:1,isPrimary:true});
  screen.dispatch('pointerup',{pointerId:1,isPrimary:true,clientX:580,clientY:230});
  await flush(); if(h.posts.length) throw Error('cancelled gesture posted input');
  screen.dispatch('pointerdown',{button:0,pointerId:1,isPrimary:true,clientX:580,clientY:230});
  screen.dispatch('pointerdown',{button:0,pointerId:2,isPrimary:false,clientX:580,clientY:230});
  screen.dispatch('pointerup',{pointerId:2,isPrimary:false,clientX:580,clientY:230});
  screen.dispatch('pointercancel',{pointerId:1,isPrimary:true});
  await flush(); if(h.posts.length) throw Error('secondary or cancelled pointer posted input');
  screen.dispatch('pointerdown',{button:0,pointerId:1,isPrimary:true,clientX:580,clientY:230});
  screen.dispatch('lostpointercapture',{pointerId:1,isPrimary:true});
  screen.dispatch('pointerup',{pointerId:1,isPrimary:true,clientX:580,clientY:230});
  await flush(); if(h.posts.length) throw Error('lost capture posted input');

  h=boot({}); await h.ready(); screen=h.screen();
  h.headers.set('X-Frame-Stale','true'); await h.refresh(true);
  screen.dispatch('pointerdown',{button:0,pointerId:3,isPrimary:true,clientX:580,clientY:230});
  screen.dispatch('pointerup',{pointerId:3,isPrimary:true,clientX:580,clientY:230});
  await flush(); if(h.posts.length) throw Error('stale frame posted input');

  h=boot({}); await h.ready(); screen=h.screen();
  screen.dispatch('pointerdown',{button:0,pointerId:3,isPrimary:true,clientX:580,clientY:230});
  h.headers.set('X-Frame-Sequence','8'); await h.refresh(true);
  screen.dispatch('pointerup',{pointerId:3,isPrimary:true,clientX:580,clientY:230});
  await flush();
  if(h.posts.length!==1 || h.posts[0].frame_sequence!==7) {
    throw Error('gesture did not retain its displayed sequence while polling was held');
  }

  h=boot({}); await h.ready(); screen=h.screen();
  await h.refresh(false);
  screen.dispatch('pointerdown',{button:0,pointerId:4,isPrimary:true,clientX:580,clientY:230});
  screen.dispatch('pointerup',{pointerId:4,isPrimary:true,clientX:580,clientY:230});
  await flush(); if(h.posts.length) throw Error('undecoded frame posted input');

  h=boot({wifi:true,source:'host-fixture'}); await h.ready(); screen=h.screen();
  screen.dispatch('pointerdown',{button:0,pointerId:5,isPrimary:true,clientX:580,clientY:230});
  screen.dispatch('pointerup',{pointerId:5,isPrimary:true,clientX:580,clientY:230});
  await flush(); if(h.posts.length) throw Error('Wi-Fi policy admitted a host-fixture frame');

  h=boot({wifi:true,source:'guest-compositor'}); await h.ready(); screen=h.screen();
  screen.dispatch('pointerdown',{button:0,pointerId:6,isPrimary:true,clientX:580,clientY:230});
  screen.dispatch('pointerup',{pointerId:6,isPrimary:true,clientX:580,clientY:230});
  await flush();await flush();
  if(h.posts.length!==1 || h.posts[0].frame_sequence!==7) throw Error('Wi-Fi click was not one correlated request '+JSON.stringify(h.posts));
  if(!h.elements.message.textContent.includes('(pointer-1)')) throw Error('Wi-Fi receipt was not correlated');
  screen.dispatch('pointerdown',{button:0,pointerId:7,isPrimary:true,clientX:100,clientY:50});
  screen.dispatch('pointerup',{pointerId:7,isPrimary:true,clientX:1060,clientY:410});
  await flush(); if(h.posts.length!==1) throw Error('Wi-Fi policy admitted a drag');
  console.log('gesture lifetime and scaling passed');
})().catch(error=>{console.error(error);process.exitCode=1});
'''


NODE_PREVIEW_SEQUENCE_TEST = r'''
const fs=require('fs');
const vm=require('vm');
const html=fs.readFileSync(process.argv[1],'utf8');
const script=html.match(/<script>([\s\S]*)<\/script>/)[1].replace('__WORKBENCH_WIFI_SIM__','false');
class Element {
  constructor(id='') { this.id=id; this.handlers={}; this.children=[]; this.value=''; this.textContent=''; this.className=''; this.hidden=false; this.attributes={}; }
  addEventListener(name,fn){this.handlers[name]=fn;}
  dispatch(name,fields={}){return this.handlers[name]?.({preventDefault(){},...fields});}
  append(...children){this.children.push(...children);} replaceChildren(){this.children=[];}
  setPointerCapture(){} focus(){} setAttribute(name,value){this.attributes[name]=String(value);}
  getBoundingClientRect(){return {left:100,top:50,width:960,height:360};}
}
const names=['screen','frameSource','frameInfo','session','message','modules','events','filter','shutdown','confirmOnce',
  'startupProgress','startupPercent','startupMessage','startupDetail','shell','leftPanel','rightPanel','toggleLeft',
  'toggleRight','syntheticBanner','scopeLabel'];
const elements=Object.fromEntries(names.map(id=>[id,new Element(id)]));
const document={getElementById:id=>elements[id],createElement:tag=>new Element(tag)};
const headers=new Map([['X-Frame-Sequence','7'],['X-Frame-Captured-Ns',String(Date.now()*1000000)],
  ['X-Frame-Width','1920'],['X-Frame-Height','720'],['X-Frame-Source','fixture'],['X-Frame-Stale','false']]);
let frameGets=0, frameTimer=null, holdTimer=null, pointerResolve=null, posted=null;
async function fetch(path,options={}) {
  if (options.method==='POST') {
    if (!path.endsWith('/input/pointer')) return {ok:true,json:async()=>({state:'completed',message:'fixture',command_id:'other'})};
    posted=JSON.parse(options.body);
    return new Promise(resolve=>{pointerResolve=()=>resolve({ok:true,json:async()=>({
      state:'completed',message:'fixture',command_id:'preview-pointer'})});});
  }
  if(path.endsWith('/frame')) { frameGets++; return {ok:true,headers,blob:async()=>({})}; }
  if(path.endsWith('/modules')) return {ok:true,json:async()=>({modules:[]})};
  if(path.endsWith('/status')) return {ok:true,json:async()=>({
    state:'running',service_state:'ready',scope:'host-fixture',progress:100})};
  return {ok:true,json:async()=>({events:[]})};
}
const sandbox={document,fetch,localStorage:{getItem:()=>null,setItem(){}},location:{origin:'http://127.0.0.1:8765'},
  URL:{createObjectURL:()=> 'blob:'+frameGets,revokeObjectURL(){}},
  setTimeout(fn,ms){if(ms===400||ms===800)frameTimer=fn;if(ms===100)holdTimer=fn;},
  setInterval(){},Date,Promise,JSON,Number,Math,String,Array,Object,encodeURIComponent};
vm.runInNewContext(script,sandbox);
const flush=()=>new Promise(resolve=>setImmediate(resolve));
(async()=>{
  await flush();await flush();await frameTimer();await flush();elements.screen.onload();
  elements.screen.dispatch('pointerdown',{button:0,pointerId:1,isPrimary:true,clientX:580,clientY:230});
  elements.screen.dispatch('pointerup',{pointerId:1,isPrimary:true,clientX:580,clientY:230});
  await flush();
  if(!posted || posted.frame_sequence!==7) throw Error('preview pointer omitted displayed sequence '+JSON.stringify(posted));
  const before=frameGets;
  await frameTimer();await flush();
  if(frameGets!==before || !holdTimer) throw Error('preview pointer command did not hold frame polling');
  pointerResolve();await flush();await flush();
  await holdTimer();await flush();
  if(frameGets!==before+1) throw Error('preview frame polling did not resume');
  console.log('preview sequence hold passed');
})().catch(error=>{console.error(error);process.exitCode=1});
'''


class WorkbenchUITests(unittest.TestCase):
    def _run_node(self, script: str, marker: str) -> None:
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node is required to execute the browser script fixture")
        result = subprocess.run(
            [node, "-e", script, str(PAGE)],
            text=True,
            capture_output=True,
            timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(marker, result.stdout)

    def test_source_contracts_and_server_anchors(self):
        page = PAGE.read_text(encoding="utf-8")
        self.assertIn("<header><h1>Gen5W VM Workbench __WORKBENCH_VERSION__</h1>", page)
        self.assertIn("position: sticky; top: 0", page)
        for anchor in (
            'id="toggleLeft"', 'id="toggleRight"', 'id="leftPanel"', 'id="rightPanel"',
            'id="syntheticBanner"', 'aria-controls="leftPanel"', 'aria-controls="rightPanel"',
        ):
            self.assertIn(anchor, page)
        for placeholder in (
            "__WORKBENCH_VERSION__", "__WORKBENCH_SESSION_TOKEN__", "__WORKBENCH_WIFI_SIM__",
        ):
            self.assertIn(placeholder, page)
        self.assertIn("const api = '/api/v1';", page)
        self.assertIn("status.scope === 'host-fixture'", page)
        self.assertIn("gen5w-workbench:panels:v1:", page)
        self.assertIn("Synthetic preview", page)
        self.assertIn("Host fixture data only.", page)

    def test_frame_preview_mouse_keyboard_and_logs(self):
        self._run_node(NODE_TEST, "fixture DOM interaction passed")

    def test_panel_preference_recovery_is_exact_and_harmless(self):
        self._run_node(NODE_LAYOUT_TEST, "panel preference recovery passed")

    def test_gesture_lifetimes_and_coordinate_scaling(self):
        self._run_node(NODE_GESTURE_TEST, "gesture lifetime and scaling passed")

    def test_simulation_input_holds_and_releases_frame_polling(self):
        self._run_node(NODE_SIMULATION_TEST, "simulation frame hold passed")

    def test_preview_pointer_sequence_holds_frame_polling(self):
        self._run_node(NODE_PREVIEW_SEQUENCE_TEST, "preview sequence hold passed")


if __name__ == "__main__":
    unittest.main()
