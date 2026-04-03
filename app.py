#!/usr/bin/env python3
import os, io, base64
from flask import Flask, render_template_string, jsonify, send_file, request
from skin_designer import generate_skin, create_zip, THEMES

app = Flask(__name__)

SIDEBAR_ITEMS = [
    ("head",      "👑", "Head & Crown"),
    ("eyes",      "👁️", "Eyes & Face"),
    ("body",      "✨", "Body FX"),
    ("scythe",    "⚔️", "Scythe & Chain"),
    ("robe",      "🌟", "Robe & Trim"),
    ("shape",     "🔮", "Shape Border"),
    ("aurora",    "🌌", "Aurora Wave"),
    ("hellfire",  "🔥", "Hellfire Rise"),
    ("crystal",   "💎", "Crystal Shards"),
    ("lightning", "⚡", "Lightning Strike"),
    ("smoke",     "💨", "Smoke Tendrils"),
    ("blood",     "🩸", "Blood Drip"),
    ("sand",      "🌪️", "Sand Vortex"),
    ("wisps",     "👻", "Ghost Wisps"),
]

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI GrimReaper Skin Maker</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#080810;color:#e0e0e0;font-family:'Segoe UI',sans-serif;min-height:100vh;display:flex;flex-direction:column}
header{background:linear-gradient(135deg,#1a0030,#0d0020);padding:14px 24px;border-bottom:1px solid #3a0060;display:flex;align-items:center;gap:10px;flex-shrink:0}
header h1{font-size:1.35rem;background:linear-gradient(90deg,#a040ff,#ff40a0);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
header p{color:#555;font-size:0.75rem;margin-top:2px}
.layout{display:flex;flex:1;overflow:hidden}
/* ── SIDEBAR ── */
.sidebar{width:200px;flex-shrink:0;background:#0c0c1a;border-right:1px solid #1e1e35;padding:16px 12px;display:flex;flex-direction:column;gap:6px;overflow-y:auto}
.sidebar h3{font-size:0.7rem;text-transform:uppercase;letter-spacing:.1em;color:#404060;margin-bottom:6px;padding-bottom:6px;border-bottom:1px solid #1e1e35}
.toggle-item{display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:8px;cursor:pointer;transition:background .15s;user-select:none}
.toggle-item:hover{background:#141428}
.toggle-item.active{background:#1a1035}
.brad{display:inline-flex;align-items:center;gap:4px;padding:4px 10px;border-radius:20px;background:#1a0a2a;border:1px solid #3a1a5a;color:#a080d0;font-size:0.72rem;cursor:pointer;transition:background .15s}
.brad:has(input:checked){background:#3a1a6a;border-color:#7030e0;color:#fff}
.brad input{display:none}
.cat-header{font-size:0.65rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#7050a0;padding:6px 4px 3px;cursor:pointer;user-select:none;border-bottom:1px solid #1e1e35;margin-top:6px}
.cat-header:hover{color:#a080d0}
.toggle-item .ico{font-size:1.1rem;width:22px;text-align:center}
.toggle-item .lbl{font-size:0.82rem;color:#c0a0e0;flex:1}
.toggle-switch{width:32px;height:18px;background:#2a2a45;border-radius:9px;position:relative;transition:background .2s;flex-shrink:0}
.toggle-switch.on{background:#7030e0}
.toggle-switch::after{content:'';position:absolute;width:12px;height:12px;background:#fff;border-radius:50%;top:3px;left:3px;transition:left .2s}
.toggle-switch.on::after{left:17px}
.sidebar-sep{height:1px;background:#1e1e35;margin:4px 0}
/* ── MAIN ── */
.main{flex:1;overflow-y:auto;padding:20px}
.controls{background:#10101c;border:1px solid #252540;border-radius:12px;padding:16px;margin-bottom:18px;display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end}
.cg{display:flex;flex-direction:column;gap:5px}
label{font-size:0.72rem;color:#666;text-transform:uppercase;letter-spacing:.05em}
select,input[type=number]{background:#181828;border:1px solid #333355;color:#e0e0e0;padding:7px 10px;border-radius:8px;font-size:0.85rem;outline:none}
select:focus,input:focus{border-color:#7030e0}
.btn{padding:8px 18px;border:none;border-radius:8px;cursor:pointer;font-size:0.88rem;font-weight:600;transition:all .18s}
.btn-gen{background:linear-gradient(135deg,#5010b0,#9030f0);color:#fff}
.btn-gen:hover{transform:translateY(-1px);box-shadow:0 4px 18px #7030f066}
.btn-gen:disabled{opacity:.45;cursor:not-allowed;transform:none}
.btn-dl{background:linear-gradient(135deg,#005030,#00a060);color:#fff}
.btn-dl:hover{transform:translateY(-1px);box-shadow:0 4px 18px #00a06066}
.btn-dl:disabled{opacity:.4;cursor:not-allowed;transform:none}
.preview{background:#10101c;border:1px solid #252540;border-radius:12px;padding:20px}
.ph{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:8px}
.sname{font-size:1.1rem;font-weight:700;color:#b070ff}
.sid{color:#404060;font-size:0.75rem;margin-top:2px}
.anims{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:16px}
.ab{background:#0c0c18;border:1px solid #1c1c32;border-radius:10px;padding:12px}
.at{font-size:0.72rem;text-transform:uppercase;letter-spacing:.1em;color:#505090;margin-bottom:8px}
.strip{display:flex;gap:4px;flex-wrap:wrap}
.strip canvas{width:76px;height:63px;background:#141428;border-radius:6px;border:1px solid #222240;cursor:pointer;transition:border-color .15s}
.strip canvas:hover{border-color:#7030e0}
.strip canvas.active{border-color:#9050f0;box-shadow:0 0 7px #7030f077}
.bigp{text-align:center;margin-top:10px}
.bigp canvas{max-width:188px;width:188px;height:156px;background:#141428;border-radius:8px;border:1px solid #2a2a50}
.loading{text-align:center;padding:50px;color:#505080}
.spin{display:inline-block;width:28px;height:28px;border:3px solid #2a2a50;border-top-color:#7030e0;border-radius:50%;animation:spin .7s linear infinite;margin-bottom:10px}
@keyframes spin{to{transform:rotate(360deg)}}
.empty{text-align:center;padding:55px 20px;color:#303050}
.hist{margin-top:18px}
.hist h3{font-size:0.75rem;text-transform:uppercase;letter-spacing:.1em;color:#404060;margin-bottom:8px}
.hgrid{display:flex;flex-wrap:wrap;gap:7px}
.hi{background:#10101c;border:1px solid #222240;border-radius:7px;padding:5px 10px;cursor:pointer;font-size:0.8rem;color:#9060c0;transition:all .15s}
.hi:hover{border-color:#5030a0;background:#181828}
.badge{display:inline-block;background:#201040;color:#b080e0;font-size:0.65rem;padding:1px 6px;border-radius:20px;margin-left:4px}
</style>
</head>
<body>
<header>
  <div>
    <h1>⚔️ AI GrimReaper Skin Maker <span style="font-size:0.65rem;background:#2a1a4a;color:#a080d0;padding:2px 7px;border-radius:10px;margin-left:6px;-webkit-text-fill-color:#a080d0">v1.03</span></h1>
    <p>49 themes · Unique eye styles · Weapons · Real-time animation toggles</p>
  </div>
</header>
<div class="layout">
  <!-- SIDEBAR -->
  <div class="sidebar">
    <!-- Enable All / Disable All -->
    <div style="display:flex;gap:4px;margin-bottom:8px">
      <button onclick="setAllGroups(true)"  style="flex:1;padding:4px;border-radius:6px;background:#1a1035;border:1px solid #5030a0;color:#a080d0;font-size:0.68rem;cursor:pointer">✅ All On</button>
      <button onclick="setAllGroups(false)" style="flex:1;padding:4px;border-radius:6px;background:#1a0a1a;border:1px solid #501030;color:#e06080;font-size:0.68rem;cursor:pointer">❌ All Off</button>
    </div>

    <!-- Category: Head -->
    <div class="cat-header" onclick="toggleCat('cat_head')">👑 Head</div>
    <div id="cat_head">
      <div class="toggle-item active" id="ti_head" onclick="toggleAnim('head')"><span class="ico">👑</span><span class="lbl">Head & Crown</span><div class="toggle-switch on" id="sw_head"></div></div>
      <div class="toggle-item active" id="ti_eyes" onclick="toggleAnim('eyes')"><span class="ico">👁️</span><span class="lbl">Eyes & Face</span><div class="toggle-switch on" id="sw_eyes"></div></div>
    </div>

    <!-- Category: Body -->
    <div class="cat-header" onclick="toggleCat('cat_body')">🧍 Body</div>
    <div id="cat_body">
      <div class="toggle-item active" id="ti_body" onclick="toggleAnim('body')"><span class="ico">✨</span><span class="lbl">Body FX</span><div class="toggle-switch on" id="sw_body"></div></div>
      <div class="toggle-item active" id="ti_robe" onclick="toggleAnim('robe')"><span class="ico">🌟</span><span class="lbl">Robe & Trim</span><div class="toggle-switch on" id="sw_robe"></div></div>
      <div class="toggle-item active" id="ti_blood" onclick="toggleAnim('blood')"><span class="ico">🩸</span><span class="lbl">Blood Drip</span><div class="toggle-switch on" id="sw_blood"></div></div>
      <div class="toggle-item active" id="ti_smoke" onclick="toggleAnim('smoke')"><span class="ico">💨</span><span class="lbl">Smoke Tendrils</span><div class="toggle-switch on" id="sw_smoke"></div></div>
    </div>

    <!-- Category: Scythe & Chain -->
    <div class="cat-header" onclick="toggleCat('cat_scythe')">⚔️ Scythe</div>
    <div id="cat_scythe">
      <div class="toggle-item active" id="ti_scythe" onclick="toggleAnim('scythe')"><span class="ico">⚔️</span><span class="lbl">Scythe & Chain</span><div class="toggle-switch on" id="sw_scythe"></div></div>
      <div class="toggle-item active" id="ti_lightning" onclick="toggleAnim('lightning')"><span class="ico">⚡</span><span class="lbl">Lightning Strike</span><div class="toggle-switch on" id="sw_lightning"></div></div>
    </div>

    <!-- Category: Aura / Particles -->
    <div class="cat-header" onclick="toggleCat('cat_aura')">🌌 Aura</div>
    <div id="cat_aura">
      <div class="toggle-item active" id="ti_aurora" onclick="toggleAnim('aurora')"><span class="ico">🌌</span><span class="lbl">Aurora Wave</span><div class="toggle-switch on" id="sw_aurora"></div></div>
      <div class="toggle-item active" id="ti_hellfire" onclick="toggleAnim('hellfire')"><span class="ico">🔥</span><span class="lbl">Hellfire Rise</span><div class="toggle-switch on" id="sw_hellfire"></div></div>
      <div class="toggle-item active" id="ti_crystal" onclick="toggleAnim('crystal')"><span class="ico">💎</span><span class="lbl">Crystal Shards</span><div class="toggle-switch on" id="sw_crystal"></div></div>
      <div class="toggle-item active" id="ti_wisps" onclick="toggleAnim('wisps')"><span class="ico">👻</span><span class="lbl">Ghost Wisps</span><div class="toggle-switch on" id="sw_wisps"></div></div>
      <div class="toggle-item active" id="ti_sand" onclick="toggleAnim('sand')"><span class="ico">🌪️</span><span class="lbl">Sand Vortex</span><div class="toggle-switch on" id="sw_sand"></div></div>
    </div>

    <!-- Category: Border -->
    <div class="cat-header" onclick="toggleCat('cat_border')">🔮 Border</div>
    <div id="cat_border">
      <div class="toggle-item active" id="ti_shape" onclick="toggleAnim('shape')"><span class="ico">🔮</span><span class="lbl">Shape Border</span><div class="toggle-switch on" id="sw_shape"></div></div>
    </div>

    <div class="sidebar-sep"></div>
    <div class="toggle-item" id="ti_pingpong" onclick="togglePP()">
      <span class="ico">🔄</span><span class="lbl">Ping-pong</span>
      <div class="toggle-switch" id="sw_pingpong"></div>
    </div>
  </div>

  <!-- MAIN -->
  <div class="main">
    <div class="controls">
      <div class="cg">
        <label>Theme</label>
        <select id="themeSelect" onchange="onThemeChange(this.value)">
          <option value="">🎲 Random</option>
          {% for t in themes %}<option value="{{t.name}}" data-anim1="{{t.get('anim1','')}}" data-anim2="{{t.get('anim2','')}}" data-border="{{t.get('border','')}}">{{t.name}}</option>{% endfor %}
        </select>
      </div>
      <div class="cg">
        <label>Seed (optional)</label>
        <input type="number" id="seedInput" placeholder="e.g. 42" style="width:100px">
      </div>
      <button class="btn btn-gen" id="genBtn" onclick="gen()">✨ Generate Skin</button>
      <button class="btn btn-dl" id="dlBtn" onclick="dl()" disabled>⬇ Download ZIP</button>
    </div>

    <!-- Border Effects (radio — 1 at a time) -->
    <div style="padding:8px 16px;background:#0d0a1a;border-bottom:1px solid #2a1a4a">
      <div style="font-size:0.7rem;color:#a080d0;font-weight:700;margin-bottom:6px;text-transform:uppercase;letter-spacing:1px">🔮 Border Effect <span style="font-size:0.6rem;color:#555;font-weight:400">(select 1, or merge 2)</span></div>
      <div style="display:flex;flex-wrap:wrap;gap:6px;align-items:center" id="borderRadios">
        <label class="brad" data-b=""><input type="radio" name="border" value="" checked onchange="onBorderChange('')"> None</label>
        <label class="brad" data-b="armor"><input type="radio" name="border" value="armor" onchange="onBorderChange('armor')"> ⚔️ Armor</label>
        <label class="brad" data-b="fire_border"><input type="radio" name="border" value="fire_border" onchange="onBorderChange('fire_border')"> 🔥 Fire</label>
        <label class="brad" data-b="ice_border"><input type="radio" name="border" value="ice_border" onchange="onBorderChange('ice_border')"> ❄️ Ice</label>
        <label class="brad" data-b="void_border"><input type="radio" name="border" value="void_border" onchange="onBorderChange('void_border')"> 🌑 Void</label>
        <label class="brad" data-b="gold_border"><input type="radio" name="border" value="gold_border" onchange="onBorderChange('gold_border')"> 🥇 Gold</label>
        <label class="brad" data-b="rainbow_border"><input type="radio" name="border" value="rainbow_border" onchange="onBorderChange('rainbow_border')"> 🌈 Rainbow</label>
        <label class="brad" data-b="electric_border"><input type="radio" name="border" value="electric_border" onchange="onBorderChange('electric_border')"> ⚡ Electric</label>
        <label class="brad" data-b="nature_border"><input type="radio" name="border" value="nature_border" onchange="onBorderChange('nature_border')"> 🌿 Nature</label>
        <label class="brad" data-b="royal"><input type="radio" name="border" value="royal" onchange="onBorderChange('royal')"> 👑 Royal</label>
        <button onclick="openMerge()" style="padding:3px 10px;border-radius:8px;background:#2a1a4a;border:1px solid #5030a0;color:#a080d0;font-size:0.7rem;cursor:pointer">⚗️ Merge 2</button>
      </div>
    </div>

    <!-- Merge Modal -->
    <div id="mergeModal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.8);z-index:9999;align-items:center;justify-content:center">
      <div style="background:#0d0a1a;border:1.5px solid #5030a0;border-radius:14px;padding:20px;width:340px;display:flex;flex-direction:column;gap:10px">
        <div style="font-size:0.9rem;font-weight:700;color:#a080d0">⚗️ Merge 2 Border Effects</div>
        <select id="merge1" style="padding:6px;border-radius:8px;background:#1a0a2a;border:1px solid #3a1a5a;color:#e0e0e0">
          <option value="fire_border">🔥 Fire</option><option value="ice_border">❄️ Ice</option>
          <option value="void_border">🌑 Void</option><option value="gold_border">🥇 Gold</option>
          <option value="rainbow_border">🌈 Rainbow</option><option value="electric_border">⚡ Electric</option>
          <option value="nature_border">🌿 Nature</option><option value="armor">⚔️ Armor</option><option value="royal">👑 Royal</option>
        </select>
        <select id="merge2" style="padding:6px;border-radius:8px;background:#1a0a2a;border:1px solid #3a1a5a;color:#e0e0e0">
          <option value="ice_border">❄️ Ice</option><option value="fire_border">🔥 Fire</option>
          <option value="void_border">🌑 Void</option><option value="gold_border">🥇 Gold</option>
          <option value="rainbow_border">🌈 Rainbow</option><option value="electric_border">⚡ Electric</option>
          <option value="nature_border">🌿 Nature</option><option value="armor">⚔️ Armor</option><option value="royal">👑 Royal</option>
        </select>
        <div style="display:flex;gap:8px">
          <button onclick="doMerge()" style="flex:1;padding:8px;border-radius:8px;background:linear-gradient(135deg,#7030e0,#a040ff);border:none;color:#fff;font-weight:700;cursor:pointer">Apply Merge</button>
          <button onclick="document.getElementById('mergeModal').style.display='none'" style="padding:8px 14px;border-radius:8px;background:#1a0a2a;border:1px solid #3a1a5a;color:#888;cursor:pointer">Cancel</button>
        </div>
      </div>
    </div>

    <div class="preview" id="preview">
      <div class="empty"><p style="font-size:2.5rem;margin-bottom:10px">🎭</p><p>Click Generate to create a skin</p></div>
    </div>

    <div class="hist" id="histSec" style="display:none">
      <h3>Recent Skins</h3>
      <div class="hgrid" id="hgrid"></div>
    </div>
  </div>
</div>

<script>
let curId=null, hist=[], intervals={};
let baseFrames={}, overlayFrames={};
let baseImgs={}, overlayImgs={};
let enabledGroups=new Set(['head','eyes','body','scythe','robe','shape']);
let pingpong=false;
let activeBorder='';
let mergedBorder=null; // {b1,b2} when merge active
const GROUPS=['head','eyes','body','scythe','robe','shape','aurora','hellfire','crystal','lightning','smoke','blood','sand','wisps'];
const ANIMS=['attack','flying','idle'];
const FPS={attack:12,flying:6,idle:6};

// Theme data from server
const THEME_DATA = {
  {% for t in themes %}"{{t.name}}":{"anim1":"{{t.get('anim1','')}}","anim2":"{{t.get('anim2','')}}","border":"{{t.get('border','')}}"},
  {% endfor %}
};

function setAllGroups(on){
  GROUPS.forEach(g=>{
    if(on) enabledGroups.add(g); else enabledGroups.delete(g);
    const sw=document.getElementById('sw_'+g);
    const ti=document.getElementById('ti_'+g);
    if(sw) sw.className='toggle-switch'+(on?' on':'');
    if(ti) ti.className='toggle-item'+(on?' active':'');
  });
  if(curId) ANIMS.forEach(anim=>{ drawAllStrip(anim); drawBig(anim,animIdxs[anim]); });
}

function toggleCat(catId){
  const el=document.getElementById(catId);
  if(el) el.style.display=el.style.display==='none'?'':'none';
}

function onThemeChange(name){
  const td=THEME_DATA[name];
  if(!td) return;
  // Auto-enable theme's 2 special animations
  if(td.anim1) enabledGroups.add(td.anim1);
  if(td.anim2) enabledGroups.add(td.anim2);
  // Auto-set theme border
  if(td.border){
    activeBorder=td.border; mergedBorder=null;
    document.querySelectorAll('input[name="border"]').forEach(r=>r.checked=(r.value===td.border));
  }
  // Refresh toggle UI
  GROUPS.forEach(g=>{
    const sw=document.getElementById('sw_'+g);
    const ti=document.getElementById('ti_'+g);
    if(sw){ const on=enabledGroups.has(g); sw.className='toggle-switch'+(on?' on':''); }
    if(ti){ const on=enabledGroups.has(g); ti.className='toggle-item'+(on?' active':''); }
  });
}

function onBorderChange(val){
  activeBorder=val; mergedBorder=null;
  if(curId) { ANIMS.forEach(anim=>{ drawAllStrip(anim); drawBig(anim,animIdxs[anim]); }); }
}

function openMerge(){ document.getElementById('mergeModal').style.display='flex'; }
function doMerge(){
  const b1=document.getElementById('merge1').value;
  const b2=document.getElementById('merge2').value;
  mergedBorder={b1,b2}; activeBorder='__merged__';
  document.querySelectorAll('input[name="border"]').forEach(r=>r.checked=false);
  document.getElementById('mergeModal').style.display='none';
  if(curId) { ANIMS.forEach(anim=>{ drawAllStrip(anim); drawBig(anim,animIdxs[anim]); }); }
}

function gen(){
  const btn=document.getElementById('genBtn');
  btn.disabled=true; document.getElementById('dlBtn').disabled=true;
  document.getElementById('preview').innerHTML='<div class="loading"><div class="spin"></div><p>Generating skin...</p></div>';
  const p=new URLSearchParams();
  const theme=document.getElementById('themeSelect').value;
  const seed=document.getElementById('seedInput').value;
  if(theme)p.append('theme',theme);
  if(seed)p.append('seed',seed);
  fetch('/generate?'+p).then(r=>r.json()).then(d=>{
    curId=d.skin_id;
    baseFrames=d.base; overlayFrames=d.overlays;
    preloadAll(()=>{
      renderUI(d.skin_id, d.theme_name);
      addHist(d.skin_id,d.theme_name);
      btn.disabled=false; document.getElementById('dlBtn').disabled=false;
    });
  }).catch(e=>{
    document.getElementById('preview').innerHTML=`<div class="loading" style="color:#f04060">Error: ${e.message}</div>`;
    btn.disabled=false;
  });
}

function preloadAll(cb){
  baseImgs={}; overlayImgs={};
  let total=0, loaded=0;
  function done(){ loaded++; if(loaded>=total) cb(); }
  ANIMS.forEach(anim=>{
    baseImgs[anim]=[];
    baseFrames[anim].forEach((b64,i)=>{
      total++;
      const img=new Image();
      img.onload=done; img.onerror=done;
      img.src='data:image/png;base64,'+b64;
      baseImgs[anim].push(img);
    });
  });
  // Load all overlay groups including shape_* border variants
  const allGroups=Object.keys(overlayFrames);
  allGroups.forEach(g=>{
    overlayImgs[g]={};
    ANIMS.forEach(anim=>{
      overlayImgs[g][anim]=[];
      (overlayFrames[g]&&overlayFrames[g][anim]||[]).forEach((b64,i)=>{
        if(!b64){overlayImgs[g][anim].push(null);return;}
        total++;
        const img=new Image();
        img.onload=done; img.onerror=done;
        img.src='data:image/png;base64,'+b64;
        overlayImgs[g][anim].push(img);
      });
    });
  });
  if(total===0) cb();
}

function compositeFrame(anim, idx){
  const base=baseImgs[anim]&&baseImgs[anim][idx];
  if(!base) return null;
  const c=document.createElement('canvas');
  c.width=base.naturalWidth; c.height=base.naturalHeight;
  const ctx=c.getContext('2d');
  ctx.drawImage(base,0,0);
  GROUPS.forEach(g=>{
    if(!enabledGroups.has(g)) return;
    const ov=overlayImgs[g]&&overlayImgs[g][anim]&&overlayImgs[g][anim][idx];
    if(ov) ctx.drawImage(ov,0,0);
  });
  // Apply border overlay(s)
  const applyBorder=(key)=>{
    const ov=overlayImgs[key]&&overlayImgs[key][anim]&&overlayImgs[key][anim][idx];
    if(ov) ctx.drawImage(ov,0,0);
  };
  if(activeBorder==='__merged__'&&mergedBorder){
    applyBorder('shape_'+mergedBorder.b1);
    applyBorder('shape_'+mergedBorder.b2);
  } else if(activeBorder&&activeBorder!==''){
    applyBorder('shape_'+activeBorder);
  }
  return c;
}

function renderUI(skinId, themeName){
  Object.values(intervals).forEach(clearInterval); intervals={};
  const defs={attack:{label:'⚔️ Attack'},flying:{label:'🦅 Flying'},idle:{label:'🧍 Idle'}};
  let html=`<div class="ph"><div><div class="sname">${themeName}</div><div class="sid">ID: ${skinId}</div></div></div><div class="anims">`;
  ANIMS.forEach(anim=>{
    const n=baseFrames[anim]?baseFrames[anim].length:0;
    html+=`<div class="ab"><div class="at">${defs[anim].label} · ${n} frames · ${FPS[anim]} FPS</div>
    <div class="strip" id="strip_${anim}"></div>
    <div class="bigp"><canvas id="big_${anim}" width="376" height="312"></canvas></div></div>`;
  });
  html+='</div>';
  document.getElementById('preview').innerHTML=html;

  // Build strip thumbnails
  ANIMS.forEach(anim=>{
    const strip=document.getElementById('strip_'+anim);
    const n=baseFrames[anim]?baseFrames[anim].length:0;
    for(let i=0;i<n;i++){
      const c=document.createElement('canvas');
      c.width=376; c.height=312; c.className=(i===0?'active':'');
      c.onclick=(()=>{const idx=i; return ()=>pickFrame(anim,idx);})();
      strip.appendChild(c);
    }
    drawAllStrip(anim);
  });

  startAnims();
}

function drawAllStrip(anim){
  const strip=document.getElementById('strip_'+anim);
  if(!strip) return;
  const canvases=strip.querySelectorAll('canvas');
  canvases.forEach((c,i)=>{
    const comp=compositeFrame(anim,i);
    if(comp){ const ctx=c.getContext('2d'); ctx.clearRect(0,0,c.width,c.height); ctx.drawImage(comp,0,0); }
  });
}

function drawBig(anim, idx){
  const big=document.getElementById('big_'+anim);
  if(!big) return;
  const comp=compositeFrame(anim,idx);
  if(comp){ const ctx=big.getContext('2d'); ctx.clearRect(0,0,big.width,big.height); ctx.drawImage(comp,0,0); }
}

function pickFrame(anim, idx){
  drawBig(anim,idx);
  const strip=document.getElementById('strip_'+anim);
  if(strip) strip.querySelectorAll('canvas').forEach((c,i)=>c.classList.toggle('active',i===idx));
}

let animIdxs={attack:0,flying:0,idle:0};
let animDirs={attack:1,flying:1,idle:1};

function startAnims(){
  Object.values(intervals).forEach(clearInterval); intervals={};
  ANIMS.forEach(anim=>{
    animIdxs[anim]=0; animDirs[anim]=1;
    const n=baseFrames[anim]?baseFrames[anim].length:0;
    if(n===0) return;
    intervals[anim]=setInterval(()=>{
      const pp=pingpong && anim!=='attack';
      if(pp){
        animIdxs[anim]+=animDirs[anim];
        if(animIdxs[anim]>=n-1){animIdxs[anim]=n-1;animDirs[anim]=-1;}
        else if(animIdxs[anim]<=0){animIdxs[anim]=0;animDirs[anim]=1;}
      } else {
        animIdxs[anim]=(animIdxs[anim]+1)%n;
      }
      drawBig(anim,animIdxs[anim]);
      // Update strip active
      const strip=document.getElementById('strip_'+anim);
      if(strip) strip.querySelectorAll('canvas').forEach((c,i)=>c.classList.toggle('active',i===animIdxs[anim]));
    }, Math.round(1000/FPS[anim]));
  });
}

function toggleAnim(group){
  if(enabledGroups.has(group)) enabledGroups.delete(group);
  else enabledGroups.add(group);
  const sw=document.getElementById('sw_'+group);
  const ti=document.getElementById('ti_'+group);
  const on=enabledGroups.has(group);
  sw.className='toggle-switch'+(on?' on':'');
  ti.className='toggle-item'+(on?' active':'');
  // Redraw all frames instantly
  ANIMS.forEach(anim=>{ drawAllStrip(anim); drawBig(anim,animIdxs[anim]); });
}

function togglePP(){
  pingpong=!pingpong;
  document.getElementById('sw_pingpong').className='toggle-switch'+(pingpong?' on':'');
  document.getElementById('ti_pingpong').className='toggle-item'+(pingpong?' active':'');
  if(curId) startAnims();
}

function dl(){if(curId)window.location.href='/download/'+curId;}

function addHist(id,name){
  hist.unshift({id,name}); if(hist.length>10)hist.pop();
  const sec=document.getElementById('histSec'),grid=document.getElementById('hgrid');
  sec.style.display='block';
  grid.innerHTML=hist.map(h=>`<div class="hi" onclick="loadSkin('${h.id}')">${h.name}<span class="badge">${h.id.split('_')[1]}</span></div>`).join('');
}

function loadSkin(id){
  fetch('/skin/'+id).then(r=>r.json()).then(d=>{
    curId=id; baseFrames=d.base; overlayFrames=d.overlays;
    preloadAll(()=>{ renderUI(id,d.theme_name); document.getElementById('dlBtn').disabled=false; });
  });
}
</script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(HTML, themes=THEMES, sidebar_items=SIDEBAR_ITEMS)

@app.route("/generate")
def generate():
    theme = request.args.get("theme") or None
    seed = request.args.get("seed")
    seed = int(seed) if seed else None
    skin_id, theme_name, base, overlays = generate_skin(theme, seed)
    return jsonify({"skin_id": skin_id, "theme_name": theme_name, "base": base, "overlays": overlays})

@app.route("/skin/<skin_id>")
def get_skin(skin_id):
    from skin_designer import OUTPUT_DIR, FRAME_DATA, get_mask, recolor, add_cosmetics, draw_overlay_group, draw_shape_fx, THEMES
    skin_dir = os.path.join(OUTPUT_DIR, skin_id)
    # Just reload from saved files as base
    base = {}; overlays = {g:{} for g in ["head","eyes","body","scythe","robe","shape"]}
    for anim in ["attack","flying","idle"]:
        d = os.path.join(skin_dir, anim)
        base[anim] = []
        for g in overlays: overlays[g][anim] = []
        if os.path.exists(d):
            for f in sorted(os.listdir(d)):
                if f.endswith(".png"):
                    with open(os.path.join(d,f),"rb") as fh:
                        base[anim].append(base64.b64encode(fh.read()).decode())
                    for g in overlays: overlays[g][anim].append("")
    name = skin_id.rsplit("_",1)[0].replace("_"," ").title()
    return jsonify({"skin_id": skin_id, "theme_name": name, "base": base, "overlays": overlays})

@app.route("/download/<skin_id>")
def download(skin_id):
    buf = create_zip(skin_id)
    return send_file(buf, mimetype="application/zip", as_attachment=True, download_name=f"{skin_id}.zip")

@app.route("/webhook", methods=["POST"])
def webhook():
    """GitHub webhook — pulls latest code and reloads."""
    import subprocess, hmac, hashlib
    secret = b"evo_deploy_secret"
    sig = request.headers.get("X-Hub-Signature-256","")
    body = request.get_data()
    expected = "sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return "Forbidden", 403
    subprocess.Popen(["git", "-C", os.path.dirname(__file__), "pull", "origin", "main"])
    return "OK", 200

if __name__ == "__main__":
    print("🎭 AI Skin Maker v1.03 → http://localhost:5050")
    app.run(host="0.0.0.0", port=5050, debug=False)
