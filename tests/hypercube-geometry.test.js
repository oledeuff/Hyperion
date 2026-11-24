import assert from 'node:assert/strict';
import test from 'node:test';
import {vertices4D,edges,primaryNodes,projectVertices,screenPoint,hitNode,edgeTriangles} from '../docs/assets/hypercube-geometry.js';

test('the tesseract retains sixteen vertices, thirty-two edges and four neighbours per vertex',()=>{
  assert.equal(vertices4D.length,16);assert.equal(edges.length,32);
  for(let vertex=0;vertex<16;vertex++)assert.equal(edges.filter(e=>e.includes(vertex)).length,4);
  assert.equal(edges.filter(([a,b])=>a<8&&b<8).length,12);
  assert.equal(edges.filter(([a,b])=>a>=8&&b>=8).length,12);
  assert.equal(edges.filter(([a,b])=>(a<8)!==(b<8)).length,8);
});
test('the automatic movement keeps both cubes within the view at mobile and desktop ratios',()=>{
  for(const aspect of [.8,1,1.5,2.2])for(let phase=0;phase<20;phase+=.25){
    const points=projectVertices({aspect,phase});
    assert.ok(points.flat().every(Number.isFinite));
    assert.ok(points.every(p=>Math.abs(p[0])<.98&&Math.abs(p[1])<.98));
    const radius=list=>Math.max(...list.map(p=>Math.hypot(p[0],p[1])));
    assert.ok(radius(points.slice(8))<radius(points.slice(0,8))*.65);
  }
});
test('each coloured point selects its own real destination, including nearby clicks',()=>{
  for(const [width,height] of [[800,470],[340,320]]){
    const points=projectVertices({aspect:width/height});
    for(const node of primaryNodes){
      const [x,y]=screenPoint(points[node.vertex],width,height);
      assert.equal(hitNode(points,x,y,width,height),node.entry);
      assert.equal(hitNode(points,x+4,y+3,width,height),node.entry);
    }
    assert.equal(hitNode(points,0,0,width,height),-1);
  }
});
test('triangulated edges preserve a visible three-pixel width rather than a one-pixel GL line',()=>{
  const points=projectVertices();
  for(const [a,b] of edges){
    const triangles=edgeTriangles(points[a],points[b],800,470,3);
    assert.equal(triangles.length,6);assert.ok(triangles.flat().every(Number.isFinite));
    const [x1,y1]=screenPoint(triangles[0],800,470),[x2,y2]=screenPoint(triangles[1],800,470);
    assert.ok(Math.abs(Math.hypot(x1-x2,y1-y2)-3)<.001);
  }
});
