/* A fixed 4D perspective keeps two recognisable cubes as the view moves. */
export const vertices4D = Array.from({length:16},(_,i)=>[0,1,2,3].map(bit=>i&(1<<bit)?1:-1));
export const edges=[];
for(let i=0;i<16;i++) for(let bit=0;bit<4;bit++) {const j=i^(1<<bit);if(i<j)edges.push([i,j]);}
export const primaryNodes=[
  {vertex:0,entry:0},{vertex:1,entry:1},{vertex:3,entry:2},
  {vertex:4,entry:3},{vertex:6,entry:6},{vertex:7,entry:8},
];
export function projectVertices({phase=0,yaw=0,pitch=0,aspect=800/470}={}) {
  const ya=.58+yaw+.12*Math.sin(phase),xa=-.33+pitch+.075*Math.sin(phase*.7);
  const fit=Math.min(1,aspect/1.2);
  const points=vertices4D.map(p=>{
    const scale=1.8/(2.45+p[3]);
    const [x,y,z]=p.slice(0,3).map(n=>n*scale);
    const xr=x*Math.cos(ya)-z*Math.sin(ya),zr=x*Math.sin(ya)+z*Math.cos(ya);
    const yr=y*Math.cos(xa)-zr*Math.sin(xa),zz=y*Math.sin(xa)+zr*Math.cos(xa);
    const perspective=2.4/(4.8-zz);
    return [xr*perspective*fit/aspect,yr*perspective*fit,-zz/10];
  });
  const extent=Math.max(...points.flatMap(p=>[Math.abs(p[0]),Math.abs(p[1])]));
  const safeScale=Math.min(1,.86/extent);
  return points.map(p=>[p[0]*safeScale,p[1]*safeScale,p[2]]);
}
export function screenPoint(p,width,height) {return [(p[0]+1)*width/2,(1-p[1])*height/2];}
export function hitNode(points,x,y,width,height,radius=26) {
  let found=-1,best=radius;
  for(const node of primaryNodes){const [px,py]=screenPoint(points[node.vertex],width,height);const d=Math.hypot(px-x,py-y);if(d<best){found=node.entry;best=d;}}
  return found;
}
export function edgeTriangles(a,b,width,height,thickness=2.7) {
  const [ax,ay]=screenPoint(a,width,height),[bx,by]=screenPoint(b,width,height);
  const len=Math.hypot(bx-ax,by-ay)||1;
  const ox=-(by-ay)/len*thickness/width,oy=-(bx-ax)/len*thickness/height;
  const left=p=>[p[0]+ox,p[1]+oy,p[2]],right=p=>[p[0]-ox,p[1]-oy,p[2]];
  return [left(a),right(a),left(b),left(b),right(a),right(b)];
}
