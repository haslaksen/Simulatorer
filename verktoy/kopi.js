// ⋯ ved simulatorens tittel kopierer tittel, ingress og lenke (pent, for Teams/OneNote). Settes inn av tema.py.
(function(){var h=document.querySelector(".lk-intro h1");if(!h)return;
var hint="Kopier tittel og lenke til simulatoren (for Teams eller OneNote)",lenke=location.origin+location.pathname.replace(/\.html$/,"").replace(/\/index$/,"/");
var st=document.createElement("style");st.textContent=".lk-kopi{margin-left:.3em;vertical-align:middle;font:700 22px/1 system-ui,sans-serif;color:inherit;background:none;border:0;border-radius:8px;padding:2px 8px;cursor:pointer;opacity:.45}.lk-kopi:hover,.lk-kopi:focus-visible{opacity:1;background:var(--lk-blue-soft)}.lk-kopi::before{content:attr(data-t)}@media print{.lk-kopi{display:none}}";document.head.appendChild(st);
var b=document.createElement("button");b.type="button";b.className="lk-kopi";b.dataset.t="⋯";b.title=hint;b.setAttribute("aria-label",hint);
function stil(el,px,ekstra){var cs=getComputedStyle(el);return "color:"+cs.color+";font-weight:"+cs.fontWeight+";text-transform:"+cs.textTransform+";letter-spacing:"+cs.letterSpacing+";font-size:"+px+"px;margin:0 0 6px;font-family:'Segoe UI',Calibri,Arial,sans-serif"+(ekstra||"");}
function esc(t){return t.replace(/&/g,"&amp;").replace(/</g,"&lt;");}
b.onclick=async function(e){e.preventDefault();var k=document.querySelector(".lk-intro .lk-kicker"),l=document.querySelector(".lk-intro .lk-lead"),navn=h.textContent.trim();
var html="<div style=\"font-family:'Segoe UI',Calibri,Arial,sans-serif\">"+(k?"<div style=\""+stil(k,13)+"\">"+esc(k.textContent.trim())+"</div>":"")+
"<h1 style=\""+stil(h,26)+"\">Simulator: "+esc(navn)+"</h1>"+(l?"<p style=\""+stil(l,15)+"\">"+esc(l.textContent.trim())+"</p>":"")+
"<p style=\"margin:8px 0 0;font-size:14px;font-family:'Segoe UI',Calibri,Arial,sans-serif\"><a href=\""+lenke+"\">"+lenke+"</a></p></div>";
try{await navigator.clipboard.write([new ClipboardItem({"text/html":new Blob([html],{type:"text/html"}),"text/plain":new Blob(["Simulator: "+navn+"\n"+lenke],{type:"text/plain"})})]);b.dataset.t="✓ Kopiert";}
catch(x){try{await navigator.clipboard.writeText(lenke);b.dataset.t="✓ Lenke kopiert";}catch(y){prompt("Kopier lenken:",lenke);}}
setTimeout(function(){b.dataset.t="⋯";},2000);};h.appendChild(b);})();
