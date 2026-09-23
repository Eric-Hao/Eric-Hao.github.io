/* Paper-inspired particle covers. Editorial geometry, not simulation output. */
(() => {
  const TAU = Math.PI * 2;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const hosts = [...document.querySelectorAll('.research-cover, .article-cover > a')]
    .filter(a => a.dataset.physics || /\/(magvortex|magknot|vortex)\.png$/.test(a.getAttribute('href')));
  const states = [];
  function geometry(kind, time) {
    const points = [];
    const add = (x,y,z,c,i) => points.push({x,y,z,c,i,uid:points.length});
    if (kind === 'magknot') {
      [3,5,7].forEach((q,k) => {
        // A single closed T(2,q) torus-knot centerline, thickened by particles.
        for (let j=0;j<900;j++) {
          const t=j/900*TAU + time*.09;
          const radius=.105+.040*Math.cos(q*t);
          for(let s=0;s<5;s++) {
            const a=s/5*TAU+j*2.4;
            add((k-1)*.320+radius*Math.cos(2*t)+.011*Math.cos(a),
              radius*Math.sin(2*t)+.011*Math.sin(a), .054*Math.sin(q*t), k%2,j+s);
          }
        }
      });
    } else if (kind === 'magvortex') {
      // Paper composition: braided orthogonal flux bundles + magnified local braid.
      for(let bundle=0;bundle<2;bundle++) for(let strand=0;strand<22;strand++) for(let j=0;j<230;j++) {
        const t=j/230*TAU+time*.07,phase=strand/22*TAU;
        const twist=phase+t*5+.25*Math.sin(t*3+phase);
        const rx=bundle?.285:.143,ry=bundle?.148:.315;
        const offset=.017*Math.cos(twist);
        add(-.14+(rx+offset)*Math.cos(t), (ry+offset)*Math.sin(t),
          .02*Math.sin(twist)+(bundle?.022*Math.sin(t):.035*Math.cos(t)),strand%3,j);
      }
      for(let strand=0;strand<30;strand++) for(let j=0;j<160;j++) {
        const u=((j/160+time*.025)%1),a=strand/30*TAU+u*TAU*1.8;
        add(.343+.045*Math.sin(a)+.008*Math.sin(u*13+strand), (u-.5)*.57,
          .015*Math.cos(a),strand%3,j);
      }
    } else {
      // Trace the silhouette and endpoint positions of paper Figure 2 (1100 × 596).
      const bez=(p,t)=>{const v=1-t;return [0,1].map(d=>v*v*v*p[0][d]+3*v*v*t*p[1][d]+3*v*t*t*p[2][d]+t*t*t*p[3][d]);};
      const emit=(x,y,c,id,z=0)=>add((x/1100-.5)*.98,(y/596-.5)*.69,z,c,id);
      const surfaces=[
        {left:[[164,450],[204,285],[284,185],[384,130]],right:[[281,471],[302,301],[365,222],[429,160]],c:2},
        {left:[[735,501],[770,352],[842,198],[950,100]],right:[[840,514],[864,357],[919,217],[1003,117]],c:0},
        {left:[[710,436],[737,291],[787,206],[861,145]],right:[[898,470],[910,332],[949,241],[982,192]],c:1}
      ];
      surfaces.forEach((surface,k)=>{
        for(let j=0;j<165;j++)for(let n=0;n<40;n++){
          const u=(j/165+time*.025)%1;
          // The blue virtual surface occludes the middle of the red physical tube.
          const occluded=k===1 && u>.14 && u<.84;
          const left=bez(surface.left,u),right=bez(surface.right,u),v=n/39;
          emit(left[0]*(1-v)+right[0]*v,left[1]*(1-v)+right[1]*v,
            surface.c,j*40+n,k*.002);
          points[points.length-1].opacity=occluded?.12:k===0?.55:1;
        }
        // Elliptical openings reproduce the tilted end rims in the source drawing.
        for(const end of [0,1])for(let j=0;j<260;j++){
          const l=bez(surface.left,end),r=bez(surface.right,end),t=j/260*TAU+time*.09;
          const v=(1+Math.cos(t))/2;
          emit(l[0]*(1-v)+r[0]*v,l[1]*(1-v)+r[1]*v+Math.sin(t)*(k===2?16:13),surface.c,j,.01);
        }
      });
      const paths=[
        {p:[[384,130],[562,8],[761,34],[950,100]],c:0},
        {p:[[384,130],[526,17],[619,159],[861,145]],c:1},
        {p:[[164,450],[385,344],[499,535],[710,436]],c:1},
        {p:[[164,450],[411,338],[482,641],[735,501]],c:0}
      ];
      paths.forEach((path,k)=>{for(let j=0;j<380;j++){
        const u=(j/380+time*.043)%1,xy=bez(path.p,u);emit(xy[0],xy[1],path.c,j,.015);
      }});
      // Vorticity-tangent particle tracks on the initial surface.
      for(let strand=0;strand<3;strand++)for(let j=0;j<310;j++){
        const u=(j/310+time*.04)%1,l=bez(surfaces[0].left,u),r=bez(surfaces[0].right,u),v=.23+strand*.24;
        emit(l[0]*(1-v)+r[0]*v,l[1]*(1-v)+r[1]*v,2,j,.02);
      }
    }
    return points;
  }
  const hash = n => { const x=Math.sin(n*127.1+311.7)*43758.5453;return x-Math.floor(x); };
  // Pre-render bloom once, rather than applying an expensive blur per particle.
  const sprites=['#9bd9ff','#ffd0a4','#f4faff'].map(color=>{
    const c=document.createElement('canvas');c.width=c.height=64;
    const g=c.getContext('2d'),glow=g.createRadialGradient(32,32,0,32,32,32);
    glow.addColorStop(0,'#ffffff');glow.addColorStop(.07,color);
    glow.addColorStop(.18,color+'a0');glow.addColorStop(.48,color+'25');glow.addColorStop(1,color+'00');
    g.fillStyle=glow;g.fillRect(0,0,64,64);return c;
  });
  function draw(s,time) {
    const {ctx,w,h}=s; if(!w||!h)return;
    ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;
    ctx.fillStyle='#060e14';ctx.fillRect(0,0,w,h);
    if(s.kind!=='vortex'){
    const haze=ctx.createRadialGradient(w*.52,h*.52,0,w*.52,h*.52,w*.62);
    haze.addColorStop(0,'#112534');haze.addColorStop(1,'#060e14');ctx.fillStyle=haze;ctx.fillRect(0,0,w,h);
    }
    for(let i=0;i<165;i++) {
      ctx.globalAlpha=.12+hash(i+93)*.4;ctx.fillStyle=i%7===0?'#eeb58c':'#82bcda';
      const size=Math.max(.45,w/1400)*(1+hash(i+14));
      ctx.fillRect(hash(i+5)*w,hash(i+600)*h,size,size);
    }
    const angle=s.kind==='magknot'?.12*Math.sin(time*.10)+s.mouse*.17:0;
    const pitch=s.kind==='magknot'?.10:0;
    const points=geometry(s.kind,time).map(p=>{
      const y=p.y*Math.cos(pitch)-p.z*Math.sin(pitch), z=p.y*Math.sin(pitch)+p.z*Math.cos(pitch);
      return {...p,x:p.x*Math.cos(angle)+z*Math.sin(angle),y,z:z*Math.cos(angle)-p.x*Math.sin(angle)};
    }).sort((a,b)=>a.z-b.z);
    ctx.globalCompositeOperation='lighter';
    for(const p of points) {
      const scale=s.kind==='vortex'?1:1/(1-p.z*.65),seed=p.uid*3+p.c*149;
      const scatter=hash(seed+10),jitter=(scatter-.5)*.003;
      const x=w*(.5+(p.x+jitter)*scale), y=h*(.5+(p.y+jitter)*scale);
      const depth=Math.max(.24,Math.min(1,.65+p.z));
      const pulse=.78+.22*Math.sin(hash(seed+9)*TAU+time*.65);
      const color=s.kind==='magknot'?(hash(seed+1)<.17?1:hash(seed+2)<.40?2:0):(p.c===0?1:p.c===1?0:2);
      const bright=hash(seed+3)>(s.kind==='magknot'?.976:.990);
      ctx.globalAlpha=depth*pulse*(bright?1:.50+scatter*.5)*(p.opacity??1);
      const radius=(bright ? w/420*(.7+scatter) : Math.max(.55,w/850)*(.45+hash(seed+4)*1.35))*(1+p.z*.6);
      if(bright) {
        const diameter=radius*(9+hash(seed+20)*7);
        ctx.drawImage(sprites[color],x-diameter/2,y-diameter/2,diameter,diameter);
      } else {
        ctx.fillStyle=['#8dccf2','#f4aa75','#e7f5ff'][color];
        ctx.beginPath();ctx.arc(x,y,radius,0,TAU);ctx.fill();
      }
    }
    ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;
    // Sparse diagram guides preserve the zoom relation and directional interpretation.
    ctx.lineWidth=Math.max(1,w/1000);
    if(s.kind==='magvortex') {
      ctx.strokeStyle='#92b7ca80';ctx.setLineDash([w*.006,w*.006]);
      ctx.strokeRect(w*.46,h*.36,w*.052,h*.23);
      ctx.strokeRect(w*.785,h*.195,w*.115,h*.61);ctx.setLineDash([]);
      ctx.beginPath();ctx.moveTo(w*.512,h*.41);ctx.bezierCurveTo(w*.63,h*.34,w*.65,h*.49,w*.785,h*.40);ctx.stroke();
    }
    ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;
  }
  hosts.forEach(host=>{
    const canvas=document.createElement('canvas');canvas.className='physics-particles';canvas.setAttribute('aria-hidden','true');
    const ctx=canvas.getContext('2d');if(!ctx)return;
    host.append(canvas);host.classList.add('particle-cover');
    const s={host,canvas,ctx,kind:host.dataset.physics || host.getAttribute('href').match(/(magvortex|magknot|vortex)\.png$/)[1],w:0,h:0,mouse:0,visible:false,paused:false,time:0};states.push(s);
    new ResizeObserver(()=>{
      const size=host.getBoundingClientRect();const dpr=Math.min(devicePixelRatio||1,2);
      canvas.width=Math.round(size.width*dpr);canvas.height=Math.round(size.height*dpr);s.w=canvas.width;s.h=canvas.height;draw(s,s.time);
    }).observe(host);
    new IntersectionObserver(entries=>{s.visible=entries[0].isIntersecting;},{rootMargin:'80px'}).observe(host);
    host.addEventListener('pointermove',e=>{const r=host.getBoundingClientRect();s.mouse=(e.clientX-r.left)/r.width-.5;});
    host.addEventListener('pointerleave',()=>{s.mouse=0;});
  });
  let previous=0;
  function tick(now){
    if(now-previous<32){requestAnimationFrame(tick);return;}
    const dt=Math.min((now-previous)/1000,.05);previous=now;
    if(!document.hidden&&!reduced.matches) for(const s of states)if(s.visible&&!s.paused){s.time+=dt;draw(s,s.time);}
    requestAnimationFrame(tick);
  }
  if(states.length)requestAnimationFrame(tick);
})();
