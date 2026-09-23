const svg=document.querySelector('#field');
const ns='http://www.w3.org/2000/svg';
for(let i=0;i<40;i++){
 const path=document.createElementNS(ns,'path');let d='';
 for(let t=0;t<=160;t++){const a=t/160*Math.PI*2, v=i/39;const x=220+(100+46*Math.cos(a*3+v*3))*Math.cos(a)+34*Math.sin(v*6.28);const y=192+(94+30*Math.cos(a*3+v*3))*Math.sin(a)*(.5+v*.5)+50*Math.cos(v*3.14);d+=(t?'L':'M')+x.toFixed(2)+','+y.toFixed(2);}
 path.setAttribute('d',d+'Z');path.setAttribute('fill','none');path.setAttribute('stroke',i%5===0?'#6f7e5e':'#8f997c');path.setAttribute('stroke-width','.65');path.setAttribute('opacity','.7');svg.appendChild(path);
}
