// Same equations as orifice_tank/core.py (SI units). Level L = water height above the orifice bottom edge.
const G=9.81,CV=0.98;
function geom(sh,a,b){let H,w,yc;
 if(sh==='circle'){const r=a/2;H=a;yc=r;w=s=>2*Math.sqrt(Math.max(r*r-(s-r)*(s-r),0));}
 else if(sh==='square'){H=a;yc=a/2;w=()=>a;}
 else if(sh==='rectangle'){H=b;yc=b/2;w=()=>a;}
 else{H=b;yc=b/3;w=s=>a*(1-s/b);}
 return{H,w,yc};}
function flow(L,g,cd,n=120){const top=Math.min(L,g.H);if(top<=0)return{q:0,A:0};
 const ds=top/n;let q=0,A=0;
 for(let i=0;i<n;i++){const s=(i+.5)*ds,w=g.w(s);q+=w*Math.sqrt(2*G*(L-s));A+=w;}
 return{q:cd*q*ds,A:A*ds};}
function drain(L0,D,g,cd){const at=Math.PI*D*D/4,Lmin=Math.max(.02*g.H,.001),T=[0],Ls=[L0];let t=0,L=L0;
 while(L>Lmin&&T.length<5000){const q=flow(L,g,cd,60).q,dt=.01*L*at/q;
  const qm=flow(Math.max(L-.5*dt*q/at,1e-9),g,cd,60).q;L-=dt*qm/at;t+=dt;T.push(t);Ls.push(Math.max(L,0));}
 return{T,L:Ls};}
function levelAt(sim,t){const T=sim.T,Ls=sim.L;if(t>=T[T.length-1])return Ls[Ls.length-1];
 let lo=0,hi=T.length-1;while(hi-lo>1){const m=(lo+hi)>>1;if(T[m]<=t)lo=m;else hi=m;}
 return Ls[lo]+(t-T[lo])/(T[hi]-T[lo])*(Ls[hi]-Ls[lo]);}
function fmtT(s){return s<90?s.toFixed(1)+' s':s<5400?(s/60).toFixed(1)+' min':(s/3600).toFixed(2)+' h';}
