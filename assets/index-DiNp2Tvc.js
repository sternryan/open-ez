(function(){let e=document.createElement(`link`).relList;if(e&&e.supports&&e.supports(`modulepreload`))return;for(let e of document.querySelectorAll(`link[rel="modulepreload"]`))n(e);new MutationObserver(e=>{for(let t of e)if(t.type===`childList`)for(let e of t.addedNodes)e.tagName===`LINK`&&e.rel===`modulepreload`&&n(e)}).observe(document,{childList:!0,subtree:!0});function t(e){let t={};return e.integrity&&(t.integrity=e.integrity),e.referrerPolicy&&(t.referrerPolicy=e.referrerPolicy),t.credentials=e.crossOrigin===`use-credentials`?`include`:e.crossOrigin===`anonymous`?`omit`:`same-origin`,t}function n(e){if(e.ep)return;e.ep=!0;let n=t(e);fetch(e.href,n)}})();var e={LEFT:0,MIDDLE:1,RIGHT:2,ROTATE:0,DOLLY:1,PAN:2},t={ROTATE:0,PAN:1,DOLLY_PAN:2,DOLLY_ROTATE:3},n=`attached`,r=1e3,i=1001,a=1002,o=1003,s=1004,c=1005,l=1006,u=1007,d=1008,f=1009,p=1010,m=1011,h=1012,g=1013,_=1014,v=1015,y=1016,b=1017,x=1018,S=1020,C=35902,w=35899,T=1021,E=1022,D=1023,O=1026,k=1027,A=1028,ee=1029,te=1030,j=1031,ne=1033,M=33776,N=33777,re=33778,ie=33779,ae=35840,oe=35841,se=35842,ce=35843,le=36196,P=37492,ue=37496,de=37488,fe=37489,pe=37490,me=37491,F=37808,he=37809,ge=37810,_e=37811,ve=37812,ye=37813,be=37814,xe=37815,Se=37816,Ce=37817,we=37818,Te=37819,Ee=37820,De=37821,Oe=36492,ke=36494,Ae=36495,je=36283,Me=36284,I=36285,Ne=36286,Pe=2300,Fe=2301,L=2302,Ie=2303,Le=2400,Re=2401,ze=2402,Be=2500,Ve=3200,He=3201,Ue=`srgb`,We=`srgb-linear`,Ge=`linear`,Ke=`srgb`,qe=7680,Je=35044,R=2e3;function z(e){for(let t=e.length-1;t>=0;--t)if(e[t]>=65535)return!0;return!1}function Ye(e){return ArrayBuffer.isView(e)&&!(e instanceof DataView)}function Xe(e){return document.createElementNS(`http://www.w3.org/1999/xhtml`,e)}function Ze(){let e=Xe(`canvas`);return e.style.display=`block`,e}var Qe={};function $e(...e){let t=`THREE.`+e.shift();console.log(t,...e)}function et(e){let t=e[0];if(typeof t==`string`&&t.startsWith(`TSL:`)){let t=e[1];t&&t.isStackTrace?e[0]+=` `+t.getLocation():e[1]=`Stack trace not available. Enable "THREE.Node.captureStackTrace" to capture stack traces.`}return e}function B(...e){e=et(e);let t=`THREE.`+e.shift();{let n=e[0];n&&n.isStackTrace?console.warn(n.getError(t)):console.warn(t,...e)}}function V(...e){e=et(e);let t=`THREE.`+e.shift();{let n=e[0];n&&n.isStackTrace?console.error(n.getError(t)):console.error(t,...e)}}function tt(...e){let t=e.join(` `);t in Qe||(Qe[t]=!0,B(...e))}function nt(e,t,n){return new Promise(function(r,i){function a(){switch(e.clientWaitSync(t,e.SYNC_FLUSH_COMMANDS_BIT,0)){case e.WAIT_FAILED:i();break;case e.TIMEOUT_EXPIRED:setTimeout(a,n);break;default:r()}}setTimeout(a,n)})}var rt={0:1,2:6,4:7,3:5,1:0,6:2,7:4,5:3},it=class{addEventListener(e,t){this._listeners===void 0&&(this._listeners={});let n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){let n=this._listeners;return n!==void 0&&n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){let n=this._listeners;if(n===void 0)return;let r=n[e];if(r!==void 0){let e=r.indexOf(t);e!==-1&&r.splice(e,1)}}dispatchEvent(e){let t=this._listeners;if(t===void 0)return;let n=t[e.type];if(n!==void 0){e.target=this;let t=n.slice(0);for(let n=0,r=t.length;n<r;n++)t[n].call(this,e);e.target=null}}},at=`00.01.02.03.04.05.06.07.08.09.0a.0b.0c.0d.0e.0f.10.11.12.13.14.15.16.17.18.19.1a.1b.1c.1d.1e.1f.20.21.22.23.24.25.26.27.28.29.2a.2b.2c.2d.2e.2f.30.31.32.33.34.35.36.37.38.39.3a.3b.3c.3d.3e.3f.40.41.42.43.44.45.46.47.48.49.4a.4b.4c.4d.4e.4f.50.51.52.53.54.55.56.57.58.59.5a.5b.5c.5d.5e.5f.60.61.62.63.64.65.66.67.68.69.6a.6b.6c.6d.6e.6f.70.71.72.73.74.75.76.77.78.79.7a.7b.7c.7d.7e.7f.80.81.82.83.84.85.86.87.88.89.8a.8b.8c.8d.8e.8f.90.91.92.93.94.95.96.97.98.99.9a.9b.9c.9d.9e.9f.a0.a1.a2.a3.a4.a5.a6.a7.a8.a9.aa.ab.ac.ad.ae.af.b0.b1.b2.b3.b4.b5.b6.b7.b8.b9.ba.bb.bc.bd.be.bf.c0.c1.c2.c3.c4.c5.c6.c7.c8.c9.ca.cb.cc.cd.ce.cf.d0.d1.d2.d3.d4.d5.d6.d7.d8.d9.da.db.dc.dd.de.df.e0.e1.e2.e3.e4.e5.e6.e7.e8.e9.ea.eb.ec.ed.ee.ef.f0.f1.f2.f3.f4.f5.f6.f7.f8.f9.fa.fb.fc.fd.fe.ff`.split(`.`),ot=1234567,st=Math.PI/180,ct=180/Math.PI;function lt(){let e=Math.random()*4294967295|0,t=Math.random()*4294967295|0,n=Math.random()*4294967295|0,r=Math.random()*4294967295|0;return(at[e&255]+at[e>>8&255]+at[e>>16&255]+at[e>>24&255]+`-`+at[t&255]+at[t>>8&255]+`-`+at[t>>16&15|64]+at[t>>24&255]+`-`+at[n&63|128]+at[n>>8&255]+`-`+at[n>>16&255]+at[n>>24&255]+at[r&255]+at[r>>8&255]+at[r>>16&255]+at[r>>24&255]).toLowerCase()}function H(e,t,n){return Math.max(t,Math.min(n,e))}function ut(e,t){return(e%t+t)%t}function dt(e,t,n,r,i){return r+(e-t)*(i-r)/(n-t)}function ft(e,t,n){return e===t?0:(n-e)/(t-e)}function pt(e,t,n){return(1-n)*e+n*t}function mt(e,t,n,r){return pt(e,t,1-Math.exp(-n*r))}function ht(e,t=1){return t-Math.abs(ut(e,t*2)-t)}function gt(e,t,n){return e<=t?0:e>=n?1:(e=(e-t)/(n-t),e*e*(3-2*e))}function _t(e,t,n){return e<=t?0:e>=n?1:(e=(e-t)/(n-t),e*e*e*(e*(e*6-15)+10))}function vt(e,t){return e+Math.floor(Math.random()*(t-e+1))}function yt(e,t){return e+Math.random()*(t-e)}function bt(e){return e*(.5-Math.random())}function xt(e){e!==void 0&&(ot=e);let t=ot+=1831565813;return t=Math.imul(t^t>>>15,t|1),t^=t+Math.imul(t^t>>>7,t|61),((t^t>>>14)>>>0)/4294967296}function St(e){return e*st}function Ct(e){return e*ct}function wt(e){return!(e&e-1)&&e!==0}function Tt(e){return 2**Math.ceil(Math.log(e)/Math.LN2)}function Et(e){return 2**Math.floor(Math.log(e)/Math.LN2)}function Dt(e,t,n,r,i){let a=Math.cos,o=Math.sin,s=a(n/2),c=o(n/2),l=a((t+r)/2),u=o((t+r)/2),d=a((t-r)/2),f=o((t-r)/2),p=a((r-t)/2),m=o((r-t)/2);switch(i){case`XYX`:e.set(s*u,c*d,c*f,s*l);break;case`YZY`:e.set(c*f,s*u,c*d,s*l);break;case`ZXZ`:e.set(c*d,c*f,s*u,s*l);break;case`XZX`:e.set(s*u,c*m,c*p,s*l);break;case`YXY`:e.set(c*p,s*u,c*m,s*l);break;case`ZYZ`:e.set(c*m,c*p,s*u,s*l);break;default:B(`MathUtils: .setQuaternionFromProperEuler() encountered an unknown order: `+i)}}function Ot(e,t){switch(t.constructor){case Float32Array:return e;case Uint32Array:return e/4294967295;case Uint16Array:return e/65535;case Uint8Array:return e/255;case Int32Array:return Math.max(e/2147483647,-1);case Int16Array:return Math.max(e/32767,-1);case Int8Array:return Math.max(e/127,-1);default:throw Error(`THREE.MathUtils: Invalid component type.`)}}function kt(e,t){switch(t.constructor){case Float32Array:return e;case Uint32Array:return Math.round(e*4294967295);case Uint16Array:return Math.round(e*65535);case Uint8Array:return Math.round(e*255);case Int32Array:return Math.round(e*2147483647);case Int16Array:return Math.round(e*32767);case Int8Array:return Math.round(e*127);default:throw Error(`THREE.MathUtils: Invalid component type.`)}}var At={DEG2RAD:st,RAD2DEG:ct,generateUUID:lt,clamp:H,euclideanModulo:ut,mapLinear:dt,inverseLerp:ft,lerp:pt,damp:mt,pingpong:ht,smoothstep:gt,smootherstep:_t,randInt:vt,randFloat:yt,randFloatSpread:bt,seededRandom:xt,degToRad:St,radToDeg:Ct,isPowerOfTwo:wt,ceilPowerOfTwo:Tt,floorPowerOfTwo:Et,setQuaternionFromProperEuler:Dt,normalize:kt,denormalize:Ot},U=class e{static{e.prototype.isVector2=!0}constructor(e=0,t=0){this.x=e,this.y=t}get width(){return this.x}set width(e){this.x=e}get height(){return this.y}set height(e){this.y=e}set(e,t){return this.x=e,this.y=t,this}setScalar(e){return this.x=e,this.y=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;default:throw Error(`THREE.Vector2: index is out of range: `+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;default:throw Error(`THREE.Vector2: index is out of range: `+e)}}clone(){return new this.constructor(this.x,this.y)}copy(e){return this.x=e.x,this.y=e.y,this}add(e){return this.x+=e.x,this.y+=e.y,this}addScalar(e){return this.x+=e,this.y+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this}subScalar(e){return this.x-=e,this.y-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this}multiply(e){return this.x*=e.x,this.y*=e.y,this}multiplyScalar(e){return this.x*=e,this.y*=e,this}divide(e){return this.x/=e.x,this.y/=e.y,this}divideScalar(e){return this.multiplyScalar(1/e)}applyMatrix3(e){let t=this.x,n=this.y,r=e.elements;return this.x=r[0]*t+r[3]*n+r[6],this.y=r[1]*t+r[4]*n+r[7],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this}clamp(e,t){return this.x=H(this.x,e.x,t.x),this.y=H(this.y,e.y,t.y),this}clampScalar(e,t){return this.x=H(this.x,e,t),this.y=H(this.y,e,t),this}clampLength(e,t){let n=this.length();return this.divideScalar(n||1).multiplyScalar(H(n,e,t))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(e){return this.x*e.x+this.y*e.y}cross(e){return this.x*e.y-this.y*e.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(e){let t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;let n=this.dot(e)/t;return Math.acos(H(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){let t=this.x-e.x,n=this.y-e.y;return t*t+n*n}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this}equals(e){return e.x===this.x&&e.y===this.y}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this}rotateAround(e,t){let n=Math.cos(t),r=Math.sin(t),i=this.x-e.x,a=this.y-e.y;return this.x=i*n-a*r+e.x,this.y=i*r+a*n+e.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}},jt=class{constructor(e=0,t=0,n=0,r=1){this.isQuaternion=!0,this._x=e,this._y=t,this._z=n,this._w=r}static slerpFlat(e,t,n,r,i,a,o){let s=n[r+0],c=n[r+1],l=n[r+2],u=n[r+3],d=i[a+0],f=i[a+1],p=i[a+2],m=i[a+3];if(u!==m||s!==d||c!==f||l!==p){let e=s*d+c*f+l*p+u*m;e<0&&(d=-d,f=-f,p=-p,m=-m,e=-e);let t=1-o;if(e<.9995){let n=Math.acos(e),r=Math.sin(n);t=Math.sin(t*n)/r,o=Math.sin(o*n)/r,s=s*t+d*o,c=c*t+f*o,l=l*t+p*o,u=u*t+m*o}else{s=s*t+d*o,c=c*t+f*o,l=l*t+p*o,u=u*t+m*o;let e=1/Math.sqrt(s*s+c*c+l*l+u*u);s*=e,c*=e,l*=e,u*=e}}e[t]=s,e[t+1]=c,e[t+2]=l,e[t+3]=u}static multiplyQuaternionsFlat(e,t,n,r,i,a){let o=n[r],s=n[r+1],c=n[r+2],l=n[r+3],u=i[a],d=i[a+1],f=i[a+2],p=i[a+3];return e[t]=o*p+l*u+s*f-c*d,e[t+1]=s*p+l*d+c*u-o*f,e[t+2]=c*p+l*f+o*d-s*u,e[t+3]=l*p-o*u-s*d-c*f,e}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get w(){return this._w}set w(e){this._w=e,this._onChangeCallback()}set(e,t,n,r){return this._x=e,this._y=t,this._z=n,this._w=r,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(e){return this._x=e.x,this._y=e.y,this._z=e.z,this._w=e.w,this._onChangeCallback(),this}setFromEuler(e,t=!0){let n=e._x,r=e._y,i=e._z,a=e._order,o=Math.cos,s=Math.sin,c=o(n/2),l=o(r/2),u=o(i/2),d=s(n/2),f=s(r/2),p=s(i/2);switch(a){case`XYZ`:this._x=d*l*u+c*f*p,this._y=c*f*u-d*l*p,this._z=c*l*p+d*f*u,this._w=c*l*u-d*f*p;break;case`YXZ`:this._x=d*l*u+c*f*p,this._y=c*f*u-d*l*p,this._z=c*l*p-d*f*u,this._w=c*l*u+d*f*p;break;case`ZXY`:this._x=d*l*u-c*f*p,this._y=c*f*u+d*l*p,this._z=c*l*p+d*f*u,this._w=c*l*u-d*f*p;break;case`ZYX`:this._x=d*l*u-c*f*p,this._y=c*f*u+d*l*p,this._z=c*l*p-d*f*u,this._w=c*l*u+d*f*p;break;case`YZX`:this._x=d*l*u+c*f*p,this._y=c*f*u+d*l*p,this._z=c*l*p-d*f*u,this._w=c*l*u-d*f*p;break;case`XZY`:this._x=d*l*u-c*f*p,this._y=c*f*u-d*l*p,this._z=c*l*p+d*f*u,this._w=c*l*u+d*f*p;break;default:B(`Quaternion: .setFromEuler() encountered an unknown order: `+a)}return t===!0&&this._onChangeCallback(),this}setFromAxisAngle(e,t){let n=t/2,r=Math.sin(n);return this._x=e.x*r,this._y=e.y*r,this._z=e.z*r,this._w=Math.cos(n),this._onChangeCallback(),this}setFromRotationMatrix(e){let t=e.elements,n=t[0],r=t[4],i=t[8],a=t[1],o=t[5],s=t[9],c=t[2],l=t[6],u=t[10],d=n+o+u;if(d>0){let e=.5/Math.sqrt(d+1);this._w=.25/e,this._x=(l-s)*e,this._y=(i-c)*e,this._z=(a-r)*e}else if(n>o&&n>u){let e=2*Math.sqrt(1+n-o-u);this._w=(l-s)/e,this._x=.25*e,this._y=(r+a)/e,this._z=(i+c)/e}else if(o>u){let e=2*Math.sqrt(1+o-n-u);this._w=(i-c)/e,this._x=(r+a)/e,this._y=.25*e,this._z=(s+l)/e}else{let e=2*Math.sqrt(1+u-n-o);this._w=(a-r)/e,this._x=(i+c)/e,this._y=(s+l)/e,this._z=.25*e}return this._onChangeCallback(),this}setFromUnitVectors(e,t){let n=e.dot(t)+1;return n<1e-8?(n=0,Math.abs(e.x)>Math.abs(e.z)?(this._x=-e.y,this._y=e.x,this._z=0,this._w=n):(this._x=0,this._y=-e.z,this._z=e.y,this._w=n)):(this._x=e.y*t.z-e.z*t.y,this._y=e.z*t.x-e.x*t.z,this._z=e.x*t.y-e.y*t.x,this._w=n),this.normalize()}angleTo(e){return 2*Math.acos(Math.abs(H(this.dot(e),-1,1)))}rotateTowards(e,t){let n=this.angleTo(e);if(n===0)return this;let r=Math.min(1,t/n);return this.slerp(e,r),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(e){return this._x*e._x+this._y*e._y+this._z*e._z+this._w*e._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let e=this.length();return e===0?(this._x=0,this._y=0,this._z=0,this._w=1):(e=1/e,this._x*=e,this._y*=e,this._z*=e,this._w*=e),this._onChangeCallback(),this}multiply(e){return this.multiplyQuaternions(this,e)}premultiply(e){return this.multiplyQuaternions(e,this)}multiplyQuaternions(e,t){let n=e._x,r=e._y,i=e._z,a=e._w,o=t._x,s=t._y,c=t._z,l=t._w;return this._x=n*l+a*o+r*c-i*s,this._y=r*l+a*s+i*o-n*c,this._z=i*l+a*c+n*s-r*o,this._w=a*l-n*o-r*s-i*c,this._onChangeCallback(),this}slerp(e,t){let n=e._x,r=e._y,i=e._z,a=e._w,o=this.dot(e);o<0&&(n=-n,r=-r,i=-i,a=-a,o=-o);let s=1-t;if(o<.9995){let e=Math.acos(o),c=Math.sin(e);s=Math.sin(s*e)/c,t=Math.sin(t*e)/c,this._x=this._x*s+n*t,this._y=this._y*s+r*t,this._z=this._z*s+i*t,this._w=this._w*s+a*t,this._onChangeCallback()}else this._x=this._x*s+n*t,this._y=this._y*s+r*t,this._z=this._z*s+i*t,this._w=this._w*s+a*t,this.normalize();return this}slerpQuaternions(e,t,n){return this.copy(e).slerp(t,n)}random(){let e=2*Math.PI*Math.random(),t=2*Math.PI*Math.random(),n=Math.random(),r=Math.sqrt(1-n),i=Math.sqrt(n);return this.set(r*Math.sin(e),r*Math.cos(e),i*Math.sin(t),i*Math.cos(t))}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._w===this._w}fromArray(e,t=0){return this._x=e[t],this._y=e[t+1],this._z=e[t+2],this._w=e[t+3],this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._w,e}fromBufferAttribute(e,t){return this._x=e.getX(t),this._y=e.getY(t),this._z=e.getZ(t),this._w=e.getW(t),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}},W=class e{static{e.prototype.isVector3=!0}constructor(e=0,t=0,n=0){this.x=e,this.y=t,this.z=n}set(e,t,n){return n===void 0&&(n=this.z),this.x=e,this.y=t,this.z=n,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;default:throw Error(`THREE.Vector3: index is out of range: `+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw Error(`THREE.Vector3: index is out of range: `+e)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this}multiplyVectors(e,t){return this.x=e.x*t.x,this.y=e.y*t.y,this.z=e.z*t.z,this}applyEuler(e){return this.applyQuaternion(Nt.setFromEuler(e))}applyAxisAngle(e,t){return this.applyQuaternion(Nt.setFromAxisAngle(e,t))}applyMatrix3(e){let t=this.x,n=this.y,r=this.z,i=e.elements;return this.x=i[0]*t+i[3]*n+i[6]*r,this.y=i[1]*t+i[4]*n+i[7]*r,this.z=i[2]*t+i[5]*n+i[8]*r,this}applyNormalMatrix(e){return this.applyMatrix3(e).normalize()}applyMatrix4(e){let t=this.x,n=this.y,r=this.z,i=e.elements,a=1/(i[3]*t+i[7]*n+i[11]*r+i[15]);return this.x=(i[0]*t+i[4]*n+i[8]*r+i[12])*a,this.y=(i[1]*t+i[5]*n+i[9]*r+i[13])*a,this.z=(i[2]*t+i[6]*n+i[10]*r+i[14])*a,this}applyQuaternion(e){let t=this.x,n=this.y,r=this.z,i=e.x,a=e.y,o=e.z,s=e.w,c=2*(a*r-o*n),l=2*(o*t-i*r),u=2*(i*n-a*t);return this.x=t+s*c+a*u-o*l,this.y=n+s*l+o*c-i*u,this.z=r+s*u+i*l-a*c,this}project(e){return this.applyMatrix4(e.matrixWorldInverse).applyMatrix4(e.projectionMatrix)}unproject(e){return this.applyMatrix4(e.projectionMatrixInverse).applyMatrix4(e.matrixWorld)}transformDirection(e){let t=this.x,n=this.y,r=this.z,i=e.elements;return this.x=i[0]*t+i[4]*n+i[8]*r,this.y=i[1]*t+i[5]*n+i[9]*r,this.z=i[2]*t+i[6]*n+i[10]*r,this.normalize()}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this}divideScalar(e){return this.multiplyScalar(1/e)}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this}clamp(e,t){return this.x=H(this.x,e.x,t.x),this.y=H(this.y,e.y,t.y),this.z=H(this.z,e.z,t.z),this}clampScalar(e,t){return this.x=H(this.x,e,t),this.y=H(this.y,e,t),this.z=H(this.z,e,t),this}clampLength(e,t){let n=this.length();return this.divideScalar(n||1).multiplyScalar(H(n,e,t))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this}cross(e){return this.crossVectors(this,e)}crossVectors(e,t){let n=e.x,r=e.y,i=e.z,a=t.x,o=t.y,s=t.z;return this.x=r*s-i*o,this.y=i*a-n*s,this.z=n*o-r*a,this}projectOnVector(e){let t=e.lengthSq();if(t===0)return this.set(0,0,0);let n=e.dot(this)/t;return this.copy(e).multiplyScalar(n)}projectOnPlane(e){return Mt.copy(this).projectOnVector(e),this.sub(Mt)}reflect(e){return this.sub(Mt.copy(e).multiplyScalar(2*this.dot(e)))}angleTo(e){let t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;let n=this.dot(e)/t;return Math.acos(H(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){let t=this.x-e.x,n=this.y-e.y,r=this.z-e.z;return t*t+n*n+r*r}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)+Math.abs(this.z-e.z)}setFromSpherical(e){return this.setFromSphericalCoords(e.radius,e.phi,e.theta)}setFromSphericalCoords(e,t,n){let r=Math.sin(t)*e;return this.x=r*Math.sin(n),this.y=Math.cos(t)*e,this.z=r*Math.cos(n),this}setFromCylindrical(e){return this.setFromCylindricalCoords(e.radius,e.theta,e.y)}setFromCylindricalCoords(e,t,n){return this.x=e*Math.sin(t),this.y=n,this.z=e*Math.cos(t),this}setFromMatrixPosition(e){let t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this}setFromMatrixScale(e){let t=this.setFromMatrixColumn(e,0).length(),n=this.setFromMatrixColumn(e,1).length(),r=this.setFromMatrixColumn(e,2).length();return this.x=t,this.y=n,this.z=r,this}setFromMatrixColumn(e,t){return this.fromArray(e.elements,t*4)}setFromMatrix3Column(e,t){return this.fromArray(e.elements,t*3)}setFromEuler(e){return this.x=e._x,this.y=e._y,this.z=e._z,this}setFromColor(e){return this.x=e.r,this.y=e.g,this.z=e.b,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){let e=Math.random()*Math.PI*2,t=Math.random()*2-1,n=Math.sqrt(1-t*t);return this.x=n*Math.cos(e),this.y=t,this.z=n*Math.sin(e),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}},Mt=new W,Nt=new jt,G=class e{static{e.prototype.isMatrix3=!0}constructor(e,t,n,r,i,a,o,s,c){this.elements=[1,0,0,0,1,0,0,0,1],e!==void 0&&this.set(e,t,n,r,i,a,o,s,c)}set(e,t,n,r,i,a,o,s,c){let l=this.elements;return l[0]=e,l[1]=r,l[2]=o,l[3]=t,l[4]=i,l[5]=s,l[6]=n,l[7]=a,l[8]=c,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(e){let t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],this}extractBasis(e,t,n){return e.setFromMatrix3Column(this,0),t.setFromMatrix3Column(this,1),n.setFromMatrix3Column(this,2),this}setFromMatrix4(e){let t=e.elements;return this.set(t[0],t[4],t[8],t[1],t[5],t[9],t[2],t[6],t[10]),this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){let n=e.elements,r=t.elements,i=this.elements,a=n[0],o=n[3],s=n[6],c=n[1],l=n[4],u=n[7],d=n[2],f=n[5],p=n[8],m=r[0],h=r[3],g=r[6],_=r[1],v=r[4],y=r[7],b=r[2],x=r[5],S=r[8];return i[0]=a*m+o*_+s*b,i[3]=a*h+o*v+s*x,i[6]=a*g+o*y+s*S,i[1]=c*m+l*_+u*b,i[4]=c*h+l*v+u*x,i[7]=c*g+l*y+u*S,i[2]=d*m+f*_+p*b,i[5]=d*h+f*v+p*x,i[8]=d*g+f*y+p*S,this}multiplyScalar(e){let t=this.elements;return t[0]*=e,t[3]*=e,t[6]*=e,t[1]*=e,t[4]*=e,t[7]*=e,t[2]*=e,t[5]*=e,t[8]*=e,this}determinant(){let e=this.elements,t=e[0],n=e[1],r=e[2],i=e[3],a=e[4],o=e[5],s=e[6],c=e[7],l=e[8];return t*a*l-t*o*c-n*i*l+n*o*s+r*i*c-r*a*s}invert(){let e=this.elements,t=e[0],n=e[1],r=e[2],i=e[3],a=e[4],o=e[5],s=e[6],c=e[7],l=e[8],u=l*a-o*c,d=o*s-l*i,f=c*i-a*s,p=t*u+n*d+r*f;if(p===0)return this.set(0,0,0,0,0,0,0,0,0);let m=1/p;return e[0]=u*m,e[1]=(r*c-l*n)*m,e[2]=(o*n-r*a)*m,e[3]=d*m,e[4]=(l*t-r*s)*m,e[5]=(r*i-o*t)*m,e[6]=f*m,e[7]=(n*s-c*t)*m,e[8]=(a*t-n*i)*m,this}transpose(){let e,t=this.elements;return e=t[1],t[1]=t[3],t[3]=e,e=t[2],t[2]=t[6],t[6]=e,e=t[5],t[5]=t[7],t[7]=e,this}getNormalMatrix(e){return this.setFromMatrix4(e).invert().transpose()}transposeIntoArray(e){let t=this.elements;return e[0]=t[0],e[1]=t[3],e[2]=t[6],e[3]=t[1],e[4]=t[4],e[5]=t[7],e[6]=t[2],e[7]=t[5],e[8]=t[8],this}setUvTransform(e,t,n,r,i,a,o){let s=Math.cos(i),c=Math.sin(i);return this.set(n*s,n*c,-n*(s*a+c*o)+a+e,-r*c,r*s,-r*(-c*a+s*o)+o+t,0,0,1),this}scale(e,t){return tt(`Matrix3: .scale() is deprecated. Use .makeScale() instead.`),this.premultiply(Pt.makeScale(e,t)),this}rotate(e){return tt(`Matrix3: .rotate() is deprecated. Use .makeRotation() instead.`),this.premultiply(Pt.makeRotation(-e)),this}translate(e,t){return tt(`Matrix3: .translate() is deprecated. Use .makeTranslation() instead.`),this.premultiply(Pt.makeTranslation(e,t)),this}makeTranslation(e,t){return e.isVector2?this.set(1,0,e.x,0,1,e.y,0,0,1):this.set(1,0,e,0,1,t,0,0,1),this}makeRotation(e){let t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,n,t,0,0,0,1),this}makeScale(e,t){return this.set(e,0,0,0,t,0,0,0,1),this}equals(e){let t=this.elements,n=e.elements;for(let e=0;e<9;e++)if(t[e]!==n[e])return!1;return!0}fromArray(e,t=0){for(let n=0;n<9;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){let n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e}clone(){return new this.constructor().fromArray(this.elements)}},Pt=new G,Ft=new G().set(.4123908,.3575843,.1804808,.212639,.7151687,.0721923,.0193308,.1191948,.9505322),It=new G().set(3.2409699,-1.5373832,-.4986108,-.9692436,1.8759675,.0415551,.0556301,-.203977,1.0569715);function Lt(){let e={enabled:!0,workingColorSpace:We,spaces:{},convert:function(e,t,n){return this.enabled===!1||t===n||!t||!n?e:(this.spaces[t].transfer===`srgb`&&(e.r=Rt(e.r),e.g=Rt(e.g),e.b=Rt(e.b)),this.spaces[t].primaries!==this.spaces[n].primaries&&(e.applyMatrix3(this.spaces[t].toXYZ),e.applyMatrix3(this.spaces[n].fromXYZ)),this.spaces[n].transfer===`srgb`&&(e.r=zt(e.r),e.g=zt(e.g),e.b=zt(e.b)),e)},workingToColorSpace:function(e,t){return this.convert(e,this.workingColorSpace,t)},colorSpaceToWorking:function(e,t){return this.convert(e,t,this.workingColorSpace)},getPrimaries:function(e){return this.spaces[e].primaries},getTransfer:function(e){return e===``?Ge:this.spaces[e].transfer},getToneMappingMode:function(e){return this.spaces[e].outputColorSpaceConfig.toneMappingMode||`standard`},getLuminanceCoefficients:function(e,t=this.workingColorSpace){return e.fromArray(this.spaces[t].luminanceCoefficients)},define:function(e){Object.assign(this.spaces,e)},_getMatrix:function(e,t,n){return e.copy(this.spaces[t].toXYZ).multiply(this.spaces[n].fromXYZ)},_getDrawingBufferColorSpace:function(e){return this.spaces[e].outputColorSpaceConfig.drawingBufferColorSpace},_getUnpackColorSpace:function(e=this.workingColorSpace){return this.spaces[e].workingColorSpaceConfig.unpackColorSpace},fromWorkingColorSpace:function(t,n){return tt(`ColorManagement: .fromWorkingColorSpace() has been renamed to .workingToColorSpace().`),e.workingToColorSpace(t,n)},toWorkingColorSpace:function(t,n){return tt(`ColorManagement: .toWorkingColorSpace() has been renamed to .colorSpaceToWorking().`),e.colorSpaceToWorking(t,n)}},t=[.64,.33,.3,.6,.15,.06],n=[.2126,.7152,.0722],r=[.3127,.329];return e.define({[We]:{primaries:t,whitePoint:r,transfer:Ge,toXYZ:Ft,fromXYZ:It,luminanceCoefficients:n,workingColorSpaceConfig:{unpackColorSpace:Ue},outputColorSpaceConfig:{drawingBufferColorSpace:Ue}},[Ue]:{primaries:t,whitePoint:r,transfer:Ke,toXYZ:Ft,fromXYZ:It,luminanceCoefficients:n,outputColorSpaceConfig:{drawingBufferColorSpace:Ue}}}),e}var K=Lt();function Rt(e){return e<.04045?e*.0773993808:(e*.9478672986+.0521327014)**2.4}function zt(e){return e<.0031308?e*12.92:1.055*e**.41666-.055}var Bt,Vt=class{static getDataURL(e,t=`image/png`){if(/^data:/i.test(e.src)||typeof HTMLCanvasElement>`u`)return e.src;let n;if(e instanceof HTMLCanvasElement)n=e;else{Bt===void 0&&(Bt=Xe(`canvas`)),Bt.width=e.width,Bt.height=e.height;let t=Bt.getContext(`2d`);e instanceof ImageData?t.putImageData(e,0,0):t.drawImage(e,0,0,e.width,e.height),n=Bt}return n.toDataURL(t)}static sRGBToLinear(e){if(typeof HTMLImageElement<`u`&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<`u`&&e instanceof HTMLCanvasElement||typeof ImageBitmap<`u`&&e instanceof ImageBitmap){let t=Xe(`canvas`);t.width=e.width,t.height=e.height;let n=t.getContext(`2d`);n.drawImage(e,0,0,e.width,e.height);let r=n.getImageData(0,0,e.width,e.height),i=r.data;for(let e=0;e<i.length;e++)i[e]=Rt(i[e]/255)*255;return n.putImageData(r,0,0),t}if(e.data){let t=e.data.slice(0);for(let e=0;e<t.length;e++)t instanceof Uint8Array||t instanceof Uint8ClampedArray?t[e]=Math.floor(Rt(t[e]/255)*255):t[e]=Rt(t[e]);return{data:t,width:e.width,height:e.height}}return B(`ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied.`),e}},Ht=0,Ut=class{constructor(e=null){this.isSource=!0,Object.defineProperty(this,"id",{value:Ht++}),this.uuid=lt(),this.data=e,this.dataReady=!0,this.version=0}getSize(e){let t=this.data;return typeof HTMLVideoElement<`u`&&t instanceof HTMLVideoElement?e.set(t.videoWidth,t.videoHeight,0):typeof VideoFrame<`u`&&t instanceof VideoFrame?e.set(t.displayWidth,t.displayHeight,0):t===null?e.set(0,0,0):e.set(t.width,t.height,t.depth||0),e}set needsUpdate(e){e===!0&&this.version++}toJSON(e){let t=e===void 0||typeof e==`string`;if(!t&&e.images[this.uuid]!==void 0)return e.images[this.uuid];let n={uuid:this.uuid,url:``},r=this.data;if(r!==null){let e;if(Array.isArray(r)){e=[];for(let t=0,n=r.length;t<n;t++)r[t].isDataTexture?e.push(Wt(r[t].image)):e.push(Wt(r[t]))}else e=Wt(r);n.url=e}return t||(e.images[this.uuid]=n),n}};function Wt(e){return typeof HTMLImageElement<`u`&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<`u`&&e instanceof HTMLCanvasElement||typeof ImageBitmap<`u`&&e instanceof ImageBitmap?Vt.getDataURL(e):e.data?{data:Array.from(e.data),width:e.width,height:e.height,type:e.data.constructor.name}:(B(`Texture: Unable to serialize Texture.`),{})}var Gt=0,Kt=new W,qt=class e extends it{constructor(t=e.DEFAULT_IMAGE,n=e.DEFAULT_MAPPING,r=i,a=i,o=l,s=d,c=D,u=f,p=e.DEFAULT_ANISOTROPY,m=``){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:Gt++}),this.uuid=lt(),this.name=``,this.source=new Ut(t),this.mipmaps=[],this.mapping=n,this.channel=0,this.wrapS=r,this.wrapT=a,this.magFilter=o,this.minFilter=s,this.anisotropy=p,this.format=c,this.internalFormat=null,this.type=u,this.offset=new U(0,0),this.repeat=new U(1,1),this.center=new U(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new G,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=m,this.userData={},this.updateRanges=[],this.version=0,this.onUpdate=null,this.renderTarget=null,this.isRenderTargetTexture=!1,this.isArrayTexture=!!(t&&t.depth&&t.depth>1),this.pmremVersion=0,this.normalized=!1}get width(){return this.source.getSize(Kt).x}get height(){return this.source.getSize(Kt).y}get depth(){return this.source.getSize(Kt).z}get image(){return this.source.data}set image(e){this.source.data=e}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}clone(){return new this.constructor().copy(this)}copy(e){return this.name=e.name,this.source=e.source,this.mipmaps=e.mipmaps.slice(0),this.mapping=e.mapping,this.channel=e.channel,this.wrapS=e.wrapS,this.wrapT=e.wrapT,this.magFilter=e.magFilter,this.minFilter=e.minFilter,this.anisotropy=e.anisotropy,this.format=e.format,this.internalFormat=e.internalFormat,this.type=e.type,this.normalized=e.normalized,this.offset.copy(e.offset),this.repeat.copy(e.repeat),this.center.copy(e.center),this.rotation=e.rotation,this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrix.copy(e.matrix),this.generateMipmaps=e.generateMipmaps,this.premultiplyAlpha=e.premultiplyAlpha,this.flipY=e.flipY,this.unpackAlignment=e.unpackAlignment,this.colorSpace=e.colorSpace,this.renderTarget=e.renderTarget,this.isRenderTargetTexture=e.isRenderTargetTexture,this.isArrayTexture=e.isArrayTexture,this.userData=JSON.parse(JSON.stringify(e.userData)),this.needsUpdate=!0,this}setValues(e){for(let t in e){let n=e[t];if(n===void 0){B(`Texture.setValues(): parameter '${t}' has value of undefined.`);continue}let r=this[t];if(r===void 0){B(`Texture.setValues(): property '${t}' does not exist.`);continue}r&&n&&r.isVector2&&n.isVector2||r&&n&&r.isVector3&&n.isVector3||r&&n&&r.isMatrix3&&n.isMatrix3?r.copy(n):this[t]=n}}toJSON(e){let t=e===void 0||typeof e==`string`;if(!t&&e.textures[this.uuid]!==void 0)return e.textures[this.uuid];let n={metadata:{version:4.7,type:`Texture`,generator:`Texture.toJSON`},uuid:this.uuid,name:this.name,image:this.source.toJSON(e).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,normalized:this.normalized,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(n.userData=this.userData),t||(e.textures[this.uuid]=n),n}dispose(){this.dispatchEvent({type:`dispose`})}transformUv(e){if(this.mapping!==300)return e;if(e.applyMatrix3(this.matrix),e.x<0||e.x>1)switch(this.wrapS){case r:e.x-=Math.floor(e.x);break;case i:e.x=e.x<0?0:1;break;case a:Math.abs(Math.floor(e.x)%2)===1?e.x=Math.ceil(e.x)-e.x:e.x-=Math.floor(e.x)}if(e.y<0||e.y>1)switch(this.wrapT){case r:e.y-=Math.floor(e.y);break;case i:e.y=e.y<0?0:1;break;case a:Math.abs(Math.floor(e.y)%2)===1?e.y=Math.ceil(e.y)-e.y:e.y-=Math.floor(e.y)}return this.flipY&&(e.y=1-e.y),e}set needsUpdate(e){e===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(e){e===!0&&this.pmremVersion++}};qt.DEFAULT_IMAGE=null,qt.DEFAULT_MAPPING=300,qt.DEFAULT_ANISOTROPY=1;var Jt=class e{static{e.prototype.isVector4=!0}constructor(e=0,t=0,n=0,r=1){this.x=e,this.y=t,this.z=n,this.w=r}get width(){return this.z}set width(e){this.z=e}get height(){return this.w}set height(e){this.w=e}set(e,t,n,r){return this.x=e,this.y=t,this.z=n,this.w=r,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this.w=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setW(e){return this.w=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;case 3:this.w=t;break;default:throw Error(`THREE.Vector4: index is out of range: `+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw Error(`THREE.Vector4: index is out of range: `+e)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this.w=e.w===void 0?1:e.w,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this.w+=e.w,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this.w+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this.w=e.w+t.w,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this.w+=e.w*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this.w-=e.w,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this.w-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this.w=e.w-t.w,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this.w*=e.w,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this.w*=e,this}applyMatrix4(e){let t=this.x,n=this.y,r=this.z,i=this.w,a=e.elements;return this.x=a[0]*t+a[4]*n+a[8]*r+a[12]*i,this.y=a[1]*t+a[5]*n+a[9]*r+a[13]*i,this.z=a[2]*t+a[6]*n+a[10]*r+a[14]*i,this.w=a[3]*t+a[7]*n+a[11]*r+a[15]*i,this}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this.w/=e.w,this}divideScalar(e){return this.multiplyScalar(1/e)}setAxisAngleFromQuaternion(e){this.w=2*Math.acos(e.w);let t=Math.sqrt(1-e.w*e.w);return t<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=e.x/t,this.y=e.y/t,this.z=e.z/t),this}setAxisAngleFromRotationMatrix(e){let t,n,r,i,a=.01,o=.1,s=e.elements,c=s[0],l=s[4],u=s[8],d=s[1],f=s[5],p=s[9],m=s[2],h=s[6],g=s[10];if(Math.abs(l-d)<a&&Math.abs(u-m)<a&&Math.abs(p-h)<a){if(Math.abs(l+d)<o&&Math.abs(u+m)<o&&Math.abs(p+h)<o&&Math.abs(c+f+g-3)<o)return this.set(1,0,0,0),this;t=Math.PI;let e=(c+1)/2,s=(f+1)/2,_=(g+1)/2,v=(l+d)/4,y=(u+m)/4,b=(p+h)/4;return e>s&&e>_?e<a?(n=0,r=.707106781,i=.707106781):(n=Math.sqrt(e),r=v/n,i=y/n):s>_?s<a?(n=.707106781,r=0,i=.707106781):(r=Math.sqrt(s),n=v/r,i=b/r):_<a?(n=.707106781,r=.707106781,i=0):(i=Math.sqrt(_),n=y/i,r=b/i),this.set(n,r,i,t),this}let _=Math.sqrt((h-p)*(h-p)+(u-m)*(u-m)+(d-l)*(d-l));return Math.abs(_)<.001&&(_=1),this.x=(h-p)/_,this.y=(u-m)/_,this.z=(d-l)/_,this.w=Math.acos((c+f+g-1)/2),this}setFromMatrixPosition(e){let t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this.w=t[15],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this.w=Math.min(this.w,e.w),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this.w=Math.max(this.w,e.w),this}clamp(e,t){return this.x=H(this.x,e.x,t.x),this.y=H(this.y,e.y,t.y),this.z=H(this.z,e.z,t.z),this.w=H(this.w,e.w,t.w),this}clampScalar(e,t){return this.x=H(this.x,e,t),this.y=H(this.y,e,t),this.z=H(this.z,e,t),this.w=H(this.w,e,t),this}clampLength(e,t){let n=this.length();return this.divideScalar(n||1).multiplyScalar(H(n,e,t))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z+this.w*e.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this.w+=(e.w-this.w)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this.w=e.w+(t.w-e.w)*n,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z&&e.w===this.w}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this.w=e[t+3],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e[t+3]=this.w,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this.w=e.getW(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}},Yt=class extends it{constructor(e=1,t=1,n={}){super(),n=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:l,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1,depth:1,multiview:!1,useArrayDepthTexture:!1},n),this.isRenderTarget=!0,this.width=e,this.height=t,this.depth=n.depth,this.scissor=new Jt(0,0,e,t),this.scissorTest=!1,this.viewport=new Jt(0,0,e,t),this.textures=[];let r=new qt({width:e,height:t,depth:n.depth}),i=n.count;for(let e=0;e<i;e++)this.textures[e]=r.clone(),this.textures[e].isRenderTargetTexture=!0,this.textures[e].renderTarget=this;this._setTextureOptions(n),this.depthBuffer=n.depthBuffer,this.stencilBuffer=n.stencilBuffer,this.resolveDepthBuffer=n.resolveDepthBuffer,this.resolveStencilBuffer=n.resolveStencilBuffer,this._depthTexture=null,this.depthTexture=n.depthTexture,this.samples=n.samples,this.multiview=n.multiview,this.useArrayDepthTexture=n.useArrayDepthTexture}_setTextureOptions(e={}){let t={minFilter:l,generateMipmaps:!1,flipY:!1,internalFormat:null};e.mapping!==void 0&&(t.mapping=e.mapping),e.wrapS!==void 0&&(t.wrapS=e.wrapS),e.wrapT!==void 0&&(t.wrapT=e.wrapT),e.wrapR!==void 0&&(t.wrapR=e.wrapR),e.magFilter!==void 0&&(t.magFilter=e.magFilter),e.minFilter!==void 0&&(t.minFilter=e.minFilter),e.format!==void 0&&(t.format=e.format),e.type!==void 0&&(t.type=e.type),e.anisotropy!==void 0&&(t.anisotropy=e.anisotropy),e.colorSpace!==void 0&&(t.colorSpace=e.colorSpace),e.flipY!==void 0&&(t.flipY=e.flipY),e.generateMipmaps!==void 0&&(t.generateMipmaps=e.generateMipmaps),e.internalFormat!==void 0&&(t.internalFormat=e.internalFormat);for(let e=0;e<this.textures.length;e++)this.textures[e].setValues(t)}get texture(){return this.textures[0]}set texture(e){this.textures[0]=e}set depthTexture(e){this._depthTexture!==null&&(this._depthTexture.renderTarget=null),e!==null&&(e.renderTarget=this),this._depthTexture=e}get depthTexture(){return this._depthTexture}setSize(e,t,n=1){if(this.width!==e||this.height!==t||this.depth!==n){this.width=e,this.height=t,this.depth=n;for(let r=0,i=this.textures.length;r<i;r++)this.textures[r].image.width=e,this.textures[r].image.height=t,this.textures[r].image.depth=n,this.textures[r].isData3DTexture!==!0&&(this.textures[r].isArrayTexture=this.textures[r].image.depth>1);this.dispose()}this.viewport.set(0,0,e,t),this.scissor.set(0,0,e,t)}clone(){return new this.constructor().copy(this)}copy(e){this.width=e.width,this.height=e.height,this.depth=e.depth,this.scissor.copy(e.scissor),this.scissorTest=e.scissorTest,this.viewport.copy(e.viewport),this.textures.length=0;for(let t=0,n=e.textures.length;t<n;t++){this.textures[t]=e.textures[t].clone(),this.textures[t].isRenderTargetTexture=!0,this.textures[t].renderTarget=this;let n=Object.assign({},e.textures[t].image);this.textures[t].source=new Ut(n)}return this.depthBuffer=e.depthBuffer,this.stencilBuffer=e.stencilBuffer,this.resolveDepthBuffer=e.resolveDepthBuffer,this.resolveStencilBuffer=e.resolveStencilBuffer,e.depthTexture!==null&&(this.depthTexture=e.depthTexture.clone()),this.samples=e.samples,this.multiview=e.multiview,this.useArrayDepthTexture=e.useArrayDepthTexture,this}dispose(){this.dispatchEvent({type:`dispose`})}},Xt=class extends Yt{constructor(e=1,t=1,n={}){super(e,t,n),this.isWebGLRenderTarget=!0}},Zt=class extends qt{constructor(e=null,t=1,n=1,r=1){super(null),this.isDataArrayTexture=!0,this.image={data:e,width:t,height:n,depth:r},this.magFilter=o,this.minFilter=o,this.wrapR=i,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(e){this.layerUpdates.add(e)}clearLayerUpdates(){this.layerUpdates.clear()}},Qt=class extends qt{constructor(e=null,t=1,n=1,r=1){super(null),this.isData3DTexture=!0,this.image={data:e,width:t,height:n,depth:r},this.magFilter=o,this.minFilter=o,this.wrapR=i,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}},q=class e{static{e.prototype.isMatrix4=!0}constructor(e,t,n,r,i,a,o,s,c,l,u,d,f,p,m,h){this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],e!==void 0&&this.set(e,t,n,r,i,a,o,s,c,l,u,d,f,p,m,h)}set(e,t,n,r,i,a,o,s,c,l,u,d,f,p,m,h){let g=this.elements;return g[0]=e,g[4]=t,g[8]=n,g[12]=r,g[1]=i,g[5]=a,g[9]=o,g[13]=s,g[2]=c,g[6]=l,g[10]=u,g[14]=d,g[3]=f,g[7]=p,g[11]=m,g[15]=h,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new e().fromArray(this.elements)}copy(e){let t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],t[9]=n[9],t[10]=n[10],t[11]=n[11],t[12]=n[12],t[13]=n[13],t[14]=n[14],t[15]=n[15],this}copyPosition(e){let t=this.elements,n=e.elements;return t[12]=n[12],t[13]=n[13],t[14]=n[14],this}setFromMatrix3(e){let t=e.elements;return this.set(t[0],t[3],t[6],0,t[1],t[4],t[7],0,t[2],t[5],t[8],0,0,0,0,1),this}extractBasis(e,t,n){return this.determinantAffine()===0?(e.set(1,0,0),t.set(0,1,0),n.set(0,0,1),this):(e.setFromMatrixColumn(this,0),t.setFromMatrixColumn(this,1),n.setFromMatrixColumn(this,2),this)}makeBasis(e,t,n){return this.set(e.x,t.x,n.x,0,e.y,t.y,n.y,0,e.z,t.z,n.z,0,0,0,0,1),this}extractRotation(e){if(e.determinantAffine()===0)return this.identity();let t=this.elements,n=e.elements,r=1/$t.setFromMatrixColumn(e,0).length(),i=1/$t.setFromMatrixColumn(e,1).length(),a=1/$t.setFromMatrixColumn(e,2).length();return t[0]=n[0]*r,t[1]=n[1]*r,t[2]=n[2]*r,t[3]=0,t[4]=n[4]*i,t[5]=n[5]*i,t[6]=n[6]*i,t[7]=0,t[8]=n[8]*a,t[9]=n[9]*a,t[10]=n[10]*a,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromEuler(e){let t=this.elements,n=e.x,r=e.y,i=e.z,a=Math.cos(n),o=Math.sin(n),s=Math.cos(r),c=Math.sin(r),l=Math.cos(i),u=Math.sin(i);if(e.order===`XYZ`){let e=a*l,n=a*u,r=o*l,i=o*u;t[0]=s*l,t[4]=-s*u,t[8]=c,t[1]=n+r*c,t[5]=e-i*c,t[9]=-o*s,t[2]=i-e*c,t[6]=r+n*c,t[10]=a*s}else if(e.order===`YXZ`){let e=s*l,n=s*u,r=c*l,i=c*u;t[0]=e+i*o,t[4]=r*o-n,t[8]=a*c,t[1]=a*u,t[5]=a*l,t[9]=-o,t[2]=n*o-r,t[6]=i+e*o,t[10]=a*s}else if(e.order===`ZXY`){let e=s*l,n=s*u,r=c*l,i=c*u;t[0]=e-i*o,t[4]=-a*u,t[8]=r+n*o,t[1]=n+r*o,t[5]=a*l,t[9]=i-e*o,t[2]=-a*c,t[6]=o,t[10]=a*s}else if(e.order===`ZYX`){let e=a*l,n=a*u,r=o*l,i=o*u;t[0]=s*l,t[4]=r*c-n,t[8]=e*c+i,t[1]=s*u,t[5]=i*c+e,t[9]=n*c-r,t[2]=-c,t[6]=o*s,t[10]=a*s}else if(e.order===`YZX`){let e=a*s,n=a*c,r=o*s,i=o*c;t[0]=s*l,t[4]=i-e*u,t[8]=r*u+n,t[1]=u,t[5]=a*l,t[9]=-o*l,t[2]=-c*l,t[6]=n*u+r,t[10]=e-i*u}else if(e.order===`XZY`){let e=a*s,n=a*c,r=o*s,i=o*c;t[0]=s*l,t[4]=-u,t[8]=c*l,t[1]=e*u+i,t[5]=a*l,t[9]=n*u-r,t[2]=r*u-n,t[6]=o*l,t[10]=i*u+e}return t[3]=0,t[7]=0,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromQuaternion(e){return this.compose(tn,e,nn)}lookAt(e,t,n){let r=this.elements;return on.subVectors(e,t),on.lengthSq()===0&&(on.z=1),on.normalize(),rn.crossVectors(n,on),rn.lengthSq()===0&&(Math.abs(n.z)===1?on.x+=1e-4:on.z+=1e-4,on.normalize(),rn.crossVectors(n,on)),rn.normalize(),an.crossVectors(on,rn),r[0]=rn.x,r[4]=an.x,r[8]=on.x,r[1]=rn.y,r[5]=an.y,r[9]=on.y,r[2]=rn.z,r[6]=an.z,r[10]=on.z,this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){let n=e.elements,r=t.elements,i=this.elements,a=n[0],o=n[4],s=n[8],c=n[12],l=n[1],u=n[5],d=n[9],f=n[13],p=n[2],m=n[6],h=n[10],g=n[14],_=n[3],v=n[7],y=n[11],b=n[15],x=r[0],S=r[4],C=r[8],w=r[12],T=r[1],E=r[5],D=r[9],O=r[13],k=r[2],A=r[6],ee=r[10],te=r[14],j=r[3],ne=r[7],M=r[11],N=r[15];return i[0]=a*x+o*T+s*k+c*j,i[4]=a*S+o*E+s*A+c*ne,i[8]=a*C+o*D+s*ee+c*M,i[12]=a*w+o*O+s*te+c*N,i[1]=l*x+u*T+d*k+f*j,i[5]=l*S+u*E+d*A+f*ne,i[9]=l*C+u*D+d*ee+f*M,i[13]=l*w+u*O+d*te+f*N,i[2]=p*x+m*T+h*k+g*j,i[6]=p*S+m*E+h*A+g*ne,i[10]=p*C+m*D+h*ee+g*M,i[14]=p*w+m*O+h*te+g*N,i[3]=_*x+v*T+y*k+b*j,i[7]=_*S+v*E+y*A+b*ne,i[11]=_*C+v*D+y*ee+b*M,i[15]=_*w+v*O+y*te+b*N,this}multiplyScalar(e){let t=this.elements;return t[0]*=e,t[4]*=e,t[8]*=e,t[12]*=e,t[1]*=e,t[5]*=e,t[9]*=e,t[13]*=e,t[2]*=e,t[6]*=e,t[10]*=e,t[14]*=e,t[3]*=e,t[7]*=e,t[11]*=e,t[15]*=e,this}determinant(){let e=this.elements,t=e[0],n=e[4],r=e[8],i=e[12],a=e[1],o=e[5],s=e[9],c=e[13],l=e[2],u=e[6],d=e[10],f=e[14],p=e[3],m=e[7],h=e[11],g=e[15],_=s*f-c*d,v=o*f-c*u,y=o*d-s*u,b=a*f-c*l,x=a*d-s*l,S=a*u-o*l;return t*(m*_-h*v+g*y)-n*(p*_-h*b+g*x)+r*(p*v-m*b+g*S)-i*(p*y-m*x+h*S)}determinantAffine(){let e=this.elements,t=e[0],n=e[4],r=e[8],i=e[1],a=e[5],o=e[9],s=e[2],c=e[6],l=e[10];return t*(a*l-o*c)-n*(i*l-o*s)+r*(i*c-a*s)}transpose(){let e=this.elements,t;return t=e[1],e[1]=e[4],e[4]=t,t=e[2],e[2]=e[8],e[8]=t,t=e[6],e[6]=e[9],e[9]=t,t=e[3],e[3]=e[12],e[12]=t,t=e[7],e[7]=e[13],e[13]=t,t=e[11],e[11]=e[14],e[14]=t,this}setPosition(e,t,n){let r=this.elements;return e.isVector3?(r[12]=e.x,r[13]=e.y,r[14]=e.z):(r[12]=e,r[13]=t,r[14]=n),this}invert(){let e=this.elements,t=e[0],n=e[1],r=e[2],i=e[3],a=e[4],o=e[5],s=e[6],c=e[7],l=e[8],u=e[9],d=e[10],f=e[11],p=e[12],m=e[13],h=e[14],g=e[15],_=t*o-n*a,v=t*s-r*a,y=t*c-i*a,b=n*s-r*o,x=n*c-i*o,S=r*c-i*s,C=l*m-u*p,w=l*h-d*p,T=l*g-f*p,E=u*h-d*m,D=u*g-f*m,O=d*g-f*h,k=_*O-v*D+y*E+b*T-x*w+S*C;if(k===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);let A=1/k;return e[0]=(o*O-s*D+c*E)*A,e[1]=(r*D-n*O-i*E)*A,e[2]=(m*S-h*x+g*b)*A,e[3]=(d*x-u*S-f*b)*A,e[4]=(s*T-a*O-c*w)*A,e[5]=(t*O-r*T+i*w)*A,e[6]=(h*y-p*S-g*v)*A,e[7]=(l*S-d*y+f*v)*A,e[8]=(a*D-o*T+c*C)*A,e[9]=(n*T-t*D-i*C)*A,e[10]=(p*x-m*y+g*_)*A,e[11]=(u*y-l*x-f*_)*A,e[12]=(o*w-a*E-s*C)*A,e[13]=(t*E-n*w+r*C)*A,e[14]=(m*v-p*b-h*_)*A,e[15]=(l*b-u*v+d*_)*A,this}scale(e){let t=this.elements,n=e.x,r=e.y,i=e.z;return t[0]*=n,t[4]*=r,t[8]*=i,t[1]*=n,t[5]*=r,t[9]*=i,t[2]*=n,t[6]*=r,t[10]*=i,t[3]*=n,t[7]*=r,t[11]*=i,this}getMaxScaleOnAxis(){let e=this.elements,t=e[0]*e[0]+e[1]*e[1]+e[2]*e[2],n=e[4]*e[4]+e[5]*e[5]+e[6]*e[6],r=e[8]*e[8]+e[9]*e[9]+e[10]*e[10];return Math.sqrt(Math.max(t,n,r))}makeTranslation(e,t,n){return e.isVector3?this.set(1,0,0,e.x,0,1,0,e.y,0,0,1,e.z,0,0,0,1):this.set(1,0,0,e,0,1,0,t,0,0,1,n,0,0,0,1),this}makeRotationX(e){let t=Math.cos(e),n=Math.sin(e);return this.set(1,0,0,0,0,t,-n,0,0,n,t,0,0,0,0,1),this}makeRotationY(e){let t=Math.cos(e),n=Math.sin(e);return this.set(t,0,n,0,0,1,0,0,-n,0,t,0,0,0,0,1),this}makeRotationZ(e){let t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,0,n,t,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(e,t){let n=Math.cos(t),r=Math.sin(t),i=1-n,a=e.x,o=e.y,s=e.z,c=i*a,l=i*o;return this.set(c*a+n,c*o-r*s,c*s+r*o,0,c*o+r*s,l*o+n,l*s-r*a,0,c*s-r*o,l*s+r*a,i*s*s+n,0,0,0,0,1),this}makeScale(e,t,n){return this.set(e,0,0,0,0,t,0,0,0,0,n,0,0,0,0,1),this}makeShear(e,t,n,r,i,a){return this.set(1,n,i,0,e,1,a,0,t,r,1,0,0,0,0,1),this}compose(e,t,n){let r=this.elements,i=t._x,a=t._y,o=t._z,s=t._w,c=i+i,l=a+a,u=o+o,d=i*c,f=i*l,p=i*u,m=a*l,h=a*u,g=o*u,_=s*c,v=s*l,y=s*u,b=n.x,x=n.y,S=n.z;return r[0]=(1-(m+g))*b,r[1]=(f+y)*b,r[2]=(p-v)*b,r[3]=0,r[4]=(f-y)*x,r[5]=(1-(d+g))*x,r[6]=(h+_)*x,r[7]=0,r[8]=(p+v)*S,r[9]=(h-_)*S,r[10]=(1-(d+m))*S,r[11]=0,r[12]=e.x,r[13]=e.y,r[14]=e.z,r[15]=1,this}decompose(e,t,n){let r=this.elements;e.x=r[12],e.y=r[13],e.z=r[14];let i=this.determinantAffine();if(i===0)return n.set(1,1,1),t.identity(),this;let a=$t.set(r[0],r[1],r[2]).length(),o=$t.set(r[4],r[5],r[6]).length(),s=$t.set(r[8],r[9],r[10]).length();i<0&&(a=-a),en.copy(this);let c=1/a,l=1/o,u=1/s;return en.elements[0]*=c,en.elements[1]*=c,en.elements[2]*=c,en.elements[4]*=l,en.elements[5]*=l,en.elements[6]*=l,en.elements[8]*=u,en.elements[9]*=u,en.elements[10]*=u,t.setFromRotationMatrix(en),n.x=a,n.y=o,n.z=s,this}makePerspective(e,t,n,r,i,a,o=R,s=!1){let c=this.elements,l=2*i/(t-e),u=2*i/(n-r),d=(t+e)/(t-e),f=(n+r)/(n-r),p,m;if(s)p=i/(a-i),m=a*i/(a-i);else if(o===2e3)p=-(a+i)/(a-i),m=-2*a*i/(a-i);else if(o===2001)p=-a/(a-i),m=-a*i/(a-i);else throw Error(`THREE.Matrix4.makePerspective(): Invalid coordinate system: `+o);return c[0]=l,c[4]=0,c[8]=d,c[12]=0,c[1]=0,c[5]=u,c[9]=f,c[13]=0,c[2]=0,c[6]=0,c[10]=p,c[14]=m,c[3]=0,c[7]=0,c[11]=-1,c[15]=0,this}makeOrthographic(e,t,n,r,i,a,o=R,s=!1){let c=this.elements,l=2/(t-e),u=2/(n-r),d=-(t+e)/(t-e),f=-(n+r)/(n-r),p,m;if(s)p=1/(a-i),m=a/(a-i);else if(o===2e3)p=-2/(a-i),m=-(a+i)/(a-i);else if(o===2001)p=-1/(a-i),m=-i/(a-i);else throw Error(`THREE.Matrix4.makeOrthographic(): Invalid coordinate system: `+o);return c[0]=l,c[4]=0,c[8]=0,c[12]=d,c[1]=0,c[5]=u,c[9]=0,c[13]=f,c[2]=0,c[6]=0,c[10]=p,c[14]=m,c[3]=0,c[7]=0,c[11]=0,c[15]=1,this}equals(e){let t=this.elements,n=e.elements;for(let e=0;e<16;e++)if(t[e]!==n[e])return!1;return!0}fromArray(e,t=0){for(let n=0;n<16;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){let n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e[t+9]=n[9],e[t+10]=n[10],e[t+11]=n[11],e[t+12]=n[12],e[t+13]=n[13],e[t+14]=n[14],e[t+15]=n[15],e}},$t=new W,en=new q,tn=new W(0,0,0),nn=new W(1,1,1),rn=new W,an=new W,on=new W,sn=new q,cn=new jt,ln=class e{constructor(t=0,n=0,r=0,i=e.DEFAULT_ORDER){this.isEuler=!0,this._x=t,this._y=n,this._z=r,this._order=i}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get order(){return this._order}set order(e){this._order=e,this._onChangeCallback()}set(e,t,n,r=this._order){return this._x=e,this._y=t,this._z=n,this._order=r,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(e){return this._x=e._x,this._y=e._y,this._z=e._z,this._order=e._order,this._onChangeCallback(),this}setFromRotationMatrix(e,t=this._order,n=!0){let r=e.elements,i=r[0],a=r[4],o=r[8],s=r[1],c=r[5],l=r[9],u=r[2],d=r[6],f=r[10];switch(t){case`XYZ`:this._y=Math.asin(H(o,-1,1)),Math.abs(o)<.9999999?(this._x=Math.atan2(-l,f),this._z=Math.atan2(-a,i)):(this._x=Math.atan2(d,c),this._z=0);break;case`YXZ`:this._x=Math.asin(-H(l,-1,1)),Math.abs(l)<.9999999?(this._y=Math.atan2(o,f),this._z=Math.atan2(s,c)):(this._y=Math.atan2(-u,i),this._z=0);break;case`ZXY`:this._x=Math.asin(H(d,-1,1)),Math.abs(d)<.9999999?(this._y=Math.atan2(-u,f),this._z=Math.atan2(-a,c)):(this._y=0,this._z=Math.atan2(s,i));break;case`ZYX`:this._y=Math.asin(-H(u,-1,1)),Math.abs(u)<.9999999?(this._x=Math.atan2(d,f),this._z=Math.atan2(s,i)):(this._x=0,this._z=Math.atan2(-a,c));break;case`YZX`:this._z=Math.asin(H(s,-1,1)),Math.abs(s)<.9999999?(this._x=Math.atan2(-l,c),this._y=Math.atan2(-u,i)):(this._x=0,this._y=Math.atan2(o,f));break;case`XZY`:this._z=Math.asin(-H(a,-1,1)),Math.abs(a)<.9999999?(this._x=Math.atan2(d,c),this._y=Math.atan2(o,i)):(this._x=Math.atan2(-l,f),this._y=0);break;default:B(`Euler: .setFromRotationMatrix() encountered an unknown order: `+t)}return this._order=t,n===!0&&this._onChangeCallback(),this}setFromQuaternion(e,t,n){return sn.makeRotationFromQuaternion(e),this.setFromRotationMatrix(sn,t,n)}setFromVector3(e,t=this._order){return this.set(e.x,e.y,e.z,t)}reorder(e){return cn.setFromEuler(this),this.setFromQuaternion(cn,e)}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._order===this._order}fromArray(e){return this._x=e[0],this._y=e[1],this._z=e[2],e[3]!==void 0&&(this._order=e[3]),this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._order,e}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}};ln.DEFAULT_ORDER=`XYZ`;var un=class{constructor(){this.mask=1}set(e){this.mask=(1<<e|0)>>>0}enable(e){this.mask|=1<<e|0}enableAll(){this.mask=-1}toggle(e){this.mask^=1<<e|0}disable(e){this.mask&=~(1<<e|0)}disableAll(){this.mask=0}test(e){return(this.mask&e.mask)!==0}isEnabled(e){return!!(this.mask&(1<<e|0))}},dn=0,fn=new W,pn=new jt,mn=new q,hn=new W,gn=new W,_n=new W,vn=new jt,yn=new W(1,0,0),bn=new W(0,1,0),xn=new W(0,0,1),Sn={type:`added`},Cn={type:`removed`},wn={type:`childadded`,child:null},Tn={type:`childremoved`,child:null},En=class e extends it{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:dn++}),this.uuid=lt(),this.name=``,this.type=`Object3D`,this.parent=null,this.children=[],this.up=e.DEFAULT_UP.clone();let t=new W,n=new ln,r=new jt,i=new W(1,1,1);function a(){r.setFromEuler(n,!1)}function o(){n.setFromQuaternion(r,void 0,!1)}n._onChange(a),r._onChange(o),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:t},rotation:{configurable:!0,enumerable:!0,value:n},quaternion:{configurable:!0,enumerable:!0,value:r},scale:{configurable:!0,enumerable:!0,value:i},modelViewMatrix:{value:new q},normalMatrix:{value:new G}}),this.matrix=new q,this.matrixWorld=new q,this.matrixAutoUpdate=e.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=e.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new un,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.customDepthMaterial=void 0,this.customDistanceMaterial=void 0,this.static=!1,this.userData={},this.pivot=null}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(e){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(e),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(e){return this.quaternion.premultiply(e),this}setRotationFromAxisAngle(e,t){this.quaternion.setFromAxisAngle(e,t)}setRotationFromEuler(e){this.quaternion.setFromEuler(e,!0)}setRotationFromMatrix(e){this.quaternion.setFromRotationMatrix(e)}setRotationFromQuaternion(e){this.quaternion.copy(e)}rotateOnAxis(e,t){return pn.setFromAxisAngle(e,t),this.quaternion.multiply(pn),this}rotateOnWorldAxis(e,t){return pn.setFromAxisAngle(e,t),this.quaternion.premultiply(pn),this}rotateX(e){return this.rotateOnAxis(yn,e)}rotateY(e){return this.rotateOnAxis(bn,e)}rotateZ(e){return this.rotateOnAxis(xn,e)}translateOnAxis(e,t){return fn.copy(e).applyQuaternion(this.quaternion),this.position.add(fn.multiplyScalar(t)),this}translateX(e){return this.translateOnAxis(yn,e)}translateY(e){return this.translateOnAxis(bn,e)}translateZ(e){return this.translateOnAxis(xn,e)}localToWorld(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(this.matrixWorld)}worldToLocal(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(mn.copy(this.matrixWorld).invert())}lookAt(e,t,n){e.isVector3?hn.copy(e):hn.set(e,t,n);let r=this.parent;this.updateWorldMatrix(!0,!1),gn.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?mn.lookAt(gn,hn,this.up):mn.lookAt(hn,gn,this.up),this.quaternion.setFromRotationMatrix(mn),r&&(mn.extractRotation(r.matrixWorld),pn.setFromRotationMatrix(mn),this.quaternion.premultiply(pn.invert()))}add(e){if(arguments.length>1){for(let e=0;e<arguments.length;e++)this.add(arguments[e]);return this}return e===this?(V(`Object3D.add: object can't be added as a child of itself.`,e),this):(e&&e.isObject3D?(e.removeFromParent(),e.parent=this,this.children.push(e),e.dispatchEvent(Sn),wn.child=e,this.dispatchEvent(wn),wn.child=null):V(`Object3D.add: object not an instance of THREE.Object3D.`,e),this)}remove(e){if(arguments.length>1){for(let e=0;e<arguments.length;e++)this.remove(arguments[e]);return this}let t=this.children.indexOf(e);return t!==-1&&(e.parent=null,this.children.splice(t,1),e.dispatchEvent(Cn),Tn.child=e,this.dispatchEvent(Tn),Tn.child=null),this}removeFromParent(){let e=this.parent;return e!==null&&e.remove(this),this}clear(){return this.remove(...this.children)}attach(e){return this.updateWorldMatrix(!0,!1),mn.copy(this.matrixWorld).invert(),e.parent!==null&&(e.parent.updateWorldMatrix(!0,!1),mn.multiply(e.parent.matrixWorld)),e.applyMatrix4(mn),e.removeFromParent(),e.parent=this,this.children.push(e),e.updateWorldMatrix(!1,!0),e.dispatchEvent(Sn),wn.child=e,this.dispatchEvent(wn),wn.child=null,this}getObjectById(e){return this.getObjectByProperty(`id`,e)}getObjectByName(e){return this.getObjectByProperty(`name`,e)}getObjectByProperty(e,t){if(this[e]===t)return this;for(let n=0,r=this.children.length;n<r;n++){let r=this.children[n].getObjectByProperty(e,t);if(r!==void 0)return r}}getObjectsByProperty(e,t,n=[]){this[e]===t&&n.push(this);let r=this.children;for(let i=0,a=r.length;i<a;i++)r[i].getObjectsByProperty(e,t,n);return n}getWorldPosition(e){return this.updateWorldMatrix(!0,!1),e.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(gn,e,_n),e}getWorldScale(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(gn,vn,e),e}getWorldDirection(e){this.updateWorldMatrix(!0,!1);let t=this.matrixWorld.elements;return e.set(t[8],t[9],t[10]).normalize()}raycast(){}traverse(e){e(this);let t=this.children;for(let n=0,r=t.length;n<r;n++)t[n].traverse(e)}traverseVisible(e){if(this.visible===!1)return;e(this);let t=this.children;for(let n=0,r=t.length;n<r;n++)t[n].traverseVisible(e)}traverseAncestors(e){let t=this.parent;t!==null&&(e(t),t.traverseAncestors(e))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale);let e=this.pivot;if(e!==null){let t=e.x,n=e.y,r=e.z,i=this.matrix.elements;i[12]+=t-i[0]*t-i[4]*n-i[8]*r,i[13]+=n-i[1]*t-i[5]*n-i[9]*r,i[14]+=r-i[2]*t-i[6]*n-i[10]*r}this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(e){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||e)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,e=!0);let t=this.children;for(let n=0,r=t.length;n<r;n++)t[n].updateMatrixWorld(e)}updateWorldMatrix(e,t,n=!1){let r=this.parent;if(e===!0&&r!==null&&r.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||n)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,n=!0),t===!0){let e=this.children;for(let t=0,r=e.length;t<r;t++)e[t].updateWorldMatrix(!1,!0,n)}}toJSON(e){let t=e===void 0||typeof e==`string`,n={};t&&(e={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},n.metadata={version:4.7,type:`Object`,generator:`Object3D.toJSON`});let r={};r.uuid=this.uuid,r.type=this.type,this.name!==``&&(r.name=this.name),this.castShadow===!0&&(r.castShadow=!0),this.receiveShadow===!0&&(r.receiveShadow=!0),this.visible===!1&&(r.visible=!1),this.frustumCulled===!1&&(r.frustumCulled=!1),this.renderOrder!==0&&(r.renderOrder=this.renderOrder),this.static!==!1&&(r.static=this.static),Object.keys(this.userData).length>0&&(r.userData=this.userData),r.layers=this.layers.mask,r.matrix=this.matrix.toArray(),r.up=this.up.toArray(),this.pivot!==null&&(r.pivot=this.pivot.toArray()),this.matrixAutoUpdate===!1&&(r.matrixAutoUpdate=!1),this.morphTargetDictionary!==void 0&&(r.morphTargetDictionary=Object.assign({},this.morphTargetDictionary)),this.morphTargetInfluences!==void 0&&(r.morphTargetInfluences=this.morphTargetInfluences.slice()),this.isInstancedMesh&&(r.type=`InstancedMesh`,r.count=this.count,r.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(r.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(r.type=`BatchedMesh`,r.perObjectFrustumCulled=this.perObjectFrustumCulled,r.sortObjects=this.sortObjects,r.drawRanges=this._drawRanges,r.reservedRanges=this._reservedRanges,r.geometryInfo=this._geometryInfo.map(e=>({...e,boundingBox:e.boundingBox?e.boundingBox.toJSON():void 0,boundingSphere:e.boundingSphere?e.boundingSphere.toJSON():void 0})),r.instanceInfo=this._instanceInfo.map(e=>({...e})),r.availableInstanceIds=this._availableInstanceIds.slice(),r.availableGeometryIds=this._availableGeometryIds.slice(),r.nextIndexStart=this._nextIndexStart,r.nextVertexStart=this._nextVertexStart,r.geometryCount=this._geometryCount,r.maxInstanceCount=this._maxInstanceCount,r.maxVertexCount=this._maxVertexCount,r.maxIndexCount=this._maxIndexCount,r.geometryInitialized=this._geometryInitialized,r.matricesTexture=this._matricesTexture.toJSON(e),r.indirectTexture=this._indirectTexture.toJSON(e),this._colorsTexture!==null&&(r.colorsTexture=this._colorsTexture.toJSON(e)),this.boundingSphere!==null&&(r.boundingSphere=this.boundingSphere.toJSON()),this.boundingBox!==null&&(r.boundingBox=this.boundingBox.toJSON()));function i(t,n){return t[n.uuid]===void 0&&(t[n.uuid]=n.toJSON(e)),n.uuid}if(this.isScene)this.background&&(this.background.isColor?r.background=this.background.toJSON():this.background.isTexture&&(r.background=this.background.toJSON(e).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(r.environment=this.environment.toJSON(e).uuid);else if(this.isMesh||this.isLine||this.isPoints){r.geometry=i(e.geometries,this.geometry);let t=this.geometry.parameters;if(t!==void 0&&t.shapes!==void 0){let n=t.shapes;if(Array.isArray(n))for(let t=0,r=n.length;t<r;t++){let r=n[t];i(e.shapes,r)}else i(e.shapes,n)}}if(this.isSkinnedMesh&&(r.bindMode=this.bindMode,r.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(i(e.skeletons,this.skeleton),r.skeleton=this.skeleton.uuid)),this.material!==void 0){if(Array.isArray(this.material)){let t=[];for(let n=0,r=this.material.length;n<r;n++)t.push(i(e.materials,this.material[n]));r.material=t}else r.material=i(e.materials,this.material)}if(this.children.length>0){r.children=[];for(let t=0;t<this.children.length;t++)r.children.push(this.children[t].toJSON(e).object)}if(this.animations.length>0){r.animations=[];for(let t=0;t<this.animations.length;t++){let n=this.animations[t];r.animations.push(i(e.animations,n))}}if(t){let t=a(e.geometries),r=a(e.materials),i=a(e.textures),o=a(e.images),s=a(e.shapes),c=a(e.skeletons),l=a(e.animations),u=a(e.nodes);t.length>0&&(n.geometries=t),r.length>0&&(n.materials=r),i.length>0&&(n.textures=i),o.length>0&&(n.images=o),s.length>0&&(n.shapes=s),c.length>0&&(n.skeletons=c),l.length>0&&(n.animations=l),u.length>0&&(n.nodes=u)}return n.object=r,n;function a(e){let t=[];for(let n in e){let r=e[n];delete r.metadata,t.push(r)}return t}}clone(e){return new this.constructor().copy(this,e)}copy(e,t=!0){if(this.name=e.name,this.up.copy(e.up),this.position.copy(e.position),this.rotation.order=e.rotation.order,this.quaternion.copy(e.quaternion),this.scale.copy(e.scale),this.pivot=e.pivot===null?null:e.pivot.clone(),this.matrix.copy(e.matrix),this.matrixWorld.copy(e.matrixWorld),this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrixWorldAutoUpdate=e.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=e.matrixWorldNeedsUpdate,this.layers.mask=e.layers.mask,this.visible=e.visible,this.castShadow=e.castShadow,this.receiveShadow=e.receiveShadow,this.frustumCulled=e.frustumCulled,this.renderOrder=e.renderOrder,this.static=e.static,this.animations=e.animations.slice(),this.userData=JSON.parse(JSON.stringify(e.userData)),t===!0)for(let t=0;t<e.children.length;t++){let n=e.children[t];this.add(n.clone())}return this}};En.DEFAULT_UP=new W(0,1,0),En.DEFAULT_MATRIX_AUTO_UPDATE=!0,En.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;var Dn=class extends En{constructor(){super(),this.isGroup=!0,this.type=`Group`}},On={type:`move`},kn=class{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new Dn,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new Dn,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new W,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new W),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new Dn,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new W,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new W,this._grip.eventsEnabled=!1),this._grip}dispatchEvent(e){return this._targetRay!==null&&this._targetRay.dispatchEvent(e),this._grip!==null&&this._grip.dispatchEvent(e),this._hand!==null&&this._hand.dispatchEvent(e),this}connect(e){if(e&&e.hand){let t=this._hand;if(t)for(let n of e.hand.values())this._getHandJoint(t,n)}return this.dispatchEvent({type:`connected`,data:e}),this}disconnect(e){return this.dispatchEvent({type:`disconnected`,data:e}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(e,t,n){let r=null,i=null,a=null,o=this._targetRay,s=this._grip,c=this._hand;if(e&&t.session.visibilityState!==`visible-blurred`){if(c&&e.hand){a=!0;for(let r of e.hand.values()){let e=t.getJointPose(r,n),i=this._getHandJoint(c,r);e!==null&&(i.matrix.fromArray(e.transform.matrix),i.matrix.decompose(i.position,i.rotation,i.scale),i.matrixWorldNeedsUpdate=!0,i.jointRadius=e.radius),i.visible=e!==null}let r=c.joints[`index-finger-tip`],i=c.joints[`thumb-tip`],o=r.position.distanceTo(i.position);c.inputState.pinching&&o>.025?(c.inputState.pinching=!1,this.dispatchEvent({type:`pinchend`,handedness:e.handedness,target:this})):!c.inputState.pinching&&o<=.015&&(c.inputState.pinching=!0,this.dispatchEvent({type:`pinchstart`,handedness:e.handedness,target:this}))}else s!==null&&e.gripSpace&&(i=t.getPose(e.gripSpace,n),i!==null&&(s.matrix.fromArray(i.transform.matrix),s.matrix.decompose(s.position,s.rotation,s.scale),s.matrixWorldNeedsUpdate=!0,i.linearVelocity?(s.hasLinearVelocity=!0,s.linearVelocity.copy(i.linearVelocity)):s.hasLinearVelocity=!1,i.angularVelocity?(s.hasAngularVelocity=!0,s.angularVelocity.copy(i.angularVelocity)):s.hasAngularVelocity=!1,s.eventsEnabled&&s.dispatchEvent({type:`gripUpdated`,data:e,target:this})));o!==null&&(r=t.getPose(e.targetRaySpace,n),r===null&&i!==null&&(r=i),r!==null&&(o.matrix.fromArray(r.transform.matrix),o.matrix.decompose(o.position,o.rotation,o.scale),o.matrixWorldNeedsUpdate=!0,r.linearVelocity?(o.hasLinearVelocity=!0,o.linearVelocity.copy(r.linearVelocity)):o.hasLinearVelocity=!1,r.angularVelocity?(o.hasAngularVelocity=!0,o.angularVelocity.copy(r.angularVelocity)):o.hasAngularVelocity=!1,this.dispatchEvent(On)))}return o!==null&&(o.visible=r!==null),s!==null&&(s.visible=i!==null),c!==null&&(c.visible=a!==null),this}_getHandJoint(e,t){if(e.joints[t.jointName]===void 0){let n=new Dn;n.matrixAutoUpdate=!1,n.visible=!1,e.joints[t.jointName]=n,e.add(n)}return e.joints[t.jointName]}},An={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},jn={h:0,s:0,l:0},Mn={h:0,s:0,l:0};function Nn(e,t,n){return n<0&&(n+=1),n>1&&--n,n<1/6?e+(t-e)*6*n:n<1/2?t:n<2/3?e+(t-e)*6*(2/3-n):e}var J=class{constructor(e,t,n){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(e,t,n)}set(e,t,n){if(t===void 0&&n===void 0){let t=e;t&&t.isColor?this.copy(t):typeof t==`number`?this.setHex(t):typeof t==`string`&&this.setStyle(t)}else this.setRGB(e,t,n);return this}setScalar(e){return this.r=e,this.g=e,this.b=e,this}setHex(e,t=Ue){return e=Math.floor(e),this.r=(e>>16&255)/255,this.g=(e>>8&255)/255,this.b=(e&255)/255,K.colorSpaceToWorking(this,t),this}setRGB(e,t,n,r=K.workingColorSpace){return this.r=e,this.g=t,this.b=n,K.colorSpaceToWorking(this,r),this}setHSL(e,t,n,r=K.workingColorSpace){if(e=ut(e,1),t=H(t,0,1),n=H(n,0,1),t===0)this.r=this.g=this.b=n;else{let r=n<=.5?n*(1+t):n+t-n*t,i=2*n-r;this.r=Nn(i,r,e+1/3),this.g=Nn(i,r,e),this.b=Nn(i,r,e-1/3)}return K.colorSpaceToWorking(this,r),this}setStyle(e,t=Ue){function n(t){t!==void 0&&parseFloat(t)<1&&B(`Color: Alpha component of `+e+` will be ignored.`)}let r;if(r=/^(\w+)\(([^\)]*)\)/.exec(e)){let i,a=r[1],o=r[2];switch(a){case`rgb`:case`rgba`:if(i=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(i[4]),this.setRGB(Math.min(255,parseInt(i[1],10))/255,Math.min(255,parseInt(i[2],10))/255,Math.min(255,parseInt(i[3],10))/255,t);if(i=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(i[4]),this.setRGB(Math.min(100,parseInt(i[1],10))/100,Math.min(100,parseInt(i[2],10))/100,Math.min(100,parseInt(i[3],10))/100,t);break;case`hsl`:case`hsla`:if(i=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(i[4]),this.setHSL(parseFloat(i[1])/360,parseFloat(i[2])/100,parseFloat(i[3])/100,t);break;default:B(`Color: Unknown color model `+e)}}else if(r=/^\#([A-Fa-f\d]+)$/.exec(e)){let n=r[1],i=n.length;if(i===3)return this.setRGB(parseInt(n.charAt(0),16)/15,parseInt(n.charAt(1),16)/15,parseInt(n.charAt(2),16)/15,t);if(i===6)return this.setHex(parseInt(n,16),t);B(`Color: Invalid hex color `+e)}else if(e&&e.length>0)return this.setColorName(e,t);return this}setColorName(e,t=Ue){let n=An[e.toLowerCase()];return n===void 0?B(`Color: Unknown color `+e):this.setHex(n,t),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(e){return this.r=e.r,this.g=e.g,this.b=e.b,this}copySRGBToLinear(e){return this.r=Rt(e.r),this.g=Rt(e.g),this.b=Rt(e.b),this}copyLinearToSRGB(e){return this.r=zt(e.r),this.g=zt(e.g),this.b=zt(e.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(e=Ue){return K.workingToColorSpace(Pn.copy(this),e),Math.round(H(Pn.r*255,0,255))*65536+Math.round(H(Pn.g*255,0,255))*256+Math.round(H(Pn.b*255,0,255))}getHexString(e=Ue){return(`000000`+this.getHex(e).toString(16)).slice(-6)}getHSL(e,t=K.workingColorSpace){K.workingToColorSpace(Pn.copy(this),t);let n=Pn.r,r=Pn.g,i=Pn.b,a=Math.max(n,r,i),o=Math.min(n,r,i),s,c,l=(o+a)/2;if(o===a)s=0,c=0;else{let e=a-o;switch(c=l<=.5?e/(a+o):e/(2-a-o),a){case n:s=(r-i)/e+(r<i?6:0);break;case r:s=(i-n)/e+2;break;case i:s=(n-r)/e+4}s/=6}return e.h=s,e.s=c,e.l=l,e}getRGB(e,t=K.workingColorSpace){return K.workingToColorSpace(Pn.copy(this),t),e.r=Pn.r,e.g=Pn.g,e.b=Pn.b,e}getStyle(e=Ue){K.workingToColorSpace(Pn.copy(this),e);let t=Pn.r,n=Pn.g,r=Pn.b;return e===`srgb`?`rgb(${Math.round(t*255)},${Math.round(n*255)},${Math.round(r*255)})`:`color(${e} ${t.toFixed(3)} ${n.toFixed(3)} ${r.toFixed(3)})`}offsetHSL(e,t,n){return this.getHSL(jn),this.setHSL(jn.h+e,jn.s+t,jn.l+n)}add(e){return this.r+=e.r,this.g+=e.g,this.b+=e.b,this}addColors(e,t){return this.r=e.r+t.r,this.g=e.g+t.g,this.b=e.b+t.b,this}addScalar(e){return this.r+=e,this.g+=e,this.b+=e,this}sub(e){return this.r=Math.max(0,this.r-e.r),this.g=Math.max(0,this.g-e.g),this.b=Math.max(0,this.b-e.b),this}multiply(e){return this.r*=e.r,this.g*=e.g,this.b*=e.b,this}multiplyScalar(e){return this.r*=e,this.g*=e,this.b*=e,this}lerp(e,t){return this.r+=(e.r-this.r)*t,this.g+=(e.g-this.g)*t,this.b+=(e.b-this.b)*t,this}lerpColors(e,t,n){return this.r=e.r+(t.r-e.r)*n,this.g=e.g+(t.g-e.g)*n,this.b=e.b+(t.b-e.b)*n,this}lerpHSL(e,t){this.getHSL(jn),e.getHSL(Mn);let n=pt(jn.h,Mn.h,t),r=pt(jn.s,Mn.s,t),i=pt(jn.l,Mn.l,t);return this.setHSL(n,r,i),this}setFromVector3(e){return this.r=e.x,this.g=e.y,this.b=e.z,this}applyMatrix3(e){let t=this.r,n=this.g,r=this.b,i=e.elements;return this.r=i[0]*t+i[3]*n+i[6]*r,this.g=i[1]*t+i[4]*n+i[7]*r,this.b=i[2]*t+i[5]*n+i[8]*r,this}equals(e){return e.r===this.r&&e.g===this.g&&e.b===this.b}fromArray(e,t=0){return this.r=e[t],this.g=e[t+1],this.b=e[t+2],this}toArray(e=[],t=0){return e[t]=this.r,e[t+1]=this.g,e[t+2]=this.b,e}fromBufferAttribute(e,t){return this.r=e.getX(t),this.g=e.getY(t),this.b=e.getZ(t),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}},Pn=new J;J.NAMES=An;var Fn=class extends En{constructor(){super(),this.isScene=!0,this.type=`Scene`,this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new ln,this.environmentIntensity=1,this.environmentRotation=new ln,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<`u`&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent(`observe`,{detail:this}))}copy(e,t){return super.copy(e,t),e.background!==null&&(this.background=e.background.clone()),e.environment!==null&&(this.environment=e.environment.clone()),e.fog!==null&&(this.fog=e.fog.clone()),this.backgroundBlurriness=e.backgroundBlurriness,this.backgroundIntensity=e.backgroundIntensity,this.backgroundRotation.copy(e.backgroundRotation),this.environmentIntensity=e.environmentIntensity,this.environmentRotation.copy(e.environmentRotation),e.overrideMaterial!==null&&(this.overrideMaterial=e.overrideMaterial.clone()),this.matrixAutoUpdate=e.matrixAutoUpdate,this}toJSON(e){let t=super.toJSON(e);return this.fog!==null&&(t.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(t.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(t.object.backgroundIntensity=this.backgroundIntensity),t.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(t.object.environmentIntensity=this.environmentIntensity),t.object.environmentRotation=this.environmentRotation.toArray(),t}},In=new W,Ln=new W,Rn=new W,zn=new W,Bn=new W,Vn=new W,Hn=new W,Un=new W,Wn=new W,Gn=new W,Kn=new Jt,qn=new Jt,Jn=new Jt,Yn=class e{constructor(e=new W,t=new W,n=new W){this.a=e,this.b=t,this.c=n}static getNormal(e,t,n,r){r.subVectors(n,t),In.subVectors(e,t),r.cross(In);let i=r.lengthSq();return i>0?r.multiplyScalar(1/Math.sqrt(i)):r.set(0,0,0)}static getBarycoord(e,t,n,r,i){In.subVectors(r,t),Ln.subVectors(n,t),Rn.subVectors(e,t);let a=In.dot(In),o=In.dot(Ln),s=In.dot(Rn),c=Ln.dot(Ln),l=Ln.dot(Rn),u=a*c-o*o;if(u===0)return i.set(0,0,0),null;let d=1/u,f=(c*s-o*l)*d,p=(a*l-o*s)*d;return i.set(1-f-p,p,f)}static containsPoint(e,t,n,r){return this.getBarycoord(e,t,n,r,zn)!==null&&zn.x>=0&&zn.y>=0&&zn.x+zn.y<=1}static getInterpolation(e,t,n,r,i,a,o,s){return this.getBarycoord(e,t,n,r,zn)===null?(s.x=0,s.y=0,`z`in s&&(s.z=0),`w`in s&&(s.w=0),null):(s.setScalar(0),s.addScaledVector(i,zn.x),s.addScaledVector(a,zn.y),s.addScaledVector(o,zn.z),s)}static getInterpolatedAttribute(e,t,n,r,i,a){return Kn.setScalar(0),qn.setScalar(0),Jn.setScalar(0),Kn.fromBufferAttribute(e,t),qn.fromBufferAttribute(e,n),Jn.fromBufferAttribute(e,r),a.setScalar(0),a.addScaledVector(Kn,i.x),a.addScaledVector(qn,i.y),a.addScaledVector(Jn,i.z),a}static isFrontFacing(e,t,n,r){return In.subVectors(n,t),Ln.subVectors(e,t),In.cross(Ln).dot(r)<0}set(e,t,n){return this.a.copy(e),this.b.copy(t),this.c.copy(n),this}setFromPointsAndIndices(e,t,n,r){return this.a.copy(e[t]),this.b.copy(e[n]),this.c.copy(e[r]),this}setFromAttributeAndIndices(e,t,n,r){return this.a.fromBufferAttribute(e,t),this.b.fromBufferAttribute(e,n),this.c.fromBufferAttribute(e,r),this}clone(){return new this.constructor().copy(this)}copy(e){return this.a.copy(e.a),this.b.copy(e.b),this.c.copy(e.c),this}getArea(){return In.subVectors(this.c,this.b),Ln.subVectors(this.a,this.b),In.cross(Ln).length()*.5}getMidpoint(e){return e.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(t){return e.getNormal(this.a,this.b,this.c,t)}getPlane(e){return e.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(t,n){return e.getBarycoord(t,this.a,this.b,this.c,n)}getInterpolation(t,n,r,i,a){return e.getInterpolation(t,this.a,this.b,this.c,n,r,i,a)}containsPoint(t){return e.containsPoint(t,this.a,this.b,this.c)}isFrontFacing(t){return e.isFrontFacing(this.a,this.b,this.c,t)}intersectsBox(e){return e.intersectsTriangle(this)}closestPointToPoint(e,t){let n=this.a,r=this.b,i=this.c,a,o;Bn.subVectors(r,n),Vn.subVectors(i,n),Un.subVectors(e,n);let s=Bn.dot(Un),c=Vn.dot(Un);if(s<=0&&c<=0)return t.copy(n);Wn.subVectors(e,r);let l=Bn.dot(Wn),u=Vn.dot(Wn);if(l>=0&&u<=l)return t.copy(r);let d=s*u-l*c;if(d<=0&&s>=0&&l<=0)return a=s/(s-l),t.copy(n).addScaledVector(Bn,a);Gn.subVectors(e,i);let f=Bn.dot(Gn),p=Vn.dot(Gn);if(p>=0&&f<=p)return t.copy(i);let m=f*c-s*p;if(m<=0&&c>=0&&p<=0)return o=c/(c-p),t.copy(n).addScaledVector(Vn,o);let h=l*p-f*u;if(h<=0&&u-l>=0&&f-p>=0)return Hn.subVectors(i,r),o=(u-l)/(u-l+(f-p)),t.copy(r).addScaledVector(Hn,o);let g=1/(h+m+d);return a=m*g,o=d*g,t.copy(n).addScaledVector(Bn,a).addScaledVector(Vn,o)}equals(e){return e.a.equals(this.a)&&e.b.equals(this.b)&&e.c.equals(this.c)}},Xn=class{constructor(e=new W(1/0,1/0,1/0),t=new W(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=e,this.max=t}set(e,t){return this.min.copy(e),this.max.copy(t),this}setFromArray(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t+=3)this.expandByPoint(Qn.fromArray(e,t));return this}setFromBufferAttribute(e){this.makeEmpty();for(let t=0,n=e.count;t<n;t++)this.expandByPoint(Qn.fromBufferAttribute(e,t));return this}setFromPoints(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t++)this.expandByPoint(e[t]);return this}setFromCenterAndSize(e,t){let n=Qn.copy(t).multiplyScalar(.5);return this.min.copy(e).sub(n),this.max.copy(e).add(n),this}setFromObject(e,t=!1){return this.makeEmpty(),this.expandByObject(e,t)}clone(){return new this.constructor().copy(this)}copy(e){return this.min.copy(e.min),this.max.copy(e.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(e){return this.isEmpty()?e.set(0,0,0):e.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(e){return this.isEmpty()?e.set(0,0,0):e.subVectors(this.max,this.min)}expandByPoint(e){return this.min.min(e),this.max.max(e),this}expandByVector(e){return this.min.sub(e),this.max.add(e),this}expandByScalar(e){return this.min.addScalar(-e),this.max.addScalar(e),this}expandByObject(e,t=!1){e.updateWorldMatrix(!1,!1);let n=e.geometry;if(n!==void 0){let r=n.getAttribute(`position`);if(t===!0&&r!==void 0&&e.isInstancedMesh!==!0)for(let t=0,n=r.count;t<n;t++)e.isMesh===!0?e.getVertexPosition(t,Qn):Qn.fromBufferAttribute(r,t),Qn.applyMatrix4(e.matrixWorld),this.expandByPoint(Qn);else e.boundingBox===void 0?(n.boundingBox===null&&n.computeBoundingBox(),$n.copy(n.boundingBox)):(e.boundingBox===null&&e.computeBoundingBox(),$n.copy(e.boundingBox)),$n.applyMatrix4(e.matrixWorld),this.union($n)}let r=e.children;for(let e=0,n=r.length;e<n;e++)this.expandByObject(r[e],t);return this}containsPoint(e){return e.x>=this.min.x&&e.x<=this.max.x&&e.y>=this.min.y&&e.y<=this.max.y&&e.z>=this.min.z&&e.z<=this.max.z}containsBox(e){return this.min.x<=e.min.x&&e.max.x<=this.max.x&&this.min.y<=e.min.y&&e.max.y<=this.max.y&&this.min.z<=e.min.z&&e.max.z<=this.max.z}getParameter(e,t){return t.set((e.x-this.min.x)/(this.max.x-this.min.x),(e.y-this.min.y)/(this.max.y-this.min.y),(e.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(e){return e.max.x>=this.min.x&&e.min.x<=this.max.x&&e.max.y>=this.min.y&&e.min.y<=this.max.y&&e.max.z>=this.min.z&&e.min.z<=this.max.z}intersectsSphere(e){return this.clampPoint(e.center,Qn),Qn.distanceToSquared(e.center)<=e.radius*e.radius}intersectsPlane(e){let t,n;return e.normal.x>0?(t=e.normal.x*this.min.x,n=e.normal.x*this.max.x):(t=e.normal.x*this.max.x,n=e.normal.x*this.min.x),e.normal.y>0?(t+=e.normal.y*this.min.y,n+=e.normal.y*this.max.y):(t+=e.normal.y*this.max.y,n+=e.normal.y*this.min.y),e.normal.z>0?(t+=e.normal.z*this.min.z,n+=e.normal.z*this.max.z):(t+=e.normal.z*this.max.z,n+=e.normal.z*this.min.z),t<=-e.constant&&n>=-e.constant}intersectsTriangle(e){if(this.isEmpty())return!1;this.getCenter(or),sr.subVectors(this.max,or),er.subVectors(e.a,or),tr.subVectors(e.b,or),nr.subVectors(e.c,or),rr.subVectors(tr,er),ir.subVectors(nr,tr),ar.subVectors(er,nr);let t=[0,-rr.z,rr.y,0,-ir.z,ir.y,0,-ar.z,ar.y,rr.z,0,-rr.x,ir.z,0,-ir.x,ar.z,0,-ar.x,-rr.y,rr.x,0,-ir.y,ir.x,0,-ar.y,ar.x,0];return!ur(t,er,tr,nr,sr)||(t=[1,0,0,0,1,0,0,0,1],!ur(t,er,tr,nr,sr))?!1:(cr.crossVectors(rr,ir),t=[cr.x,cr.y,cr.z],ur(t,er,tr,nr,sr))}clampPoint(e,t){return t.copy(e).clamp(this.min,this.max)}distanceToPoint(e){return this.clampPoint(e,Qn).distanceTo(e)}getBoundingSphere(e){return this.isEmpty()?e.makeEmpty():(this.getCenter(e.center),e.radius=this.getSize(Qn).length()*.5),e}intersect(e){return this.min.max(e.min),this.max.min(e.max),this.isEmpty()&&this.makeEmpty(),this}union(e){return this.min.min(e.min),this.max.max(e.max),this}applyMatrix4(e){return this.isEmpty()?this:(Zn[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(e),Zn[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(e),Zn[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(e),Zn[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(e),Zn[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(e),Zn[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(e),Zn[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(e),Zn[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(e),this.setFromPoints(Zn),this)}translate(e){return this.min.add(e),this.max.add(e),this}equals(e){return e.min.equals(this.min)&&e.max.equals(this.max)}toJSON(){return{min:this.min.toArray(),max:this.max.toArray()}}fromJSON(e){return this.min.fromArray(e.min),this.max.fromArray(e.max),this}},Zn=[new W,new W,new W,new W,new W,new W,new W,new W],Qn=new W,$n=new Xn,er=new W,tr=new W,nr=new W,rr=new W,ir=new W,ar=new W,or=new W,sr=new W,cr=new W,lr=new W;function ur(e,t,n,r,i){for(let a=0,o=e.length-3;a<=o;a+=3){lr.fromArray(e,a);let o=i.x*Math.abs(lr.x)+i.y*Math.abs(lr.y)+i.z*Math.abs(lr.z),s=t.dot(lr),c=n.dot(lr),l=r.dot(lr);if(Math.max(-Math.max(s,c,l),Math.min(s,c,l))>o)return!1}return!0}var dr=new W,fr=new U,pr=0,mr=class extends it{constructor(e,t,n=!1){if(super(),Array.isArray(e))throw TypeError(`THREE.BufferAttribute: array should be a Typed Array.`);this.isBufferAttribute=!0,Object.defineProperty(this,"id",{value:pr++}),this.name=``,this.array=e,this.itemSize=t,this.count=e===void 0?0:e.length/t,this.normalized=n,this.usage=Je,this.updateRanges=[],this.gpuType=v,this.version=0}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.name=e.name,this.array=new e.array.constructor(e.array),this.itemSize=e.itemSize,this.count=e.count,this.normalized=e.normalized,this.usage=e.usage,this.gpuType=e.gpuType,this}copyAt(e,t,n){e*=this.itemSize,n*=t.itemSize;for(let r=0,i=this.itemSize;r<i;r++)this.array[e+r]=t.array[n+r];return this}copyArray(e){return this.array.set(e),this}applyMatrix3(e){if(this.itemSize===2)for(let t=0,n=this.count;t<n;t++)fr.fromBufferAttribute(this,t),fr.applyMatrix3(e),this.setXY(t,fr.x,fr.y);else if(this.itemSize===3)for(let t=0,n=this.count;t<n;t++)dr.fromBufferAttribute(this,t),dr.applyMatrix3(e),this.setXYZ(t,dr.x,dr.y,dr.z);return this}applyMatrix4(e){for(let t=0,n=this.count;t<n;t++)dr.fromBufferAttribute(this,t),dr.applyMatrix4(e),this.setXYZ(t,dr.x,dr.y,dr.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)dr.fromBufferAttribute(this,t),dr.applyNormalMatrix(e),this.setXYZ(t,dr.x,dr.y,dr.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)dr.fromBufferAttribute(this,t),dr.transformDirection(e),this.setXYZ(t,dr.x,dr.y,dr.z);return this}set(e,t=0){return this.array.set(e,t),this}getComponent(e,t){let n=this.array[e*this.itemSize+t];return this.normalized&&(n=Ot(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=kt(n,this.array)),this.array[e*this.itemSize+t]=n,this}getX(e){let t=this.array[e*this.itemSize];return this.normalized&&(t=Ot(t,this.array)),t}setX(e,t){return this.normalized&&(t=kt(t,this.array)),this.array[e*this.itemSize]=t,this}getY(e){let t=this.array[e*this.itemSize+1];return this.normalized&&(t=Ot(t,this.array)),t}setY(e,t){return this.normalized&&(t=kt(t,this.array)),this.array[e*this.itemSize+1]=t,this}getZ(e){let t=this.array[e*this.itemSize+2];return this.normalized&&(t=Ot(t,this.array)),t}setZ(e,t){return this.normalized&&(t=kt(t,this.array)),this.array[e*this.itemSize+2]=t,this}getW(e){let t=this.array[e*this.itemSize+3];return this.normalized&&(t=Ot(t,this.array)),t}setW(e,t){return this.normalized&&(t=kt(t,this.array)),this.array[e*this.itemSize+3]=t,this}setXY(e,t,n){return e*=this.itemSize,this.normalized&&(t=kt(t,this.array),n=kt(n,this.array)),this.array[e+0]=t,this.array[e+1]=n,this}setXYZ(e,t,n,r){return e*=this.itemSize,this.normalized&&(t=kt(t,this.array),n=kt(n,this.array),r=kt(r,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=r,this}setXYZW(e,t,n,r,i){return e*=this.itemSize,this.normalized&&(t=kt(t,this.array),n=kt(n,this.array),r=kt(r,this.array),i=kt(i,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=r,this.array[e+3]=i,this}onUpload(e){return this.onUploadCallback=e,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){let e={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==``&&(e.name=this.name),this.usage!==35044&&(e.usage=this.usage),e}dispose(){this.dispatchEvent({type:`dispose`})}},hr=class extends mr{constructor(e,t,n){super(new Uint16Array(e),t,n)}},gr=class extends mr{constructor(e,t,n){super(new Uint32Array(e),t,n)}},_r=class extends mr{constructor(e,t,n){super(new Float32Array(e),t,n)}},vr=new Xn,yr=new W,br=new W,xr=class{constructor(e=new W,t=-1){this.isSphere=!0,this.center=e,this.radius=t}set(e,t){return this.center.copy(e),this.radius=t,this}setFromPoints(e,t){let n=this.center;t===void 0?vr.setFromPoints(e).getCenter(n):n.copy(t);let r=0;for(let t=0,i=e.length;t<i;t++)r=Math.max(r,n.distanceToSquared(e[t]));return this.radius=Math.sqrt(r),this}copy(e){return this.center.copy(e.center),this.radius=e.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(e){return e.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(e){return e.distanceTo(this.center)-this.radius}intersectsSphere(e){let t=this.radius+e.radius;return e.center.distanceToSquared(this.center)<=t*t}intersectsBox(e){return e.intersectsSphere(this)}intersectsPlane(e){return Math.abs(e.distanceToPoint(this.center))<=this.radius}clampPoint(e,t){let n=this.center.distanceToSquared(e);return t.copy(e),n>this.radius*this.radius&&(t.sub(this.center).normalize(),t.multiplyScalar(this.radius).add(this.center)),t}getBoundingBox(e){return this.isEmpty()?(e.makeEmpty(),e):(e.set(this.center,this.center),e.expandByScalar(this.radius),e)}applyMatrix4(e){return this.center.applyMatrix4(e),this.radius*=e.getMaxScaleOnAxis(),this}translate(e){return this.center.add(e),this}expandByPoint(e){if(this.isEmpty())return this.center.copy(e),this.radius=0,this;yr.subVectors(e,this.center);let t=yr.lengthSq();if(t>this.radius*this.radius){let e=Math.sqrt(t),n=(e-this.radius)*.5;this.center.addScaledVector(yr,n/e),this.radius+=n}return this}union(e){return e.isEmpty()?this:this.isEmpty()?(this.copy(e),this):(this.center.equals(e.center)===!0?this.radius=Math.max(this.radius,e.radius):(br.subVectors(e.center,this.center).setLength(e.radius),this.expandByPoint(yr.copy(e.center).add(br)),this.expandByPoint(yr.copy(e.center).sub(br))),this)}equals(e){return e.center.equals(this.center)&&e.radius===this.radius}clone(){return new this.constructor().copy(this)}toJSON(){return{radius:this.radius,center:this.center.toArray()}}fromJSON(e){return this.radius=e.radius,this.center.fromArray(e.center),this}},Sr=0,Y=new q,Cr=new En,wr=new W,Tr=new Xn,Er=new Xn,Dr=new W,Or=class e extends it{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:Sr++}),this.uuid=lt(),this.name=``,this.type=`BufferGeometry`,this.index=null,this.indirect=null,this.indirectOffset=0,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={},this._transformed=!1}getIndex(){return this.index}setIndex(e){return this.index=Array.isArray(e)?new(z(e)?gr:hr)(e,1):e,this}setIndirect(e,t=0){return this.indirect=e,this.indirectOffset=t,this}getIndirect(){return this.indirect}getAttribute(e){return this.attributes[e]}setAttribute(e,t){return this.attributes[e]=t,this}deleteAttribute(e){return delete this.attributes[e],this}hasAttribute(e){return this.attributes[e]!==void 0}addGroup(e,t,n=0){this.groups.push({start:e,count:t,materialIndex:n})}clearGroups(){this.groups=[]}setDrawRange(e,t){this.drawRange.start=e,this.drawRange.count=t}applyMatrix4(e){let t=this.attributes.position;t!==void 0&&(t.applyMatrix4(e),t.needsUpdate=!0);let n=this.attributes.normal;if(n!==void 0){let t=new G().getNormalMatrix(e);n.applyNormalMatrix(t),n.needsUpdate=!0}let r=this.attributes.tangent;return r!==void 0&&(r.transformDirection(e),r.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this._transformed=!0,this}applyQuaternion(e){return Y.makeRotationFromQuaternion(e),this.applyMatrix4(Y),this}rotateX(e){return Y.makeRotationX(e),this.applyMatrix4(Y),this}rotateY(e){return Y.makeRotationY(e),this.applyMatrix4(Y),this}rotateZ(e){return Y.makeRotationZ(e),this.applyMatrix4(Y),this}translate(e,t,n){return Y.makeTranslation(e,t,n),this.applyMatrix4(Y),this}scale(e,t,n){return Y.makeScale(e,t,n),this.applyMatrix4(Y),this}lookAt(e){return Cr.lookAt(e),Cr.updateMatrix(),this.applyMatrix4(Cr.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(wr).negate(),this.translate(wr.x,wr.y,wr.z),this}setFromPoints(e){let t=this.getAttribute(`position`);if(t===void 0){let t=[];for(let n=0,r=e.length;n<r;n++){let r=e[n];t.push(r.x,r.y,r.z||0)}this.setAttribute(`position`,new _r(t,3))}else{let n=Math.min(e.length,t.count);for(let r=0;r<n;r++){let n=e[r];t.setXYZ(r,n.x,n.y,n.z||0)}e.length>t.count&&B(`BufferGeometry: Buffer size too small for points data. Use .dispose() and create a new geometry.`),t.needsUpdate=!0}return this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new Xn);let e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){V(`BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.`,this),this.boundingBox.set(new W(-1/0,-1/0,-1/0),new W(1/0,1/0,1/0));return}if(e!==void 0){if(this.boundingBox.setFromBufferAttribute(e),t)for(let e=0,n=t.length;e<n;e++){let n=t[e];Tr.setFromBufferAttribute(n),this.morphTargetsRelative?(Dr.addVectors(this.boundingBox.min,Tr.min),this.boundingBox.expandByPoint(Dr),Dr.addVectors(this.boundingBox.max,Tr.max),this.boundingBox.expandByPoint(Dr)):(this.boundingBox.expandByPoint(Tr.min),this.boundingBox.expandByPoint(Tr.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&V(`BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.`,this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new xr);let e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){V(`BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.`,this),this.boundingSphere.set(new W,1/0);return}if(e){let n=this.boundingSphere.center;if(Tr.setFromBufferAttribute(e),t)for(let e=0,n=t.length;e<n;e++){let n=t[e];Er.setFromBufferAttribute(n),this.morphTargetsRelative?(Dr.addVectors(Tr.min,Er.min),Tr.expandByPoint(Dr),Dr.addVectors(Tr.max,Er.max),Tr.expandByPoint(Dr)):(Tr.expandByPoint(Er.min),Tr.expandByPoint(Er.max))}Tr.getCenter(n);let r=0;for(let t=0,i=e.count;t<i;t++)Dr.fromBufferAttribute(e,t),r=Math.max(r,n.distanceToSquared(Dr));if(t)for(let i=0,a=t.length;i<a;i++){let a=t[i],o=this.morphTargetsRelative;for(let t=0,i=a.count;t<i;t++)Dr.fromBufferAttribute(a,t),o&&(wr.fromBufferAttribute(e,t),Dr.add(wr)),r=Math.max(r,n.distanceToSquared(Dr))}this.boundingSphere.radius=Math.sqrt(r),isNaN(this.boundingSphere.radius)&&V(`BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.`,this)}}computeTangents(){let e=this.index,t=this.attributes;if(e===null||t.position===void 0||t.normal===void 0||t.uv===void 0){V(`BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)`);return}let n=t.position,r=t.normal,i=t.uv,a=this.getAttribute(`tangent`);(a===void 0||a.count!==n.count)&&(a=new mr(new Float32Array(4*n.count),4),this.setAttribute(`tangent`,a));let o=[],s=[];for(let e=0;e<n.count;e++)o[e]=new W,s[e]=new W;let c=new W,l=new W,u=new W,d=new U,f=new U,p=new U,m=new W,h=new W;function g(e,t,r){c.fromBufferAttribute(n,e),l.fromBufferAttribute(n,t),u.fromBufferAttribute(n,r),d.fromBufferAttribute(i,e),f.fromBufferAttribute(i,t),p.fromBufferAttribute(i,r),l.sub(c),u.sub(c),f.sub(d),p.sub(d);let a=1/(f.x*p.y-p.x*f.y);isFinite(a)&&(m.copy(l).multiplyScalar(p.y).addScaledVector(u,-f.y).multiplyScalar(a),h.copy(u).multiplyScalar(f.x).addScaledVector(l,-p.x).multiplyScalar(a),o[e].add(m),o[t].add(m),o[r].add(m),s[e].add(h),s[t].add(h),s[r].add(h))}let _=this.groups;_.length===0&&(_=[{start:0,count:e.count}]);for(let t=0,n=_.length;t<n;++t){let n=_[t],r=n.start,i=n.count;for(let t=r,n=r+i;t<n;t+=3)g(e.getX(t+0),e.getX(t+1),e.getX(t+2))}let v=new W,y=new W,b=new W,x=new W;function S(e){b.fromBufferAttribute(r,e),x.copy(b);let t=o[e];v.copy(t),v.sub(b.multiplyScalar(b.dot(t))).normalize(),y.crossVectors(x,t);let n=y.dot(s[e])<0?-1:1;a.setXYZW(e,v.x,v.y,v.z,n)}for(let t=0,n=_.length;t<n;++t){let n=_[t],r=n.start,i=n.count;for(let t=r,n=r+i;t<n;t+=3)S(e.getX(t+0)),S(e.getX(t+1)),S(e.getX(t+2))}this._transformed=!0}computeVertexNormals(){let e=this.index,t=this.getAttribute(`position`);if(t!==void 0){let n=this.getAttribute(`normal`);if(n===void 0||n.count!==t.count)n=new mr(new Float32Array(t.count*3),3),this.setAttribute(`normal`,n);else for(let e=0,t=n.count;e<t;e++)n.setXYZ(e,0,0,0);let r=new W,i=new W,a=new W,o=new W,s=new W,c=new W,l=new W,u=new W;if(e)for(let d=0,f=e.count;d<f;d+=3){let f=e.getX(d+0),p=e.getX(d+1),m=e.getX(d+2);r.fromBufferAttribute(t,f),i.fromBufferAttribute(t,p),a.fromBufferAttribute(t,m),l.subVectors(a,i),u.subVectors(r,i),l.cross(u),o.fromBufferAttribute(n,f),s.fromBufferAttribute(n,p),c.fromBufferAttribute(n,m),o.add(l),s.add(l),c.add(l),n.setXYZ(f,o.x,o.y,o.z),n.setXYZ(p,s.x,s.y,s.z),n.setXYZ(m,c.x,c.y,c.z)}else for(let e=0,o=t.count;e<o;e+=3)r.fromBufferAttribute(t,e+0),i.fromBufferAttribute(t,e+1),a.fromBufferAttribute(t,e+2),l.subVectors(a,i),u.subVectors(r,i),l.cross(u),n.setXYZ(e+0,l.x,l.y,l.z),n.setXYZ(e+1,l.x,l.y,l.z),n.setXYZ(e+2,l.x,l.y,l.z);this.normalizeNormals(),n.needsUpdate=!0}}normalizeNormals(){let e=this.attributes.normal;for(let t=0,n=e.count;t<n;t++)Dr.fromBufferAttribute(e,t),Dr.normalize(),e.setXYZ(t,Dr.x,Dr.y,Dr.z)}toNonIndexed(){function t(e,t){let n=e.array,r=e.itemSize,i=e.normalized,a=new n.constructor(t.length*r),o=0,s=0;for(let i=0,c=t.length;i<c;i++){o=e.isInterleavedBufferAttribute?t[i]*e.data.stride+e.offset:t[i]*r;for(let e=0;e<r;e++)a[s++]=n[o++]}return new mr(a,r,i)}if(this.index===null)return B(`BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed.`),this;let n=new e,r=this.index.array,i=this.attributes;for(let e in i){let a=i[e],o=t(a,r);n.setAttribute(e,o)}let a=this.morphAttributes;for(let e in a){let i=[],o=a[e];for(let e=0,n=o.length;e<n;e++){let n=o[e],a=t(n,r);i.push(a)}n.morphAttributes[e]=i}n.morphTargetsRelative=this.morphTargetsRelative;let o=this.groups;for(let e=0,t=o.length;e<t;e++){let t=o[e];n.addGroup(t.start,t.count,t.materialIndex)}return n}toJSON(){let e={metadata:{version:4.7,type:`BufferGeometry`,generator:`BufferGeometry.toJSON`}};if(e.uuid=this.uuid,e.type=this.parameters!==void 0&&this._transformed===!0?`BufferGeometry`:this.type,this.name!==``&&(e.name=this.name),Object.keys(this.userData).length>0&&(e.userData=this.userData),this.parameters!==void 0&&this._transformed!==!0){let t=this.parameters;for(let n in t)t[n]!==void 0&&(e[n]=t[n]);return e}e.data={attributes:{}};let t=this.index;t!==null&&(e.data.index={type:t.array.constructor.name,array:Array.prototype.slice.call(t.array)});let n=this.attributes;for(let t in n){let r=n[t];e.data.attributes[t]=r.toJSON(e.data)}let r={},i=!1;for(let t in this.morphAttributes){let n=this.morphAttributes[t],a=[];for(let t=0,r=n.length;t<r;t++){let r=n[t];a.push(r.toJSON(e.data))}a.length>0&&(r[t]=a,i=!0)}i&&(e.data.morphAttributes=r,e.data.morphTargetsRelative=this.morphTargetsRelative);let a=this.groups;a.length>0&&(e.data.groups=JSON.parse(JSON.stringify(a)));let o=this.boundingSphere;return o!==null&&(e.data.boundingSphere=o.toJSON()),e}clone(){return new this.constructor().copy(this)}copy(e){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;let t={};this.name=e.name;let n=e.index;n!==null&&this.setIndex(n.clone());let r=e.attributes;for(let e in r){let n=r[e];this.setAttribute(e,n.clone(t))}let i=e.morphAttributes;for(let e in i){let n=[],r=i[e];for(let e=0,i=r.length;e<i;e++)n.push(r[e].clone(t));this.morphAttributes[e]=n}this.morphTargetsRelative=e.morphTargetsRelative;let a=e.groups;for(let e=0,t=a.length;e<t;e++){let t=a[e];this.addGroup(t.start,t.count,t.materialIndex)}let o=e.boundingBox;o!==null&&(this.boundingBox=o.clone());let s=e.boundingSphere;return s!==null&&(this.boundingSphere=s.clone()),this.drawRange.start=e.drawRange.start,this.drawRange.count=e.drawRange.count,this.userData=e.userData,this._transformed=e._transformed,this}dispose(){this.dispatchEvent({type:`dispose`})}},kr=class{constructor(e,t){this.isInterleavedBuffer=!0,this.array=e,this.stride=t,this.count=e===void 0?0:e.length/t,this.usage=Je,this.updateRanges=[],this.version=0,this.uuid=lt()}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.array=new e.array.constructor(e.array),this.count=e.count,this.stride=e.stride,this.usage=e.usage,this}copyAt(e,t,n){e*=this.stride,n*=t.stride;for(let r=0,i=this.stride;r<i;r++)this.array[e+r]=t.array[n+r];return this}set(e,t=0){return this.array.set(e,t),this}clone(e){e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=lt()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=this.array.slice(0).buffer);let t=new this.array.constructor(e.arrayBuffers[this.array.buffer._uuid]),n=new this.constructor(t,this.stride);return n.setUsage(this.usage),n}onUpload(e){return this.onUploadCallback=e,this}toJSON(e){return e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=lt()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=Array.from(new Uint32Array(this.array.buffer))),{uuid:this.uuid,buffer:this.array.buffer._uuid,type:this.array.constructor.name,stride:this.stride}}},Ar=new W,jr=class e{constructor(e,t,n,r=!1){this.isInterleavedBufferAttribute=!0,this.name=``,this.data=e,this.itemSize=t,this.offset=n,this.normalized=r}get count(){return this.data.count}get array(){return this.data.array}set needsUpdate(e){this.data.needsUpdate=e}applyMatrix4(e){for(let t=0,n=this.data.count;t<n;t++)Ar.fromBufferAttribute(this,t),Ar.applyMatrix4(e),this.setXYZ(t,Ar.x,Ar.y,Ar.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)Ar.fromBufferAttribute(this,t),Ar.applyNormalMatrix(e),this.setXYZ(t,Ar.x,Ar.y,Ar.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)Ar.fromBufferAttribute(this,t),Ar.transformDirection(e),this.setXYZ(t,Ar.x,Ar.y,Ar.z);return this}getComponent(e,t){let n=this.array[e*this.data.stride+this.offset+t];return this.normalized&&(n=Ot(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=kt(n,this.array)),this.data.array[e*this.data.stride+this.offset+t]=n,this}setX(e,t){return this.normalized&&(t=kt(t,this.array)),this.data.array[e*this.data.stride+this.offset]=t,this}setY(e,t){return this.normalized&&(t=kt(t,this.array)),this.data.array[e*this.data.stride+this.offset+1]=t,this}setZ(e,t){return this.normalized&&(t=kt(t,this.array)),this.data.array[e*this.data.stride+this.offset+2]=t,this}setW(e,t){return this.normalized&&(t=kt(t,this.array)),this.data.array[e*this.data.stride+this.offset+3]=t,this}getX(e){let t=this.data.array[e*this.data.stride+this.offset];return this.normalized&&(t=Ot(t,this.array)),t}getY(e){let t=this.data.array[e*this.data.stride+this.offset+1];return this.normalized&&(t=Ot(t,this.array)),t}getZ(e){let t=this.data.array[e*this.data.stride+this.offset+2];return this.normalized&&(t=Ot(t,this.array)),t}getW(e){let t=this.data.array[e*this.data.stride+this.offset+3];return this.normalized&&(t=Ot(t,this.array)),t}setXY(e,t,n){return e=e*this.data.stride+this.offset,this.normalized&&(t=kt(t,this.array),n=kt(n,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this}setXYZ(e,t,n,r){return e=e*this.data.stride+this.offset,this.normalized&&(t=kt(t,this.array),n=kt(n,this.array),r=kt(r,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=r,this}setXYZW(e,t,n,r,i){return e=e*this.data.stride+this.offset,this.normalized&&(t=kt(t,this.array),n=kt(n,this.array),r=kt(r,this.array),i=kt(i,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=r,this.data.array[e+3]=i,this}clone(t){if(t===void 0){$e(`InterleavedBufferAttribute.clone(): Cloning an interleaved buffer attribute will de-interleave buffer data.`);let e=[];for(let t=0;t<this.count;t++){let n=t*this.data.stride+this.offset;for(let t=0;t<this.itemSize;t++)e.push(this.data.array[n+t])}return new mr(new this.array.constructor(e),this.itemSize,this.normalized)}return t.interleavedBuffers===void 0&&(t.interleavedBuffers={}),t.interleavedBuffers[this.data.uuid]===void 0&&(t.interleavedBuffers[this.data.uuid]=this.data.clone(t)),new e(t.interleavedBuffers[this.data.uuid],this.itemSize,this.offset,this.normalized)}toJSON(e){if(e===void 0){$e(`InterleavedBufferAttribute.toJSON(): Serializing an interleaved buffer attribute will de-interleave buffer data.`);let e=[];for(let t=0;t<this.count;t++){let n=t*this.data.stride+this.offset;for(let t=0;t<this.itemSize;t++)e.push(this.data.array[n+t])}return{itemSize:this.itemSize,type:this.array.constructor.name,array:e,normalized:this.normalized}}return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.toJSON(e)),{isInterleavedBufferAttribute:!0,itemSize:this.itemSize,data:this.data.uuid,offset:this.offset,normalized:this.normalized}}},Mr=0,Nr=class extends it{constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:Mr++}),this.uuid=lt(),this.name=``,this.type=`Material`,this.blending=1,this.side=0,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=204,this.blendDst=205,this.blendEquation=100,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new J(0,0,0),this.blendAlpha=0,this.depthFunc=3,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=519,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=qe,this.stencilZFail=qe,this.stencilZPass=qe,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.allowOverride=!0,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(e){this._alphaTest>0!=e>0&&this.version++,this._alphaTest=e}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(e){if(e!==void 0)for(let t in e){let n=e[t];if(n===void 0){B(`Material: parameter '${t}' has value of undefined.`);continue}let r=this[t];if(r===void 0){B(`Material: '${t}' is not a property of THREE.${this.type}.`);continue}r&&r.isColor?r.set(n):r&&r.isVector2&&n&&n.isVector2||r&&r.isEuler&&n&&n.isEuler||r&&r.isVector3&&n&&n.isVector3?r.copy(n):this[t]=n}}toJSON(e){let t=e===void 0||typeof e==`string`;t&&(e={textures:{},images:{}});let n={metadata:{version:4.7,type:`Material`,generator:`Material.toJSON`}};n.uuid=this.uuid,n.type=this.type,this.name!==``&&(n.name=this.name),this.color&&this.color.isColor&&(n.color=this.color.getHex()),this.roughness!==void 0&&(n.roughness=this.roughness),this.metalness!==void 0&&(n.metalness=this.metalness),this.sheen!==void 0&&(n.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(n.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(n.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(n.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(n.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(n.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(n.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(n.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(n.shininess=this.shininess),this.clearcoat!==void 0&&(n.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(n.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(n.clearcoatMap=this.clearcoatMap.toJSON(e).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(n.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(e).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(n.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(e).uuid,n.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.sheenColorMap&&this.sheenColorMap.isTexture&&(n.sheenColorMap=this.sheenColorMap.toJSON(e).uuid),this.sheenRoughnessMap&&this.sheenRoughnessMap.isTexture&&(n.sheenRoughnessMap=this.sheenRoughnessMap.toJSON(e).uuid),this.dispersion!==void 0&&(n.dispersion=this.dispersion),this.iridescence!==void 0&&(n.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(n.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(n.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(n.iridescenceMap=this.iridescenceMap.toJSON(e).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(n.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(e).uuid),this.anisotropy!==void 0&&(n.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(n.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(n.anisotropyMap=this.anisotropyMap.toJSON(e).uuid),this.map&&this.map.isTexture&&(n.map=this.map.toJSON(e).uuid),this.matcap&&this.matcap.isTexture&&(n.matcap=this.matcap.toJSON(e).uuid),this.alphaMap&&this.alphaMap.isTexture&&(n.alphaMap=this.alphaMap.toJSON(e).uuid),this.lightMap&&this.lightMap.isTexture&&(n.lightMap=this.lightMap.toJSON(e).uuid,n.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(n.aoMap=this.aoMap.toJSON(e).uuid,n.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(n.bumpMap=this.bumpMap.toJSON(e).uuid,n.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(n.normalMap=this.normalMap.toJSON(e).uuid,n.normalMapType=this.normalMapType,n.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(n.displacementMap=this.displacementMap.toJSON(e).uuid,n.displacementScale=this.displacementScale,n.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(n.roughnessMap=this.roughnessMap.toJSON(e).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(n.metalnessMap=this.metalnessMap.toJSON(e).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(n.emissiveMap=this.emissiveMap.toJSON(e).uuid),this.specularMap&&this.specularMap.isTexture&&(n.specularMap=this.specularMap.toJSON(e).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(n.specularIntensityMap=this.specularIntensityMap.toJSON(e).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(n.specularColorMap=this.specularColorMap.toJSON(e).uuid),this.envMap&&this.envMap.isTexture&&(n.envMap=this.envMap.toJSON(e).uuid,this.combine!==void 0&&(n.combine=this.combine)),this.envMapRotation!==void 0&&(n.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(n.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(n.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(n.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(n.gradientMap=this.gradientMap.toJSON(e).uuid),this.transmission!==void 0&&(n.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(n.transmissionMap=this.transmissionMap.toJSON(e).uuid),this.thickness!==void 0&&(n.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(n.thicknessMap=this.thicknessMap.toJSON(e).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(n.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(n.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(n.size=this.size),this.shadowSide!==null&&(n.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(n.sizeAttenuation=this.sizeAttenuation),this.blending!==1&&(n.blending=this.blending),this.side!==0&&(n.side=this.side),this.vertexColors===!0&&(n.vertexColors=!0),this.opacity<1&&(n.opacity=this.opacity),this.transparent===!0&&(n.transparent=!0),this.blendSrc!==204&&(n.blendSrc=this.blendSrc),this.blendDst!==205&&(n.blendDst=this.blendDst),this.blendEquation!==100&&(n.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(n.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(n.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(n.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(n.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(n.blendAlpha=this.blendAlpha),this.depthFunc!==3&&(n.depthFunc=this.depthFunc),this.depthTest===!1&&(n.depthTest=this.depthTest),this.depthWrite===!1&&(n.depthWrite=this.depthWrite),this.colorWrite===!1&&(n.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(n.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==519&&(n.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(n.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(n.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==7680&&(n.stencilFail=this.stencilFail),this.stencilZFail!==7680&&(n.stencilZFail=this.stencilZFail),this.stencilZPass!==7680&&(n.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(n.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(n.rotation=this.rotation),this.polygonOffset===!0&&(n.polygonOffset=!0),this.polygonOffsetFactor!==0&&(n.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(n.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(n.linewidth=this.linewidth),this.dashSize!==void 0&&(n.dashSize=this.dashSize),this.gapSize!==void 0&&(n.gapSize=this.gapSize),this.scale!==void 0&&(n.scale=this.scale),this.dithering===!0&&(n.dithering=!0),this.alphaTest>0&&(n.alphaTest=this.alphaTest),this.alphaHash===!0&&(n.alphaHash=!0),this.alphaToCoverage===!0&&(n.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(n.premultipliedAlpha=!0),this.forceSinglePass===!0&&(n.forceSinglePass=!0),this.allowOverride===!1&&(n.allowOverride=!1),this.wireframe===!0&&(n.wireframe=!0),this.wireframeLinewidth>1&&(n.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!==`round`&&(n.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!==`round`&&(n.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(n.flatShading=!0),this.visible===!1&&(n.visible=!1),this.toneMapped===!1&&(n.toneMapped=!1),this.fog===!1&&(n.fog=!1),Object.keys(this.userData).length>0&&(n.userData=this.userData);function r(e){let t=[];for(let n in e){let r=e[n];delete r.metadata,t.push(r)}return t}if(t){let t=r(e.textures),i=r(e.images);t.length>0&&(n.textures=t),i.length>0&&(n.images=i)}return n}fromJSON(e,t){if(e.uuid!==void 0&&(this.uuid=e.uuid),e.name!==void 0&&(this.name=e.name),e.color!==void 0&&this.color!==void 0&&this.color.setHex(e.color),e.roughness!==void 0&&(this.roughness=e.roughness),e.metalness!==void 0&&(this.metalness=e.metalness),e.sheen!==void 0&&(this.sheen=e.sheen),e.sheenColor!==void 0&&(this.sheenColor=new J().setHex(e.sheenColor)),e.sheenRoughness!==void 0&&(this.sheenRoughness=e.sheenRoughness),e.emissive!==void 0&&this.emissive!==void 0&&this.emissive.setHex(e.emissive),e.specular!==void 0&&this.specular!==void 0&&this.specular.setHex(e.specular),e.specularIntensity!==void 0&&(this.specularIntensity=e.specularIntensity),e.specularColor!==void 0&&this.specularColor!==void 0&&this.specularColor.setHex(e.specularColor),e.shininess!==void 0&&(this.shininess=e.shininess),e.clearcoat!==void 0&&(this.clearcoat=e.clearcoat),e.clearcoatRoughness!==void 0&&(this.clearcoatRoughness=e.clearcoatRoughness),e.dispersion!==void 0&&(this.dispersion=e.dispersion),e.iridescence!==void 0&&(this.iridescence=e.iridescence),e.iridescenceIOR!==void 0&&(this.iridescenceIOR=e.iridescenceIOR),e.iridescenceThicknessRange!==void 0&&(this.iridescenceThicknessRange=e.iridescenceThicknessRange),e.transmission!==void 0&&(this.transmission=e.transmission),e.thickness!==void 0&&(this.thickness=e.thickness),e.attenuationDistance!==void 0&&(this.attenuationDistance=e.attenuationDistance),e.attenuationColor!==void 0&&this.attenuationColor!==void 0&&this.attenuationColor.setHex(e.attenuationColor),e.anisotropy!==void 0&&(this.anisotropy=e.anisotropy),e.anisotropyRotation!==void 0&&(this.anisotropyRotation=e.anisotropyRotation),e.fog!==void 0&&(this.fog=e.fog),e.flatShading!==void 0&&(this.flatShading=e.flatShading),e.blending!==void 0&&(this.blending=e.blending),e.combine!==void 0&&(this.combine=e.combine),e.side!==void 0&&(this.side=e.side),e.shadowSide!==void 0&&(this.shadowSide=e.shadowSide),e.opacity!==void 0&&(this.opacity=e.opacity),e.transparent!==void 0&&(this.transparent=e.transparent),e.alphaTest!==void 0&&(this.alphaTest=e.alphaTest),e.alphaHash!==void 0&&(this.alphaHash=e.alphaHash),e.depthFunc!==void 0&&(this.depthFunc=e.depthFunc),e.depthTest!==void 0&&(this.depthTest=e.depthTest),e.depthWrite!==void 0&&(this.depthWrite=e.depthWrite),e.colorWrite!==void 0&&(this.colorWrite=e.colorWrite),e.blendSrc!==void 0&&(this.blendSrc=e.blendSrc),e.blendDst!==void 0&&(this.blendDst=e.blendDst),e.blendEquation!==void 0&&(this.blendEquation=e.blendEquation),e.blendSrcAlpha!==void 0&&(this.blendSrcAlpha=e.blendSrcAlpha),e.blendDstAlpha!==void 0&&(this.blendDstAlpha=e.blendDstAlpha),e.blendEquationAlpha!==void 0&&(this.blendEquationAlpha=e.blendEquationAlpha),e.blendColor!==void 0&&this.blendColor!==void 0&&this.blendColor.setHex(e.blendColor),e.blendAlpha!==void 0&&(this.blendAlpha=e.blendAlpha),e.stencilWriteMask!==void 0&&(this.stencilWriteMask=e.stencilWriteMask),e.stencilFunc!==void 0&&(this.stencilFunc=e.stencilFunc),e.stencilRef!==void 0&&(this.stencilRef=e.stencilRef),e.stencilFuncMask!==void 0&&(this.stencilFuncMask=e.stencilFuncMask),e.stencilFail!==void 0&&(this.stencilFail=e.stencilFail),e.stencilZFail!==void 0&&(this.stencilZFail=e.stencilZFail),e.stencilZPass!==void 0&&(this.stencilZPass=e.stencilZPass),e.stencilWrite!==void 0&&(this.stencilWrite=e.stencilWrite),e.wireframe!==void 0&&(this.wireframe=e.wireframe),e.wireframeLinewidth!==void 0&&(this.wireframeLinewidth=e.wireframeLinewidth),e.wireframeLinecap!==void 0&&(this.wireframeLinecap=e.wireframeLinecap),e.wireframeLinejoin!==void 0&&(this.wireframeLinejoin=e.wireframeLinejoin),e.rotation!==void 0&&(this.rotation=e.rotation),e.linewidth!==void 0&&(this.linewidth=e.linewidth),e.dashSize!==void 0&&(this.dashSize=e.dashSize),e.gapSize!==void 0&&(this.gapSize=e.gapSize),e.scale!==void 0&&(this.scale=e.scale),e.polygonOffset!==void 0&&(this.polygonOffset=e.polygonOffset),e.polygonOffsetFactor!==void 0&&(this.polygonOffsetFactor=e.polygonOffsetFactor),e.polygonOffsetUnits!==void 0&&(this.polygonOffsetUnits=e.polygonOffsetUnits),e.dithering!==void 0&&(this.dithering=e.dithering),e.alphaToCoverage!==void 0&&(this.alphaToCoverage=e.alphaToCoverage),e.premultipliedAlpha!==void 0&&(this.premultipliedAlpha=e.premultipliedAlpha),e.forceSinglePass!==void 0&&(this.forceSinglePass=e.forceSinglePass),e.allowOverride!==void 0&&(this.allowOverride=e.allowOverride),e.visible!==void 0&&(this.visible=e.visible),e.toneMapped!==void 0&&(this.toneMapped=e.toneMapped),e.userData!==void 0&&(this.userData=e.userData),e.vertexColors!==void 0&&(this.vertexColors=typeof e.vertexColors==`number`?e.vertexColors>0:e.vertexColors),e.size!==void 0&&(this.size=e.size),e.sizeAttenuation!==void 0&&(this.sizeAttenuation=e.sizeAttenuation),e.map!==void 0&&(this.map=t[e.map]||null),e.matcap!==void 0&&(this.matcap=t[e.matcap]||null),e.alphaMap!==void 0&&(this.alphaMap=t[e.alphaMap]||null),e.bumpMap!==void 0&&(this.bumpMap=t[e.bumpMap]||null),e.bumpScale!==void 0&&(this.bumpScale=e.bumpScale),e.normalMap!==void 0&&(this.normalMap=t[e.normalMap]||null),e.normalMapType!==void 0&&(this.normalMapType=e.normalMapType),e.normalScale!==void 0){let t=e.normalScale;Array.isArray(t)===!1&&(t=[t,t]),this.normalScale=new U().fromArray(t)}return e.displacementMap!==void 0&&(this.displacementMap=t[e.displacementMap]||null),e.displacementScale!==void 0&&(this.displacementScale=e.displacementScale),e.displacementBias!==void 0&&(this.displacementBias=e.displacementBias),e.roughnessMap!==void 0&&(this.roughnessMap=t[e.roughnessMap]||null),e.metalnessMap!==void 0&&(this.metalnessMap=t[e.metalnessMap]||null),e.emissiveMap!==void 0&&(this.emissiveMap=t[e.emissiveMap]||null),e.emissiveIntensity!==void 0&&(this.emissiveIntensity=e.emissiveIntensity),e.specularMap!==void 0&&(this.specularMap=t[e.specularMap]||null),e.specularIntensityMap!==void 0&&(this.specularIntensityMap=t[e.specularIntensityMap]||null),e.specularColorMap!==void 0&&(this.specularColorMap=t[e.specularColorMap]||null),e.envMap!==void 0&&(this.envMap=t[e.envMap]||null),e.envMapRotation!==void 0&&this.envMapRotation.fromArray(e.envMapRotation),e.envMapIntensity!==void 0&&(this.envMapIntensity=e.envMapIntensity),e.reflectivity!==void 0&&(this.reflectivity=e.reflectivity),e.refractionRatio!==void 0&&(this.refractionRatio=e.refractionRatio),e.lightMap!==void 0&&(this.lightMap=t[e.lightMap]||null),e.lightMapIntensity!==void 0&&(this.lightMapIntensity=e.lightMapIntensity),e.aoMap!==void 0&&(this.aoMap=t[e.aoMap]||null),e.aoMapIntensity!==void 0&&(this.aoMapIntensity=e.aoMapIntensity),e.gradientMap!==void 0&&(this.gradientMap=t[e.gradientMap]||null),e.clearcoatMap!==void 0&&(this.clearcoatMap=t[e.clearcoatMap]||null),e.clearcoatRoughnessMap!==void 0&&(this.clearcoatRoughnessMap=t[e.clearcoatRoughnessMap]||null),e.clearcoatNormalMap!==void 0&&(this.clearcoatNormalMap=t[e.clearcoatNormalMap]||null),e.clearcoatNormalScale!==void 0&&(this.clearcoatNormalScale=new U().fromArray(e.clearcoatNormalScale)),e.iridescenceMap!==void 0&&(this.iridescenceMap=t[e.iridescenceMap]||null),e.iridescenceThicknessMap!==void 0&&(this.iridescenceThicknessMap=t[e.iridescenceThicknessMap]||null),e.transmissionMap!==void 0&&(this.transmissionMap=t[e.transmissionMap]||null),e.thicknessMap!==void 0&&(this.thicknessMap=t[e.thicknessMap]||null),e.anisotropyMap!==void 0&&(this.anisotropyMap=t[e.anisotropyMap]||null),e.sheenColorMap!==void 0&&(this.sheenColorMap=t[e.sheenColorMap]||null),e.sheenRoughnessMap!==void 0&&(this.sheenRoughnessMap=t[e.sheenRoughnessMap]||null),this}clone(){return new this.constructor().copy(this)}copy(e){this.name=e.name,this.blending=e.blending,this.side=e.side,this.vertexColors=e.vertexColors,this.opacity=e.opacity,this.transparent=e.transparent,this.blendSrc=e.blendSrc,this.blendDst=e.blendDst,this.blendEquation=e.blendEquation,this.blendSrcAlpha=e.blendSrcAlpha,this.blendDstAlpha=e.blendDstAlpha,this.blendEquationAlpha=e.blendEquationAlpha,this.blendColor.copy(e.blendColor),this.blendAlpha=e.blendAlpha,this.depthFunc=e.depthFunc,this.depthTest=e.depthTest,this.depthWrite=e.depthWrite,this.stencilWriteMask=e.stencilWriteMask,this.stencilFunc=e.stencilFunc,this.stencilRef=e.stencilRef,this.stencilFuncMask=e.stencilFuncMask,this.stencilFail=e.stencilFail,this.stencilZFail=e.stencilZFail,this.stencilZPass=e.stencilZPass,this.stencilWrite=e.stencilWrite;let t=e.clippingPlanes,n=null;if(t!==null){let e=t.length;n=Array(e);for(let r=0;r!==e;++r)n[r]=t[r].clone()}return this.clippingPlanes=n,this.clipIntersection=e.clipIntersection,this.clipShadows=e.clipShadows,this.shadowSide=e.shadowSide,this.colorWrite=e.colorWrite,this.precision=e.precision,this.polygonOffset=e.polygonOffset,this.polygonOffsetFactor=e.polygonOffsetFactor,this.polygonOffsetUnits=e.polygonOffsetUnits,this.dithering=e.dithering,this.alphaTest=e.alphaTest,this.alphaHash=e.alphaHash,this.alphaToCoverage=e.alphaToCoverage,this.premultipliedAlpha=e.premultipliedAlpha,this.forceSinglePass=e.forceSinglePass,this.allowOverride=e.allowOverride,this.visible=e.visible,this.toneMapped=e.toneMapped,this.userData=JSON.parse(JSON.stringify(e.userData)),this}dispose(){this.dispatchEvent({type:`dispose`})}set needsUpdate(e){e===!0&&this.version++}},Pr=new W,Fr=new W,Ir=new W,Lr=new W,Rr=new W,zr=new W,Br=new W,Vr=class{constructor(e=new W,t=new W(0,0,-1)){this.origin=e,this.direction=t}set(e,t){return this.origin.copy(e),this.direction.copy(t),this}copy(e){return this.origin.copy(e.origin),this.direction.copy(e.direction),this}at(e,t){return t.copy(this.origin).addScaledVector(this.direction,e)}lookAt(e){return this.direction.copy(e).sub(this.origin).normalize(),this}recast(e){return this.origin.copy(this.at(e,Pr)),this}closestPointToPoint(e,t){t.subVectors(e,this.origin);let n=t.dot(this.direction);return n<0?t.copy(this.origin):t.copy(this.origin).addScaledVector(this.direction,n)}distanceToPoint(e){return Math.sqrt(this.distanceSqToPoint(e))}distanceSqToPoint(e){let t=Pr.subVectors(e,this.origin).dot(this.direction);return t<0?this.origin.distanceToSquared(e):(Pr.copy(this.origin).addScaledVector(this.direction,t),Pr.distanceToSquared(e))}distanceSqToSegment(e,t,n,r){Fr.copy(e).add(t).multiplyScalar(.5),Ir.copy(t).sub(e).normalize(),Lr.copy(this.origin).sub(Fr);let i=e.distanceTo(t)*.5,a=-this.direction.dot(Ir),o=Lr.dot(this.direction),s=-Lr.dot(Ir),c=Lr.lengthSq(),l=Math.abs(1-a*a),u,d,f,p;if(l>0){if(u=a*s-o,d=a*o-s,p=i*l,u>=0){if(d>=-p){if(d<=p){let e=1/l;u*=e,d*=e,f=u*(u+a*d+2*o)+d*(a*u+d+2*s)+c}else d=i,u=Math.max(0,-(a*d+o)),f=-u*u+d*(d+2*s)+c}else d=-i,u=Math.max(0,-(a*d+o)),f=-u*u+d*(d+2*s)+c}else d<=-p?(u=Math.max(0,-(-a*i+o)),d=u>0?-i:Math.min(Math.max(-i,-s),i),f=-u*u+d*(d+2*s)+c):d<=p?(u=0,d=Math.min(Math.max(-i,-s),i),f=d*(d+2*s)+c):(u=Math.max(0,-(a*i+o)),d=u>0?i:Math.min(Math.max(-i,-s),i),f=-u*u+d*(d+2*s)+c)}else d=a>0?-i:i,u=Math.max(0,-(a*d+o)),f=-u*u+d*(d+2*s)+c;return n&&n.copy(this.origin).addScaledVector(this.direction,u),r&&r.copy(Fr).addScaledVector(Ir,d),f}intersectSphere(e,t){Pr.subVectors(e.center,this.origin);let n=Pr.dot(this.direction),r=Pr.dot(Pr)-n*n,i=e.radius*e.radius;if(r>i)return null;let a=Math.sqrt(i-r),o=n-a,s=n+a;return s<0?null:o<0?this.at(s,t):this.at(o,t)}intersectsSphere(e){return e.radius<0?!1:this.distanceSqToPoint(e.center)<=e.radius*e.radius}distanceToPlane(e){let t=e.normal.dot(this.direction);if(t===0)return e.distanceToPoint(this.origin)===0?0:null;let n=-(this.origin.dot(e.normal)+e.constant)/t;return n>=0?n:null}intersectPlane(e,t){let n=this.distanceToPlane(e);return n===null?null:this.at(n,t)}intersectsPlane(e){let t=e.distanceToPoint(this.origin);return t===0||e.normal.dot(this.direction)*t<0}intersectBox(e,t){let n,r,i,a,o,s,c=1/this.direction.x,l=1/this.direction.y,u=1/this.direction.z,d=this.origin;return c>=0?(n=(e.min.x-d.x)*c,r=(e.max.x-d.x)*c):(n=(e.max.x-d.x)*c,r=(e.min.x-d.x)*c),l>=0?(i=(e.min.y-d.y)*l,a=(e.max.y-d.y)*l):(i=(e.max.y-d.y)*l,a=(e.min.y-d.y)*l),n>a||i>r||((i>n||isNaN(n))&&(n=i),(a<r||isNaN(r))&&(r=a),u>=0?(o=(e.min.z-d.z)*u,s=(e.max.z-d.z)*u):(o=(e.max.z-d.z)*u,s=(e.min.z-d.z)*u),n>s||o>r)||((o>n||n!==n)&&(n=o),(s<r||r!==r)&&(r=s),r<0)?null:this.at(n>=0?n:r,t)}intersectsBox(e){return this.intersectBox(e,Pr)!==null}intersectTriangle(e,t,n,r,i){Rr.subVectors(t,e),zr.subVectors(n,e),Br.crossVectors(Rr,zr);let a=this.direction.dot(Br),o;if(a>0){if(r)return null;o=1}else if(a<0)o=-1,a=-a;else return null;Lr.subVectors(this.origin,e);let s=o*this.direction.dot(zr.crossVectors(Lr,zr));if(s<0)return null;let c=o*this.direction.dot(Rr.cross(Lr));if(c<0||s+c>a)return null;let l=-o*Lr.dot(Br);return l<0?null:this.at(l/a,i)}applyMatrix4(e){return this.origin.applyMatrix4(e),this.direction.transformDirection(e),this}equals(e){return e.origin.equals(this.origin)&&e.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}},Hr=class extends Nr{constructor(e){super(),this.isMeshBasicMaterial=!0,this.type=`MeshBasicMaterial`,this.color=new J(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new ln,this.combine=0,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap=`round`,this.wireframeLinejoin=`round`,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.specularMap=e.specularMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.combine=e.combine,this.reflectivity=e.reflectivity,this.refractionRatio=e.refractionRatio,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.fog=e.fog,this}},Ur=new q,Wr=new Vr,Gr=new xr,Kr=new W,qr=new W,Jr=new W,Yr=new W,Xr=new W,Zr=new W,Qr=new W,$r=new W,ei=class extends En{constructor(e=new Or,t=new Hr){super(),this.isMesh=!0,this.type=`Mesh`,this.geometry=e,this.material=t,this.morphTargetDictionary=void 0,this.morphTargetInfluences=void 0,this.count=1,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),e.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=e.morphTargetInfluences.slice()),e.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},e.morphTargetDictionary)),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}updateMorphTargets(){let e=this.geometry.morphAttributes,t=Object.keys(e);if(t.length>0){let n=e[t[0]];if(n!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let e=0,t=n.length;e<t;e++){let t=n[e].name||String(e);this.morphTargetInfluences.push(0),this.morphTargetDictionary[t]=e}}}}getVertexPosition(e,t){let n=this.geometry,r=n.attributes.position,i=n.morphAttributes.position,a=n.morphTargetsRelative;t.fromBufferAttribute(r,e);let o=this.morphTargetInfluences;if(i&&o){Zr.set(0,0,0);for(let n=0,r=i.length;n<r;n++){let r=o[n],s=i[n];r!==0&&(Xr.fromBufferAttribute(s,e),a?Zr.addScaledVector(Xr,r):Zr.addScaledVector(Xr.sub(t),r))}t.add(Zr)}return t}raycast(e,t){let n=this.geometry,r=this.material,i=this.matrixWorld;r!==void 0&&(n.boundingSphere===null&&n.computeBoundingSphere(),Gr.copy(n.boundingSphere),Gr.applyMatrix4(i),Wr.copy(e.ray).recast(e.near),!(Gr.containsPoint(Wr.origin)===!1&&(Wr.intersectSphere(Gr,Kr)===null||Wr.origin.distanceToSquared(Kr)>(e.far-e.near)**2))&&(Ur.copy(i).invert(),Wr.copy(e.ray).applyMatrix4(Ur),(n.boundingBox===null||Wr.intersectsBox(n.boundingBox)!==!1)&&this._computeIntersections(e,t,Wr)))}_computeIntersections(e,t,n){let r,i=this.geometry,a=this.material,o=i.index,s=i.attributes.position,c=i.attributes.uv,l=i.attributes.uv1,u=i.attributes.normal,d=i.groups,f=i.drawRange;if(o!==null){if(Array.isArray(a))for(let i=0,s=d.length;i<s;i++){let s=d[i],p=a[s.materialIndex],m=Math.max(s.start,f.start),h=Math.min(o.count,Math.min(s.start+s.count,f.start+f.count));for(let i=m,a=h;i<a;i+=3){let a=o.getX(i),d=o.getX(i+1),f=o.getX(i+2);r=ni(this,p,e,n,c,l,u,a,d,f),r&&(r.faceIndex=Math.floor(i/3),r.face.materialIndex=s.materialIndex,t.push(r))}}else{let i=Math.max(0,f.start),s=Math.min(o.count,f.start+f.count);for(let d=i,f=s;d<f;d+=3){let i=o.getX(d),s=o.getX(d+1),f=o.getX(d+2);r=ni(this,a,e,n,c,l,u,i,s,f),r&&(r.faceIndex=Math.floor(d/3),t.push(r))}}}else if(s!==void 0){if(Array.isArray(a))for(let i=0,o=d.length;i<o;i++){let o=d[i],p=a[o.materialIndex],m=Math.max(o.start,f.start),h=Math.min(s.count,Math.min(o.start+o.count,f.start+f.count));for(let i=m,a=h;i<a;i+=3){let a=i,s=i+1,d=i+2;r=ni(this,p,e,n,c,l,u,a,s,d),r&&(r.faceIndex=Math.floor(i/3),r.face.materialIndex=o.materialIndex,t.push(r))}}else{let i=Math.max(0,f.start),o=Math.min(s.count,f.start+f.count);for(let s=i,d=o;s<d;s+=3){let i=s,o=s+1,d=s+2;r=ni(this,a,e,n,c,l,u,i,o,d),r&&(r.faceIndex=Math.floor(s/3),t.push(r))}}}}};function ti(e,t,n,r,i,a,o,s){let c;if(c=t.side===1?r.intersectTriangle(o,a,i,!0,s):r.intersectTriangle(i,a,o,t.side===0,s),c===null)return null;$r.copy(s),$r.applyMatrix4(e.matrixWorld);let l=n.ray.origin.distanceTo($r);return l<n.near||l>n.far?null:{distance:l,point:$r.clone(),object:e}}function ni(e,t,n,r,i,a,o,s,c,l){e.getVertexPosition(s,qr),e.getVertexPosition(c,Jr),e.getVertexPosition(l,Yr);let u=ti(e,t,n,r,qr,Jr,Yr,Qr);if(u){let e=new W;Yn.getBarycoord(Qr,qr,Jr,Yr,e),i&&(u.uv=Yn.getInterpolatedAttribute(i,s,c,l,e,new U)),a&&(u.uv1=Yn.getInterpolatedAttribute(a,s,c,l,e,new U)),o&&(u.normal=Yn.getInterpolatedAttribute(o,s,c,l,e,new W),u.normal.dot(r.direction)>0&&u.normal.multiplyScalar(-1));let t={a:s,b:c,c:l,normal:new W,materialIndex:0};Yn.getNormal(qr,Jr,Yr,t.normal),u.face=t,u.barycoord=e}return u}var ri=new Jt,ii=new Jt,ai=new Jt,oi=new Jt,si=new q,ci=new W,li=new xr,ui=new q,di=new Vr,fi=class extends ei{constructor(e,t){super(e,t),this.isSkinnedMesh=!0,this.type=`SkinnedMesh`,this.bindMode=n,this.bindMatrix=new q,this.bindMatrixInverse=new q,this.boundingBox=null,this.boundingSphere=null}computeBoundingBox(){let e=this.geometry;this.boundingBox===null&&(this.boundingBox=new Xn),this.boundingBox.makeEmpty();let t=e.getAttribute(`position`);for(let e=0;e<t.count;e++)this.getVertexPosition(e,ci),this.boundingBox.expandByPoint(ci)}computeBoundingSphere(){let e=this.geometry;this.boundingSphere===null&&(this.boundingSphere=new xr),this.boundingSphere.makeEmpty();let t=e.getAttribute(`position`);for(let e=0;e<t.count;e++)this.getVertexPosition(e,ci),this.boundingSphere.expandByPoint(ci)}copy(e,t){return super.copy(e,t),this.bindMode=e.bindMode,this.bindMatrix.copy(e.bindMatrix),this.bindMatrixInverse.copy(e.bindMatrixInverse),this.skeleton=e.skeleton,e.boundingBox!==null&&(this.boundingBox=e.boundingBox.clone()),e.boundingSphere!==null&&(this.boundingSphere=e.boundingSphere.clone()),this}raycast(e,t){let n=this.material,r=this.matrixWorld;n!==void 0&&(this.boundingSphere===null&&this.computeBoundingSphere(),li.copy(this.boundingSphere),li.applyMatrix4(r),e.ray.intersectsSphere(li)!==!1&&(ui.copy(r).invert(),di.copy(e.ray).applyMatrix4(ui),(this.boundingBox===null||di.intersectsBox(this.boundingBox)!==!1)&&this._computeIntersections(e,t,di)))}getVertexPosition(e,t){return super.getVertexPosition(e,t),this.applyBoneTransform(e,t),t}bind(e,t){this.skeleton=e,t===void 0&&(this.updateMatrixWorld(!0),this.skeleton.calculateInverses(),t=this.matrixWorld),this.bindMatrix.copy(t),this.bindMatrixInverse.copy(t).invert()}pose(){this.skeleton.pose()}normalizeSkinWeights(){let e=new Jt,t=this.geometry.attributes.skinWeight;for(let n=0,r=t.count;n<r;n++){e.fromBufferAttribute(t,n);let r=1/e.manhattanLength();r===1/0?e.set(1,0,0,0):e.multiplyScalar(r),t.setXYZW(n,e.x,e.y,e.z,e.w)}}updateMatrixWorld(e){super.updateMatrixWorld(e),this.bindMode===`attached`?this.bindMatrixInverse.copy(this.matrixWorld).invert():this.bindMode===`detached`?this.bindMatrixInverse.copy(this.bindMatrix).invert():B(`SkinnedMesh: Unrecognized bindMode: `+this.bindMode)}applyBoneTransform(e,t){let n=this.skeleton,r=this.geometry;ii.fromBufferAttribute(r.attributes.skinIndex,e),ai.fromBufferAttribute(r.attributes.skinWeight,e),t.isVector4?(ri.copy(t),t.set(0,0,0,0)):(ri.set(...t,1),t.set(0,0,0)),ri.applyMatrix4(this.bindMatrix);for(let e=0;e<4;e++){let r=ai.getComponent(e);if(r!==0){let i=ii.getComponent(e);si.multiplyMatrices(n.bones[i].matrixWorld,n.boneInverses[i]),t.addScaledVector(oi.copy(ri).applyMatrix4(si),r)}}return t.isVector4&&(t.w=ri.w),t.applyMatrix4(this.bindMatrixInverse)}},pi=class extends En{constructor(){super(),this.isBone=!0,this.type=`Bone`}},mi=class extends qt{constructor(e=null,t=1,n=1,r,i,a,s,c,l=o,u=o,d,f){super(null,a,s,c,l,u,r,i,d,f),this.isDataTexture=!0,this.image={data:e,width:t,height:n},this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}},hi=new q,gi=new q,_i=class e{constructor(e=[],t=[]){this.uuid=lt(),this.bones=e.slice(0),this.boneInverses=t,this.boneMatrices=null,this.boneTexture=null,this.init()}init(){let e=this.bones,t=this.boneInverses;if(this.boneMatrices=new Float32Array(e.length*16),t.length===0)this.calculateInverses();else if(e.length!==t.length){B(`Skeleton: Number of inverse bone matrices does not match amount of bones.`),this.boneInverses=[];for(let e=0,t=this.bones.length;e<t;e++)this.boneInverses.push(new q)}}calculateInverses(){this.boneInverses.length=0;for(let e=0,t=this.bones.length;e<t;e++){let t=new q;this.bones[e]&&t.copy(this.bones[e].matrixWorld).invert(),this.boneInverses.push(t)}}pose(){for(let e=0,t=this.bones.length;e<t;e++){let t=this.bones[e];t&&t.matrixWorld.copy(this.boneInverses[e]).invert()}for(let e=0,t=this.bones.length;e<t;e++){let t=this.bones[e];t&&(t.parent&&t.parent.isBone?(t.matrix.copy(t.parent.matrixWorld).invert(),t.matrix.multiply(t.matrixWorld)):t.matrix.copy(t.matrixWorld),t.matrix.decompose(t.position,t.quaternion,t.scale))}}update(){let e=this.bones,t=this.boneInverses,n=this.boneMatrices,r=this.boneTexture;for(let r=0,i=e.length;r<i;r++){let i=e[r]?e[r].matrixWorld:gi;hi.multiplyMatrices(i,t[r]),hi.toArray(n,r*16)}r!==null&&(r.needsUpdate=!0)}clone(){return new e(this.bones,this.boneInverses)}computeBoneTexture(){let e=Math.sqrt(this.bones.length*4);e=Math.ceil(e/4)*4,e=Math.max(e,4);let t=new Float32Array(e*e*4);t.set(this.boneMatrices);let n=new mi(t,e,e,D,v);return n.needsUpdate=!0,this.boneMatrices=t,this.boneTexture=n,this}getBoneByName(e){for(let t=0,n=this.bones.length;t<n;t++){let n=this.bones[t];if(n.name===e)return n}}dispose(){this.boneTexture!==null&&(this.boneTexture.dispose(),this.boneTexture=null)}fromJSON(e,t){this.uuid=e.uuid;for(let n=0,r=e.bones.length;n<r;n++){let r=e.bones[n],i=t[r];i===void 0&&(B(`Skeleton: No bone found with UUID:`,r),i=new pi),this.bones.push(i),this.boneInverses.push(new q().fromArray(e.boneInverses[n]))}return this.init(),this}toJSON(){let e={metadata:{version:4.7,type:`Skeleton`,generator:`Skeleton.toJSON`},bones:[],boneInverses:[]};e.uuid=this.uuid;let t=this.bones,n=this.boneInverses;for(let r=0,i=t.length;r<i;r++){let i=t[r];e.bones.push(i.uuid);let a=n[r];e.boneInverses.push(a.toArray())}return e}},vi=class extends mr{constructor(e,t,n,r=1){super(e,t,n),this.isInstancedBufferAttribute=!0,this.meshPerAttribute=r}copy(e){return super.copy(e),this.meshPerAttribute=e.meshPerAttribute,this}toJSON(){let e=super.toJSON();return e.meshPerAttribute=this.meshPerAttribute,e.isInstancedBufferAttribute=!0,e}},yi=new q,bi=new q,xi=[],Si=new Xn,Ci=new q,wi=new ei,Ti=new xr,Ei=class extends ei{constructor(e,t,n){super(e,t),this.isInstancedMesh=!0,this.instanceMatrix=new vi(new Float32Array(n*16),16),this.instanceColor=null,this.morphTexture=null,this.count=n,this.boundingBox=null,this.boundingSphere=null;for(let e=0;e<n;e++)this.setMatrixAt(e,Ci)}computeBoundingBox(){let e=this.geometry,t=this.count;this.boundingBox===null&&(this.boundingBox=new Xn),e.boundingBox===null&&e.computeBoundingBox(),this.boundingBox.makeEmpty();for(let n=0;n<t;n++)this.getMatrixAt(n,yi),Si.copy(e.boundingBox).applyMatrix4(yi),this.boundingBox.union(Si)}computeBoundingSphere(){let e=this.geometry,t=this.count;this.boundingSphere===null&&(this.boundingSphere=new xr),e.boundingSphere===null&&e.computeBoundingSphere(),this.boundingSphere.makeEmpty();for(let n=0;n<t;n++)this.getMatrixAt(n,yi),Ti.copy(e.boundingSphere).applyMatrix4(yi),this.boundingSphere.union(Ti)}copy(e,t){return super.copy(e,t),this.instanceMatrix.copy(e.instanceMatrix),e.morphTexture!==null&&(this.morphTexture=e.morphTexture.clone()),e.instanceColor!==null&&(this.instanceColor=e.instanceColor.clone()),this.count=e.count,e.boundingBox!==null&&(this.boundingBox=e.boundingBox.clone()),e.boundingSphere!==null&&(this.boundingSphere=e.boundingSphere.clone()),this}getColorAt(e,t){return this.instanceColor===null?t.setRGB(1,1,1):t.fromArray(this.instanceColor.array,e*3)}getMatrixAt(e,t){return t.fromArray(this.instanceMatrix.array,e*16)}getMorphAt(e,t){let n=t.morphTargetInfluences,r=this.morphTexture.source.data.data,i=e*(n.length+1)+1;for(let e=0;e<n.length;e++)n[e]=r[i+e]}raycast(e,t){let n=this.matrixWorld,r=this.count;if(wi.geometry=this.geometry,wi.material=this.material,wi.material!==void 0&&(this.boundingSphere===null&&this.computeBoundingSphere(),Ti.copy(this.boundingSphere),Ti.applyMatrix4(n),e.ray.intersectsSphere(Ti)!==!1))for(let i=0;i<r;i++){this.getMatrixAt(i,yi),bi.multiplyMatrices(n,yi),wi.matrixWorld=bi,wi.raycast(e,xi);for(let e=0,n=xi.length;e<n;e++){let n=xi[e];n.instanceId=i,n.object=this,t.push(n)}xi.length=0}}setColorAt(e,t){return this.instanceColor===null&&(this.instanceColor=new vi(new Float32Array(this.instanceMatrix.count*3).fill(1),3)),t.toArray(this.instanceColor.array,e*3),this}setMatrixAt(e,t){return t.toArray(this.instanceMatrix.array,e*16),this}setMorphAt(e,t){let n=t.morphTargetInfluences,r=n.length+1;this.morphTexture===null&&(this.morphTexture=new mi(new Float32Array(r*this.count),r,this.count,A,v));let i=this.morphTexture.source.data.data,a=0;for(let e=0;e<n.length;e++)a+=n[e];let o=this.geometry.morphTargetsRelative?1:1-a,s=r*e;return i[s]=o,i.set(n,s+1),this}updateMorphTargets(){}dispose(){this.dispatchEvent({type:`dispose`}),this.morphTexture!==null&&(this.morphTexture.dispose(),this.morphTexture=null)}},Di=new W,Oi=new W,ki=new G,Ai=class{constructor(e=new W(1,0,0),t=0){this.isPlane=!0,this.normal=e,this.constant=t}set(e,t){return this.normal.copy(e),this.constant=t,this}setComponents(e,t,n,r){return this.normal.set(e,t,n),this.constant=r,this}setFromNormalAndCoplanarPoint(e,t){return this.normal.copy(e),this.constant=-t.dot(this.normal),this}setFromCoplanarPoints(e,t,n){let r=Di.subVectors(n,t).cross(Oi.subVectors(e,t)).normalize();return this.setFromNormalAndCoplanarPoint(r,e),this}copy(e){return this.normal.copy(e.normal),this.constant=e.constant,this}normalize(){let e=1/this.normal.length();return this.normal.multiplyScalar(e),this.constant*=e,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(e){return this.normal.dot(e)+this.constant}distanceToSphere(e){return this.distanceToPoint(e.center)-e.radius}projectPoint(e,t){return t.copy(e).addScaledVector(this.normal,-this.distanceToPoint(e))}intersectLine(e,t,n=!0){let r=e.delta(Di),i=this.normal.dot(r);if(i===0)return this.distanceToPoint(e.start)===0?t.copy(e.start):null;let a=-(e.start.dot(this.normal)+this.constant)/i;return n===!0&&(a<0||a>1)?null:t.copy(e.start).addScaledVector(r,a)}intersectsLine(e){let t=this.distanceToPoint(e.start),n=this.distanceToPoint(e.end);return t<0&&n>0||n<0&&t>0}intersectsBox(e){return e.intersectsPlane(this)}intersectsSphere(e){return e.intersectsPlane(this)}coplanarPoint(e){return e.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(e,t){let n=t||ki.getNormalMatrix(e),r=this.coplanarPoint(Di).applyMatrix4(e),i=this.normal.applyMatrix3(n).normalize();return this.constant=-r.dot(i),this}translate(e){return this.constant-=e.dot(this.normal),this}equals(e){return e.normal.equals(this.normal)&&e.constant===this.constant}clone(){return new this.constructor().copy(this)}},ji=new xr,Mi=new U(.5,.5),Ni=new W,Pi=class{constructor(e=new Ai,t=new Ai,n=new Ai,r=new Ai,i=new Ai,a=new Ai){this.planes=[e,t,n,r,i,a]}set(e,t,n,r,i,a){let o=this.planes;return o[0].copy(e),o[1].copy(t),o[2].copy(n),o[3].copy(r),o[4].copy(i),o[5].copy(a),this}copy(e){let t=this.planes;for(let n=0;n<6;n++)t[n].copy(e.planes[n]);return this}setFromProjectionMatrix(e,t=R,n=!1){let r=this.planes,i=e.elements,a=i[0],o=i[1],s=i[2],c=i[3],l=i[4],u=i[5],d=i[6],f=i[7],p=i[8],m=i[9],h=i[10],g=i[11],_=i[12],v=i[13],y=i[14],b=i[15];if(r[0].setComponents(c-a,f-l,g-p,b-_).normalize(),r[1].setComponents(c+a,f+l,g+p,b+_).normalize(),r[2].setComponents(c+o,f+u,g+m,b+v).normalize(),r[3].setComponents(c-o,f-u,g-m,b-v).normalize(),n)r[4].setComponents(s,d,h,y).normalize(),r[5].setComponents(c-s,f-d,g-h,b-y).normalize();else if(r[4].setComponents(c-s,f-d,g-h,b-y).normalize(),t===2e3)r[5].setComponents(c+s,f+d,g+h,b+y).normalize();else if(t===2001)r[5].setComponents(s,d,h,y).normalize();else throw Error(`THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: `+t);return this}intersectsObject(e){if(e.boundingSphere!==void 0)e.boundingSphere===null&&e.computeBoundingSphere(),ji.copy(e.boundingSphere).applyMatrix4(e.matrixWorld);else{let t=e.geometry;t.boundingSphere===null&&t.computeBoundingSphere(),ji.copy(t.boundingSphere).applyMatrix4(e.matrixWorld)}return this.intersectsSphere(ji)}intersectsSprite(e){return ji.center.set(0,0,0),ji.radius=.7071067811865476+Mi.distanceTo(e.center),ji.applyMatrix4(e.matrixWorld),this.intersectsSphere(ji)}intersectsSphere(e){let t=this.planes,n=e.center,r=-e.radius;for(let e=0;e<6;e++)if(t[e].distanceToPoint(n)<r)return!1;return!0}intersectsBox(e){let t=this.planes;for(let n=0;n<6;n++){let r=t[n];if(Ni.x=r.normal.x>0?e.max.x:e.min.x,Ni.y=r.normal.y>0?e.max.y:e.min.y,Ni.z=r.normal.z>0?e.max.z:e.min.z,r.distanceToPoint(Ni)<0)return!1}return!0}containsPoint(e){let t=this.planes;for(let n=0;n<6;n++)if(t[n].distanceToPoint(e)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}},Fi=class extends Nr{constructor(e){super(),this.isLineBasicMaterial=!0,this.type=`LineBasicMaterial`,this.color=new J(16777215),this.map=null,this.linewidth=1,this.linecap=`round`,this.linejoin=`round`,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.linewidth=e.linewidth,this.linecap=e.linecap,this.linejoin=e.linejoin,this.fog=e.fog,this}},Ii=new W,Li=new W,Ri=new q,zi=new Vr,Bi=new xr,Vi=new W,Hi=new W,Ui=class extends En{constructor(e=new Or,t=new Fi){super(),this.isLine=!0,this.type=`Line`,this.geometry=e,this.material=t,this.morphTargetDictionary=void 0,this.morphTargetInfluences=void 0,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}computeLineDistances(){let e=this.geometry;if(e.index===null){let t=e.attributes.position,n=[0];for(let e=1,r=t.count;e<r;e++)Ii.fromBufferAttribute(t,e-1),Li.fromBufferAttribute(t,e),n[e]=n[e-1],n[e]+=Ii.distanceTo(Li);e.setAttribute(`lineDistance`,new _r(n,1))}else B(`Line.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.`);return this}raycast(e,t){let n=this.geometry,r=this.matrixWorld,i=e.params.Line.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),Bi.copy(n.boundingSphere),Bi.applyMatrix4(r),Bi.radius+=i,e.ray.intersectsSphere(Bi)===!1)return;Ri.copy(r).invert(),zi.copy(e.ray).applyMatrix4(Ri);let o=i/((this.scale.x+this.scale.y+this.scale.z)/3),s=o*o,c=this.isLineSegments?2:1,l=n.index,u=n.attributes.position;if(l!==null){let n=Math.max(0,a.start),r=Math.min(l.count,a.start+a.count);for(let i=n,a=r-1;i<a;i+=c){let n=l.getX(i),r=l.getX(i+1),a=Wi(this,e,zi,s,n,r,i);a&&t.push(a)}if(this.isLineLoop){let i=l.getX(r-1),a=l.getX(n),o=Wi(this,e,zi,s,i,a,r-1);o&&t.push(o)}}else{let n=Math.max(0,a.start),r=Math.min(u.count,a.start+a.count);for(let i=n,a=r-1;i<a;i+=c){let n=Wi(this,e,zi,s,i,i+1,i);n&&t.push(n)}if(this.isLineLoop){let i=Wi(this,e,zi,s,r-1,n,r-1);i&&t.push(i)}}}updateMorphTargets(){let e=this.geometry.morphAttributes,t=Object.keys(e);if(t.length>0){let n=e[t[0]];if(n!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let e=0,t=n.length;e<t;e++){let t=n[e].name||String(e);this.morphTargetInfluences.push(0),this.morphTargetDictionary[t]=e}}}}};function Wi(e,t,n,r,i,a,o){let s=e.geometry.attributes.position;if(Ii.fromBufferAttribute(s,i),Li.fromBufferAttribute(s,a),n.distanceSqToSegment(Ii,Li,Vi,Hi)>r)return;Vi.applyMatrix4(e.matrixWorld);let c=t.ray.origin.distanceTo(Vi);if(!(c<t.near||c>t.far))return{distance:c,point:Hi.clone().applyMatrix4(e.matrixWorld),index:o,face:null,faceIndex:null,barycoord:null,object:e}}var Gi=new W,Ki=new W,qi=class extends Ui{constructor(e,t){super(e,t),this.isLineSegments=!0,this.type=`LineSegments`}computeLineDistances(){let e=this.geometry;if(e.index===null){let t=e.attributes.position,n=[];for(let e=0,r=t.count;e<r;e+=2)Gi.fromBufferAttribute(t,e),Ki.fromBufferAttribute(t,e+1),n[e]=e===0?0:n[e-1],n[e+1]=n[e]+Gi.distanceTo(Ki);e.setAttribute(`lineDistance`,new _r(n,1))}else B(`LineSegments.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.`);return this}},Ji=class extends Ui{constructor(e,t){super(e,t),this.isLineLoop=!0,this.type=`LineLoop`}},Yi=class extends Nr{constructor(e){super(),this.isPointsMaterial=!0,this.type=`PointsMaterial`,this.color=new J(16777215),this.map=null,this.alphaMap=null,this.size=1,this.sizeAttenuation=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.size=e.size,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}},Xi=new q,Zi=new Vr,Qi=new xr,$i=new W,ea=class extends En{constructor(e=new Or,t=new Yi){super(),this.isPoints=!0,this.type=`Points`,this.geometry=e,this.material=t,this.morphTargetDictionary=void 0,this.morphTargetInfluences=void 0,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}raycast(e,t){let n=this.geometry,r=this.matrixWorld,i=e.params.Points.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),Qi.copy(n.boundingSphere),Qi.applyMatrix4(r),Qi.radius+=i,e.ray.intersectsSphere(Qi)===!1)return;Xi.copy(r).invert(),Zi.copy(e.ray).applyMatrix4(Xi);let o=i/((this.scale.x+this.scale.y+this.scale.z)/3),s=o*o,c=n.index,l=n.attributes.position;if(c!==null){let n=Math.max(0,a.start),i=Math.min(c.count,a.start+a.count);for(let a=n,o=i;a<o;a++){let n=c.getX(a);$i.fromBufferAttribute(l,n),ta($i,n,s,r,e,t,this)}}else{let n=Math.max(0,a.start),i=Math.min(l.count,a.start+a.count);for(let a=n,o=i;a<o;a++)$i.fromBufferAttribute(l,a),ta($i,a,s,r,e,t,this)}}updateMorphTargets(){let e=this.geometry.morphAttributes,t=Object.keys(e);if(t.length>0){let n=e[t[0]];if(n!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let e=0,t=n.length;e<t;e++){let t=n[e].name||String(e);this.morphTargetInfluences.push(0),this.morphTargetDictionary[t]=e}}}}};function ta(e,t,n,r,i,a,o){let s=Zi.distanceSqToPoint(e);if(s<n){let n=new W;Zi.closestPointToPoint(e,n),n.applyMatrix4(r);let c=i.ray.origin.distanceTo(n);if(c<i.near||c>i.far)return;a.push({distance:c,distanceToRay:Math.sqrt(s),point:n,index:t,face:null,faceIndex:null,barycoord:null,object:o})}}var na=class extends qt{constructor(e=[],t=301,n,r,i,a,o,s,c,l){super(e,t,n,r,i,a,o,s,c,l),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(e){this.image=e}},ra=class extends qt{constructor(e,t,n,r,i,a,o,s,c){super(e,t,n,r,i,a,o,s,c),this.isCanvasTexture=!0,this.needsUpdate=!0}},ia=class extends qt{constructor(e,t,n=_,r,i,a,s=o,c=o,l,u=O,d=1){if(u!==1026&&u!==1027)throw Error(`THREE.DepthTexture: format must be either THREE.DepthFormat or THREE.DepthStencilFormat`);super({width:e,height:t,depth:d},r,i,a,s,c,u,n,l),this.isDepthTexture=!0,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(e){return super.copy(e),this.source=new Ut(Object.assign({},e.image)),this.compareFunction=e.compareFunction,this}toJSON(e){let t=super.toJSON(e);return this.compareFunction!==null&&(t.compareFunction=this.compareFunction),t}},aa=class extends ia{constructor(e,t=_,n=301,r,i,a=o,s=o,c,l=O){let u={width:e,height:e,depth:1},d=[u,u,u,u,u,u];super(e,e,t,n,r,i,a,s,c,l),this.image=d,this.isCubeDepthTexture=!0,this.isCubeTexture=!0}get images(){return this.image}set images(e){this.image=e}},oa=class extends qt{constructor(e=null){super(),this.sourceTexture=e,this.isExternalTexture=!0}copy(e){return super.copy(e),this.sourceTexture=e.sourceTexture,this}},sa=class e extends Or{constructor(e=1,t=1,n=1,r=1,i=1,a=1){super(),this.type=`BoxGeometry`,this.parameters={width:e,height:t,depth:n,widthSegments:r,heightSegments:i,depthSegments:a};let o=this;r=Math.floor(r),i=Math.floor(i),a=Math.floor(a);let s=[],c=[],l=[],u=[],d=0,f=0;p(`z`,`y`,`x`,-1,-1,n,t,e,a,i,0),p(`z`,`y`,`x`,1,-1,n,t,-e,a,i,1),p(`x`,`z`,`y`,1,1,e,n,t,r,a,2),p(`x`,`z`,`y`,1,-1,e,n,-t,r,a,3),p(`x`,`y`,`z`,1,-1,e,t,n,r,i,4),p(`x`,`y`,`z`,-1,-1,e,t,-n,r,i,5),this.setIndex(s),this.setAttribute(`position`,new _r(c,3)),this.setAttribute(`normal`,new _r(l,3)),this.setAttribute(`uv`,new _r(u,2));function p(e,t,n,r,i,a,p,m,h,g,_){let v=a/h,y=p/g,b=a/2,x=p/2,S=m/2,C=h+1,w=g+1,T=0,E=0,D=new W;for(let a=0;a<w;a++){let o=a*y-x;for(let s=0;s<C;s++)D[e]=(s*v-b)*r,D[t]=o*i,D[n]=S,c.push(D.x,D.y,D.z),D[e]=0,D[t]=0,D[n]=m>0?1:-1,l.push(D.x,D.y,D.z),u.push(s/h),u.push(1-a/g),T+=1}for(let e=0;e<g;e++)for(let t=0;t<h;t++){let n=d+t+C*e,r=d+t+C*(e+1),i=d+(t+1)+C*(e+1),a=d+(t+1)+C*e;s.push(n,r,a),s.push(r,i,a),E+=6}o.addGroup(f,E,_),f+=E,d+=T}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(t){return new e(t.width,t.height,t.depth,t.widthSegments,t.heightSegments,t.depthSegments)}},ca=class e extends Or{constructor(e=1,t=1,n=1,r=32,i=1,a=!1,o=0,s=Math.PI*2){super(),this.type=`CylinderGeometry`,this.parameters={radiusTop:e,radiusBottom:t,height:n,radialSegments:r,heightSegments:i,openEnded:a,thetaStart:o,thetaLength:s};let c=this;r=Math.floor(r),i=Math.floor(i);let l=[],u=[],d=[],f=[],p=0,m=[],h=n/2,g=0;_(),a===!1&&(e>0&&v(!0),t>0&&v(!1)),this.setIndex(l),this.setAttribute(`position`,new _r(u,3)),this.setAttribute(`normal`,new _r(d,3)),this.setAttribute(`uv`,new _r(f,2));function _(){let a=new W,_=new W,v=0,y=(t-e)/n;for(let c=0;c<=i;c++){let l=[],g=c/i,v=g*(t-e)+e;for(let e=0;e<=r;e++){let t=e/r,i=t*s+o,c=Math.sin(i),m=Math.cos(i);_.x=v*c,_.y=-g*n+h,_.z=v*m,u.push(_.x,_.y,_.z),a.set(c,y,m).normalize(),d.push(a.x,a.y,a.z),f.push(t,1-g),l.push(p++)}m.push(l)}for(let n=0;n<r;n++)for(let r=0;r<i;r++){let a=m[r][n],o=m[r+1][n],s=m[r+1][n+1],c=m[r][n+1];(e>0||r!==0)&&(l.push(a,o,c),v+=3),(t>0||r!==i-1)&&(l.push(o,s,c),v+=3)}c.addGroup(g,v,0),g+=v}function v(n){let i=p,a=new U,m=new W,_=0,v=n===!0?e:t,y=n===!0?1:-1;for(let e=1;e<=r;e++)u.push(0,h*y,0),d.push(0,y,0),f.push(.5,.5),p++;let b=p;for(let e=0;e<=r;e++){let t=e/r*s+o,n=Math.cos(t),i=Math.sin(t);m.x=v*i,m.y=h*y,m.z=v*n,u.push(m.x,m.y,m.z),d.push(0,y,0),a.x=n*.5+.5,a.y=i*.5*y+.5,f.push(a.x,a.y),p++}for(let e=0;e<r;e++){let t=i+e,r=b+e;n===!0?l.push(r,r+1,t):l.push(r+1,r,t),_+=3}c.addGroup(g,_,n===!0?1:2),g+=_}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(t){return new e(t.radiusTop,t.radiusBottom,t.height,t.radialSegments,t.heightSegments,t.openEnded,t.thetaStart,t.thetaLength)}},la=class{constructor(){this.type=`Curve`,this.arcLengthDivisions=200,this.needsUpdate=!1,this.cacheArcLengths=null}getPoint(){B(`Curve: .getPoint() not implemented.`)}getPointAt(e,t){let n=this.getUtoTmapping(e);return this.getPoint(n,t)}getPoints(e=5){let t=[];for(let n=0;n<=e;n++)t.push(this.getPoint(n/e));return t}getSpacedPoints(e=5){let t=[];for(let n=0;n<=e;n++)t.push(this.getPointAt(n/e));return t}getLength(){let e=this.getLengths();return e[e.length-1]}getLengths(e=this.arcLengthDivisions){if(this.cacheArcLengths&&this.cacheArcLengths.length===e+1&&!this.needsUpdate)return this.cacheArcLengths;this.needsUpdate=!1;let t=[],n,r=this.getPoint(0),i=0;t.push(0);for(let a=1;a<=e;a++)n=this.getPoint(a/e),i+=n.distanceTo(r),t.push(i),r=n;return this.cacheArcLengths=t,t}updateArcLengths(){this.needsUpdate=!0,this.getLengths()}getUtoTmapping(e,t=null){let n=this.getLengths(),r=0,i=n.length,a;a=t||e*n[i-1];let o=0,s=i-1,c;for(;o<=s;)if(r=Math.floor(o+(s-o)/2),c=n[r]-a,c<0)o=r+1;else if(c>0)s=r-1;else{s=r;break}if(r=s,n[r]===a)return r/(i-1);let l=n[r],u=n[r+1]-l,d=(a-l)/u;return(r+d)/(i-1)}getTangent(e,t){let n=1e-4,r=e-n,i=e+n;r<0&&(r=0),i>1&&(i=1);let a=this.getPoint(r),o=this.getPoint(i),s=t||(a.isVector2?new U:new W);return s.copy(o).sub(a).normalize(),s}getTangentAt(e,t){let n=this.getUtoTmapping(e);return this.getTangent(n,t)}computeFrenetFrames(e,t=!1){let n=new W,r=[],i=[],a=[],o=new W,s=new q;for(let t=0;t<=e;t++){let n=t/e;r[t]=this.getTangentAt(n,new W)}i[0]=new W,a[0]=new W;let c=Number.MAX_VALUE,l=Math.abs(r[0].x),u=Math.abs(r[0].y),d=Math.abs(r[0].z);l<=c&&(c=l,n.set(1,0,0)),u<=c&&(c=u,n.set(0,1,0)),d<=c&&n.set(0,0,1),o.crossVectors(r[0],n).normalize(),i[0].crossVectors(r[0],o),a[0].crossVectors(r[0],i[0]);for(let t=1;t<=e;t++){if(i[t]=i[t-1].clone(),a[t]=a[t-1].clone(),o.crossVectors(r[t-1],r[t]),o.length()>2**-52){o.normalize();let e=Math.acos(H(r[t-1].dot(r[t]),-1,1));i[t].applyMatrix4(s.makeRotationAxis(o,e))}a[t].crossVectors(r[t],i[t])}if(t===!0){let t=Math.acos(H(i[0].dot(i[e]),-1,1));t/=e,r[0].dot(o.crossVectors(i[0],i[e]))>0&&(t=-t);for(let n=1;n<=e;n++)i[n].applyMatrix4(s.makeRotationAxis(r[n],t*n)),a[n].crossVectors(r[n],i[n])}return{tangents:r,normals:i,binormals:a}}clone(){return new this.constructor().copy(this)}copy(e){return this.arcLengthDivisions=e.arcLengthDivisions,this}toJSON(){let e={metadata:{version:4.7,type:`Curve`,generator:`Curve.toJSON`}};return e.arcLengthDivisions=this.arcLengthDivisions,e.type=this.type,e}fromJSON(e){return this.arcLengthDivisions=e.arcLengthDivisions,this}},ua=class extends la{constructor(e=0,t=0,n=1,r=1,i=0,a=Math.PI*2,o=!1,s=0){super(),this.isEllipseCurve=!0,this.type=`EllipseCurve`,this.aX=e,this.aY=t,this.xRadius=n,this.yRadius=r,this.aStartAngle=i,this.aEndAngle=a,this.aClockwise=o,this.aRotation=s}getPoint(e,t=new U){let n=t,r=Math.PI*2,i=this.aEndAngle-this.aStartAngle,a=Math.abs(i)<2**-52;for(;i<0;)i+=r;for(;i>r;)i-=r;i<2**-52&&(i=a?0:r),this.aClockwise===!0&&!a&&(i===r?i=-r:i-=r);let o=this.aStartAngle+e*i,s=this.aX+this.xRadius*Math.cos(o),c=this.aY+this.yRadius*Math.sin(o);if(this.aRotation!==0){let e=Math.cos(this.aRotation),t=Math.sin(this.aRotation),n=s-this.aX,r=c-this.aY;s=n*e-r*t+this.aX,c=n*t+r*e+this.aY}return n.set(s,c)}copy(e){return super.copy(e),this.aX=e.aX,this.aY=e.aY,this.xRadius=e.xRadius,this.yRadius=e.yRadius,this.aStartAngle=e.aStartAngle,this.aEndAngle=e.aEndAngle,this.aClockwise=e.aClockwise,this.aRotation=e.aRotation,this}toJSON(){let e=super.toJSON();return e.aX=this.aX,e.aY=this.aY,e.xRadius=this.xRadius,e.yRadius=this.yRadius,e.aStartAngle=this.aStartAngle,e.aEndAngle=this.aEndAngle,e.aClockwise=this.aClockwise,e.aRotation=this.aRotation,e}fromJSON(e){return super.fromJSON(e),this.aX=e.aX,this.aY=e.aY,this.xRadius=e.xRadius,this.yRadius=e.yRadius,this.aStartAngle=e.aStartAngle,this.aEndAngle=e.aEndAngle,this.aClockwise=e.aClockwise,this.aRotation=e.aRotation,this}},da=class extends ua{constructor(e,t,n,r,i,a){super(e,t,n,n,r,i,a),this.isArcCurve=!0,this.type=`ArcCurve`}};function fa(){let e=0,t=0,n=0,r=0;function i(i,a,o,s){e=i,t=o,n=-3*i+3*a-2*o-s,r=2*i-2*a+o+s}return{initCatmullRom:function(e,t,n,r,a){i(t,n,a*(n-e),a*(r-t))},initNonuniformCatmullRom:function(e,t,n,r,a,o,s){let c=(t-e)/a-(n-e)/(a+o)+(n-t)/o,l=(n-t)/o-(r-t)/(o+s)+(r-n)/s;c*=o,l*=o,i(t,n,c,l)},calc:function(i){let a=i*i,o=a*i;return e+t*i+n*a+r*o}}}var pa=new W,ma=new W,ha=new fa,ga=new fa,_a=new fa,va=class extends la{constructor(e=[],t=!1,n=`centripetal`,r=.5){super(),this.isCatmullRomCurve3=!0,this.type=`CatmullRomCurve3`,this.points=e,this.closed=t,this.curveType=n,this.tension=r}getPoint(e,t=new W){let n=t,r=this.points,i=r.length,a=(i-+!this.closed)*e,o=Math.floor(a),s=a-o;this.closed?o+=o>0?0:(Math.floor(Math.abs(o)/i)+1)*i:s===0&&o===i-1&&(o=i-2,s=1);let c,l;this.closed||o>0?c=r[(o-1)%i]:(ma.subVectors(r[0],r[1]).add(r[0]),c=ma);let u=r[o%i],d=r[(o+1)%i];if(this.closed||o+2<i?l=r[(o+2)%i]:(pa.subVectors(r[i-1],r[i-2]).add(r[i-1]),l=pa),this.curveType===`centripetal`||this.curveType===`chordal`){let e=this.curveType===`chordal`?.5:.25,t=c.distanceToSquared(u)**+e,n=u.distanceToSquared(d)**+e,r=d.distanceToSquared(l)**+e;n<1e-4&&(n=1),t<1e-4&&(t=n),r<1e-4&&(r=n),ha.initNonuniformCatmullRom(c.x,u.x,d.x,l.x,t,n,r),ga.initNonuniformCatmullRom(c.y,u.y,d.y,l.y,t,n,r),_a.initNonuniformCatmullRom(c.z,u.z,d.z,l.z,t,n,r)}else this.curveType===`catmullrom`&&(ha.initCatmullRom(c.x,u.x,d.x,l.x,this.tension),ga.initCatmullRom(c.y,u.y,d.y,l.y,this.tension),_a.initCatmullRom(c.z,u.z,d.z,l.z,this.tension));return n.set(ha.calc(s),ga.calc(s),_a.calc(s)),n}copy(e){super.copy(e),this.points=[];for(let t=0,n=e.points.length;t<n;t++){let n=e.points[t];this.points.push(n.clone())}return this.closed=e.closed,this.curveType=e.curveType,this.tension=e.tension,this}toJSON(){let e=super.toJSON();e.points=[];for(let t=0,n=this.points.length;t<n;t++){let n=this.points[t];e.points.push(n.toArray())}return e.closed=this.closed,e.curveType=this.curveType,e.tension=this.tension,e}fromJSON(e){super.fromJSON(e),this.points=[];for(let t=0,n=e.points.length;t<n;t++){let n=e.points[t];this.points.push(new W().fromArray(n))}return this.closed=e.closed,this.curveType=e.curveType,this.tension=e.tension,this}};function ya(e,t,n,r,i){let a=(r-t)*.5,o=(i-n)*.5,s=e*e,c=e*s;return(2*n-2*r+a+o)*c+(-3*n+3*r-2*a-o)*s+a*e+n}function ba(e,t){let n=1-e;return n*n*t}function xa(e,t){return 2*(1-e)*e*t}function Sa(e,t){return e*e*t}function Ca(e,t,n,r){return ba(e,t)+xa(e,n)+Sa(e,r)}function wa(e,t){let n=1-e;return n*n*n*t}function Ta(e,t){let n=1-e;return 3*n*n*e*t}function Ea(e,t){return 3*(1-e)*e*e*t}function Da(e,t){return e*e*e*t}function Oa(e,t,n,r,i){return wa(e,t)+Ta(e,n)+Ea(e,r)+Da(e,i)}var ka=class extends la{constructor(e=new U,t=new U,n=new U,r=new U){super(),this.isCubicBezierCurve=!0,this.type=`CubicBezierCurve`,this.v0=e,this.v1=t,this.v2=n,this.v3=r}getPoint(e,t=new U){let n=t,r=this.v0,i=this.v1,a=this.v2,o=this.v3;return n.set(Oa(e,r.x,i.x,a.x,o.x),Oa(e,r.y,i.y,a.y,o.y)),n}copy(e){return super.copy(e),this.v0.copy(e.v0),this.v1.copy(e.v1),this.v2.copy(e.v2),this.v3.copy(e.v3),this}toJSON(){let e=super.toJSON();return e.v0=this.v0.toArray(),e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e.v3=this.v3.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v0.fromArray(e.v0),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this.v3.fromArray(e.v3),this}},Aa=class extends la{constructor(e=new W,t=new W,n=new W,r=new W){super(),this.isCubicBezierCurve3=!0,this.type=`CubicBezierCurve3`,this.v0=e,this.v1=t,this.v2=n,this.v3=r}getPoint(e,t=new W){let n=t,r=this.v0,i=this.v1,a=this.v2,o=this.v3;return n.set(Oa(e,r.x,i.x,a.x,o.x),Oa(e,r.y,i.y,a.y,o.y),Oa(e,r.z,i.z,a.z,o.z)),n}copy(e){return super.copy(e),this.v0.copy(e.v0),this.v1.copy(e.v1),this.v2.copy(e.v2),this.v3.copy(e.v3),this}toJSON(){let e=super.toJSON();return e.v0=this.v0.toArray(),e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e.v3=this.v3.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v0.fromArray(e.v0),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this.v3.fromArray(e.v3),this}},ja=class extends la{constructor(e=new U,t=new U){super(),this.isLineCurve=!0,this.type=`LineCurve`,this.v1=e,this.v2=t}getPoint(e,t=new U){let n=t;return e===1?n.copy(this.v2):(n.copy(this.v2).sub(this.v1),n.multiplyScalar(e).add(this.v1)),n}getPointAt(e,t){return this.getPoint(e,t)}getTangent(e,t=new U){return t.subVectors(this.v2,this.v1).normalize()}getTangentAt(e,t){return this.getTangent(e,t)}copy(e){return super.copy(e),this.v1.copy(e.v1),this.v2.copy(e.v2),this}toJSON(){let e=super.toJSON();return e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this}},Ma=class extends la{constructor(e=new W,t=new W){super(),this.isLineCurve3=!0,this.type=`LineCurve3`,this.v1=e,this.v2=t}getPoint(e,t=new W){let n=t;return e===1?n.copy(this.v2):(n.copy(this.v2).sub(this.v1),n.multiplyScalar(e).add(this.v1)),n}getPointAt(e,t){return this.getPoint(e,t)}getTangent(e,t=new W){return t.subVectors(this.v2,this.v1).normalize()}getTangentAt(e,t){return this.getTangent(e,t)}copy(e){return super.copy(e),this.v1.copy(e.v1),this.v2.copy(e.v2),this}toJSON(){let e=super.toJSON();return e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this}},Na=class extends la{constructor(e=new U,t=new U,n=new U){super(),this.isQuadraticBezierCurve=!0,this.type=`QuadraticBezierCurve`,this.v0=e,this.v1=t,this.v2=n}getPoint(e,t=new U){let n=t,r=this.v0,i=this.v1,a=this.v2;return n.set(Ca(e,r.x,i.x,a.x),Ca(e,r.y,i.y,a.y)),n}copy(e){return super.copy(e),this.v0.copy(e.v0),this.v1.copy(e.v1),this.v2.copy(e.v2),this}toJSON(){let e=super.toJSON();return e.v0=this.v0.toArray(),e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v0.fromArray(e.v0),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this}},Pa=class extends la{constructor(e=new W,t=new W,n=new W){super(),this.isQuadraticBezierCurve3=!0,this.type=`QuadraticBezierCurve3`,this.v0=e,this.v1=t,this.v2=n}getPoint(e,t=new W){let n=t,r=this.v0,i=this.v1,a=this.v2;return n.set(Ca(e,r.x,i.x,a.x),Ca(e,r.y,i.y,a.y),Ca(e,r.z,i.z,a.z)),n}copy(e){return super.copy(e),this.v0.copy(e.v0),this.v1.copy(e.v1),this.v2.copy(e.v2),this}toJSON(){let e=super.toJSON();return e.v0=this.v0.toArray(),e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v0.fromArray(e.v0),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this}},Fa=class extends la{constructor(e=[]){super(),this.isSplineCurve=!0,this.type=`SplineCurve`,this.points=e}getPoint(e,t=new U){let n=t,r=this.points,i=(r.length-1)*e,a=Math.floor(i),o=i-a,s=r[a===0?a:a-1],c=r[a],l=r[a>r.length-2?r.length-1:a+1],u=r[a>r.length-3?r.length-1:a+2];return n.set(ya(o,s.x,c.x,l.x,u.x),ya(o,s.y,c.y,l.y,u.y)),n}copy(e){super.copy(e),this.points=[];for(let t=0,n=e.points.length;t<n;t++){let n=e.points[t];this.points.push(n.clone())}return this}toJSON(){let e=super.toJSON();e.points=[];for(let t=0,n=this.points.length;t<n;t++){let n=this.points[t];e.points.push(n.toArray())}return e}fromJSON(e){super.fromJSON(e),this.points=[];for(let t=0,n=e.points.length;t<n;t++){let n=e.points[t];this.points.push(new U().fromArray(n))}return this}},Ia=Object.freeze({__proto__:null,ArcCurve:da,CatmullRomCurve3:va,CubicBezierCurve:ka,CubicBezierCurve3:Aa,EllipseCurve:ua,LineCurve:ja,LineCurve3:Ma,QuadraticBezierCurve:Na,QuadraticBezierCurve3:Pa,SplineCurve:Fa}),La=class extends la{constructor(){super(),this.type=`CurvePath`,this.curves=[],this.autoClose=!1}add(e){this.curves.push(e)}closePath(){let e=this.curves[0].getPoint(0),t=this.curves[this.curves.length-1].getPoint(1);if(!e.equals(t)){let n=e.isVector2===!0?`LineCurve`:`LineCurve3`;this.curves.push(new Ia[n](t,e))}return this}getPoint(e,t){let n=e*this.getLength(),r=this.getCurveLengths(),i=0;for(;i<r.length;){if(r[i]>=n){let e=r[i]-n,a=this.curves[i],o=a.getLength(),s=o===0?0:1-e/o;return a.getPointAt(s,t)}i++}return null}getLength(){let e=this.getCurveLengths();return e[e.length-1]}updateArcLengths(){this.needsUpdate=!0,this.cacheLengths=null,this.getCurveLengths()}getCurveLengths(){if(this.cacheLengths&&this.cacheLengths.length===this.curves.length)return this.cacheLengths;let e=[],t=0;for(let n=0,r=this.curves.length;n<r;n++)t+=this.curves[n].getLength(),e.push(t);return this.cacheLengths=e,e}getSpacedPoints(e=40){let t=[];for(let n=0;n<=e;n++)t.push(this.getPoint(n/e));return this.autoClose&&t.push(t[0]),t}getPoints(e=12){let t=[],n;for(let r=0,i=this.curves;r<i.length;r++){let a=i[r],o=a.isEllipseCurve?e*2:a.isLineCurve||a.isLineCurve3?1:a.isSplineCurve?e*a.points.length:e,s=a.getPoints(o);for(let e=0;e<s.length;e++){let r=s[e];n&&n.equals(r)||(t.push(r),n=r)}}return this.autoClose&&t.length>1&&!t[t.length-1].equals(t[0])&&t.push(t[0]),t}copy(e){super.copy(e),this.curves=[];for(let t=0,n=e.curves.length;t<n;t++){let n=e.curves[t];this.curves.push(n.clone())}return this.autoClose=e.autoClose,this}toJSON(){let e=super.toJSON();e.autoClose=this.autoClose,e.curves=[];for(let t=0,n=this.curves.length;t<n;t++){let n=this.curves[t];e.curves.push(n.toJSON())}return e}fromJSON(e){super.fromJSON(e),this.autoClose=e.autoClose,this.curves=[];for(let t=0,n=e.curves.length;t<n;t++){let n=e.curves[t];this.curves.push(new Ia[n.type]().fromJSON(n))}return this}},Ra=class extends La{constructor(e){super(),this.type=`Path`,this.currentPoint=new U,e&&this.setFromPoints(e)}setFromPoints(e){this.moveTo(e[0].x,e[0].y);for(let t=1,n=e.length;t<n;t++)this.lineTo(e[t].x,e[t].y);return this}moveTo(e,t){return this.currentPoint.set(e,t),this}lineTo(e,t){let n=new ja(this.currentPoint.clone(),new U(e,t));return this.curves.push(n),this.currentPoint.set(e,t),this}quadraticCurveTo(e,t,n,r){let i=new Na(this.currentPoint.clone(),new U(e,t),new U(n,r));return this.curves.push(i),this.currentPoint.set(n,r),this}bezierCurveTo(e,t,n,r,i,a){let o=new ka(this.currentPoint.clone(),new U(e,t),new U(n,r),new U(i,a));return this.curves.push(o),this.currentPoint.set(i,a),this}splineThru(e){let t=new Fa([this.currentPoint.clone()].concat(e));return this.curves.push(t),this.currentPoint.copy(e[e.length-1]),this}arc(e,t,n,r,i,a){let o=this.currentPoint.x,s=this.currentPoint.y;return this.absarc(e+o,t+s,n,r,i,a),this}absarc(e,t,n,r,i,a){return this.absellipse(e,t,n,n,r,i,a),this}ellipse(e,t,n,r,i,a,o,s){let c=this.currentPoint.x,l=this.currentPoint.y;return this.absellipse(e+c,t+l,n,r,i,a,o,s),this}absellipse(e,t,n,r,i,a,o,s){let c=new ua(e,t,n,r,i,a,o,s);if(this.curves.length>0){let e=c.getPoint(0);e.equals(this.currentPoint)||this.lineTo(e.x,e.y)}this.curves.push(c);let l=c.getPoint(1);return this.currentPoint.copy(l),this}copy(e){return super.copy(e),this.currentPoint.copy(e.currentPoint),this}toJSON(){let e=super.toJSON();return e.currentPoint=this.currentPoint.toArray(),e}fromJSON(e){return super.fromJSON(e),this.currentPoint.fromArray(e.currentPoint),this}},za=class extends Ra{constructor(e){super(e),this.uuid=lt(),this.type=`Shape`,this.holes=[]}getPointsHoles(e){let t=[];for(let n=0,r=this.holes.length;n<r;n++)t[n]=this.holes[n].getPoints(e);return t}extractPoints(e){return{shape:this.getPoints(e),holes:this.getPointsHoles(e)}}copy(e){super.copy(e),this.holes=[];for(let t=0,n=e.holes.length;t<n;t++){let n=e.holes[t];this.holes.push(n.clone())}return this}toJSON(){let e=super.toJSON();e.uuid=this.uuid,e.holes=[];for(let t=0,n=this.holes.length;t<n;t++){let n=this.holes[t];e.holes.push(n.toJSON())}return e}fromJSON(e){super.fromJSON(e),this.uuid=e.uuid,this.holes=[];for(let t=0,n=e.holes.length;t<n;t++){let n=e.holes[t];this.holes.push(new Ra().fromJSON(n))}return this}};function Ba(e,t,n=2){let r=t&&t.length,i=r?t[0]*n:e.length,a=Va(e,0,i,n,!0),o=[];if(!a||a.next===a.prev)return o;let s,c,l;if(r&&(a=Ja(e,t,a,n)),e.length>80*n){s=e[0],c=e[1];let t=s,r=c;for(let a=n;a<i;a+=n){let n=e[a],i=e[a+1];n<s&&(s=n),i<c&&(c=i),n>t&&(t=n),i>r&&(r=i)}l=Math.max(t-s,r-c),l=l===0?0:32767/l}return Ua(a,o,n,s,c,l,0),o}function Va(e,t,n,r,i){let a;if(i===yo(e,t,n,r)>0)for(let i=t;i<n;i+=r)a=go(i/r|0,e[i],e[i+1],a);else for(let i=n-r;i>=t;i-=r)a=go(i/r|0,e[i],e[i+1],a);return a&&so(a,a.next)&&(_o(a),a=a.next),a}function Ha(e,t){if(!e)return e;t||=e;let n=e,r;do if(r=!1,!n.steiner&&(so(n,n.next)||oo(n.prev,n,n.next)===0)){if(_o(n),n=t=n.prev,n===n.next)break;r=!0}else n=n.next;while(r||n!==t);return t}function Ua(e,t,n,r,i,a,o){if(!e)return;!o&&a&&$a(e,r,i,a);let s=e;for(;e.prev!==e.next;){let c=e.prev,l=e.next;if(a?Ga(e,r,i,a):Wa(e)){t.push(c.i,e.i,l.i),_o(e),e=l.next,s=l.next;continue}if(e=l,e===s){o?o===1?(e=Ka(Ha(e),t),Ua(e,t,n,r,i,a,2)):o===2&&qa(e,t,n,r,i,a):Ua(Ha(e),t,n,r,i,a,1);break}}}function Wa(e){let t=e.prev,n=e,r=e.next;if(oo(t,n,r)>=0)return!1;let i=t.x,a=n.x,o=r.x,s=t.y,c=n.y,l=r.y,u=Math.min(i,a,o),d=Math.min(s,c,l),f=Math.max(i,a,o),p=Math.max(s,c,l),m=r.next;for(;m!==t;){if(m.x>=u&&m.x<=f&&m.y>=d&&m.y<=p&&io(i,s,a,c,o,l,m.x,m.y)&&oo(m.prev,m,m.next)>=0)return!1;m=m.next}return!0}function Ga(e,t,n,r){let i=e.prev,a=e,o=e.next;if(oo(i,a,o)>=0)return!1;let s=i.x,c=a.x,l=o.x,u=i.y,d=a.y,f=o.y,p=Math.min(s,c,l),m=Math.min(u,d,f),h=Math.max(s,c,l),g=Math.max(u,d,f),_=to(p,m,t,n,r),v=to(h,g,t,n,r),y=e.prevZ,b=e.nextZ;for(;y&&y.z>=_&&b&&b.z<=v;){if(y.x>=p&&y.x<=h&&y.y>=m&&y.y<=g&&y!==i&&y!==o&&io(s,u,c,d,l,f,y.x,y.y)&&oo(y.prev,y,y.next)>=0||(y=y.prevZ,b.x>=p&&b.x<=h&&b.y>=m&&b.y<=g&&b!==i&&b!==o&&io(s,u,c,d,l,f,b.x,b.y)&&oo(b.prev,b,b.next)>=0))return!1;b=b.nextZ}for(;y&&y.z>=_;){if(y.x>=p&&y.x<=h&&y.y>=m&&y.y<=g&&y!==i&&y!==o&&io(s,u,c,d,l,f,y.x,y.y)&&oo(y.prev,y,y.next)>=0)return!1;y=y.prevZ}for(;b&&b.z<=v;){if(b.x>=p&&b.x<=h&&b.y>=m&&b.y<=g&&b!==i&&b!==o&&io(s,u,c,d,l,f,b.x,b.y)&&oo(b.prev,b,b.next)>=0)return!1;b=b.nextZ}return!0}function Ka(e,t){let n=e;do{let r=n.prev,i=n.next.next;!so(r,i)&&co(r,n,n.next,i)&&po(r,i)&&po(i,r)&&(t.push(r.i,n.i,i.i),_o(n),_o(n.next),n=e=i),n=n.next}while(n!==e);return Ha(n)}function qa(e,t,n,r,i,a){let o=e;do{let e=o.next.next;for(;e!==o.prev;){if(o.i!==e.i&&ao(o,e)){let s=ho(o,e);o=Ha(o,o.next),s=Ha(s,s.next),Ua(o,t,n,r,i,a,0),Ua(s,t,n,r,i,a,0);return}e=e.next}o=o.next}while(o!==e)}function Ja(e,t,n,r){let i=[];for(let n=0,a=t.length;n<a;n++){let o=Va(e,t[n]*r,n<a-1?t[n+1]*r:e.length,r,!1);o===o.next&&(o.steiner=!0),i.push(no(o))}i.sort(Ya);for(let e=0;e<i.length;e++)n=Xa(i[e],n);return n}function Ya(e,t){let n=e.x-t.x;return n===0&&(n=e.y-t.y,n===0&&(n=(e.next.y-e.y)/(e.next.x-e.x)-(t.next.y-t.y)/(t.next.x-t.x))),n}function Xa(e,t){let n=Za(e,t);if(!n)return t;let r=ho(n,e);return Ha(r,r.next),Ha(n,n.next)}function Za(e,t){let n=t,r=e.x,i=e.y,a=-1/0,o;if(so(e,n))return n;do{if(so(e,n.next))return n.next;if(i<=n.y&&i>=n.next.y&&n.next.y!==n.y){let e=n.x+(i-n.y)*(n.next.x-n.x)/(n.next.y-n.y);if(e<=r&&e>a&&(a=e,o=n.x<n.next.x?n:n.next,e===r))return o}n=n.next}while(n!==t);if(!o)return null;let s=o,c=o.x,l=o.y,u=1/0;n=o;do{if(r>=n.x&&n.x>=c&&r!==n.x&&ro(i<l?r:a,i,c,l,i<l?a:r,i,n.x,n.y)){let t=Math.abs(i-n.y)/(r-n.x);po(n,e)&&(t<u||t===u&&(n.x>o.x||n.x===o.x&&Qa(o,n)))&&(o=n,u=t)}n=n.next}while(n!==s);return o}function Qa(e,t){return oo(e.prev,e,t.prev)<0&&oo(t.next,e,e.next)<0}function $a(e,t,n,r){let i=e;do i.z===0&&(i.z=to(i.x,i.y,t,n,r)),i.prevZ=i.prev,i.nextZ=i.next,i=i.next;while(i!==e);i.prevZ.nextZ=null,i.prevZ=null,eo(i)}function eo(e){let t,n=1;do{let r=e,i;e=null;let a=null;for(t=0;r;){t++;let o=r,s=0;for(let e=0;e<n&&(s++,o=o.nextZ,o);e++);let c=n;for(;s>0||c>0&&o;)s!==0&&(c===0||!o||r.z<=o.z)?(i=r,r=r.nextZ,s--):(i=o,o=o.nextZ,c--),a?a.nextZ=i:e=i,i.prevZ=a,a=i;r=o}a.nextZ=null,n*=2}while(t>1);return e}function to(e,t,n,r,i){return e=(e-n)*i|0,t=(t-r)*i|0,e=(e|e<<8)&16711935,e=(e|e<<4)&252645135,e=(e|e<<2)&858993459,e=(e|e<<1)&1431655765,t=(t|t<<8)&16711935,t=(t|t<<4)&252645135,t=(t|t<<2)&858993459,t=(t|t<<1)&1431655765,e|t<<1}function no(e){let t=e,n=e;do(t.x<n.x||t.x===n.x&&t.y<n.y)&&(n=t),t=t.next;while(t!==e);return n}function ro(e,t,n,r,i,a,o,s){return(i-o)*(t-s)>=(e-o)*(a-s)&&(e-o)*(r-s)>=(n-o)*(t-s)&&(n-o)*(a-s)>=(i-o)*(r-s)}function io(e,t,n,r,i,a,o,s){return(e!==o||t!==s)&&ro(e,t,n,r,i,a,o,s)}function ao(e,t){return e.next.i!==t.i&&e.prev.i!==t.i&&!fo(e,t)&&(po(e,t)&&po(t,e)&&mo(e,t)&&(oo(e.prev,e,t.prev)||oo(e,t.prev,t))||so(e,t)&&oo(e.prev,e,e.next)>0&&oo(t.prev,t,t.next)>0)}function oo(e,t,n){return(t.y-e.y)*(n.x-t.x)-(t.x-e.x)*(n.y-t.y)}function so(e,t){return e.x===t.x&&e.y===t.y}function co(e,t,n,r){let i=uo(oo(e,t,n)),a=uo(oo(e,t,r)),o=uo(oo(n,r,e)),s=uo(oo(n,r,t));return!!(i!==a&&o!==s||i===0&&lo(e,n,t)||a===0&&lo(e,r,t)||o===0&&lo(n,e,r)||s===0&&lo(n,t,r))}function lo(e,t,n){return t.x<=Math.max(e.x,n.x)&&t.x>=Math.min(e.x,n.x)&&t.y<=Math.max(e.y,n.y)&&t.y>=Math.min(e.y,n.y)}function uo(e){return e>0?1:e<0?-1:0}function fo(e,t){let n=e;do{if(n.i!==e.i&&n.next.i!==e.i&&n.i!==t.i&&n.next.i!==t.i&&co(n,n.next,e,t))return!0;n=n.next}while(n!==e);return!1}function po(e,t){return oo(e.prev,e,e.next)<0?oo(e,t,e.next)>=0&&oo(e,e.prev,t)>=0:oo(e,t,e.prev)<0||oo(e,e.next,t)<0}function mo(e,t){let n=e,r=!1,i=(e.x+t.x)/2,a=(e.y+t.y)/2;do n.y>a!=n.next.y>a&&n.next.y!==n.y&&i<(n.next.x-n.x)*(a-n.y)/(n.next.y-n.y)+n.x&&(r=!r),n=n.next;while(n!==e);return r}function ho(e,t){let n=vo(e.i,e.x,e.y),r=vo(t.i,t.x,t.y),i=e.next,a=t.prev;return e.next=t,t.prev=e,n.next=i,i.prev=n,r.next=n,n.prev=r,a.next=r,r.prev=a,r}function go(e,t,n,r){let i=vo(e,t,n);return r?(i.next=r.next,i.prev=r,r.next.prev=i,r.next=i):(i.prev=i,i.next=i),i}function _o(e){e.next.prev=e.prev,e.prev.next=e.next,e.prevZ&&(e.prevZ.nextZ=e.nextZ),e.nextZ&&(e.nextZ.prevZ=e.prevZ)}function vo(e,t,n){return{i:e,x:t,y:n,prev:null,next:null,z:0,prevZ:null,nextZ:null,steiner:!1}}function yo(e,t,n,r){let i=0;for(let a=t,o=n-r;a<n;a+=r)i+=(e[o]-e[a])*(e[a+1]+e[o+1]),o=a;return i}var bo=class{static triangulate(e,t,n=2){return Ba(e,t,n)}},xo=class e{static area(e){let t=e.length,n=0;for(let r=t-1,i=0;i<t;r=i++)n+=e[r].x*e[i].y-e[i].x*e[r].y;return n*.5}static isClockWise(t){return e.area(t)<0}static triangulateShape(e,t){let n=[],r=[],i=[];So(e),Co(n,e);let a=e.length;t.forEach(So);for(let e=0;e<t.length;e++)r.push(a),a+=t[e].length,Co(n,t[e]);let o=bo.triangulate(n,r);for(let e=0;e<o.length;e+=3)i.push(o.slice(e,e+3));return i}};function So(e){let t=e.length;t>2&&e[t-1].equals(e[0])&&e.pop()}function Co(e,t){for(let n=0;n<t.length;n++)e.push(t[n].x),e.push(t[n].y)}var wo=class e extends Or{constructor(e=new za([new U(.5,.5),new U(-.5,.5),new U(-.5,-.5),new U(.5,-.5)]),t={}){super(),this.type=`ExtrudeGeometry`,this.parameters={shapes:e,options:t},e=Array.isArray(e)?e:[e];let n=this,r=[],i=[];for(let t=0,n=e.length;t<n;t++){let n=e[t];a(n)}this.setAttribute(`position`,new _r(r,3)),this.setAttribute(`uv`,new _r(i,2)),this.computeVertexNormals();function a(e){let a=[],o=t.curveSegments===void 0?12:t.curveSegments,s=t.steps===void 0?1:t.steps,c=t.depth===void 0?1:t.depth,l=t.bevelEnabled===void 0||t.bevelEnabled,u=t.bevelThickness===void 0?.2:t.bevelThickness,d=t.bevelSize===void 0?u-.1:t.bevelSize,f=t.bevelOffset===void 0?0:t.bevelOffset,p=t.bevelSegments===void 0?3:t.bevelSegments,m=t.extrudePath,h=t.UVGenerator===void 0?To:t.UVGenerator,g,_=!1,v,y,b,x;if(m){g=m.getSpacedPoints(s),_=!0,l=!1;let e=m.isCatmullRomCurve3?m.closed:!1;v=m.computeFrenetFrames(s,e),y=new W,b=new W,x=new W}l||(p=0,u=0,d=0,f=0);let S=e.extractPoints(o),C=S.shape,w=S.holes;if(!xo.isClockWise(C)){C=C.reverse();for(let e=0,t=w.length;e<t;e++){let t=w[e];xo.isClockWise(t)&&(w[e]=t.reverse())}}function T(e){let t=e[0];for(let n=1;n<=e.length;n++){let r=n%e.length,i=e[r],a=i.x-t.x,o=i.y-t.y,s=a*a+o*o,c=Math.max(Math.abs(i.x),Math.abs(i.y),Math.abs(t.x),Math.abs(t.y));if(s<=10000000000000001e-36*c*c){e.splice(r,1),n--;continue}t=i}}T(C),w.forEach(T);let E=w.length,D=C;for(let e=0;e<E;e++){let t=w[e];C=C.concat(t)}function O(e,t,n){return t||V(`ExtrudeGeometry: vec does not exist`),e.clone().addScaledVector(t,n)}let k=C.length;function A(e,t,n){let r,i,a,o=e.x-t.x,s=e.y-t.y,c=n.x-e.x,l=n.y-e.y,u=o*o+s*s,d=o*l-s*c;if(Math.abs(d)>2**-52){let d=Math.sqrt(u),f=Math.sqrt(c*c+l*l),p=t.x-s/d,m=t.y+o/d,h=n.x-l/f,g=n.y+c/f,_=((h-p)*l-(g-m)*c)/(o*l-s*c);r=p+o*_-e.x,i=m+s*_-e.y;let v=r*r+i*i;if(v<=2)return new U(r,i);a=Math.sqrt(v/2)}else{let e=!1;o>2**-52?c>2**-52&&(e=!0):o<-(2**-52)?c<-(2**-52)&&(e=!0):Math.sign(s)===Math.sign(l)&&(e=!0),e?(r=-s,i=o,a=Math.sqrt(u)):(r=o,i=s,a=Math.sqrt(u/2))}return new U(r/a,i/a)}let ee=[];for(let e=0,t=D.length,n=t-1,r=e+1;e<t;e++,n++,r++)n===t&&(n=0),r===t&&(r=0),ee[e]=A(D[e],D[n],D[r]);let te=[],j,ne=ee.concat();for(let e=0,t=E;e<t;e++){let t=w[e];j=[];for(let e=0,n=t.length,r=n-1,i=e+1;e<n;e++,r++,i++)r===n&&(r=0),i===n&&(i=0),j[e]=A(t[e],t[r],t[i]);te.push(j),ne=ne.concat(j)}let M;if(p===0)M=xo.triangulateShape(D,w);else{let e=[],t=[];for(let n=0;n<p;n++){let r=n/p,i=u*Math.cos(r*Math.PI/2),a=d*Math.sin(r*Math.PI/2)+f;for(let t=0,n=D.length;t<n;t++){let n=O(D[t],ee[t],a);se(n.x,n.y,-i),r===0&&e.push(n)}for(let e=0,n=E;e<n;e++){let n=w[e];j=te[e];let o=[];for(let e=0,t=n.length;e<t;e++){let t=O(n[e],j[e],a);se(t.x,t.y,-i),r===0&&o.push(t)}r===0&&t.push(o)}}M=xo.triangulateShape(e,t)}let N=M.length,re=d+f;for(let e=0;e<k;e++){let t=l?O(C[e],ne[e],re):C[e];_?(b.copy(v.normals[0]).multiplyScalar(t.x),y.copy(v.binormals[0]).multiplyScalar(t.y),x.copy(g[0]).add(b).add(y),se(x.x,x.y,x.z)):se(t.x,t.y,0)}for(let e=1;e<=s;e++)for(let t=0;t<k;t++){let n=l?O(C[t],ne[t],re):C[t];_?(b.copy(v.normals[e]).multiplyScalar(n.x),y.copy(v.binormals[e]).multiplyScalar(n.y),x.copy(g[e]).add(b).add(y),se(x.x,x.y,x.z)):se(n.x,n.y,c/s*e)}for(let e=p-1;e>=0;e--){let t=e/p,n=u*Math.cos(t*Math.PI/2),r=d*Math.sin(t*Math.PI/2)+f;for(let e=0,t=D.length;e<t;e++){let t=O(D[e],ee[e],r);se(t.x,t.y,c+n)}for(let e=0,t=w.length;e<t;e++){let t=w[e];j=te[e];for(let e=0,i=t.length;e<i;e++){let i=O(t[e],j[e],r);_?se(i.x,i.y+g[s-1].y,g[s-1].x+n):se(i.x,i.y,c+n)}}}ie(),ae();function ie(){let e=r.length/3;if(l){let e=0,t=k*e;for(let e=0;e<N;e++){let n=M[e];ce(n[2]+t,n[1]+t,n[0]+t)}e=s+p*2,t=k*e;for(let e=0;e<N;e++){let n=M[e];ce(n[0]+t,n[1]+t,n[2]+t)}}else{for(let e=0;e<N;e++){let t=M[e];ce(t[2],t[1],t[0])}for(let e=0;e<N;e++){let t=M[e];ce(t[0]+k*s,t[1]+k*s,t[2]+k*s)}}n.addGroup(e,r.length/3-e,0)}function ae(){let e=r.length/3,t=0;oe(D,t),t+=D.length;for(let e=0,n=w.length;e<n;e++){let n=w[e];oe(n,t),t+=n.length}n.addGroup(e,r.length/3-e,1)}function oe(e,t){let n=e.length;for(;--n>=0;){let r=n,i=n-1;i<0&&(i=e.length-1);for(let e=0,n=s+p*2;e<n;e++){let n=k*e,a=k*(e+1);le(t+r+n,t+i+n,t+i+a,t+r+a)}}}function se(e,t,n){a.push(e),a.push(t),a.push(n)}function ce(e,t,i){P(e),P(t),P(i);let a=r.length/3,o=h.generateTopUV(n,r,a-3,a-2,a-1);ue(o[0]),ue(o[1]),ue(o[2])}function le(e,t,i,a){P(e),P(t),P(a),P(t),P(i),P(a);let o=r.length/3,s=h.generateSideWallUV(n,r,o-6,o-3,o-2,o-1);ue(s[0]),ue(s[1]),ue(s[3]),ue(s[1]),ue(s[2]),ue(s[3])}function P(e){r.push(a[e*3+0]),r.push(a[e*3+1]),r.push(a[e*3+2])}function ue(e){i.push(e.x),i.push(e.y)}}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}toJSON(){let e=super.toJSON(),t=this.parameters.shapes,n=this.parameters.options;return Eo(t,n,e)}static fromJSON(t,n){let r=[];for(let e=0,i=t.shapes.length;e<i;e++){let i=n[t.shapes[e]];r.push(i)}let i=t.options.extrudePath;return i!==void 0&&(t.options.extrudePath=new Ia[i.type]().fromJSON(i)),new e(r,t.options)}},To={generateTopUV:function(e,t,n,r,i){let a=t[n*3],o=t[n*3+1],s=t[r*3],c=t[r*3+1],l=t[i*3],u=t[i*3+1];return[new U(a,o),new U(s,c),new U(l,u)]},generateSideWallUV:function(e,t,n,r,i,a){let o=t[n*3],s=t[n*3+1],c=t[n*3+2],l=t[r*3],u=t[r*3+1],d=t[r*3+2],f=t[i*3],p=t[i*3+1],m=t[i*3+2],h=t[a*3],g=t[a*3+1],_=t[a*3+2];return Math.abs(s-u)<Math.abs(o-l)?[new U(o,1-c),new U(l,1-d),new U(f,1-m),new U(h,1-_)]:[new U(s,1-c),new U(u,1-d),new U(p,1-m),new U(g,1-_)]}};function Eo(e,t,n){if(n.shapes=[],Array.isArray(e))for(let t=0,r=e.length;t<r;t++){let r=e[t];n.shapes.push(r.uuid)}else n.shapes.push(e.uuid);return n.options=Object.assign({},t),t.extrudePath!==void 0&&(n.options.extrudePath=t.extrudePath.toJSON()),n}var Do=class e extends Or{constructor(e=1,t=1,n=1,r=1){super(),this.type=`PlaneGeometry`,this.parameters={width:e,height:t,widthSegments:n,heightSegments:r};let i=e/2,a=t/2,o=Math.floor(n),s=Math.floor(r),c=o+1,l=s+1,u=e/o,d=t/s,f=[],p=[],m=[],h=[];for(let e=0;e<l;e++){let t=e*d-a;for(let n=0;n<c;n++){let r=n*u-i;p.push(r,-t,0),m.push(0,0,1),h.push(n/o),h.push(1-e/s)}}for(let e=0;e<s;e++)for(let t=0;t<o;t++){let n=t+c*e,r=t+c*(e+1),i=t+1+c*(e+1),a=t+1+c*e;f.push(n,r,a),f.push(r,i,a)}this.setIndex(f),this.setAttribute(`position`,new _r(p,3)),this.setAttribute(`normal`,new _r(m,3)),this.setAttribute(`uv`,new _r(h,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(t){return new e(t.width,t.height,t.widthSegments,t.heightSegments)}},Oo=class e extends Or{constructor(e=1,t=.4,n=12,r=48,i=Math.PI*2,a=0,o=Math.PI*2){super(),this.type=`TorusGeometry`,this.parameters={radius:e,tube:t,radialSegments:n,tubularSegments:r,arc:i,thetaStart:a,thetaLength:o},n=Math.floor(n),r=Math.floor(r);let s=[],c=[],l=[],u=[],d=new W,f=new W,p=new W;for(let s=0;s<=n;s++){let m=a+s/n*o;for(let a=0;a<=r;a++){let o=a/r*i;f.x=(e+t*Math.cos(m))*Math.cos(o),f.y=(e+t*Math.cos(m))*Math.sin(o),f.z=t*Math.sin(m),c.push(f.x,f.y,f.z),d.x=e*Math.cos(o),d.y=e*Math.sin(o),p.subVectors(f,d).normalize(),l.push(p.x,p.y,p.z),u.push(a/r),u.push(s/n)}}for(let e=1;e<=n;e++)for(let t=1;t<=r;t++){let n=(r+1)*e+t-1,i=(r+1)*(e-1)+t-1,a=(r+1)*(e-1)+t,o=(r+1)*e+t;s.push(n,i,o),s.push(i,a,o)}this.setIndex(s),this.setAttribute(`position`,new _r(c,3)),this.setAttribute(`normal`,new _r(l,3)),this.setAttribute(`uv`,new _r(u,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(t){return new e(t.radius,t.tube,t.radialSegments,t.tubularSegments,t.arc)}};function ko(e){let t={};for(let n in e){t[n]={};for(let r in e[n]){let i=e[n][r];if(jo(i))i.isRenderTargetTexture?(B(`UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms().`),t[n][r]=null):t[n][r]=i.clone();else if(Array.isArray(i)){if(jo(i[0])){let e=[];for(let t=0,n=i.length;t<n;t++)e[t]=i[t].clone();t[n][r]=e}else t[n][r]=i.slice()}else t[n][r]=i}}return t}function Ao(e){let t={};for(let n=0;n<e.length;n++){let r=ko(e[n]);for(let e in r)t[e]=r[e]}return t}function jo(e){return e&&(e.isColor||e.isMatrix3||e.isMatrix4||e.isVector2||e.isVector3||e.isVector4||e.isTexture||e.isQuaternion)}function Mo(e){let t=[];for(let n=0;n<e.length;n++)t.push(e[n].clone());return t}function No(e){let t=e.getRenderTarget();return t===null?e.outputColorSpace:t.isXRRenderTarget===!0?t.texture.colorSpace:K.workingColorSpace}var Po={clone:ko,merge:Ao},Fo=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,Io=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`,Lo=class extends Nr{constructor(e){super(),this.isShaderMaterial=!0,this.type=`ShaderMaterial`,this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=Fo,this.fragmentShader=Io,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,e!==void 0&&this.setValues(e)}copy(e){return super.copy(e),this.fragmentShader=e.fragmentShader,this.vertexShader=e.vertexShader,this.uniforms=ko(e.uniforms),this.uniformsGroups=Mo(e.uniformsGroups),this.defines=Object.assign({},e.defines),this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.fog=e.fog,this.lights=e.lights,this.clipping=e.clipping,this.extensions=Object.assign({},e.extensions),this.glslVersion=e.glslVersion,this.defaultAttributeValues=Object.assign({},e.defaultAttributeValues),this.index0AttributeName=e.index0AttributeName,this.uniformsNeedUpdate=e.uniformsNeedUpdate,this}toJSON(e){let t=super.toJSON(e);t.glslVersion=this.glslVersion,t.uniforms={};for(let n in this.uniforms){let r=this.uniforms[n].value;r&&r.isTexture?t.uniforms[n]={type:`t`,value:r.toJSON(e).uuid}:r&&r.isColor?t.uniforms[n]={type:`c`,value:r.getHex()}:r&&r.isVector2?t.uniforms[n]={type:`v2`,value:r.toArray()}:r&&r.isVector3?t.uniforms[n]={type:`v3`,value:r.toArray()}:r&&r.isVector4?t.uniforms[n]={type:`v4`,value:r.toArray()}:r&&r.isMatrix3?t.uniforms[n]={type:`m3`,value:r.toArray()}:r&&r.isMatrix4?t.uniforms[n]={type:`m4`,value:r.toArray()}:t.uniforms[n]={value:r}}Object.keys(this.defines).length>0&&(t.defines=this.defines),t.vertexShader=this.vertexShader,t.fragmentShader=this.fragmentShader,t.lights=this.lights,t.clipping=this.clipping;let n={};for(let e in this.extensions)this.extensions[e]===!0&&(n[e]=!0);return Object.keys(n).length>0&&(t.extensions=n),t}fromJSON(e,t){if(super.fromJSON(e,t),e.uniforms!==void 0)for(let n in e.uniforms){let r=e.uniforms[n];switch(this.uniforms[n]={},r.type){case`t`:this.uniforms[n].value=t[r.value]||null;break;case`c`:this.uniforms[n].value=new J().setHex(r.value);break;case`v2`:this.uniforms[n].value=new U().fromArray(r.value);break;case`v3`:this.uniforms[n].value=new W().fromArray(r.value);break;case`v4`:this.uniforms[n].value=new Jt().fromArray(r.value);break;case`m3`:this.uniforms[n].value=new G().fromArray(r.value);break;case`m4`:this.uniforms[n].value=new q().fromArray(r.value);break;default:this.uniforms[n].value=r.value}}if(e.defines!==void 0&&(this.defines=e.defines),e.vertexShader!==void 0&&(this.vertexShader=e.vertexShader),e.fragmentShader!==void 0&&(this.fragmentShader=e.fragmentShader),e.glslVersion!==void 0&&(this.glslVersion=e.glslVersion),e.extensions!==void 0)for(let t in e.extensions)this.extensions[t]=e.extensions[t];return e.lights!==void 0&&(this.lights=e.lights),e.clipping!==void 0&&(this.clipping=e.clipping),this}},Ro=class extends Lo{constructor(e){super(e),this.isRawShaderMaterial=!0,this.type=`RawShaderMaterial`}},zo=class extends Nr{constructor(e){super(),this.isMeshStandardMaterial=!0,this.type=`MeshStandardMaterial`,this.defines={STANDARD:``},this.color=new J(16777215),this.roughness=1,this.metalness=0,this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.emissive=new J(0),this.emissiveIntensity=1,this.emissiveMap=null,this.bumpMap=null,this.bumpScale=1,this.normalMap=null,this.normalMapType=0,this.normalScale=new U(1,1),this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.roughnessMap=null,this.metalnessMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new ln,this.envMapIntensity=1,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap=`round`,this.wireframeLinejoin=`round`,this.flatShading=!1,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.defines={STANDARD:``},this.color.copy(e.color),this.roughness=e.roughness,this.metalness=e.metalness,this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.emissive.copy(e.emissive),this.emissiveMap=e.emissiveMap,this.emissiveIntensity=e.emissiveIntensity,this.bumpMap=e.bumpMap,this.bumpScale=e.bumpScale,this.normalMap=e.normalMap,this.normalMapType=e.normalMapType,this.normalScale.copy(e.normalScale),this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.roughnessMap=e.roughnessMap,this.metalnessMap=e.metalnessMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.envMapIntensity=e.envMapIntensity,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.flatShading=e.flatShading,this.fog=e.fog,this}},Bo=class extends zo{constructor(e){super(),this.isMeshPhysicalMaterial=!0,this.defines={STANDARD:``,PHYSICAL:``},this.type=`MeshPhysicalMaterial`,this.anisotropyRotation=0,this.anisotropyMap=null,this.clearcoatMap=null,this.clearcoatRoughness=0,this.clearcoatRoughnessMap=null,this.clearcoatNormalScale=new U(1,1),this.clearcoatNormalMap=null,this.ior=1.5,Object.defineProperty(this,"reflectivity",{get:function(){return H(2.5*(this.ior-1)/(this.ior+1),0,1)},set:function(e){this.ior=(1+.4*e)/(1-.4*e)}}),this.iridescenceMap=null,this.iridescenceIOR=1.3,this.iridescenceThicknessRange=[100,400],this.iridescenceThicknessMap=null,this.sheenColor=new J(0),this.sheenColorMap=null,this.sheenRoughness=1,this.sheenRoughnessMap=null,this.transmissionMap=null,this.thickness=0,this.thicknessMap=null,this.attenuationDistance=1/0,this.attenuationColor=new J(1,1,1),this.specularIntensity=1,this.specularIntensityMap=null,this.specularColor=new J(1,1,1),this.specularColorMap=null,this._anisotropy=0,this._clearcoat=0,this._dispersion=0,this._iridescence=0,this._sheen=0,this._transmission=0,this.setValues(e)}get anisotropy(){return this._anisotropy}set anisotropy(e){this._anisotropy>0!=e>0&&this.version++,this._anisotropy=e}get clearcoat(){return this._clearcoat}set clearcoat(e){this._clearcoat>0!=e>0&&this.version++,this._clearcoat=e}get iridescence(){return this._iridescence}set iridescence(e){this._iridescence>0!=e>0&&this.version++,this._iridescence=e}get dispersion(){return this._dispersion}set dispersion(e){this._dispersion>0!=e>0&&this.version++,this._dispersion=e}get sheen(){return this._sheen}set sheen(e){this._sheen>0!=e>0&&this.version++,this._sheen=e}get transmission(){return this._transmission}set transmission(e){this._transmission>0!=e>0&&this.version++,this._transmission=e}copy(e){return super.copy(e),this.defines={STANDARD:``,PHYSICAL:``},this.anisotropy=e.anisotropy,this.anisotropyRotation=e.anisotropyRotation,this.anisotropyMap=e.anisotropyMap,this.clearcoat=e.clearcoat,this.clearcoatMap=e.clearcoatMap,this.clearcoatRoughness=e.clearcoatRoughness,this.clearcoatRoughnessMap=e.clearcoatRoughnessMap,this.clearcoatNormalMap=e.clearcoatNormalMap,this.clearcoatNormalScale.copy(e.clearcoatNormalScale),this.dispersion=e.dispersion,this.ior=e.ior,this.iridescence=e.iridescence,this.iridescenceMap=e.iridescenceMap,this.iridescenceIOR=e.iridescenceIOR,this.iridescenceThicknessRange=[...e.iridescenceThicknessRange],this.iridescenceThicknessMap=e.iridescenceThicknessMap,this.sheen=e.sheen,this.sheenColor.copy(e.sheenColor),this.sheenColorMap=e.sheenColorMap,this.sheenRoughness=e.sheenRoughness,this.sheenRoughnessMap=e.sheenRoughnessMap,this.transmission=e.transmission,this.transmissionMap=e.transmissionMap,this.thickness=e.thickness,this.thicknessMap=e.thicknessMap,this.attenuationDistance=e.attenuationDistance,this.attenuationColor.copy(e.attenuationColor),this.specularIntensity=e.specularIntensity,this.specularIntensityMap=e.specularIntensityMap,this.specularColor.copy(e.specularColor),this.specularColorMap=e.specularColorMap,this}},Vo=class extends Nr{constructor(e){super(),this.isMeshDepthMaterial=!0,this.type=`MeshDepthMaterial`,this.depthPacking=Ve,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(e)}copy(e){return super.copy(e),this.depthPacking=e.depthPacking,this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this}},Ho=class extends Nr{constructor(e){super(),this.isMeshDistanceMaterial=!0,this.type=`MeshDistanceMaterial`,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(e)}copy(e){return super.copy(e),this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this}};function Uo(e,t){return!e||e.constructor===t?e:typeof t.BYTES_PER_ELEMENT==`number`?new t(e):Array.prototype.slice.call(e)}function Wo(e){function t(t,n){return e[t]-e[n]}let n=e.length,r=Array(n);for(let e=0;e!==n;++e)r[e]=e;return r.sort(t),r}function Go(e,t,n){let r=e.length,i=new e.constructor(r);for(let a=0,o=0;o!==r;++a){let r=n[a]*t;for(let n=0;n!==t;++n)i[o++]=e[r+n]}return i}function Ko(e,t,n,r){let i=1,a=e[0];for(;a!==void 0&&a[r]===void 0;)a=e[i++];if(a===void 0)return;let o=a[r];if(o!==void 0){if(Array.isArray(o))do o=a[r],o!==void 0&&(t.push(a.time),n.push(...o)),a=e[i++];while(a!==void 0);else if(o.toArray!==void 0)do o=a[r],o!==void 0&&(t.push(a.time),o.toArray(n,n.length)),a=e[i++];while(a!==void 0);else do o=a[r],o!==void 0&&(t.push(a.time),n.push(o)),a=e[i++];while(a!==void 0)}}var qo=class{constructor(e,t,n,r){this.parameterPositions=e,this._cachedIndex=0,this.resultBuffer=r===void 0?new t.constructor(n):r,this.sampleValues=t,this.valueSize=n,this.settings=null,this.DefaultSettings_={}}evaluate(e){let t=this.parameterPositions,n=this._cachedIndex,r=t[n],i=t[n-1];validate_interval:{seek:{let a;linear_scan:{forward_scan:if(!(e<r)){for(let a=n+2;;){if(r===void 0){if(e<i)break forward_scan;return n=t.length,this._cachedIndex=n,this.copySampleValue_(n-1)}if(n===a)break;if(i=r,r=t[++n],e<r)break seek}a=t.length;break linear_scan}if(!(e>=i)){let o=t[1];e<o&&(n=2,i=o);for(let a=n-2;;){if(i===void 0)return this._cachedIndex=0,this.copySampleValue_(0);if(n===a)break;if(r=i,i=t[--n-1],e>=i)break seek}a=n,n=0;break linear_scan}break validate_interval}for(;n<a;){let r=n+a>>>1;e<t[r]?a=r:n=r+1}if(r=t[n],i=t[n-1],i===void 0)return this._cachedIndex=0,this.copySampleValue_(0);if(r===void 0)return n=t.length,this._cachedIndex=n,this.copySampleValue_(n-1)}this._cachedIndex=n,this.intervalChanged_(n,i,r)}return this.interpolate_(n,i,e,r)}getSettings_(){return this.settings||this.DefaultSettings_}copySampleValue_(e){let t=this.resultBuffer,n=this.sampleValues,r=this.valueSize,i=e*r;for(let e=0;e!==r;++e)t[e]=n[i+e];return t}interpolate_(){throw Error(`THREE.Interpolant: Call to abstract method.`)}intervalChanged_(){}},Jo=class extends qo{constructor(e,t,n,r){super(e,t,n,r),this._weightPrev=-0,this._offsetPrev=-0,this._weightNext=-0,this._offsetNext=-0,this.DefaultSettings_={endingStart:Le,endingEnd:Le}}intervalChanged_(e,t,n){let r=this.parameterPositions,i=e-2,a=e+1,o=r[i],s=r[a];if(o===void 0)switch(this.getSettings_().endingStart){case Re:i=e,o=2*t-n;break;case ze:i=r.length-2,o=t+r[i]-r[i+1];break;default:i=e,o=n}if(s===void 0)switch(this.getSettings_().endingEnd){case Re:a=e,s=2*n-t;break;case ze:a=1,s=n+r[1]-r[0];break;default:a=e-1,s=t}let c=(n-t)*.5,l=this.valueSize;this._weightPrev=c/(t-o),this._weightNext=c/(s-n),this._offsetPrev=i*l,this._offsetNext=a*l}interpolate_(e,t,n,r){let i=this.resultBuffer,a=this.sampleValues,o=this.valueSize,s=e*o,c=s-o,l=this._offsetPrev,u=this._offsetNext,d=this._weightPrev,f=this._weightNext,p=(n-t)/(r-t),m=p*p,h=m*p,g=-d*h+2*d*m-d*p,_=(1+d)*h+(-1.5-2*d)*m+(-.5+d)*p+1,v=(-1-f)*h+(1.5+f)*m+.5*p,y=f*h-f*m;for(let e=0;e!==o;++e)i[e]=g*a[l+e]+_*a[c+e]+v*a[s+e]+y*a[u+e];return i}},Yo=class extends qo{constructor(e,t,n,r){super(e,t,n,r)}interpolate_(e,t,n,r){let i=this.resultBuffer,a=this.sampleValues,o=this.valueSize,s=e*o,c=s-o,l=(n-t)/(r-t),u=1-l;for(let e=0;e!==o;++e)i[e]=a[c+e]*u+a[s+e]*l;return i}},Xo=class extends qo{constructor(e,t,n,r){super(e,t,n,r)}interpolate_(e){return this.copySampleValue_(e-1)}},Zo=class extends qo{interpolate_(e,t,n,r){let i=this.resultBuffer,a=this.sampleValues,o=this.valueSize,s=e*o,c=s-o,l=this.inTangents,u=this.outTangents;if(!l||!u){let e=(n-t)/(r-t),l=1-e;for(let t=0;t!==o;++t)i[t]=a[c+t]*l+a[s+t]*e;return i}let d=o*2,f=e-1;for(let p=0;p!==o;++p){let o=a[c+p],m=a[s+p],h=f*d+p*2,g=u[h],_=u[h+1],v=e*d+p*2,y=l[v],b=l[v+1],x=(n-t)/(r-t),S,C,w,T,E;for(let e=0;e<8;e++){S=x*x,C=S*x,w=1-x,T=w*w,E=T*w;let e=E*t+3*T*x*g+3*w*S*y+C*r-n;if(Math.abs(e)<1e-10)break;let i=3*T*(g-t)+6*w*x*(y-g)+3*S*(r-y);if(Math.abs(i)<1e-10)break;x-=e/i,x=Math.max(0,Math.min(1,x))}i[p]=E*o+3*T*x*_+3*w*S*b+C*m}return i}},Qo=class{constructor(e,t,n,r){if(e===void 0)throw Error(`THREE.KeyframeTrack: track name is undefined`);if(t===void 0||t.length===0)throw Error(`THREE.KeyframeTrack: no keyframes in track named `+e);this.name=e,this.times=Uo(t,this.TimeBufferType),this.values=Uo(n,this.ValueBufferType),this.setInterpolation(r||this.DefaultInterpolation)}static toJSON(e){let t=e.constructor,n;if(t.toJSON!==this.toJSON)n=t.toJSON(e);else{n={name:e.name,times:Uo(e.times,Array),values:Uo(e.values,Array)};let t=e.getInterpolation();t!==e.DefaultInterpolation&&(n.interpolation=t)}return n.type=e.ValueTypeName,n}InterpolantFactoryMethodDiscrete(e){return new Xo(this.times,this.values,this.getValueSize(),e)}InterpolantFactoryMethodLinear(e){return new Yo(this.times,this.values,this.getValueSize(),e)}InterpolantFactoryMethodSmooth(e){return new Jo(this.times,this.values,this.getValueSize(),e)}InterpolantFactoryMethodBezier(e){let t=new Zo(this.times,this.values,this.getValueSize(),e);return this.settings&&(t.inTangents=this.settings.inTangents,t.outTangents=this.settings.outTangents),t}setInterpolation(e){let t;switch(e){case Pe:t=this.InterpolantFactoryMethodDiscrete;break;case Fe:t=this.InterpolantFactoryMethodLinear;break;case L:t=this.InterpolantFactoryMethodSmooth;break;case Ie:t=this.InterpolantFactoryMethodBezier}if(t===void 0){let t=`unsupported interpolation for `+this.ValueTypeName+` keyframe track named `+this.name;if(this.createInterpolant===void 0){if(e!==this.DefaultInterpolation)this.setInterpolation(this.DefaultInterpolation);else throw Error(t)}return B(`KeyframeTrack:`,t),this}return this.createInterpolant=t,this}getInterpolation(){switch(this.createInterpolant){case this.InterpolantFactoryMethodDiscrete:return Pe;case this.InterpolantFactoryMethodLinear:return Fe;case this.InterpolantFactoryMethodSmooth:return L;case this.InterpolantFactoryMethodBezier:return Ie}}getValueSize(){return this.values.length/this.times.length}shift(e){if(e!==0){let t=this.times;for(let n=0,r=t.length;n!==r;++n)t[n]+=e}return this}scale(e){if(e!==1){let t=this.times;for(let n=0,r=t.length;n!==r;++n)t[n]*=e}return this}trim(e,t){let n=this.times,r=n.length,i=0,a=r-1;for(;i!==r&&n[i]<e;)++i;for(;a!==-1&&n[a]>t;)--a;if(++a,i!==0||a!==r){i>=a&&(a=Math.max(a,1),i=a-1);let e=this.getValueSize();this.times=n.slice(i,a),this.values=this.values.slice(i*e,a*e)}return this}validate(){let e=!0,t=this.getValueSize();t-Math.floor(t)!==0&&(V(`KeyframeTrack: Invalid value size in track.`,this),e=!1);let n=this.times,r=this.values,i=n.length;i===0&&(V(`KeyframeTrack: Track is empty.`,this),e=!1);let a=null;for(let t=0;t!==i;t++){let r=n[t];if(typeof r==`number`&&isNaN(r)){V(`KeyframeTrack: Time is not a valid number.`,this,t,r),e=!1;break}if(a!==null&&a>r){V(`KeyframeTrack: Out of order keys.`,this,t,r,a),e=!1;break}a=r}if(r!==void 0&&Ye(r))for(let t=0,n=r.length;t!==n;++t){let n=r[t];if(isNaN(n)){V(`KeyframeTrack: Value is not a valid number.`,this,t,n),e=!1;break}}return e}optimize(){let e=this.times.slice(),t=this.values.slice(),n=this.getValueSize(),r=this.getInterpolation()===L,i=e.length-1,a=1;for(let o=1;o<i;++o){let i=!1,s=e[o];if(s!==e[o+1]&&(o!==1||s!==e[0])){if(r)i=!0;else{let e=o*n,r=e-n,a=e+n;for(let o=0;o!==n;++o){let n=t[e+o];if(n!==t[r+o]||n!==t[a+o]){i=!0;break}}}}if(i){if(o!==a){e[a]=e[o];let r=o*n,i=a*n;for(let e=0;e!==n;++e)t[i+e]=t[r+e]}++a}}if(i>0){e[a]=e[i];for(let e=i*n,r=a*n,o=0;o!==n;++o)t[r+o]=t[e+o];++a}return a===e.length?(this.times=e,this.values=t):(this.times=e.slice(0,a),this.values=t.slice(0,a*n)),this}clone(){let e=this.times.slice(),t=this.values.slice(),n=this.constructor,r=new n(this.name,e,t);return r.createInterpolant=this.createInterpolant,r}};Qo.prototype.ValueTypeName=``,Qo.prototype.TimeBufferType=Float32Array,Qo.prototype.ValueBufferType=Float32Array,Qo.prototype.DefaultInterpolation=Fe;var $o=class extends Qo{constructor(e,t,n){super(e,t,n)}};$o.prototype.ValueTypeName=`bool`,$o.prototype.ValueBufferType=Array,$o.prototype.DefaultInterpolation=Pe,$o.prototype.InterpolantFactoryMethodLinear=void 0,$o.prototype.InterpolantFactoryMethodSmooth=void 0;var es=class extends Qo{constructor(e,t,n,r){super(e,t,n,r)}};es.prototype.ValueTypeName=`color`;var ts=class extends Qo{constructor(e,t,n,r){super(e,t,n,r)}};ts.prototype.ValueTypeName=`number`;var ns=class extends qo{constructor(e,t,n,r){super(e,t,n,r)}interpolate_(e,t,n,r){let i=this.resultBuffer,a=this.sampleValues,o=this.valueSize,s=(n-t)/(r-t),c=e*o;for(let e=c+o;c!==e;c+=4)jt.slerpFlat(i,0,a,c-o,a,c,s);return i}},rs=class extends Qo{constructor(e,t,n,r){super(e,t,n,r)}InterpolantFactoryMethodLinear(e){return new ns(this.times,this.values,this.getValueSize(),e)}};rs.prototype.ValueTypeName=`quaternion`,rs.prototype.InterpolantFactoryMethodSmooth=void 0;var is=class extends Qo{constructor(e,t,n){super(e,t,n)}};is.prototype.ValueTypeName=`string`,is.prototype.ValueBufferType=Array,is.prototype.DefaultInterpolation=Pe,is.prototype.InterpolantFactoryMethodLinear=void 0,is.prototype.InterpolantFactoryMethodSmooth=void 0;var as=class extends Qo{constructor(e,t,n,r){super(e,t,n,r)}};as.prototype.ValueTypeName=`vector`;var os=class{constructor(e=``,t=-1,n=[],r=Be){this.name=e,this.tracks=n,this.duration=t,this.blendMode=r,this.uuid=lt(),this.userData={},this.duration<0&&this.resetDuration()}static parse(e){let t=[],n=e.tracks,r=1/(e.fps||1);for(let e=0,i=n.length;e!==i;++e)t.push(cs(n[e]).scale(r));let i=new this(e.name,e.duration,t,e.blendMode);return i.uuid=e.uuid,i.userData=JSON.parse(e.userData||`{}`),i}static toJSON(e){let t=[],n=e.tracks,r={name:e.name,duration:e.duration,tracks:t,uuid:e.uuid,blendMode:e.blendMode,userData:JSON.stringify(e.userData)};for(let e=0,r=n.length;e!==r;++e)t.push(Qo.toJSON(n[e]));return r}static CreateFromMorphTargetSequence(e,t,n,r){let i=t.length,a=[];for(let e=0;e<i;e++){let o=[],s=[];o.push((e+i-1)%i,e,(e+1)%i),s.push(0,1,0);let c=Wo(o);o=Go(o,1,c),s=Go(s,1,c),!r&&o[0]===0&&(o.push(i),s.push(s[0])),a.push(new ts(`.morphTargetInfluences[`+t[e].name+`]`,o,s).scale(1/n))}return new this(e,-1,a)}static findByName(e,t){let n=e;if(!Array.isArray(e)){let t=e;n=t.geometry&&t.geometry.animations||t.animations}for(let e=0;e<n.length;e++)if(n[e].name===t)return n[e];return null}static CreateClipsFromMorphTargetSequences(e,t,n){let r={},i=/^([\w-]*?)([\d]+)$/;for(let t=0,n=e.length;t<n;t++){let n=e[t],a=n.name.match(i);if(a&&a.length>1){let e=a[1],t=r[e];t||(r[e]=t=[]),t.push(n)}}let a=[];for(let e in r)a.push(this.CreateFromMorphTargetSequence(e,r[e],t,n));return a}resetDuration(){let e=this.tracks,t=0;for(let n=0,r=e.length;n!==r;++n){let e=this.tracks[n];t=Math.max(t,e.times[e.times.length-1])}return this.duration=t,this}trim(){for(let e=0;e<this.tracks.length;e++)this.tracks[e].trim(0,this.duration);return this}validate(){let e=!0;for(let t=0;t<this.tracks.length;t++)e&&=this.tracks[t].validate();return e}optimize(){for(let e=0;e<this.tracks.length;e++)this.tracks[e].optimize();return this}clone(){let e=[];for(let t=0;t<this.tracks.length;t++)e.push(this.tracks[t].clone());let t=new this.constructor(this.name,this.duration,e,this.blendMode);return t.userData=JSON.parse(JSON.stringify(this.userData)),t}toJSON(){return this.constructor.toJSON(this)}};function ss(e){switch(e.toLowerCase()){case`scalar`:case`double`:case`float`:case`number`:case`integer`:return ts;case`vector`:case`vector2`:case`vector3`:case`vector4`:return as;case`color`:return es;case`quaternion`:return rs;case`bool`:case`boolean`:return $o;case`string`:return is}throw Error(`THREE.KeyframeTrack: Unsupported typeName: `+e)}function cs(e){if(e.type===void 0)throw Error(`THREE.KeyframeTrack: track type undefined, can not parse`);let t=ss(e.type);if(e.times===void 0){let t=[],n=[];Ko(e.keys,t,n,`value`),e.times=t,e.values=n}return t.parse===void 0?new t(e.name,e.times,e.values,e.interpolation):t.parse(e)}var ls={enabled:!1,files:{},add:function(e,t){this.enabled!==!1&&(us(e)||(this.files[e]=t))},get:function(e){if(this.enabled!==!1&&!us(e))return this.files[e]},remove:function(e){delete this.files[e]},clear:function(){this.files={}}};function us(e){try{let t=e.slice(e.indexOf(`:`)+1);return new URL(t).protocol===`blob:`}catch{return!1}}var ds=new class{constructor(e,t,n){let r=this,i=!1,a=0,o=0,s,c=[];this.onStart=void 0,this.onLoad=e,this.onProgress=t,this.onError=n,this._abortController=null,this.itemStart=function(e){o++,i===!1&&r.onStart!==void 0&&r.onStart(e,a,o),i=!0},this.itemEnd=function(e){a++,r.onProgress!==void 0&&r.onProgress(e,a,o),a===o&&(i=!1,r.onLoad!==void 0&&r.onLoad())},this.itemError=function(e){r.onError!==void 0&&r.onError(e)},this.resolveURL=function(e){return e=e.normalize(`NFC`),s?s(e):e},this.setURLModifier=function(e){return s=e,this},this.addHandler=function(e,t){return c.push(e,t),this},this.removeHandler=function(e){let t=c.indexOf(e);return t!==-1&&c.splice(t,2),this},this.getHandler=function(e){for(let t=0,n=c.length;t<n;t+=2){let n=c[t],r=c[t+1];if(n.global&&(n.lastIndex=0),n.test(e))return r}return null},this.abort=function(){return this.abortController.abort(),this._abortController=null,this}}get abortController(){return this._abortController||=new AbortController,this._abortController}},fs=class{constructor(e){this.manager=e===void 0?ds:e,this.crossOrigin=`anonymous`,this.withCredentials=!1,this.path=``,this.resourcePath=``,this.requestHeader={},typeof __THREE_DEVTOOLS__<`u`&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent(`observe`,{detail:this}))}load(){}loadAsync(e,t){let n=this;return new Promise(function(r,i){n.load(e,r,t,i)})}parse(){}setCrossOrigin(e){return this.crossOrigin=e,this}setWithCredentials(e){return this.withCredentials=e,this}setPath(e){return this.path=e,this}setResourcePath(e){return this.resourcePath=e,this}setRequestHeader(e){return this.requestHeader=e,this}abort(){return this}};fs.DEFAULT_MATERIAL_NAME=`__DEFAULT`;var ps={},ms=class extends Error{constructor(e,t){super(e),this.response=t}},hs=class extends fs{constructor(e){super(e),this.mimeType=``,this.responseType=``,this._abortController=new AbortController}load(e,t,n,r){e===void 0&&(e=``),this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);let i=ls.get(`file:${e}`);if(i!==void 0){this.manager.itemStart(e),setTimeout(()=>{t&&t(i),this.manager.itemEnd(e)},0);return}if(ps[e]!==void 0){ps[e].push({onLoad:t,onProgress:n,onError:r});return}ps[e]=[],ps[e].push({onLoad:t,onProgress:n,onError:r});let a=new Request(e,{headers:new Headers(this.requestHeader),credentials:this.withCredentials?`include`:`same-origin`,signal:typeof AbortSignal.any==`function`?AbortSignal.any([this._abortController.signal,this.manager.abortController.signal]):this._abortController.signal}),o=this.mimeType,s=this.responseType;fetch(a).then(t=>{if(t.status===200||t.status===0){if(t.status===0&&B(`FileLoader: HTTP Status 0 received.`),typeof ReadableStream>`u`||t.body===void 0||t.body.getReader===void 0)return t;let n=ps[e],r=t.body.getReader(),i=t.headers.get(`X-File-Size`)||t.headers.get(`Content-Length`),a=i?parseInt(i):0,o=a!==0,s=0,c=new ReadableStream({start(e){t();function t(){r.read().then(({done:r,value:i})=>{if(r)e.close();else{s+=i.byteLength;let r=new ProgressEvent(`progress`,{lengthComputable:o,loaded:s,total:a});for(let e=0,t=n.length;e<t;e++){let t=n[e];t.onProgress&&t.onProgress(r)}e.enqueue(i),t()}},t=>{e.error(t)})}}});return new Response(c)}throw new ms(`fetch for "${t.url}" responded with ${t.status}: ${t.statusText}`,t)}).then(e=>{switch(s){case`arraybuffer`:return e.arrayBuffer();case`blob`:return e.blob();case`document`:return e.text().then(e=>new DOMParser().parseFromString(e,o));case`json`:return e.json();default:if(o===``)return e.text();{let t=/charset="?([^;"\s]*)"?/i.exec(o),n=t&&t[1]?t[1].toLowerCase():void 0,r=new TextDecoder(n);return e.arrayBuffer().then(e=>r.decode(e))}}}).then(t=>{ls.add(`file:${e}`,t);let n=ps[e];delete ps[e];for(let e=0,r=n.length;e<r;e++){let r=n[e];r.onLoad&&r.onLoad(t)}}).catch(t=>{let n=ps[e];if(n===void 0)throw this.manager.itemError(e),t;delete ps[e];for(let e=0,r=n.length;e<r;e++){let r=n[e];r.onError&&r.onError(t)}this.manager.itemError(e)}).finally(()=>{this.manager.itemEnd(e)}),this.manager.itemStart(e)}setResponseType(e){return this.responseType=e,this}setMimeType(e){return this.mimeType=e,this}abort(){return this._abortController.abort(),this._abortController=new AbortController,this}},gs=new WeakMap,_s=class extends fs{constructor(e){super(e)}load(e,t,n,r){this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);let i=this,a=ls.get(`image:${e}`);if(a!==void 0){if(a.complete===!0)i.manager.itemStart(e),setTimeout(function(){t&&t(a),i.manager.itemEnd(e)},0);else{let e=gs.get(a);e===void 0&&(e=[],gs.set(a,e)),e.push({onLoad:t,onError:r})}return a}let o=Xe(`img`);function s(){l(),t&&t(this);let n=gs.get(this)||[];for(let e=0;e<n.length;e++){let t=n[e];t.onLoad&&t.onLoad(this)}gs.delete(this),i.manager.itemEnd(e)}function c(t){l(),r&&r(t),ls.remove(`image:${e}`);let n=gs.get(this)||[];for(let e=0;e<n.length;e++){let r=n[e];r.onError&&r.onError(t)}gs.delete(this),i.manager.itemError(e),i.manager.itemEnd(e)}function l(){o.removeEventListener(`load`,s,!1),o.removeEventListener(`error`,c,!1)}return o.addEventListener(`load`,s,!1),o.addEventListener(`error`,c,!1),e.slice(0,5)!==`data:`&&this.crossOrigin!==void 0&&(o.crossOrigin=this.crossOrigin),ls.add(`image:${e}`,o),i.manager.itemStart(e),o.src=e,o}},vs=class extends fs{constructor(e){super(e)}load(e,t,n,r){let i=new qt,a=new _s(this.manager);return a.setCrossOrigin(this.crossOrigin),a.setPath(this.path),a.load(e,function(e){i.image=e,i.needsUpdate=!0,t!==void 0&&t(i)},n,r),i}},ys=class extends En{constructor(e,t=1){super(),this.isLight=!0,this.type=`Light`,this.color=new J(e),this.intensity=t}dispose(){this.dispatchEvent({type:`dispose`})}copy(e,t){return super.copy(e,t),this.color.copy(e.color),this.intensity=e.intensity,this}toJSON(e){let t=super.toJSON(e);return t.object.color=this.color.getHex(),t.object.intensity=this.intensity,t}},bs=new q,xs=new W,Ss=new W,Cs=class{constructor(e){this.camera=e,this.intensity=1,this.bias=0,this.biasNode=null,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new U(512,512),this.mapType=f,this.map=null,this.mapPass=null,this.matrix=new q,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new Pi,this._frameExtents=new U(1,1),this._viewportCount=1,this._viewports=[new Jt(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(e){let t=this.camera,n=this.matrix;xs.setFromMatrixPosition(e.matrixWorld),t.position.copy(xs),Ss.setFromMatrixPosition(e.target.matrixWorld),t.lookAt(Ss),t.updateMatrixWorld(),bs.multiplyMatrices(t.projectionMatrix,t.matrixWorldInverse),this._frustum.setFromProjectionMatrix(bs,t.coordinateSystem,t.reversedDepth),t.coordinateSystem===2001||t.reversedDepth?n.set(.5,0,0,.5,0,.5,0,.5,0,0,1,0,0,0,0,1):n.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),n.multiply(bs)}getViewport(e){return this._viewports[e]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(e){return this.camera=e.camera.clone(),this.intensity=e.intensity,this.bias=e.bias,this.radius=e.radius,this.autoUpdate=e.autoUpdate,this.needsUpdate=e.needsUpdate,this.normalBias=e.normalBias,this.blurSamples=e.blurSamples,this.mapSize.copy(e.mapSize),this.biasNode=e.biasNode,this}clone(){return new this.constructor().copy(this)}toJSON(){let e={};return this.intensity!==1&&(e.intensity=this.intensity),this.bias!==0&&(e.bias=this.bias),this.normalBias!==0&&(e.normalBias=this.normalBias),this.radius!==1&&(e.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(e.mapSize=this.mapSize.toArray()),e.camera=this.camera.toJSON(!1).object,delete e.camera.matrix,e}},ws=new W,Ts=new jt,Es=new W,Ds=class extends En{constructor(){super(),this.isCamera=!0,this.type=`Camera`,this.matrixWorldInverse=new q,this.projectionMatrix=new q,this.projectionMatrixInverse=new q,this.coordinateSystem=R,this._reversedDepth=!1}get reversedDepth(){return this._reversedDepth}copy(e,t){return super.copy(e,t),this.matrixWorldInverse.copy(e.matrixWorldInverse),this.projectionMatrix.copy(e.projectionMatrix),this.projectionMatrixInverse.copy(e.projectionMatrixInverse),this.coordinateSystem=e.coordinateSystem,this}getWorldDirection(e){return super.getWorldDirection(e).negate()}updateMatrixWorld(e){super.updateMatrixWorld(e),this.matrixWorld.decompose(ws,Ts,Es),Es.x===1&&Es.y===1&&Es.z===1?this.matrixWorldInverse.copy(this.matrixWorld).invert():this.matrixWorldInverse.compose(ws,Ts,Es.set(1,1,1)).invert()}updateWorldMatrix(e,t,n=!1){super.updateWorldMatrix(e,t,n),this.matrixWorld.decompose(ws,Ts,Es),Es.x===1&&Es.y===1&&Es.z===1?this.matrixWorldInverse.copy(this.matrixWorld).invert():this.matrixWorldInverse.compose(ws,Ts,Es.set(1,1,1)).invert()}clone(){return new this.constructor().copy(this)}},Os=new W,ks=new U,As=new U,js=class extends Ds{constructor(e=50,t=1,n=.1,r=2e3){super(),this.isPerspectiveCamera=!0,this.type=`PerspectiveCamera`,this.fov=e,this.zoom=1,this.near=n,this.far=r,this.focus=10,this.aspect=t,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.fov=e.fov,this.zoom=e.zoom,this.near=e.near,this.far=e.far,this.focus=e.focus,this.aspect=e.aspect,this.view=e.view===null?null:Object.assign({},e.view),this.filmGauge=e.filmGauge,this.filmOffset=e.filmOffset,this}setFocalLength(e){let t=.5*this.getFilmHeight()/e;this.fov=ct*2*Math.atan(t),this.updateProjectionMatrix()}getFocalLength(){let e=Math.tan(st*.5*this.fov);return .5*this.getFilmHeight()/e}getEffectiveFOV(){return ct*2*Math.atan(Math.tan(st*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(e,t,n){Os.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),t.set(Os.x,Os.y).multiplyScalar(-e/Os.z),Os.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),n.set(Os.x,Os.y).multiplyScalar(-e/Os.z)}getViewSize(e,t){return this.getViewBounds(e,ks,As),t.subVectors(As,ks)}setViewOffset(e,t,n,r,i,a){this.aspect=e/t,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=r,this.view.width=i,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){let e=this.near,t=e*Math.tan(st*.5*this.fov)/this.zoom,n=2*t,r=this.aspect*n,i=-.5*r,a=this.view;if(this.view!==null&&this.view.enabled){let e=a.fullWidth,o=a.fullHeight;i+=a.offsetX*r/e,t-=a.offsetY*n/o,r*=a.width/e,n*=a.height/o}let o=this.filmOffset;o!==0&&(i+=e*o/this.getFilmWidth()),this.projectionMatrix.makePerspective(i,i+r,t,t-n,e,this.far,this.coordinateSystem,this.reversedDepth),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){let t=super.toJSON(e);return t.object.fov=this.fov,t.object.zoom=this.zoom,t.object.near=this.near,t.object.far=this.far,t.object.focus=this.focus,t.object.aspect=this.aspect,this.view!==null&&(t.object.view=Object.assign({},this.view)),t.object.filmGauge=this.filmGauge,t.object.filmOffset=this.filmOffset,t}},Ms=class extends Cs{constructor(){super(new js(50,1,.5,500)),this.isSpotLightShadow=!0,this.focus=1,this.aspect=1}updateMatrices(e){let t=this.camera,n=ct*2*e.angle*this.focus,r=this.mapSize.width/this.mapSize.height*this.aspect,i=e.distance||t.far;(n!==t.fov||r!==t.aspect||i!==t.far)&&(t.fov=n,t.aspect=r,t.far=i,t.updateProjectionMatrix()),super.updateMatrices(e)}copy(e){return super.copy(e),this.focus=e.focus,this}},Ns=class extends ys{constructor(e,t,n=0,r=Math.PI/3,i=0,a=2){super(e,t),this.isSpotLight=!0,this.type=`SpotLight`,this.position.copy(En.DEFAULT_UP),this.updateMatrix(),this.target=new En,this.distance=n,this.angle=r,this.penumbra=i,this.decay=a,this.map=null,this.shadow=new Ms}get power(){return this.intensity*Math.PI}set power(e){this.intensity=e/Math.PI}dispose(){super.dispose(),this.shadow.dispose()}copy(e,t){return super.copy(e,t),this.distance=e.distance,this.angle=e.angle,this.penumbra=e.penumbra,this.decay=e.decay,this.target=e.target.clone(),this.map=e.map,this.shadow=e.shadow.clone(),this}toJSON(e){let t=super.toJSON(e);return t.object.distance=this.distance,t.object.angle=this.angle,t.object.decay=this.decay,t.object.penumbra=this.penumbra,t.object.target=this.target.uuid,this.map&&this.map.isTexture&&(t.object.map=this.map.toJSON(e).uuid),t.object.shadow=this.shadow.toJSON(),t}},Ps=class extends Cs{constructor(){super(new js(90,1,.5,500)),this.isPointLightShadow=!0}},Fs=class extends ys{constructor(e,t,n=0,r=2){super(e,t),this.isPointLight=!0,this.type=`PointLight`,this.distance=n,this.decay=r,this.shadow=new Ps}get power(){return this.intensity*4*Math.PI}set power(e){this.intensity=e/(4*Math.PI)}dispose(){super.dispose(),this.shadow.dispose()}copy(e,t){return super.copy(e,t),this.distance=e.distance,this.decay=e.decay,this.shadow=e.shadow.clone(),this}toJSON(e){let t=super.toJSON(e);return t.object.distance=this.distance,t.object.decay=this.decay,t.object.shadow=this.shadow.toJSON(),t}},Is=class extends Ds{constructor(e=-1,t=1,n=1,r=-1,i=.1,a=2e3){super(),this.isOrthographicCamera=!0,this.type=`OrthographicCamera`,this.zoom=1,this.view=null,this.left=e,this.right=t,this.top=n,this.bottom=r,this.near=i,this.far=a,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.left=e.left,this.right=e.right,this.top=e.top,this.bottom=e.bottom,this.near=e.near,this.far=e.far,this.zoom=e.zoom,this.view=e.view===null?null:Object.assign({},e.view),this}setViewOffset(e,t,n,r,i,a){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=r,this.view.width=i,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){let e=(this.right-this.left)/(2*this.zoom),t=(this.top-this.bottom)/(2*this.zoom),n=(this.right+this.left)/2,r=(this.top+this.bottom)/2,i=n-e,a=n+e,o=r+t,s=r-t;if(this.view!==null&&this.view.enabled){let e=(this.right-this.left)/this.view.fullWidth/this.zoom,t=(this.top-this.bottom)/this.view.fullHeight/this.zoom;i+=e*this.view.offsetX,a=i+e*this.view.width,o-=t*this.view.offsetY,s=o-t*this.view.height}this.projectionMatrix.makeOrthographic(i,a,o,s,this.near,this.far,this.coordinateSystem,this.reversedDepth),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){let t=super.toJSON(e);return t.object.zoom=this.zoom,t.object.left=this.left,t.object.right=this.right,t.object.top=this.top,t.object.bottom=this.bottom,t.object.near=this.near,t.object.far=this.far,this.view!==null&&(t.object.view=Object.assign({},this.view)),t}},Ls=class extends Cs{constructor(){super(new Is(-5,5,5,-5,.5,500)),this.isDirectionalLightShadow=!0}},Rs=class extends ys{constructor(e,t){super(e,t),this.isDirectionalLight=!0,this.type=`DirectionalLight`,this.position.copy(En.DEFAULT_UP),this.updateMatrix(),this.target=new En,this.shadow=new Ls}dispose(){super.dispose(),this.shadow.dispose()}copy(e){return super.copy(e),this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}toJSON(e){let t=super.toJSON(e);return t.object.shadow=this.shadow.toJSON(),t.object.target=this.target.uuid,t}},zs=class{static extractUrlBase(e){let t=e.lastIndexOf(`/`);return t===-1?`./`:e.slice(0,t+1)}static resolveURL(e,t){return typeof e!=`string`||e===``?``:(/^https?:\/\//i.test(t)&&/^\//.test(e)&&(t=t.replace(/(^https?:\/\/[^\/]+).*/i,`$1`)),/^(https?:)?\/\//i.test(e)||/^data:.*,.*$/i.test(e)||/^blob:.*$/i.test(e)?e:t+e)}},Bs=new WeakMap,Vs=class extends fs{constructor(e){super(e),this.isImageBitmapLoader=!0,typeof createImageBitmap>`u`&&B(`ImageBitmapLoader: createImageBitmap() not supported.`),typeof fetch>`u`&&B(`ImageBitmapLoader: fetch() not supported.`),this.options={premultiplyAlpha:`none`},this._abortController=new AbortController}setOptions(e){return this.options=e,this}load(e,t,n,r){e===void 0&&(e=``),this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);let i=this,a=ls.get(`image-bitmap:${e}`);if(a!==void 0){if(i.manager.itemStart(e),a.then){a.then(n=>{Bs.has(a)===!0?(r&&r(Bs.get(a)),i.manager.itemError(e),i.manager.itemEnd(e)):(t&&t(n),i.manager.itemEnd(e))});return}setTimeout(function(){t&&t(a),i.manager.itemEnd(e)},0);return}let o={};o.credentials=this.crossOrigin===`anonymous`?`same-origin`:`include`,o.headers=this.requestHeader,o.signal=typeof AbortSignal.any==`function`?AbortSignal.any([this._abortController.signal,this.manager.abortController.signal]):this._abortController.signal;let s=fetch(e,o).then(function(e){return e.blob()}).then(function(e){return createImageBitmap(e,Object.assign(i.options,{colorSpaceConversion:`none`}))}).then(function(n){ls.add(`image-bitmap:${e}`,n),t&&t(n),i.manager.itemEnd(e)}).catch(function(t){r&&r(t),Bs.set(s,t),ls.remove(`image-bitmap:${e}`),i.manager.itemError(e),i.manager.itemEnd(e)});ls.add(`image-bitmap:${e}`,s),i.manager.itemStart(e)}abort(){return this._abortController.abort(),this._abortController=new AbortController,this}},Hs=-90,Us=1,Ws=class extends En{constructor(e,t,n){super(),this.type=`CubeCamera`,this.renderTarget=n,this.coordinateSystem=null,this.activeMipmapLevel=0;let r=new js(Hs,Us,e,t);r.layers=this.layers,this.add(r);let i=new js(Hs,Us,e,t);i.layers=this.layers,this.add(i);let a=new js(Hs,Us,e,t);a.layers=this.layers,this.add(a);let o=new js(Hs,Us,e,t);o.layers=this.layers,this.add(o);let s=new js(Hs,Us,e,t);s.layers=this.layers,this.add(s);let c=new js(Hs,Us,e,t);c.layers=this.layers,this.add(c)}updateCoordinateSystem(){let e=this.coordinateSystem,t=this.children.concat(),[n,r,i,a,o,s]=t;for(let e of t)this.remove(e);if(e===2e3)n.up.set(0,1,0),n.lookAt(1,0,0),r.up.set(0,1,0),r.lookAt(-1,0,0),i.up.set(0,0,-1),i.lookAt(0,1,0),a.up.set(0,0,1),a.lookAt(0,-1,0),o.up.set(0,1,0),o.lookAt(0,0,1),s.up.set(0,1,0),s.lookAt(0,0,-1);else if(e===2001)n.up.set(0,-1,0),n.lookAt(-1,0,0),r.up.set(0,-1,0),r.lookAt(1,0,0),i.up.set(0,0,1),i.lookAt(0,1,0),a.up.set(0,0,-1),a.lookAt(0,-1,0),o.up.set(0,-1,0),o.lookAt(0,0,1),s.up.set(0,-1,0),s.lookAt(0,0,-1);else throw Error(`THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: `+e);for(let e of t)this.add(e),e.updateMatrixWorld()}update(e,t){this.parent===null&&this.updateMatrixWorld();let{renderTarget:n,activeMipmapLevel:r}=this;this.coordinateSystem!==e.coordinateSystem&&(this.coordinateSystem=e.coordinateSystem,this.updateCoordinateSystem());let[i,a,o,s,c,l]=this.children,u=e.getRenderTarget(),d=e.getActiveCubeFace(),f=e.getActiveMipmapLevel(),p=e.xr.enabled;e.xr.enabled=!1;let m=n.texture.generateMipmaps;n.texture.generateMipmaps=!1;let h=!1;h=e.isWebGLRenderer===!0?e.state.buffers.depth.getReversed():e.reversedDepthBuffer,e.setRenderTarget(n,0,r),h&&e.autoClear===!1&&e.clearDepth(),e.render(t,i),e.setRenderTarget(n,1,r),h&&e.autoClear===!1&&e.clearDepth(),e.render(t,a),e.setRenderTarget(n,2,r),h&&e.autoClear===!1&&e.clearDepth(),e.render(t,o),e.setRenderTarget(n,3,r),h&&e.autoClear===!1&&e.clearDepth(),e.render(t,s),e.setRenderTarget(n,4,r),h&&e.autoClear===!1&&e.clearDepth(),e.render(t,c),n.texture.generateMipmaps=m,e.setRenderTarget(n,5,r),h&&e.autoClear===!1&&e.clearDepth(),e.render(t,l),e.setRenderTarget(u,d,f),e.xr.enabled=p,n.texture.needsPMREMUpdate=!0}},Gs=class extends js{constructor(e=[]){super(),this.isArrayCamera=!0,this.isMultiViewCamera=!1,this.cameras=e}},Ks=`\\[\\]\\.:\\/`,qs=RegExp(`[\\[\\]\\.:\\/]`,`g`),Js=`[^\\[\\]\\.:\\/]`,Ys=`[^`+Ks.replace(`\\.`,``)+`]`,Xs=`((?:WC+[\\/:])*)`.replace(`WC`,Js),Zs=`(WCOD+)?`.replace(`WCOD`,Ys),Qs=`(?:\\.(WC+)(?:\\[(.+)\\])?)?`.replace(`WC`,Js),$s=`\\.(WC+)(?:\\[(.+)\\])?`.replace(`WC`,Js),ec=RegExp(`^`+Xs+Zs+Qs+$s+`$`),tc=[`material`,`materials`,`bones`,`map`],nc=class{constructor(e,t,n){let r=n||rc.parseTrackName(t);this._targetGroup=e,this._bindings=e.subscribe_(t,r)}getValue(e,t){this.bind();let n=this._targetGroup.nCachedObjects_,r=this._bindings[n];r!==void 0&&r.getValue(e,t)}setValue(e,t){let n=this._bindings;for(let r=this._targetGroup.nCachedObjects_,i=n.length;r!==i;++r)n[r].setValue(e,t)}bind(){let e=this._bindings;for(let t=this._targetGroup.nCachedObjects_,n=e.length;t!==n;++t)e[t].bind()}unbind(){let e=this._bindings;for(let t=this._targetGroup.nCachedObjects_,n=e.length;t!==n;++t)e[t].unbind()}},rc=class e{constructor(t,n,r){this.path=n,this.parsedPath=r||e.parseTrackName(n),this.node=e.findNode(t,this.parsedPath.nodeName),this.rootNode=t,this.getValue=this._getValue_unbound,this.setValue=this._setValue_unbound}static create(t,n,r){return t&&t.isAnimationObjectGroup?new e.Composite(t,n,r):new e(t,n,r)}static sanitizeNodeName(e){return e.replace(/\s/g,`_`).replace(qs,``)}static parseTrackName(e){let t=ec.exec(e);if(t===null)throw Error(`THREE.PropertyBinding: Cannot parse trackName: `+e);let n={nodeName:t[2],objectName:t[3],objectIndex:t[4],propertyName:t[5],propertyIndex:t[6]},r=n.nodeName&&n.nodeName.lastIndexOf(`.`);if(r!==void 0&&r!==-1){let e=n.nodeName.substring(r+1);tc.indexOf(e)!==-1&&(n.nodeName=n.nodeName.substring(0,r),n.objectName=e)}if(n.propertyName===null||n.propertyName.length===0)throw Error(`THREE.PropertyBinding: can not parse propertyName from trackName: `+e);return n}static findNode(e,t){if(t===void 0||t===``||t===`.`||t===-1||t===e.name||t===e.uuid)return e;if(e.skeleton){let n=e.skeleton.getBoneByName(t);if(n!==void 0)return n}if(e.children){let n=function(e){for(let r=0;r<e.length;r++){let i=e[r];if(i.name===t||i.uuid===t)return i;let a=n(i.children);if(a)return a}return null},r=n(e.children);if(r)return r}return null}_getValue_unavailable(){}_setValue_unavailable(){}_getValue_direct(e,t){e[t]=this.targetObject[this.propertyName]}_getValue_array(e,t){let n=this.resolvedProperty;for(let r=0,i=n.length;r!==i;++r)e[t++]=n[r]}_getValue_arrayElement(e,t){e[t]=this.resolvedProperty[this.propertyIndex]}_getValue_toArray(e,t){this.resolvedProperty.toArray(e,t)}_setValue_direct(e,t){this.targetObject[this.propertyName]=e[t]}_setValue_direct_setNeedsUpdate(e,t){this.targetObject[this.propertyName]=e[t],this.targetObject.needsUpdate=!0}_setValue_direct_setMatrixWorldNeedsUpdate(e,t){this.targetObject[this.propertyName]=e[t],this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_array(e,t){let n=this.resolvedProperty;for(let r=0,i=n.length;r!==i;++r)n[r]=e[t++]}_setValue_array_setNeedsUpdate(e,t){let n=this.resolvedProperty;for(let r=0,i=n.length;r!==i;++r)n[r]=e[t++];this.targetObject.needsUpdate=!0}_setValue_array_setMatrixWorldNeedsUpdate(e,t){let n=this.resolvedProperty;for(let r=0,i=n.length;r!==i;++r)n[r]=e[t++];this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_arrayElement(e,t){this.resolvedProperty[this.propertyIndex]=e[t]}_setValue_arrayElement_setNeedsUpdate(e,t){this.resolvedProperty[this.propertyIndex]=e[t],this.targetObject.needsUpdate=!0}_setValue_arrayElement_setMatrixWorldNeedsUpdate(e,t){this.resolvedProperty[this.propertyIndex]=e[t],this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_fromArray(e,t){this.resolvedProperty.fromArray(e,t)}_setValue_fromArray_setNeedsUpdate(e,t){this.resolvedProperty.fromArray(e,t),this.targetObject.needsUpdate=!0}_setValue_fromArray_setMatrixWorldNeedsUpdate(e,t){this.resolvedProperty.fromArray(e,t),this.targetObject.matrixWorldNeedsUpdate=!0}_getValue_unbound(e,t){this.bind(),this.getValue(e,t)}_setValue_unbound(e,t){this.bind(),this.setValue(e,t)}bind(){let t=this.node,n=this.parsedPath,r=n.objectName,i=n.propertyName,a=n.propertyIndex;if(t||(t=e.findNode(this.rootNode,n.nodeName),this.node=t),this.getValue=this._getValue_unavailable,this.setValue=this._setValue_unavailable,!t){B(`PropertyBinding: No target node found for track: `+this.path+`.`);return}if(r){let e=n.objectIndex;switch(r){case`materials`:if(!t.material){V(`PropertyBinding: Can not bind to material as node does not have a material.`,this);return}if(!t.material.materials){V(`PropertyBinding: Can not bind to material.materials as node.material does not have a materials array.`,this);return}t=t.material.materials;break;case`bones`:if(!t.skeleton){V(`PropertyBinding: Can not bind to bones as node does not have a skeleton.`,this);return}t=t.skeleton.bones;for(let n=0;n<t.length;n++)if(t[n].name===e){e=n;break}break;case`map`:if(`map`in t){t=t.map;break}if(!t.material){V(`PropertyBinding: Can not bind to material as node does not have a material.`,this);return}if(!t.material.map){V(`PropertyBinding: Can not bind to material.map as node.material does not have a map.`,this);return}t=t.material.map;break;default:if(t[r]===void 0){V(`PropertyBinding: Can not bind to objectName of node undefined.`,this);return}t=t[r]}if(e!==void 0){if(t[e]===void 0){V(`PropertyBinding: Trying to bind to objectIndex of objectName, but is undefined.`,this,t);return}t=t[e]}}let o=t[i];if(o===void 0){let e=n.nodeName;V(`PropertyBinding: Trying to update property for track: `+e+`.`+i+` but it wasn't found.`,t);return}let s=this.Versioning.None;this.targetObject=t,t.isMaterial===!0?s=this.Versioning.NeedsUpdate:t.isObject3D===!0&&(s=this.Versioning.MatrixWorldNeedsUpdate);let c=this.BindingType.Direct;if(a!==void 0){if(i===`morphTargetInfluences`){if(!t.geometry){V(`PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.`,this);return}if(!t.geometry.morphAttributes){V(`PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.morphAttributes.`,this);return}t.morphTargetDictionary[a]!==void 0&&(a=t.morphTargetDictionary[a])}c=this.BindingType.ArrayElement,this.resolvedProperty=o,this.propertyIndex=a}else o.fromArray!==void 0&&o.toArray!==void 0?(c=this.BindingType.HasFromToArray,this.resolvedProperty=o):Array.isArray(o)?(c=this.BindingType.EntireArray,this.resolvedProperty=o):this.propertyName=i;this.getValue=this.GetterByBindingType[c],this.setValue=this.SetterByBindingTypeAndVersioning[c][s]}unbind(){this.node=null,this.getValue=this._getValue_unbound,this.setValue=this._setValue_unbound}};rc.Composite=nc,rc.prototype.BindingType={Direct:0,EntireArray:1,ArrayElement:2,HasFromToArray:3},rc.prototype.Versioning={None:0,NeedsUpdate:1,MatrixWorldNeedsUpdate:2},rc.prototype.GetterByBindingType=[rc.prototype._getValue_direct,rc.prototype._getValue_array,rc.prototype._getValue_arrayElement,rc.prototype._getValue_toArray],rc.prototype.SetterByBindingTypeAndVersioning=[[rc.prototype._setValue_direct,rc.prototype._setValue_direct_setNeedsUpdate,rc.prototype._setValue_direct_setMatrixWorldNeedsUpdate],[rc.prototype._setValue_array,rc.prototype._setValue_array_setNeedsUpdate,rc.prototype._setValue_array_setMatrixWorldNeedsUpdate],[rc.prototype._setValue_arrayElement,rc.prototype._setValue_arrayElement_setNeedsUpdate,rc.prototype._setValue_arrayElement_setMatrixWorldNeedsUpdate],[rc.prototype._setValue_fromArray,rc.prototype._setValue_fromArray_setNeedsUpdate,rc.prototype._setValue_fromArray_setMatrixWorldNeedsUpdate]];var ic=new q,ac=class{constructor(e,t,n=0,r=1/0){this.ray=new Vr(e,t),this.near=n,this.far=r,this.camera=null,this.layers=new un,this.params={Mesh:{},Line:{threshold:1},LOD:{},Points:{threshold:1},Sprite:{}}}set(e,t){this.ray.set(e,t)}setFromCamera(e,t){t.isPerspectiveCamera?(this.ray.origin.setFromMatrixPosition(t.matrixWorld),this.ray.direction.set(e.x,e.y,.5).unproject(t).sub(this.ray.origin).normalize(),this.camera=t):t.isOrthographicCamera?(this.ray.origin.set(e.x,e.y,t.projectionMatrix.elements[14]).unproject(t),this.ray.direction.set(0,0,-1).transformDirection(t.matrixWorld),this.camera=t):V(`Raycaster: Unsupported camera type: `+t.type)}setFromXRController(e){return ic.identity().extractRotation(e.matrixWorld),this.ray.origin.setFromMatrixPosition(e.matrixWorld),this.ray.direction.set(0,0,-1).applyMatrix4(ic),this}intersectObject(e,t=!0,n=[]){return sc(e,this,n,t),n.sort(oc),n}intersectObjects(e,t=!0,n=[]){for(let r=0,i=e.length;r<i;r++)sc(e[r],this,n,t);return n.sort(oc),n}};function oc(e,t){return e.distance-t.distance}function sc(e,t,n,r){let i=!0;if(e.layers.test(t.layers)&&e.raycast(t,n)===!1&&(i=!1),i===!0&&r===!0){let r=e.children;for(let e=0,i=r.length;e<i;e++)sc(r[e],t,n,!0)}}var cc=class{constructor(e=1,t=0,n=0){this.radius=e,this.phi=t,this.theta=n}set(e,t,n){return this.radius=e,this.phi=t,this.theta=n,this}copy(e){return this.radius=e.radius,this.phi=e.phi,this.theta=e.theta,this}makeSafe(){let e=1e-6;return this.phi=H(this.phi,e,Math.PI-e),this}setFromVector3(e){return this.setFromCartesianCoords(e.x,e.y,e.z)}setFromCartesianCoords(e,t,n){return this.radius=Math.sqrt(e*e+t*t+n*n),this.radius===0?(this.theta=0,this.phi=0):(this.theta=Math.atan2(e,n),this.phi=Math.acos(H(t/this.radius,-1,1))),this}clone(){return new this.constructor().copy(this)}};(class e{static{e.prototype.isMatrix2=!0}constructor(e,t,n,r){this.elements=[1,0,0,1],e!==void 0&&this.set(e,t,n,r)}identity(){return this.set(1,0,0,1),this}fromArray(e,t=0){for(let n=0;n<4;n++)this.elements[n]=e[n+t];return this}set(e,t,n,r){let i=this.elements;return i[0]=e,i[2]=t,i[1]=n,i[3]=r,this}});var lc=class extends it{constructor(e,t=null){super(),this.object=e,this.domElement=t,this.enabled=!0,this.state=-1,this.keys={},this.mouseButtons={LEFT:null,MIDDLE:null,RIGHT:null},this.touches={ONE:null,TWO:null}}connect(e){if(e===void 0){B(`Controls: connect() now requires an element.`);return}this.domElement!==null&&this.disconnect(),this.domElement=e}disconnect(){}dispose(){}update(){}};function uc(e,t,n,r){let i=dc(r);switch(n){case T:return e*t;case A:return e*t/i.components*i.byteLength;case ee:return e*t/i.components*i.byteLength;case te:return e*t*2/i.components*i.byteLength;case j:return e*t*2/i.components*i.byteLength;case E:return e*t*3/i.components*i.byteLength;case D:return e*t*4/i.components*i.byteLength;case ne:return e*t*4/i.components*i.byteLength;case M:case N:return Math.floor((e+3)/4)*Math.floor((t+3)/4)*8;case re:case ie:return Math.floor((e+3)/4)*Math.floor((t+3)/4)*16;case oe:case ce:return Math.max(e,16)*Math.max(t,8)/4;case ae:case se:return Math.max(e,8)*Math.max(t,8)/2;case le:case P:case de:case fe:return Math.floor((e+3)/4)*Math.floor((t+3)/4)*8;case ue:case pe:case me:return Math.floor((e+3)/4)*Math.floor((t+3)/4)*16;case F:return Math.floor((e+3)/4)*Math.floor((t+3)/4)*16;case he:return Math.floor((e+4)/5)*Math.floor((t+3)/4)*16;case ge:return Math.floor((e+4)/5)*Math.floor((t+4)/5)*16;case _e:return Math.floor((e+5)/6)*Math.floor((t+4)/5)*16;case ve:return Math.floor((e+5)/6)*Math.floor((t+5)/6)*16;case ye:return Math.floor((e+7)/8)*Math.floor((t+4)/5)*16;case be:return Math.floor((e+7)/8)*Math.floor((t+5)/6)*16;case xe:return Math.floor((e+7)/8)*Math.floor((t+7)/8)*16;case Se:return Math.floor((e+9)/10)*Math.floor((t+4)/5)*16;case Ce:return Math.floor((e+9)/10)*Math.floor((t+5)/6)*16;case we:return Math.floor((e+9)/10)*Math.floor((t+7)/8)*16;case Te:return Math.floor((e+9)/10)*Math.floor((t+9)/10)*16;case Ee:return Math.floor((e+11)/12)*Math.floor((t+9)/10)*16;case De:return Math.floor((e+11)/12)*Math.floor((t+11)/12)*16;case Oe:case ke:case Ae:return Math.ceil(e/4)*Math.ceil(t/4)*16;case je:case Me:return Math.ceil(e/4)*Math.ceil(t/4)*8;case I:case Ne:return Math.ceil(e/4)*Math.ceil(t/4)*16}throw Error(`Unable to determine texture byte length for ${n} format.`)}function dc(e){switch(e){case f:case p:return{byteLength:1,components:1};case h:case m:case y:return{byteLength:2,components:1};case b:case x:return{byteLength:2,components:4};case _:case g:case v:return{byteLength:4,components:1};case C:case w:return{byteLength:4,components:3}}throw Error(`THREE.TextureUtils: Unknown texture type ${e}.`)}typeof __THREE_DEVTOOLS__<`u`&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent(`register`,{detail:{revision:`185`}})),typeof window<`u`&&(window.__THREE__?B(`WARNING: Multiple instances of Three.js being imported.`):window.__THREE__=`185`);function fc(){let e=null,t=!1,n=null,r=null;function i(t,a){n(t,a),r=e.requestAnimationFrame(i)}return{start:function(){t!==!0&&n!==null&&e!==null&&(r=e.requestAnimationFrame(i),t=!0)},stop:function(){e!==null&&e.cancelAnimationFrame(r),t=!1},setAnimationLoop:function(e){n=e},setContext:function(t){e=t}}}function pc(e){let t=new WeakMap;function n(t,n){let r=t.array,i=t.usage,a=r.byteLength,o=e.createBuffer();e.bindBuffer(n,o),e.bufferData(n,r,i),t.onUploadCallback();let s;if(r instanceof Float32Array)s=e.FLOAT;else if(typeof Float16Array<`u`&&r instanceof Float16Array)s=e.HALF_FLOAT;else if(r instanceof Uint16Array)s=t.isFloat16BufferAttribute?e.HALF_FLOAT:e.UNSIGNED_SHORT;else if(r instanceof Int16Array)s=e.SHORT;else if(r instanceof Uint32Array)s=e.UNSIGNED_INT;else if(r instanceof Int32Array)s=e.INT;else if(r instanceof Int8Array)s=e.BYTE;else if(r instanceof Uint8Array)s=e.UNSIGNED_BYTE;else if(r instanceof Uint8ClampedArray)s=e.UNSIGNED_BYTE;else throw Error(`THREE.WebGLAttributes: Unsupported buffer data format: `+r);return{buffer:o,type:s,bytesPerElement:r.BYTES_PER_ELEMENT,version:t.version,size:a}}function r(t,n,r){let i=n.array,a=n.updateRanges;if(e.bindBuffer(r,t),a.length===0)e.bufferSubData(r,0,i);else{a.sort((e,t)=>e.start-t.start);let t=0;for(let e=1;e<a.length;e++){let n=a[t],r=a[e];r.start<=n.start+n.count+1?n.count=Math.max(n.count,r.start+r.count-n.start):(++t,a[t]=r)}a.length=t+1;for(let t=0,n=a.length;t<n;t++){let n=a[t];e.bufferSubData(r,n.start*i.BYTES_PER_ELEMENT,i,n.start,n.count)}n.clearUpdateRanges()}n.onUploadCallback()}function i(e){return e.isInterleavedBufferAttribute&&(e=e.data),t.get(e)}function a(n){n.isInterleavedBufferAttribute&&(n=n.data);let r=t.get(n);r&&(e.deleteBuffer(r.buffer),t.delete(n))}function o(e,i){if(e.isInterleavedBufferAttribute&&(e=e.data),e.isGLBufferAttribute){let n=t.get(e);(!n||n.version<e.version)&&t.set(e,{buffer:e.buffer,type:e.type,bytesPerElement:e.elementSize,version:e.version});return}let a=t.get(e);if(a===void 0)t.set(e,n(e,i));else if(a.version<e.version){if(a.size!==e.array.byteLength)throw Error(`THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.`);r(a.buffer,e,i),a.version=e.version}}return{get:i,remove:a,update:o}}var mc={alphahash_fragment:`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,alphahash_pars_fragment:`#ifdef USE_ALPHAHASH
	const float ALPHA_HASH_SCALE = 0.05;
	float hash2D( vec2 value ) {
		return fract( 1.0e4 * sin( 17.0 * value.x + 0.1 * value.y ) * ( 0.1 + abs( sin( 13.0 * value.y + value.x ) ) ) );
	}
	float hash3D( vec3 value ) {
		return hash2D( vec2( hash2D( value.xy ), value.z ) );
	}
	float getAlphaHashThreshold( vec3 position ) {
		float maxDeriv = max(
			length( dFdx( position.xyz ) ),
			length( dFdy( position.xyz ) )
		);
		float pixScale = 1.0 / ( ALPHA_HASH_SCALE * maxDeriv );
		vec2 pixScales = vec2(
			exp2( floor( log2( pixScale ) ) ),
			exp2( ceil( log2( pixScale ) ) )
		);
		vec2 alpha = vec2(
			hash3D( floor( pixScales.x * position.xyz ) ),
			hash3D( floor( pixScales.y * position.xyz ) )
		);
		float lerpFactor = fract( log2( pixScale ) );
		float x = ( 1.0 - lerpFactor ) * alpha.x + lerpFactor * alpha.y;
		float a = min( lerpFactor, 1.0 - lerpFactor );
		vec3 cases = vec3(
			x * x / ( 2.0 * a * ( 1.0 - a ) ),
			( x - 0.5 * a ) / ( 1.0 - a ),
			1.0 - ( ( 1.0 - x ) * ( 1.0 - x ) / ( 2.0 * a * ( 1.0 - a ) ) )
		);
		float threshold = ( x < ( 1.0 - a ) )
			? ( ( x < a ) ? cases.x : cases.y )
			: cases.z;
		return clamp( threshold , 1.0e-6, 1.0 );
	}
#endif`,alphamap_fragment:`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,alphamap_pars_fragment:`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,alphatest_fragment:`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,alphatest_pars_fragment:`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,aomap_fragment:`#ifdef USE_AOMAP
	float ambientOcclusion = ( texture2D( aoMap, vAoMapUv ).r - 1.0 ) * aoMapIntensity + 1.0;
	reflectedLight.indirectDiffuse *= ambientOcclusion;
	#if defined( USE_CLEARCOAT ) 
		clearcoatSpecularIndirect *= ambientOcclusion;
	#endif
	#if defined( USE_SHEEN ) 
		sheenSpecularIndirect *= ambientOcclusion;
	#endif
	#if defined( USE_ENVMAP ) && defined( STANDARD )
		float dotNV = saturate( dot( geometryNormal, geometryViewDir ) );
		reflectedLight.indirectSpecular *= computeSpecularOcclusion( dotNV, ambientOcclusion, material.roughness );
	#endif
#endif`,aomap_pars_fragment:`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,batching_pars_vertex:`#ifdef USE_BATCHING
	#if ! defined( GL_ANGLE_multi_draw )
	#define gl_DrawID _gl_DrawID
	uniform int _gl_DrawID;
	#endif
	uniform highp sampler2D batchingTexture;
	uniform highp usampler2D batchingIdTexture;
	mat4 getBatchingMatrix( const in float i ) {
		int size = textureSize( batchingTexture, 0 ).x;
		int j = int( i ) * 4;
		int x = j % size;
		int y = j / size;
		vec4 v1 = texelFetch( batchingTexture, ivec2( x, y ), 0 );
		vec4 v2 = texelFetch( batchingTexture, ivec2( x + 1, y ), 0 );
		vec4 v3 = texelFetch( batchingTexture, ivec2( x + 2, y ), 0 );
		vec4 v4 = texelFetch( batchingTexture, ivec2( x + 3, y ), 0 );
		return mat4( v1, v2, v3, v4 );
	}
	float getIndirectIndex( const in int i ) {
		int size = textureSize( batchingIdTexture, 0 ).x;
		int x = i % size;
		int y = i / size;
		return float( texelFetch( batchingIdTexture, ivec2( x, y ), 0 ).r );
	}
#endif
#ifdef USE_BATCHING_COLOR
	uniform sampler2D batchingColorTexture;
	vec4 getBatchingColor( const in float i ) {
		int size = textureSize( batchingColorTexture, 0 ).x;
		int j = int( i );
		int x = j % size;
		int y = j / size;
		return texelFetch( batchingColorTexture, ivec2( x, y ), 0 );
	}
#endif`,batching_vertex:`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,begin_vertex:`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,beginnormal_vertex:`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,bsdfs:`float G_BlinnPhong_Implicit( ) {
	return 0.25;
}
float D_BlinnPhong( const in float shininess, const in float dotNH ) {
	return RECIPROCAL_PI * ( shininess * 0.5 + 1.0 ) * pow( dotNH, shininess );
}
vec3 BRDF_BlinnPhong( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in vec3 specularColor, const in float shininess ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( specularColor, 1.0, dotVH );
	float G = G_BlinnPhong_Implicit( );
	float D = D_BlinnPhong( shininess, dotNH );
	return F * ( G * D );
} // validated`,iridescence_fragment:`#ifdef USE_IRIDESCENCE
	const mat3 XYZ_TO_REC709 = mat3(
		 3.2404542, -0.9692660,  0.0556434,
		-1.5371385,  1.8760108, -0.2040259,
		-0.4985314,  0.0415560,  1.0572252
	);
	vec3 Fresnel0ToIor( vec3 fresnel0 ) {
		vec3 sqrtF0 = sqrt( fresnel0 );
		return ( vec3( 1.0 ) + sqrtF0 ) / ( vec3( 1.0 ) - sqrtF0 );
	}
	vec3 IorToFresnel0( vec3 transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - vec3( incidentIor ) ) / ( transmittedIor + vec3( incidentIor ) ) );
	}
	float IorToFresnel0( float transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - incidentIor ) / ( transmittedIor + incidentIor ));
	}
	vec3 evalSensitivity( float OPD, vec3 shift ) {
		float phase = 2.0 * PI * OPD * 1.0e-9;
		vec3 val = vec3( 5.4856e-13, 4.4201e-13, 5.2481e-13 );
		vec3 pos = vec3( 1.6810e+06, 1.7953e+06, 2.2084e+06 );
		vec3 var = vec3( 4.3278e+09, 9.3046e+09, 6.6121e+09 );
		vec3 xyz = val * sqrt( 2.0 * PI * var ) * cos( pos * phase + shift ) * exp( - pow2( phase ) * var );
		xyz.x += 9.7470e-14 * sqrt( 2.0 * PI * 4.5282e+09 ) * cos( 2.2399e+06 * phase + shift[ 0 ] ) * exp( - 4.5282e+09 * pow2( phase ) );
		xyz /= 1.0685e-7;
		vec3 rgb = XYZ_TO_REC709 * xyz;
		return rgb;
	}
	vec3 evalIridescence( float outsideIOR, float eta2, float cosTheta1, float thinFilmThickness, vec3 baseF0 ) {
		vec3 I;
		float iridescenceIOR = mix( outsideIOR, eta2, smoothstep( 0.0, 0.03, thinFilmThickness ) );
		float sinTheta2Sq = pow2( outsideIOR / iridescenceIOR ) * ( 1.0 - pow2( cosTheta1 ) );
		float cosTheta2Sq = 1.0 - sinTheta2Sq;
		if ( cosTheta2Sq < 0.0 ) {
			return vec3( 1.0 );
		}
		float cosTheta2 = sqrt( cosTheta2Sq );
		float R0 = IorToFresnel0( iridescenceIOR, outsideIOR );
		float R12 = F_Schlick( R0, 1.0, cosTheta1 );
		float T121 = 1.0 - R12;
		float phi12 = 0.0;
		if ( iridescenceIOR < outsideIOR ) phi12 = PI;
		float phi21 = PI - phi12;
		vec3 baseIOR = Fresnel0ToIor( clamp( baseF0, 0.0, 0.9999 ) );		vec3 R1 = IorToFresnel0( baseIOR, iridescenceIOR );
		vec3 R23 = F_Schlick( R1, 1.0, cosTheta2 );
		vec3 phi23 = vec3( 0.0 );
		if ( baseIOR[ 0 ] < iridescenceIOR ) phi23[ 0 ] = PI;
		if ( baseIOR[ 1 ] < iridescenceIOR ) phi23[ 1 ] = PI;
		if ( baseIOR[ 2 ] < iridescenceIOR ) phi23[ 2 ] = PI;
		float OPD = 2.0 * iridescenceIOR * thinFilmThickness * cosTheta2;
		vec3 phi = vec3( phi21 ) + phi23;
		vec3 R123 = clamp( R12 * R23, 1e-5, 0.9999 );
		vec3 r123 = sqrt( R123 );
		vec3 Rs = pow2( T121 ) * R23 / ( vec3( 1.0 ) - R123 );
		vec3 C0 = R12 + Rs;
		I = C0;
		vec3 Cm = Rs - T121;
		for ( int m = 1; m <= 2; ++ m ) {
			Cm *= r123;
			vec3 Sm = 2.0 * evalSensitivity( float( m ) * OPD, float( m ) * phi );
			I += Cm * Sm;
		}
		return max( I, vec3( 0.0 ) );
	}
#endif`,bumpmap_pars_fragment:`#ifdef USE_BUMPMAP
	uniform sampler2D bumpMap;
	uniform float bumpScale;
	vec2 dHdxy_fwd() {
		vec2 dSTdx = dFdx( vBumpMapUv );
		vec2 dSTdy = dFdy( vBumpMapUv );
		float Hll = bumpScale * texture2D( bumpMap, vBumpMapUv ).x;
		float dBx = bumpScale * texture2D( bumpMap, vBumpMapUv + dSTdx ).x - Hll;
		float dBy = bumpScale * texture2D( bumpMap, vBumpMapUv + dSTdy ).x - Hll;
		return vec2( dBx, dBy );
	}
	vec3 perturbNormalArb( vec3 surf_pos, vec3 surf_norm, vec2 dHdxy, float faceDirection ) {
		vec3 vSigmaX = normalize( dFdx( surf_pos.xyz ) );
		vec3 vSigmaY = normalize( dFdy( surf_pos.xyz ) );
		vec3 vN = surf_norm;
		vec3 R1 = cross( vSigmaY, vN );
		vec3 R2 = cross( vN, vSigmaX );
		float fDet = dot( vSigmaX, R1 ) * faceDirection;
		vec3 vGrad = sign( fDet ) * ( dHdxy.x * R1 + dHdxy.y * R2 );
		return normalize( abs( fDet ) * surf_norm - vGrad );
	}
#endif`,clipping_planes_fragment:`#if NUM_CLIPPING_PLANES > 0
	vec4 plane;
	#ifdef ALPHA_TO_COVERAGE
		float distanceToPlane, distanceGradient;
		float clipOpacity = 1.0;
		#pragma unroll_loop_start
		for ( int i = 0; i < UNION_CLIPPING_PLANES; i ++ ) {
			plane = clippingPlanes[ i ];
			distanceToPlane = - dot( vClipPosition, plane.xyz ) + plane.w;
			distanceGradient = fwidth( distanceToPlane ) / 2.0;
			clipOpacity *= smoothstep( - distanceGradient, distanceGradient, distanceToPlane );
			if ( clipOpacity == 0.0 ) discard;
		}
		#pragma unroll_loop_end
		#if UNION_CLIPPING_PLANES < NUM_CLIPPING_PLANES
			float unionClipOpacity = 1.0;
			#pragma unroll_loop_start
			for ( int i = UNION_CLIPPING_PLANES; i < NUM_CLIPPING_PLANES; i ++ ) {
				plane = clippingPlanes[ i ];
				distanceToPlane = - dot( vClipPosition, plane.xyz ) + plane.w;
				distanceGradient = fwidth( distanceToPlane ) / 2.0;
				unionClipOpacity *= 1.0 - smoothstep( - distanceGradient, distanceGradient, distanceToPlane );
			}
			#pragma unroll_loop_end
			clipOpacity *= 1.0 - unionClipOpacity;
		#endif
		diffuseColor.a *= clipOpacity;
		if ( diffuseColor.a == 0.0 ) discard;
	#else
		#pragma unroll_loop_start
		for ( int i = 0; i < UNION_CLIPPING_PLANES; i ++ ) {
			plane = clippingPlanes[ i ];
			if ( dot( vClipPosition, plane.xyz ) > plane.w ) discard;
		}
		#pragma unroll_loop_end
		#if UNION_CLIPPING_PLANES < NUM_CLIPPING_PLANES
			bool clipped = true;
			#pragma unroll_loop_start
			for ( int i = UNION_CLIPPING_PLANES; i < NUM_CLIPPING_PLANES; i ++ ) {
				plane = clippingPlanes[ i ];
				clipped = ( dot( vClipPosition, plane.xyz ) > plane.w ) && clipped;
			}
			#pragma unroll_loop_end
			if ( clipped ) discard;
		#endif
	#endif
#endif`,clipping_planes_pars_fragment:`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,clipping_planes_pars_vertex:`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,clipping_planes_vertex:`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,color_fragment:`#if defined( USE_COLOR ) || defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#endif`,color_pars_fragment:`#if defined( USE_COLOR ) || defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#endif`,color_pars_vertex:`#if defined( USE_COLOR ) || defined( USE_COLOR_ALPHA ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec4 vColor;
#endif`,color_vertex:`#if defined( USE_COLOR ) || defined( USE_COLOR_ALPHA ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	vColor = vec4( 1.0 );
#endif
#ifdef USE_COLOR_ALPHA
	vColor *= color;
#elif defined( USE_COLOR )
	vColor.rgb *= color;
#endif
#ifdef USE_INSTANCING_COLOR
	vColor.rgb *= instanceColor.rgb;
#endif
#ifdef USE_BATCHING_COLOR
	vColor *= getBatchingColor( getIndirectIndex( gl_DrawID ) );
#endif`,common:`#define PI 3.141592653589793
#define PI2 6.283185307179586
#define PI_HALF 1.5707963267948966
#define RECIPROCAL_PI 0.3183098861837907
#define RECIPROCAL_PI2 0.15915494309189535
#define EPSILON 1e-6
#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
#define whiteComplement( a ) ( 1.0 - saturate( a ) )
float pow2( const in float x ) { return x*x; }
vec3 pow2( const in vec3 x ) { return x*x; }
float pow3( const in float x ) { return x*x*x; }
float pow4( const in float x ) { float x2 = x*x; return x2*x2; }
float max3( const in vec3 v ) { return max( max( v.x, v.y ), v.z ); }
float average( const in vec3 v ) { return dot( v, vec3( 0.3333333 ) ); }
highp float rand( const in vec2 uv ) {
	const highp float a = 12.9898, b = 78.233, c = 43758.5453;
	highp float dt = dot( uv.xy, vec2( a,b ) ), sn = mod( dt, PI );
	return fract( sin( sn ) * c );
}
#ifdef HIGH_PRECISION
	float precisionSafeLength( vec3 v ) { return length( v ); }
#else
	float precisionSafeLength( vec3 v ) {
		float maxComponent = max3( abs( v ) );
		return length( v / maxComponent ) * maxComponent;
	}
#endif
struct IncidentLight {
	vec3 color;
	vec3 direction;
	bool visible;
};
struct ReflectedLight {
	vec3 directDiffuse;
	vec3 directSpecular;
	vec3 indirectDiffuse;
	vec3 indirectSpecular;
};
#ifdef USE_ALPHAHASH
	varying vec3 vPosition;
#endif
vec3 transformDirection( in vec3 dir, in mat4 matrix ) {
	return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );
}
#define inverseTransformDirection transformDirectionByInverseViewMatrix
vec3 transformNormalByInverseViewMatrix( in vec3 normal, in mat4 viewMatrix ) {
	return normalize( ( vec4( normal, 0.0 ) * viewMatrix ).xyz );
}
vec3 transformDirectionByInverseViewMatrix( in vec3 dir, in mat4 viewMatrix ) {
	return normalize( ( vec4( dir, 0.0 ) * viewMatrix ).xyz );
}
bool isPerspectiveMatrix( mat4 m ) {
	return m[ 2 ][ 3 ] == - 1.0;
}
vec2 equirectUv( in vec3 dir ) {
	float u = atan( dir.z, dir.x ) * RECIPROCAL_PI2 + 0.5;
	float v = asin( clamp( dir.y, - 1.0, 1.0 ) ) * RECIPROCAL_PI + 0.5;
	return vec2( u, v );
}
vec3 BRDF_Lambert( const in vec3 diffuseColor ) {
	return RECIPROCAL_PI * diffuseColor;
}
vec3 F_Schlick( const in vec3 f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
}
float F_Schlick( const in float f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
} // validated`,cube_uv_reflection_fragment:`#ifdef ENVMAP_TYPE_CUBE_UV
	#define cubeUV_minMipLevel 4.0
	#define cubeUV_minTileSize 16.0
	float getFace( vec3 direction ) {
		vec3 absDirection = abs( direction );
		float face = - 1.0;
		if ( absDirection.x > absDirection.z ) {
			if ( absDirection.x > absDirection.y )
				face = direction.x > 0.0 ? 0.0 : 3.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		} else {
			if ( absDirection.z > absDirection.y )
				face = direction.z > 0.0 ? 2.0 : 5.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		}
		return face;
	}
	vec2 getUV( vec3 direction, float face ) {
		vec2 uv;
		if ( face == 0.0 ) {
			uv = vec2( direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 1.0 ) {
			uv = vec2( - direction.x, - direction.z ) / abs( direction.y );
		} else if ( face == 2.0 ) {
			uv = vec2( - direction.x, direction.y ) / abs( direction.z );
		} else if ( face == 3.0 ) {
			uv = vec2( - direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 4.0 ) {
			uv = vec2( - direction.x, direction.z ) / abs( direction.y );
		} else {
			uv = vec2( direction.x, direction.y ) / abs( direction.z );
		}
		return 0.5 * ( uv + 1.0 );
	}
	vec3 bilinearCubeUV( sampler2D envMap, vec3 direction, float mipInt ) {
		float face = getFace( direction );
		float filterInt = max( cubeUV_minMipLevel - mipInt, 0.0 );
		mipInt = max( mipInt, cubeUV_minMipLevel );
		float faceSize = exp2( mipInt );
		highp vec2 uv = getUV( direction, face ) * ( faceSize - 2.0 ) + 1.0;
		if ( face > 2.0 ) {
			uv.y += faceSize;
			face -= 3.0;
		}
		uv.x += face * faceSize;
		uv.x += filterInt * 3.0 * cubeUV_minTileSize;
		uv.y += 4.0 * ( exp2( CUBEUV_MAX_MIP ) - faceSize );
		uv.x *= CUBEUV_TEXEL_WIDTH;
		uv.y *= CUBEUV_TEXEL_HEIGHT;
		#ifdef texture2DGradEXT
			return texture2DGradEXT( envMap, uv, vec2( 0.0 ), vec2( 0.0 ) ).rgb;
		#else
			return texture2D( envMap, uv ).rgb;
		#endif
	}
	#define cubeUV_r0 1.0
	#define cubeUV_m0 - 2.0
	#define cubeUV_r1 0.8
	#define cubeUV_m1 - 1.0
	#define cubeUV_r4 0.4
	#define cubeUV_m4 2.0
	#define cubeUV_r5 0.305
	#define cubeUV_m5 3.0
	#define cubeUV_r6 0.21
	#define cubeUV_m6 4.0
	float roughnessToMip( float roughness ) {
		float mip = 0.0;
		if ( roughness >= cubeUV_r1 ) {
			mip = ( cubeUV_r0 - roughness ) * ( cubeUV_m1 - cubeUV_m0 ) / ( cubeUV_r0 - cubeUV_r1 ) + cubeUV_m0;
		} else if ( roughness >= cubeUV_r4 ) {
			mip = ( cubeUV_r1 - roughness ) * ( cubeUV_m4 - cubeUV_m1 ) / ( cubeUV_r1 - cubeUV_r4 ) + cubeUV_m1;
		} else if ( roughness >= cubeUV_r5 ) {
			mip = ( cubeUV_r4 - roughness ) * ( cubeUV_m5 - cubeUV_m4 ) / ( cubeUV_r4 - cubeUV_r5 ) + cubeUV_m4;
		} else if ( roughness >= cubeUV_r6 ) {
			mip = ( cubeUV_r5 - roughness ) * ( cubeUV_m6 - cubeUV_m5 ) / ( cubeUV_r5 - cubeUV_r6 ) + cubeUV_m5;
		} else {
			mip = - 2.0 * log2( 1.16 * roughness );		}
		return mip;
	}
	vec4 textureCubeUV( sampler2D envMap, vec3 sampleDir, float roughness ) {
		float mip = clamp( roughnessToMip( roughness ), cubeUV_m0, CUBEUV_MAX_MIP );
		float mipF = fract( mip );
		float mipInt = floor( mip );
		vec3 color0 = bilinearCubeUV( envMap, sampleDir, mipInt );
		if ( mipF == 0.0 ) {
			return vec4( color0, 1.0 );
		} else {
			vec3 color1 = bilinearCubeUV( envMap, sampleDir, mipInt + 1.0 );
			return vec4( mix( color0, color1, mipF ), 1.0 );
		}
	}
#endif`,defaultnormal_vertex:`vec3 transformedNormal = objectNormal;
#ifdef USE_TANGENT
	vec3 transformedTangent = objectTangent;
#endif
#ifdef USE_BATCHING
	mat3 bm = mat3( batchingMatrix );
	transformedNormal /= vec3( dot( bm[ 0 ], bm[ 0 ] ), dot( bm[ 1 ], bm[ 1 ] ), dot( bm[ 2 ], bm[ 2 ] ) );
	transformedNormal = bm * transformedNormal;
	#ifdef USE_TANGENT
		transformedTangent = bm * transformedTangent;
	#endif
#endif
#ifdef USE_INSTANCING
	mat3 im = mat3( instanceMatrix );
	transformedNormal /= vec3( dot( im[ 0 ], im[ 0 ] ), dot( im[ 1 ], im[ 1 ] ), dot( im[ 2 ], im[ 2 ] ) );
	transformedNormal = im * transformedNormal;
	#ifdef USE_TANGENT
		transformedTangent = im * transformedTangent;
	#endif
#endif
transformedNormal = normalMatrix * transformedNormal;
#ifdef FLIP_SIDED
	transformedNormal = - transformedNormal;
#endif
#ifdef USE_TANGENT
	transformedTangent = ( modelViewMatrix * vec4( transformedTangent, 0.0 ) ).xyz;
#endif`,displacementmap_pars_vertex:`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,displacementmap_vertex:`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,emissivemap_fragment:`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	#ifdef DECODE_VIDEO_TEXTURE_EMISSIVE
		emissiveColor = sRGBTransferEOTF( emissiveColor );
	#endif
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,emissivemap_pars_fragment:`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,colorspace_fragment:`gl_FragColor = linearToOutputTexel( gl_FragColor );`,colorspace_pars_fragment:`vec4 LinearTransferOETF( in vec4 value ) {
	return value;
}
vec4 sRGBTransferEOTF( in vec4 value ) {
	return vec4( mix( pow( value.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), value.rgb * 0.0773993808, vec3( lessThanEqual( value.rgb, vec3( 0.04045 ) ) ) ), value.a );
}
vec4 sRGBTransferOETF( in vec4 value ) {
	return vec4( mix( pow( value.rgb, vec3( 0.41666 ) ) * 1.055 - vec3( 0.055 ), value.rgb * 12.92, vec3( lessThanEqual( value.rgb, vec3( 0.0031308 ) ) ) ), value.a );
}`,envmap_fragment:`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vec3 cameraToFrag;
		if ( isOrthographic ) {
			cameraToFrag = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToFrag = normalize( vWorldPosition - cameraPosition );
		}
		vec3 worldNormal = transformNormalByInverseViewMatrix( normal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vec3 reflectVec = reflect( cameraToFrag, worldNormal );
		#else
			vec3 reflectVec = refract( cameraToFrag, worldNormal, refractionRatio );
		#endif
	#else
		vec3 reflectVec = vReflect;
	#endif
	#ifdef ENVMAP_TYPE_CUBE
		vec4 envColor = textureCube( envMap, envMapRotation * reflectVec );
		#ifdef ENVMAP_BLENDING_MULTIPLY
			outgoingLight = mix( outgoingLight, outgoingLight * envColor.xyz, specularStrength * reflectivity );
		#elif defined( ENVMAP_BLENDING_MIX )
			outgoingLight = mix( outgoingLight, envColor.xyz, specularStrength * reflectivity );
		#elif defined( ENVMAP_BLENDING_ADD )
			outgoingLight += envColor.xyz * specularStrength * reflectivity;
		#endif
	#endif
#endif`,envmap_common_pars_fragment:`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
#endif`,envmap_pars_fragment:`#ifdef USE_ENVMAP
	uniform float reflectivity;
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		varying vec3 vWorldPosition;
		uniform float refractionRatio;
	#else
		varying vec3 vReflect;
	#endif
#endif`,envmap_pars_vertex:`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,envmap_physical_pars_fragment:`#ifdef USE_ENVMAP
	vec3 getIBLIrradiance( const in vec3 normal ) {
		#ifdef ENVMAP_TYPE_CUBE_UV
			vec3 worldNormal = transformNormalByInverseViewMatrix( normal, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, envMapRotation * worldNormal, 1.0 );
			return PI * envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	vec3 getIBLRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness ) {
		#ifdef ENVMAP_TYPE_CUBE_UV
			vec3 reflectVec = reflect( - viewDir, normal );
			reflectVec = normalize( mix( reflectVec, normal, pow4( roughness ) ) );
			reflectVec = transformDirectionByInverseViewMatrix( reflectVec, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, envMapRotation * reflectVec, roughness );
			return envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	#ifdef USE_ANISOTROPY
		vec3 getIBLAnisotropyRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness, const in vec3 bitangent, const in float anisotropy ) {
			#ifdef ENVMAP_TYPE_CUBE_UV
				vec3 bentNormal = cross( bitangent, viewDir );
				bentNormal = normalize( cross( bentNormal, bitangent ) );
				bentNormal = normalize( mix( bentNormal, normal, pow2( pow2( 1.0 - anisotropy * ( 1.0 - roughness ) ) ) ) );
				return getIBLRadiance( viewDir, bentNormal, roughness );
			#else
				return vec3( 0.0 );
			#endif
		}
	#endif
#endif`,envmap_vertex:`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vWorldPosition = worldPosition.xyz;
	#else
		vec3 cameraToVertex;
		if ( isOrthographic ) {
			cameraToVertex = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToVertex = normalize( worldPosition.xyz - cameraPosition );
		}
		vec3 worldNormal = transformNormalByInverseViewMatrix( transformedNormal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vReflect = reflect( cameraToVertex, worldNormal );
		#else
			vReflect = refract( cameraToVertex, worldNormal, refractionRatio );
		#endif
	#endif
#endif`,fog_vertex:`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,fog_pars_vertex:`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,fog_fragment:`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,fog_pars_fragment:`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,gradientmap_pars_fragment:`#ifdef USE_GRADIENTMAP
	uniform sampler2D gradientMap;
#endif
vec3 getGradientIrradiance( vec3 normal, vec3 lightDirection ) {
	float dotNL = dot( normal, lightDirection );
	vec2 coord = vec2( dotNL * 0.5 + 0.5, 0.0 );
	#ifdef USE_GRADIENTMAP
		return vec3( texture2D( gradientMap, coord ).r );
	#else
		vec2 fw = fwidth( coord ) * 0.5;
		return mix( vec3( 0.7 ), vec3( 1.0 ), smoothstep( 0.7 - fw.x, 0.7 + fw.x, coord.x ) );
	#endif
}`,lightmap_pars_fragment:`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,lights_lambert_fragment:`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,lights_lambert_pars_fragment:`varying vec3 vViewPosition;
struct LambertMaterial {
	vec3 diffuseColor;
	float specularStrength;
};
void RE_Direct_Lambert( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Lambert( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Lambert
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,lights_pars_begin:`uniform bool receiveShadow;
uniform vec3 ambientLightColor;
#if defined( USE_LIGHT_PROBES )
	uniform vec3 lightProbe[ 9 ];
#endif
vec3 shGetIrradianceAt( in vec3 normal, in vec3 shCoefficients[ 9 ] ) {
	float x = normal.x, y = normal.y, z = normal.z;
	vec3 result = shCoefficients[ 0 ] * 0.886227;
	result += shCoefficients[ 1 ] * 2.0 * 0.511664 * y;
	result += shCoefficients[ 2 ] * 2.0 * 0.511664 * z;
	result += shCoefficients[ 3 ] * 2.0 * 0.511664 * x;
	result += shCoefficients[ 4 ] * 2.0 * 0.429043 * x * y;
	result += shCoefficients[ 5 ] * 2.0 * 0.429043 * y * z;
	result += shCoefficients[ 6 ] * ( 0.743125 * z * z - 0.247708 );
	result += shCoefficients[ 7 ] * 2.0 * 0.429043 * x * z;
	result += shCoefficients[ 8 ] * 0.429043 * ( x * x - y * y );
	return result;
}
vec3 getLightProbeIrradiance( const in vec3 lightProbe[ 9 ], const in vec3 normal ) {
	vec3 worldNormal = transformNormalByInverseViewMatrix( normal, viewMatrix );
	vec3 irradiance = shGetIrradianceAt( worldNormal, lightProbe );
	return irradiance;
}
vec3 getAmbientLightIrradiance( const in vec3 ambientLightColor ) {
	vec3 irradiance = ambientLightColor;
	return irradiance;
}
float getDistanceAttenuation( const in float lightDistance, const in float cutoffDistance, const in float decayExponent ) {
	float distanceFalloff = 1.0 / max( pow( lightDistance, decayExponent ), 0.01 );
	if ( cutoffDistance > 0.0 ) {
		distanceFalloff *= pow2( saturate( 1.0 - pow4( lightDistance / cutoffDistance ) ) );
	}
	return distanceFalloff;
}
float getSpotAttenuation( const in float coneCosine, const in float penumbraCosine, const in float angleCosine ) {
	return smoothstep( coneCosine, penumbraCosine, angleCosine );
}
#if NUM_DIR_LIGHTS > 0
	struct DirectionalLight {
		vec3 direction;
		vec3 color;
	};
	uniform DirectionalLight directionalLights[ NUM_DIR_LIGHTS ];
	void getDirectionalLightInfo( const in DirectionalLight directionalLight, out IncidentLight light ) {
		light.color = directionalLight.color;
		light.direction = directionalLight.direction;
		light.visible = true;
	}
#endif
#if NUM_POINT_LIGHTS > 0
	struct PointLight {
		vec3 position;
		vec3 color;
		float distance;
		float decay;
	};
	uniform PointLight pointLights[ NUM_POINT_LIGHTS ];
	void getPointLightInfo( const in PointLight pointLight, const in vec3 geometryPosition, out IncidentLight light ) {
		vec3 lVector = pointLight.position - geometryPosition;
		light.direction = normalize( lVector );
		float lightDistance = length( lVector );
		light.color = pointLight.color;
		light.color *= getDistanceAttenuation( lightDistance, pointLight.distance, pointLight.decay );
		light.visible = ( light.color != vec3( 0.0 ) );
	}
#endif
#if NUM_SPOT_LIGHTS > 0
	struct SpotLight {
		vec3 position;
		vec3 direction;
		vec3 color;
		float distance;
		float decay;
		float coneCos;
		float penumbraCos;
	};
	uniform SpotLight spotLights[ NUM_SPOT_LIGHTS ];
	void getSpotLightInfo( const in SpotLight spotLight, const in vec3 geometryPosition, out IncidentLight light ) {
		vec3 lVector = spotLight.position - geometryPosition;
		light.direction = normalize( lVector );
		float angleCos = dot( light.direction, spotLight.direction );
		float spotAttenuation = getSpotAttenuation( spotLight.coneCos, spotLight.penumbraCos, angleCos );
		if ( spotAttenuation > 0.0 ) {
			float lightDistance = length( lVector );
			light.color = spotLight.color * spotAttenuation;
			light.color *= getDistanceAttenuation( lightDistance, spotLight.distance, spotLight.decay );
			light.visible = ( light.color != vec3( 0.0 ) );
		} else {
			light.color = vec3( 0.0 );
			light.visible = false;
		}
	}
#endif
#if NUM_RECT_AREA_LIGHTS > 0
	struct RectAreaLight {
		vec3 color;
		vec3 position;
		vec3 halfWidth;
		vec3 halfHeight;
	};
	uniform sampler2D ltc_1;	uniform sampler2D ltc_2;
	uniform RectAreaLight rectAreaLights[ NUM_RECT_AREA_LIGHTS ];
#endif
#if NUM_HEMI_LIGHTS > 0
	struct HemisphereLight {
		vec3 direction;
		vec3 skyColor;
		vec3 groundColor;
	};
	uniform HemisphereLight hemisphereLights[ NUM_HEMI_LIGHTS ];
	vec3 getHemisphereLightIrradiance( const in HemisphereLight hemiLight, const in vec3 normal ) {
		float dotNL = dot( normal, hemiLight.direction );
		float hemiDiffuseWeight = 0.5 * dotNL + 0.5;
		vec3 irradiance = mix( hemiLight.groundColor, hemiLight.skyColor, hemiDiffuseWeight );
		return irradiance;
	}
#endif
#include <lightprobes_pars_fragment>`,lights_toon_fragment:`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,lights_toon_pars_fragment:`varying vec3 vViewPosition;
struct ToonMaterial {
	vec3 diffuseColor;
};
void RE_Direct_Toon( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	vec3 irradiance = getGradientIrradiance( geometryNormal, directLight.direction ) * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Toon( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Toon
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,lights_phong_fragment:`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,lights_phong_pars_fragment:`varying vec3 vViewPosition;
struct BlinnPhongMaterial {
	vec3 diffuseColor;
	vec3 specularColor;
	float specularShininess;
	float specularStrength;
};
void RE_Direct_BlinnPhong( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
	reflectedLight.directSpecular += irradiance * BRDF_BlinnPhong( directLight.direction, geometryViewDir, geometryNormal, material.specularColor, material.specularShininess ) * material.specularStrength;
}
void RE_IndirectDiffuse_BlinnPhong( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_BlinnPhong
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,lights_physical_fragment:`PhysicalMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.diffuseContribution = diffuseColor.rgb * ( 1.0 - metalnessFactor );
material.metalness = metalnessFactor;
vec3 dxy = max( abs( dFdx( nonPerturbedNormal ) ), abs( dFdy( nonPerturbedNormal ) ) );
float geometryRoughness = max( max( dxy.x, dxy.y ), dxy.z );
material.roughness = max( roughnessFactor, 0.0525 );material.roughness += geometryRoughness;
material.roughness = min( material.roughness, 1.0 );
#ifdef IOR
	material.ior = ior;
	#ifdef USE_SPECULAR
		float specularIntensityFactor = specularIntensity;
		vec3 specularColorFactor = specularColor;
		#ifdef USE_SPECULAR_COLORMAP
			specularColorFactor *= texture2D( specularColorMap, vSpecularColorMapUv ).rgb;
		#endif
		#ifdef USE_SPECULAR_INTENSITYMAP
			specularIntensityFactor *= texture2D( specularIntensityMap, vSpecularIntensityMapUv ).a;
		#endif
		material.specularF90 = mix( specularIntensityFactor, 1.0, metalnessFactor );
	#else
		float specularIntensityFactor = 1.0;
		vec3 specularColorFactor = vec3( 1.0 );
		material.specularF90 = 1.0;
	#endif
	material.specularColor = min( pow2( ( material.ior - 1.0 ) / ( material.ior + 1.0 ) ) * specularColorFactor, vec3( 1.0 ) ) * specularIntensityFactor;
	material.specularColorBlended = mix( material.specularColor, diffuseColor.rgb, metalnessFactor );
#else
	material.specularColor = vec3( 0.04 );
	material.specularColorBlended = mix( material.specularColor, diffuseColor.rgb, metalnessFactor );
	material.specularF90 = 1.0;
#endif
#ifdef USE_CLEARCOAT
	material.clearcoat = clearcoat;
	material.clearcoatRoughness = clearcoatRoughness;
	material.clearcoatF0 = vec3( 0.04 );
	material.clearcoatF90 = 1.0;
	#ifdef USE_CLEARCOATMAP
		material.clearcoat *= texture2D( clearcoatMap, vClearcoatMapUv ).x;
	#endif
	#ifdef USE_CLEARCOAT_ROUGHNESSMAP
		material.clearcoatRoughness *= texture2D( clearcoatRoughnessMap, vClearcoatRoughnessMapUv ).y;
	#endif
	material.clearcoat = saturate( material.clearcoat );	material.clearcoatRoughness = max( material.clearcoatRoughness, 0.0525 );
	material.clearcoatRoughness += geometryRoughness;
	material.clearcoatRoughness = min( material.clearcoatRoughness, 1.0 );
#endif
#ifdef USE_DISPERSION
	material.dispersion = dispersion;
#endif
#ifdef USE_IRIDESCENCE
	material.iridescence = iridescence;
	material.iridescenceIOR = iridescenceIOR;
	#ifdef USE_IRIDESCENCEMAP
		material.iridescence *= texture2D( iridescenceMap, vIridescenceMapUv ).r;
	#endif
	#ifdef USE_IRIDESCENCE_THICKNESSMAP
		material.iridescenceThickness = (iridescenceThicknessMaximum - iridescenceThicknessMinimum) * texture2D( iridescenceThicknessMap, vIridescenceThicknessMapUv ).g + iridescenceThicknessMinimum;
	#else
		material.iridescenceThickness = iridescenceThicknessMaximum;
	#endif
#endif
#ifdef USE_SHEEN
	material.sheenColor = sheenColor;
	#ifdef USE_SHEEN_COLORMAP
		material.sheenColor *= texture2D( sheenColorMap, vSheenColorMapUv ).rgb;
	#endif
	material.sheenRoughness = clamp( sheenRoughness, 0.0001, 1.0 );
	#ifdef USE_SHEEN_ROUGHNESSMAP
		material.sheenRoughness *= texture2D( sheenRoughnessMap, vSheenRoughnessMapUv ).a;
	#endif
#endif
#ifdef USE_ANISOTROPY
	#ifdef USE_ANISOTROPYMAP
		mat2 anisotropyMat = mat2( anisotropyVector.x, anisotropyVector.y, - anisotropyVector.y, anisotropyVector.x );
		vec3 anisotropyPolar = texture2D( anisotropyMap, vAnisotropyMapUv ).rgb;
		vec2 anisotropyV = anisotropyMat * normalize( 2.0 * anisotropyPolar.rg - vec2( 1.0 ) ) * anisotropyPolar.b;
	#else
		vec2 anisotropyV = anisotropyVector;
	#endif
	material.anisotropy = length( anisotropyV );
	if( material.anisotropy == 0.0 ) {
		anisotropyV = vec2( 1.0, 0.0 );
	} else {
		anisotropyV /= material.anisotropy;
		material.anisotropy = saturate( material.anisotropy );
	}
	material.alphaT = mix( pow2( material.roughness ), 1.0, pow2( material.anisotropy ) );
	material.anisotropyT = tbn[ 0 ] * anisotropyV.x + tbn[ 1 ] * anisotropyV.y;
	material.anisotropyB = tbn[ 1 ] * anisotropyV.x - tbn[ 0 ] * anisotropyV.y;
#endif`,lights_physical_pars_fragment:`uniform sampler2D dfgLUT;
struct PhysicalMaterial {
	vec3 diffuseColor;
	vec3 diffuseContribution;
	vec3 specularColor;
	vec3 specularColorBlended;
	float roughness;
	float metalness;
	float specularF90;
	float dispersion;
	#ifdef USE_CLEARCOAT
		float clearcoat;
		float clearcoatRoughness;
		vec3 clearcoatF0;
		float clearcoatF90;
	#endif
	#ifdef USE_IRIDESCENCE
		float iridescence;
		float iridescenceIOR;
		float iridescenceThickness;
		vec3 iridescenceFresnel;
		vec3 iridescenceF0;
		vec3 iridescenceFresnelDielectric;
		vec3 iridescenceFresnelMetallic;
	#endif
	#ifdef USE_SHEEN
		vec3 sheenColor;
		float sheenRoughness;
	#endif
	#ifdef IOR
		float ior;
	#endif
	#ifdef USE_TRANSMISSION
		float transmission;
		float transmissionAlpha;
		float thickness;
		float attenuationDistance;
		vec3 attenuationColor;
	#endif
	#ifdef USE_ANISOTROPY
		float anisotropy;
		float alphaT;
		vec3 anisotropyT;
		vec3 anisotropyB;
	#endif
};
vec3 clearcoatSpecularDirect = vec3( 0.0 );
vec3 clearcoatSpecularIndirect = vec3( 0.0 );
vec3 sheenSpecularDirect = vec3( 0.0 );
vec3 sheenSpecularIndirect = vec3(0.0 );
vec3 Schlick_to_F0( const in vec3 f, const in float f90, const in float dotVH ) {
    float x = clamp( 1.0 - dotVH, 0.0, 1.0 );
    float x2 = x * x;
    float x5 = clamp( x * x2 * x2, 0.0, 0.9999 );
    return ( f - vec3( f90 ) * x5 ) / ( 1.0 - x5 );
}
float V_GGX_SmithCorrelated( const in float alpha, const in float dotNL, const in float dotNV ) {
	float a2 = pow2( alpha );
	float gv = dotNL * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNV ) );
	float gl = dotNV * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNL ) );
	return 0.5 / max( gv + gl, EPSILON );
}
float D_GGX( const in float alpha, const in float dotNH ) {
	float a2 = pow2( alpha );
	float denom = pow2( dotNH ) * ( a2 - 1.0 ) + 1.0;
	return RECIPROCAL_PI * a2 / pow2( denom );
}
#ifdef USE_ANISOTROPY
	float V_GGX_SmithCorrelated_Anisotropic( const in float alphaT, const in float alphaB, const in float dotTV, const in float dotBV, const in float dotTL, const in float dotBL, const in float dotNV, const in float dotNL ) {
		float gv = dotNL * length( vec3( alphaT * dotTV, alphaB * dotBV, dotNV ) );
		float gl = dotNV * length( vec3( alphaT * dotTL, alphaB * dotBL, dotNL ) );
		return 0.5 / max( gv + gl, EPSILON );
	}
	float D_GGX_Anisotropic( const in float alphaT, const in float alphaB, const in float dotNH, const in float dotTH, const in float dotBH ) {
		float a2 = alphaT * alphaB;
		highp vec3 v = vec3( alphaB * dotTH, alphaT * dotBH, a2 * dotNH );
		highp float v2 = dot( v, v );
		float w2 = a2 / v2;
		return RECIPROCAL_PI * a2 * pow2 ( w2 );
	}
#endif
#ifdef USE_CLEARCOAT
	vec3 BRDF_GGX_Clearcoat( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material) {
		vec3 f0 = material.clearcoatF0;
		float f90 = material.clearcoatF90;
		float roughness = material.clearcoatRoughness;
		float alpha = pow2( roughness );
		vec3 halfDir = normalize( lightDir + viewDir );
		float dotNL = saturate( dot( normal, lightDir ) );
		float dotNV = saturate( dot( normal, viewDir ) );
		float dotNH = saturate( dot( normal, halfDir ) );
		float dotVH = saturate( dot( viewDir, halfDir ) );
		vec3 F = F_Schlick( f0, f90, dotVH );
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
		return F * ( V * D );
	}
#endif
vec3 BRDF_GGX( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material ) {
	vec3 f0 = material.specularColorBlended;
	float f90 = material.specularF90;
	float roughness = material.roughness;
	float alpha = pow2( roughness );
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( f0, f90, dotVH );
	#ifdef USE_IRIDESCENCE
		F = mix( F, material.iridescenceFresnel, material.iridescence );
	#endif
	#ifdef USE_ANISOTROPY
		float dotTL = dot( material.anisotropyT, lightDir );
		float dotTV = dot( material.anisotropyT, viewDir );
		float dotTH = dot( material.anisotropyT, halfDir );
		float dotBL = dot( material.anisotropyB, lightDir );
		float dotBV = dot( material.anisotropyB, viewDir );
		float dotBH = dot( material.anisotropyB, halfDir );
		float V = V_GGX_SmithCorrelated_Anisotropic( material.alphaT, alpha, dotTV, dotBV, dotTL, dotBL, dotNV, dotNL );
		float D = D_GGX_Anisotropic( material.alphaT, alpha, dotNH, dotTH, dotBH );
	#else
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
	#endif
	return F * ( V * D );
}
vec2 LTC_Uv( const in vec3 N, const in vec3 V, const in float roughness ) {
	const float LUT_SIZE = 64.0;
	const float LUT_SCALE = ( LUT_SIZE - 1.0 ) / LUT_SIZE;
	const float LUT_BIAS = 0.5 / LUT_SIZE;
	float dotNV = saturate( dot( N, V ) );
	vec2 uv = vec2( roughness, sqrt( 1.0 - dotNV ) );
	uv = uv * LUT_SCALE + LUT_BIAS;
	return uv;
}
float LTC_ClippedSphereFormFactor( const in vec3 f ) {
	float l = length( f );
	return max( ( l * l + f.z ) / ( l + 1.0 ), 0.0 );
}
vec3 LTC_EdgeVectorFormFactor( const in vec3 v1, const in vec3 v2 ) {
	float x = dot( v1, v2 );
	float y = abs( x );
	float a = 0.8543985 + ( 0.4965155 + 0.0145206 * y ) * y;
	float b = 3.4175940 + ( 4.1616724 + y ) * y;
	float v = a / b;
	float theta_sintheta = ( x > 0.0 ) ? v : 0.5 * inversesqrt( max( 1.0 - x * x, 1e-7 ) ) - v;
	return cross( v1, v2 ) * theta_sintheta;
}
vec3 LTC_Evaluate( const in vec3 N, const in vec3 V, const in vec3 P, const in mat3 mInv, const in vec3 rectCoords[ 4 ] ) {
	vec3 v1 = rectCoords[ 1 ] - rectCoords[ 0 ];
	vec3 v2 = rectCoords[ 3 ] - rectCoords[ 0 ];
	vec3 lightNormal = cross( v1, v2 );
	if( dot( lightNormal, P - rectCoords[ 0 ] ) < 0.0 ) return vec3( 0.0 );
	vec3 T1, T2;
	T1 = normalize( V - N * dot( V, N ) );
	T2 = - cross( N, T1 );
	mat3 mat = mInv * transpose( mat3( T1, T2, N ) );
	vec3 coords[ 4 ];
	coords[ 0 ] = mat * ( rectCoords[ 0 ] - P );
	coords[ 1 ] = mat * ( rectCoords[ 1 ] - P );
	coords[ 2 ] = mat * ( rectCoords[ 2 ] - P );
	coords[ 3 ] = mat * ( rectCoords[ 3 ] - P );
	coords[ 0 ] = normalize( coords[ 0 ] );
	coords[ 1 ] = normalize( coords[ 1 ] );
	coords[ 2 ] = normalize( coords[ 2 ] );
	coords[ 3 ] = normalize( coords[ 3 ] );
	vec3 vectorFormFactor = vec3( 0.0 );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 0 ], coords[ 1 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 1 ], coords[ 2 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 2 ], coords[ 3 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 3 ], coords[ 0 ] );
	float result = LTC_ClippedSphereFormFactor( vectorFormFactor );
	return vec3( result );
}
#if defined( USE_SHEEN )
float D_Charlie( float roughness, float dotNH ) {
	float alpha = pow2( roughness );
	float invAlpha = 1.0 / alpha;
	float cos2h = dotNH * dotNH;
	float sin2h = max( 1.0 - cos2h, 0.0078125 );
	return ( 2.0 + invAlpha ) * pow( sin2h, invAlpha * 0.5 ) / ( 2.0 * PI );
}
float V_Neubelt( float dotNV, float dotNL ) {
	return saturate( 1.0 / ( 4.0 * ( dotNL + dotNV - dotNL * dotNV ) ) );
}
vec3 BRDF_Sheen( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, vec3 sheenColor, const in float sheenRoughness ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float D = D_Charlie( sheenRoughness, dotNH );
	float V = V_Neubelt( dotNV, dotNL );
	return sheenColor * ( D * V );
}
#endif
float IBLSheenBRDF( const in vec3 normal, const in vec3 viewDir, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	float r2 = roughness * roughness;
	float rInv = 1.0 / ( roughness + 0.1 );
	float a = -1.9362 + 1.0678 * roughness + 0.4573 * r2 - 0.8469 * rInv;
	float b = -0.6014 + 0.5538 * roughness - 0.4670 * r2 - 0.1255 * rInv;
	float DG = exp( a * dotNV + b );
	return saturate( DG );
}
vec3 EnvironmentBRDF( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	vec2 fab = texture2D( dfgLUT, vec2( roughness, dotNV ) ).rg;
	return specularColor * fab.x + specularF90 * fab.y;
}
#ifdef USE_IRIDESCENCE
void computeMultiscatteringIridescence( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float iridescence, const in vec3 iridescenceF0, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#else
void computeMultiscattering( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#endif
	float dotNV = saturate( dot( normal, viewDir ) );
	vec2 fab = texture2D( dfgLUT, vec2( roughness, dotNV ) ).rg;
	#ifdef USE_IRIDESCENCE
		vec3 Fr = mix( specularColor, iridescenceF0, iridescence );
	#else
		vec3 Fr = specularColor;
	#endif
	vec3 FssEss = Fr * fab.x + specularF90 * fab.y;
	float Ess = fab.x + fab.y;
	float Ems = 1.0 - Ess;
	vec3 Favg = Fr + ( 1.0 - Fr ) * 0.047619;	vec3 Fms = FssEss * Favg / ( 1.0 - Ems * Favg );
	singleScatter += FssEss;
	multiScatter += Fms * Ems;
}
vec3 BRDF_GGX_Multiscatter( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material ) {
	vec3 singleScatter = BRDF_GGX( lightDir, viewDir, normal, material );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	vec2 dfgV = texture2D( dfgLUT, vec2( material.roughness, dotNV ) ).rg;
	vec2 dfgL = texture2D( dfgLUT, vec2( material.roughness, dotNL ) ).rg;
	vec3 FssEss_V = material.specularColorBlended * dfgV.x + material.specularF90 * dfgV.y;
	vec3 FssEss_L = material.specularColorBlended * dfgL.x + material.specularF90 * dfgL.y;
	float Ess_V = dfgV.x + dfgV.y;
	float Ess_L = dfgL.x + dfgL.y;
	float Ems_V = 1.0 - Ess_V;
	float Ems_L = 1.0 - Ess_L;
	vec3 Favg = material.specularColorBlended + ( 1.0 - material.specularColorBlended ) * 0.047619;
	vec3 Fms = FssEss_V * FssEss_L * Favg / ( 1.0 - Ems_V * Ems_L * Favg + EPSILON );
	float compensationFactor = Ems_V * Ems_L;
	vec3 multiScatter = Fms * compensationFactor;
	return singleScatter + multiScatter;
}
#if NUM_RECT_AREA_LIGHTS > 0
	void RE_Direct_RectArea_Physical( const in RectAreaLight rectAreaLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
		vec3 normal = geometryNormal;
		vec3 viewDir = geometryViewDir;
		vec3 position = geometryPosition;
		vec3 lightPos = rectAreaLight.position;
		vec3 halfWidth = rectAreaLight.halfWidth;
		vec3 halfHeight = rectAreaLight.halfHeight;
		vec3 lightColor = rectAreaLight.color;
		float roughness = material.roughness;
		vec3 rectCoords[ 4 ];
		rectCoords[ 0 ] = lightPos + halfWidth - halfHeight;		rectCoords[ 1 ] = lightPos - halfWidth - halfHeight;
		rectCoords[ 2 ] = lightPos - halfWidth + halfHeight;
		rectCoords[ 3 ] = lightPos + halfWidth + halfHeight;
		vec2 uv = LTC_Uv( normal, viewDir, roughness );
		vec4 t1 = texture2D( ltc_1, uv );
		vec4 t2 = texture2D( ltc_2, uv );
		mat3 mInv = mat3(
			vec3( t1.x, 0, t1.y ),
			vec3(    0, 1,    0 ),
			vec3( t1.z, 0, t1.w )
		);
		vec3 fresnel = ( material.specularColorBlended * t2.x + ( material.specularF90 - material.specularColorBlended ) * t2.y );
		reflectedLight.directSpecular += lightColor * fresnel * LTC_Evaluate( normal, viewDir, position, mInv, rectCoords );
		reflectedLight.directDiffuse += lightColor * material.diffuseContribution * LTC_Evaluate( normal, viewDir, position, mat3( 1.0 ), rectCoords );
		#ifdef USE_CLEARCOAT
			vec3 Ncc = geometryClearcoatNormal;
			vec2 uvClearcoat = LTC_Uv( Ncc, viewDir, material.clearcoatRoughness );
			vec4 t1Clearcoat = texture2D( ltc_1, uvClearcoat );
			vec4 t2Clearcoat = texture2D( ltc_2, uvClearcoat );
			mat3 mInvClearcoat = mat3(
				vec3( t1Clearcoat.x, 0, t1Clearcoat.y ),
				vec3(             0, 1,             0 ),
				vec3( t1Clearcoat.z, 0, t1Clearcoat.w )
			);
			vec3 fresnelClearcoat = material.clearcoatF0 * t2Clearcoat.x + ( material.clearcoatF90 - material.clearcoatF0 ) * t2Clearcoat.y;
			clearcoatSpecularDirect += lightColor * fresnelClearcoat * LTC_Evaluate( Ncc, viewDir, position, mInvClearcoat, rectCoords );
		#endif
	}
#endif
void RE_Direct_Physical( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	#ifdef USE_CLEARCOAT
		float dotNLcc = saturate( dot( geometryClearcoatNormal, directLight.direction ) );
		vec3 ccIrradiance = dotNLcc * directLight.color;
		clearcoatSpecularDirect += ccIrradiance * BRDF_GGX_Clearcoat( directLight.direction, geometryViewDir, geometryClearcoatNormal, material );
	#endif
	#ifdef USE_SHEEN
 
 		sheenSpecularDirect += irradiance * BRDF_Sheen( directLight.direction, geometryViewDir, geometryNormal, material.sheenColor, material.sheenRoughness );
 
 		float sheenAlbedoV = IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness );
 		float sheenAlbedoL = IBLSheenBRDF( geometryNormal, directLight.direction, material.sheenRoughness );
 
 		float sheenEnergyComp = 1.0 - max3( material.sheenColor ) * max( sheenAlbedoV, sheenAlbedoL );
 
 		irradiance *= sheenEnergyComp;
 
 	#endif
	reflectedLight.directSpecular += irradiance * BRDF_GGX_Multiscatter( directLight.direction, geometryViewDir, geometryNormal, material );
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseContribution );
}
void RE_IndirectDiffuse_Physical( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	vec3 diffuse = irradiance * BRDF_Lambert( material.diffuseContribution );
	#ifdef USE_SHEEN
		float sheenAlbedo = IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness );
		float sheenEnergyComp = 1.0 - max3( material.sheenColor ) * sheenAlbedo;
		diffuse *= sheenEnergyComp;
	#endif
	reflectedLight.indirectDiffuse += diffuse;
}
void RE_IndirectSpecular_Physical( const in vec3 radiance, const in vec3 irradiance, const in vec3 clearcoatRadiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight) {
	#ifdef USE_CLEARCOAT
		clearcoatSpecularIndirect += clearcoatRadiance * EnvironmentBRDF( geometryClearcoatNormal, geometryViewDir, material.clearcoatF0, material.clearcoatF90, material.clearcoatRoughness );
	#endif
	#ifdef USE_SHEEN
		sheenSpecularIndirect += irradiance * material.sheenColor * IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness ) * RECIPROCAL_PI;
 	#endif
	vec3 singleScatteringDielectric = vec3( 0.0 );
	vec3 multiScatteringDielectric = vec3( 0.0 );
	vec3 singleScatteringMetallic = vec3( 0.0 );
	vec3 multiScatteringMetallic = vec3( 0.0 );
	#ifdef USE_IRIDESCENCE
		computeMultiscatteringIridescence( geometryNormal, geometryViewDir, material.specularColor, material.specularF90, material.iridescence, material.iridescenceFresnelDielectric, material.roughness, singleScatteringDielectric, multiScatteringDielectric );
		computeMultiscatteringIridescence( geometryNormal, geometryViewDir, material.diffuseColor, material.specularF90, material.iridescence, material.iridescenceFresnelMetallic, material.roughness, singleScatteringMetallic, multiScatteringMetallic );
	#else
		computeMultiscattering( geometryNormal, geometryViewDir, material.specularColor, material.specularF90, material.roughness, singleScatteringDielectric, multiScatteringDielectric );
		computeMultiscattering( geometryNormal, geometryViewDir, material.diffuseColor, material.specularF90, material.roughness, singleScatteringMetallic, multiScatteringMetallic );
	#endif
	vec3 singleScattering = mix( singleScatteringDielectric, singleScatteringMetallic, material.metalness );
	vec3 multiScattering = mix( multiScatteringDielectric, multiScatteringMetallic, material.metalness );
	vec3 totalScatteringDielectric = singleScatteringDielectric + multiScatteringDielectric;
	vec3 diffuse = material.diffuseContribution * ( 1.0 - totalScatteringDielectric );
	vec3 cosineWeightedIrradiance = irradiance * RECIPROCAL_PI;
	vec3 indirectSpecular = radiance * singleScattering;
	indirectSpecular += multiScattering * cosineWeightedIrradiance;
	vec3 indirectDiffuse = diffuse * cosineWeightedIrradiance;
	#ifdef USE_SHEEN
		float sheenAlbedo = IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness );
		float sheenEnergyComp = 1.0 - max3( material.sheenColor ) * sheenAlbedo;
		indirectSpecular *= sheenEnergyComp;
		indirectDiffuse *= sheenEnergyComp;
	#endif
	reflectedLight.indirectSpecular += indirectSpecular;
	reflectedLight.indirectDiffuse += indirectDiffuse;
}
#define RE_Direct				RE_Direct_Physical
#define RE_Direct_RectArea		RE_Direct_RectArea_Physical
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Physical
#define RE_IndirectSpecular		RE_IndirectSpecular_Physical
float computeSpecularOcclusion( const in float dotNV, const in float ambientOcclusion, const in float roughness ) {
	return saturate( pow( dotNV + ambientOcclusion, exp2( - 16.0 * roughness - 1.0 ) ) - 1.0 + ambientOcclusion );
}`,lights_fragment_begin:`
vec3 geometryPosition = - vViewPosition;
vec3 geometryNormal = normal;
vec3 geometryViewDir = ( isOrthographic ) ? vec3( 0, 0, 1 ) : normalize( vViewPosition );
vec3 geometryClearcoatNormal = vec3( 0.0 );
#ifdef USE_CLEARCOAT
	geometryClearcoatNormal = clearcoatNormal;
#endif
#ifdef USE_IRIDESCENCE
	float dotNVi = saturate( dot( normal, geometryViewDir ) );
	if ( material.iridescenceThickness == 0.0 ) {
		material.iridescence = 0.0;
	} else {
		material.iridescence = saturate( material.iridescence );
	}
	if ( material.iridescence > 0.0 ) {
		material.iridescenceFresnelDielectric = evalIridescence( 1.0, material.iridescenceIOR, dotNVi, material.iridescenceThickness, material.specularColor );
		material.iridescenceFresnelMetallic = evalIridescence( 1.0, material.iridescenceIOR, dotNVi, material.iridescenceThickness, material.diffuseColor );
		material.iridescenceFresnel = mix( material.iridescenceFresnelDielectric, material.iridescenceFresnelMetallic, material.metalness );
		material.iridescenceF0 = Schlick_to_F0( material.iridescenceFresnel, 1.0, dotNVi );
	}
#endif
IncidentLight directLight;
#if ( NUM_POINT_LIGHTS > 0 ) && defined( RE_Direct )
	PointLight pointLight;
	#if defined( USE_SHADOWMAP ) && NUM_POINT_LIGHT_SHADOWS > 0
	PointLightShadow pointLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHTS; i ++ ) {
		pointLight = pointLights[ i ];
		getPointLightInfo( pointLight, geometryPosition, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_POINT_LIGHT_SHADOWS ) && ( defined( SHADOWMAP_TYPE_PCF ) || defined( SHADOWMAP_TYPE_BASIC ) )
		pointLightShadow = pointLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getPointShadow( pointShadowMap[ i ], pointLightShadow.shadowMapSize, pointLightShadow.shadowIntensity, pointLightShadow.shadowBias, pointLightShadow.shadowRadius, vPointShadowCoord[ i ], pointLightShadow.shadowCameraNear, pointLightShadow.shadowCameraFar ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_SPOT_LIGHTS > 0 ) && defined( RE_Direct )
	SpotLight spotLight;
	vec4 spotColor;
	vec3 spotLightCoord;
	bool inSpotLightMap;
	#if defined( USE_SHADOWMAP ) && NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHTS; i ++ ) {
		spotLight = spotLights[ i ];
		getSpotLightInfo( spotLight, geometryPosition, directLight );
		#if ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#define SPOT_LIGHT_MAP_INDEX UNROLLED_LOOP_INDEX
		#elif ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		#define SPOT_LIGHT_MAP_INDEX NUM_SPOT_LIGHT_MAPS
		#else
		#define SPOT_LIGHT_MAP_INDEX ( UNROLLED_LOOP_INDEX - NUM_SPOT_LIGHT_SHADOWS + NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#endif
		#if ( SPOT_LIGHT_MAP_INDEX < NUM_SPOT_LIGHT_MAPS )
			spotLightCoord = vSpotLightCoord[ i ].xyz / vSpotLightCoord[ i ].w;
			inSpotLightMap = all( lessThan( abs( spotLightCoord * 2. - 1. ), vec3( 1.0 ) ) );
			spotColor = texture2D( spotLightMap[ SPOT_LIGHT_MAP_INDEX ], spotLightCoord.xy );
			directLight.color = inSpotLightMap ? directLight.color * spotColor.rgb : directLight.color;
		#endif
		#undef SPOT_LIGHT_MAP_INDEX
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		spotLightShadow = spotLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( spotShadowMap[ i ], spotLightShadow.shadowMapSize, spotLightShadow.shadowIntensity, spotLightShadow.shadowBias, spotLightShadow.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_DIR_LIGHTS > 0 ) && defined( RE_Direct )
	DirectionalLight directionalLight;
	#if defined( USE_SHADOWMAP ) && NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHTS; i ++ ) {
		directionalLight = directionalLights[ i ];
		getDirectionalLightInfo( directionalLight, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_DIR_LIGHT_SHADOWS )
		directionalLightShadow = directionalLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( directionalShadowMap[ i ], directionalLightShadow.shadowMapSize, directionalLightShadow.shadowIntensity, directionalLightShadow.shadowBias, directionalLightShadow.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_RECT_AREA_LIGHTS > 0 ) && defined( RE_Direct_RectArea )
	RectAreaLight rectAreaLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_RECT_AREA_LIGHTS; i ++ ) {
		rectAreaLight = rectAreaLights[ i ];
		RE_Direct_RectArea( rectAreaLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if defined( RE_IndirectDiffuse )
	vec3 iblIrradiance = vec3( 0.0 );
	vec3 irradiance = getAmbientLightIrradiance( ambientLightColor );
	#if defined( USE_LIGHT_PROBES )
		irradiance += getLightProbeIrradiance( lightProbe, geometryNormal );
	#endif
	#if ( NUM_HEMI_LIGHTS > 0 )
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_HEMI_LIGHTS; i ++ ) {
			irradiance += getHemisphereLightIrradiance( hemisphereLights[ i ], geometryNormal );
		}
		#pragma unroll_loop_end
	#endif
	#ifdef USE_LIGHT_PROBES_GRID
		vec3 probeWorldPos = ( ( vec4( geometryPosition, 1.0 ) - viewMatrix[ 3 ] ) * viewMatrix ).xyz;
		vec3 probeWorldNormal = transformNormalByInverseViewMatrix( geometryNormal, viewMatrix );
		irradiance += getLightProbeGridIrradiance( probeWorldPos, probeWorldNormal );
	#endif
#endif
#if defined( RE_IndirectSpecular )
	vec3 radiance = vec3( 0.0 );
	vec3 clearcoatRadiance = vec3( 0.0 );
#endif`,lights_fragment_maps:`#if defined( RE_IndirectDiffuse )
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
		vec3 lightMapIrradiance = lightMapTexel.rgb * lightMapIntensity;
		irradiance += lightMapIrradiance;
	#endif
	#if defined( USE_ENVMAP ) && defined( ENVMAP_TYPE_CUBE_UV )
		#if defined( STANDARD ) || defined( LAMBERT ) || defined( PHONG )
			iblIrradiance += getIBLIrradiance( geometryNormal );
		#endif
	#endif
#endif
#if defined( USE_ENVMAP ) && defined( RE_IndirectSpecular )
	#ifdef USE_ANISOTROPY
		radiance += getIBLAnisotropyRadiance( geometryViewDir, geometryNormal, material.roughness, material.anisotropyB, material.anisotropy );
	#else
		radiance += getIBLRadiance( geometryViewDir, geometryNormal, material.roughness );
	#endif
	#ifdef USE_CLEARCOAT
		clearcoatRadiance += getIBLRadiance( geometryViewDir, geometryClearcoatNormal, material.clearcoatRoughness );
	#endif
#endif`,lights_fragment_end:`#if defined( RE_IndirectDiffuse )
	#if defined( LAMBERT ) || defined( PHONG )
		irradiance += iblIrradiance;
	#endif
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,lightprobes_pars_fragment:`#ifdef USE_LIGHT_PROBES_GRID
uniform highp sampler3D probesSH;
uniform vec3 probesMin;
uniform vec3 probesMax;
uniform vec3 probesResolution;
vec3 getLightProbeGridIrradiance( vec3 worldPos, vec3 worldNormal ) {
	vec3 res = probesResolution;
	vec3 gridRange = probesMax - probesMin;
	vec3 resMinusOne = res - 1.0;
	vec3 probeSpacing = gridRange / resMinusOne;
	vec3 samplePos = worldPos + worldNormal * probeSpacing * 0.5;
	vec3 uvw = clamp( ( samplePos - probesMin ) / gridRange, 0.0, 1.0 );
	uvw = uvw * resMinusOne / res + 0.5 / res;
	float nz          = res.z;
	float paddedSlices = nz + 2.0;
	float atlasDepth  = 7.0 * paddedSlices;
	float uvZBase     = uvw.z * nz + 1.0;
	vec4 s0 = texture( probesSH, vec3( uvw.xy, ( uvZBase                       ) / atlasDepth ) );
	vec4 s1 = texture( probesSH, vec3( uvw.xy, ( uvZBase +       paddedSlices   ) / atlasDepth ) );
	vec4 s2 = texture( probesSH, vec3( uvw.xy, ( uvZBase + 2.0 * paddedSlices   ) / atlasDepth ) );
	vec4 s3 = texture( probesSH, vec3( uvw.xy, ( uvZBase + 3.0 * paddedSlices   ) / atlasDepth ) );
	vec4 s4 = texture( probesSH, vec3( uvw.xy, ( uvZBase + 4.0 * paddedSlices   ) / atlasDepth ) );
	vec4 s5 = texture( probesSH, vec3( uvw.xy, ( uvZBase + 5.0 * paddedSlices   ) / atlasDepth ) );
	vec4 s6 = texture( probesSH, vec3( uvw.xy, ( uvZBase + 6.0 * paddedSlices   ) / atlasDepth ) );
	vec3 c0 = s0.xyz;
	vec3 c1 = vec3( s0.w, s1.xy );
	vec3 c2 = vec3( s1.zw, s2.x );
	vec3 c3 = s2.yzw;
	vec3 c4 = s3.xyz;
	vec3 c5 = vec3( s3.w, s4.xy );
	vec3 c6 = vec3( s4.zw, s5.x );
	vec3 c7 = s5.yzw;
	vec3 c8 = s6.xyz;
	float x = worldNormal.x, y = worldNormal.y, z = worldNormal.z;
	vec3 result = c0 * 0.886227;
	result += c1 * 2.0 * 0.511664 * y;
	result += c2 * 2.0 * 0.511664 * z;
	result += c3 * 2.0 * 0.511664 * x;
	result += c4 * 2.0 * 0.429043 * x * y;
	result += c5 * 2.0 * 0.429043 * y * z;
	result += c6 * ( 0.743125 * z * z - 0.247708 );
	result += c7 * 2.0 * 0.429043 * x * z;
	result += c8 * 0.429043 * ( x * x - y * y );
	return max( result, vec3( 0.0 ) );
}
#endif`,logdepthbuf_fragment:`#if defined( USE_LOGARITHMIC_DEPTH_BUFFER )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,logdepthbuf_pars_fragment:`#if defined( USE_LOGARITHMIC_DEPTH_BUFFER )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,logdepthbuf_pars_vertex:`#ifdef USE_LOGARITHMIC_DEPTH_BUFFER
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,logdepthbuf_vertex:`#ifdef USE_LOGARITHMIC_DEPTH_BUFFER
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,map_fragment:`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = sRGBTransferEOTF( sampledDiffuseColor );
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,map_pars_fragment:`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,map_particle_fragment:`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
	#if defined( USE_POINTS_UV )
		vec2 uv = vUv;
	#else
		vec2 uv = ( uvTransform * vec3( gl_PointCoord.x, 1.0 - gl_PointCoord.y, 1 ) ).xy;
	#endif
#endif
#ifdef USE_MAP
	diffuseColor *= texture2D( map, uv );
#endif
#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, uv ).g;
#endif`,map_particle_pars_fragment:`#if defined( USE_POINTS_UV )
	varying vec2 vUv;
#else
	#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
		uniform mat3 uvTransform;
	#endif
#endif
#ifdef USE_MAP
	uniform sampler2D map;
#endif
#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,metalnessmap_fragment:`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,metalnessmap_pars_fragment:`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,morphinstance_vertex:`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,morphcolor_vertex:`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,morphnormal_vertex:`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,morphtarget_pars_vertex:`#ifdef USE_MORPHTARGETS
	#ifndef USE_INSTANCING_MORPH
		uniform float morphTargetBaseInfluence;
		uniform float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	#endif
	uniform sampler2DArray morphTargetsTexture;
	uniform ivec2 morphTargetsTextureSize;
	vec4 getMorph( const in int vertexIndex, const in int morphTargetIndex, const in int offset ) {
		int texelIndex = vertexIndex * MORPHTARGETS_TEXTURE_STRIDE + offset;
		int y = texelIndex / morphTargetsTextureSize.x;
		int x = texelIndex - y * morphTargetsTextureSize.x;
		ivec3 morphUV = ivec3( x, y, morphTargetIndex );
		return texelFetch( morphTargetsTexture, morphUV, 0 );
	}
#endif`,morphtarget_vertex:`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,normal_fragment_begin:`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
#ifdef FLAT_SHADED
	vec3 fdx = dFdx( vViewPosition );
	vec3 fdy = dFdy( vViewPosition );
	vec3 normal = normalize( cross( fdx, fdy ) );
#else
	vec3 normal = normalize( vNormal );
	#ifdef DOUBLE_SIDED
		normal *= faceDirection;
	#endif
#endif
#if defined( USE_NORMALMAP_TANGENTSPACE ) || defined( USE_CLEARCOAT_NORMALMAP ) || defined( USE_ANISOTROPY )
	#ifdef USE_TANGENT
		mat3 tbn = mat3( normalize( vTangent ), normalize( vBitangent ), normal );
	#else
		mat3 tbn = getTangentFrame( - vViewPosition, normal,
		#if defined( USE_NORMALMAP )
			vNormalMapUv
		#elif defined( USE_CLEARCOAT_NORMALMAP )
			vClearcoatNormalMapUv
		#else
			vUv
		#endif
		);
	#endif
	#ifdef DOUBLE_SIDED
		tbn[0] *= faceDirection;
		tbn[1] *= faceDirection;
	#endif
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	#ifdef USE_TANGENT
		mat3 tbn2 = mat3( normalize( vTangent ), normalize( vBitangent ), normal );
	#else
		mat3 tbn2 = getTangentFrame( - vViewPosition, normal, vClearcoatNormalMapUv );
	#endif
	#ifdef DOUBLE_SIDED
		tbn2[0] *= faceDirection;
		tbn2[1] *= faceDirection;
	#endif
#endif
vec3 nonPerturbedNormal = normal;`,normal_fragment_maps:`#ifdef USE_NORMALMAP_OBJECTSPACE
	normal = texture2D( normalMap, vNormalMapUv ).xyz * 2.0 - 1.0;
	#ifdef FLIP_SIDED
		normal = - normal;
	#endif
	#ifdef DOUBLE_SIDED
		normal = normal * faceDirection;
	#endif
	normal = normalize( normalMatrix * normal );
#elif defined( USE_NORMALMAP_TANGENTSPACE )
	vec3 mapN = texture2D( normalMap, vNormalMapUv ).xyz * 2.0 - 1.0;
	#if defined( USE_PACKED_NORMALMAP )
		mapN = vec3( mapN.xy, sqrt( saturate( 1.0 - dot( mapN.xy, mapN.xy ) ) ) );
	#endif
	mapN.xy *= normalScale;
	normal = normalize( tbn * mapN );
#elif defined( USE_BUMPMAP )
	normal = perturbNormalArb( - vViewPosition, normal, dHdxy_fwd(), faceDirection );
#endif`,normal_pars_fragment:`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,normal_pars_vertex:`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,normal_vertex:`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
		#ifdef FLIP_SIDED
			vBitangent = - vBitangent;
		#endif
	#endif
#endif`,normalmap_pars_fragment:`#ifdef USE_NORMALMAP
	uniform sampler2D normalMap;
	uniform vec2 normalScale;
#endif
#ifdef USE_NORMALMAP_OBJECTSPACE
	uniform mat3 normalMatrix;
#endif
#if ! defined ( USE_TANGENT ) && ( defined ( USE_NORMALMAP_TANGENTSPACE ) || defined ( USE_CLEARCOAT_NORMALMAP ) || defined( USE_ANISOTROPY ) )
	mat3 getTangentFrame( vec3 eye_pos, vec3 surf_norm, vec2 uv ) {
		vec3 q0 = dFdx( eye_pos.xyz );
		vec3 q1 = dFdy( eye_pos.xyz );
		vec2 st0 = dFdx( uv.st );
		vec2 st1 = dFdy( uv.st );
		vec3 N = surf_norm;
		vec3 q1perp = cross( q1, N );
		vec3 q0perp = cross( N, q0 );
		vec3 T = q1perp * st0.x + q0perp * st1.x;
		vec3 B = q1perp * st0.y + q0perp * st1.y;
		float det = max( dot( T, T ), dot( B, B ) );
		float scale = ( det == 0.0 ) ? 0.0 : inversesqrt( det );
		return mat3( T * scale, B * scale, N );
	}
#endif`,clearcoat_normal_fragment_begin:`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,clearcoat_normal_fragment_maps:`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,clearcoat_pars_fragment:`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,iridescence_pars_fragment:`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,opaque_fragment:`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,packing:`vec3 packNormalToRGB( const in vec3 normal ) {
	return normalize( normal ) * 0.5 + 0.5;
}
vec3 unpackRGBToNormal( const in vec3 rgb ) {
	return 2.0 * rgb.xyz - 1.0;
}
const float PackUpscale = 256. / 255.;const float UnpackDownscale = 255. / 256.;const float ShiftRight8 = 1. / 256.;
const float Inv255 = 1. / 255.;
const vec4 PackFactors = vec4( 1.0, 256.0, 256.0 * 256.0, 256.0 * 256.0 * 256.0 );
const vec2 UnpackFactors2 = vec2( UnpackDownscale, 1.0 / PackFactors.g );
const vec3 UnpackFactors3 = vec3( UnpackDownscale / PackFactors.rg, 1.0 / PackFactors.b );
const vec4 UnpackFactors4 = vec4( UnpackDownscale / PackFactors.rgb, 1.0 / PackFactors.a );
vec4 packDepthToRGBA( const in float v ) {
	if( v <= 0.0 )
		return vec4( 0., 0., 0., 0. );
	if( v >= 1.0 )
		return vec4( 1., 1., 1., 1. );
	float vuf;
	float af = modf( v * PackFactors.a, vuf );
	float bf = modf( vuf * ShiftRight8, vuf );
	float gf = modf( vuf * ShiftRight8, vuf );
	return vec4( vuf * Inv255, gf * PackUpscale, bf * PackUpscale, af );
}
vec3 packDepthToRGB( const in float v ) {
	if( v <= 0.0 )
		return vec3( 0., 0., 0. );
	if( v >= 1.0 )
		return vec3( 1., 1., 1. );
	float vuf;
	float bf = modf( v * PackFactors.b, vuf );
	float gf = modf( vuf * ShiftRight8, vuf );
	return vec3( vuf * Inv255, gf * PackUpscale, bf );
}
vec2 packDepthToRG( const in float v ) {
	if( v <= 0.0 )
		return vec2( 0., 0. );
	if( v >= 1.0 )
		return vec2( 1., 1. );
	float vuf;
	float gf = modf( v * 256., vuf );
	return vec2( vuf * Inv255, gf );
}
float unpackRGBAToDepth( const in vec4 v ) {
	return dot( v, UnpackFactors4 );
}
float unpackRGBToDepth( const in vec3 v ) {
	return dot( v, UnpackFactors3 );
}
float unpackRGToDepth( const in vec2 v ) {
	return v.r * UnpackFactors2.r + v.g * UnpackFactors2.g;
}
vec4 pack2HalfToRGBA( const in vec2 v ) {
	vec4 r = vec4( v.x, fract( v.x * 255.0 ), v.y, fract( v.y * 255.0 ) );
	return vec4( r.x - r.y / 255.0, r.y, r.z - r.w / 255.0, r.w );
}
vec2 unpackRGBATo2Half( const in vec4 v ) {
	return vec2( v.x + ( v.y / 255.0 ), v.z + ( v.w / 255.0 ) );
}
float viewZToOrthographicDepth( const in float viewZ, const in float near, const in float far ) {
	return ( viewZ + near ) / ( near - far );
}
float orthographicDepthToViewZ( const in float depth, const in float near, const in float far ) {
	#ifdef USE_REVERSED_DEPTH_BUFFER
	
		return depth * ( far - near ) - far;
	#else
		return depth * ( near - far ) - near;
	#endif
}
float viewZToPerspectiveDepth( const in float viewZ, const in float near, const in float far ) {
	return ( ( near + viewZ ) * far ) / ( ( far - near ) * viewZ );
}
float perspectiveDepthToViewZ( const in float depth, const in float near, const in float far ) {
	
	#ifdef USE_REVERSED_DEPTH_BUFFER
		return ( near * far ) / ( ( near - far ) * depth - near );
	#else
		return ( near * far ) / ( ( far - near ) * depth - far );
	#endif
}`,premultiplied_alpha_fragment:`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,project_vertex:`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,dithering_fragment:`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,dithering_pars_fragment:`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,roughnessmap_fragment:`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,roughnessmap_pars_fragment:`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,shadowmap_pars_fragment:`#if NUM_SPOT_LIGHT_COORDS > 0
	varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#if NUM_SPOT_LIGHT_MAPS > 0
	uniform sampler2D spotLightMap[ NUM_SPOT_LIGHT_MAPS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		#if defined( SHADOWMAP_TYPE_PCF )
			uniform sampler2DShadow directionalShadowMap[ NUM_DIR_LIGHT_SHADOWS ];
		#else
			uniform sampler2D directionalShadowMap[ NUM_DIR_LIGHT_SHADOWS ];
		#endif
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		#if defined( SHADOWMAP_TYPE_PCF )
			uniform sampler2DShadow spotShadowMap[ NUM_SPOT_LIGHT_SHADOWS ];
		#else
			uniform sampler2D spotShadowMap[ NUM_SPOT_LIGHT_SHADOWS ];
		#endif
		struct SpotLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		#if defined( SHADOWMAP_TYPE_PCF )
			uniform samplerCubeShadow pointShadowMap[ NUM_POINT_LIGHT_SHADOWS ];
		#elif defined( SHADOWMAP_TYPE_BASIC )
			uniform samplerCube pointShadowMap[ NUM_POINT_LIGHT_SHADOWS ];
		#endif
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
	#if defined( SHADOWMAP_TYPE_PCF )
		float interleavedGradientNoise( vec2 position ) {
			return fract( 52.9829189 * fract( dot( position, vec2( 0.06711056, 0.00583715 ) ) ) );
		}
		vec2 vogelDiskSample( int sampleIndex, int samplesCount, float phi ) {
			const float goldenAngle = 2.399963229728653;
			float r = sqrt( ( float( sampleIndex ) + 0.5 ) / float( samplesCount ) );
			float theta = float( sampleIndex ) * goldenAngle + phi;
			return vec2( cos( theta ), sin( theta ) ) * r;
		}
	#endif
	#if defined( SHADOWMAP_TYPE_PCF )
		float getShadow( sampler2DShadow shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord ) {
			float shadow = 1.0;
			shadowCoord.xyz /= shadowCoord.w;
			shadowCoord.z += shadowBias;
			bool inFrustum = shadowCoord.x >= 0.0 && shadowCoord.x <= 1.0 && shadowCoord.y >= 0.0 && shadowCoord.y <= 1.0;
			bool frustumTest = inFrustum && shadowCoord.z <= 1.0;
			if ( frustumTest ) {
				vec2 texelSize = vec2( 1.0 ) / shadowMapSize;
				float radius = shadowRadius * texelSize.x;
				float phi = interleavedGradientNoise( gl_FragCoord.xy ) * PI2;
				shadow = (
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 0, 5, phi ) * radius, shadowCoord.z ) ) +
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 1, 5, phi ) * radius, shadowCoord.z ) ) +
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 2, 5, phi ) * radius, shadowCoord.z ) ) +
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 3, 5, phi ) * radius, shadowCoord.z ) ) +
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 4, 5, phi ) * radius, shadowCoord.z ) )
				) * 0.2;
			}
			return mix( 1.0, shadow, shadowIntensity );
		}
	#elif defined( SHADOWMAP_TYPE_VSM )
		float getShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord ) {
			float shadow = 1.0;
			shadowCoord.xyz /= shadowCoord.w;
			#ifdef USE_REVERSED_DEPTH_BUFFER
				shadowCoord.z -= shadowBias;
			#else
				shadowCoord.z += shadowBias;
			#endif
			bool inFrustum = shadowCoord.x >= 0.0 && shadowCoord.x <= 1.0 && shadowCoord.y >= 0.0 && shadowCoord.y <= 1.0;
			bool frustumTest = inFrustum && shadowCoord.z <= 1.0;
			if ( frustumTest ) {
				vec2 distribution = texture2D( shadowMap, shadowCoord.xy ).rg;
				float mean = distribution.x;
				float variance = distribution.y * distribution.y;
				#ifdef USE_REVERSED_DEPTH_BUFFER
					float hard_shadow = step( mean, shadowCoord.z );
				#else
					float hard_shadow = step( shadowCoord.z, mean );
				#endif
				
				if ( hard_shadow == 1.0 ) {
					shadow = 1.0;
				} else {
					variance = max( variance, 0.0000001 );
					float d = shadowCoord.z - mean;
					float p_max = variance / ( variance + d * d );
					p_max = clamp( ( p_max - 0.3 ) / 0.65, 0.0, 1.0 );
					shadow = max( hard_shadow, p_max );
				}
			}
			return mix( 1.0, shadow, shadowIntensity );
		}
	#else
		float getShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord ) {
			float shadow = 1.0;
			shadowCoord.xyz /= shadowCoord.w;
			#ifdef USE_REVERSED_DEPTH_BUFFER
				shadowCoord.z -= shadowBias;
			#else
				shadowCoord.z += shadowBias;
			#endif
			bool inFrustum = shadowCoord.x >= 0.0 && shadowCoord.x <= 1.0 && shadowCoord.y >= 0.0 && shadowCoord.y <= 1.0;
			bool frustumTest = inFrustum && shadowCoord.z <= 1.0;
			if ( frustumTest ) {
				float depth = texture2D( shadowMap, shadowCoord.xy ).r;
				#ifdef USE_REVERSED_DEPTH_BUFFER
					shadow = step( depth, shadowCoord.z );
				#else
					shadow = step( shadowCoord.z, depth );
				#endif
			}
			return mix( 1.0, shadow, shadowIntensity );
		}
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
	#if defined( SHADOWMAP_TYPE_PCF )
	float getPointShadow( samplerCubeShadow shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord, float shadowCameraNear, float shadowCameraFar ) {
		float shadow = 1.0;
		vec3 lightToPosition = shadowCoord.xyz;
		vec3 bd3D = normalize( lightToPosition );
		vec3 absVec = abs( lightToPosition );
		float viewSpaceZ = max( max( absVec.x, absVec.y ), absVec.z );
		if ( viewSpaceZ - shadowCameraFar <= 0.0 && viewSpaceZ - shadowCameraNear >= 0.0 ) {
			#ifdef USE_REVERSED_DEPTH_BUFFER
				float dp = ( shadowCameraNear * ( shadowCameraFar - viewSpaceZ ) ) / ( viewSpaceZ * ( shadowCameraFar - shadowCameraNear ) );
				dp -= shadowBias;
			#else
				float dp = ( shadowCameraFar * ( viewSpaceZ - shadowCameraNear ) ) / ( viewSpaceZ * ( shadowCameraFar - shadowCameraNear ) );
				dp += shadowBias;
			#endif
			float texelSize = shadowRadius / shadowMapSize.x;
			vec3 absDir = abs( bd3D );
			vec3 tangent = absDir.x > absDir.z ? vec3( 0.0, 1.0, 0.0 ) : vec3( 1.0, 0.0, 0.0 );
			tangent = normalize( cross( bd3D, tangent ) );
			vec3 bitangent = cross( bd3D, tangent );
			float phi = interleavedGradientNoise( gl_FragCoord.xy ) * PI2;
			vec2 sample0 = vogelDiskSample( 0, 5, phi );
			vec2 sample1 = vogelDiskSample( 1, 5, phi );
			vec2 sample2 = vogelDiskSample( 2, 5, phi );
			vec2 sample3 = vogelDiskSample( 3, 5, phi );
			vec2 sample4 = vogelDiskSample( 4, 5, phi );
			shadow = (
				texture( shadowMap, vec4( bd3D + ( tangent * sample0.x + bitangent * sample0.y ) * texelSize, dp ) ) +
				texture( shadowMap, vec4( bd3D + ( tangent * sample1.x + bitangent * sample1.y ) * texelSize, dp ) ) +
				texture( shadowMap, vec4( bd3D + ( tangent * sample2.x + bitangent * sample2.y ) * texelSize, dp ) ) +
				texture( shadowMap, vec4( bd3D + ( tangent * sample3.x + bitangent * sample3.y ) * texelSize, dp ) ) +
				texture( shadowMap, vec4( bd3D + ( tangent * sample4.x + bitangent * sample4.y ) * texelSize, dp ) )
			) * 0.2;
		}
		return mix( 1.0, shadow, shadowIntensity );
	}
	#elif defined( SHADOWMAP_TYPE_BASIC )
	float getPointShadow( samplerCube shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord, float shadowCameraNear, float shadowCameraFar ) {
		float shadow = 1.0;
		vec3 lightToPosition = shadowCoord.xyz;
		vec3 absVec = abs( lightToPosition );
		float viewSpaceZ = max( max( absVec.x, absVec.y ), absVec.z );
		if ( viewSpaceZ - shadowCameraFar <= 0.0 && viewSpaceZ - shadowCameraNear >= 0.0 ) {
			float dp = ( shadowCameraFar * ( viewSpaceZ - shadowCameraNear ) ) / ( viewSpaceZ * ( shadowCameraFar - shadowCameraNear ) );
			dp += shadowBias;
			vec3 bd3D = normalize( lightToPosition );
			float depth = textureCube( shadowMap, bd3D ).r;
			#ifdef USE_REVERSED_DEPTH_BUFFER
				depth = 1.0 - depth;
			#endif
			shadow = step( dp, depth );
		}
		return mix( 1.0, shadow, shadowIntensity );
	}
	#endif
	#endif
#endif`,shadowmap_pars_vertex:`#if NUM_SPOT_LIGHT_COORDS > 0
	uniform mat4 spotLightMatrix[ NUM_SPOT_LIGHT_COORDS ];
	varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		uniform mat4 directionalShadowMatrix[ NUM_DIR_LIGHT_SHADOWS ];
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		struct SpotLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		uniform mat4 pointShadowMatrix[ NUM_POINT_LIGHT_SHADOWS ];
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
#endif`,shadowmap_vertex:`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
	#ifdef HAS_NORMAL
		vec3 shadowWorldNormal = transformNormalByInverseViewMatrix( transformedNormal, viewMatrix );
	#else
		vec3 shadowWorldNormal = vec3( 0.0 );
	#endif
	vec4 shadowWorldPosition;
#endif
#if defined( USE_SHADOWMAP )
	#if NUM_DIR_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * directionalLightShadows[ i ].shadowNormalBias, 0 );
			vDirectionalShadowCoord[ i ] = directionalShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * pointLightShadows[ i ].shadowNormalBias, 0 );
			vPointShadowCoord[ i ] = pointShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
#endif
#if NUM_SPOT_LIGHT_COORDS > 0
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_COORDS; i ++ ) {
		shadowWorldPosition = worldPosition;
		#if ( defined( USE_SHADOWMAP ) && UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
			shadowWorldPosition.xyz += shadowWorldNormal * spotLightShadows[ i ].shadowNormalBias;
		#endif
		vSpotLightCoord[ i ] = spotLightMatrix[ i ] * shadowWorldPosition;
	}
	#pragma unroll_loop_end
#endif`,shadowmask_pars_fragment:`float getShadowMask() {
	float shadow = 1.0;
	#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
		directionalLight = directionalLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( directionalShadowMap[ i ], directionalLight.shadowMapSize, directionalLight.shadowIntensity, directionalLight.shadowBias, directionalLight.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_SHADOWS; i ++ ) {
		spotLight = spotLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( spotShadowMap[ i ], spotLight.shadowMapSize, spotLight.shadowIntensity, spotLight.shadowBias, spotLight.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0 && ( defined( SHADOWMAP_TYPE_PCF ) || defined( SHADOWMAP_TYPE_BASIC ) )
	PointLightShadow pointLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
		pointLight = pointLightShadows[ i ];
		shadow *= receiveShadow ? getPointShadow( pointShadowMap[ i ], pointLight.shadowMapSize, pointLight.shadowIntensity, pointLight.shadowBias, pointLight.shadowRadius, vPointShadowCoord[ i ], pointLight.shadowCameraNear, pointLight.shadowCameraFar ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#endif
	return shadow;
}`,skinbase_vertex:`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,skinning_pars_vertex:`#ifdef USE_SKINNING
	uniform mat4 bindMatrix;
	uniform mat4 bindMatrixInverse;
	uniform highp sampler2D boneTexture;
	mat4 getBoneMatrix( const in float i ) {
		int size = textureSize( boneTexture, 0 ).x;
		int j = int( i ) * 4;
		int x = j % size;
		int y = j / size;
		vec4 v1 = texelFetch( boneTexture, ivec2( x, y ), 0 );
		vec4 v2 = texelFetch( boneTexture, ivec2( x + 1, y ), 0 );
		vec4 v3 = texelFetch( boneTexture, ivec2( x + 2, y ), 0 );
		vec4 v4 = texelFetch( boneTexture, ivec2( x + 3, y ), 0 );
		return mat4( v1, v2, v3, v4 );
	}
#endif`,skinning_vertex:`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,skinnormal_vertex:`#ifdef USE_SKINNING
	mat4 skinMatrix = mat4( 0.0 );
	skinMatrix += skinWeight.x * boneMatX;
	skinMatrix += skinWeight.y * boneMatY;
	skinMatrix += skinWeight.z * boneMatZ;
	skinMatrix += skinWeight.w * boneMatW;
	skinMatrix = bindMatrixInverse * skinMatrix * bindMatrix;
	objectNormal = vec4( skinMatrix * vec4( objectNormal, 0.0 ) ).xyz;
	#ifdef USE_TANGENT
		objectTangent = vec4( skinMatrix * vec4( objectTangent, 0.0 ) ).xyz;
	#endif
#endif`,specularmap_fragment:`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,specularmap_pars_fragment:`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,tonemapping_fragment:`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,tonemapping_pars_fragment:`#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
uniform float toneMappingExposure;
vec3 LinearToneMapping( vec3 color ) {
	return saturate( toneMappingExposure * color );
}
vec3 ReinhardToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	return saturate( color / ( vec3( 1.0 ) + color ) );
}
vec3 CineonToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	color = max( vec3( 0.0 ), color - 0.004 );
	return pow( ( color * ( 6.2 * color + 0.5 ) ) / ( color * ( 6.2 * color + 1.7 ) + 0.06 ), vec3( 2.2 ) );
}
vec3 RRTAndODTFit( vec3 v ) {
	vec3 a = v * ( v + 0.0245786 ) - 0.000090537;
	vec3 b = v * ( 0.983729 * v + 0.4329510 ) + 0.238081;
	return a / b;
}
vec3 ACESFilmicToneMapping( vec3 color ) {
	const mat3 ACESInputMat = mat3(
		vec3( 0.59719, 0.07600, 0.02840 ),		vec3( 0.35458, 0.90834, 0.13383 ),
		vec3( 0.04823, 0.01566, 0.83777 )
	);
	const mat3 ACESOutputMat = mat3(
		vec3(  1.60475, -0.10208, -0.00327 ),		vec3( -0.53108,  1.10813, -0.07276 ),
		vec3( -0.07367, -0.00605,  1.07602 )
	);
	color *= toneMappingExposure / 0.6;
	color = ACESInputMat * color;
	color = RRTAndODTFit( color );
	color = ACESOutputMat * color;
	return saturate( color );
}
const mat3 LINEAR_REC2020_TO_LINEAR_SRGB = mat3(
	vec3( 1.6605, - 0.1246, - 0.0182 ),
	vec3( - 0.5876, 1.1329, - 0.1006 ),
	vec3( - 0.0728, - 0.0083, 1.1187 )
);
const mat3 LINEAR_SRGB_TO_LINEAR_REC2020 = mat3(
	vec3( 0.6274, 0.0691, 0.0164 ),
	vec3( 0.3293, 0.9195, 0.0880 ),
	vec3( 0.0433, 0.0113, 0.8956 )
);
vec3 agxDefaultContrastApprox( vec3 x ) {
	vec3 x2 = x * x;
	vec3 x4 = x2 * x2;
	return + 15.5 * x4 * x2
		- 40.14 * x4 * x
		+ 31.96 * x4
		- 6.868 * x2 * x
		+ 0.4298 * x2
		+ 0.1191 * x
		- 0.00232;
}
vec3 AgXToneMapping( vec3 color ) {
	const mat3 AgXInsetMatrix = mat3(
		vec3( 0.856627153315983, 0.137318972929847, 0.11189821299995 ),
		vec3( 0.0951212405381588, 0.761241990602591, 0.0767994186031903 ),
		vec3( 0.0482516061458583, 0.101439036467562, 0.811302368396859 )
	);
	const mat3 AgXOutsetMatrix = mat3(
		vec3( 1.1271005818144368, - 0.1413297634984383, - 0.14132976349843826 ),
		vec3( - 0.11060664309660323, 1.157823702216272, - 0.11060664309660294 ),
		vec3( - 0.016493938717834573, - 0.016493938717834257, 1.2519364065950405 )
	);
	const float AgxMinEv = - 12.47393;	const float AgxMaxEv = 4.026069;
	color *= toneMappingExposure;
	color = LINEAR_SRGB_TO_LINEAR_REC2020 * color;
	color = AgXInsetMatrix * color;
	color = max( color, 1e-10 );	color = log2( color );
	color = ( color - AgxMinEv ) / ( AgxMaxEv - AgxMinEv );
	color = clamp( color, 0.0, 1.0 );
	color = agxDefaultContrastApprox( color );
	color = AgXOutsetMatrix * color;
	color = pow( max( vec3( 0.0 ), color ), vec3( 2.2 ) );
	color = LINEAR_REC2020_TO_LINEAR_SRGB * color;
	color = clamp( color, 0.0, 1.0 );
	return color;
}
vec3 NeutralToneMapping( vec3 color ) {
	const float StartCompression = 0.8 - 0.04;
	const float Desaturation = 0.15;
	color *= toneMappingExposure;
	float x = min( color.r, min( color.g, color.b ) );
	float offset = x < 0.08 ? x - 6.25 * x * x : 0.04;
	color -= offset;
	float peak = max( color.r, max( color.g, color.b ) );
	if ( peak < StartCompression ) return color;
	float d = 1. - StartCompression;
	float newPeak = 1. - d * d / ( peak + d - StartCompression );
	color *= newPeak / peak;
	float g = 1. - 1. / ( Desaturation * ( peak - newPeak ) + 1. );
	return mix( color, vec3( newPeak ), g );
}
vec3 CustomToneMapping( vec3 color ) { return color; }`,transmission_fragment:`#ifdef USE_TRANSMISSION
	material.transmission = transmission;
	material.transmissionAlpha = 1.0;
	material.thickness = thickness;
	material.attenuationDistance = attenuationDistance;
	material.attenuationColor = attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		material.transmission *= texture2D( transmissionMap, vTransmissionMapUv ).r;
	#endif
	#ifdef USE_THICKNESSMAP
		material.thickness *= texture2D( thicknessMap, vThicknessMapUv ).g;
	#endif
	vec3 pos = vWorldPosition;
	vec3 v = normalize( cameraPosition - pos );
	vec3 n = transformNormalByInverseViewMatrix( normal, viewMatrix );
	vec4 transmitted = getIBLVolumeRefraction(
		n, v, material.roughness, material.diffuseContribution, material.specularColorBlended, material.specularF90,
		pos, modelMatrix, viewMatrix, projectionMatrix, material.dispersion, material.ior, material.thickness,
		material.attenuationColor, material.attenuationDistance );
	material.transmissionAlpha = mix( material.transmissionAlpha, transmitted.a, material.transmission );
	totalDiffuse = mix( totalDiffuse, transmitted.rgb, material.transmission );
#endif`,transmission_pars_fragment:`#ifdef USE_TRANSMISSION
	uniform float transmission;
	uniform float thickness;
	uniform float attenuationDistance;
	uniform vec3 attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		uniform sampler2D transmissionMap;
	#endif
	#ifdef USE_THICKNESSMAP
		uniform sampler2D thicknessMap;
	#endif
	uniform vec2 transmissionSamplerSize;
	uniform sampler2D transmissionSamplerMap;
	uniform mat4 modelMatrix;
	uniform mat4 projectionMatrix;
	varying vec3 vWorldPosition;
	float w0( float a ) {
		return ( 1.0 / 6.0 ) * ( a * ( a * ( - a + 3.0 ) - 3.0 ) + 1.0 );
	}
	float w1( float a ) {
		return ( 1.0 / 6.0 ) * ( a *  a * ( 3.0 * a - 6.0 ) + 4.0 );
	}
	float w2( float a ){
		return ( 1.0 / 6.0 ) * ( a * ( a * ( - 3.0 * a + 3.0 ) + 3.0 ) + 1.0 );
	}
	float w3( float a ) {
		return ( 1.0 / 6.0 ) * ( a * a * a );
	}
	float g0( float a ) {
		return w0( a ) + w1( a );
	}
	float g1( float a ) {
		return w2( a ) + w3( a );
	}
	float h0( float a ) {
		return - 1.0 + w1( a ) / ( w0( a ) + w1( a ) );
	}
	float h1( float a ) {
		return 1.0 + w3( a ) / ( w2( a ) + w3( a ) );
	}
	vec4 bicubic( sampler2D tex, vec2 uv, vec4 texelSize, float lod ) {
		uv = uv * texelSize.zw + 0.5;
		vec2 iuv = floor( uv );
		vec2 fuv = fract( uv );
		float g0x = g0( fuv.x );
		float g1x = g1( fuv.x );
		float h0x = h0( fuv.x );
		float h1x = h1( fuv.x );
		float h0y = h0( fuv.y );
		float h1y = h1( fuv.y );
		vec2 p0 = ( vec2( iuv.x + h0x, iuv.y + h0y ) - 0.5 ) * texelSize.xy;
		vec2 p1 = ( vec2( iuv.x + h1x, iuv.y + h0y ) - 0.5 ) * texelSize.xy;
		vec2 p2 = ( vec2( iuv.x + h0x, iuv.y + h1y ) - 0.5 ) * texelSize.xy;
		vec2 p3 = ( vec2( iuv.x + h1x, iuv.y + h1y ) - 0.5 ) * texelSize.xy;
		return g0( fuv.y ) * ( g0x * textureLod( tex, p0, lod ) + g1x * textureLod( tex, p1, lod ) ) +
			g1( fuv.y ) * ( g0x * textureLod( tex, p2, lod ) + g1x * textureLod( tex, p3, lod ) );
	}
	vec4 textureBicubic( sampler2D sampler, vec2 uv, float lod ) {
		vec2 fLodSize = vec2( textureSize( sampler, int( lod ) ) );
		vec2 cLodSize = vec2( textureSize( sampler, int( lod + 1.0 ) ) );
		vec2 fLodSizeInv = 1.0 / fLodSize;
		vec2 cLodSizeInv = 1.0 / cLodSize;
		vec4 fSample = bicubic( sampler, uv, vec4( fLodSizeInv, fLodSize ), floor( lod ) );
		vec4 cSample = bicubic( sampler, uv, vec4( cLodSizeInv, cLodSize ), ceil( lod ) );
		return mix( fSample, cSample, fract( lod ) );
	}
	vec3 getVolumeTransmissionRay( const in vec3 n, const in vec3 v, const in float thickness, const in float ior, const in mat4 modelMatrix ) {
		vec3 refractionVector = refract( - v, normalize( n ), 1.0 / ior );
		vec3 modelScale;
		modelScale.x = length( vec3( modelMatrix[ 0 ].xyz ) );
		modelScale.y = length( vec3( modelMatrix[ 1 ].xyz ) );
		modelScale.z = length( vec3( modelMatrix[ 2 ].xyz ) );
		return normalize( refractionVector ) * thickness * modelScale;
	}
	float applyIorToRoughness( const in float roughness, const in float ior ) {
		return roughness * clamp( ior * 2.0 - 2.0, 0.0, 1.0 );
	}
	vec4 getTransmissionSample( const in vec2 fragCoord, const in float roughness, const in float ior ) {
		float lod = log2( transmissionSamplerSize.x ) * applyIorToRoughness( roughness, ior );
		return textureBicubic( transmissionSamplerMap, fragCoord.xy, lod );
	}
	vec3 volumeAttenuation( const in float transmissionDistance, const in vec3 attenuationColor, const in float attenuationDistance ) {
		if ( isinf( attenuationDistance ) ) {
			return vec3( 1.0 );
		} else {
			vec3 attenuationCoefficient = -log( attenuationColor ) / attenuationDistance;
			vec3 transmittance = exp( - attenuationCoefficient * transmissionDistance );			return transmittance;
		}
	}
	vec4 getIBLVolumeRefraction( const in vec3 n, const in vec3 v, const in float roughness, const in vec3 diffuseColor,
		const in vec3 specularColor, const in float specularF90, const in vec3 position, const in mat4 modelMatrix,
		const in mat4 viewMatrix, const in mat4 projMatrix, const in float dispersion, const in float ior, const in float thickness,
		const in vec3 attenuationColor, const in float attenuationDistance ) {
		vec4 transmittedLight;
		vec3 transmittance;
		#ifdef USE_DISPERSION
			float halfSpread = ( ior - 1.0 ) * 0.025 * dispersion;
			vec3 iors = vec3( ior - halfSpread, ior, ior + halfSpread );
			for ( int i = 0; i < 3; i ++ ) {
				vec3 transmissionRay = getVolumeTransmissionRay( n, v, thickness, iors[ i ], modelMatrix );
				vec3 refractedRayExit = position + transmissionRay;
				vec4 ndcPos = projMatrix * viewMatrix * vec4( refractedRayExit, 1.0 );
				vec2 refractionCoords = ndcPos.xy / ndcPos.w;
				refractionCoords += 1.0;
				refractionCoords /= 2.0;
				vec4 transmissionSample = getTransmissionSample( refractionCoords, roughness, iors[ i ] );
				transmittedLight[ i ] = transmissionSample[ i ];
				transmittedLight.a += transmissionSample.a;
				transmittance[ i ] = diffuseColor[ i ] * volumeAttenuation( length( transmissionRay ), attenuationColor, attenuationDistance )[ i ];
			}
			transmittedLight.a /= 3.0;
		#else
			vec3 transmissionRay = getVolumeTransmissionRay( n, v, thickness, ior, modelMatrix );
			vec3 refractedRayExit = position + transmissionRay;
			vec4 ndcPos = projMatrix * viewMatrix * vec4( refractedRayExit, 1.0 );
			vec2 refractionCoords = ndcPos.xy / ndcPos.w;
			refractionCoords += 1.0;
			refractionCoords /= 2.0;
			transmittedLight = getTransmissionSample( refractionCoords, roughness, ior );
			transmittance = diffuseColor * volumeAttenuation( length( transmissionRay ), attenuationColor, attenuationDistance );
		#endif
		vec3 attenuatedColor = transmittance * transmittedLight.rgb;
		vec3 F = EnvironmentBRDF( n, v, specularColor, specularF90, roughness );
		float transmittanceFactor = ( transmittance.r + transmittance.g + transmittance.b ) / 3.0;
		return vec4( ( 1.0 - F ) * attenuatedColor, 1.0 - ( 1.0 - transmittedLight.a ) * transmittanceFactor );
	}
#endif`,uv_pars_fragment:`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	varying vec2 vUv;
#endif
#ifdef USE_MAP
	varying vec2 vMapUv;
#endif
#ifdef USE_ALPHAMAP
	varying vec2 vAlphaMapUv;
#endif
#ifdef USE_LIGHTMAP
	varying vec2 vLightMapUv;
#endif
#ifdef USE_AOMAP
	varying vec2 vAoMapUv;
#endif
#ifdef USE_BUMPMAP
	varying vec2 vBumpMapUv;
#endif
#ifdef USE_NORMALMAP
	varying vec2 vNormalMapUv;
#endif
#ifdef USE_EMISSIVEMAP
	varying vec2 vEmissiveMapUv;
#endif
#ifdef USE_METALNESSMAP
	varying vec2 vMetalnessMapUv;
#endif
#ifdef USE_ROUGHNESSMAP
	varying vec2 vRoughnessMapUv;
#endif
#ifdef USE_ANISOTROPYMAP
	varying vec2 vAnisotropyMapUv;
#endif
#ifdef USE_CLEARCOATMAP
	varying vec2 vClearcoatMapUv;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	varying vec2 vClearcoatNormalMapUv;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	varying vec2 vClearcoatRoughnessMapUv;
#endif
#ifdef USE_IRIDESCENCEMAP
	varying vec2 vIridescenceMapUv;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	varying vec2 vIridescenceThicknessMapUv;
#endif
#ifdef USE_SHEEN_COLORMAP
	varying vec2 vSheenColorMapUv;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	varying vec2 vSheenRoughnessMapUv;
#endif
#ifdef USE_SPECULARMAP
	varying vec2 vSpecularMapUv;
#endif
#ifdef USE_SPECULAR_COLORMAP
	varying vec2 vSpecularColorMapUv;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	varying vec2 vSpecularIntensityMapUv;
#endif
#ifdef USE_TRANSMISSIONMAP
	uniform mat3 transmissionMapTransform;
	varying vec2 vTransmissionMapUv;
#endif
#ifdef USE_THICKNESSMAP
	uniform mat3 thicknessMapTransform;
	varying vec2 vThicknessMapUv;
#endif`,uv_pars_vertex:`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	varying vec2 vUv;
#endif
#ifdef USE_MAP
	uniform mat3 mapTransform;
	varying vec2 vMapUv;
#endif
#ifdef USE_ALPHAMAP
	uniform mat3 alphaMapTransform;
	varying vec2 vAlphaMapUv;
#endif
#ifdef USE_LIGHTMAP
	uniform mat3 lightMapTransform;
	varying vec2 vLightMapUv;
#endif
#ifdef USE_AOMAP
	uniform mat3 aoMapTransform;
	varying vec2 vAoMapUv;
#endif
#ifdef USE_BUMPMAP
	uniform mat3 bumpMapTransform;
	varying vec2 vBumpMapUv;
#endif
#ifdef USE_NORMALMAP
	uniform mat3 normalMapTransform;
	varying vec2 vNormalMapUv;
#endif
#ifdef USE_DISPLACEMENTMAP
	uniform mat3 displacementMapTransform;
	varying vec2 vDisplacementMapUv;
#endif
#ifdef USE_EMISSIVEMAP
	uniform mat3 emissiveMapTransform;
	varying vec2 vEmissiveMapUv;
#endif
#ifdef USE_METALNESSMAP
	uniform mat3 metalnessMapTransform;
	varying vec2 vMetalnessMapUv;
#endif
#ifdef USE_ROUGHNESSMAP
	uniform mat3 roughnessMapTransform;
	varying vec2 vRoughnessMapUv;
#endif
#ifdef USE_ANISOTROPYMAP
	uniform mat3 anisotropyMapTransform;
	varying vec2 vAnisotropyMapUv;
#endif
#ifdef USE_CLEARCOATMAP
	uniform mat3 clearcoatMapTransform;
	varying vec2 vClearcoatMapUv;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform mat3 clearcoatNormalMapTransform;
	varying vec2 vClearcoatNormalMapUv;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform mat3 clearcoatRoughnessMapTransform;
	varying vec2 vClearcoatRoughnessMapUv;
#endif
#ifdef USE_SHEEN_COLORMAP
	uniform mat3 sheenColorMapTransform;
	varying vec2 vSheenColorMapUv;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	uniform mat3 sheenRoughnessMapTransform;
	varying vec2 vSheenRoughnessMapUv;
#endif
#ifdef USE_IRIDESCENCEMAP
	uniform mat3 iridescenceMapTransform;
	varying vec2 vIridescenceMapUv;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform mat3 iridescenceThicknessMapTransform;
	varying vec2 vIridescenceThicknessMapUv;
#endif
#ifdef USE_SPECULARMAP
	uniform mat3 specularMapTransform;
	varying vec2 vSpecularMapUv;
#endif
#ifdef USE_SPECULAR_COLORMAP
	uniform mat3 specularColorMapTransform;
	varying vec2 vSpecularColorMapUv;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	uniform mat3 specularIntensityMapTransform;
	varying vec2 vSpecularIntensityMapUv;
#endif
#ifdef USE_TRANSMISSIONMAP
	uniform mat3 transmissionMapTransform;
	varying vec2 vTransmissionMapUv;
#endif
#ifdef USE_THICKNESSMAP
	uniform mat3 thicknessMapTransform;
	varying vec2 vThicknessMapUv;
#endif`,uv_vertex:`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	vUv = vec3( uv, 1 ).xy;
#endif
#ifdef USE_MAP
	vMapUv = ( mapTransform * vec3( MAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ALPHAMAP
	vAlphaMapUv = ( alphaMapTransform * vec3( ALPHAMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_LIGHTMAP
	vLightMapUv = ( lightMapTransform * vec3( LIGHTMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_AOMAP
	vAoMapUv = ( aoMapTransform * vec3( AOMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_BUMPMAP
	vBumpMapUv = ( bumpMapTransform * vec3( BUMPMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_NORMALMAP
	vNormalMapUv = ( normalMapTransform * vec3( NORMALMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_DISPLACEMENTMAP
	vDisplacementMapUv = ( displacementMapTransform * vec3( DISPLACEMENTMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_EMISSIVEMAP
	vEmissiveMapUv = ( emissiveMapTransform * vec3( EMISSIVEMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_METALNESSMAP
	vMetalnessMapUv = ( metalnessMapTransform * vec3( METALNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ROUGHNESSMAP
	vRoughnessMapUv = ( roughnessMapTransform * vec3( ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ANISOTROPYMAP
	vAnisotropyMapUv = ( anisotropyMapTransform * vec3( ANISOTROPYMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOATMAP
	vClearcoatMapUv = ( clearcoatMapTransform * vec3( CLEARCOATMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	vClearcoatNormalMapUv = ( clearcoatNormalMapTransform * vec3( CLEARCOAT_NORMALMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	vClearcoatRoughnessMapUv = ( clearcoatRoughnessMapTransform * vec3( CLEARCOAT_ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_IRIDESCENCEMAP
	vIridescenceMapUv = ( iridescenceMapTransform * vec3( IRIDESCENCEMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	vIridescenceThicknessMapUv = ( iridescenceThicknessMapTransform * vec3( IRIDESCENCE_THICKNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SHEEN_COLORMAP
	vSheenColorMapUv = ( sheenColorMapTransform * vec3( SHEEN_COLORMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	vSheenRoughnessMapUv = ( sheenRoughnessMapTransform * vec3( SHEEN_ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULARMAP
	vSpecularMapUv = ( specularMapTransform * vec3( SPECULARMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULAR_COLORMAP
	vSpecularColorMapUv = ( specularColorMapTransform * vec3( SPECULAR_COLORMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	vSpecularIntensityMapUv = ( specularIntensityMapTransform * vec3( SPECULAR_INTENSITYMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_TRANSMISSIONMAP
	vTransmissionMapUv = ( transmissionMapTransform * vec3( TRANSMISSIONMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_THICKNESSMAP
	vThicknessMapUv = ( thicknessMapTransform * vec3( THICKNESSMAP_UV, 1 ) ).xy;
#endif`,worldpos_vertex:`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`,background_vert:`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,background_frag:`uniform sampler2D t2D;
uniform float backgroundIntensity;
varying vec2 vUv;
void main() {
	vec4 texColor = texture2D( t2D, vUv );
	#ifdef DECODE_VIDEO_TEXTURE
		texColor = vec4( mix( pow( texColor.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), texColor.rgb * 0.0773993808, vec3( lessThanEqual( texColor.rgb, vec3( 0.04045 ) ) ) ), texColor.w );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,backgroundCube_vert:`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,backgroundCube_frag:`#ifdef ENVMAP_TYPE_CUBE
	uniform samplerCube envMap;
#elif defined( ENVMAP_TYPE_CUBE_UV )
	uniform sampler2D envMap;
#endif
uniform float backgroundBlurriness;
uniform float backgroundIntensity;
uniform mat3 backgroundRotation;
varying vec3 vWorldDirection;
#include <cube_uv_reflection_fragment>
void main() {
	#ifdef ENVMAP_TYPE_CUBE
		vec4 texColor = textureCube( envMap, backgroundRotation * vWorldDirection );
	#elif defined( ENVMAP_TYPE_CUBE_UV )
		vec4 texColor = textureCubeUV( envMap, backgroundRotation * vWorldDirection, backgroundBlurriness );
	#else
		vec4 texColor = vec4( 0.0, 0.0, 0.0, 1.0 );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,cube_vert:`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,cube_frag:`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,depth_vert:`#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
varying vec2 vHighPrecisionZW;
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <skinbase_vertex>
	#include <morphinstance_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vHighPrecisionZW = gl_Position.zw;
}`,depth_frag:`#if DEPTH_PACKING == 3200
	uniform float opacity;
#endif
#include <common>
#include <packing>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
varying vec2 vHighPrecisionZW;
void main() {
	vec4 diffuseColor = vec4( 1.0 );
	#include <clipping_planes_fragment>
	#if DEPTH_PACKING == 3200
		diffuseColor.a = opacity;
	#endif
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <logdepthbuf_fragment>
	#ifdef USE_REVERSED_DEPTH_BUFFER
		float fragCoordZ = vHighPrecisionZW[ 0 ] / vHighPrecisionZW[ 1 ];
	#else
		float fragCoordZ = 0.5 * vHighPrecisionZW[ 0 ] / vHighPrecisionZW[ 1 ] + 0.5;
	#endif
	#if DEPTH_PACKING == 3200
		gl_FragColor = vec4( vec3( 1.0 - fragCoordZ ), opacity );
	#elif DEPTH_PACKING == 3201
		gl_FragColor = packDepthToRGBA( fragCoordZ );
	#elif DEPTH_PACKING == 3202
		gl_FragColor = vec4( packDepthToRGB( fragCoordZ ), 1.0 );
	#elif DEPTH_PACKING == 3203
		gl_FragColor = vec4( packDepthToRG( fragCoordZ ), 0.0, 1.0 );
	#endif
}`,distance_vert:`#define DISTANCE
varying vec3 vWorldPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <skinbase_vertex>
	#include <morphinstance_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <worldpos_vertex>
	#include <clipping_planes_vertex>
	vWorldPosition = worldPosition.xyz;
}`,distance_frag:`#define DISTANCE
uniform vec3 referencePosition;
uniform float nearDistance;
uniform float farDistance;
varying vec3 vWorldPosition;
#include <common>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( 1.0 );
	#include <clipping_planes_fragment>
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	float dist = length( vWorldPosition - referencePosition );
	dist = ( dist - nearDistance ) / ( farDistance - nearDistance );
	dist = saturate( dist );
	gl_FragColor = vec4( dist, 0.0, 0.0, 1.0 );
}`,equirect_vert:`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,equirect_frag:`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,linedashed_vert:`uniform float scale;
attribute float lineDistance;
varying float vLineDistance;
#include <common>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	vLineDistance = scale * lineDistance;
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,linedashed_frag:`uniform vec3 diffuse;
uniform float opacity;
uniform float dashSize;
uniform float totalSize;
varying float vLineDistance;
#include <common>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	if ( mod( vLineDistance, totalSize ) > dashSize ) {
		discard;
	}
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,meshbasic_vert:`#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#if defined ( USE_ENVMAP ) || defined ( USE_SKINNING )
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinbase_vertex>
		#include <skinnormal_vertex>
		#include <defaultnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <fog_vertex>
}`,meshbasic_frag:`uniform vec3 diffuse;
uniform float opacity;
#ifndef FLAT_SHADED
	varying vec3 vNormal;
#endif
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
		reflectedLight.indirectDiffuse += lightMapTexel.rgb * lightMapIntensity * RECIPROCAL_PI;
	#else
		reflectedLight.indirectDiffuse += vec3( 1.0 );
	#endif
	#include <aomap_fragment>
	reflectedLight.indirectDiffuse *= diffuseColor.rgb;
	vec3 outgoingLight = reflectedLight.indirectDiffuse;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,meshlambert_vert:`#define LAMBERT
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,meshlambert_frag:`#define LAMBERT
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <cube_uv_reflection_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <envmap_physical_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_lambert_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_lambert_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,meshmatcap_vert:`#define MATCAP
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <displacementmap_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
	vViewPosition = - mvPosition.xyz;
}`,meshmatcap_frag:`#define MATCAP
uniform vec3 diffuse;
uniform float opacity;
uniform sampler2D matcap;
varying vec3 vViewPosition;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	vec3 viewDir = normalize( vViewPosition );
	vec3 x = normalize( vec3( viewDir.z, 0.0, - viewDir.x ) );
	vec3 y = cross( viewDir, x );
	vec2 uv = vec2( dot( x, normal ), dot( y, normal ) ) * 0.495 + 0.5;
	#ifdef USE_MATCAP
		vec4 matcapColor = texture2D( matcap, uv );
	#else
		vec4 matcapColor = vec4( vec3( mix( 0.2, 0.8, uv.y ) ), 1.0 );
	#endif
	vec3 outgoingLight = diffuseColor.rgb * matcapColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,meshnormal_vert:`#define NORMAL
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	varying vec3 vViewPosition;
#endif
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	vViewPosition = - mvPosition.xyz;
#endif
}`,meshnormal_frag:`#define NORMAL
uniform float opacity;
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	varying vec3 vViewPosition;
#endif
#include <uv_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( 0.0, 0.0, 0.0, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	gl_FragColor = vec4( normalize( normal ) * 0.5 + 0.5, diffuseColor.a );
	#ifdef OPAQUE
		gl_FragColor.a = 1.0;
	#endif
}`,meshphong_vert:`#define PHONG
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,meshphong_frag:`#define PHONG
uniform vec3 diffuse;
uniform vec3 emissive;
uniform vec3 specular;
uniform float shininess;
uniform float opacity;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <cube_uv_reflection_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <envmap_physical_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_phong_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_phong_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + reflectedLight.directSpecular + reflectedLight.indirectSpecular + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,meshphysical_vert:`#define STANDARD
varying vec3 vViewPosition;
#ifdef USE_TRANSMISSION
	varying vec3 vWorldPosition;
#endif
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
#ifdef USE_TRANSMISSION
	vWorldPosition = worldPosition.xyz;
#endif
}`,meshphysical_frag:`#define STANDARD
#ifdef PHYSICAL
	#define IOR
	#define USE_SPECULAR
#endif
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float roughness;
uniform float metalness;
uniform float opacity;
#ifdef IOR
	uniform float ior;
#endif
#ifdef USE_SPECULAR
	uniform float specularIntensity;
	uniform vec3 specularColor;
	#ifdef USE_SPECULAR_COLORMAP
		uniform sampler2D specularColorMap;
	#endif
	#ifdef USE_SPECULAR_INTENSITYMAP
		uniform sampler2D specularIntensityMap;
	#endif
#endif
#ifdef USE_CLEARCOAT
	uniform float clearcoat;
	uniform float clearcoatRoughness;
#endif
#ifdef USE_DISPERSION
	uniform float dispersion;
#endif
#ifdef USE_IRIDESCENCE
	uniform float iridescence;
	uniform float iridescenceIOR;
	uniform float iridescenceThicknessMinimum;
	uniform float iridescenceThicknessMaximum;
#endif
#ifdef USE_SHEEN
	uniform vec3 sheenColor;
	uniform float sheenRoughness;
	#ifdef USE_SHEEN_COLORMAP
		uniform sampler2D sheenColorMap;
	#endif
	#ifdef USE_SHEEN_ROUGHNESSMAP
		uniform sampler2D sheenRoughnessMap;
	#endif
#endif
#ifdef USE_ANISOTROPY
	uniform vec2 anisotropyVector;
	#ifdef USE_ANISOTROPYMAP
		uniform sampler2D anisotropyMap;
	#endif
#endif
varying vec3 vViewPosition;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <iridescence_fragment>
#include <cube_uv_reflection_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_physical_pars_fragment>
#include <fog_pars_fragment>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_physical_pars_fragment>
#include <transmission_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <clearcoat_pars_fragment>
#include <iridescence_pars_fragment>
#include <roughnessmap_pars_fragment>
#include <metalnessmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <roughnessmap_fragment>
	#include <metalnessmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <clearcoat_normal_fragment_begin>
	#include <clearcoat_normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_physical_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 totalDiffuse = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse;
	vec3 totalSpecular = reflectedLight.directSpecular + reflectedLight.indirectSpecular;
	#include <transmission_fragment>
	vec3 outgoingLight = totalDiffuse + totalSpecular + totalEmissiveRadiance;
	#ifdef USE_SHEEN
 
		outgoingLight = outgoingLight + sheenSpecularDirect + sheenSpecularIndirect;
 
 	#endif
	#ifdef USE_CLEARCOAT
		float dotNVcc = saturate( dot( geometryClearcoatNormal, geometryViewDir ) );
		vec3 Fcc = F_Schlick( material.clearcoatF0, material.clearcoatF90, dotNVcc );
		outgoingLight = outgoingLight * ( 1.0 - material.clearcoat * Fcc ) + ( clearcoatSpecularDirect + clearcoatSpecularIndirect ) * material.clearcoat;
	#endif
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,meshtoon_vert:`#define TOON
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,meshtoon_frag:`#define TOON
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <gradientmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_toon_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_toon_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,points_vert:`uniform float size;
uniform float scale;
#include <common>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
#ifdef USE_POINTS_UV
	varying vec2 vUv;
	uniform mat3 uvTransform;
#endif
void main() {
	#ifdef USE_POINTS_UV
		vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	#endif
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	gl_PointSize = size;
	#ifdef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) gl_PointSize *= ( scale / - mvPosition.z );
	#endif
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <fog_vertex>
}`,points_frag:`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <color_pars_fragment>
#include <map_particle_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_particle_fragment>
	#include <color_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,shadow_vert:`#include <common>
#include <batching_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <shadowmap_pars_vertex>
void main() {
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,shadow_frag:`uniform vec3 color;
uniform float opacity;
#include <common>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <logdepthbuf_pars_fragment>
#include <shadowmap_pars_fragment>
#include <shadowmask_pars_fragment>
void main() {
	#include <logdepthbuf_fragment>
	gl_FragColor = vec4( color, opacity * ( 1.0 - getShadowMask() ) );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,sprite_vert:`uniform float rotation;
uniform vec2 center;
#include <common>
#include <uv_pars_vertex>
#include <fog_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	vec4 mvPosition = modelViewMatrix[ 3 ];
	vec2 scale = vec2( length( modelMatrix[ 0 ].xyz ), length( modelMatrix[ 1 ].xyz ) );
	#ifndef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) scale *= - mvPosition.z;
	#endif
	vec2 alignedPosition = ( position.xy - ( center - vec2( 0.5 ) ) ) * scale;
	vec2 rotatedPosition;
	rotatedPosition.x = cos( rotation ) * alignedPosition.x - sin( rotation ) * alignedPosition.y;
	rotatedPosition.y = sin( rotation ) * alignedPosition.x + cos( rotation ) * alignedPosition.y;
	mvPosition.xy += rotatedPosition;
	gl_Position = projectionMatrix * mvPosition;
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,sprite_frag:`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
}`},X={common:{diffuse:{value:new J(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new G},alphaMap:{value:null},alphaMapTransform:{value:new G},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new G}},envmap:{envMap:{value:null},envMapRotation:{value:new G},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98},dfgLUT:{value:null}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new G}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new G}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new G},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new G},normalScale:{value:new U(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new G},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new G}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new G}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new G}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new J(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null},probesSH:{value:null},probesMin:{value:new W},probesMax:{value:new W},probesResolution:{value:new W}},points:{diffuse:{value:new J(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new G},alphaTest:{value:0},uvTransform:{value:new G}},sprite:{diffuse:{value:new J(16777215)},opacity:{value:1},center:{value:new U(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new G},alphaMap:{value:null},alphaMapTransform:{value:new G},alphaTest:{value:0}}},hc={basic:{uniforms:Ao([X.common,X.specularmap,X.envmap,X.aomap,X.lightmap,X.fog]),vertexShader:mc.meshbasic_vert,fragmentShader:mc.meshbasic_frag},lambert:{uniforms:Ao([X.common,X.specularmap,X.envmap,X.aomap,X.lightmap,X.emissivemap,X.bumpmap,X.normalmap,X.displacementmap,X.fog,X.lights,{emissive:{value:new J(0)},envMapIntensity:{value:1}}]),vertexShader:mc.meshlambert_vert,fragmentShader:mc.meshlambert_frag},phong:{uniforms:Ao([X.common,X.specularmap,X.envmap,X.aomap,X.lightmap,X.emissivemap,X.bumpmap,X.normalmap,X.displacementmap,X.fog,X.lights,{emissive:{value:new J(0)},specular:{value:new J(1118481)},shininess:{value:30},envMapIntensity:{value:1}}]),vertexShader:mc.meshphong_vert,fragmentShader:mc.meshphong_frag},standard:{uniforms:Ao([X.common,X.envmap,X.aomap,X.lightmap,X.emissivemap,X.bumpmap,X.normalmap,X.displacementmap,X.roughnessmap,X.metalnessmap,X.fog,X.lights,{emissive:{value:new J(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:mc.meshphysical_vert,fragmentShader:mc.meshphysical_frag},toon:{uniforms:Ao([X.common,X.aomap,X.lightmap,X.emissivemap,X.bumpmap,X.normalmap,X.displacementmap,X.gradientmap,X.fog,X.lights,{emissive:{value:new J(0)}}]),vertexShader:mc.meshtoon_vert,fragmentShader:mc.meshtoon_frag},matcap:{uniforms:Ao([X.common,X.bumpmap,X.normalmap,X.displacementmap,X.fog,{matcap:{value:null}}]),vertexShader:mc.meshmatcap_vert,fragmentShader:mc.meshmatcap_frag},points:{uniforms:Ao([X.points,X.fog]),vertexShader:mc.points_vert,fragmentShader:mc.points_frag},dashed:{uniforms:Ao([X.common,X.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:mc.linedashed_vert,fragmentShader:mc.linedashed_frag},depth:{uniforms:Ao([X.common,X.displacementmap]),vertexShader:mc.depth_vert,fragmentShader:mc.depth_frag},normal:{uniforms:Ao([X.common,X.bumpmap,X.normalmap,X.displacementmap,{opacity:{value:1}}]),vertexShader:mc.meshnormal_vert,fragmentShader:mc.meshnormal_frag},sprite:{uniforms:Ao([X.sprite,X.fog]),vertexShader:mc.sprite_vert,fragmentShader:mc.sprite_frag},background:{uniforms:{uvTransform:{value:new G},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:mc.background_vert,fragmentShader:mc.background_frag},backgroundCube:{uniforms:{envMap:{value:null},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new G}},vertexShader:mc.backgroundCube_vert,fragmentShader:mc.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:mc.cube_vert,fragmentShader:mc.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:mc.equirect_vert,fragmentShader:mc.equirect_frag},distance:{uniforms:Ao([X.common,X.displacementmap,{referencePosition:{value:new W},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:mc.distance_vert,fragmentShader:mc.distance_frag},shadow:{uniforms:Ao([X.lights,X.fog,{color:{value:new J(0)},opacity:{value:1}}]),vertexShader:mc.shadow_vert,fragmentShader:mc.shadow_frag}};hc.physical={uniforms:Ao([hc.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new G},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new G},clearcoatNormalScale:{value:new U(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new G},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new G},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new G},sheen:{value:0},sheenColor:{value:new J(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new G},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new G},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new G},transmissionSamplerSize:{value:new U},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new G},attenuationDistance:{value:0},attenuationColor:{value:new J(0)},specularColor:{value:new J(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new G},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new G},anisotropyVector:{value:new U},anisotropyMap:{value:null},anisotropyMapTransform:{value:new G}}]),vertexShader:mc.meshphysical_vert,fragmentShader:mc.meshphysical_frag};var gc={r:0,b:0,g:0},_c=new q,vc=new G;vc.set(-1,0,0,0,1,0,0,0,1);function yc(e,t,n,r,i,a){let o=new J(0),s=i===!0?0:1,c,l,u=null,d=0,f=null;function p(e){let n=e.isScene===!0?e.background:null;if(n&&n.isTexture){let r=e.backgroundBlurriness>0;n=t.get(n,r)}return n}function m(t){let r=!1,i=p(t);i===null?g(o,s):i&&i.isColor&&(g(i,1),r=!0);let c=e.xr.getEnvironmentBlendMode();c===`additive`?n.buffers.color.setClear(0,0,0,1,a):c===`alpha-blend`&&n.buffers.color.setClear(0,0,0,0,a),(e.autoClear||r)&&(n.buffers.depth.setTest(!0),n.buffers.depth.setMask(!0),n.buffers.color.setMask(!0),e.clear(e.autoClearColor,e.autoClearDepth,e.autoClearStencil))}function h(t,n){let i=p(n);i&&(i.isCubeTexture||i.mapping===306)?(l===void 0&&(l=new ei(new sa(1,1,1),new Lo({name:`BackgroundCubeMaterial`,uniforms:ko(hc.backgroundCube.uniforms),vertexShader:hc.backgroundCube.vertexShader,fragmentShader:hc.backgroundCube.fragmentShader,side:1,depthTest:!1,depthWrite:!1,fog:!1,allowOverride:!1})),l.geometry.deleteAttribute(`normal`),l.geometry.deleteAttribute(`uv`),l.onBeforeRender=function(e,t,n){this.matrixWorld.copyPosition(n.matrixWorld)},Object.defineProperty(l.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),r.update(l)),l.material.uniforms.envMap.value=i,l.material.uniforms.backgroundBlurriness.value=n.backgroundBlurriness,l.material.uniforms.backgroundIntensity.value=n.backgroundIntensity,l.material.uniforms.backgroundRotation.value.setFromMatrix4(_c.makeRotationFromEuler(n.backgroundRotation)).transpose(),i.isCubeTexture&&i.isRenderTargetTexture===!1&&l.material.uniforms.backgroundRotation.value.premultiply(vc),l.material.toneMapped=K.getTransfer(i.colorSpace)!==Ke,(u!==i||d!==i.version||f!==e.toneMapping)&&(l.material.needsUpdate=!0,u=i,d=i.version,f=e.toneMapping),l.layers.enableAll(),t.unshift(l,l.geometry,l.material,0,0,null)):i&&i.isTexture&&(c===void 0&&(c=new ei(new Do(2,2),new Lo({name:`BackgroundMaterial`,uniforms:ko(hc.background.uniforms),vertexShader:hc.background.vertexShader,fragmentShader:hc.background.fragmentShader,side:0,depthTest:!1,depthWrite:!1,fog:!1,allowOverride:!1})),c.geometry.deleteAttribute(`normal`),Object.defineProperty(c.material,"map",{get:function(){return this.uniforms.t2D.value}}),r.update(c)),c.material.uniforms.t2D.value=i,c.material.uniforms.backgroundIntensity.value=n.backgroundIntensity,c.material.toneMapped=K.getTransfer(i.colorSpace)!==Ke,i.matrixAutoUpdate===!0&&i.updateMatrix(),c.material.uniforms.uvTransform.value.copy(i.matrix),(u!==i||d!==i.version||f!==e.toneMapping)&&(c.material.needsUpdate=!0,u=i,d=i.version,f=e.toneMapping),c.layers.enableAll(),t.unshift(c,c.geometry,c.material,0,0,null))}function g(t,r){t.getRGB(gc,No(e)),n.buffers.color.setClear(gc.r,gc.g,gc.b,r,a)}function _(){l!==void 0&&(l.geometry.dispose(),l.material.dispose(),l=void 0),c!==void 0&&(c.geometry.dispose(),c.material.dispose(),c=void 0)}return{getClearColor:function(){return o},setClearColor:function(e,t=1){o.set(e),s=t,g(o,s)},getClearAlpha:function(){return s},setClearAlpha:function(e){s=e,g(o,s)},render:m,addToRenderList:h,dispose:_}}function bc(e,t){let n=e.getParameter(e.MAX_VERTEX_ATTRIBS),r={},i=f(null),a=i,o=!1;function s(n,r,i,s,c){let u=!1,f=d(n,s,i,r);a!==f&&(a=f,l(a.object)),u=p(n,s,i,c),u&&m(n,s,i,c),c!==null&&t.update(c,e.ELEMENT_ARRAY_BUFFER),(u||o)&&(o=!1,b(n,r,i,s),c!==null&&e.bindBuffer(e.ELEMENT_ARRAY_BUFFER,t.get(c).buffer))}function c(){return e.createVertexArray()}function l(t){return e.bindVertexArray(t)}function u(t){return e.deleteVertexArray(t)}function d(e,t,n,i){let a=i.wireframe===!0,o=r[t.id];o===void 0&&(o={},r[t.id]=o);let s=e.isInstancedMesh===!0?e.id:0,l=o[s];l===void 0&&(l={},o[s]=l);let u=l[n.id];u===void 0&&(u={},l[n.id]=u);let d=u[a];return d===void 0&&(d=f(c()),u[a]=d),d}function f(e){let t=[],r=[],i=[];for(let e=0;e<n;e++)t[e]=0,r[e]=0,i[e]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:t,enabledAttributes:r,attributeDivisors:i,object:e,attributes:{},index:null}}function p(e,t,n,r){let i=a.attributes,o=t.attributes,s=0,c=n.getAttributes();for(let t in c)if(c[t].location>=0){let n=i[t],r=o[t];if(r===void 0&&(t===`instanceMatrix`&&e.instanceMatrix&&(r=e.instanceMatrix),t===`instanceColor`&&e.instanceColor&&(r=e.instanceColor)),n===void 0||n.attribute!==r||r&&n.data!==r.data)return!0;s++}return a.attributesNum!==s||a.index!==r}function m(e,t,n,r){let i={},o=t.attributes,s=0,c=n.getAttributes();for(let t in c)if(c[t].location>=0){let n=o[t];n===void 0&&(t===`instanceMatrix`&&e.instanceMatrix&&(n=e.instanceMatrix),t===`instanceColor`&&e.instanceColor&&(n=e.instanceColor));let r={};r.attribute=n,n&&n.data&&(r.data=n.data),i[t]=r,s++}a.attributes=i,a.attributesNum=s,a.index=r}function h(){let e=a.newAttributes;for(let t=0,n=e.length;t<n;t++)e[t]=0}function g(e){_(e,0)}function _(t,n){let r=a.newAttributes,i=a.enabledAttributes,o=a.attributeDivisors;r[t]=1,i[t]===0&&(e.enableVertexAttribArray(t),i[t]=1),o[t]!==n&&(e.vertexAttribDivisor(t,n),o[t]=n)}function v(){let t=a.newAttributes,n=a.enabledAttributes;for(let r=0,i=n.length;r<i;r++)n[r]!==t[r]&&(e.disableVertexAttribArray(r),n[r]=0)}function y(t,n,r,i,a,o,s){s===!0?e.vertexAttribIPointer(t,n,r,a,o):e.vertexAttribPointer(t,n,r,i,a,o)}function b(n,r,i,a){h();let o=a.attributes,s=i.getAttributes(),c=r.defaultAttributeValues;for(let r in s){let i=s[r];if(i.location>=0){let s=o[r];if(s===void 0&&(r===`instanceMatrix`&&n.instanceMatrix&&(s=n.instanceMatrix),r===`instanceColor`&&n.instanceColor&&(s=n.instanceColor)),s!==void 0){let r=s.normalized,o=s.itemSize,c=t.get(s);if(c===void 0)continue;let l=c.buffer,u=c.type,d=c.bytesPerElement,f=u===e.INT||u===e.UNSIGNED_INT||s.gpuType===1013;if(s.isInterleavedBufferAttribute){let t=s.data,c=t.stride,p=s.offset;if(t.isInstancedInterleavedBuffer){for(let e=0;e<i.locationSize;e++)_(i.location+e,t.meshPerAttribute);n.isInstancedMesh!==!0&&a._maxInstanceCount===void 0&&(a._maxInstanceCount=t.meshPerAttribute*t.count)}else for(let e=0;e<i.locationSize;e++)g(i.location+e);e.bindBuffer(e.ARRAY_BUFFER,l);for(let e=0;e<i.locationSize;e++)y(i.location+e,o/i.locationSize,u,r,c*d,(p+o/i.locationSize*e)*d,f)}else{if(s.isInstancedBufferAttribute){for(let e=0;e<i.locationSize;e++)_(i.location+e,s.meshPerAttribute);n.isInstancedMesh!==!0&&a._maxInstanceCount===void 0&&(a._maxInstanceCount=s.meshPerAttribute*s.count)}else for(let e=0;e<i.locationSize;e++)g(i.location+e);e.bindBuffer(e.ARRAY_BUFFER,l);for(let e=0;e<i.locationSize;e++)y(i.location+e,o/i.locationSize,u,r,o*d,o/i.locationSize*e*d,f)}}else if(c!==void 0){let t=c[r];if(t!==void 0)switch(t.length){case 2:e.vertexAttrib2fv(i.location,t);break;case 3:e.vertexAttrib3fv(i.location,t);break;case 4:e.vertexAttrib4fv(i.location,t);break;default:e.vertexAttrib1fv(i.location,t)}}}}v()}function x(){T();for(let e in r){let t=r[e];for(let e in t){let n=t[e];for(let e in n){let t=n[e];for(let e in t)u(t[e].object),delete t[e];delete n[e]}}delete r[e]}}function S(e){if(r[e.id]===void 0)return;let t=r[e.id];for(let e in t){let n=t[e];for(let e in n){let t=n[e];for(let e in t)u(t[e].object),delete t[e];delete n[e]}}delete r[e.id]}function C(e){for(let t in r){let n=r[t];for(let t in n){let r=n[t];if(r[e.id]===void 0)continue;let i=r[e.id];for(let e in i)u(i[e].object),delete i[e];delete r[e.id]}}}function w(e){for(let t in r){let n=r[t],i=e.isInstancedMesh===!0?e.id:0,a=n[i];if(a!==void 0){for(let e in a){let t=a[e];for(let e in t)u(t[e].object),delete t[e];delete a[e]}delete n[i],Object.keys(n).length===0&&delete r[t]}}}function T(){E(),o=!0,a!==i&&(a=i,l(a.object))}function E(){i.geometry=null,i.program=null,i.wireframe=!1}return{setup:s,reset:T,resetDefaultState:E,dispose:x,releaseStatesOfGeometry:S,releaseStatesOfObject:w,releaseStatesOfProgram:C,initAttributes:h,enableAttribute:g,disableUnusedAttributes:v}}function xc(e,t,n){let r;function i(e){r=e}function a(t,i){e.drawArrays(r,t,i),n.update(i,r,1)}function o(t,i,a){a!==0&&(e.drawArraysInstanced(r,t,i,a),n.update(i,r,a))}function s(e,i,a){if(a===0)return;t.get(`WEBGL_multi_draw`).multiDrawArraysWEBGL(r,e,0,i,0,a);let o=0;for(let e=0;e<a;e++)o+=i[e];n.update(o,r,1)}this.setMode=i,this.render=a,this.renderInstances=o,this.renderMultiDraw=s}function Sc(e,t,n,r){let i;function a(){if(i!==void 0)return i;if(t.has(`EXT_texture_filter_anisotropic`)===!0){let n=t.get(`EXT_texture_filter_anisotropic`);i=e.getParameter(n.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else i=0;return i}function o(t){return t===1023||r.convert(t)===e.getParameter(e.IMPLEMENTATION_COLOR_READ_FORMAT)}function s(n){let i=n===1016&&(t.has(`EXT_color_buffer_half_float`)||t.has(`EXT_color_buffer_float`));return!(n!==1009&&r.convert(n)!==e.getParameter(e.IMPLEMENTATION_COLOR_READ_TYPE)&&n!==1015&&!i)}function c(t){if(t===`highp`){if(e.getShaderPrecisionFormat(e.VERTEX_SHADER,e.HIGH_FLOAT).precision>0&&e.getShaderPrecisionFormat(e.FRAGMENT_SHADER,e.HIGH_FLOAT).precision>0)return`highp`;t=`mediump`}return t===`mediump`&&e.getShaderPrecisionFormat(e.VERTEX_SHADER,e.MEDIUM_FLOAT).precision>0&&e.getShaderPrecisionFormat(e.FRAGMENT_SHADER,e.MEDIUM_FLOAT).precision>0?`mediump`:`lowp`}let l=n.precision===void 0?`highp`:n.precision,u=c(l);u!==l&&(B(`WebGLRenderer:`,l,`not supported, using`,u,`instead.`),l=u);let d=n.logarithmicDepthBuffer===!0,f=n.reversedDepthBuffer===!0&&t.has(`EXT_clip_control`);n.reversedDepthBuffer===!0&&f===!1&&B(`WebGLRenderer: Unable to use reversed depth buffer due to missing EXT_clip_control extension. Fallback to default depth buffer.`);let p=e.getParameter(e.MAX_TEXTURE_IMAGE_UNITS),m=e.getParameter(e.MAX_VERTEX_TEXTURE_IMAGE_UNITS),h=e.getParameter(e.MAX_TEXTURE_SIZE),g=e.getParameter(e.MAX_CUBE_MAP_TEXTURE_SIZE),_=e.getParameter(e.MAX_VERTEX_ATTRIBS),v=e.getParameter(e.MAX_VERTEX_UNIFORM_VECTORS),y=e.getParameter(e.MAX_VARYING_VECTORS),b=e.getParameter(e.MAX_FRAGMENT_UNIFORM_VECTORS),x=e.getParameter(e.MAX_SAMPLES),S=e.getParameter(e.SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:a,getMaxPrecision:c,textureFormatReadable:o,textureTypeReadable:s,precision:l,logarithmicDepthBuffer:d,reversedDepthBuffer:f,maxTextures:p,maxVertexTextures:m,maxTextureSize:h,maxCubemapSize:g,maxAttributes:_,maxVertexUniforms:v,maxVaryings:y,maxFragmentUniforms:b,maxSamples:x,samples:S}}function Cc(e){let t=this,n=null,r=0,i=!1,a=!1,o=new Ai,s=new G,c={value:null,needsUpdate:!1};this.uniform=c,this.numPlanes=0,this.numIntersection=0,this.init=function(e,t){let n=e.length!==0||t||r!==0||i;return i=t,r=e.length,n},this.beginShadows=function(){a=!0,u(null)},this.endShadows=function(){a=!1},this.setGlobalState=function(e,t){n=u(e,t,0)},this.setState=function(t,o,s){let d=t.clippingPlanes,f=t.clipIntersection,p=t.clipShadows,m=e.get(t);if(!i||d===null||d.length===0||a&&!p)a?u(null):l();else{let e=a?0:r,t=e*4,i=m.clippingState||null;c.value=i,i=u(d,o,t,s);for(let e=0;e!==t;++e)i[e]=n[e];m.clippingState=i,this.numIntersection=f?this.numPlanes:0,this.numPlanes+=e}};function l(){c.value!==n&&(c.value=n,c.needsUpdate=r>0),t.numPlanes=r,t.numIntersection=0}function u(e,n,r,i){let a=e===null?0:e.length,l=null;if(a!==0){if(l=c.value,i!==!0||l===null){let t=r+a*4,i=n.matrixWorldInverse;s.getNormalMatrix(i),(l===null||l.length<t)&&(l=new Float32Array(t));for(let t=0,n=r;t!==a;++t,n+=4)o.copy(e[t]).applyMatrix4(i,s),o.normal.toArray(l,n),l[n+3]=o.constant}c.value=l,c.needsUpdate=!0}return t.numPlanes=a,t.numIntersection=0,l}}var wc=4,Tc=[.125,.215,.35,.446,.526,.582],Ec=20,Dc=256,Oc=new Is,kc=new J,Ac=null,jc=0,Mc=0,Nc=!1,Pc=new W,Fc=class{constructor(e){this._renderer=e,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._sizeLods=[],this._sigmas=[],this._lodMeshes=[],this._backgroundBox=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._blurMaterial=null,this._ggxMaterial=null}fromScene(e,t=0,n=.1,r=100,i={}){let{size:a=256,position:o=Pc}=i;Ac=this._renderer.getRenderTarget(),jc=this._renderer.getActiveCubeFace(),Mc=this._renderer.getActiveMipmapLevel(),Nc=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(a);let s=this._allocateTargets();return s.depthBuffer=!0,this._sceneToCubeUV(e,n,r,s,o),t>0&&this._blur(s,0,0,t),this._applyPMREM(s),this._cleanup(s),s}fromEquirectangular(e,t=null){return this._fromTexture(e,t)}fromCubemap(e,t=null){return this._fromTexture(e,t)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=Hc(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=Vc(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose(),this._backgroundBox!==null&&(this._backgroundBox.geometry.dispose(),this._backgroundBox.material.dispose())}_setSize(e){this._lodMax=Math.floor(Math.log2(e)),this._cubeSize=2**this._lodMax}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._ggxMaterial!==null&&this._ggxMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let e=0;e<this._lodMeshes.length;e++)this._lodMeshes[e].geometry.dispose()}_cleanup(e){this._renderer.setRenderTarget(Ac,jc,Mc),this._renderer.xr.enabled=Nc,e.scissorTest=!1,Rc(e,0,0,e.width,e.height)}_fromTexture(e,t){e.mapping===301||e.mapping===302?this._setSize(e.image.length===0?16:e.image[0].width||e.image[0].image.width):this._setSize(e.image.width/4),Ac=this._renderer.getRenderTarget(),jc=this._renderer.getActiveCubeFace(),Mc=this._renderer.getActiveMipmapLevel(),Nc=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;let n=t||this._allocateTargets();return this._textureToCubeUV(e,n),this._applyPMREM(n),this._cleanup(n),n}_allocateTargets(){let e=3*Math.max(this._cubeSize,112),t=4*this._cubeSize,n={magFilter:l,minFilter:l,generateMipmaps:!1,type:y,format:D,colorSpace:We,depthBuffer:!1},r=Lc(e,t,n);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==e||this._pingPongRenderTarget.height!==t){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=Lc(e,t,n);let{_lodMax:r}=this;({lodMeshes:this._lodMeshes,sizeLods:this._sizeLods,sigmas:this._sigmas}=Ic(r)),this._blurMaterial=Bc(r,e,t),this._ggxMaterial=zc(r,e,t)}return r}_compileMaterial(e){let t=new ei(new Or,e);this._renderer.compile(t,Oc)}_sceneToCubeUV(e,t,n,r,i){let a=new js(90,1,t,n),o=[1,-1,1,1,1,1],s=[1,1,1,-1,-1,-1],c=this._renderer,l=c.autoClear,u=c.toneMapping;c.getClearColor(kc),c.toneMapping=0,c.autoClear=!1,c.state.buffers.depth.getReversed()&&(c.setRenderTarget(r),c.clearDepth(),c.setRenderTarget(null)),this._backgroundBox===null&&(this._backgroundBox=new ei(new sa,new Hr({name:`PMREM.Background`,side:1,depthWrite:!1,depthTest:!1})));let d=this._backgroundBox,f=d.material,p=!1,m=e.background;m?m.isColor&&(f.color.copy(m),e.background=null,p=!0):(f.color.copy(kc),p=!0);for(let t=0;t<6;t++){let n=t%3;n===0?(a.up.set(0,o[t],0),a.position.set(i.x,i.y,i.z),a.lookAt(i.x+s[t],i.y,i.z)):n===1?(a.up.set(0,0,o[t]),a.position.set(i.x,i.y,i.z),a.lookAt(i.x,i.y+s[t],i.z)):(a.up.set(0,o[t],0),a.position.set(i.x,i.y,i.z),a.lookAt(i.x,i.y,i.z+s[t]));let l=this._cubeSize;Rc(r,n*l,t>2?l:0,l,l),c.setRenderTarget(r),p&&c.render(d,a),c.render(e,a)}c.toneMapping=u,c.autoClear=l,e.background=m}_textureToCubeUV(e,t){let n=this._renderer,r=e.mapping===301||e.mapping===302;r?(this._cubemapMaterial===null&&(this._cubemapMaterial=Hc()),this._cubemapMaterial.uniforms.flipEnvMap.value=e.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=Vc());let i=r?this._cubemapMaterial:this._equirectMaterial,a=this._lodMeshes[0];a.material=i;let o=i.uniforms;o.envMap.value=e;let s=this._cubeSize;Rc(t,0,0,3*s,2*s),n.setRenderTarget(t),n.render(a,Oc)}_applyPMREM(e){let t=this._renderer,n=t.autoClear;t.autoClear=!1;let r=this._lodMeshes.length;for(let t=1;t<r;t++)this._applyGGXFilter(e,t-1,t);t.autoClear=n}_applyGGXFilter(e,t,n){let r=this._renderer,i=this._pingPongRenderTarget,a=this._ggxMaterial,o=this._lodMeshes[n];o.material=a;let s=a.uniforms,c=n/(this._lodMeshes.length-1),l=t/(this._lodMeshes.length-1),u=Math.sqrt(c*c-l*l)*(0+c*1.25),{_lodMax:d}=this,f=this._sizeLods[n],p=3*f*(n>d-wc?n-d+wc:0),m=4*(this._cubeSize-f);s.envMap.value=e.texture,s.roughness.value=u,s.mipInt.value=d-t,Rc(i,p,m,3*f,2*f),r.setRenderTarget(i),r.render(o,Oc),s.envMap.value=i.texture,s.roughness.value=0,s.mipInt.value=d-n,Rc(e,p,m,3*f,2*f),r.setRenderTarget(e),r.render(o,Oc)}_blur(e,t,n,r,i){let a=this._pingPongRenderTarget;this._halfBlur(e,a,t,n,r,`latitudinal`,i),this._halfBlur(a,e,n,n,r,`longitudinal`,i)}_halfBlur(e,t,n,r,i,a,o){let s=this._renderer,c=this._blurMaterial;a!==`latitudinal`&&a!==`longitudinal`&&V(`blur direction must be either latitudinal or longitudinal!`);let l=this._lodMeshes[r];l.material=c;let u=c.uniforms,d=this._sizeLods[n]-1,f=isFinite(i)?Math.PI/(2*d):2*Math.PI/39,p=i/f,m=isFinite(i)?1+Math.floor(3*p):Ec;m>Ec&&B(`sigmaRadians, ${i}, is too large and will clip, as it requested ${m} samples when the maximum is set to ${Ec}`);let h=[],g=0;for(let e=0;e<Ec;++e){let t=e/p,n=Math.exp(-t*t/2);h.push(n),e===0?g+=n:e<m&&(g+=2*n)}for(let e=0;e<h.length;e++)h[e]=h[e]/g;u.envMap.value=e.texture,u.samples.value=m,u.weights.value=h,u.latitudinal.value=a===`latitudinal`,o&&(u.poleAxis.value=o);let{_lodMax:_}=this;u.dTheta.value=f,u.mipInt.value=_-n;let v=this._sizeLods[r];Rc(t,3*v*(r>_-wc?r-_+wc:0),4*(this._cubeSize-v),3*v,2*v),s.setRenderTarget(t),s.render(l,Oc)}};function Ic(e){let t=[],n=[],r=[],i=e,a=e-wc+1+Tc.length;for(let o=0;o<a;o++){let a=2**i;t.push(a);let s=1/a;o>e-wc?s=Tc[o-e+wc-1]:o===0&&(s=0),n.push(s);let c=1/(a-2),l=-c,u=1+c,d=[l,l,u,l,u,u,l,l,u,u,l,u],f=new Float32Array(108),p=new Float32Array(72),m=new Float32Array(36);for(let e=0;e<6;e++){let t=e%3*2/3-1,n=e>2?0:-1,r=[t,n,0,t+2/3,n,0,t+2/3,n+1,0,t,n,0,t+2/3,n+1,0,t,n+1,0];f.set(r,18*e),p.set(d,12*e);let i=[e,e,e,e,e,e];m.set(i,6*e)}let h=new Or;h.setAttribute(`position`,new mr(f,3)),h.setAttribute(`uv`,new mr(p,2)),h.setAttribute(`faceIndex`,new mr(m,1)),r.push(new ei(h,null)),i>wc&&i--}return{lodMeshes:r,sizeLods:t,sigmas:n}}function Lc(e,t,n){let r=new Xt(e,t,n);return r.texture.mapping=306,r.texture.name=`PMREM.cubeUv`,r.scissorTest=!0,r}function Rc(e,t,n,r,i){e.viewport.set(t,n,r,i),e.scissor.set(t,n,r,i)}function zc(e,t,n){return new Lo({name:`PMREMGGXConvolution`,defines:{GGX_SAMPLES:Dc,CUBEUV_TEXEL_WIDTH:1/t,CUBEUV_TEXEL_HEIGHT:1/n,CUBEUV_MAX_MIP:`${e}.0`},uniforms:{envMap:{value:null},roughness:{value:0},mipInt:{value:0}},vertexShader:Uc(),fragmentShader:`

			precision highp float;
			precision highp int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;
			uniform float roughness;
			uniform float mipInt;

			#define ENVMAP_TYPE_CUBE_UV
			#include <cube_uv_reflection_fragment>

			#define PI 3.14159265359

			// Van der Corput radical inverse
			float radicalInverse_VdC(uint bits) {
				bits = (bits << 16u) | (bits >> 16u);
				bits = ((bits & 0x55555555u) << 1u) | ((bits & 0xAAAAAAAAu) >> 1u);
				bits = ((bits & 0x33333333u) << 2u) | ((bits & 0xCCCCCCCCu) >> 2u);
				bits = ((bits & 0x0F0F0F0Fu) << 4u) | ((bits & 0xF0F0F0F0u) >> 4u);
				bits = ((bits & 0x00FF00FFu) << 8u) | ((bits & 0xFF00FF00u) >> 8u);
				return float(bits) * 2.3283064365386963e-10; // / 0x100000000
			}

			// Hammersley sequence
			vec2 hammersley(uint i, uint N) {
				return vec2(float(i) / float(N), radicalInverse_VdC(i));
			}

			// GGX VNDF importance sampling (Eric Heitz 2018)
			// "Sampling the GGX Distribution of Visible Normals"
			// https://jcgt.org/published/0007/04/01/
			vec3 importanceSampleGGX_VNDF(vec2 Xi, vec3 V, float roughness) {
				float alpha = roughness * roughness;

				// Section 4.1: Orthonormal basis
				vec3 T1 = vec3(1.0, 0.0, 0.0);
				vec3 T2 = cross(V, T1);

				// Section 4.2: Parameterization of projected area
				float r = sqrt(Xi.x);
				float phi = 2.0 * PI * Xi.y;
				float t1 = r * cos(phi);
				float t2 = r * sin(phi);
				float s = 0.5 * (1.0 + V.z);
				t2 = (1.0 - s) * sqrt(1.0 - t1 * t1) + s * t2;

				// Section 4.3: Reprojection onto hemisphere
				vec3 Nh = t1 * T1 + t2 * T2 + sqrt(max(0.0, 1.0 - t1 * t1 - t2 * t2)) * V;

				// Section 3.4: Transform back to ellipsoid configuration
				return normalize(vec3(alpha * Nh.x, alpha * Nh.y, max(0.0, Nh.z)));
			}

			void main() {
				vec3 N = normalize(vOutputDirection);
				vec3 V = N; // Assume view direction equals normal for pre-filtering

				vec3 prefilteredColor = vec3(0.0);
				float totalWeight = 0.0;

				// For very low roughness, just sample the environment directly
				if (roughness < 0.001) {
					gl_FragColor = vec4(bilinearCubeUV(envMap, N, mipInt), 1.0);
					return;
				}

				// Tangent space basis for VNDF sampling
				vec3 up = abs(N.z) < 0.999 ? vec3(0.0, 0.0, 1.0) : vec3(1.0, 0.0, 0.0);
				vec3 tangent = normalize(cross(up, N));
				vec3 bitangent = cross(N, tangent);

				for(uint i = 0u; i < uint(GGX_SAMPLES); i++) {
					vec2 Xi = hammersley(i, uint(GGX_SAMPLES));

					// For PMREM, V = N, so in tangent space V is always (0, 0, 1)
					vec3 H_tangent = importanceSampleGGX_VNDF(Xi, vec3(0.0, 0.0, 1.0), roughness);

					// Transform H back to world space
					vec3 H = normalize(tangent * H_tangent.x + bitangent * H_tangent.y + N * H_tangent.z);
					vec3 L = normalize(2.0 * dot(V, H) * H - V);

					float NdotL = max(dot(N, L), 0.0);

					if(NdotL > 0.0) {
						// Sample environment at fixed mip level
						// VNDF importance sampling handles the distribution filtering
						vec3 sampleColor = bilinearCubeUV(envMap, L, mipInt);

						// Weight by NdotL for the split-sum approximation
						// VNDF PDF naturally accounts for the visible microfacet distribution
						prefilteredColor += sampleColor * NdotL;
						totalWeight += NdotL;
					}
				}

				if (totalWeight > 0.0) {
					prefilteredColor = prefilteredColor / totalWeight;
				}

				gl_FragColor = vec4(prefilteredColor, 1.0);
			}
		`,blending:0,depthTest:!1,depthWrite:!1})}function Bc(e,t,n){let r=new Float32Array(Ec),i=new W(0,1,0);return new Lo({name:`SphericalGaussianBlur`,defines:{n:Ec,CUBEUV_TEXEL_WIDTH:1/t,CUBEUV_TEXEL_HEIGHT:1/n,CUBEUV_MAX_MIP:`${e}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:r},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:i}},vertexShader:Uc(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;
			uniform int samples;
			uniform float weights[ n ];
			uniform bool latitudinal;
			uniform float dTheta;
			uniform float mipInt;
			uniform vec3 poleAxis;

			#define ENVMAP_TYPE_CUBE_UV
			#include <cube_uv_reflection_fragment>

			vec3 getSample( float theta, vec3 axis ) {

				float cosTheta = cos( theta );
				// Rodrigues' axis-angle rotation
				vec3 sampleDirection = vOutputDirection * cosTheta
					+ cross( axis, vOutputDirection ) * sin( theta )
					+ axis * dot( axis, vOutputDirection ) * ( 1.0 - cosTheta );

				return bilinearCubeUV( envMap, sampleDirection, mipInt );

			}

			void main() {

				vec3 axis = latitudinal ? poleAxis : cross( poleAxis, vOutputDirection );

				if ( all( equal( axis, vec3( 0.0 ) ) ) ) {

					axis = vec3( vOutputDirection.z, 0.0, - vOutputDirection.x );

				}

				axis = normalize( axis );

				gl_FragColor = vec4( 0.0, 0.0, 0.0, 1.0 );
				gl_FragColor.rgb += weights[ 0 ] * getSample( 0.0, axis );

				for ( int i = 1; i < n; i++ ) {

					if ( i >= samples ) {

						break;

					}

					float theta = dTheta * float( i );
					gl_FragColor.rgb += weights[ i ] * getSample( -1.0 * theta, axis );
					gl_FragColor.rgb += weights[ i ] * getSample( theta, axis );

				}

			}
		`,blending:0,depthTest:!1,depthWrite:!1})}function Vc(){return new Lo({name:`EquirectangularToCubeUV`,uniforms:{envMap:{value:null}},vertexShader:Uc(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;

			#include <common>

			void main() {

				vec3 outputDirection = normalize( vOutputDirection );
				vec2 uv = equirectUv( outputDirection );

				gl_FragColor = vec4( texture2D ( envMap, uv ).rgb, 1.0 );

			}
		`,blending:0,depthTest:!1,depthWrite:!1})}function Hc(){return new Lo({name:`CubemapToCubeUV`,uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:Uc(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:0,depthTest:!1,depthWrite:!1})}function Uc(){return`

		precision mediump float;
		precision mediump int;

		attribute float faceIndex;

		varying vec3 vOutputDirection;

		// RH coordinate system; PMREM face-indexing convention
		vec3 getDirection( vec2 uv, float face ) {

			uv = 2.0 * uv - 1.0;

			vec3 direction = vec3( uv, 1.0 );

			if ( face == 0.0 ) {

				direction = direction.zyx; // ( 1, v, u ) pos x

			} else if ( face == 1.0 ) {

				direction = direction.xzy;
				direction.xz *= -1.0; // ( -u, 1, -v ) pos y

			} else if ( face == 2.0 ) {

				direction.x *= -1.0; // ( -u, v, 1 ) pos z

			} else if ( face == 3.0 ) {

				direction = direction.zyx;
				direction.xz *= -1.0; // ( -1, v, -u ) neg x

			} else if ( face == 4.0 ) {

				direction = direction.xzy;
				direction.xy *= -1.0; // ( -u, -1, v ) neg y

			} else if ( face == 5.0 ) {

				direction.z *= -1.0; // ( u, v, -1 ) neg z

			}

			return direction;

		}

		void main() {

			vOutputDirection = getDirection( uv, faceIndex );
			gl_Position = vec4( position, 1.0 );

		}
	`}var Wc=class extends Xt{constructor(e=1,t={}){super(e,e,t),this.isWebGLCubeRenderTarget=!0;let n={width:e,height:e,depth:1},r=[n,n,n,n,n,n];this.texture=new na(r),this._setTextureOptions(t),this.texture.isRenderTargetTexture=!0}fromEquirectangularTexture(e,t){this.texture.type=t.type,this.texture.colorSpace=t.colorSpace,this.texture.generateMipmaps=t.generateMipmaps,this.texture.minFilter=t.minFilter,this.texture.magFilter=t.magFilter;let n={uniforms:{tEquirect:{value:null}},vertexShader:`

				varying vec3 vWorldDirection;

				vec3 transformDirection( in vec3 dir, in mat4 matrix ) {

					return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );

				}

				void main() {

					vWorldDirection = transformDirection( position, modelMatrix );

					#include <begin_vertex>
					#include <project_vertex>

				}
			`,fragmentShader:`

				uniform sampler2D tEquirect;

				varying vec3 vWorldDirection;

				#include <common>

				void main() {

					vec3 direction = normalize( vWorldDirection );

					vec2 sampleUV = equirectUv( direction );

					gl_FragColor = texture2D( tEquirect, sampleUV );

				}
			`},r=new sa(5,5,5),i=new Lo({name:`CubemapFromEquirect`,uniforms:ko(n.uniforms),vertexShader:n.vertexShader,fragmentShader:n.fragmentShader,side:1,blending:0});i.uniforms.tEquirect.value=t;let a=new ei(r,i),o=t.minFilter;return t.minFilter===1008&&(t.minFilter=l),new Ws(1,10,this).update(e,a),t.minFilter=o,a.geometry.dispose(),a.material.dispose(),this}clear(e,t=!0,n=!0,r=!0){let i=e.getRenderTarget();for(let i=0;i<6;i++)e.setRenderTarget(this,i),e.clear(t,n,r);e.setRenderTarget(i)}};function Gc(e){let t=new WeakMap,n=new WeakMap,r=null;function i(e,t=!1){return e==null?null:t?o(e):a(e)}function a(n){if(n&&n.isTexture){let r=n.mapping;if(r===303||r===304){if(t.has(n)){let e=t.get(n).texture;return s(e,n.mapping)}{let r=n.image;if(r&&r.height>0){let i=new Wc(r.height);return i.fromEquirectangularTexture(e,n),t.set(n,i),n.addEventListener(`dispose`,l),s(i.texture,n.mapping)}return null}}}return n}function o(t){if(t&&t.isTexture){let i=t.mapping,a=i===303||i===304,o=i===301||i===302;if(a||o){let i=n.get(t),s=i===void 0?0:i.texture.pmremVersion;if(t.isRenderTargetTexture&&t.pmremVersion!==s)return r===null&&(r=new Fc(e)),i=a?r.fromEquirectangular(t,i):r.fromCubemap(t,i),i.texture.pmremVersion=t.pmremVersion,n.set(t,i),i.texture;if(i!==void 0)return i.texture;{let s=t.image;return a&&s&&s.height>0||o&&s&&c(s)?(r===null&&(r=new Fc(e)),i=a?r.fromEquirectangular(t):r.fromCubemap(t),i.texture.pmremVersion=t.pmremVersion,n.set(t,i),t.addEventListener(`dispose`,u),i.texture):null}}}return t}function s(e,t){return t===303?e.mapping=301:t===304&&(e.mapping=302),e}function c(e){let t=0;for(let n=0;n<6;n++)e[n]!==void 0&&t++;return t===6}function l(e){let n=e.target;n.removeEventListener(`dispose`,l);let r=t.get(n);r!==void 0&&(t.delete(n),r.dispose())}function u(e){let t=e.target;t.removeEventListener(`dispose`,u);let r=n.get(t);r!==void 0&&(n.delete(t),r.dispose())}function d(){t=new WeakMap,n=new WeakMap,r!==null&&(r.dispose(),r=null)}return{get:i,dispose:d}}function Kc(e){let t={};function n(n){if(t[n]!==void 0)return t[n];let r=e.getExtension(n);return t[n]=r,r}return{has:function(e){return n(e)!==null},init:function(){n(`EXT_color_buffer_float`),n(`WEBGL_clip_cull_distance`),n(`OES_texture_float_linear`),n(`EXT_color_buffer_half_float`),n(`WEBGL_multisampled_render_to_texture`),n(`WEBGL_render_shared_exponent`)},get:function(e){let t=n(e);return t===null&&tt(`WebGLRenderer: `+e+` extension not supported.`),t}}}function qc(e,t,n,r){let i={},a=new WeakMap;function o(e){let s=e.target;s.index!==null&&t.remove(s.index);for(let e in s.attributes)t.remove(s.attributes[e]);s.removeEventListener(`dispose`,o),delete i[s.id];let c=a.get(s);c&&(t.remove(c),a.delete(s)),r.releaseStatesOfGeometry(s),s.isInstancedBufferGeometry===!0&&delete s._maxInstanceCount,n.memory.geometries--}function s(e,t){return i[t.id]===!0?t:(t.addEventListener(`dispose`,o),i[t.id]=!0,n.memory.geometries++,t)}function c(n){let r=n.attributes;for(let n in r)t.update(r[n],e.ARRAY_BUFFER)}function l(e){let n=[],r=e.index,i=e.attributes.position,o=0;if(i===void 0)return;if(r!==null){let e=r.array;o=r.version;for(let t=0,r=e.length;t<r;t+=3){let r=e[t+0],i=e[t+1],a=e[t+2];n.push(r,i,i,a,a,r)}}else{let e=i.array;o=i.version;for(let t=0,r=e.length/3-1;t<r;t+=3){let e=t+0,r=t+1,i=t+2;n.push(e,r,r,i,i,e)}}let s=new(i.count>=65535?gr:hr)(n,1);s.version=o;let c=a.get(e);c&&t.remove(c),a.set(e,s)}function u(e){let t=a.get(e);if(t){let n=e.index;n!==null&&t.version<n.version&&l(e)}else l(e);return a.get(e)}return{get:s,update:c,getWireframeAttribute:u}}function Jc(e,t,n){let r;function i(e){r=e}let a,o;function s(e){a=e.type,o=e.bytesPerElement}function c(t,i){e.drawElements(r,i,a,t*o),n.update(i,r,1)}function l(t,i,s){s!==0&&(e.drawElementsInstanced(r,i,a,t*o,s),n.update(i,r,s))}function u(e,i,o){if(o===0)return;t.get(`WEBGL_multi_draw`).multiDrawElementsWEBGL(r,i,0,a,e,0,o);let s=0;for(let e=0;e<o;e++)s+=i[e];n.update(s,r,1)}this.setMode=i,this.setIndex=s,this.render=c,this.renderInstances=l,this.renderMultiDraw=u}function Yc(e){let t={geometries:0,textures:0},n={frame:0,calls:0,triangles:0,points:0,lines:0};function r(t,r,i){switch(n.calls++,r){case e.TRIANGLES:n.triangles+=t/3*i;break;case e.LINES:n.lines+=t/2*i;break;case e.LINE_STRIP:n.lines+=i*(t-1);break;case e.LINE_LOOP:n.lines+=i*t;break;case e.POINTS:n.points+=i*t;break;default:V(`WebGLInfo: Unknown draw mode:`,r)}}function i(){n.calls=0,n.triangles=0,n.points=0,n.lines=0}return{memory:t,render:n,programs:null,autoReset:!0,reset:i,update:r}}function Xc(e,t,n){let r=new WeakMap,i=new Jt;function a(a,o,s){let c=a.morphTargetInfluences,l=o.morphAttributes.position||o.morphAttributes.normal||o.morphAttributes.color,u=l===void 0?0:l.length,d=r.get(o);if(d===void 0||d.count!==u){d!==void 0&&d.texture.dispose();let e=o.morphAttributes.position!==void 0,n=o.morphAttributes.normal!==void 0,a=o.morphAttributes.color!==void 0,s=o.morphAttributes.position||[],c=o.morphAttributes.normal||[],l=o.morphAttributes.color||[],f=0;e===!0&&(f=1),n===!0&&(f=2),a===!0&&(f=3);let p=o.attributes.position.count*f,m=1;p>t.maxTextureSize&&(m=Math.ceil(p/t.maxTextureSize),p=t.maxTextureSize);let h=new Float32Array(p*m*4*u),g=new Zt(h,p,m,u);g.type=v,g.needsUpdate=!0;let _=f*4;for(let t=0;t<u;t++){let r=s[t],o=c[t],u=l[t],d=p*m*4*t;for(let t=0;t<r.count;t++){let s=t*_;e===!0&&(i.fromBufferAttribute(r,t),h[d+s+0]=i.x,h[d+s+1]=i.y,h[d+s+2]=i.z,h[d+s+3]=0),n===!0&&(i.fromBufferAttribute(o,t),h[d+s+4]=i.x,h[d+s+5]=i.y,h[d+s+6]=i.z,h[d+s+7]=0),a===!0&&(i.fromBufferAttribute(u,t),h[d+s+8]=i.x,h[d+s+9]=i.y,h[d+s+10]=i.z,h[d+s+11]=u.itemSize===4?i.w:1)}}d={count:u,texture:g,size:new U(p,m)},r.set(o,d);function y(){g.dispose(),r.delete(o),o.removeEventListener(`dispose`,y)}o.addEventListener(`dispose`,y)}if(a.isInstancedMesh===!0&&a.morphTexture!==null)s.getUniforms().setValue(e,`morphTexture`,a.morphTexture,n);else{let t=0;for(let e=0;e<c.length;e++)t+=c[e];let n=o.morphTargetsRelative?1:1-t;s.getUniforms().setValue(e,`morphTargetBaseInfluence`,n),s.getUniforms().setValue(e,`morphTargetInfluences`,c)}s.getUniforms().setValue(e,`morphTargetsTexture`,d.texture,n),s.getUniforms().setValue(e,`morphTargetsTextureSize`,d.size)}return{update:a}}function Zc(e,t,n,r,i){let a=new WeakMap;function o(r){let o=i.render.frame,s=r.geometry,l=t.get(r,s);if(a.get(l)!==o&&(t.update(l),a.set(l,o)),r.isInstancedMesh&&(r.hasEventListener(`dispose`,c)===!1&&r.addEventListener(`dispose`,c),a.get(r)!==o&&(n.update(r.instanceMatrix,e.ARRAY_BUFFER),r.instanceColor!==null&&n.update(r.instanceColor,e.ARRAY_BUFFER),a.set(r,o))),r.isSkinnedMesh){let e=r.skeleton;a.get(e)!==o&&(e.update(),a.set(e,o))}return l}function s(){a=new WeakMap}function c(e){let t=e.target;t.removeEventListener(`dispose`,c),r.releaseStatesOfObject(t),n.remove(t.instanceMatrix),t.instanceColor!==null&&n.remove(t.instanceColor)}return{update:o,dispose:s}}var Qc={1:`LINEAR_TONE_MAPPING`,2:`REINHARD_TONE_MAPPING`,3:`CINEON_TONE_MAPPING`,4:`ACES_FILMIC_TONE_MAPPING`,6:`AGX_TONE_MAPPING`,7:`NEUTRAL_TONE_MAPPING`,5:`CUSTOM_TONE_MAPPING`};function $c(e,t,n,r,i,a){let o=new Xt(t,n,{type:e,depthBuffer:i,stencilBuffer:a,samples:r?4:0,depthTexture:i?new ia(t,n):void 0}),s=new Xt(t,n,{type:y,depthBuffer:!1,stencilBuffer:!1}),c=new Or;c.setAttribute(`position`,new _r([-1,3,0,-1,-1,0,3,-1,0],3)),c.setAttribute(`uv`,new _r([0,2,0,0,2,0],2));let l=new Ro({uniforms:{tDiffuse:{value:null}},vertexShader:`
			precision highp float;

			uniform mat4 modelViewMatrix;
			uniform mat4 projectionMatrix;

			attribute vec3 position;
			attribute vec2 uv;

			varying vec2 vUv;

			void main() {
				vUv = uv;
				gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
			}`,fragmentShader:`
			precision highp float;

			uniform sampler2D tDiffuse;

			varying vec2 vUv;

			#include <tonemapping_pars_fragment>
			#include <colorspace_pars_fragment>

			void main() {
				gl_FragColor = texture2D( tDiffuse, vUv );

				#ifdef LINEAR_TONE_MAPPING
					gl_FragColor.rgb = LinearToneMapping( gl_FragColor.rgb );
				#elif defined( REINHARD_TONE_MAPPING )
					gl_FragColor.rgb = ReinhardToneMapping( gl_FragColor.rgb );
				#elif defined( CINEON_TONE_MAPPING )
					gl_FragColor.rgb = CineonToneMapping( gl_FragColor.rgb );
				#elif defined( ACES_FILMIC_TONE_MAPPING )
					gl_FragColor.rgb = ACESFilmicToneMapping( gl_FragColor.rgb );
				#elif defined( AGX_TONE_MAPPING )
					gl_FragColor.rgb = AgXToneMapping( gl_FragColor.rgb );
				#elif defined( NEUTRAL_TONE_MAPPING )
					gl_FragColor.rgb = NeutralToneMapping( gl_FragColor.rgb );
				#elif defined( CUSTOM_TONE_MAPPING )
					gl_FragColor.rgb = CustomToneMapping( gl_FragColor.rgb );
				#endif

				#ifdef SRGB_TRANSFER
					gl_FragColor = sRGBTransferOETF( gl_FragColor );
				#endif
			}`,depthTest:!1,depthWrite:!1}),u=new ei(c,l),d=new Is(-1,1,1,-1,0,1),f=null,p=null,m=!1,h,g=null,_=[],v=!1;this.setSize=function(e,t){o.setSize(e,t),s.setSize(e,t);for(let n=0;n<_.length;n++){let r=_[n];r.setSize&&r.setSize(e,t)}},this.setEffects=function(e){_=e,v=_.length>0&&_[0].isRenderPass===!0;let t=o.width,n=o.height;for(let e=0;e<_.length;e++){let r=_[e];r.setSize&&r.setSize(t,n)}},this.begin=function(e,t){if(m||e.toneMapping===0&&_.length===0)return!1;if(g=t,t!==null){let e=t.width,n=t.height;(o.width!==e||o.height!==n)&&this.setSize(e,n)}return v===!1&&e.setRenderTarget(o),h=e.toneMapping,e.toneMapping=0,!0},this.hasRenderPass=function(){return v},this.end=function(e,t){e.toneMapping=h,m=!0;let n=o,r=s;for(let i=0;i<_.length;i++){let a=_[i];if(a.enabled!==!1&&(a.render(e,r,n,t),a.needsSwap!==!1)){let e=n;n=r,r=e}}if(f!==e.outputColorSpace||p!==e.toneMapping){f=e.outputColorSpace,p=e.toneMapping,l.defines={},K.getTransfer(f)===`srgb`&&(l.defines.SRGB_TRANSFER=``);let t=Qc[p];t&&(l.defines[t]=``),l.needsUpdate=!0}l.uniforms.tDiffuse.value=n.texture,e.setRenderTarget(g),e.render(u,d),g=null,m=!1},this.isCompositing=function(){return m},this.dispose=function(){o.depthTexture&&o.depthTexture.dispose(),o.dispose(),s.dispose(),c.dispose(),l.dispose()}}var el=new qt,tl=new ia(1,1),nl=new Zt,rl=new Qt,il=new na,al=[],ol=[],sl=new Float32Array(16),cl=new Float32Array(9),ll=new Float32Array(4);function ul(e,t,n){let r=e[0];if(r<=0||r>0)return e;let i=t*n,a=al[i];if(a===void 0&&(a=new Float32Array(i),al[i]=a),t!==0){r.toArray(a,0);for(let r=1,i=0;r!==t;++r)i+=n,e[r].toArray(a,i)}return a}function dl(e,t){if(e.length!==t.length)return!1;for(let n=0,r=e.length;n<r;n++)if(e[n]!==t[n])return!1;return!0}function fl(e,t){for(let n=0,r=t.length;n<r;n++)e[n]=t[n]}function pl(e,t){let n=ol[t];n===void 0&&(n=new Int32Array(t),ol[t]=n);for(let r=0;r!==t;++r)n[r]=e.allocateTextureUnit();return n}function ml(e,t){let n=this.cache;n[0]!==t&&(e.uniform1f(this.addr,t),n[0]=t)}function hl(e,t){let n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y)&&(e.uniform2f(this.addr,t.x,t.y),n[0]=t.x,n[1]=t.y);else{if(dl(n,t))return;e.uniform2fv(this.addr,t),fl(n,t)}}function gl(e,t){let n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z)&&(e.uniform3f(this.addr,t.x,t.y,t.z),n[0]=t.x,n[1]=t.y,n[2]=t.z);else if(t.r!==void 0)(n[0]!==t.r||n[1]!==t.g||n[2]!==t.b)&&(e.uniform3f(this.addr,t.r,t.g,t.b),n[0]=t.r,n[1]=t.g,n[2]=t.b);else{if(dl(n,t))return;e.uniform3fv(this.addr,t),fl(n,t)}}function _l(e,t){let n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z||n[3]!==t.w)&&(e.uniform4f(this.addr,t.x,t.y,t.z,t.w),n[0]=t.x,n[1]=t.y,n[2]=t.z,n[3]=t.w);else{if(dl(n,t))return;e.uniform4fv(this.addr,t),fl(n,t)}}function vl(e,t){let n=this.cache,r=t.elements;if(r===void 0){if(dl(n,t))return;e.uniformMatrix2fv(this.addr,!1,t),fl(n,t)}else{if(dl(n,r))return;ll.set(r),e.uniformMatrix2fv(this.addr,!1,ll),fl(n,r)}}function yl(e,t){let n=this.cache,r=t.elements;if(r===void 0){if(dl(n,t))return;e.uniformMatrix3fv(this.addr,!1,t),fl(n,t)}else{if(dl(n,r))return;cl.set(r),e.uniformMatrix3fv(this.addr,!1,cl),fl(n,r)}}function bl(e,t){let n=this.cache,r=t.elements;if(r===void 0){if(dl(n,t))return;e.uniformMatrix4fv(this.addr,!1,t),fl(n,t)}else{if(dl(n,r))return;sl.set(r),e.uniformMatrix4fv(this.addr,!1,sl),fl(n,r)}}function xl(e,t){let n=this.cache;n[0]!==t&&(e.uniform1i(this.addr,t),n[0]=t)}function Sl(e,t){let n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y)&&(e.uniform2i(this.addr,t.x,t.y),n[0]=t.x,n[1]=t.y);else{if(dl(n,t))return;e.uniform2iv(this.addr,t),fl(n,t)}}function Cl(e,t){let n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z)&&(e.uniform3i(this.addr,t.x,t.y,t.z),n[0]=t.x,n[1]=t.y,n[2]=t.z);else{if(dl(n,t))return;e.uniform3iv(this.addr,t),fl(n,t)}}function wl(e,t){let n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z||n[3]!==t.w)&&(e.uniform4i(this.addr,t.x,t.y,t.z,t.w),n[0]=t.x,n[1]=t.y,n[2]=t.z,n[3]=t.w);else{if(dl(n,t))return;e.uniform4iv(this.addr,t),fl(n,t)}}function Tl(e,t){let n=this.cache;n[0]!==t&&(e.uniform1ui(this.addr,t),n[0]=t)}function El(e,t){let n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y)&&(e.uniform2ui(this.addr,t.x,t.y),n[0]=t.x,n[1]=t.y);else{if(dl(n,t))return;e.uniform2uiv(this.addr,t),fl(n,t)}}function Dl(e,t){let n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z)&&(e.uniform3ui(this.addr,t.x,t.y,t.z),n[0]=t.x,n[1]=t.y,n[2]=t.z);else{if(dl(n,t))return;e.uniform3uiv(this.addr,t),fl(n,t)}}function Ol(e,t){let n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z||n[3]!==t.w)&&(e.uniform4ui(this.addr,t.x,t.y,t.z,t.w),n[0]=t.x,n[1]=t.y,n[2]=t.z,n[3]=t.w);else{if(dl(n,t))return;e.uniform4uiv(this.addr,t),fl(n,t)}}function kl(e,t,n){let r=this.cache,i=n.allocateTextureUnit();r[0]!==i&&(e.uniform1i(this.addr,i),r[0]=i);let a;this.type===e.SAMPLER_2D_SHADOW?(tl.compareFunction=n.isReversedDepthBuffer()?518:515,a=tl):a=el,n.setTexture2D(t||a,i)}function Al(e,t,n){let r=this.cache,i=n.allocateTextureUnit();r[0]!==i&&(e.uniform1i(this.addr,i),r[0]=i),n.setTexture3D(t||rl,i)}function jl(e,t,n){let r=this.cache,i=n.allocateTextureUnit();r[0]!==i&&(e.uniform1i(this.addr,i),r[0]=i),n.setTextureCube(t||il,i)}function Ml(e,t,n){let r=this.cache,i=n.allocateTextureUnit();r[0]!==i&&(e.uniform1i(this.addr,i),r[0]=i),n.setTexture2DArray(t||nl,i)}function Nl(e){switch(e){case 5126:return ml;case 35664:return hl;case 35665:return gl;case 35666:return _l;case 35674:return vl;case 35675:return yl;case 35676:return bl;case 5124:case 35670:return xl;case 35667:case 35671:return Sl;case 35668:case 35672:return Cl;case 35669:case 35673:return wl;case 5125:return Tl;case 36294:return El;case 36295:return Dl;case 36296:return Ol;case 35678:case 36198:case 36298:case 36306:case 35682:return kl;case 35679:case 36299:case 36307:return Al;case 35680:case 36300:case 36308:case 36293:return jl;case 36289:case 36303:case 36311:case 36292:return Ml}}function Pl(e,t){e.uniform1fv(this.addr,t)}function Fl(e,t){let n=ul(t,this.size,2);e.uniform2fv(this.addr,n)}function Il(e,t){let n=ul(t,this.size,3);e.uniform3fv(this.addr,n)}function Ll(e,t){let n=ul(t,this.size,4);e.uniform4fv(this.addr,n)}function Rl(e,t){let n=ul(t,this.size,4);e.uniformMatrix2fv(this.addr,!1,n)}function zl(e,t){let n=ul(t,this.size,9);e.uniformMatrix3fv(this.addr,!1,n)}function Bl(e,t){let n=ul(t,this.size,16);e.uniformMatrix4fv(this.addr,!1,n)}function Vl(e,t){e.uniform1iv(this.addr,t)}function Hl(e,t){e.uniform2iv(this.addr,t)}function Ul(e,t){e.uniform3iv(this.addr,t)}function Wl(e,t){e.uniform4iv(this.addr,t)}function Gl(e,t){e.uniform1uiv(this.addr,t)}function Kl(e,t){e.uniform2uiv(this.addr,t)}function ql(e,t){e.uniform3uiv(this.addr,t)}function Jl(e,t){e.uniform4uiv(this.addr,t)}function Yl(e,t,n){let r=this.cache,i=t.length,a=pl(n,i);dl(r,a)||(e.uniform1iv(this.addr,a),fl(r,a));let o;o=this.type===e.SAMPLER_2D_SHADOW?tl:el;for(let e=0;e!==i;++e)n.setTexture2D(t[e]||o,a[e])}function Xl(e,t,n){let r=this.cache,i=t.length,a=pl(n,i);dl(r,a)||(e.uniform1iv(this.addr,a),fl(r,a));for(let e=0;e!==i;++e)n.setTexture3D(t[e]||rl,a[e])}function Zl(e,t,n){let r=this.cache,i=t.length,a=pl(n,i);dl(r,a)||(e.uniform1iv(this.addr,a),fl(r,a));for(let e=0;e!==i;++e)n.setTextureCube(t[e]||il,a[e])}function Ql(e,t,n){let r=this.cache,i=t.length,a=pl(n,i);dl(r,a)||(e.uniform1iv(this.addr,a),fl(r,a));for(let e=0;e!==i;++e)n.setTexture2DArray(t[e]||nl,a[e])}function $l(e){switch(e){case 5126:return Pl;case 35664:return Fl;case 35665:return Il;case 35666:return Ll;case 35674:return Rl;case 35675:return zl;case 35676:return Bl;case 5124:case 35670:return Vl;case 35667:case 35671:return Hl;case 35668:case 35672:return Ul;case 35669:case 35673:return Wl;case 5125:return Gl;case 36294:return Kl;case 36295:return ql;case 36296:return Jl;case 35678:case 36198:case 36298:case 36306:case 35682:return Yl;case 35679:case 36299:case 36307:return Xl;case 35680:case 36300:case 36308:case 36293:return Zl;case 36289:case 36303:case 36311:case 36292:return Ql}}var eu=class{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.setValue=Nl(t.type)}},tu=class{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.size=t.size,this.setValue=$l(t.type)}},nu=class{constructor(e){this.id=e,this.seq=[],this.map={}}setValue(e,t,n){let r=this.seq;for(let i=0,a=r.length;i!==a;++i){let a=r[i];a.setValue(e,t[a.id],n)}}},ru=/(\w+)(\])?(\[|\.)?/g;function iu(e,t){e.seq.push(t),e.map[t.id]=t}function au(e,t,n){let r=e.name,i=r.length;for(ru.lastIndex=0;;){let a=ru.exec(r),o=ru.lastIndex,s=a[1],c=a[2]===`]`,l=a[3];if(c&&(s|=0),l===void 0||l===`[`&&o+2===i){iu(n,l===void 0?new eu(s,e,t):new tu(s,e,t));break}{let e=n.map[s];e===void 0&&(e=new nu(s),iu(n,e)),n=e}}}var ou=class{constructor(e,t){this.seq=[],this.map={};let n=e.getProgramParameter(t,e.ACTIVE_UNIFORMS);for(let r=0;r<n;++r){let n=e.getActiveUniform(t,r);au(n,e.getUniformLocation(t,n.name),this)}let r=[],i=[];for(let t of this.seq)t.type===e.SAMPLER_2D_SHADOW||t.type===e.SAMPLER_CUBE_SHADOW||t.type===e.SAMPLER_2D_ARRAY_SHADOW?r.push(t):i.push(t);r.length>0&&(this.seq=r.concat(i))}setValue(e,t,n,r){let i=this.map[t];i!==void 0&&i.setValue(e,n,r)}setOptional(e,t,n){let r=t[n];r!==void 0&&this.setValue(e,n,r)}static upload(e,t,n,r){for(let i=0,a=t.length;i!==a;++i){let a=t[i],o=n[a.id];o.needsUpdate!==!1&&a.setValue(e,o.value,r)}}static seqWithValue(e,t){let n=[];for(let r=0,i=e.length;r!==i;++r){let i=e[r];i.id in t&&n.push(i)}return n}};function su(e,t,n){let r=e.createShader(t);return e.shaderSource(r,n),e.compileShader(r),r}var cu=37297,lu=0;function uu(e,t){let n=e.split(`
`),r=[],i=Math.max(t-6,0),a=Math.min(t+6,n.length);for(let e=i;e<a;e++){let i=e+1;r.push(`${i===t?`>`:` `} ${i}: ${n[e]}`)}return r.join(`
`)}var du=new G;function fu(e){K._getMatrix(du,K.workingColorSpace,e);let t=`mat3( ${du.elements.map(e=>e.toFixed(4))} )`;switch(K.getTransfer(e)){case Ge:return[t,`LinearTransferOETF`];case Ke:return[t,`sRGBTransferOETF`];default:return B(`WebGLProgram: Unsupported color space: `,e),[t,`LinearTransferOETF`]}}function pu(e,t,n){let r=e.getShaderParameter(t,e.COMPILE_STATUS),i=(e.getShaderInfoLog(t)||``).trim();if(r&&i===``)return``;let a=/ERROR: 0:(\d+)/.exec(i);if(a){let r=parseInt(a[1]);return n.toUpperCase()+`

`+i+`

`+uu(e.getShaderSource(t),r)}return i}function mu(e,t){let n=fu(t);return[`vec4 ${e}( vec4 value ) {`,`	return ${n[1]}( vec4( value.rgb * ${n[0]}, value.a ) );`,`}`].join(`
`)}var hu={1:`Linear`,2:`Reinhard`,3:`Cineon`,4:`ACESFilmic`,6:`AgX`,7:`Neutral`,5:`Custom`};function gu(e,t){let n=hu[t];return n===void 0?(B(`WebGLProgram: Unsupported toneMapping:`,t),`vec3 `+e+`( vec3 color ) { return LinearToneMapping( color ); }`):`vec3 `+e+`( vec3 color ) { return `+n+`ToneMapping( color ); }`}var _u=new W;function vu(){return K.getLuminanceCoefficients(_u),[`float luminance( const in vec3 rgb ) {`,`	const vec3 weights = vec3( ${_u.x.toFixed(4)}, ${_u.y.toFixed(4)}, ${_u.z.toFixed(4)} );`,`	return dot( weights, rgb );`,`}`].join(`
`)}function yu(e){return[e.extensionClipCullDistance?`#extension GL_ANGLE_clip_cull_distance : require`:``,e.extensionMultiDraw?`#extension GL_ANGLE_multi_draw : require`:``].filter(Su).join(`
`)}function bu(e){let t=[];for(let n in e){let r=e[n];r!==!1&&t.push(`#define `+n+` `+r)}return t.join(`
`)}function xu(e,t){let n={},r=e.getProgramParameter(t,e.ACTIVE_ATTRIBUTES);for(let i=0;i<r;i++){let r=e.getActiveAttrib(t,i),a=r.name,o=1;r.type===e.FLOAT_MAT2&&(o=2),r.type===e.FLOAT_MAT3&&(o=3),r.type===e.FLOAT_MAT4&&(o=4),n[a]={type:r.type,location:e.getAttribLocation(t,a),locationSize:o}}return n}function Su(e){return e!==``}function Cu(e,t){let n=t.numSpotLightShadows+t.numSpotLightMaps-t.numSpotLightShadowsWithMaps;return e.replace(/NUM_DIR_LIGHTS/g,t.numDirLights).replace(/NUM_SPOT_LIGHTS/g,t.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,t.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,n).replace(/NUM_RECT_AREA_LIGHTS/g,t.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,t.numPointLights).replace(/NUM_HEMI_LIGHTS/g,t.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,t.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,t.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,t.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,t.numPointLightShadows)}function wu(e,t){return e.replace(/NUM_CLIPPING_PLANES/g,t.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,t.numClippingPlanes-t.numClipIntersection)}var Tu=/^[ \t]*#include +<([\w\d./]+)>/gm;function Eu(e){return e.replace(Tu,Ou)}var Du=new Map;function Ou(e,t){let n=mc[t];if(n===void 0){let e=Du.get(t);if(e!==void 0)n=mc[e],B(`WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.`,t,e);else throw Error(`THREE.WebGLProgram: Can not resolve #include <`+t+`>`)}return Eu(n)}var ku=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function Au(e){return e.replace(ku,ju)}function ju(e,t,n,r){let i=``;for(let e=parseInt(t);e<parseInt(n);e++)i+=r.replace(/\[\s*i\s*\]/g,`[ `+e+` ]`).replace(/UNROLLED_LOOP_INDEX/g,e);return i}function Mu(e){let t=`precision ${e.precision} float;
	precision ${e.precision} int;
	precision ${e.precision} sampler2D;
	precision ${e.precision} samplerCube;
	precision ${e.precision} sampler3D;
	precision ${e.precision} sampler2DArray;
	precision ${e.precision} sampler2DShadow;
	precision ${e.precision} samplerCubeShadow;
	precision ${e.precision} sampler2DArrayShadow;
	precision ${e.precision} isampler2D;
	precision ${e.precision} isampler3D;
	precision ${e.precision} isamplerCube;
	precision ${e.precision} isampler2DArray;
	precision ${e.precision} usampler2D;
	precision ${e.precision} usampler3D;
	precision ${e.precision} usamplerCube;
	precision ${e.precision} usampler2DArray;
	`;return e.precision===`highp`?t+=`
#define HIGH_PRECISION`:e.precision===`mediump`?t+=`
#define MEDIUM_PRECISION`:e.precision===`lowp`&&(t+=`
#define LOW_PRECISION`),t}var Nu={1:`SHADOWMAP_TYPE_PCF`,3:`SHADOWMAP_TYPE_VSM`};function Pu(e){return Nu[e.shadowMapType]||`SHADOWMAP_TYPE_BASIC`}var Fu={301:`ENVMAP_TYPE_CUBE`,302:`ENVMAP_TYPE_CUBE`,306:`ENVMAP_TYPE_CUBE_UV`};function Iu(e){return e.envMap===!1?`ENVMAP_TYPE_CUBE`:Fu[e.envMapMode]||`ENVMAP_TYPE_CUBE`}var Lu={302:`ENVMAP_MODE_REFRACTION`};function Ru(e){return e.envMap===!1?`ENVMAP_MODE_REFLECTION`:Lu[e.envMapMode]||`ENVMAP_MODE_REFLECTION`}var zu={0:`ENVMAP_BLENDING_MULTIPLY`,1:`ENVMAP_BLENDING_MIX`,2:`ENVMAP_BLENDING_ADD`};function Bu(e){return e.envMap===!1?`ENVMAP_BLENDING_NONE`:zu[e.combine]||`ENVMAP_BLENDING_NONE`}function Vu(e){let t=e.envMapCubeUVHeight;if(t===null)return null;let n=Math.log2(t)-2,r=1/t;return{texelWidth:1/(3*Math.max(2**n,112)),texelHeight:r,maxMip:n}}function Hu(e,t,n,r){let i=e.getContext(),a=n.defines,o=n.vertexShader,s=n.fragmentShader,c=Pu(n),l=Iu(n),u=Ru(n),d=Bu(n),f=Vu(n),p=yu(n),m=bu(a),h=i.createProgram(),g,_,v=n.glslVersion?`#version `+n.glslVersion+`
`:``;n.isRawShaderMaterial?(g=[`#define SHADER_TYPE `+n.shaderType,`#define SHADER_NAME `+n.shaderName,m].filter(Su).join(`
`),g.length>0&&(g+=`
`),_=[`#define SHADER_TYPE `+n.shaderType,`#define SHADER_NAME `+n.shaderName,m].filter(Su).join(`
`),_.length>0&&(_+=`
`)):(g=[Mu(n),`#define SHADER_TYPE `+n.shaderType,`#define SHADER_NAME `+n.shaderName,m,n.extensionClipCullDistance?`#define USE_CLIP_DISTANCE`:``,n.batching?`#define USE_BATCHING`:``,n.batchingColor?`#define USE_BATCHING_COLOR`:``,n.instancing?`#define USE_INSTANCING`:``,n.instancingColor?`#define USE_INSTANCING_COLOR`:``,n.instancingMorph?`#define USE_INSTANCING_MORPH`:``,n.useFog&&n.fog?`#define USE_FOG`:``,n.useFog&&n.fogExp2?`#define FOG_EXP2`:``,n.map?`#define USE_MAP`:``,n.envMap?`#define USE_ENVMAP`:``,n.envMap?`#define `+u:``,n.lightMap?`#define USE_LIGHTMAP`:``,n.aoMap?`#define USE_AOMAP`:``,n.bumpMap?`#define USE_BUMPMAP`:``,n.normalMap?`#define USE_NORMALMAP`:``,n.normalMapObjectSpace?`#define USE_NORMALMAP_OBJECTSPACE`:``,n.normalMapTangentSpace?`#define USE_NORMALMAP_TANGENTSPACE`:``,n.displacementMap?`#define USE_DISPLACEMENTMAP`:``,n.emissiveMap?`#define USE_EMISSIVEMAP`:``,n.anisotropy?`#define USE_ANISOTROPY`:``,n.anisotropyMap?`#define USE_ANISOTROPYMAP`:``,n.clearcoatMap?`#define USE_CLEARCOATMAP`:``,n.clearcoatRoughnessMap?`#define USE_CLEARCOAT_ROUGHNESSMAP`:``,n.clearcoatNormalMap?`#define USE_CLEARCOAT_NORMALMAP`:``,n.iridescenceMap?`#define USE_IRIDESCENCEMAP`:``,n.iridescenceThicknessMap?`#define USE_IRIDESCENCE_THICKNESSMAP`:``,n.specularMap?`#define USE_SPECULARMAP`:``,n.specularColorMap?`#define USE_SPECULAR_COLORMAP`:``,n.specularIntensityMap?`#define USE_SPECULAR_INTENSITYMAP`:``,n.roughnessMap?`#define USE_ROUGHNESSMAP`:``,n.metalnessMap?`#define USE_METALNESSMAP`:``,n.alphaMap?`#define USE_ALPHAMAP`:``,n.alphaHash?`#define USE_ALPHAHASH`:``,n.transmission?`#define USE_TRANSMISSION`:``,n.transmissionMap?`#define USE_TRANSMISSIONMAP`:``,n.thicknessMap?`#define USE_THICKNESSMAP`:``,n.sheenColorMap?`#define USE_SHEEN_COLORMAP`:``,n.sheenRoughnessMap?`#define USE_SHEEN_ROUGHNESSMAP`:``,n.mapUv?`#define MAP_UV `+n.mapUv:``,n.alphaMapUv?`#define ALPHAMAP_UV `+n.alphaMapUv:``,n.lightMapUv?`#define LIGHTMAP_UV `+n.lightMapUv:``,n.aoMapUv?`#define AOMAP_UV `+n.aoMapUv:``,n.emissiveMapUv?`#define EMISSIVEMAP_UV `+n.emissiveMapUv:``,n.bumpMapUv?`#define BUMPMAP_UV `+n.bumpMapUv:``,n.normalMapUv?`#define NORMALMAP_UV `+n.normalMapUv:``,n.displacementMapUv?`#define DISPLACEMENTMAP_UV `+n.displacementMapUv:``,n.metalnessMapUv?`#define METALNESSMAP_UV `+n.metalnessMapUv:``,n.roughnessMapUv?`#define ROUGHNESSMAP_UV `+n.roughnessMapUv:``,n.anisotropyMapUv?`#define ANISOTROPYMAP_UV `+n.anisotropyMapUv:``,n.clearcoatMapUv?`#define CLEARCOATMAP_UV `+n.clearcoatMapUv:``,n.clearcoatNormalMapUv?`#define CLEARCOAT_NORMALMAP_UV `+n.clearcoatNormalMapUv:``,n.clearcoatRoughnessMapUv?`#define CLEARCOAT_ROUGHNESSMAP_UV `+n.clearcoatRoughnessMapUv:``,n.iridescenceMapUv?`#define IRIDESCENCEMAP_UV `+n.iridescenceMapUv:``,n.iridescenceThicknessMapUv?`#define IRIDESCENCE_THICKNESSMAP_UV `+n.iridescenceThicknessMapUv:``,n.sheenColorMapUv?`#define SHEEN_COLORMAP_UV `+n.sheenColorMapUv:``,n.sheenRoughnessMapUv?`#define SHEEN_ROUGHNESSMAP_UV `+n.sheenRoughnessMapUv:``,n.specularMapUv?`#define SPECULARMAP_UV `+n.specularMapUv:``,n.specularColorMapUv?`#define SPECULAR_COLORMAP_UV `+n.specularColorMapUv:``,n.specularIntensityMapUv?`#define SPECULAR_INTENSITYMAP_UV `+n.specularIntensityMapUv:``,n.transmissionMapUv?`#define TRANSMISSIONMAP_UV `+n.transmissionMapUv:``,n.thicknessMapUv?`#define THICKNESSMAP_UV `+n.thicknessMapUv:``,n.vertexTangents&&n.flatShading===!1?`#define USE_TANGENT`:``,n.vertexNormals?`#define HAS_NORMAL`:``,n.vertexColors?`#define USE_COLOR`:``,n.vertexAlphas?`#define USE_COLOR_ALPHA`:``,n.vertexUv1s?`#define USE_UV1`:``,n.vertexUv2s?`#define USE_UV2`:``,n.vertexUv3s?`#define USE_UV3`:``,n.pointsUvs?`#define USE_POINTS_UV`:``,n.flatShading?`#define FLAT_SHADED`:``,n.skinning?`#define USE_SKINNING`:``,n.morphTargets?`#define USE_MORPHTARGETS`:``,n.morphNormals&&n.flatShading===!1?`#define USE_MORPHNORMALS`:``,n.morphColors?`#define USE_MORPHCOLORS`:``,n.morphTargetsCount>0?`#define MORPHTARGETS_TEXTURE_STRIDE `+n.morphTextureStride:``,n.morphTargetsCount>0?`#define MORPHTARGETS_COUNT `+n.morphTargetsCount:``,n.doubleSided?`#define DOUBLE_SIDED`:``,n.flipSided?`#define FLIP_SIDED`:``,n.shadowMapEnabled?`#define USE_SHADOWMAP`:``,n.shadowMapEnabled?`#define `+c:``,n.sizeAttenuation?`#define USE_SIZEATTENUATION`:``,n.numLightProbes>0?`#define USE_LIGHT_PROBES`:``,n.logarithmicDepthBuffer?`#define USE_LOGARITHMIC_DEPTH_BUFFER`:``,n.reversedDepthBuffer?`#define USE_REVERSED_DEPTH_BUFFER`:``,`uniform mat4 modelMatrix;`,`uniform mat4 modelViewMatrix;`,`uniform mat4 projectionMatrix;`,`uniform mat4 viewMatrix;`,`uniform mat3 normalMatrix;`,`uniform vec3 cameraPosition;`,`uniform bool isOrthographic;`,`#ifdef USE_INSTANCING`,`	attribute mat4 instanceMatrix;`,`#endif`,`#ifdef USE_INSTANCING_COLOR`,`	attribute vec3 instanceColor;`,`#endif`,`#ifdef USE_INSTANCING_MORPH`,`	uniform sampler2D morphTexture;`,`#endif`,`attribute vec3 position;`,`attribute vec3 normal;`,`attribute vec2 uv;`,`#ifdef USE_UV1`,`	attribute vec2 uv1;`,`#endif`,`#ifdef USE_UV2`,`	attribute vec2 uv2;`,`#endif`,`#ifdef USE_UV3`,`	attribute vec2 uv3;`,`#endif`,`#ifdef USE_TANGENT`,`	attribute vec4 tangent;`,`#endif`,`#if defined( USE_COLOR_ALPHA )`,`	attribute vec4 color;`,`#elif defined( USE_COLOR )`,`	attribute vec3 color;`,`#endif`,`#ifdef USE_SKINNING`,`	attribute vec4 skinIndex;`,`	attribute vec4 skinWeight;`,`#endif`,`
`].filter(Su).join(`
`),_=[Mu(n),`#define SHADER_TYPE `+n.shaderType,`#define SHADER_NAME `+n.shaderName,m,n.useFog&&n.fog?`#define USE_FOG`:``,n.useFog&&n.fogExp2?`#define FOG_EXP2`:``,n.alphaToCoverage?`#define ALPHA_TO_COVERAGE`:``,n.map?`#define USE_MAP`:``,n.matcap?`#define USE_MATCAP`:``,n.envMap?`#define USE_ENVMAP`:``,n.envMap?`#define `+l:``,n.envMap?`#define `+u:``,n.envMap?`#define `+d:``,f?`#define CUBEUV_TEXEL_WIDTH `+f.texelWidth:``,f?`#define CUBEUV_TEXEL_HEIGHT `+f.texelHeight:``,f?`#define CUBEUV_MAX_MIP `+f.maxMip+`.0`:``,n.lightMap?`#define USE_LIGHTMAP`:``,n.aoMap?`#define USE_AOMAP`:``,n.bumpMap?`#define USE_BUMPMAP`:``,n.normalMap?`#define USE_NORMALMAP`:``,n.normalMapObjectSpace?`#define USE_NORMALMAP_OBJECTSPACE`:``,n.normalMapTangentSpace?`#define USE_NORMALMAP_TANGENTSPACE`:``,n.packedNormalMap?`#define USE_PACKED_NORMALMAP`:``,n.emissiveMap?`#define USE_EMISSIVEMAP`:``,n.anisotropy?`#define USE_ANISOTROPY`:``,n.anisotropyMap?`#define USE_ANISOTROPYMAP`:``,n.clearcoat?`#define USE_CLEARCOAT`:``,n.clearcoatMap?`#define USE_CLEARCOATMAP`:``,n.clearcoatRoughnessMap?`#define USE_CLEARCOAT_ROUGHNESSMAP`:``,n.clearcoatNormalMap?`#define USE_CLEARCOAT_NORMALMAP`:``,n.dispersion?`#define USE_DISPERSION`:``,n.iridescence?`#define USE_IRIDESCENCE`:``,n.iridescenceMap?`#define USE_IRIDESCENCEMAP`:``,n.iridescenceThicknessMap?`#define USE_IRIDESCENCE_THICKNESSMAP`:``,n.specularMap?`#define USE_SPECULARMAP`:``,n.specularColorMap?`#define USE_SPECULAR_COLORMAP`:``,n.specularIntensityMap?`#define USE_SPECULAR_INTENSITYMAP`:``,n.roughnessMap?`#define USE_ROUGHNESSMAP`:``,n.metalnessMap?`#define USE_METALNESSMAP`:``,n.alphaMap?`#define USE_ALPHAMAP`:``,n.alphaTest?`#define USE_ALPHATEST`:``,n.alphaHash?`#define USE_ALPHAHASH`:``,n.sheen?`#define USE_SHEEN`:``,n.sheenColorMap?`#define USE_SHEEN_COLORMAP`:``,n.sheenRoughnessMap?`#define USE_SHEEN_ROUGHNESSMAP`:``,n.transmission?`#define USE_TRANSMISSION`:``,n.transmissionMap?`#define USE_TRANSMISSIONMAP`:``,n.thicknessMap?`#define USE_THICKNESSMAP`:``,n.vertexTangents&&n.flatShading===!1?`#define USE_TANGENT`:``,n.vertexColors||n.instancingColor?`#define USE_COLOR`:``,n.vertexAlphas||n.batchingColor?`#define USE_COLOR_ALPHA`:``,n.vertexUv1s?`#define USE_UV1`:``,n.vertexUv2s?`#define USE_UV2`:``,n.vertexUv3s?`#define USE_UV3`:``,n.pointsUvs?`#define USE_POINTS_UV`:``,n.gradientMap?`#define USE_GRADIENTMAP`:``,n.flatShading?`#define FLAT_SHADED`:``,n.doubleSided?`#define DOUBLE_SIDED`:``,n.flipSided?`#define FLIP_SIDED`:``,n.shadowMapEnabled?`#define USE_SHADOWMAP`:``,n.shadowMapEnabled?`#define `+c:``,n.premultipliedAlpha?`#define PREMULTIPLIED_ALPHA`:``,n.numLightProbes>0?`#define USE_LIGHT_PROBES`:``,n.numLightProbeGrids>0?`#define USE_LIGHT_PROBES_GRID`:``,n.decodeVideoTexture?`#define DECODE_VIDEO_TEXTURE`:``,n.decodeVideoTextureEmissive?`#define DECODE_VIDEO_TEXTURE_EMISSIVE`:``,n.logarithmicDepthBuffer?`#define USE_LOGARITHMIC_DEPTH_BUFFER`:``,n.reversedDepthBuffer?`#define USE_REVERSED_DEPTH_BUFFER`:``,`uniform mat4 viewMatrix;`,`uniform vec3 cameraPosition;`,`uniform bool isOrthographic;`,n.toneMapping===0?``:`#define TONE_MAPPING`,n.toneMapping===0?``:mc.tonemapping_pars_fragment,n.toneMapping===0?``:gu(`toneMapping`,n.toneMapping),n.dithering?`#define DITHERING`:``,n.opaque?`#define OPAQUE`:``,mc.colorspace_pars_fragment,mu(`linearToOutputTexel`,n.outputColorSpace),vu(),n.useDepthPacking?`#define DEPTH_PACKING `+n.depthPacking:``,`
`].filter(Su).join(`
`)),o=Eu(o),o=Cu(o,n),o=wu(o,n),s=Eu(s),s=Cu(s,n),s=wu(s,n),o=Au(o),s=Au(s),n.isRawShaderMaterial!==!0&&(v=`#version 300 es
`,g=[p,`#define attribute in`,`#define varying out`,`#define texture2D texture`].join(`
`)+`
`+g,_=[`#define varying in`,n.glslVersion===`300 es`?``:`layout(location = 0) out highp vec4 pc_fragColor;`,n.glslVersion===`300 es`?``:`#define gl_FragColor pc_fragColor`,`#define gl_FragDepthEXT gl_FragDepth`,`#define texture2D texture`,`#define textureCube texture`,`#define texture2DProj textureProj`,`#define texture2DLodEXT textureLod`,`#define texture2DProjLodEXT textureProjLod`,`#define textureCubeLodEXT textureLod`,`#define texture2DGradEXT textureGrad`,`#define texture2DProjGradEXT textureProjGrad`,`#define textureCubeGradEXT textureGrad`].join(`
`)+`
`+_);let y=v+g+o,b=v+_+s,x=su(i,i.VERTEX_SHADER,y),S=su(i,i.FRAGMENT_SHADER,b);i.attachShader(h,x),i.attachShader(h,S),n.index0AttributeName===void 0?n.hasPositionAttribute===!0&&i.bindAttribLocation(h,0,`position`):i.bindAttribLocation(h,0,n.index0AttributeName),i.linkProgram(h);function C(t){if(e.debug.checkShaderErrors){let n=i.getProgramInfoLog(h)||``,r=i.getShaderInfoLog(x)||``,a=i.getShaderInfoLog(S)||``,o=n.trim(),s=r.trim(),c=a.trim(),l=!0,u=!0;if(i.getProgramParameter(h,i.LINK_STATUS)===!1){if(l=!1,typeof e.debug.onShaderError==`function`)e.debug.onShaderError(i,h,x,S);else{let e=pu(i,x,`vertex`),n=pu(i,S,`fragment`);V(`WebGLProgram: Shader Error `+i.getError()+` - VALIDATE_STATUS `+i.getProgramParameter(h,i.VALIDATE_STATUS)+`

Material Name: `+t.name+`
Material Type: `+t.type+`

Program Info Log: `+o+`
`+e+`
`+n)}}else o===``?(s===``||c===``)&&(u=!1):B(`WebGLProgram: Program Info Log:`,o);u&&(t.diagnostics={runnable:l,programLog:o,vertexShader:{log:s,prefix:g},fragmentShader:{log:c,prefix:_}})}i.deleteShader(x),i.deleteShader(S),w=new ou(i,h),T=xu(i,h)}let w;this.getUniforms=function(){return w===void 0&&C(this),w};let T;this.getAttributes=function(){return T===void 0&&C(this),T};let E=n.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return E===!1&&(E=i.getProgramParameter(h,cu)),E},this.destroy=function(){r.releaseStatesOfProgram(this),i.deleteProgram(h),this.program=void 0},this.type=n.shaderType,this.name=n.shaderName,this.id=lu++,this.cacheKey=t,this.usedTimes=1,this.program=h,this.vertexShader=x,this.fragmentShader=S,this}var Uu=0,Wu=class{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(e,t,n){let r=this._getShaderCacheForMaterial(e);return r.has(t)===!1&&(r.add(t),t.usedTimes++),r.has(n)===!1&&(r.add(n),n.usedTimes++),this}remove(e){let t=this.materialCache.get(e);for(let e of t)e.usedTimes--,e.usedTimes===0&&this.shaderCache.delete(e.code);return this.materialCache.delete(e),this}getVertexShaderStage(e){return this._getShaderStage(e.vertexShader)}getFragmentShaderStage(e){return this._getShaderStage(e.fragmentShader)}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(e){let t=this.materialCache,n=t.get(e);return n===void 0&&(n=new Set,t.set(e,n)),n}_getShaderStage(e){let t=this.shaderCache,n=t.get(e);return n===void 0&&(n=new Gu(e),t.set(e,n)),n}},Gu=class{constructor(e){this.id=Uu++,this.code=e,this.usedTimes=0}};function Ku(e){return e===1030||e===37490||e===36285}function qu(e,t,n,r,i,a){let o=new un,s=new Wu,c=new Set,l=[],u=new Map,d=r.logarithmicDepthBuffer,f=r.precision,p={MeshDepthMaterial:`depth`,MeshDistanceMaterial:`distance`,MeshNormalMaterial:`normal`,MeshBasicMaterial:`basic`,MeshLambertMaterial:`lambert`,MeshPhongMaterial:`phong`,MeshToonMaterial:`toon`,MeshStandardMaterial:`physical`,MeshPhysicalMaterial:`physical`,MeshMatcapMaterial:`matcap`,LineBasicMaterial:`basic`,LineDashedMaterial:`dashed`,PointsMaterial:`points`,ShadowMaterial:`shadow`,SpriteMaterial:`sprite`};function m(e){return c.add(e),e===0?`uv`:`uv${e}`}function h(i,o,l,u,h,g){let _=u.fog,v=h.geometry,y=i.isMeshStandardMaterial||i.isMeshLambertMaterial||i.isMeshPhongMaterial?u.environment:null,b=i.isMeshStandardMaterial||i.isMeshLambertMaterial&&!i.envMap||i.isMeshPhongMaterial&&!i.envMap,x=t.get(i.envMap||y,b),S=x&&x.mapping===306?x.image.height:null,C=p[i.type];i.precision!==null&&(f=r.getMaxPrecision(i.precision),f!==i.precision&&B(`WebGLProgram.getParameters:`,i.precision,`not supported, using`,f,`instead.`));let w=v.morphAttributes.position||v.morphAttributes.normal||v.morphAttributes.color,T=w===void 0?0:w.length,E=0;v.morphAttributes.position!==void 0&&(E=1),v.morphAttributes.normal!==void 0&&(E=2),v.morphAttributes.color!==void 0&&(E=3);let D,O,k,A;if(C){let e=hc[C];D=e.vertexShader,O=e.fragmentShader}else{D=i.vertexShader,O=i.fragmentShader;let e=s.getVertexShaderStage(i),t=s.getFragmentShaderStage(i);s.update(i,e,t),k=e.id,A=t.id}let ee=e.getRenderTarget(),te=e.state.buffers.depth.getReversed(),j=h.isInstancedMesh===!0,ne=h.isBatchedMesh===!0,M=!!i.map,N=!!i.matcap,re=!!x,ie=!!i.aoMap,ae=!!i.lightMap,oe=!!i.bumpMap&&i.wireframe===!1,se=!!i.normalMap,ce=!!i.displacementMap,le=!!i.emissiveMap,P=!!i.metalnessMap,ue=!!i.roughnessMap,de=i.anisotropy>0,fe=i.clearcoat>0,pe=i.dispersion>0,me=i.iridescence>0,F=i.sheen>0,he=i.transmission>0,ge=de&&!!i.anisotropyMap,_e=fe&&!!i.clearcoatMap,ve=fe&&!!i.clearcoatNormalMap,ye=fe&&!!i.clearcoatRoughnessMap,be=me&&!!i.iridescenceMap,xe=me&&!!i.iridescenceThicknessMap,Se=F&&!!i.sheenColorMap,Ce=F&&!!i.sheenRoughnessMap,we=!!i.specularMap,Te=!!i.specularColorMap,Ee=!!i.specularIntensityMap,De=he&&!!i.transmissionMap,Oe=he&&!!i.thicknessMap,ke=!!i.gradientMap,Ae=!!i.alphaMap,je=i.alphaTest>0,Me=!!i.alphaHash,I=!!i.extensions,Ne=0;i.toneMapped&&(ee===null||ee.isXRRenderTarget===!0)&&(Ne=e.toneMapping);let Pe={shaderID:C,shaderType:i.type,shaderName:i.name,vertexShader:D,fragmentShader:O,defines:i.defines,customVertexShaderID:k,customFragmentShaderID:A,isRawShaderMaterial:i.isRawShaderMaterial===!0,glslVersion:i.glslVersion,precision:f,batching:ne,batchingColor:ne&&h._colorsTexture!==null,instancing:j,instancingColor:j&&h.instanceColor!==null,instancingMorph:j&&h.morphTexture!==null,outputColorSpace:ee===null?e.outputColorSpace:ee.isXRRenderTarget===!0?ee.texture.colorSpace:K.workingColorSpace,alphaToCoverage:!!i.alphaToCoverage,map:M,matcap:N,envMap:re,envMapMode:re&&x.mapping,envMapCubeUVHeight:S,aoMap:ie,lightMap:ae,bumpMap:oe,normalMap:se,displacementMap:ce,emissiveMap:le,normalMapObjectSpace:se&&i.normalMapType===1,normalMapTangentSpace:se&&i.normalMapType===0,packedNormalMap:se&&i.normalMapType===0&&Ku(i.normalMap.format),metalnessMap:P,roughnessMap:ue,anisotropy:de,anisotropyMap:ge,clearcoat:fe,clearcoatMap:_e,clearcoatNormalMap:ve,clearcoatRoughnessMap:ye,dispersion:pe,iridescence:me,iridescenceMap:be,iridescenceThicknessMap:xe,sheen:F,sheenColorMap:Se,sheenRoughnessMap:Ce,specularMap:we,specularColorMap:Te,specularIntensityMap:Ee,transmission:he,transmissionMap:De,thicknessMap:Oe,gradientMap:ke,opaque:i.transparent===!1&&i.blending===1&&i.alphaToCoverage===!1,alphaMap:Ae,alphaTest:je,alphaHash:Me,combine:i.combine,mapUv:M&&m(i.map.channel),aoMapUv:ie&&m(i.aoMap.channel),lightMapUv:ae&&m(i.lightMap.channel),bumpMapUv:oe&&m(i.bumpMap.channel),normalMapUv:se&&m(i.normalMap.channel),displacementMapUv:ce&&m(i.displacementMap.channel),emissiveMapUv:le&&m(i.emissiveMap.channel),metalnessMapUv:P&&m(i.metalnessMap.channel),roughnessMapUv:ue&&m(i.roughnessMap.channel),anisotropyMapUv:ge&&m(i.anisotropyMap.channel),clearcoatMapUv:_e&&m(i.clearcoatMap.channel),clearcoatNormalMapUv:ve&&m(i.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:ye&&m(i.clearcoatRoughnessMap.channel),iridescenceMapUv:be&&m(i.iridescenceMap.channel),iridescenceThicknessMapUv:xe&&m(i.iridescenceThicknessMap.channel),sheenColorMapUv:Se&&m(i.sheenColorMap.channel),sheenRoughnessMapUv:Ce&&m(i.sheenRoughnessMap.channel),specularMapUv:we&&m(i.specularMap.channel),specularColorMapUv:Te&&m(i.specularColorMap.channel),specularIntensityMapUv:Ee&&m(i.specularIntensityMap.channel),transmissionMapUv:De&&m(i.transmissionMap.channel),thicknessMapUv:Oe&&m(i.thicknessMap.channel),alphaMapUv:Ae&&m(i.alphaMap.channel),vertexTangents:!!v.attributes.tangent&&(se||de),vertexNormals:!!v.attributes.normal,vertexColors:i.vertexColors,vertexAlphas:i.vertexColors===!0&&!!v.attributes.color&&v.attributes.color.itemSize===4,pointsUvs:h.isPoints===!0&&!!v.attributes.uv&&(M||Ae),fog:!!_,useFog:i.fog===!0,fogExp2:!!_&&_.isFogExp2,flatShading:i.wireframe===!1&&(i.flatShading===!0||v.attributes.normal===void 0&&se===!1&&(i.isMeshLambertMaterial||i.isMeshPhongMaterial||i.isMeshStandardMaterial||i.isMeshPhysicalMaterial)),sizeAttenuation:i.sizeAttenuation===!0,logarithmicDepthBuffer:d,reversedDepthBuffer:te,skinning:h.isSkinnedMesh===!0,hasPositionAttribute:v.attributes.position!==void 0,morphTargets:v.morphAttributes.position!==void 0,morphNormals:v.morphAttributes.normal!==void 0,morphColors:v.morphAttributes.color!==void 0,morphTargetsCount:T,morphTextureStride:E,numDirLights:o.directional.length,numPointLights:o.point.length,numSpotLights:o.spot.length,numSpotLightMaps:o.spotLightMap.length,numRectAreaLights:o.rectArea.length,numHemiLights:o.hemi.length,numDirLightShadows:o.directionalShadowMap.length,numPointLightShadows:o.pointShadowMap.length,numSpotLightShadows:o.spotShadowMap.length,numSpotLightShadowsWithMaps:o.numSpotLightShadowsWithMaps,numLightProbes:o.numLightProbes,numLightProbeGrids:g.length,numClippingPlanes:a.numPlanes,numClipIntersection:a.numIntersection,dithering:i.dithering,shadowMapEnabled:e.shadowMap.enabled&&l.length>0,shadowMapType:e.shadowMap.type,toneMapping:Ne,decodeVideoTexture:M&&i.map.isVideoTexture===!0&&K.getTransfer(i.map.colorSpace)===`srgb`,decodeVideoTextureEmissive:le&&i.emissiveMap.isVideoTexture===!0&&K.getTransfer(i.emissiveMap.colorSpace)===`srgb`,premultipliedAlpha:i.premultipliedAlpha,doubleSided:i.side===2,flipSided:i.side===1,useDepthPacking:i.depthPacking>=0,depthPacking:i.depthPacking||0,index0AttributeName:i.index0AttributeName,extensionClipCullDistance:I&&i.extensions.clipCullDistance===!0&&n.has(`WEBGL_clip_cull_distance`),extensionMultiDraw:(I&&i.extensions.multiDraw===!0||ne)&&n.has(`WEBGL_multi_draw`),rendererExtensionParallelShaderCompile:n.has(`KHR_parallel_shader_compile`),customProgramCacheKey:i.customProgramCacheKey()};return Pe.vertexUv1s=c.has(1),Pe.vertexUv2s=c.has(2),Pe.vertexUv3s=c.has(3),c.clear(),Pe}function g(t){let n=[];if(t.shaderID?n.push(t.shaderID):(n.push(t.customVertexShaderID),n.push(t.customFragmentShaderID)),t.defines!==void 0)for(let e in t.defines)n.push(e),n.push(t.defines[e]);return t.isRawShaderMaterial===!1&&(_(n,t),v(n,t),n.push(e.outputColorSpace)),n.push(t.customProgramCacheKey),n.join()}function _(e,t){e.push(t.precision),e.push(t.outputColorSpace),e.push(t.envMapMode),e.push(t.envMapCubeUVHeight),e.push(t.mapUv),e.push(t.alphaMapUv),e.push(t.lightMapUv),e.push(t.aoMapUv),e.push(t.bumpMapUv),e.push(t.normalMapUv),e.push(t.displacementMapUv),e.push(t.emissiveMapUv),e.push(t.metalnessMapUv),e.push(t.roughnessMapUv),e.push(t.anisotropyMapUv),e.push(t.clearcoatMapUv),e.push(t.clearcoatNormalMapUv),e.push(t.clearcoatRoughnessMapUv),e.push(t.iridescenceMapUv),e.push(t.iridescenceThicknessMapUv),e.push(t.sheenColorMapUv),e.push(t.sheenRoughnessMapUv),e.push(t.specularMapUv),e.push(t.specularColorMapUv),e.push(t.specularIntensityMapUv),e.push(t.transmissionMapUv),e.push(t.thicknessMapUv),e.push(t.combine),e.push(t.fogExp2),e.push(t.sizeAttenuation),e.push(t.morphTargetsCount),e.push(t.morphAttributeCount),e.push(t.numDirLights),e.push(t.numPointLights),e.push(t.numSpotLights),e.push(t.numSpotLightMaps),e.push(t.numHemiLights),e.push(t.numRectAreaLights),e.push(t.numDirLightShadows),e.push(t.numPointLightShadows),e.push(t.numSpotLightShadows),e.push(t.numSpotLightShadowsWithMaps),e.push(t.numLightProbes),e.push(t.shadowMapType),e.push(t.toneMapping),e.push(t.numClippingPlanes),e.push(t.numClipIntersection),e.push(t.depthPacking)}function v(e,t){o.disableAll(),t.instancing&&o.enable(0),t.instancingColor&&o.enable(1),t.instancingMorph&&o.enable(2),t.matcap&&o.enable(3),t.envMap&&o.enable(4),t.normalMapObjectSpace&&o.enable(5),t.normalMapTangentSpace&&o.enable(6),t.clearcoat&&o.enable(7),t.iridescence&&o.enable(8),t.alphaTest&&o.enable(9),t.vertexColors&&o.enable(10),t.vertexAlphas&&o.enable(11),t.vertexUv1s&&o.enable(12),t.vertexUv2s&&o.enable(13),t.vertexUv3s&&o.enable(14),t.vertexTangents&&o.enable(15),t.anisotropy&&o.enable(16),t.alphaHash&&o.enable(17),t.batching&&o.enable(18),t.dispersion&&o.enable(19),t.batchingColor&&o.enable(20),t.gradientMap&&o.enable(21),t.packedNormalMap&&o.enable(22),t.vertexNormals&&o.enable(23),e.push(o.mask),o.disableAll(),t.fog&&o.enable(0),t.useFog&&o.enable(1),t.flatShading&&o.enable(2),t.logarithmicDepthBuffer&&o.enable(3),t.reversedDepthBuffer&&o.enable(4),t.skinning&&o.enable(5),t.morphTargets&&o.enable(6),t.morphNormals&&o.enable(7),t.morphColors&&o.enable(8),t.premultipliedAlpha&&o.enable(9),t.shadowMapEnabled&&o.enable(10),t.doubleSided&&o.enable(11),t.flipSided&&o.enable(12),t.useDepthPacking&&o.enable(13),t.dithering&&o.enable(14),t.transmission&&o.enable(15),t.sheen&&o.enable(16),t.opaque&&o.enable(17),t.pointsUvs&&o.enable(18),t.decodeVideoTexture&&o.enable(19),t.decodeVideoTextureEmissive&&o.enable(20),t.alphaToCoverage&&o.enable(21),t.numLightProbeGrids>0&&o.enable(22),t.hasPositionAttribute&&o.enable(23),e.push(o.mask)}function y(e){let t=p[e.type],n;if(t){let e=hc[t];n=Po.clone(e.uniforms)}else n=e.uniforms;return n}function b(t,n){let r=u.get(n);return r===void 0?(r=new Hu(e,n,t,i),l.push(r),u.set(n,r)):++r.usedTimes,r}function x(e){if(--e.usedTimes===0){let t=l.indexOf(e);l[t]=l[l.length-1],l.pop(),u.delete(e.cacheKey),e.destroy()}}function S(e){s.remove(e)}function C(){s.dispose()}return{getParameters:h,getProgramCacheKey:g,getUniforms:y,acquireProgram:b,releaseProgram:x,releaseShaderCache:S,programs:l,dispose:C}}function Ju(){let e=new WeakMap;function t(t){return e.has(t)}function n(t){let n=e.get(t);return n===void 0&&(n={},e.set(t,n)),n}function r(t){e.delete(t)}function i(t,n,r){e.get(t)[n]=r}function a(){e=new WeakMap}return{has:t,get:n,remove:r,update:i,dispose:a}}function Yu(e,t){return e.groupOrder===t.groupOrder?e.renderOrder===t.renderOrder?e.material.id===t.material.id?e.materialVariant===t.materialVariant?e.z===t.z?e.id-t.id:e.z-t.z:e.materialVariant-t.materialVariant:e.material.id-t.material.id:e.renderOrder-t.renderOrder:e.groupOrder-t.groupOrder}function Xu(e,t){return e.groupOrder===t.groupOrder?e.renderOrder===t.renderOrder?e.z===t.z?e.id-t.id:t.z-e.z:e.renderOrder-t.renderOrder:e.groupOrder-t.groupOrder}function Zu(){let e=[],t=0,n=[],r=[],i=[];function a(){t=0,n.length=0,r.length=0,i.length=0}function o(e){let t=0;return e.isInstancedMesh&&(t+=2),e.isSkinnedMesh&&(t+=1),t}function s(n,r,i,a,s,c){let l=e[t];return l===void 0?(l={id:n.id,object:n,geometry:r,material:i,materialVariant:o(n),groupOrder:a,renderOrder:n.renderOrder,z:s,group:c},e[t]=l):(l.id=n.id,l.object=n,l.geometry=r,l.material=i,l.materialVariant=o(n),l.groupOrder=a,l.renderOrder=n.renderOrder,l.z=s,l.group=c),t++,l}function c(e,t,a,o,c,l){let u=s(e,t,a,o,c,l);a.transmission>0?r.push(u):a.transparent===!0?i.push(u):n.push(u)}function l(e,t,a,o,c,l){let u=s(e,t,a,o,c,l);a.transmission>0?r.unshift(u):a.transparent===!0?i.unshift(u):n.unshift(u)}function u(e,t,a){n.length>1&&n.sort(e||Yu),r.length>1&&r.sort(t||Xu),i.length>1&&i.sort(t||Xu),a&&(n.reverse(),r.reverse(),i.reverse())}function d(){for(let n=t,r=e.length;n<r;n++){let t=e[n];if(t.id===null)break;t.id=null,t.object=null,t.geometry=null,t.material=null,t.group=null}}return{opaque:n,transmissive:r,transparent:i,init:a,push:c,unshift:l,finish:d,sort:u}}function Qu(){let e=new WeakMap;function t(t,n){let r=e.get(t),i;return r===void 0?(i=new Zu,e.set(t,[i])):n>=r.length?(i=new Zu,r.push(i)):i=r[n],i}function n(){e=new WeakMap}return{get:t,dispose:n}}function $u(){let e={};return{get:function(t){if(e[t.id]!==void 0)return e[t.id];let n;switch(t.type){case`DirectionalLight`:n={direction:new W,color:new J};break;case`SpotLight`:n={position:new W,direction:new W,color:new J,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case`PointLight`:n={position:new W,color:new J,distance:0,decay:0};break;case`HemisphereLight`:n={direction:new W,skyColor:new J,groundColor:new J};break;case`RectAreaLight`:n={color:new J,position:new W,halfWidth:new W,halfHeight:new W}}return e[t.id]=n,n}}}function ed(){let e={};return{get:function(t){if(e[t.id]!==void 0)return e[t.id];let n;switch(t.type){case`DirectionalLight`:n={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new U};break;case`SpotLight`:n={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new U};break;case`PointLight`:n={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new U,shadowCameraNear:1,shadowCameraFar:1e3}}return e[t.id]=n,n}}}var td=0;function nd(e,t){return(t.castShadow?2:0)-(e.castShadow?2:0)+ +!!t.map-!!e.map}function rd(e){let t=new $u,n=ed(),r={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let e=0;e<9;e++)r.probe.push(new W);let i=new W,a=new q,o=new q;function s(i){let a=0,o=0,s=0;for(let e=0;e<9;e++)r.probe[e].set(0,0,0);let c=0,l=0,u=0,d=0,f=0,p=0,m=0,h=0,g=0,_=0,v=0;i.sort(nd);for(let e=0,y=i.length;e<y;e++){let y=i[e],b=y.color,x=y.intensity,S=y.distance,C=null;if(y.shadow&&y.shadow.map&&(C=y.shadow.map.texture.format===1030?y.shadow.map.texture:y.shadow.map.depthTexture||y.shadow.map.texture),y.isAmbientLight)a+=b.r*x,o+=b.g*x,s+=b.b*x;else if(y.isLightProbe){for(let e=0;e<9;e++)r.probe[e].addScaledVector(y.sh.coefficients[e],x);v++}else if(y.isDirectionalLight){let e=t.get(y);if(e.color.copy(y.color).multiplyScalar(y.intensity),y.castShadow){let e=y.shadow,t=n.get(y);t.shadowIntensity=e.intensity,t.shadowBias=e.bias,t.shadowNormalBias=e.normalBias,t.shadowRadius=e.radius,t.shadowMapSize=e.mapSize,r.directionalShadow[c]=t,r.directionalShadowMap[c]=C,r.directionalShadowMatrix[c]=y.shadow.matrix,p++}r.directional[c]=e,c++}else if(y.isSpotLight){let e=t.get(y);e.position.setFromMatrixPosition(y.matrixWorld),e.color.copy(b).multiplyScalar(x),e.distance=S,e.coneCos=Math.cos(y.angle),e.penumbraCos=Math.cos(y.angle*(1-y.penumbra)),e.decay=y.decay,r.spot[u]=e;let i=y.shadow;if(y.map&&(r.spotLightMap[g]=y.map,g++,i.updateMatrices(y),y.castShadow&&_++),r.spotLightMatrix[u]=i.matrix,y.castShadow){let e=n.get(y);e.shadowIntensity=i.intensity,e.shadowBias=i.bias,e.shadowNormalBias=i.normalBias,e.shadowRadius=i.radius,e.shadowMapSize=i.mapSize,r.spotShadow[u]=e,r.spotShadowMap[u]=C,h++}u++}else if(y.isRectAreaLight){let e=t.get(y);e.color.copy(b).multiplyScalar(x),e.halfWidth.set(y.width*.5,0,0),e.halfHeight.set(0,y.height*.5,0),r.rectArea[d]=e,d++}else if(y.isPointLight){let e=t.get(y);if(e.color.copy(y.color).multiplyScalar(y.intensity),e.distance=y.distance,e.decay=y.decay,y.castShadow){let e=y.shadow,t=n.get(y);t.shadowIntensity=e.intensity,t.shadowBias=e.bias,t.shadowNormalBias=e.normalBias,t.shadowRadius=e.radius,t.shadowMapSize=e.mapSize,t.shadowCameraNear=e.camera.near,t.shadowCameraFar=e.camera.far,r.pointShadow[l]=t,r.pointShadowMap[l]=C,r.pointShadowMatrix[l]=y.shadow.matrix,m++}r.point[l]=e,l++}else if(y.isHemisphereLight){let e=t.get(y);e.skyColor.copy(y.color).multiplyScalar(x),e.groundColor.copy(y.groundColor).multiplyScalar(x),r.hemi[f]=e,f++}}d>0&&(e.has(`OES_texture_float_linear`)===!0?(r.rectAreaLTC1=X.LTC_FLOAT_1,r.rectAreaLTC2=X.LTC_FLOAT_2):(r.rectAreaLTC1=X.LTC_HALF_1,r.rectAreaLTC2=X.LTC_HALF_2)),r.ambient[0]=a,r.ambient[1]=o,r.ambient[2]=s;let y=r.hash;(y.directionalLength!==c||y.pointLength!==l||y.spotLength!==u||y.rectAreaLength!==d||y.hemiLength!==f||y.numDirectionalShadows!==p||y.numPointShadows!==m||y.numSpotShadows!==h||y.numSpotMaps!==g||y.numLightProbes!==v)&&(r.directional.length=c,r.spot.length=u,r.rectArea.length=d,r.point.length=l,r.hemi.length=f,r.directionalShadow.length=p,r.directionalShadowMap.length=p,r.pointShadow.length=m,r.pointShadowMap.length=m,r.spotShadow.length=h,r.spotShadowMap.length=h,r.directionalShadowMatrix.length=p,r.pointShadowMatrix.length=m,r.spotLightMatrix.length=h+g-_,r.spotLightMap.length=g,r.numSpotLightShadowsWithMaps=_,r.numLightProbes=v,y.directionalLength=c,y.pointLength=l,y.spotLength=u,y.rectAreaLength=d,y.hemiLength=f,y.numDirectionalShadows=p,y.numPointShadows=m,y.numSpotShadows=h,y.numSpotMaps=g,y.numLightProbes=v,r.version=td++)}function c(e,t){let n=0,s=0,c=0,l=0,u=0,d=t.matrixWorldInverse;for(let t=0,f=e.length;t<f;t++){let f=e[t];if(f.isDirectionalLight){let e=r.directional[n];e.direction.setFromMatrixPosition(f.matrixWorld),i.setFromMatrixPosition(f.target.matrixWorld),e.direction.sub(i),e.direction.transformDirection(d),n++}else if(f.isSpotLight){let e=r.spot[c];e.position.setFromMatrixPosition(f.matrixWorld),e.position.applyMatrix4(d),e.direction.setFromMatrixPosition(f.matrixWorld),i.setFromMatrixPosition(f.target.matrixWorld),e.direction.sub(i),e.direction.transformDirection(d),c++}else if(f.isRectAreaLight){let e=r.rectArea[l];e.position.setFromMatrixPosition(f.matrixWorld),e.position.applyMatrix4(d),o.identity(),a.copy(f.matrixWorld),a.premultiply(d),o.extractRotation(a),e.halfWidth.set(f.width*.5,0,0),e.halfHeight.set(0,f.height*.5,0),e.halfWidth.applyMatrix4(o),e.halfHeight.applyMatrix4(o),l++}else if(f.isPointLight){let e=r.point[s];e.position.setFromMatrixPosition(f.matrixWorld),e.position.applyMatrix4(d),s++}else if(f.isHemisphereLight){let e=r.hemi[u];e.direction.setFromMatrixPosition(f.matrixWorld),e.direction.transformDirection(d),u++}}}return{setup:s,setupView:c,state:r}}function id(e){let t=new rd(e),n=[],r=[],i=[];function a(e){d.camera=e,n.length=0,r.length=0,i.length=0}function o(e){n.push(e)}function s(e){r.push(e)}function c(e){i.push(e)}function l(){t.setup(n)}function u(e){t.setupView(n,e)}let d={lightsArray:n,shadowsArray:r,lightProbeGridArray:i,camera:null,lights:t,transmissionRenderTarget:{},textureUnits:0};return{init:a,state:d,setupLights:l,setupLightsView:u,pushLight:o,pushShadow:s,pushLightProbeGrid:c}}function ad(e){let t=new WeakMap;function n(n,r=0){let i=t.get(n),a;return i===void 0?(a=new id(e),t.set(n,[a])):r>=i.length?(a=new id(e),i.push(a)):a=i[r],a}function r(){t=new WeakMap}return{get:n,dispose:r}}var od=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,sd=`uniform sampler2D shadow_pass;
uniform vec2 resolution;
uniform float radius;
void main() {
	const float samples = float( VSM_SAMPLES );
	float mean = 0.0;
	float squared_mean = 0.0;
	float uvStride = samples <= 1.0 ? 0.0 : 2.0 / ( samples - 1.0 );
	float uvStart = samples <= 1.0 ? 0.0 : - 1.0;
	for ( float i = 0.0; i < samples; i ++ ) {
		float uvOffset = uvStart + i * uvStride;
		#ifdef HORIZONTAL_PASS
			vec2 distribution = texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( uvOffset, 0.0 ) * radius ) / resolution ).rg;
			mean += distribution.x;
			squared_mean += distribution.y * distribution.y + distribution.x * distribution.x;
		#else
			float depth = texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( 0.0, uvOffset ) * radius ) / resolution ).r;
			mean += depth;
			squared_mean += depth * depth;
		#endif
	}
	mean = mean / samples;
	squared_mean = squared_mean / samples;
	float std_dev = sqrt( max( 0.0, squared_mean - mean * mean ) );
	gl_FragColor = vec4( mean, std_dev, 0.0, 1.0 );
}`,cd=[new W(1,0,0),new W(-1,0,0),new W(0,1,0),new W(0,-1,0),new W(0,0,1),new W(0,0,-1)],ld=[new W(0,-1,0),new W(0,-1,0),new W(0,0,1),new W(0,0,-1),new W(0,-1,0),new W(0,-1,0)],ud=new q,dd=new W,fd=new W;function pd(e,t,n){let r=new Pi,i=new U,a=new U,s=new Jt,c=new Vo,u=new Ho,d={},f=n.maxTextureSize,p={0:1,1:0,2:2},m=new Lo({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new U},radius:{value:4}},vertexShader:od,fragmentShader:sd}),h=m.clone();h.defines.HORIZONTAL_PASS=1;let g=new Or;g.setAttribute(`position`,new mr(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));let b=new ei(g,m),x=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=1;let S=this.type;this.render=function(t,n,c){if(x.enabled===!1||x.autoUpdate===!1&&x.needsUpdate===!1||t.length===0)return;this.type===2&&(B(`WebGLShadowMap: PCFSoftShadowMap has been deprecated. Using PCFShadowMap instead.`),this.type=1);let u=e.getRenderTarget(),d=e.getActiveCubeFace(),p=e.getActiveMipmapLevel(),m=e.state;m.setBlending(0),m.buffers.depth.getReversed()===!0?m.buffers.color.setClear(0,0,0,0):m.buffers.color.setClear(1,1,1,1),m.buffers.depth.setTest(!0),m.setScissorTest(!1);let h=S!==this.type;h&&n.traverse(function(e){e.material&&(Array.isArray(e.material)?e.material.forEach(e=>e.needsUpdate=!0):e.material.needsUpdate=!0)});for(let u=0,d=t.length;u<d;u++){let d=t[u],p=d.shadow;if(p===void 0){B(`WebGLShadowMap:`,d,`has no shadow.`);continue}if(p.autoUpdate===!1&&p.needsUpdate===!1)continue;i.copy(p.mapSize);let g=p.getFrameExtents();i.multiply(g),a.copy(p.mapSize),(i.x>f||i.y>f)&&(i.x>f&&(a.x=Math.floor(f/g.x),i.x=a.x*g.x,p.mapSize.x=a.x),i.y>f&&(a.y=Math.floor(f/g.y),i.y=a.y*g.y,p.mapSize.y=a.y));let b=e.state.buffers.depth.getReversed();if(p.camera._reversedDepth=b,p.map===null||h===!0){if(p.map!==null&&(p.map.depthTexture!==null&&(p.map.depthTexture.dispose(),p.map.depthTexture=null),p.map.dispose()),this.type===3){if(d.isPointLight){B(`WebGLShadowMap: VSM shadow maps are not supported for PointLights. Use PCF or BasicShadowMap instead.`);continue}p.map=new Xt(i.x,i.y,{format:te,type:y,minFilter:l,magFilter:l,generateMipmaps:!1}),p.map.texture.name=d.name+`.shadowMap`,p.map.depthTexture=new ia(i.x,i.y,v),p.map.depthTexture.name=d.name+`.shadowMapDepth`,p.map.depthTexture.format=O,p.map.depthTexture.compareFunction=null,p.map.depthTexture.minFilter=o,p.map.depthTexture.magFilter=o}else d.isPointLight?(p.map=new Wc(i.x),p.map.depthTexture=new aa(i.x,_)):(p.map=new Xt(i.x,i.y),p.map.depthTexture=new ia(i.x,i.y,_)),p.map.depthTexture.name=d.name+`.shadowMap`,p.map.depthTexture.format=O,this.type===1?(p.map.depthTexture.compareFunction=b?518:515,p.map.depthTexture.minFilter=l,p.map.depthTexture.magFilter=l):(p.map.depthTexture.compareFunction=null,p.map.depthTexture.minFilter=o,p.map.depthTexture.magFilter=o);p.camera.updateProjectionMatrix()}let x=p.map.isWebGLCubeRenderTarget?6:1;for(let t=0;t<x;t++){if(p.map.isWebGLCubeRenderTarget)e.setRenderTarget(p.map,t),e.clear();else{t===0&&(e.setRenderTarget(p.map),e.clear());let n=p.getViewport(t);s.set(a.x*n.x,a.y*n.y,a.x*n.z,a.y*n.w),m.viewport(s)}if(d.isPointLight){let e=p.camera,n=p.matrix,r=d.distance||e.far;r!==e.far&&(e.far=r,e.updateProjectionMatrix()),dd.setFromMatrixPosition(d.matrixWorld),e.position.copy(dd),fd.copy(e.position),fd.add(cd[t]),e.up.copy(ld[t]),e.lookAt(fd),e.updateMatrixWorld(),n.makeTranslation(-dd.x,-dd.y,-dd.z),ud.multiplyMatrices(e.projectionMatrix,e.matrixWorldInverse),p._frustum.setFromProjectionMatrix(ud,e.coordinateSystem,e.reversedDepth)}else p.updateMatrices(d);r=p.getFrustum(),T(n,c,p.camera,d,this.type)}p.isPointLightShadow!==!0&&this.type===3&&C(p,c),p.needsUpdate=!1}S=this.type,x.needsUpdate=!1,e.setRenderTarget(u,d,p)};function C(n,r){let a=t.update(b);m.defines.VSM_SAMPLES!==n.blurSamples&&(m.defines.VSM_SAMPLES=n.blurSamples,h.defines.VSM_SAMPLES=n.blurSamples,m.needsUpdate=!0,h.needsUpdate=!0),n.mapPass===null&&(n.mapPass=new Xt(i.x,i.y,{format:te,type:y})),m.uniforms.shadow_pass.value=n.map.depthTexture,m.uniforms.resolution.value=n.mapSize,m.uniforms.radius.value=n.radius,e.setRenderTarget(n.mapPass),e.clear(),e.renderBufferDirect(r,null,a,m,b,null),h.uniforms.shadow_pass.value=n.mapPass.texture,h.uniforms.resolution.value=n.mapSize,h.uniforms.radius.value=n.radius,e.setRenderTarget(n.map),e.clear(),e.renderBufferDirect(r,null,a,h,b,null)}function w(t,n,r,i){let a=null,o=r.isPointLight===!0?t.customDistanceMaterial:t.customDepthMaterial;if(o!==void 0)a=o;else if(a=r.isPointLight===!0?u:c,e.localClippingEnabled&&n.clipShadows===!0&&Array.isArray(n.clippingPlanes)&&n.clippingPlanes.length!==0||n.displacementMap&&n.displacementScale!==0||n.alphaMap&&n.alphaTest>0||n.map&&n.alphaTest>0||n.alphaToCoverage===!0){let e=a.uuid,t=n.uuid,r=d[e];r===void 0&&(r={},d[e]=r);let i=r[t];i===void 0&&(i=a.clone(),r[t]=i,n.addEventListener(`dispose`,E)),a=i}if(a.visible=n.visible,a.wireframe=n.wireframe,i===3?a.side=n.shadowSide===null?n.side:n.shadowSide:a.side=n.shadowSide===null?p[n.side]:n.shadowSide,a.alphaMap=n.alphaMap,a.alphaTest=n.alphaToCoverage===!0?.5:n.alphaTest,a.map=n.map,a.clipShadows=n.clipShadows,a.clippingPlanes=n.clippingPlanes,a.clipIntersection=n.clipIntersection,a.displacementMap=n.displacementMap,a.displacementScale=n.displacementScale,a.displacementBias=n.displacementBias,a.wireframeLinewidth=n.wireframeLinewidth,a.linewidth=n.linewidth,r.isPointLight===!0&&a.isMeshDistanceMaterial===!0){let t=e.properties.get(a);t.light=r}return a}function T(n,i,a,o,s){if(n.visible===!1)return;if(n.layers.test(i.layers)&&(n.isMesh||n.isLine||n.isPoints)&&(n.castShadow||n.receiveShadow&&s===3)&&(!n.frustumCulled||r.intersectsObject(n))){n.modelViewMatrix.multiplyMatrices(a.matrixWorldInverse,n.matrixWorld);let r=t.update(n),c=n.material;if(Array.isArray(c)){let t=r.groups;for(let l=0,u=t.length;l<u;l++){let u=t[l],d=c[u.materialIndex];if(d&&d.visible){let t=w(n,d,o,s);n.onBeforeShadow(e,n,i,a,r,t,u),e.renderBufferDirect(a,null,r,t,n,u),n.onAfterShadow(e,n,i,a,r,t,u)}}}else if(c.visible){let t=w(n,c,o,s);n.onBeforeShadow(e,n,i,a,r,t,null),e.renderBufferDirect(a,null,r,t,n,null),n.onAfterShadow(e,n,i,a,r,t,null)}}let c=n.children;for(let e=0,t=c.length;e<t;e++)T(c[e],i,a,o,s)}function E(e){e.target.removeEventListener(`dispose`,E);for(let t in d){let n=d[t],r=e.target.uuid;r in n&&(n[r].dispose(),delete n[r])}}}function md(e,t){function n(){let t=!1,n=new Jt,r=null,i=new Jt(0,0,0,0);return{setMask:function(n){r!==n&&!t&&(e.colorMask(n,n,n,n),r=n)},setLocked:function(e){t=e},setClear:function(t,r,a,o,s){s===!0&&(t*=o,r*=o,a*=o),n.set(t,r,a,o),i.equals(n)===!1&&(e.clearColor(t,r,a,o),i.copy(n))},reset:function(){t=!1,r=null,i.set(-1,0,0,0)}}}function r(){let n=!1,r=!1,i=null,a=null,o=null;return{setReversed:function(e){if(r!==e){let n=t.get(`EXT_clip_control`);e?n.clipControlEXT(n.LOWER_LEFT_EXT,n.ZERO_TO_ONE_EXT):n.clipControlEXT(n.LOWER_LEFT_EXT,n.NEGATIVE_ONE_TO_ONE_EXT),r=e;let i=o;o=null,this.setClear(i)}},getReversed:function(){return r},setTest:function(t){t?P(e.DEPTH_TEST):ue(e.DEPTH_TEST)},setMask:function(t){i!==t&&!n&&(e.depthMask(t),i=t)},setFunc:function(t){if(r&&(t=rt[t]),a!==t){switch(t){case 0:e.depthFunc(e.NEVER);break;case 1:e.depthFunc(e.ALWAYS);break;case 2:e.depthFunc(e.LESS);break;case 3:e.depthFunc(e.LEQUAL);break;case 4:e.depthFunc(e.EQUAL);break;case 5:e.depthFunc(e.GEQUAL);break;case 6:e.depthFunc(e.GREATER);break;case 7:e.depthFunc(e.NOTEQUAL);break;default:e.depthFunc(e.LEQUAL)}a=t}},setLocked:function(e){n=e},setClear:function(t){o!==t&&(o=t,r&&(t=1-t),e.clearDepth(t))},reset:function(){n=!1,i=null,a=null,o=null,r=!1}}}function i(){let t=!1,n=null,r=null,i=null,a=null,o=null,s=null,c=null,l=null;return{setTest:function(n){t||(n?P(e.STENCIL_TEST):ue(e.STENCIL_TEST))},setMask:function(r){n!==r&&!t&&(e.stencilMask(r),n=r)},setFunc:function(t,n,o){(r!==t||i!==n||a!==o)&&(e.stencilFunc(t,n,o),r=t,i=n,a=o)},setOp:function(t,n,r){(o!==t||s!==n||c!==r)&&(e.stencilOp(t,n,r),o=t,s=n,c=r)},setLocked:function(e){t=e},setClear:function(t){l!==t&&(e.clearStencil(t),l=t)},reset:function(){t=!1,n=null,r=null,i=null,a=null,o=null,s=null,c=null,l=null}}}let a=new n,o=new r,s=new i,c=new WeakMap,l=new WeakMap,u={},d={},f={},p=new WeakMap,m=[],h=null,g=!1,_=null,v=null,y=null,b=null,x=null,S=null,C=null,w=new J(0,0,0),T=0,E=!1,D=null,O=null,k=null,A=null,ee=null,te=e.getParameter(e.MAX_COMBINED_TEXTURE_IMAGE_UNITS),j=!1,ne=0,M=e.getParameter(e.VERSION);M.indexOf(`WebGL`)===-1?M.indexOf(`OpenGL ES`)!==-1&&(ne=parseFloat(/^OpenGL ES (\d)/.exec(M)[1]),j=ne>=2):(ne=parseFloat(/^WebGL (\d)/.exec(M)[1]),j=ne>=1);let N=null,re={},ie=e.getParameter(e.SCISSOR_BOX),ae=e.getParameter(e.VIEWPORT),oe=new Jt().fromArray(ie),se=new Jt().fromArray(ae);function ce(t,n,r,i){let a=new Uint8Array(4),o=e.createTexture();e.bindTexture(t,o),e.texParameteri(t,e.TEXTURE_MIN_FILTER,e.NEAREST),e.texParameteri(t,e.TEXTURE_MAG_FILTER,e.NEAREST);for(let o=0;o<r;o++)t===e.TEXTURE_3D||t===e.TEXTURE_2D_ARRAY?e.texImage3D(n,0,e.RGBA,1,1,i,0,e.RGBA,e.UNSIGNED_BYTE,a):e.texImage2D(n+o,0,e.RGBA,1,1,0,e.RGBA,e.UNSIGNED_BYTE,a);return o}let le={};le[e.TEXTURE_2D]=ce(e.TEXTURE_2D,e.TEXTURE_2D,1),le[e.TEXTURE_CUBE_MAP]=ce(e.TEXTURE_CUBE_MAP,e.TEXTURE_CUBE_MAP_POSITIVE_X,6),le[e.TEXTURE_2D_ARRAY]=ce(e.TEXTURE_2D_ARRAY,e.TEXTURE_2D_ARRAY,1,1),le[e.TEXTURE_3D]=ce(e.TEXTURE_3D,e.TEXTURE_3D,1,1),a.setClear(0,0,0,1),o.setClear(1),s.setClear(0),P(e.DEPTH_TEST),o.setFunc(3),_e(!1),ve(1),P(e.CULL_FACE),he(0);function P(t){u[t]!==!0&&(e.enable(t),u[t]=!0)}function ue(t){u[t]!==!1&&(e.disable(t),u[t]=!1)}function de(t,n){return f[t]!==n&&(e.bindFramebuffer(t,n),f[t]=n,t===e.DRAW_FRAMEBUFFER&&(f[e.FRAMEBUFFER]=n),t===e.FRAMEBUFFER&&(f[e.DRAW_FRAMEBUFFER]=n),!0)}function fe(t,n){let r=m,i=!1;if(t){r=p.get(n),r===void 0&&(r=[],p.set(n,r));let a=t.textures;if(r.length!==a.length||r[0]!==e.COLOR_ATTACHMENT0){for(let t=0,n=a.length;t<n;t++)r[t]=e.COLOR_ATTACHMENT0+t;r.length=a.length,i=!0}}else r[0]!==e.BACK&&(r[0]=e.BACK,i=!0);i&&e.drawBuffers(r)}function pe(t){return h!==t&&(e.useProgram(t),h=t,!0)}let me={100:e.FUNC_ADD,101:e.FUNC_SUBTRACT,102:e.FUNC_REVERSE_SUBTRACT};me[103]=e.MIN,me[104]=e.MAX;let F={200:e.ZERO,201:e.ONE,202:e.SRC_COLOR,204:e.SRC_ALPHA,210:e.SRC_ALPHA_SATURATE,208:e.DST_COLOR,206:e.DST_ALPHA,203:e.ONE_MINUS_SRC_COLOR,205:e.ONE_MINUS_SRC_ALPHA,209:e.ONE_MINUS_DST_COLOR,207:e.ONE_MINUS_DST_ALPHA,211:e.CONSTANT_COLOR,212:e.ONE_MINUS_CONSTANT_COLOR,213:e.CONSTANT_ALPHA,214:e.ONE_MINUS_CONSTANT_ALPHA};function he(t,n,r,i,a,o,s,c,l,u){if(t===0){g===!0&&(ue(e.BLEND),g=!1);return}if(g===!1&&(P(e.BLEND),g=!0),t!==5){if(t!==_||u!==E){if((v!==100||x!==100)&&(e.blendEquation(e.FUNC_ADD),v=100,x=100),u)switch(t){case 1:e.blendFuncSeparate(e.ONE,e.ONE_MINUS_SRC_ALPHA,e.ONE,e.ONE_MINUS_SRC_ALPHA);break;case 2:e.blendFunc(e.ONE,e.ONE);break;case 3:e.blendFuncSeparate(e.ZERO,e.ONE_MINUS_SRC_COLOR,e.ZERO,e.ONE);break;case 4:e.blendFuncSeparate(e.DST_COLOR,e.ONE_MINUS_SRC_ALPHA,e.ZERO,e.ONE);break;default:V(`WebGLState: Invalid blending: `,t)}else switch(t){case 1:e.blendFuncSeparate(e.SRC_ALPHA,e.ONE_MINUS_SRC_ALPHA,e.ONE,e.ONE_MINUS_SRC_ALPHA);break;case 2:e.blendFuncSeparate(e.SRC_ALPHA,e.ONE,e.ONE,e.ONE);break;case 3:V(`WebGLState: SubtractiveBlending requires material.premultipliedAlpha = true`);break;case 4:V(`WebGLState: MultiplyBlending requires material.premultipliedAlpha = true`);break;default:V(`WebGLState: Invalid blending: `,t)}y=null,b=null,S=null,C=null,w.set(0,0,0),T=0,_=t,E=u}return}a||=n,o||=r,s||=i,(n!==v||a!==x)&&(e.blendEquationSeparate(me[n],me[a]),v=n,x=a),(r!==y||i!==b||o!==S||s!==C)&&(e.blendFuncSeparate(F[r],F[i],F[o],F[s]),y=r,b=i,S=o,C=s),(c.equals(w)===!1||l!==T)&&(e.blendColor(c.r,c.g,c.b,l),w.copy(c),T=l),_=t,E=!1}function ge(t,n){t.side===2?ue(e.CULL_FACE):P(e.CULL_FACE);let r=t.side===1;n&&(r=!r),_e(r),t.blending===1&&t.transparent===!1?he(0):he(t.blending,t.blendEquation,t.blendSrc,t.blendDst,t.blendEquationAlpha,t.blendSrcAlpha,t.blendDstAlpha,t.blendColor,t.blendAlpha,t.premultipliedAlpha),o.setFunc(t.depthFunc),o.setTest(t.depthTest),o.setMask(t.depthWrite),a.setMask(t.colorWrite);let i=t.stencilWrite;s.setTest(i),i&&(s.setMask(t.stencilWriteMask),s.setFunc(t.stencilFunc,t.stencilRef,t.stencilFuncMask),s.setOp(t.stencilFail,t.stencilZFail,t.stencilZPass)),be(t.polygonOffset,t.polygonOffsetFactor,t.polygonOffsetUnits),t.alphaToCoverage===!0?P(e.SAMPLE_ALPHA_TO_COVERAGE):ue(e.SAMPLE_ALPHA_TO_COVERAGE)}function _e(t){D!==t&&(t?e.frontFace(e.CW):e.frontFace(e.CCW),D=t)}function ve(t){t===0?ue(e.CULL_FACE):(P(e.CULL_FACE),t!==O&&(t===1?e.cullFace(e.BACK):t===2?e.cullFace(e.FRONT):e.cullFace(e.FRONT_AND_BACK))),O=t}function ye(t){t!==k&&(j&&e.lineWidth(t),k=t)}function be(t,n,r){t?(P(e.POLYGON_OFFSET_FILL),(A!==n||ee!==r)&&(A=n,ee=r,o.getReversed()&&(n=-n),e.polygonOffset(n,r))):ue(e.POLYGON_OFFSET_FILL)}function xe(t){t?P(e.SCISSOR_TEST):ue(e.SCISSOR_TEST)}function Se(t){t===void 0&&(t=e.TEXTURE0+te-1),N!==t&&(e.activeTexture(t),N=t)}function Ce(t,n,r){r===void 0&&(r=N===null?e.TEXTURE0+te-1:N);let i=re[r];i===void 0&&(i={type:void 0,texture:void 0},re[r]=i),(i.type!==t||i.texture!==n)&&(N!==r&&(e.activeTexture(r),N=r),e.bindTexture(t,n||le[t]),i.type=t,i.texture=n)}function we(){let t=re[N];t!==void 0&&t.type!==void 0&&(e.bindTexture(t.type,null),t.type=void 0,t.texture=void 0)}function Te(){try{e.compressedTexImage2D(...arguments)}catch(e){V(`WebGLState:`,e)}}function Ee(){try{e.compressedTexImage3D(...arguments)}catch(e){V(`WebGLState:`,e)}}function De(){try{e.texSubImage2D(...arguments)}catch(e){V(`WebGLState:`,e)}}function Oe(){try{e.texSubImage3D(...arguments)}catch(e){V(`WebGLState:`,e)}}function ke(){try{e.compressedTexSubImage2D(...arguments)}catch(e){V(`WebGLState:`,e)}}function Ae(){try{e.compressedTexSubImage3D(...arguments)}catch(e){V(`WebGLState:`,e)}}function je(){try{e.texStorage2D(...arguments)}catch(e){V(`WebGLState:`,e)}}function Me(){try{e.texStorage3D(...arguments)}catch(e){V(`WebGLState:`,e)}}function I(){try{e.texImage2D(...arguments)}catch(e){V(`WebGLState:`,e)}}function Ne(){try{e.texImage3D(...arguments)}catch(e){V(`WebGLState:`,e)}}function Pe(t){return d[t]===void 0?e.getParameter(t):d[t]}function Fe(t,n){d[t]!==n&&(e.pixelStorei(t,n),d[t]=n)}function L(t){oe.equals(t)===!1&&(e.scissor(t.x,t.y,t.z,t.w),oe.copy(t))}function Ie(t){se.equals(t)===!1&&(e.viewport(t.x,t.y,t.z,t.w),se.copy(t))}function Le(t,n){let r=l.get(n);r===void 0&&(r=new WeakMap,l.set(n,r));let i=r.get(t);i===void 0&&(i=e.getUniformBlockIndex(n,t.name),r.set(t,i))}function Re(t,n){let r=l.get(n).get(t);c.get(n)!==r&&(e.uniformBlockBinding(n,r,t.__bindingPointIndex),c.set(n,r))}function ze(){e.disable(e.BLEND),e.disable(e.CULL_FACE),e.disable(e.DEPTH_TEST),e.disable(e.POLYGON_OFFSET_FILL),e.disable(e.SCISSOR_TEST),e.disable(e.STENCIL_TEST),e.disable(e.SAMPLE_ALPHA_TO_COVERAGE),e.blendEquation(e.FUNC_ADD),e.blendFunc(e.ONE,e.ZERO),e.blendFuncSeparate(e.ONE,e.ZERO,e.ONE,e.ZERO),e.blendColor(0,0,0,0),e.colorMask(!0,!0,!0,!0),e.clearColor(0,0,0,0),e.depthMask(!0),e.depthFunc(e.LESS),o.setReversed(!1),e.clearDepth(1),e.stencilMask(4294967295),e.stencilFunc(e.ALWAYS,0,4294967295),e.stencilOp(e.KEEP,e.KEEP,e.KEEP),e.clearStencil(0),e.cullFace(e.BACK),e.frontFace(e.CCW),e.polygonOffset(0,0),e.activeTexture(e.TEXTURE0),e.bindFramebuffer(e.FRAMEBUFFER,null),e.bindFramebuffer(e.DRAW_FRAMEBUFFER,null),e.bindFramebuffer(e.READ_FRAMEBUFFER,null),e.useProgram(null),e.lineWidth(1),e.scissor(0,0,e.canvas.width,e.canvas.height),e.viewport(0,0,e.canvas.width,e.canvas.height),e.pixelStorei(e.PACK_ALIGNMENT,4),e.pixelStorei(e.UNPACK_ALIGNMENT,4),e.pixelStorei(e.UNPACK_FLIP_Y_WEBGL,!1),e.pixelStorei(e.UNPACK_PREMULTIPLY_ALPHA_WEBGL,!1),e.pixelStorei(e.UNPACK_COLORSPACE_CONVERSION_WEBGL,e.BROWSER_DEFAULT_WEBGL),e.pixelStorei(e.PACK_ROW_LENGTH,0),e.pixelStorei(e.PACK_SKIP_PIXELS,0),e.pixelStorei(e.PACK_SKIP_ROWS,0),e.pixelStorei(e.UNPACK_ROW_LENGTH,0),e.pixelStorei(e.UNPACK_IMAGE_HEIGHT,0),e.pixelStorei(e.UNPACK_SKIP_PIXELS,0),e.pixelStorei(e.UNPACK_SKIP_ROWS,0),e.pixelStorei(e.UNPACK_SKIP_IMAGES,0),u={},d={},N=null,re={},f={},p=new WeakMap,m=[],h=null,g=!1,_=null,v=null,y=null,b=null,x=null,S=null,C=null,w=new J(0,0,0),T=0,E=!1,D=null,O=null,k=null,A=null,ee=null,oe.set(0,0,e.canvas.width,e.canvas.height),se.set(0,0,e.canvas.width,e.canvas.height),a.reset(),o.reset(),s.reset()}return{buffers:{color:a,depth:o,stencil:s},enable:P,disable:ue,bindFramebuffer:de,drawBuffers:fe,useProgram:pe,setBlending:he,setMaterial:ge,setFlipSided:_e,setCullFace:ve,setLineWidth:ye,setPolygonOffset:be,setScissorTest:xe,activeTexture:Se,bindTexture:Ce,unbindTexture:we,compressedTexImage2D:Te,compressedTexImage3D:Ee,texImage2D:I,texImage3D:Ne,pixelStorei:Fe,getParameter:Pe,updateUBOMapping:Le,uniformBlockBinding:Re,texStorage2D:je,texStorage3D:Me,texSubImage2D:De,texSubImage3D:Oe,compressedTexSubImage2D:ke,compressedTexSubImage3D:Ae,scissor:L,viewport:Ie,reset:ze}}function hd(e,t,n,f,p,m,h){let g=t.has(`WEBGL_multisampled_render_to_texture`)?t.get(`WEBGL_multisampled_render_to_texture`):null,_=typeof navigator>`u`?!1:/OculusBrowser/g.test(navigator.userAgent),v=new U,y=new WeakMap,b=new Set,x,S=new WeakMap,C=!1;try{C=typeof OffscreenCanvas<`u`&&new OffscreenCanvas(1,1).getContext(`2d`)!==null}catch{}function w(e,t){return C?new OffscreenCanvas(e,t):Xe(`canvas`)}function T(e,t,n){let r=1,i=Pe(e);if((i.width>n||i.height>n)&&(r=n/Math.max(i.width,i.height)),r<1){if(typeof HTMLImageElement<`u`&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<`u`&&e instanceof HTMLCanvasElement||typeof ImageBitmap<`u`&&e instanceof ImageBitmap||typeof VideoFrame<`u`&&e instanceof VideoFrame){let n=Math.floor(r*i.width),a=Math.floor(r*i.height);x===void 0&&(x=w(n,a));let o=t?w(n,a):x;return o.width=n,o.height=a,o.getContext(`2d`).drawImage(e,0,0,n,a),B(`WebGLRenderer: Texture has been resized from (`+i.width+`x`+i.height+`) to (`+n+`x`+a+`).`),o}return`data`in e&&B(`WebGLRenderer: Image in DataTexture is too big (`+i.width+`x`+i.height+`).`),e}return e}function E(e){return e.generateMipmaps}function D(t){e.generateMipmap(t)}function O(t){return t.isWebGLCubeRenderTarget?e.TEXTURE_CUBE_MAP:t.isWebGL3DRenderTarget?e.TEXTURE_3D:t.isWebGLArrayRenderTarget||t.isCompressedArrayTexture?e.TEXTURE_2D_ARRAY:e.TEXTURE_2D}function A(n,r,i,a,o,s=!1){if(n!==null){if(e[n]!==void 0)return e[n];B(`WebGLRenderer: Attempt to use non-existing WebGL internal format '`+n+`'`)}let c;a&&(c=t.get(`EXT_texture_norm16`),c||B(`WebGLRenderer: Unable to use normalized textures without EXT_texture_norm16 extension`));let l=r;if(r===e.RED&&(i===e.FLOAT&&(l=e.R32F),i===e.HALF_FLOAT&&(l=e.R16F),i===e.UNSIGNED_BYTE&&(l=e.R8),i===e.UNSIGNED_SHORT&&c&&(l=c.R16_EXT),i===e.SHORT&&c&&(l=c.R16_SNORM_EXT)),r===e.RED_INTEGER&&(i===e.UNSIGNED_BYTE&&(l=e.R8UI),i===e.UNSIGNED_SHORT&&(l=e.R16UI),i===e.UNSIGNED_INT&&(l=e.R32UI),i===e.BYTE&&(l=e.R8I),i===e.SHORT&&(l=e.R16I),i===e.INT&&(l=e.R32I)),r===e.RG&&(i===e.FLOAT&&(l=e.RG32F),i===e.HALF_FLOAT&&(l=e.RG16F),i===e.UNSIGNED_BYTE&&(l=e.RG8),i===e.UNSIGNED_SHORT&&c&&(l=c.RG16_EXT),i===e.SHORT&&c&&(l=c.RG16_SNORM_EXT)),r===e.RG_INTEGER&&(i===e.UNSIGNED_BYTE&&(l=e.RG8UI),i===e.UNSIGNED_SHORT&&(l=e.RG16UI),i===e.UNSIGNED_INT&&(l=e.RG32UI),i===e.BYTE&&(l=e.RG8I),i===e.SHORT&&(l=e.RG16I),i===e.INT&&(l=e.RG32I)),r===e.RGB_INTEGER&&(i===e.UNSIGNED_BYTE&&(l=e.RGB8UI),i===e.UNSIGNED_SHORT&&(l=e.RGB16UI),i===e.UNSIGNED_INT&&(l=e.RGB32UI),i===e.BYTE&&(l=e.RGB8I),i===e.SHORT&&(l=e.RGB16I),i===e.INT&&(l=e.RGB32I)),r===e.RGBA_INTEGER&&(i===e.UNSIGNED_BYTE&&(l=e.RGBA8UI),i===e.UNSIGNED_SHORT&&(l=e.RGBA16UI),i===e.UNSIGNED_INT&&(l=e.RGBA32UI),i===e.BYTE&&(l=e.RGBA8I),i===e.SHORT&&(l=e.RGBA16I),i===e.INT&&(l=e.RGBA32I)),r===e.RGB&&(i===e.UNSIGNED_SHORT&&c&&(l=c.RGB16_EXT),i===e.SHORT&&c&&(l=c.RGB16_SNORM_EXT),i===e.UNSIGNED_INT_5_9_9_9_REV&&(l=e.RGB9_E5),i===e.UNSIGNED_INT_10F_11F_11F_REV&&(l=e.R11F_G11F_B10F)),r===e.RGBA){let t=s?Ge:K.getTransfer(o);i===e.FLOAT&&(l=e.RGBA32F),i===e.HALF_FLOAT&&(l=e.RGBA16F),i===e.UNSIGNED_BYTE&&(l=t===`srgb`?e.SRGB8_ALPHA8:e.RGBA8),i===e.UNSIGNED_SHORT&&c&&(l=c.RGBA16_EXT),i===e.SHORT&&c&&(l=c.RGBA16_SNORM_EXT),i===e.UNSIGNED_SHORT_4_4_4_4&&(l=e.RGBA4),i===e.UNSIGNED_SHORT_5_5_5_1&&(l=e.RGB5_A1)}return(l===e.R16F||l===e.R32F||l===e.RG16F||l===e.RG32F||l===e.RGBA16F||l===e.RGBA32F)&&t.get(`EXT_color_buffer_float`),l}function ee(t,n){let r;return t?n===null||n===1014||n===1020?r=e.DEPTH24_STENCIL8:n===1015?r=e.DEPTH32F_STENCIL8:n===1012&&(r=e.DEPTH24_STENCIL8,B(`DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.`)):n===null||n===1014||n===1020?r=e.DEPTH_COMPONENT24:n===1015?r=e.DEPTH_COMPONENT32F:n===1012&&(r=e.DEPTH_COMPONENT16),r}function te(e,t){return E(e)===!0||e.isFramebufferTexture&&e.minFilter!==1003&&e.minFilter!==1006?Math.log2(Math.max(t.width,t.height))+1:e.mipmaps!==void 0&&e.mipmaps.length>0?e.mipmaps.length:e.isCompressedTexture&&Array.isArray(e.image)?t.mipmaps.length:1}function j(e){let t=e.target;t.removeEventListener(`dispose`,j),M(t),t.isVideoTexture&&y.delete(t),t.isHTMLTexture&&b.delete(t)}function ne(e){let t=e.target;t.removeEventListener(`dispose`,ne),re(t)}function M(e){let t=f.get(e);if(t.__webglInit===void 0)return;let n=e.source,r=S.get(n);if(r){let i=r[t.__cacheKey];i.usedTimes--,i.usedTimes===0&&N(e),Object.keys(r).length===0&&S.delete(n)}f.remove(e)}function N(t){let n=f.get(t);e.deleteTexture(n.__webglTexture);let r=t.source,i=S.get(r);delete i[n.__cacheKey],h.memory.textures--}function re(t){let n=f.get(t);if(t.depthTexture&&(t.depthTexture.dispose(),f.remove(t.depthTexture)),t.isWebGLCubeRenderTarget)for(let t=0;t<6;t++){if(Array.isArray(n.__webglFramebuffer[t]))for(let r=0;r<n.__webglFramebuffer[t].length;r++)e.deleteFramebuffer(n.__webglFramebuffer[t][r]);else e.deleteFramebuffer(n.__webglFramebuffer[t]);n.__webglDepthbuffer&&e.deleteRenderbuffer(n.__webglDepthbuffer[t])}else{if(Array.isArray(n.__webglFramebuffer))for(let t=0;t<n.__webglFramebuffer.length;t++)e.deleteFramebuffer(n.__webglFramebuffer[t]);else e.deleteFramebuffer(n.__webglFramebuffer);if(n.__webglDepthbuffer&&e.deleteRenderbuffer(n.__webglDepthbuffer),n.__webglMultisampledFramebuffer&&e.deleteFramebuffer(n.__webglMultisampledFramebuffer),n.__webglColorRenderbuffer)for(let t=0;t<n.__webglColorRenderbuffer.length;t++)n.__webglColorRenderbuffer[t]&&e.deleteRenderbuffer(n.__webglColorRenderbuffer[t]);n.__webglDepthRenderbuffer&&e.deleteRenderbuffer(n.__webglDepthRenderbuffer)}let r=t.textures;for(let t=0,n=r.length;t<n;t++){let n=f.get(r[t]);n.__webglTexture&&(e.deleteTexture(n.__webglTexture),h.memory.textures--),f.remove(r[t])}f.remove(t)}let ie=0;function ae(){ie=0}function oe(){return ie}function se(e){ie=e}function ce(){let e=ie;return e>=p.maxTextures&&B(`WebGLTextures: Trying to use `+e+` texture units while this GPU supports only `+p.maxTextures),ie+=1,e}function le(e){let t=[];return t.push(e.wrapS),t.push(e.wrapT),t.push(e.wrapR||0),t.push(e.magFilter),t.push(e.minFilter),t.push(e.anisotropy),t.push(e.internalFormat),t.push(e.format),t.push(e.type),t.push(e.generateMipmaps),t.push(e.premultiplyAlpha),t.push(e.flipY),t.push(e.unpackAlignment),t.push(e.colorSpace),t.join()}function P(t,r){let i=f.get(t);if(t.isVideoTexture&&I(t),t.isRenderTargetTexture===!1&&t.isExternalTexture!==!0&&t.version>0&&i.__version!==t.version){let e=t.image;if(e===null)B(`WebGLRenderer: Texture marked for update but no image data found.`);else if(e.complete===!1)B(`WebGLRenderer: Texture marked for update but image is incomplete`);else{ye(i,t,r);return}}else t.isExternalTexture&&(i.__webglTexture=t.sourceTexture?t.sourceTexture:null);n.bindTexture(e.TEXTURE_2D,i.__webglTexture,e.TEXTURE0+r)}function ue(t,r){let i=f.get(t);if(t.isRenderTargetTexture===!1&&t.version>0&&i.__version!==t.version){ye(i,t,r);return}t.isExternalTexture&&(i.__webglTexture=t.sourceTexture?t.sourceTexture:null),n.bindTexture(e.TEXTURE_2D_ARRAY,i.__webglTexture,e.TEXTURE0+r)}function de(t,r){let i=f.get(t);if(t.isRenderTargetTexture===!1&&t.version>0&&i.__version!==t.version){ye(i,t,r);return}n.bindTexture(e.TEXTURE_3D,i.__webglTexture,e.TEXTURE0+r)}function fe(t,r){let i=f.get(t);if(t.isCubeDepthTexture!==!0&&t.version>0&&i.__version!==t.version){be(i,t,r);return}n.bindTexture(e.TEXTURE_CUBE_MAP,i.__webglTexture,e.TEXTURE0+r)}let pe={[r]:e.REPEAT,[i]:e.CLAMP_TO_EDGE,[a]:e.MIRRORED_REPEAT},me={[o]:e.NEAREST,[s]:e.NEAREST_MIPMAP_NEAREST,[c]:e.NEAREST_MIPMAP_LINEAR,[l]:e.LINEAR,[u]:e.LINEAR_MIPMAP_NEAREST,[d]:e.LINEAR_MIPMAP_LINEAR},F={512:e.NEVER,519:e.ALWAYS,513:e.LESS,515:e.LEQUAL,514:e.EQUAL,518:e.GEQUAL,516:e.GREATER,517:e.NOTEQUAL};function he(n,r){if(r.type===1015&&t.has(`OES_texture_float_linear`)===!1&&(r.magFilter===1006||r.magFilter===1007||r.magFilter===1005||r.magFilter===1008||r.minFilter===1006||r.minFilter===1007||r.minFilter===1005||r.minFilter===1008)&&B(`WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device.`),e.texParameteri(n,e.TEXTURE_WRAP_S,pe[r.wrapS]),e.texParameteri(n,e.TEXTURE_WRAP_T,pe[r.wrapT]),(n===e.TEXTURE_3D||n===e.TEXTURE_2D_ARRAY)&&e.texParameteri(n,e.TEXTURE_WRAP_R,pe[r.wrapR]),e.texParameteri(n,e.TEXTURE_MAG_FILTER,me[r.magFilter]),e.texParameteri(n,e.TEXTURE_MIN_FILTER,me[r.minFilter]),r.compareFunction&&(e.texParameteri(n,e.TEXTURE_COMPARE_MODE,e.COMPARE_REF_TO_TEXTURE),e.texParameteri(n,e.TEXTURE_COMPARE_FUNC,F[r.compareFunction])),t.has(`EXT_texture_filter_anisotropic`)===!0){if(r.magFilter===1003||r.minFilter!==1005&&r.minFilter!==1008||r.type===1015&&t.has(`OES_texture_float_linear`)===!1)return;if(r.anisotropy>1||f.get(r).__currentAnisotropy){let i=t.get(`EXT_texture_filter_anisotropic`);e.texParameterf(n,i.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(r.anisotropy,p.getMaxAnisotropy())),f.get(r).__currentAnisotropy=r.anisotropy}}}function ge(t,n){let r=!1;t.__webglInit===void 0&&(t.__webglInit=!0,n.addEventListener(`dispose`,j));let i=n.source,a=S.get(i);a===void 0&&(a={},S.set(i,a));let o=le(n);if(o!==t.__cacheKey){a[o]===void 0&&(a[o]={texture:e.createTexture(),usedTimes:0},h.memory.textures++,r=!0),a[o].usedTimes++;let i=a[t.__cacheKey];i!==void 0&&(a[t.__cacheKey].usedTimes--,i.usedTimes===0&&N(n)),t.__cacheKey=o,t.__webglTexture=a[o].texture}return r}function _e(e,t,n){return Math.floor(Math.floor(e/n)/t)}function ve(t,r,i,a){let o=t.updateRanges;if(o.length===0)n.texSubImage2D(e.TEXTURE_2D,0,0,0,r.width,r.height,i,a,r.data);else{o.sort((e,t)=>e.start-t.start);let s=0;for(let e=1;e<o.length;e++){let t=o[s],n=o[e],i=t.start+t.count,a=_e(n.start,r.width,4),c=_e(t.start,r.width,4);n.start<=i+1&&a===c&&_e(n.start+n.count-1,r.width,4)===a?t.count=Math.max(t.count,n.start+n.count-t.start):(++s,o[s]=n)}o.length=s+1;let c=n.getParameter(e.UNPACK_ROW_LENGTH),l=n.getParameter(e.UNPACK_SKIP_PIXELS),u=n.getParameter(e.UNPACK_SKIP_ROWS);n.pixelStorei(e.UNPACK_ROW_LENGTH,r.width);for(let t=0,s=o.length;t<s;t++){let s=o[t],c=Math.floor(s.start/4),l=Math.ceil(s.count/4),u=c%r.width,d=Math.floor(c/r.width),f=l;n.pixelStorei(e.UNPACK_SKIP_PIXELS,u),n.pixelStorei(e.UNPACK_SKIP_ROWS,d),n.texSubImage2D(e.TEXTURE_2D,0,u,d,f,1,i,a,r.data)}t.clearUpdateRanges(),n.pixelStorei(e.UNPACK_ROW_LENGTH,c),n.pixelStorei(e.UNPACK_SKIP_PIXELS,l),n.pixelStorei(e.UNPACK_SKIP_ROWS,u)}}function ye(t,r,i){let a=e.TEXTURE_2D;(r.isDataArrayTexture||r.isCompressedArrayTexture)&&(a=e.TEXTURE_2D_ARRAY),r.isData3DTexture&&(a=e.TEXTURE_3D);let o=ge(t,r),s=r.source;n.bindTexture(a,t.__webglTexture,e.TEXTURE0+i);let c=f.get(s);if(s.version!==c.__version||o===!0){if(n.activeTexture(e.TEXTURE0+i),!(typeof ImageBitmap<`u`&&r.image instanceof ImageBitmap)){let t=K.getPrimaries(K.workingColorSpace),i=r.colorSpace===``?null:K.getPrimaries(r.colorSpace),a=r.colorSpace===``||t===i?e.NONE:e.BROWSER_DEFAULT_WEBGL;n.pixelStorei(e.UNPACK_FLIP_Y_WEBGL,r.flipY),n.pixelStorei(e.UNPACK_PREMULTIPLY_ALPHA_WEBGL,r.premultiplyAlpha),n.pixelStorei(e.UNPACK_COLORSPACE_CONVERSION_WEBGL,a)}n.pixelStorei(e.UNPACK_ALIGNMENT,r.unpackAlignment);let t=T(r.image,!1,p.maxTextureSize);t=Ne(r,t);let l=m.convert(r.format,r.colorSpace),u=m.convert(r.type),d=A(r.internalFormat,l,u,r.normalized,r.colorSpace,r.isVideoTexture);he(a,r);let f,h=r.mipmaps,g=r.isVideoTexture!==!0,_=c.__version===void 0||o===!0,v=s.dataReady,y=te(r,t);if(r.isDepthTexture)d=ee(r.format===k,r.type),_&&(g?n.texStorage2D(e.TEXTURE_2D,1,d,t.width,t.height):n.texImage2D(e.TEXTURE_2D,0,d,t.width,t.height,0,l,u,null));else if(r.isDataTexture){if(h.length>0){g&&_&&n.texStorage2D(e.TEXTURE_2D,y,d,h[0].width,h[0].height);for(let t=0,r=h.length;t<r;t++)f=h[t],g?v&&n.texSubImage2D(e.TEXTURE_2D,t,0,0,f.width,f.height,l,u,f.data):n.texImage2D(e.TEXTURE_2D,t,d,f.width,f.height,0,l,u,f.data);r.generateMipmaps=!1}else g?(_&&n.texStorage2D(e.TEXTURE_2D,y,d,t.width,t.height),v&&ve(r,t,l,u)):n.texImage2D(e.TEXTURE_2D,0,d,t.width,t.height,0,l,u,t.data)}else if(r.isCompressedTexture){if(r.isCompressedArrayTexture){g&&_&&n.texStorage3D(e.TEXTURE_2D_ARRAY,y,d,h[0].width,h[0].height,t.depth);for(let i=0,a=h.length;i<a;i++)if(f=h[i],r.format!==1023){if(l!==null){if(g){if(v){if(r.layerUpdates.size>0){let t=uc(f.width,f.height,r.format,r.type);for(let a of r.layerUpdates){let r=f.data.subarray(a*t/f.data.BYTES_PER_ELEMENT,(a+1)*t/f.data.BYTES_PER_ELEMENT);n.compressedTexSubImage3D(e.TEXTURE_2D_ARRAY,i,0,0,a,f.width,f.height,1,l,r)}r.clearLayerUpdates()}else n.compressedTexSubImage3D(e.TEXTURE_2D_ARRAY,i,0,0,0,f.width,f.height,t.depth,l,f.data)}}else n.compressedTexImage3D(e.TEXTURE_2D_ARRAY,i,d,f.width,f.height,t.depth,0,f.data,0,0)}else B(`WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()`)}else g?v&&n.texSubImage3D(e.TEXTURE_2D_ARRAY,i,0,0,0,f.width,f.height,t.depth,l,u,f.data):n.texImage3D(e.TEXTURE_2D_ARRAY,i,d,f.width,f.height,t.depth,0,l,u,f.data)}else{g&&_&&n.texStorage2D(e.TEXTURE_2D,y,d,h[0].width,h[0].height);for(let t=0,i=h.length;t<i;t++)f=h[t],r.format===1023?g?v&&n.texSubImage2D(e.TEXTURE_2D,t,0,0,f.width,f.height,l,u,f.data):n.texImage2D(e.TEXTURE_2D,t,d,f.width,f.height,0,l,u,f.data):l===null?B(`WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()`):g?v&&n.compressedTexSubImage2D(e.TEXTURE_2D,t,0,0,f.width,f.height,l,f.data):n.compressedTexImage2D(e.TEXTURE_2D,t,d,f.width,f.height,0,f.data)}}else if(r.isDataArrayTexture){if(g){if(_&&n.texStorage3D(e.TEXTURE_2D_ARRAY,y,d,t.width,t.height,t.depth),v){if(r.layerUpdates.size>0){let i=uc(t.width,t.height,r.format,r.type);for(let a of r.layerUpdates){let r=t.data.subarray(a*i/t.data.BYTES_PER_ELEMENT,(a+1)*i/t.data.BYTES_PER_ELEMENT);n.texSubImage3D(e.TEXTURE_2D_ARRAY,0,0,0,a,t.width,t.height,1,l,u,r)}r.clearLayerUpdates()}else n.texSubImage3D(e.TEXTURE_2D_ARRAY,0,0,0,0,t.width,t.height,t.depth,l,u,t.data)}}else n.texImage3D(e.TEXTURE_2D_ARRAY,0,d,t.width,t.height,t.depth,0,l,u,t.data)}else if(r.isData3DTexture)g?(_&&n.texStorage3D(e.TEXTURE_3D,y,d,t.width,t.height,t.depth),v&&n.texSubImage3D(e.TEXTURE_3D,0,0,0,0,t.width,t.height,t.depth,l,u,t.data)):n.texImage3D(e.TEXTURE_3D,0,d,t.width,t.height,t.depth,0,l,u,t.data);else if(r.isFramebufferTexture){if(_){if(g)n.texStorage2D(e.TEXTURE_2D,y,d,t.width,t.height);else{let r=t.width,i=t.height;for(let t=0;t<y;t++)n.texImage2D(e.TEXTURE_2D,t,d,r,i,0,l,u,null),r>>=1,i>>=1}}}else if(r.isHTMLTexture){if(`texElementImage2D`in e){let n=e.canvas;if(n.hasAttribute(`layoutsubtree`)||n.setAttribute(`layoutsubtree`,`true`),t.parentNode!==n){n.appendChild(t),b.add(r),n.onpaint=e=>{let t=e.changedElements;for(let e of b)t.includes(e.image)&&(e.needsUpdate=!0)},n.requestPaint();return}if(e.texElementImage2D.length===3)e.texElementImage2D(e.TEXTURE_2D,e.RGBA8,t);else{let n=e.RGBA,r=e.RGBA,i=e.UNSIGNED_BYTE;e.texElementImage2D(e.TEXTURE_2D,0,n,r,i,t)}e.texParameteri(e.TEXTURE_2D,e.TEXTURE_MIN_FILTER,e.LINEAR),e.texParameteri(e.TEXTURE_2D,e.TEXTURE_WRAP_S,e.CLAMP_TO_EDGE),e.texParameteri(e.TEXTURE_2D,e.TEXTURE_WRAP_T,e.CLAMP_TO_EDGE)}}else if(h.length>0){if(g&&_){let t=Pe(h[0]);n.texStorage2D(e.TEXTURE_2D,y,d,t.width,t.height)}for(let t=0,r=h.length;t<r;t++)f=h[t],g?v&&n.texSubImage2D(e.TEXTURE_2D,t,0,0,l,u,f):n.texImage2D(e.TEXTURE_2D,t,d,l,u,f);r.generateMipmaps=!1}else if(g){if(_){let r=Pe(t);n.texStorage2D(e.TEXTURE_2D,y,d,r.width,r.height)}v&&n.texSubImage2D(e.TEXTURE_2D,0,0,0,l,u,t)}else n.texImage2D(e.TEXTURE_2D,0,d,l,u,t);E(r)&&D(a),c.__version=s.version,r.onUpdate&&r.onUpdate(r)}t.__version=r.version}function be(t,r,i){if(r.image.length!==6)return;let a=ge(t,r),o=r.source;n.bindTexture(e.TEXTURE_CUBE_MAP,t.__webglTexture,e.TEXTURE0+i);let s=f.get(o);if(o.version!==s.__version||a===!0){n.activeTexture(e.TEXTURE0+i);let t=K.getPrimaries(K.workingColorSpace),c=r.colorSpace===``?null:K.getPrimaries(r.colorSpace),l=r.colorSpace===``||t===c?e.NONE:e.BROWSER_DEFAULT_WEBGL;n.pixelStorei(e.UNPACK_FLIP_Y_WEBGL,r.flipY),n.pixelStorei(e.UNPACK_PREMULTIPLY_ALPHA_WEBGL,r.premultiplyAlpha),n.pixelStorei(e.UNPACK_ALIGNMENT,r.unpackAlignment),n.pixelStorei(e.UNPACK_COLORSPACE_CONVERSION_WEBGL,l);let u=r.isCompressedTexture||r.image[0].isCompressedTexture,d=r.image[0]&&r.image[0].isDataTexture,f=[];for(let e=0;e<6;e++)!u&&!d?f[e]=T(r.image[e],!0,p.maxCubemapSize):f[e]=d?r.image[e].image:r.image[e],f[e]=Ne(r,f[e]);let h=f[0],g=m.convert(r.format,r.colorSpace),_=m.convert(r.type),v=A(r.internalFormat,g,_,r.normalized,r.colorSpace),y=r.isVideoTexture!==!0,b=s.__version===void 0||a===!0,x=o.dataReady,S=te(r,h);he(e.TEXTURE_CUBE_MAP,r);let C;if(u){y&&b&&n.texStorage2D(e.TEXTURE_CUBE_MAP,S,v,h.width,h.height);for(let t=0;t<6;t++){C=f[t].mipmaps;for(let i=0;i<C.length;i++){let a=C[i];r.format===1023?y?x&&n.texSubImage2D(e.TEXTURE_CUBE_MAP_POSITIVE_X+t,i,0,0,a.width,a.height,g,_,a.data):n.texImage2D(e.TEXTURE_CUBE_MAP_POSITIVE_X+t,i,v,a.width,a.height,0,g,_,a.data):g===null?B(`WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()`):y?x&&n.compressedTexSubImage2D(e.TEXTURE_CUBE_MAP_POSITIVE_X+t,i,0,0,a.width,a.height,g,a.data):n.compressedTexImage2D(e.TEXTURE_CUBE_MAP_POSITIVE_X+t,i,v,a.width,a.height,0,a.data)}}}else{if(C=r.mipmaps,y&&b){C.length>0&&S++;let t=Pe(f[0]);n.texStorage2D(e.TEXTURE_CUBE_MAP,S,v,t.width,t.height)}for(let t=0;t<6;t++)if(d){y?x&&n.texSubImage2D(e.TEXTURE_CUBE_MAP_POSITIVE_X+t,0,0,0,f[t].width,f[t].height,g,_,f[t].data):n.texImage2D(e.TEXTURE_CUBE_MAP_POSITIVE_X+t,0,v,f[t].width,f[t].height,0,g,_,f[t].data);for(let r=0;r<C.length;r++){let i=C[r].image[t].image;y?x&&n.texSubImage2D(e.TEXTURE_CUBE_MAP_POSITIVE_X+t,r+1,0,0,i.width,i.height,g,_,i.data):n.texImage2D(e.TEXTURE_CUBE_MAP_POSITIVE_X+t,r+1,v,i.width,i.height,0,g,_,i.data)}}else{y?x&&n.texSubImage2D(e.TEXTURE_CUBE_MAP_POSITIVE_X+t,0,0,0,g,_,f[t]):n.texImage2D(e.TEXTURE_CUBE_MAP_POSITIVE_X+t,0,v,g,_,f[t]);for(let r=0;r<C.length;r++){let i=C[r];y?x&&n.texSubImage2D(e.TEXTURE_CUBE_MAP_POSITIVE_X+t,r+1,0,0,g,_,i.image[t]):n.texImage2D(e.TEXTURE_CUBE_MAP_POSITIVE_X+t,r+1,v,g,_,i.image[t])}}}E(r)&&D(e.TEXTURE_CUBE_MAP),s.__version=o.version,r.onUpdate&&r.onUpdate(r)}t.__version=r.version}function xe(t,r,i,a,o,s){let c=m.convert(i.format,i.colorSpace),l=m.convert(i.type),u=A(i.internalFormat,c,l,i.normalized,i.colorSpace),d=f.get(r),p=f.get(i);if(p.__renderTarget=r,!d.__hasExternalTextures){let t=Math.max(1,r.width>>s),i=Math.max(1,r.height>>s);o===e.TEXTURE_3D||o===e.TEXTURE_2D_ARRAY?n.texImage3D(o,s,u,t,i,r.depth,0,c,l,null):n.texImage2D(o,s,u,t,i,0,c,l,null)}n.bindFramebuffer(e.FRAMEBUFFER,t),Me(r)?g.framebufferTexture2DMultisampleEXT(e.FRAMEBUFFER,a,o,p.__webglTexture,0,je(r)):(o===e.TEXTURE_2D||o>=e.TEXTURE_CUBE_MAP_POSITIVE_X&&o<=e.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&e.framebufferTexture2D(e.FRAMEBUFFER,a,o,p.__webglTexture,s),n.bindFramebuffer(e.FRAMEBUFFER,null)}function Se(t,n,r){if(e.bindRenderbuffer(e.RENDERBUFFER,t),n.depthBuffer){let i=n.depthTexture,a=i&&i.isDepthTexture?i.type:null,o=ee(n.stencilBuffer,a),s=n.stencilBuffer?e.DEPTH_STENCIL_ATTACHMENT:e.DEPTH_ATTACHMENT;Me(n)?g.renderbufferStorageMultisampleEXT(e.RENDERBUFFER,je(n),o,n.width,n.height):r?e.renderbufferStorageMultisample(e.RENDERBUFFER,je(n),o,n.width,n.height):e.renderbufferStorage(e.RENDERBUFFER,o,n.width,n.height),e.framebufferRenderbuffer(e.FRAMEBUFFER,s,e.RENDERBUFFER,t)}else{let t=n.textures;for(let i=0;i<t.length;i++){let a=t[i],o=m.convert(a.format,a.colorSpace),s=m.convert(a.type),c=A(a.internalFormat,o,s,a.normalized,a.colorSpace);Me(n)?g.renderbufferStorageMultisampleEXT(e.RENDERBUFFER,je(n),c,n.width,n.height):r?e.renderbufferStorageMultisample(e.RENDERBUFFER,je(n),c,n.width,n.height):e.renderbufferStorage(e.RENDERBUFFER,c,n.width,n.height)}}e.bindRenderbuffer(e.RENDERBUFFER,null)}function Ce(t,r,i){let a=r.isWebGLCubeRenderTarget===!0;if(n.bindFramebuffer(e.FRAMEBUFFER,t),!(r.depthTexture&&r.depthTexture.isDepthTexture))throw Error(`THREE.WebGLTextures: renderTarget.depthTexture must be an instance of THREE.DepthTexture.`);let o=f.get(r.depthTexture);if(o.__renderTarget=r,(!o.__webglTexture||r.depthTexture.image.width!==r.width||r.depthTexture.image.height!==r.height)&&(r.depthTexture.image.width=r.width,r.depthTexture.image.height=r.height,r.depthTexture.needsUpdate=!0),a){if(o.__webglInit===void 0&&(o.__webglInit=!0,r.depthTexture.addEventListener(`dispose`,j)),o.__webglTexture===void 0){o.__webglTexture=e.createTexture(),n.bindTexture(e.TEXTURE_CUBE_MAP,o.__webglTexture),he(e.TEXTURE_CUBE_MAP,r.depthTexture);let t=m.convert(r.depthTexture.format),i=m.convert(r.depthTexture.type),a;r.depthTexture.format===1026?a=e.DEPTH_COMPONENT24:r.depthTexture.format===1027&&(a=e.DEPTH24_STENCIL8);for(let n=0;n<6;n++)e.texImage2D(e.TEXTURE_CUBE_MAP_POSITIVE_X+n,0,a,r.width,r.height,0,t,i,null)}}else P(r.depthTexture,0);let s=o.__webglTexture,c=je(r),l=a?e.TEXTURE_CUBE_MAP_POSITIVE_X+i:e.TEXTURE_2D,u=r.depthTexture.format===1027?e.DEPTH_STENCIL_ATTACHMENT:e.DEPTH_ATTACHMENT;if(r.depthTexture.format===1026)Me(r)?g.framebufferTexture2DMultisampleEXT(e.FRAMEBUFFER,u,l,s,0,c):e.framebufferTexture2D(e.FRAMEBUFFER,u,l,s,0);else if(r.depthTexture.format===1027)Me(r)?g.framebufferTexture2DMultisampleEXT(e.FRAMEBUFFER,u,l,s,0,c):e.framebufferTexture2D(e.FRAMEBUFFER,u,l,s,0);else throw Error(`THREE.WebGLTextures: Unknown depthTexture format.`)}function we(t){let r=f.get(t),i=t.isWebGLCubeRenderTarget===!0;if(r.__boundDepthTexture!==t.depthTexture){let e=t.depthTexture;if(r.__depthDisposeCallback&&r.__depthDisposeCallback(),e){let t=()=>{delete r.__boundDepthTexture,delete r.__depthDisposeCallback,e.removeEventListener(`dispose`,t)};e.addEventListener(`dispose`,t),r.__depthDisposeCallback=t}r.__boundDepthTexture=e}if(t.depthTexture&&!r.__autoAllocateDepthBuffer){if(i)for(let e=0;e<6;e++)Ce(r.__webglFramebuffer[e],t,e);else{let e=t.texture.mipmaps;e&&e.length>0?Ce(r.__webglFramebuffer[0],t,0):Ce(r.__webglFramebuffer,t,0)}}else if(i){r.__webglDepthbuffer=[];for(let i=0;i<6;i++)if(n.bindFramebuffer(e.FRAMEBUFFER,r.__webglFramebuffer[i]),r.__webglDepthbuffer[i]===void 0)r.__webglDepthbuffer[i]=e.createRenderbuffer(),Se(r.__webglDepthbuffer[i],t,!1);else{let n=t.stencilBuffer?e.DEPTH_STENCIL_ATTACHMENT:e.DEPTH_ATTACHMENT,a=r.__webglDepthbuffer[i];e.bindRenderbuffer(e.RENDERBUFFER,a),e.framebufferRenderbuffer(e.FRAMEBUFFER,n,e.RENDERBUFFER,a)}}else{let i=t.texture.mipmaps;if(i&&i.length>0?n.bindFramebuffer(e.FRAMEBUFFER,r.__webglFramebuffer[0]):n.bindFramebuffer(e.FRAMEBUFFER,r.__webglFramebuffer),r.__webglDepthbuffer===void 0)r.__webglDepthbuffer=e.createRenderbuffer(),Se(r.__webglDepthbuffer,t,!1);else{let n=t.stencilBuffer?e.DEPTH_STENCIL_ATTACHMENT:e.DEPTH_ATTACHMENT,i=r.__webglDepthbuffer;e.bindRenderbuffer(e.RENDERBUFFER,i),e.framebufferRenderbuffer(e.FRAMEBUFFER,n,e.RENDERBUFFER,i)}}n.bindFramebuffer(e.FRAMEBUFFER,null)}function Te(t,n,r){let i=f.get(t);n!==void 0&&xe(i.__webglFramebuffer,t,t.texture,e.COLOR_ATTACHMENT0,e.TEXTURE_2D,0),r!==void 0&&we(t)}function Ee(t){let r=t.texture,i=f.get(t),a=f.get(r);t.addEventListener(`dispose`,ne);let o=t.textures,s=t.isWebGLCubeRenderTarget===!0,c=o.length>1;if(c||(a.__webglTexture===void 0&&(a.__webglTexture=e.createTexture()),a.__version=r.version,h.memory.textures++),s){i.__webglFramebuffer=[];for(let t=0;t<6;t++)if(r.mipmaps&&r.mipmaps.length>0){i.__webglFramebuffer[t]=[];for(let n=0;n<r.mipmaps.length;n++)i.__webglFramebuffer[t][n]=e.createFramebuffer()}else i.__webglFramebuffer[t]=e.createFramebuffer()}else{if(r.mipmaps&&r.mipmaps.length>0){i.__webglFramebuffer=[];for(let t=0;t<r.mipmaps.length;t++)i.__webglFramebuffer[t]=e.createFramebuffer()}else i.__webglFramebuffer=e.createFramebuffer();if(c)for(let t=0,n=o.length;t<n;t++){let n=f.get(o[t]);n.__webglTexture===void 0&&(n.__webglTexture=e.createTexture(),h.memory.textures++)}if(t.samples>0&&Me(t)===!1){i.__webglMultisampledFramebuffer=e.createFramebuffer(),i.__webglColorRenderbuffer=[],n.bindFramebuffer(e.FRAMEBUFFER,i.__webglMultisampledFramebuffer);for(let n=0;n<o.length;n++){let r=o[n];i.__webglColorRenderbuffer[n]=e.createRenderbuffer(),e.bindRenderbuffer(e.RENDERBUFFER,i.__webglColorRenderbuffer[n]);let a=m.convert(r.format,r.colorSpace),s=m.convert(r.type),c=A(r.internalFormat,a,s,r.normalized,r.colorSpace,t.isXRRenderTarget===!0),l=je(t);e.renderbufferStorageMultisample(e.RENDERBUFFER,l,c,t.width,t.height),e.framebufferRenderbuffer(e.FRAMEBUFFER,e.COLOR_ATTACHMENT0+n,e.RENDERBUFFER,i.__webglColorRenderbuffer[n])}e.bindRenderbuffer(e.RENDERBUFFER,null),t.depthBuffer&&(i.__webglDepthRenderbuffer=e.createRenderbuffer(),Se(i.__webglDepthRenderbuffer,t,!0)),n.bindFramebuffer(e.FRAMEBUFFER,null)}}if(s){n.bindTexture(e.TEXTURE_CUBE_MAP,a.__webglTexture),he(e.TEXTURE_CUBE_MAP,r);for(let n=0;n<6;n++)if(r.mipmaps&&r.mipmaps.length>0)for(let a=0;a<r.mipmaps.length;a++)xe(i.__webglFramebuffer[n][a],t,r,e.COLOR_ATTACHMENT0,e.TEXTURE_CUBE_MAP_POSITIVE_X+n,a);else xe(i.__webglFramebuffer[n],t,r,e.COLOR_ATTACHMENT0,e.TEXTURE_CUBE_MAP_POSITIVE_X+n,0);E(r)&&D(e.TEXTURE_CUBE_MAP),n.unbindTexture()}else if(c){for(let r=0,a=o.length;r<a;r++){let a=o[r],s=f.get(a),c=e.TEXTURE_2D;(t.isWebGL3DRenderTarget||t.isWebGLArrayRenderTarget)&&(c=t.isWebGL3DRenderTarget?e.TEXTURE_3D:e.TEXTURE_2D_ARRAY),n.bindTexture(c,s.__webglTexture),he(c,a),xe(i.__webglFramebuffer,t,a,e.COLOR_ATTACHMENT0+r,c,0),E(a)&&D(c)}n.unbindTexture()}else{let o=e.TEXTURE_2D;if((t.isWebGL3DRenderTarget||t.isWebGLArrayRenderTarget)&&(o=t.isWebGL3DRenderTarget?e.TEXTURE_3D:e.TEXTURE_2D_ARRAY),n.bindTexture(o,a.__webglTexture),he(o,r),r.mipmaps&&r.mipmaps.length>0)for(let n=0;n<r.mipmaps.length;n++)xe(i.__webglFramebuffer[n],t,r,e.COLOR_ATTACHMENT0,o,n);else xe(i.__webglFramebuffer,t,r,e.COLOR_ATTACHMENT0,o,0);E(r)&&D(o),n.unbindTexture()}t.depthBuffer&&we(t)}function De(e){let t=e.textures;for(let r=0,i=t.length;r<i;r++){let i=t[r];if(E(i)){let t=O(e),r=f.get(i).__webglTexture;n.bindTexture(t,r),D(t),n.unbindTexture()}}}let Oe=[],ke=[];function Ae(t){if(t.samples>0){if(Me(t)===!1){let r=t.textures,i=t.width,a=t.height,o=e.COLOR_BUFFER_BIT,s=t.stencilBuffer?e.DEPTH_STENCIL_ATTACHMENT:e.DEPTH_ATTACHMENT,c=f.get(t),l=r.length>1;if(l)for(let t=0;t<r.length;t++)n.bindFramebuffer(e.FRAMEBUFFER,c.__webglMultisampledFramebuffer),e.framebufferRenderbuffer(e.FRAMEBUFFER,e.COLOR_ATTACHMENT0+t,e.RENDERBUFFER,null),n.bindFramebuffer(e.FRAMEBUFFER,c.__webglFramebuffer),e.framebufferTexture2D(e.DRAW_FRAMEBUFFER,e.COLOR_ATTACHMENT0+t,e.TEXTURE_2D,null,0);n.bindFramebuffer(e.READ_FRAMEBUFFER,c.__webglMultisampledFramebuffer);let u=t.texture.mipmaps;u&&u.length>0?n.bindFramebuffer(e.DRAW_FRAMEBUFFER,c.__webglFramebuffer[0]):n.bindFramebuffer(e.DRAW_FRAMEBUFFER,c.__webglFramebuffer);for(let n=0;n<r.length;n++){if(t.resolveDepthBuffer&&(t.depthBuffer&&(o|=e.DEPTH_BUFFER_BIT),t.stencilBuffer&&t.resolveStencilBuffer&&(o|=e.STENCIL_BUFFER_BIT)),l){e.framebufferRenderbuffer(e.READ_FRAMEBUFFER,e.COLOR_ATTACHMENT0,e.RENDERBUFFER,c.__webglColorRenderbuffer[n]);let t=f.get(r[n]).__webglTexture;e.framebufferTexture2D(e.DRAW_FRAMEBUFFER,e.COLOR_ATTACHMENT0,e.TEXTURE_2D,t,0)}e.blitFramebuffer(0,0,i,a,0,0,i,a,o,e.NEAREST),_===!0&&(Oe.length=0,ke.length=0,Oe.push(e.COLOR_ATTACHMENT0+n),t.depthBuffer&&t.resolveDepthBuffer===!1&&(Oe.push(s),ke.push(s),e.invalidateFramebuffer(e.DRAW_FRAMEBUFFER,ke)),e.invalidateFramebuffer(e.READ_FRAMEBUFFER,Oe))}if(n.bindFramebuffer(e.READ_FRAMEBUFFER,null),n.bindFramebuffer(e.DRAW_FRAMEBUFFER,null),l)for(let t=0;t<r.length;t++){n.bindFramebuffer(e.FRAMEBUFFER,c.__webglMultisampledFramebuffer),e.framebufferRenderbuffer(e.FRAMEBUFFER,e.COLOR_ATTACHMENT0+t,e.RENDERBUFFER,c.__webglColorRenderbuffer[t]);let i=f.get(r[t]).__webglTexture;n.bindFramebuffer(e.FRAMEBUFFER,c.__webglFramebuffer),e.framebufferTexture2D(e.DRAW_FRAMEBUFFER,e.COLOR_ATTACHMENT0+t,e.TEXTURE_2D,i,0)}n.bindFramebuffer(e.DRAW_FRAMEBUFFER,c.__webglMultisampledFramebuffer)}else if(t.depthBuffer&&t.resolveDepthBuffer===!1&&_){let n=t.stencilBuffer?e.DEPTH_STENCIL_ATTACHMENT:e.DEPTH_ATTACHMENT;e.invalidateFramebuffer(e.DRAW_FRAMEBUFFER,[n])}}}function je(e){return Math.min(p.maxSamples,e.samples)}function Me(e){let n=f.get(e);return e.samples>0&&t.has(`WEBGL_multisampled_render_to_texture`)===!0&&n.__useRenderToTexture!==!1}function I(e){let t=h.render.frame;y.get(e)!==t&&(y.set(e,t),e.update())}function Ne(e,t){let n=e.colorSpace,r=e.format,i=e.type;return e.isCompressedTexture===!0||e.isVideoTexture===!0||n!==`srgb-linear`&&n!==``&&(K.getTransfer(n)===`srgb`?(r!==1023||i!==1009)&&B(`WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType.`):V(`WebGLTextures: Unsupported texture color space:`,n)),t}function Pe(e){return typeof HTMLImageElement<`u`&&e instanceof HTMLImageElement?(v.width=e.naturalWidth||e.width,v.height=e.naturalHeight||e.height):typeof VideoFrame<`u`&&e instanceof VideoFrame?(v.width=e.displayWidth,v.height=e.displayHeight):(v.width=e.width,v.height=e.height),v}this.allocateTextureUnit=ce,this.resetTextureUnits=ae,this.getTextureUnits=oe,this.setTextureUnits=se,this.setTexture2D=P,this.setTexture2DArray=ue,this.setTexture3D=de,this.setTextureCube=fe,this.rebindTextures=Te,this.setupRenderTarget=Ee,this.updateRenderTargetMipmap=De,this.updateMultisampleRenderTarget=Ae,this.setupDepthRenderbuffer=we,this.setupFrameBufferTexture=xe,this.useMultisampledRTT=Me,this.isReversedDepthBuffer=function(){return n.buffers.depth.getReversed()}}function gd(e,t){function n(n,r=``){let i,a=K.getTransfer(r);if(n===1009)return e.UNSIGNED_BYTE;if(n===1017)return e.UNSIGNED_SHORT_4_4_4_4;if(n===1018)return e.UNSIGNED_SHORT_5_5_5_1;if(n===35902)return e.UNSIGNED_INT_5_9_9_9_REV;if(n===35899)return e.UNSIGNED_INT_10F_11F_11F_REV;if(n===1010)return e.BYTE;if(n===1011)return e.SHORT;if(n===1012)return e.UNSIGNED_SHORT;if(n===1013)return e.INT;if(n===1014)return e.UNSIGNED_INT;if(n===1015)return e.FLOAT;if(n===1016)return e.HALF_FLOAT;if(n===1021)return e.ALPHA;if(n===1022)return e.RGB;if(n===1023)return e.RGBA;if(n===1026)return e.DEPTH_COMPONENT;if(n===1027)return e.DEPTH_STENCIL;if(n===1028)return e.RED;if(n===1029)return e.RED_INTEGER;if(n===1030)return e.RG;if(n===1031)return e.RG_INTEGER;if(n===1033)return e.RGBA_INTEGER;if(n===33776||n===33777||n===33778||n===33779){if(a===`srgb`){if(i=t.get(`WEBGL_compressed_texture_s3tc_srgb`),i!==null){if(n===33776)return i.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(n===33777)return i.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(n===33778)return i.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(n===33779)return i.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null}else if(i=t.get(`WEBGL_compressed_texture_s3tc`),i!==null){if(n===33776)return i.COMPRESSED_RGB_S3TC_DXT1_EXT;if(n===33777)return i.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(n===33778)return i.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(n===33779)return i.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null}if(n===35840||n===35841||n===35842||n===35843){if(i=t.get(`WEBGL_compressed_texture_pvrtc`),i!==null){if(n===35840)return i.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(n===35841)return i.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(n===35842)return i.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(n===35843)return i.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null}if(n===36196||n===37492||n===37496||n===37488||n===37489||n===37490||n===37491){if(i=t.get(`WEBGL_compressed_texture_etc`),i!==null){if(n===36196||n===37492)return a===`srgb`?i.COMPRESSED_SRGB8_ETC2:i.COMPRESSED_RGB8_ETC2;if(n===37496)return a===`srgb`?i.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:i.COMPRESSED_RGBA8_ETC2_EAC;if(n===37488)return i.COMPRESSED_R11_EAC;if(n===37489)return i.COMPRESSED_SIGNED_R11_EAC;if(n===37490)return i.COMPRESSED_RG11_EAC;if(n===37491)return i.COMPRESSED_SIGNED_RG11_EAC}else return null}if(n===37808||n===37809||n===37810||n===37811||n===37812||n===37813||n===37814||n===37815||n===37816||n===37817||n===37818||n===37819||n===37820||n===37821){if(i=t.get(`WEBGL_compressed_texture_astc`),i!==null){if(n===37808)return a===`srgb`?i.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:i.COMPRESSED_RGBA_ASTC_4x4_KHR;if(n===37809)return a===`srgb`?i.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:i.COMPRESSED_RGBA_ASTC_5x4_KHR;if(n===37810)return a===`srgb`?i.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:i.COMPRESSED_RGBA_ASTC_5x5_KHR;if(n===37811)return a===`srgb`?i.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:i.COMPRESSED_RGBA_ASTC_6x5_KHR;if(n===37812)return a===`srgb`?i.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:i.COMPRESSED_RGBA_ASTC_6x6_KHR;if(n===37813)return a===`srgb`?i.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:i.COMPRESSED_RGBA_ASTC_8x5_KHR;if(n===37814)return a===`srgb`?i.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:i.COMPRESSED_RGBA_ASTC_8x6_KHR;if(n===37815)return a===`srgb`?i.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:i.COMPRESSED_RGBA_ASTC_8x8_KHR;if(n===37816)return a===`srgb`?i.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:i.COMPRESSED_RGBA_ASTC_10x5_KHR;if(n===37817)return a===`srgb`?i.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:i.COMPRESSED_RGBA_ASTC_10x6_KHR;if(n===37818)return a===`srgb`?i.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:i.COMPRESSED_RGBA_ASTC_10x8_KHR;if(n===37819)return a===`srgb`?i.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:i.COMPRESSED_RGBA_ASTC_10x10_KHR;if(n===37820)return a===`srgb`?i.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:i.COMPRESSED_RGBA_ASTC_12x10_KHR;if(n===37821)return a===`srgb`?i.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:i.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null}if(n===36492||n===36494||n===36495){if(i=t.get(`EXT_texture_compression_bptc`),i!==null){if(n===36492)return a===`srgb`?i.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:i.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(n===36494)return i.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(n===36495)return i.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null}if(n===36283||n===36284||n===36285||n===36286){if(i=t.get(`EXT_texture_compression_rgtc`),i!==null){if(n===36283)return i.COMPRESSED_RED_RGTC1_EXT;if(n===36284)return i.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(n===36285)return i.COMPRESSED_RED_GREEN_RGTC2_EXT;if(n===36286)return i.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null}return n===1020?e.UNSIGNED_INT_24_8:e[n]===void 0?null:e[n]}return{convert:n}}var _d=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,vd=`
uniform sampler2DArray depthColor;
uniform float depthWidth;
uniform float depthHeight;

void main() {

	vec2 coord = vec2( gl_FragCoord.x / depthWidth, gl_FragCoord.y / depthHeight );

	if ( coord.x >= 1.0 ) {

		gl_FragDepth = texture( depthColor, vec3( coord.x - 1.0, coord.y, 1 ) ).r;

	} else {

		gl_FragDepth = texture( depthColor, vec3( coord.x, coord.y, 0 ) ).r;

	}

}`,yd=class{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(e,t){if(this.texture===null){let n=new oa(e.texture);(e.depthNear!==t.depthNear||e.depthFar!==t.depthFar)&&(this.depthNear=e.depthNear,this.depthFar=e.depthFar),this.texture=n}}getMesh(e){if(this.texture!==null&&this.mesh===null){let t=e.cameras[0].viewport,n=new Lo({vertexShader:_d,fragmentShader:vd,uniforms:{depthColor:{value:this.texture},depthWidth:{value:t.z},depthHeight:{value:t.w}}});this.mesh=new ei(new Do(20,20),n)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}},bd=class extends it{constructor(e,t){super();let n=this,r=null,i=1,a=null,o=`local-floor`,s=1,c=null,l=null,u=null,d=null,p=null,m=null,h=typeof XRWebGLBinding<`u`,g=new yd,v={},y=t.getContextAttributes(),b=null,x=null,C=[],w=[],T=new U,E=null,A=new js;A.viewport=new Jt;let ee=new js;ee.viewport=new Jt;let te=[A,ee],j=new Gs,ne=null,M=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(e){let t=C[e];return t===void 0&&(t=new kn,C[e]=t),t.getTargetRaySpace()},this.getControllerGrip=function(e){let t=C[e];return t===void 0&&(t=new kn,C[e]=t),t.getGripSpace()},this.getHand=function(e){let t=C[e];return t===void 0&&(t=new kn,C[e]=t),t.getHandSpace()};function N(e){let t=w.indexOf(e.inputSource);if(t===-1)return;let n=C[t];n!==void 0&&(n.update(e.inputSource,e.frame,c||a),n.dispatchEvent({type:e.type,data:e.inputSource}))}function re(){r.removeEventListener(`select`,N),r.removeEventListener(`selectstart`,N),r.removeEventListener(`selectend`,N),r.removeEventListener(`squeeze`,N),r.removeEventListener(`squeezestart`,N),r.removeEventListener(`squeezeend`,N),r.removeEventListener(`end`,re),r.removeEventListener(`inputsourceschange`,ie);for(let e=0;e<C.length;e++){let t=w[e];t!==null&&(w[e]=null,C[e].disconnect(t))}ne=null,M=null,g.reset();for(let e in v)delete v[e];e.setRenderTarget(b),p=null,d=null,u=null,r=null,x=null,de.stop(),n.isPresenting=!1,e.setPixelRatio(E),e.setSize(T.width,T.height,!1),n.dispatchEvent({type:`sessionend`})}this.setFramebufferScaleFactor=function(e){i=e,n.isPresenting===!0&&B(`WebXRManager: Cannot change framebuffer scale while presenting.`)},this.setReferenceSpaceType=function(e){o=e,n.isPresenting===!0&&B(`WebXRManager: Cannot change reference space type while presenting.`)},this.getReferenceSpace=function(){return c||a},this.setReferenceSpace=function(e){c=e},this.getBaseLayer=function(){return d===null?p:d},this.getBinding=function(){return u===null&&h&&(u=new XRWebGLBinding(r,t)),u},this.getFrame=function(){return m},this.getSession=function(){return r},this.setSession=async function(l){if(r=l,r!==null){if(b=e.getRenderTarget(),r.addEventListener(`select`,N),r.addEventListener(`selectstart`,N),r.addEventListener(`selectend`,N),r.addEventListener(`squeeze`,N),r.addEventListener(`squeezestart`,N),r.addEventListener(`squeezeend`,N),r.addEventListener(`end`,re),r.addEventListener(`inputsourceschange`,ie),y.xrCompatible!==!0&&await t.makeXRCompatible(),E=e.getPixelRatio(),e.getSize(T),h&&`createProjectionLayer`in XRWebGLBinding.prototype){let n=null,a=null,o=null;y.depth&&(o=y.stencil?t.DEPTH24_STENCIL8:t.DEPTH_COMPONENT24,n=y.stencil?k:O,a=y.stencil?S:_);let s={colorFormat:t.RGBA8,depthFormat:o,scaleFactor:i};u=this.getBinding(),d=u.createProjectionLayer(s),r.updateRenderState({layers:[d]}),e.setPixelRatio(1),e.setSize(d.textureWidth,d.textureHeight,!1),x=new Xt(d.textureWidth,d.textureHeight,{format:D,type:f,depthTexture:new ia(d.textureWidth,d.textureHeight,a,void 0,void 0,void 0,void 0,void 0,void 0,n),stencilBuffer:y.stencil,colorSpace:e.outputColorSpace,samples:y.antialias?4:0,resolveDepthBuffer:d.ignoreDepthValues===!1,resolveStencilBuffer:d.ignoreDepthValues===!1})}else{let n={antialias:y.antialias,alpha:!0,depth:y.depth,stencil:y.stencil,framebufferScaleFactor:i};p=new XRWebGLLayer(r,t,n),r.updateRenderState({baseLayer:p}),e.setPixelRatio(1),e.setSize(p.framebufferWidth,p.framebufferHeight,!1),x=new Xt(p.framebufferWidth,p.framebufferHeight,{format:D,type:f,colorSpace:e.outputColorSpace,stencilBuffer:y.stencil,resolveDepthBuffer:p.ignoreDepthValues===!1,resolveStencilBuffer:p.ignoreDepthValues===!1})}x.isXRRenderTarget=!0,this.setFoveation(s),c=null,a=await r.requestReferenceSpace(o),de.setContext(r),de.start(),n.isPresenting=!0,n.dispatchEvent({type:`sessionstart`})}},this.getEnvironmentBlendMode=function(){if(r!==null)return r.environmentBlendMode},this.getDepthTexture=function(){return g.getDepthTexture()};function ie(e){for(let t=0;t<e.removed.length;t++){let n=e.removed[t],r=w.indexOf(n);r>=0&&(w[r]=null,C[r].disconnect(n))}for(let t=0;t<e.added.length;t++){let n=e.added[t],r=w.indexOf(n);if(r===-1){for(let e=0;e<C.length;e++)if(e>=w.length){w.push(n),r=e;break}else if(w[e]===null){w[e]=n,r=e;break}if(r===-1)break}let i=C[r];i&&i.connect(n)}}let ae=new W,oe=new W;function se(e,t,n){ae.setFromMatrixPosition(t.matrixWorld),oe.setFromMatrixPosition(n.matrixWorld);let r=ae.distanceTo(oe),i=t.projectionMatrix.elements,a=n.projectionMatrix.elements,o=i[14]/(i[10]-1),s=i[14]/(i[10]+1),c=(i[9]+1)/i[5],l=(i[9]-1)/i[5],u=(i[8]-1)/i[0],d=(a[8]+1)/a[0],f=o*u,p=o*d,m=r/(-u+d),h=m*-u;if(t.matrixWorld.decompose(e.position,e.quaternion,e.scale),e.translateX(h),e.translateZ(m),e.matrixWorld.compose(e.position,e.quaternion,e.scale),e.matrixWorldInverse.copy(e.matrixWorld).invert(),i[10]===-1)e.projectionMatrix.copy(t.projectionMatrix),e.projectionMatrixInverse.copy(t.projectionMatrixInverse);else{let t=o+m,n=s+m,i=f-h,a=p+(r-h),u=c*s/n*t,d=l*s/n*t;e.projectionMatrix.makePerspective(i,a,u,d,t,n),e.projectionMatrixInverse.copy(e.projectionMatrix).invert()}}function ce(e,t){t===null?e.matrixWorld.copy(e.matrix):e.matrixWorld.multiplyMatrices(t.matrixWorld,e.matrix),e.matrixWorldInverse.copy(e.matrixWorld).invert()}this.updateCamera=function(e){if(r===null)return;let t=e.near,n=e.far;g.texture!==null&&(g.depthNear>0&&(t=g.depthNear),g.depthFar>0&&(n=g.depthFar)),j.near=ee.near=A.near=t,j.far=ee.far=A.far=n,(ne!==j.near||M!==j.far)&&(r.updateRenderState({depthNear:j.near,depthFar:j.far}),ne=j.near,M=j.far),j.layers.mask=e.layers.mask|6,A.layers.mask=j.layers.mask&-5,ee.layers.mask=j.layers.mask&-3;let i=e.parent,a=j.cameras;ce(j,i);for(let e=0;e<a.length;e++)ce(a[e],i);a.length===2?se(j,A,ee):j.projectionMatrix.copy(A.projectionMatrix),le(e,j,i)};function le(e,t,n){n===null?e.matrix.copy(t.matrixWorld):(e.matrix.copy(n.matrixWorld),e.matrix.invert(),e.matrix.multiply(t.matrixWorld)),e.matrix.decompose(e.position,e.quaternion,e.scale),e.updateMatrixWorld(!0),e.projectionMatrix.copy(t.projectionMatrix),e.projectionMatrixInverse.copy(t.projectionMatrixInverse),e.isPerspectiveCamera&&(e.fov=ct*2*Math.atan(1/e.projectionMatrix.elements[5]),e.zoom=1)}this.getCamera=function(){return j},this.getFoveation=function(){if(d!==null||p!==null)return s},this.setFoveation=function(e){s=e,d!==null&&(d.fixedFoveation=e),p!==null&&p.fixedFoveation!==void 0&&(p.fixedFoveation=e)},this.hasDepthSensing=function(){return g.texture!==null},this.getDepthSensingMesh=function(){return g.getMesh(j)},this.getCameraTexture=function(e){return v[e]};let P=null;function ue(t,i){if(l=i.getViewerPose(c||a),m=i,l!==null){let t=l.views;p!==null&&(e.setRenderTargetFramebuffer(x,p.framebuffer),e.setRenderTarget(x));let i=!1;t.length!==j.cameras.length&&(j.cameras.length=0,i=!0);for(let n=0;n<t.length;n++){let r=t[n],a=null;if(p!==null)a=p.getViewport(r);else{let t=u.getViewSubImage(d,r);a=t.viewport,n===0&&(e.setRenderTargetTextures(x,t.colorTexture,t.depthStencilTexture),e.setRenderTarget(x))}let o=te[n];o===void 0&&(o=new js,o.layers.enable(n),o.viewport=new Jt,te[n]=o),o.matrix.fromArray(r.transform.matrix),o.matrix.decompose(o.position,o.quaternion,o.scale),o.projectionMatrix.fromArray(r.projectionMatrix),o.projectionMatrixInverse.copy(o.projectionMatrix).invert(),o.viewport.set(a.x,a.y,a.width,a.height),n===0&&(j.matrix.copy(o.matrix),j.matrix.decompose(j.position,j.quaternion,j.scale)),i===!0&&j.cameras.push(o)}let a=r.enabledFeatures;if(a&&a.includes(`depth-sensing`)&&r.depthUsage==`gpu-optimized`&&h){u=n.getBinding();let e=u.getDepthInformation(t[0]);e&&e.isValid&&e.texture&&g.init(e,r.renderState)}if(a&&a.includes(`camera-access`)&&h){e.state.unbindTexture(),u=n.getBinding();for(let e=0;e<t.length;e++){let n=t[e].camera;if(n){let e=v[n];e||(e=new oa,v[n]=e);let t=u.getCameraImage(n);e.sourceTexture=t}}}}for(let e=0;e<C.length;e++){let t=w[e],n=C[e];t!==null&&n!==void 0&&n.update(t,i,c||a)}P&&P(t,i),i.detectedPlanes&&n.dispatchEvent({type:`planesdetected`,data:i}),m=null}let de=new fc;de.setAnimationLoop(ue),this.setAnimationLoop=function(e){P=e},this.dispose=function(){}}},xd=new q,Sd=new G;Sd.set(-1,0,0,0,1,0,0,0,1);function Cd(e,t){function n(e,t){e.matrixAutoUpdate===!0&&e.updateMatrix(),t.value.copy(e.matrix)}function r(t,n){n.color.getRGB(t.fogColor.value,No(e)),n.isFog?(t.fogNear.value=n.near,t.fogFar.value=n.far):n.isFogExp2&&(t.fogDensity.value=n.density)}function i(e,t,n,r,i){t.isNodeMaterial?t.uniformsNeedUpdate=!1:t.isMeshBasicMaterial?a(e,t):t.isMeshLambertMaterial?(a(e,t),t.envMap&&(e.envMapIntensity.value=t.envMapIntensity)):t.isMeshToonMaterial?(a(e,t),d(e,t)):t.isMeshPhongMaterial?(a(e,t),u(e,t),t.envMap&&(e.envMapIntensity.value=t.envMapIntensity)):t.isMeshStandardMaterial?(a(e,t),f(e,t),t.isMeshPhysicalMaterial&&p(e,t,i)):t.isMeshMatcapMaterial?(a(e,t),m(e,t)):t.isMeshDepthMaterial?a(e,t):t.isMeshDistanceMaterial?(a(e,t),h(e,t)):t.isMeshNormalMaterial?a(e,t):t.isLineBasicMaterial?(o(e,t),t.isLineDashedMaterial&&s(e,t)):t.isPointsMaterial?c(e,t,n,r):t.isSpriteMaterial?l(e,t):t.isShadowMaterial?(e.color.value.copy(t.color),e.opacity.value=t.opacity):t.isShaderMaterial&&(t.uniformsNeedUpdate=!1)}function a(e,r){e.opacity.value=r.opacity,r.color&&e.diffuse.value.copy(r.color),r.emissive&&e.emissive.value.copy(r.emissive).multiplyScalar(r.emissiveIntensity),r.map&&(e.map.value=r.map,n(r.map,e.mapTransform)),r.alphaMap&&(e.alphaMap.value=r.alphaMap,n(r.alphaMap,e.alphaMapTransform)),r.bumpMap&&(e.bumpMap.value=r.bumpMap,n(r.bumpMap,e.bumpMapTransform),e.bumpScale.value=r.bumpScale,r.side===1&&(e.bumpScale.value*=-1)),r.normalMap&&(e.normalMap.value=r.normalMap,n(r.normalMap,e.normalMapTransform),e.normalScale.value.copy(r.normalScale),r.side===1&&e.normalScale.value.negate()),r.displacementMap&&(e.displacementMap.value=r.displacementMap,n(r.displacementMap,e.displacementMapTransform),e.displacementScale.value=r.displacementScale,e.displacementBias.value=r.displacementBias),r.emissiveMap&&(e.emissiveMap.value=r.emissiveMap,n(r.emissiveMap,e.emissiveMapTransform)),r.specularMap&&(e.specularMap.value=r.specularMap,n(r.specularMap,e.specularMapTransform)),r.alphaTest>0&&(e.alphaTest.value=r.alphaTest);let i=t.get(r),a=i.envMap,o=i.envMapRotation;a&&(e.envMap.value=a,e.envMapRotation.value.setFromMatrix4(xd.makeRotationFromEuler(o)).transpose(),a.isCubeTexture&&a.isRenderTargetTexture===!1&&e.envMapRotation.value.premultiply(Sd),e.reflectivity.value=r.reflectivity,e.ior.value=r.ior,e.refractionRatio.value=r.refractionRatio),r.lightMap&&(e.lightMap.value=r.lightMap,e.lightMapIntensity.value=r.lightMapIntensity,n(r.lightMap,e.lightMapTransform)),r.aoMap&&(e.aoMap.value=r.aoMap,e.aoMapIntensity.value=r.aoMapIntensity,n(r.aoMap,e.aoMapTransform))}function o(e,t){e.diffuse.value.copy(t.color),e.opacity.value=t.opacity,t.map&&(e.map.value=t.map,n(t.map,e.mapTransform))}function s(e,t){e.dashSize.value=t.dashSize,e.totalSize.value=t.dashSize+t.gapSize,e.scale.value=t.scale}function c(e,t,r,i){e.diffuse.value.copy(t.color),e.opacity.value=t.opacity,e.size.value=t.size*r,e.scale.value=i*.5,t.map&&(e.map.value=t.map,n(t.map,e.uvTransform)),t.alphaMap&&(e.alphaMap.value=t.alphaMap,n(t.alphaMap,e.alphaMapTransform)),t.alphaTest>0&&(e.alphaTest.value=t.alphaTest)}function l(e,t){e.diffuse.value.copy(t.color),e.opacity.value=t.opacity,e.rotation.value=t.rotation,t.map&&(e.map.value=t.map,n(t.map,e.mapTransform)),t.alphaMap&&(e.alphaMap.value=t.alphaMap,n(t.alphaMap,e.alphaMapTransform)),t.alphaTest>0&&(e.alphaTest.value=t.alphaTest)}function u(e,t){e.specular.value.copy(t.specular),e.shininess.value=Math.max(t.shininess,1e-4)}function d(e,t){t.gradientMap&&(e.gradientMap.value=t.gradientMap)}function f(e,t){e.metalness.value=t.metalness,t.metalnessMap&&(e.metalnessMap.value=t.metalnessMap,n(t.metalnessMap,e.metalnessMapTransform)),e.roughness.value=t.roughness,t.roughnessMap&&(e.roughnessMap.value=t.roughnessMap,n(t.roughnessMap,e.roughnessMapTransform)),t.envMap&&(e.envMapIntensity.value=t.envMapIntensity)}function p(e,t,r){e.ior.value=t.ior,t.sheen>0&&(e.sheenColor.value.copy(t.sheenColor).multiplyScalar(t.sheen),e.sheenRoughness.value=t.sheenRoughness,t.sheenColorMap&&(e.sheenColorMap.value=t.sheenColorMap,n(t.sheenColorMap,e.sheenColorMapTransform)),t.sheenRoughnessMap&&(e.sheenRoughnessMap.value=t.sheenRoughnessMap,n(t.sheenRoughnessMap,e.sheenRoughnessMapTransform))),t.clearcoat>0&&(e.clearcoat.value=t.clearcoat,e.clearcoatRoughness.value=t.clearcoatRoughness,t.clearcoatMap&&(e.clearcoatMap.value=t.clearcoatMap,n(t.clearcoatMap,e.clearcoatMapTransform)),t.clearcoatRoughnessMap&&(e.clearcoatRoughnessMap.value=t.clearcoatRoughnessMap,n(t.clearcoatRoughnessMap,e.clearcoatRoughnessMapTransform)),t.clearcoatNormalMap&&(e.clearcoatNormalMap.value=t.clearcoatNormalMap,n(t.clearcoatNormalMap,e.clearcoatNormalMapTransform),e.clearcoatNormalScale.value.copy(t.clearcoatNormalScale),t.side===1&&e.clearcoatNormalScale.value.negate())),t.dispersion>0&&(e.dispersion.value=t.dispersion),t.iridescence>0&&(e.iridescence.value=t.iridescence,e.iridescenceIOR.value=t.iridescenceIOR,e.iridescenceThicknessMinimum.value=t.iridescenceThicknessRange[0],e.iridescenceThicknessMaximum.value=t.iridescenceThicknessRange[1],t.iridescenceMap&&(e.iridescenceMap.value=t.iridescenceMap,n(t.iridescenceMap,e.iridescenceMapTransform)),t.iridescenceThicknessMap&&(e.iridescenceThicknessMap.value=t.iridescenceThicknessMap,n(t.iridescenceThicknessMap,e.iridescenceThicknessMapTransform))),t.transmission>0&&(e.transmission.value=t.transmission,e.transmissionSamplerMap.value=r.texture,e.transmissionSamplerSize.value.set(r.width,r.height),t.transmissionMap&&(e.transmissionMap.value=t.transmissionMap,n(t.transmissionMap,e.transmissionMapTransform)),e.thickness.value=t.thickness,t.thicknessMap&&(e.thicknessMap.value=t.thicknessMap,n(t.thicknessMap,e.thicknessMapTransform)),e.attenuationDistance.value=t.attenuationDistance,e.attenuationColor.value.copy(t.attenuationColor)),t.anisotropy>0&&(e.anisotropyVector.value.set(t.anisotropy*Math.cos(t.anisotropyRotation),t.anisotropy*Math.sin(t.anisotropyRotation)),t.anisotropyMap&&(e.anisotropyMap.value=t.anisotropyMap,n(t.anisotropyMap,e.anisotropyMapTransform))),e.specularIntensity.value=t.specularIntensity,e.specularColor.value.copy(t.specularColor),t.specularColorMap&&(e.specularColorMap.value=t.specularColorMap,n(t.specularColorMap,e.specularColorMapTransform)),t.specularIntensityMap&&(e.specularIntensityMap.value=t.specularIntensityMap,n(t.specularIntensityMap,e.specularIntensityMapTransform))}function m(e,t){t.matcap&&(e.matcap.value=t.matcap)}function h(e,n){let r=t.get(n).light;e.referencePosition.value.setFromMatrixPosition(r.matrixWorld),e.nearDistance.value=r.shadow.camera.near,e.farDistance.value=r.shadow.camera.far}return{refreshFogUniforms:r,refreshMaterialUniforms:i}}function wd(e,t,n,r){let i={},a={},o=[],s=e.getParameter(e.MAX_UNIFORM_BUFFER_BINDINGS);function c(e,t){let n=t.program;r.uniformBlockBinding(e,n)}function l(e,n){let o=i[e.id];o===void 0&&(g(e),o=u(e),i[e.id]=o,e.addEventListener(`dispose`,v));let s=n.program;r.updateUBOMapping(e,s);let c=t.render.frame;a[e.id]!==c&&(f(e),a[e.id]=c)}function u(t){let n=d();t.__bindingPointIndex=n;let r=e.createBuffer(),i=t.__size,a=t.usage;return e.bindBuffer(e.UNIFORM_BUFFER,r),e.bufferData(e.UNIFORM_BUFFER,i,a),e.bindBuffer(e.UNIFORM_BUFFER,null),e.bindBufferBase(e.UNIFORM_BUFFER,n,r),r}function d(){for(let e=0;e<s;e++)if(o.indexOf(e)===-1)return o.push(e),e;return V(`WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached.`),0}function f(t){let n=i[t.id],r=t.uniforms,a=t.__cache;e.bindBuffer(e.UNIFORM_BUFFER,n);for(let e=0,t=r.length;e<t;e++){let t=r[e];if(Array.isArray(t))for(let n=0,r=t.length;n<r;n++)p(t[n],e,n,a);else p(t,e,0,a)}e.bindBuffer(e.UNIFORM_BUFFER,null)}function p(t,n,r,i){if(h(t,n,r,i)===!0){let n=t.__offset,r=t.value;if(Array.isArray(r)){let e=0;for(let n=0;n<r.length;n++){let i=r[n],a=_(i);m(i,t.__data,e),typeof i!=`number`&&typeof i!=`boolean`&&!i.isMatrix3&&!ArrayBuffer.isView(i)&&(e+=a.storage/Float32Array.BYTES_PER_ELEMENT)}}else m(r,t.__data,0);e.bufferSubData(e.UNIFORM_BUFFER,n,t.__data)}}function m(e,t,n){typeof e==`number`||typeof e==`boolean`?t[0]=e:e.isMatrix3?(t[0]=e.elements[0],t[1]=e.elements[1],t[2]=e.elements[2],t[3]=0,t[4]=e.elements[3],t[5]=e.elements[4],t[6]=e.elements[5],t[7]=0,t[8]=e.elements[6],t[9]=e.elements[7],t[10]=e.elements[8],t[11]=0):ArrayBuffer.isView(e)?t.set(new e.constructor(e.buffer,e.byteOffset,t.length)):e.toArray(t,n)}function h(e,t,n,r){let i=e.value,a=t+`_`+n;if(r[a]===void 0)return r[a]=typeof i==`number`||typeof i==`boolean`?i:ArrayBuffer.isView(i)?i.slice():i.clone(),!0;{let e=r[a];if(typeof i==`number`||typeof i==`boolean`){if(e!==i)return r[a]=i,!0}else if(ArrayBuffer.isView(i))return!0;else if(e.equals(i)===!1)return e.copy(i),!0}return!1}function g(e){let t=e.uniforms,n=0;for(let e=0,r=t.length;e<r;e++){let r=Array.isArray(t[e])?t[e]:[t[e]];for(let e=0,t=r.length;e<t;e++){let t=r[e],i=Array.isArray(t.value)?t.value:[t.value];for(let e=0,r=i.length;e<r;e++){let r=i[e],a=_(r),o=n%16,s=o%a.boundary,c=o+s;n+=s,c!==0&&16-c<a.storage&&(n+=16-c),t.__data=new Float32Array(a.storage/Float32Array.BYTES_PER_ELEMENT),t.__offset=n,n+=a.storage}}}let r=n%16;return r>0&&(n+=16-r),e.__size=n,e.__cache={},this}function _(e){let t={boundary:0,storage:0};return typeof e==`number`||typeof e==`boolean`?(t.boundary=4,t.storage=4):e.isVector2?(t.boundary=8,t.storage=8):e.isVector3||e.isColor?(t.boundary=16,t.storage=12):e.isVector4?(t.boundary=16,t.storage=16):e.isMatrix3?(t.boundary=48,t.storage=48):e.isMatrix4?(t.boundary=64,t.storage=64):e.isTexture?B(`WebGLRenderer: Texture samplers can not be part of an uniforms group.`):ArrayBuffer.isView(e)?(t.boundary=16,t.storage=e.byteLength):B(`WebGLRenderer: Unsupported uniform value type.`,e),t}function v(t){let n=t.target;n.removeEventListener(`dispose`,v);let r=o.indexOf(n.__bindingPointIndex);o.splice(r,1),e.deleteBuffer(i[n.id]),delete i[n.id],delete a[n.id]}function y(){for(let t in i)e.deleteBuffer(i[t]);o=[],i={},a={}}return{bind:c,update:l,dispose:y}}var Td=new Uint16Array([12469,15057,12620,14925,13266,14620,13807,14376,14323,13990,14545,13625,14713,13328,14840,12882,14931,12528,14996,12233,15039,11829,15066,11525,15080,11295,15085,10976,15082,10705,15073,10495,13880,14564,13898,14542,13977,14430,14158,14124,14393,13732,14556,13410,14702,12996,14814,12596,14891,12291,14937,11834,14957,11489,14958,11194,14943,10803,14921,10506,14893,10278,14858,9960,14484,14039,14487,14025,14499,13941,14524,13740,14574,13468,14654,13106,14743,12678,14818,12344,14867,11893,14889,11509,14893,11180,14881,10751,14852,10428,14812,10128,14765,9754,14712,9466,14764,13480,14764,13475,14766,13440,14766,13347,14769,13070,14786,12713,14816,12387,14844,11957,14860,11549,14868,11215,14855,10751,14825,10403,14782,10044,14729,9651,14666,9352,14599,9029,14967,12835,14966,12831,14963,12804,14954,12723,14936,12564,14917,12347,14900,11958,14886,11569,14878,11247,14859,10765,14828,10401,14784,10011,14727,9600,14660,9289,14586,8893,14508,8533,15111,12234,15110,12234,15104,12216,15092,12156,15067,12010,15028,11776,14981,11500,14942,11205,14902,10752,14861,10393,14812,9991,14752,9570,14682,9252,14603,8808,14519,8445,14431,8145,15209,11449,15208,11451,15202,11451,15190,11438,15163,11384,15117,11274,15055,10979,14994,10648,14932,10343,14871,9936,14803,9532,14729,9218,14645,8742,14556,8381,14461,8020,14365,7603,15273,10603,15272,10607,15267,10619,15256,10631,15231,10614,15182,10535,15118,10389,15042,10167,14963,9787,14883,9447,14800,9115,14710,8665,14615,8318,14514,7911,14411,7507,14279,7198,15314,9675,15313,9683,15309,9712,15298,9759,15277,9797,15229,9773,15166,9668,15084,9487,14995,9274,14898,8910,14800,8539,14697,8234,14590,7790,14479,7409,14367,7067,14178,6621,15337,8619,15337,8631,15333,8677,15325,8769,15305,8871,15264,8940,15202,8909,15119,8775,15022,8565,14916,8328,14804,8009,14688,7614,14569,7287,14448,6888,14321,6483,14088,6171,15350,7402,15350,7419,15347,7480,15340,7613,15322,7804,15287,7973,15229,8057,15148,8012,15046,7846,14933,7611,14810,7357,14682,7069,14552,6656,14421,6316,14251,5948,14007,5528,15356,5942,15356,5977,15353,6119,15348,6294,15332,6551,15302,6824,15249,7044,15171,7122,15070,7050,14949,6861,14818,6611,14679,6349,14538,6067,14398,5651,14189,5311,13935,4958,15359,4123,15359,4153,15356,4296,15353,4646,15338,5160,15311,5508,15263,5829,15188,6042,15088,6094,14966,6001,14826,5796,14678,5543,14527,5287,14377,4985,14133,4586,13869,4257,15360,1563,15360,1642,15358,2076,15354,2636,15341,3350,15317,4019,15273,4429,15203,4732,15105,4911,14981,4932,14836,4818,14679,4621,14517,4386,14359,4156,14083,3795,13808,3437,15360,122,15360,137,15358,285,15355,636,15344,1274,15322,2177,15281,2765,15215,3223,15120,3451,14995,3569,14846,3567,14681,3466,14511,3305,14344,3121,14037,2800,13753,2467,15360,0,15360,1,15359,21,15355,89,15346,253,15325,479,15287,796,15225,1148,15133,1492,15008,1749,14856,1882,14685,1886,14506,1783,14324,1608,13996,1398,13702,1183]),Ed=null;function Dd(){return Ed===null&&(Ed=new mi(Td,16,16,te,y),Ed.name=`DFG_LUT`,Ed.minFilter=l,Ed.magFilter=l,Ed.wrapS=i,Ed.wrapT=i,Ed.generateMipmaps=!1,Ed.needsUpdate=!0),Ed}var Od=class{constructor(e={}){let{canvas:t=Ze(),context:n=null,depth:r=!0,stencil:i=!1,alpha:a=!1,antialias:o=!1,premultipliedAlpha:s=!0,preserveDrawingBuffer:c=!1,powerPreference:l=`default`,failIfMajorPerformanceCaveat:u=!1,reversedDepthBuffer:p=!1,outputBufferType:m=f}=e;this.isWebGLRenderer=!0;let g;if(n!==null){if(typeof WebGLRenderingContext<`u`&&n instanceof WebGLRenderingContext)throw Error(`THREE.WebGLRenderer: WebGL 1 is not supported since r163.`);g=n.getContextAttributes().alpha}else g=a;let v=m,C=new Set([ne,j,ee]),w=new Set([f,_,h,S,b,x]),T=new Uint32Array(4),E=new Int32Array(4),D=new W,O=null,k=null,A=[],te=[],M=null;this.domElement=t,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this.toneMapping=0,this.toneMappingExposure=1,this.transmissionResolutionScale=1;let N=this,re=!1,ie=null,ae=null,oe=null,se=null;this._outputColorSpace=Ue;let ce=0,le=0,P=null,ue=-1,de=null,fe=new Jt,pe=new Jt,me=null,F=new J(0),he=0,ge=t.width,_e=t.height,ve=1,ye=null,be=null,xe=new Jt(0,0,ge,_e),Se=new Jt(0,0,ge,_e),Ce=!1,we=new Pi,Te=!1,Ee=!1,De=new q,Oe=new W,ke=new Jt,Ae={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0},je=!1;function Me(){return P===null?ve:1}let I=n;function Ne(e,n){return t.getContext(e,n)}try{let e={alpha:!0,depth:r,stencil:i,antialias:o,premultipliedAlpha:s,preserveDrawingBuffer:c,powerPreference:l,failIfMajorPerformanceCaveat:u};if(`setAttribute`in t&&t.setAttribute(`data-engine`,`three.js r185`),t.addEventListener(`webglcontextlost`,st,!1),t.addEventListener(`webglcontextrestored`,ct,!1),t.addEventListener(`webglcontextcreationerror`,lt,!1),I===null){let t=`webgl2`;if(I=Ne(t,e),I===null)throw Ne(t)?Error(`THREE.WebGLRenderer: Error creating WebGL context with your selected attributes.`):Error(`THREE.WebGLRenderer: Error creating WebGL context.`)}}catch(e){throw V(`WebGLRenderer: `+e.message),e}let Pe,Fe,L,Ie,Le,Re,ze,Be,Ve,He,We,Ge,Ke,qe,Je,z,Ye,Xe,Qe,et,tt,rt,it;function at(){Pe=new Kc(I),Pe.init(),tt=new gd(I,Pe),Fe=new Sc(I,Pe,e,tt),L=new md(I,Pe),Fe.reversedDepthBuffer&&p&&L.buffers.depth.setReversed(!0),ae=I.createFramebuffer(),oe=I.createFramebuffer(),se=I.createFramebuffer(),Ie=new Yc(I),Le=new Ju,Re=new hd(I,Pe,L,Le,Fe,tt,Ie),ze=new Gc(N),Be=new pc(I),rt=new bc(I,Be),Ve=new qc(I,Be,Ie,rt),He=new Zc(I,Ve,Be,rt,Ie),Xe=new Xc(I,Fe,Re),Je=new Cc(Le),We=new qu(N,ze,Pe,Fe,rt,Je),Ge=new Cd(N,Le),Ke=new Qu,qe=new ad(Pe),Ye=new yc(N,ze,L,He,g,s),z=new pd(N,He,Fe),it=new wd(I,Ie,Fe,L),Qe=new xc(I,Pe,Ie),et=new Jc(I,Pe,Ie),Ie.programs=We.programs,N.capabilities=Fe,N.extensions=Pe,N.properties=Le,N.renderLists=Ke,N.shadowMap=z,N.state=L,N.info=Ie}at(),v!==1009&&(M=new $c(v,t.width,t.height,o,r,i));let ot=new bd(N,I);this.xr=ot,this.getContext=function(){return I},this.getContextAttributes=function(){return I.getContextAttributes()},this.forceContextLoss=function(){let e=Pe.get(`WEBGL_lose_context`);e&&e.loseContext()},this.forceContextRestore=function(){let e=Pe.get(`WEBGL_lose_context`);e&&e.restoreContext()},this.getPixelRatio=function(){return ve},this.setPixelRatio=function(e){e!==void 0&&(ve=e,this.setSize(ge,_e,!1))},this.getSize=function(e){return e.set(ge,_e)},this.setSize=function(e,n,r=!0){if(ot.isPresenting){B(`WebGLRenderer: Can't change size while VR device is presenting.`);return}ge=e,_e=n,t.width=Math.floor(e*ve),t.height=Math.floor(n*ve),r===!0&&(t.style.width=e+`px`,t.style.height=n+`px`),M!==null&&M.setSize(t.width,t.height),this.setViewport(0,0,e,n)},this.getDrawingBufferSize=function(e){return e.set(ge*ve,_e*ve).floor()},this.setDrawingBufferSize=function(e,n,r){ge=e,_e=n,ve=r,t.width=Math.floor(e*r),t.height=Math.floor(n*r),this.setViewport(0,0,e,n)},this.setEffects=function(e){if(v===1009){V(`WebGLRenderer: setEffects() requires outputBufferType set to HalfFloatType or FloatType.`);return}if(e){for(let t=0;t<e.length;t++)if(e[t].isOutputPass===!0){B(`WebGLRenderer: OutputPass is not needed in setEffects(). Tone mapping and color space conversion are applied automatically.`);break}}M.setEffects(e||[])},this.getCurrentViewport=function(e){return e.copy(fe)},this.getViewport=function(e){return e.copy(xe)},this.setViewport=function(e,t,n,r){e.isVector4?xe.set(e.x,e.y,e.z,e.w):xe.set(e,t,n,r),L.viewport(fe.copy(xe).multiplyScalar(ve).round())},this.getScissor=function(e){return e.copy(Se)},this.setScissor=function(e,t,n,r){e.isVector4?Se.set(e.x,e.y,e.z,e.w):Se.set(e,t,n,r),L.scissor(pe.copy(Se).multiplyScalar(ve).round())},this.getScissorTest=function(){return Ce},this.setScissorTest=function(e){L.setScissorTest(Ce=e)},this.setOpaqueSort=function(e){ye=e},this.setTransparentSort=function(e){be=e},this.getClearColor=function(e){return e.copy(Ye.getClearColor())},this.setClearColor=function(){Ye.setClearColor(...arguments)},this.getClearAlpha=function(){return Ye.getClearAlpha()},this.setClearAlpha=function(){Ye.setClearAlpha(...arguments)},this.clear=function(e=!0,t=!0,n=!0){let r=0;if(e){let e=!1;if(P!==null){let t=P.texture.format;e=C.has(t)}if(e){let e=P.texture.type,t=w.has(e),n=Ye.getClearColor(),r=Ye.getClearAlpha(),i=n.r,a=n.g,o=n.b;t?(T[0]=i,T[1]=a,T[2]=o,T[3]=r,I.clearBufferuiv(I.COLOR,0,T)):(E[0]=i,E[1]=a,E[2]=o,E[3]=r,I.clearBufferiv(I.COLOR,0,E))}else r|=I.COLOR_BUFFER_BIT}t&&(r|=I.DEPTH_BUFFER_BIT,this.state.buffers.depth.setMask(!0)),n&&(r|=I.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),r!==0&&I.clear(r)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.setNodesHandler=function(e){e.setRenderer(this),ie=e},this.dispose=function(){t.removeEventListener(`webglcontextlost`,st,!1),t.removeEventListener(`webglcontextrestored`,ct,!1),t.removeEventListener(`webglcontextcreationerror`,lt,!1),Ye.dispose(),Ke.dispose(),qe.dispose(),Le.dispose(),ze.dispose(),He.dispose(),rt.dispose(),it.dispose(),We.dispose(),ot.dispose(),ot.removeEventListener(`sessionstart`,ht),ot.removeEventListener(`sessionend`,gt),_t.stop()};function st(e){e.preventDefault(),$e(`WebGLRenderer: Context Lost.`),re=!0}function ct(){$e(`WebGLRenderer: Context Restored.`),re=!1;let e=Ie.autoReset,t=z.enabled,n=z.autoUpdate,r=z.needsUpdate,i=z.type;at(),Ie.autoReset=e,z.enabled=t,z.autoUpdate=n,z.needsUpdate=r,z.type=i}function lt(e){V(`WebGLRenderer: A WebGL context could not be created. Reason: `,e.statusMessage)}function H(e){let t=e.target;t.removeEventListener(`dispose`,H),ut(t)}function ut(e){dt(e),Le.remove(e)}function dt(e){let t=Le.get(e).programs;t!==void 0&&(t.forEach(function(e){We.releaseProgram(e)}),e.isShaderMaterial&&We.releaseShaderCache(e))}this.renderBufferDirect=function(e,t,n,r,i,a){t===null&&(t=Ae);let o=i.isMesh&&i.matrixWorld.determinantAffine()<0,s=Dt(e,t,n,r,i);L.setMaterial(r,o);let c=n.index,l=1;if(r.wireframe===!0){if(c=Ve.getWireframeAttribute(n),c===void 0)return;l=2}let u=n.drawRange,d=n.attributes.position,f=u.start*l,p=(u.start+u.count)*l;a!==null&&(f=Math.max(f,a.start*l),p=Math.min(p,(a.start+a.count)*l)),c===null?d!=null&&(f=Math.max(f,0),p=Math.min(p,d.count)):(f=Math.max(f,0),p=Math.min(p,c.count));let m=p-f;if(m<0||m===1/0)return;rt.setup(i,r,s,n,c);let h,g=Qe;if(c!==null&&(h=Be.get(c),g=et,g.setIndex(h)),i.isMesh)r.wireframe===!0?(L.setLineWidth(r.wireframeLinewidth*Me()),g.setMode(I.LINES)):g.setMode(I.TRIANGLES);else if(i.isLine){let e=r.linewidth;e===void 0&&(e=1),L.setLineWidth(e*Me()),i.isLineSegments?g.setMode(I.LINES):i.isLineLoop?g.setMode(I.LINE_LOOP):g.setMode(I.LINE_STRIP)}else i.isPoints?g.setMode(I.POINTS):i.isSprite&&g.setMode(I.TRIANGLES);if(i.isBatchedMesh){if(Pe.get(`WEBGL_multi_draw`))g.renderMultiDraw(i._multiDrawStarts,i._multiDrawCounts,i._multiDrawCount);else{let e=i._multiDrawStarts,t=i._multiDrawCounts,n=i._multiDrawCount,a=c?Be.get(c).bytesPerElement:1,o=Le.get(r).currentProgram.getUniforms();for(let r=0;r<n;r++)o.setValue(I,`_gl_DrawID`,r),g.render(e[r]/a,t[r])}}else if(i.isInstancedMesh)g.renderInstances(f,m,i.count);else if(n.isInstancedBufferGeometry){let e=n._maxInstanceCount===void 0?1/0:n._maxInstanceCount,t=Math.min(n.instanceCount,e);g.renderInstances(f,m,t)}else g.render(f,m)};function ft(e,t,n){e.transparent===!0&&e.side===2&&e.forceSinglePass===!1?(e.side=1,e.needsUpdate=!0,Ct(e,t,n),e.side=0,e.needsUpdate=!0,Ct(e,t,n),e.side=2):Ct(e,t,n)}this.compile=function(e,t,n=null){n===null&&(n=e),k=qe.get(n),k.init(t),te.push(k),n.traverseVisible(function(e){e.isLight&&e.layers.test(t.layers)&&(k.pushLight(e),e.castShadow&&k.pushShadow(e))}),e!==n&&e.traverseVisible(function(e){e.isLight&&e.layers.test(t.layers)&&(k.pushLight(e),e.castShadow&&k.pushShadow(e))}),k.setupLights();let r=new Set;return e.traverse(function(e){if(!(e.isMesh||e.isPoints||e.isLine||e.isSprite))return;let t=e.material;if(t){if(Array.isArray(t))for(let i=0;i<t.length;i++){let a=t[i];ft(a,n,e),r.add(a)}else ft(t,n,e),r.add(t)}}),k=te.pop(),r},this.compileAsync=function(e,t,n=null){let r=this.compile(e,t,n);return new Promise(t=>{function n(){if(r.forEach(function(e){Le.get(e).currentProgram.isReady()&&r.delete(e)}),r.size===0){t(e);return}setTimeout(n,10)}Pe.get(`KHR_parallel_shader_compile`)===null?setTimeout(n,10):n()})};let pt=null;function mt(e){pt&&pt(e)}function ht(){_t.stop()}function gt(){_t.start()}let _t=new fc;_t.setAnimationLoop(mt),typeof self<`u`&&_t.setContext(self),this.setAnimationLoop=function(e){pt=e,ot.setAnimationLoop(e),e===null?_t.stop():_t.start()},ot.addEventListener(`sessionstart`,ht),ot.addEventListener(`sessionend`,gt),this.render=function(e,t){if(t!==void 0&&t.isCamera!==!0){V(`WebGLRenderer.render: camera is not an instance of THREE.Camera.`);return}if(re===!0)return;ie!==null&&ie.renderStart(e,t);let n=ot.enabled===!0&&ot.isPresenting===!0,r=M!==null&&(P===null||n)&&M.begin(N,P);if(e.matrixWorldAutoUpdate===!0&&e.updateMatrixWorld(),t.parent===null&&t.matrixWorldAutoUpdate===!0&&t.updateMatrixWorld(),ot.enabled===!0&&ot.isPresenting===!0&&(M===null||M.isCompositing()===!1)&&(ot.cameraAutoUpdate===!0&&ot.updateCamera(t),t=ot.getCamera()),e.isScene===!0&&e.onBeforeRender(N,e,t,P),k=qe.get(e,te.length),k.init(t),k.state.textureUnits=Re.getTextureUnits(),te.push(k),De.multiplyMatrices(t.projectionMatrix,t.matrixWorldInverse),we.setFromProjectionMatrix(De,R,t.reversedDepth),Ee=this.localClippingEnabled,Te=Je.init(this.clippingPlanes,Ee),O=Ke.get(e,A.length),O.init(),A.push(O),ot.enabled===!0&&ot.isPresenting===!0){let e=N.xr.getDepthSensingMesh();e!==null&&vt(e,t,-1/0,N.sortObjects)}vt(e,t,0,N.sortObjects),O.finish(),N.sortObjects===!0&&O.sort(ye,be,t.reversedDepth),je=ot.enabled===!1||ot.isPresenting===!1||ot.hasDepthSensing()===!1,je&&Ye.addToRenderList(O,e),this.info.render.frame++,this.info.autoReset===!0&&this.info.reset(),Te===!0&&Je.beginShadows();let i=k.state.shadowsArray;if(z.render(i,e,t),Te===!0&&Je.endShadows(),(r&&M.hasRenderPass())===!1){let n=O.opaque,r=O.transmissive;if(k.setupLights(),t.isArrayCamera){let i=t.cameras;if(r.length>0)for(let t=0,a=i.length;t<a;t++){let a=i[t];bt(n,r,e,a)}je&&Ye.render(e);for(let t=0,n=i.length;t<n;t++){let n=i[t];yt(O,e,n,n.viewport)}}else r.length>0&&bt(n,r,e,t),je&&Ye.render(e),yt(O,e,t)}P!==null&&le===0&&(Re.updateMultisampleRenderTarget(P),Re.updateRenderTargetMipmap(P)),r&&M.end(N),e.isScene===!0&&e.onAfterRender(N,e,t),rt.resetDefaultState(),ue=-1,de=null,te.pop(),te.length>0?(k=te[te.length-1],Re.setTextureUnits(k.state.textureUnits),Te===!0&&Je.setGlobalState(N.clippingPlanes,k.state.camera)):k=null,A.pop(),O=A.length>0?A[A.length-1]:null,ie!==null&&ie.renderEnd()};function vt(e,t,n,r){if(e.visible===!1)return;if(e.layers.test(t.layers)){if(e.isGroup)n=e.renderOrder;else if(e.isLOD)e.autoUpdate===!0&&e.update(t);else if(e.isLightProbeGrid)k.pushLightProbeGrid(e);else if(e.isLight)k.pushLight(e),e.castShadow&&k.pushShadow(e);else if(e.isSprite){if(!e.frustumCulled||we.intersectsSprite(e)){r&&ke.setFromMatrixPosition(e.matrixWorld).applyMatrix4(De);let t=He.update(e),i=e.material;i.visible&&O.push(e,t,i,n,ke.z,null)}}else if((e.isMesh||e.isLine||e.isPoints)&&(!e.frustumCulled||we.intersectsObject(e))){let t=He.update(e),i=e.material;if(r&&(e.boundingSphere===void 0?(t.boundingSphere===null&&t.computeBoundingSphere(),ke.copy(t.boundingSphere.center)):(e.boundingSphere===null&&e.computeBoundingSphere(),ke.copy(e.boundingSphere.center)),ke.applyMatrix4(e.matrixWorld).applyMatrix4(De)),Array.isArray(i)){let r=t.groups;for(let a=0,o=r.length;a<o;a++){let o=r[a],s=i[o.materialIndex];s&&s.visible&&O.push(e,t,s,n,ke.z,o)}}else i.visible&&O.push(e,t,i,n,ke.z,null)}}let i=e.children;for(let e=0,a=i.length;e<a;e++)vt(i[e],t,n,r)}function yt(e,t,n,r){let{opaque:i,transmissive:a,transparent:o}=e;k.setupLightsView(n),Te===!0&&Je.setGlobalState(N.clippingPlanes,n),r&&L.viewport(fe.copy(r)),i.length>0&&xt(i,t,n),a.length>0&&xt(a,t,n),o.length>0&&xt(o,t,n),L.buffers.depth.setTest(!0),L.buffers.depth.setMask(!0),L.buffers.color.setMask(!0),L.setPolygonOffset(!1)}function bt(e,t,n,r){if((n.isScene===!0?n.overrideMaterial:null)!==null)return;if(k.state.transmissionRenderTarget[r.id]===void 0){let e=Pe.has(`EXT_color_buffer_half_float`)||Pe.has(`EXT_color_buffer_float`);k.state.transmissionRenderTarget[r.id]=new Xt(1,1,{generateMipmaps:!0,type:e?y:f,minFilter:d,samples:Math.max(4,Fe.samples),stencilBuffer:i,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:K.workingColorSpace})}let a=k.state.transmissionRenderTarget[r.id],o=r.viewport||fe;a.setSize(o.z*N.transmissionResolutionScale,o.w*N.transmissionResolutionScale);let s=N.getRenderTarget(),c=N.getActiveCubeFace(),l=N.getActiveMipmapLevel();N.setRenderTarget(a),N.getClearColor(F),he=N.getClearAlpha(),he<1&&N.setClearColor(16777215,.5),N.clear(),je&&Ye.render(n);let u=N.toneMapping;N.toneMapping=0;let p=r.viewport;if(r.viewport!==void 0&&(r.viewport=void 0),k.setupLightsView(r),Te===!0&&Je.setGlobalState(N.clippingPlanes,r),xt(e,n,r),Re.updateMultisampleRenderTarget(a),Re.updateRenderTargetMipmap(a),Pe.has(`WEBGL_multisampled_render_to_texture`)===!1){let e=!1;for(let i=0,a=t.length;i<a;i++){let{object:a,geometry:o,material:s,group:c}=t[i];if(s.side===2&&a.layers.test(r.layers)){let t=s.side;s.side=1,s.needsUpdate=!0,St(a,n,r,o,s,c),s.side=t,s.needsUpdate=!0,e=!0}}e===!0&&(Re.updateMultisampleRenderTarget(a),Re.updateRenderTargetMipmap(a))}N.setRenderTarget(s,c,l),N.setClearColor(F,he),p!==void 0&&(r.viewport=p),N.toneMapping=u}function xt(e,t,n){let r=t.isScene===!0?t.overrideMaterial:null;for(let i=0,a=e.length;i<a;i++){let a=e[i],{object:o,geometry:s,group:c}=a,l=a.material;l.allowOverride===!0&&r!==null&&(l=r),o.layers.test(n.layers)&&St(o,t,n,s,l,c)}}function St(e,t,n,r,i,a){e.onBeforeRender(N,t,n,r,i,a),e.modelViewMatrix.multiplyMatrices(n.matrixWorldInverse,e.matrixWorld),e.normalMatrix.getNormalMatrix(e.modelViewMatrix),i.onBeforeRender(N,t,n,r,e,a),i.transparent===!0&&i.side===2&&i.forceSinglePass===!1?(i.side=1,i.needsUpdate=!0,N.renderBufferDirect(n,t,r,i,e,a),i.side=0,i.needsUpdate=!0,N.renderBufferDirect(n,t,r,i,e,a),i.side=2):N.renderBufferDirect(n,t,r,i,e,a),e.onAfterRender(N,t,n,r,i,a)}function Ct(e,t,n){t.isScene!==!0&&(t=Ae);let r=Le.get(e),i=k.state.lights,a=k.state.shadowsArray,o=i.state.version,s=We.getParameters(e,i.state,a,t,n,k.state.lightProbeGridArray),c=We.getProgramCacheKey(s),l=r.programs;r.environment=e.isMeshStandardMaterial||e.isMeshLambertMaterial||e.isMeshPhongMaterial?t.environment:null,r.fog=t.fog;let u=e.isMeshStandardMaterial||e.isMeshLambertMaterial&&!e.envMap||e.isMeshPhongMaterial&&!e.envMap;r.envMap=ze.get(e.envMap||r.environment,u),r.envMapRotation=r.environment!==null&&e.envMap===null?t.environmentRotation:e.envMapRotation,l===void 0&&(e.addEventListener(`dispose`,H),l=new Map,r.programs=l);let d=l.get(c);if(d!==void 0){if(r.currentProgram===d&&r.lightsStateVersion===o)return Tt(e,s),d}else s.uniforms=We.getUniforms(e),ie!==null&&e.isNodeMaterial&&ie.build(e,n,s),e.onBeforeCompile(s,N),d=We.acquireProgram(s,c),l.set(c,d),r.uniforms=s.uniforms;let f=r.uniforms;return(!e.isShaderMaterial&&!e.isRawShaderMaterial||e.clipping===!0)&&(f.clippingPlanes=Je.uniform),Tt(e,s),r.needsLights=kt(e),r.lightsStateVersion=o,r.needsLights&&(f.ambientLightColor.value=i.state.ambient,f.lightProbe.value=i.state.probe,f.directionalLights.value=i.state.directional,f.directionalLightShadows.value=i.state.directionalShadow,f.spotLights.value=i.state.spot,f.spotLightShadows.value=i.state.spotShadow,f.rectAreaLights.value=i.state.rectArea,f.ltc_1.value=i.state.rectAreaLTC1,f.ltc_2.value=i.state.rectAreaLTC2,f.pointLights.value=i.state.point,f.pointLightShadows.value=i.state.pointShadow,f.hemisphereLights.value=i.state.hemi,f.directionalShadowMatrix.value=i.state.directionalShadowMatrix,f.spotLightMatrix.value=i.state.spotLightMatrix,f.spotLightMap.value=i.state.spotLightMap,f.pointShadowMatrix.value=i.state.pointShadowMatrix),r.lightProbeGrid=k.state.lightProbeGridArray.length>0,r.currentProgram=d,r.uniformsList=null,d}function wt(e){if(e.uniformsList===null){let t=e.currentProgram.getUniforms();e.uniformsList=ou.seqWithValue(t.seq,e.uniforms)}return e.uniformsList}function Tt(e,t){let n=Le.get(e);n.outputColorSpace=t.outputColorSpace,n.batching=t.batching,n.batchingColor=t.batchingColor,n.instancing=t.instancing,n.instancingColor=t.instancingColor,n.instancingMorph=t.instancingMorph,n.skinning=t.skinning,n.morphTargets=t.morphTargets,n.morphNormals=t.morphNormals,n.morphColors=t.morphColors,n.morphTargetsCount=t.morphTargetsCount,n.numClippingPlanes=t.numClippingPlanes,n.numIntersection=t.numClipIntersection,n.vertexAlphas=t.vertexAlphas,n.vertexTangents=t.vertexTangents,n.toneMapping=t.toneMapping}function Et(e,t){if(e.length===0)return null;if(e.length===1)return e[0].texture===null?null:e[0];D.setFromMatrixPosition(t.matrixWorld);for(let t=0,n=e.length;t<n;t++){let n=e[t];if(n.texture!==null&&n.boundingBox.containsPoint(D))return n}return null}function Dt(e,t,n,r,i){t.isScene!==!0&&(t=Ae),Re.resetTextureUnits();let a=t.fog,o=r.isMeshStandardMaterial||r.isMeshLambertMaterial||r.isMeshPhongMaterial?t.environment:null,s=P===null?N.outputColorSpace:P.isXRRenderTarget===!0?P.texture.colorSpace:K.workingColorSpace,c=r.isMeshStandardMaterial||r.isMeshLambertMaterial&&!r.envMap||r.isMeshPhongMaterial&&!r.envMap,l=ze.get(r.envMap||o,c),u=r.vertexColors===!0&&!!n.attributes.color&&n.attributes.color.itemSize===4,d=!!n.attributes.tangent&&(!!r.normalMap||r.anisotropy>0),f=!!n.morphAttributes.position,p=!!n.morphAttributes.normal,m=!!n.morphAttributes.color,h=0;r.toneMapped&&(P===null||P.isXRRenderTarget===!0)&&(h=N.toneMapping);let g=n.morphAttributes.position||n.morphAttributes.normal||n.morphAttributes.color,_=g===void 0?0:g.length,v=Le.get(r),y=k.state.lights;if(Te===!0&&(Ee===!0||e!==de)){let t=e===de&&r.id===ue;Je.setState(r,e,t)}let b=!1;r.version===v.__version?v.needsLights&&v.lightsStateVersion!==y.state.version?b=!0:v.outputColorSpace===s?i.isBatchedMesh&&v.batching===!1||!i.isBatchedMesh&&v.batching===!0||i.isBatchedMesh&&v.batchingColor===!0&&i.colorTexture===null||i.isBatchedMesh&&v.batchingColor===!1&&i.colorTexture!==null||i.isInstancedMesh&&v.instancing===!1||!i.isInstancedMesh&&v.instancing===!0||i.isSkinnedMesh&&v.skinning===!1||!i.isSkinnedMesh&&v.skinning===!0||i.isInstancedMesh&&v.instancingColor===!0&&i.instanceColor===null||i.isInstancedMesh&&v.instancingColor===!1&&i.instanceColor!==null||i.isInstancedMesh&&v.instancingMorph===!0&&i.morphTexture===null||i.isInstancedMesh&&v.instancingMorph===!1&&i.morphTexture!==null?b=!0:v.envMap===l?r.fog===!0&&v.fog!==a||v.numClippingPlanes!==void 0&&(v.numClippingPlanes!==Je.numPlanes||v.numIntersection!==Je.numIntersection)?b=!0:v.vertexAlphas===u&&v.vertexTangents===d&&v.morphTargets===f&&v.morphNormals===p&&v.morphColors===m&&v.toneMapping===h&&v.morphTargetsCount===_?!!v.lightProbeGrid!=k.state.lightProbeGridArray.length>0&&(b=!0):b=!0:b=!0:b=!0:(b=!0,v.__version=r.version);let x=v.currentProgram;b===!0&&(x=Ct(r,t,i),ie&&r.isNodeMaterial&&ie.onUpdateProgram(r,x,v));let S=!1,C=!1,w=!1,T=x.getUniforms(),E=v.uniforms;if(L.useProgram(x.program)&&(S=!0,C=!0,w=!0),r.id!==ue&&(ue=r.id,C=!0),v.needsLights){let e=Et(k.state.lightProbeGridArray,i);v.lightProbeGrid!==e&&(v.lightProbeGrid=e,C=!0)}if(S||de!==e){L.buffers.depth.getReversed()&&e.reversedDepth!==!0&&(e._reversedDepth=!0,e.updateProjectionMatrix()),T.setValue(I,`projectionMatrix`,e.projectionMatrix),T.setValue(I,`viewMatrix`,e.matrixWorldInverse);let t=T.map.cameraPosition;t!==void 0&&t.setValue(I,Oe.setFromMatrixPosition(e.matrixWorld)),Fe.logarithmicDepthBuffer&&T.setValue(I,`logDepthBufFC`,2/(Math.log(e.far+1)/Math.LN2)),(r.isMeshPhongMaterial||r.isMeshToonMaterial||r.isMeshLambertMaterial||r.isMeshBasicMaterial||r.isMeshStandardMaterial||r.isShaderMaterial)&&T.setValue(I,`isOrthographic`,e.isOrthographicCamera===!0),de!==e&&(de=e,C=!0,w=!0)}if(v.needsLights&&(y.state.directionalShadowMap.length>0&&T.setValue(I,`directionalShadowMap`,y.state.directionalShadowMap,Re),y.state.spotShadowMap.length>0&&T.setValue(I,`spotShadowMap`,y.state.spotShadowMap,Re),y.state.pointShadowMap.length>0&&T.setValue(I,`pointShadowMap`,y.state.pointShadowMap,Re)),i.isSkinnedMesh){T.setOptional(I,i,`bindMatrix`),T.setOptional(I,i,`bindMatrixInverse`);let e=i.skeleton;e&&(e.boneTexture===null&&e.computeBoneTexture(),T.setValue(I,`boneTexture`,e.boneTexture,Re))}i.isBatchedMesh&&(T.setOptional(I,i,`batchingTexture`),T.setValue(I,`batchingTexture`,i._matricesTexture,Re),T.setOptional(I,i,`batchingIdTexture`),T.setValue(I,`batchingIdTexture`,i._indirectTexture,Re),T.setOptional(I,i,`batchingColorTexture`),i._colorsTexture!==null&&T.setValue(I,`batchingColorTexture`,i._colorsTexture,Re));let D=n.morphAttributes;if((D.position!==void 0||D.normal!==void 0||D.color!==void 0)&&Xe.update(i,n,x),(C||v.receiveShadow!==i.receiveShadow)&&(v.receiveShadow=i.receiveShadow,T.setValue(I,`receiveShadow`,i.receiveShadow)),(r.isMeshStandardMaterial||r.isMeshLambertMaterial||r.isMeshPhongMaterial)&&r.envMap===null&&t.environment!==null&&(E.envMapIntensity.value=t.environmentIntensity),E.dfgLUT!==void 0&&(E.dfgLUT.value=Dd()),C){if(T.setValue(I,`toneMappingExposure`,N.toneMappingExposure),v.needsLights&&Ot(E,w),a&&r.fog===!0&&Ge.refreshFogUniforms(E,a),Ge.refreshMaterialUniforms(E,r,ve,_e,k.state.transmissionRenderTarget[e.id]),v.needsLights&&v.lightProbeGrid){let e=v.lightProbeGrid;E.probesSH.value=e.texture,E.probesMin.value.copy(e.boundingBox.min),E.probesMax.value.copy(e.boundingBox.max),E.probesResolution.value.copy(e.resolution)}ou.upload(I,wt(v),E,Re)}if(r.isShaderMaterial&&r.uniformsNeedUpdate===!0&&(ou.upload(I,wt(v),E,Re),r.uniformsNeedUpdate=!1),r.isSpriteMaterial&&T.setValue(I,`center`,i.center),T.setValue(I,`modelViewMatrix`,i.modelViewMatrix),T.setValue(I,`normalMatrix`,i.normalMatrix),T.setValue(I,`modelMatrix`,i.matrixWorld),r.uniformsGroups!==void 0){let e=r.uniformsGroups;for(let t=0,n=e.length;t<n;t++){let n=e[t];it.update(n,x),it.bind(n,x)}}return x}function Ot(e,t){e.ambientLightColor.needsUpdate=t,e.lightProbe.needsUpdate=t,e.directionalLights.needsUpdate=t,e.directionalLightShadows.needsUpdate=t,e.pointLights.needsUpdate=t,e.pointLightShadows.needsUpdate=t,e.spotLights.needsUpdate=t,e.spotLightShadows.needsUpdate=t,e.rectAreaLights.needsUpdate=t,e.hemisphereLights.needsUpdate=t}function kt(e){return e.isMeshLambertMaterial||e.isMeshToonMaterial||e.isMeshPhongMaterial||e.isMeshStandardMaterial||e.isShadowMaterial||e.isShaderMaterial&&e.lights===!0}this.getActiveCubeFace=function(){return ce},this.getActiveMipmapLevel=function(){return le},this.getRenderTarget=function(){return P},this.setRenderTargetTextures=function(e,t,n){let r=Le.get(e);r.__autoAllocateDepthBuffer=e.resolveDepthBuffer===!1,r.__autoAllocateDepthBuffer===!1&&(r.__useRenderToTexture=!1),Le.get(e.texture).__webglTexture=t,Le.get(e.depthTexture).__webglTexture=r.__autoAllocateDepthBuffer?void 0:n,r.__hasExternalTextures=!0},this.setRenderTargetFramebuffer=function(e,t){let n=Le.get(e);n.__webglFramebuffer=t,n.__useDefaultFramebuffer=t===void 0},this.setRenderTarget=function(e,t=0,n=0){P=e,ce=t,le=n;let r=null,i=!1,a=!1;if(e){let o=Le.get(e);if(o.__useDefaultFramebuffer!==void 0){L.bindFramebuffer(I.FRAMEBUFFER,o.__webglFramebuffer),fe.copy(e.viewport),pe.copy(e.scissor),me=e.scissorTest,L.viewport(fe),L.scissor(pe),L.setScissorTest(me),ue=-1;return}if(o.__webglFramebuffer===void 0)Re.setupRenderTarget(e);else if(o.__hasExternalTextures)Re.rebindTextures(e,Le.get(e.texture).__webglTexture,Le.get(e.depthTexture).__webglTexture);else if(e.depthBuffer){let t=e.depthTexture;if(o.__boundDepthTexture!==t){if(t!==null&&Le.has(t)&&(e.width!==t.image.width||e.height!==t.image.height))throw Error(`THREE.WebGLRenderer: Attached DepthTexture is initialized to the incorrect size.`);Re.setupDepthRenderbuffer(e)}}let s=e.texture;(s.isData3DTexture||s.isDataArrayTexture||s.isCompressedArrayTexture)&&(a=!0);let c=Le.get(e).__webglFramebuffer;e.isWebGLCubeRenderTarget?(r=Array.isArray(c[t])?c[t][n]:c[t],i=!0):r=e.samples>0&&Re.useMultisampledRTT(e)===!1?Le.get(e).__webglMultisampledFramebuffer:Array.isArray(c)?c[n]:c,fe.copy(e.viewport),pe.copy(e.scissor),me=e.scissorTest}else fe.copy(xe).multiplyScalar(ve).floor(),pe.copy(Se).multiplyScalar(ve).floor(),me=Ce;if(n!==0&&(r=ae),L.bindFramebuffer(I.FRAMEBUFFER,r)&&L.drawBuffers(e,r),L.viewport(fe),L.scissor(pe),L.setScissorTest(me),i){let r=Le.get(e.texture);I.framebufferTexture2D(I.FRAMEBUFFER,I.COLOR_ATTACHMENT0,I.TEXTURE_CUBE_MAP_POSITIVE_X+t,r.__webglTexture,n)}else if(a){let r=t;for(let t=0;t<e.textures.length;t++){let i=Le.get(e.textures[t]);I.framebufferTextureLayer(I.FRAMEBUFFER,I.COLOR_ATTACHMENT0+t,i.__webglTexture,n,r)}}else if(e!==null&&n!==0){let t=Le.get(e.texture);I.framebufferTexture2D(I.FRAMEBUFFER,I.COLOR_ATTACHMENT0,I.TEXTURE_2D,t.__webglTexture,n)}ue=-1},this.readRenderTargetPixels=function(e,t,n,r,i,a,o,s=0){if(!(e&&e.isWebGLRenderTarget)){V(`WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.`);return}let c=Le.get(e).__webglFramebuffer;if(e.isWebGLCubeRenderTarget&&o!==void 0&&(c=c[o]),c){L.bindFramebuffer(I.FRAMEBUFFER,c);try{let o=e.textures[s],c=o.format,l=o.type;if(e.textures.length>1&&I.readBuffer(I.COLOR_ATTACHMENT0+s),!Fe.textureFormatReadable(c)){V(`WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.`);return}if(!Fe.textureTypeReadable(l)){V(`WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.`);return}t>=0&&t<=e.width-r&&n>=0&&n<=e.height-i&&I.readPixels(t,n,r,i,tt.convert(c),tt.convert(l),a)}finally{let e=P===null?null:Le.get(P).__webglFramebuffer;L.bindFramebuffer(I.FRAMEBUFFER,e)}}},this.readRenderTargetPixelsAsync=async function(e,t,n,r,i,a,o,s=0){if(!(e&&e.isWebGLRenderTarget))throw Error(`THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.`);let c=Le.get(e).__webglFramebuffer;if(e.isWebGLCubeRenderTarget&&o!==void 0&&(c=c[o]),c){if(t>=0&&t<=e.width-r&&n>=0&&n<=e.height-i){L.bindFramebuffer(I.FRAMEBUFFER,c);let o=e.textures[s],l=o.format,u=o.type;if(e.textures.length>1&&I.readBuffer(I.COLOR_ATTACHMENT0+s),!Fe.textureFormatReadable(l))throw Error(`THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.`);if(!Fe.textureTypeReadable(u))throw Error(`THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.`);let d=I.createBuffer();I.bindBuffer(I.PIXEL_PACK_BUFFER,d),I.bufferData(I.PIXEL_PACK_BUFFER,a.byteLength,I.STREAM_READ),I.readPixels(t,n,r,i,tt.convert(l),tt.convert(u),0);let f=P===null?null:Le.get(P).__webglFramebuffer;L.bindFramebuffer(I.FRAMEBUFFER,f);let p=I.fenceSync(I.SYNC_GPU_COMMANDS_COMPLETE,0);return I.flush(),await nt(I,p,4),I.bindBuffer(I.PIXEL_PACK_BUFFER,d),I.getBufferSubData(I.PIXEL_PACK_BUFFER,0,a),I.deleteBuffer(d),I.deleteSync(p),a}throw Error(`THREE.WebGLRenderer.readRenderTargetPixelsAsync: requested read bounds are out of range.`)}},this.copyFramebufferToTexture=function(e,t=null,n=0){let r=2**-n,i=Math.floor(e.image.width*r),a=Math.floor(e.image.height*r),o=t===null?0:t.x,s=t===null?0:t.y;Re.setTexture2D(e,0),I.copyTexSubImage2D(I.TEXTURE_2D,n,0,0,o,s,i,a),L.unbindTexture()},this.copyTextureToTexture=function(e,t,n=null,r=null,i=0,a=0){let o,s,c,l,u,d,f,p,m,h=e.isCompressedTexture?e.mipmaps[a]:e.image;if(n!==null)o=n.max.x-n.min.x,s=n.max.y-n.min.y,c=n.isBox3?n.max.z-n.min.z:1,l=n.min.x,u=n.min.y,d=n.isBox3?n.min.z:0;else{let t=2**-i;o=Math.floor(h.width*t),s=Math.floor(h.height*t),c=e.isDataArrayTexture?h.depth:e.isData3DTexture?Math.floor(h.depth*t):1,l=0,u=0,d=0}r===null?(f=0,p=0,m=0):(f=r.x,p=r.y,m=r.z);let g=tt.convert(t.format),_=tt.convert(t.type),v;t.isData3DTexture?(Re.setTexture3D(t,0),v=I.TEXTURE_3D):t.isDataArrayTexture||t.isCompressedArrayTexture?(Re.setTexture2DArray(t,0),v=I.TEXTURE_2D_ARRAY):(Re.setTexture2D(t,0),v=I.TEXTURE_2D),L.activeTexture(I.TEXTURE0),L.pixelStorei(I.UNPACK_FLIP_Y_WEBGL,t.flipY),L.pixelStorei(I.UNPACK_PREMULTIPLY_ALPHA_WEBGL,t.premultiplyAlpha),L.pixelStorei(I.UNPACK_ALIGNMENT,t.unpackAlignment);let y=L.getParameter(I.UNPACK_ROW_LENGTH),b=L.getParameter(I.UNPACK_IMAGE_HEIGHT),x=L.getParameter(I.UNPACK_SKIP_PIXELS),S=L.getParameter(I.UNPACK_SKIP_ROWS),C=L.getParameter(I.UNPACK_SKIP_IMAGES);L.pixelStorei(I.UNPACK_ROW_LENGTH,h.width),L.pixelStorei(I.UNPACK_IMAGE_HEIGHT,h.height),L.pixelStorei(I.UNPACK_SKIP_PIXELS,l),L.pixelStorei(I.UNPACK_SKIP_ROWS,u),L.pixelStorei(I.UNPACK_SKIP_IMAGES,d);let w=e.isDataArrayTexture||e.isData3DTexture,T=t.isDataArrayTexture||t.isData3DTexture;if(e.isDepthTexture){let n=Le.get(e),r=Le.get(t),h=Le.get(n.__renderTarget),g=Le.get(r.__renderTarget);L.bindFramebuffer(I.READ_FRAMEBUFFER,h.__webglFramebuffer),L.bindFramebuffer(I.DRAW_FRAMEBUFFER,g.__webglFramebuffer);for(let n=0;n<c;n++)w&&(I.framebufferTextureLayer(I.READ_FRAMEBUFFER,I.COLOR_ATTACHMENT0,Le.get(e).__webglTexture,i,d+n),I.framebufferTextureLayer(I.DRAW_FRAMEBUFFER,I.COLOR_ATTACHMENT0,Le.get(t).__webglTexture,a,m+n)),I.blitFramebuffer(l,u,o,s,f,p,o,s,I.DEPTH_BUFFER_BIT,I.NEAREST);L.bindFramebuffer(I.READ_FRAMEBUFFER,null),L.bindFramebuffer(I.DRAW_FRAMEBUFFER,null)}else if(i!==0||e.isRenderTargetTexture||Le.has(e)){let n=Le.get(e),r=Le.get(t);L.bindFramebuffer(I.READ_FRAMEBUFFER,oe),L.bindFramebuffer(I.DRAW_FRAMEBUFFER,se);for(let e=0;e<c;e++)w?I.framebufferTextureLayer(I.READ_FRAMEBUFFER,I.COLOR_ATTACHMENT0,n.__webglTexture,i,d+e):I.framebufferTexture2D(I.READ_FRAMEBUFFER,I.COLOR_ATTACHMENT0,I.TEXTURE_2D,n.__webglTexture,i),T?I.framebufferTextureLayer(I.DRAW_FRAMEBUFFER,I.COLOR_ATTACHMENT0,r.__webglTexture,a,m+e):I.framebufferTexture2D(I.DRAW_FRAMEBUFFER,I.COLOR_ATTACHMENT0,I.TEXTURE_2D,r.__webglTexture,a),i===0?T?I.copyTexSubImage3D(v,a,f,p,m+e,l,u,o,s):I.copyTexSubImage2D(v,a,f,p,l,u,o,s):I.blitFramebuffer(l,u,o,s,f,p,o,s,I.COLOR_BUFFER_BIT,I.NEAREST);L.bindFramebuffer(I.READ_FRAMEBUFFER,null),L.bindFramebuffer(I.DRAW_FRAMEBUFFER,null)}else T?e.isDataTexture||e.isData3DTexture?I.texSubImage3D(v,a,f,p,m,o,s,c,g,_,h.data):t.isCompressedArrayTexture?I.compressedTexSubImage3D(v,a,f,p,m,o,s,c,g,h.data):I.texSubImage3D(v,a,f,p,m,o,s,c,g,_,h):e.isDataTexture?I.texSubImage2D(I.TEXTURE_2D,a,f,p,o,s,g,_,h.data):e.isCompressedTexture?I.compressedTexSubImage2D(I.TEXTURE_2D,a,f,p,h.width,h.height,g,h.data):I.texSubImage2D(I.TEXTURE_2D,a,f,p,o,s,g,_,h);L.pixelStorei(I.UNPACK_ROW_LENGTH,y),L.pixelStorei(I.UNPACK_IMAGE_HEIGHT,b),L.pixelStorei(I.UNPACK_SKIP_PIXELS,x),L.pixelStorei(I.UNPACK_SKIP_ROWS,S),L.pixelStorei(I.UNPACK_SKIP_IMAGES,C),a===0&&t.generateMipmaps&&I.generateMipmap(v),L.unbindTexture()},this.initRenderTarget=function(e){Le.get(e).__webglFramebuffer===void 0&&Re.setupRenderTarget(e)},this.initTexture=function(e){e.isCubeTexture?Re.setTextureCube(e,0):e.isData3DTexture?Re.setTexture3D(e,0):e.isDataArrayTexture||e.isCompressedArrayTexture?Re.setTexture2DArray(e,0):Re.setTexture2D(e,0),L.unbindTexture()},this.resetState=function(){ce=0,le=0,P=null,L.reset(),rt.reset()},typeof __THREE_DEVTOOLS__<`u`&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent(`observe`,{detail:this}))}get coordinateSystem(){return R}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(e){this._outputColorSpace=e;let t=this.getContext();t.drawingBufferColorSpace=K._getDrawingBufferColorSpace(e),t.unpackColorSpace=K._getUnpackColorSpace()}};function kd(e,t=!1){let n=e[0].index!==null,r=new Set(Object.keys(e[0].attributes)),i=new Set(Object.keys(e[0].morphAttributes)),a={},o={},s=e[0].morphTargetsRelative,c=new Or,l=0;for(let u=0;u<e.length;++u){let d=e[u],f=0;if(n!==(d.index!==null))return console.error(`THREE.BufferGeometryUtils: .mergeGeometries() failed with geometry at index `+u+`. All geometries must have compatible attributes; make sure index attribute exists among all geometries, or in none of them.`),null;for(let e in d.attributes){if(!r.has(e))return console.error(`THREE.BufferGeometryUtils: .mergeGeometries() failed with geometry at index `+u+`. All geometries must have compatible attributes; make sure "`+e+`" attribute exists among all geometries, or in none of them.`),null;a[e]===void 0&&(a[e]=[]),a[e].push(d.attributes[e]),f++}if(f!==r.size)return console.error(`THREE.BufferGeometryUtils: .mergeGeometries() failed with geometry at index `+u+`. Make sure all geometries have the same number of attributes.`),null;if(s!==d.morphTargetsRelative)return console.error(`THREE.BufferGeometryUtils: .mergeGeometries() failed with geometry at index `+u+`. .morphTargetsRelative must be consistent throughout all geometries.`),null;for(let e in d.morphAttributes){if(!i.has(e))return console.error(`THREE.BufferGeometryUtils: .mergeGeometries() failed with geometry at index `+u+`.  .morphAttributes must be consistent throughout all geometries.`),null;o[e]===void 0&&(o[e]=[]),o[e].push(d.morphAttributes[e])}if(t){let e;if(n)e=d.index.count;else if(d.attributes.position!==void 0)e=d.attributes.position.count;else return console.error(`THREE.BufferGeometryUtils: .mergeGeometries() failed with geometry at index `+u+`. The geometry must have either an index or a position attribute`),null;c.addGroup(l,e,u),l+=e}}if(n){let t=0,n=[];for(let r=0;r<e.length;++r){let i=e[r].index;for(let e=0;e<i.count;++e)n.push(i.getX(e)+t);t+=e[r].attributes.position.count}c.setIndex(n)}for(let e in a){let t=Ad(a[e]);if(!t)return console.error(`THREE.BufferGeometryUtils: .mergeGeometries() failed while trying to merge the `+e+` attribute.`),null;c.setAttribute(e,t)}for(let e in o){let t=o[e][0].length;if(t!==0){c.morphAttributes=c.morphAttributes||{},c.morphAttributes[e]=[];for(let n=0;n<t;++n){let t=[];for(let r=0;r<o[e].length;++r)t.push(o[e][r][n]);let r=Ad(t);if(!r)return console.error(`THREE.BufferGeometryUtils: .mergeGeometries() failed while trying to merge the `+e+` morphAttribute.`),null;c.morphAttributes[e].push(r)}}}return c}function Ad(e){let t,n,r,i=-1,a=0;for(let o=0;o<e.length;++o){let s=e[o];if(t===void 0&&(t=s.array.constructor),t!==s.array.constructor)return console.error(`THREE.BufferGeometryUtils: .mergeAttributes() failed. BufferAttribute.array must be of consistent array types across matching attributes.`),null;if(n===void 0&&(n=s.itemSize),n!==s.itemSize)return console.error(`THREE.BufferGeometryUtils: .mergeAttributes() failed. BufferAttribute.itemSize must be consistent across matching attributes.`),null;if(r===void 0&&(r=s.normalized),r!==s.normalized)return console.error(`THREE.BufferGeometryUtils: .mergeAttributes() failed. BufferAttribute.normalized must be consistent across matching attributes.`),null;if(i===-1&&(i=s.gpuType),i!==s.gpuType)return console.error(`THREE.BufferGeometryUtils: .mergeAttributes() failed. BufferAttribute.gpuType must be consistent across matching attributes.`),null;a+=s.count*n}let o=new t(a),s=new mr(o,n,r),c=0;for(let t=0;t<e.length;++t){let r=e[t];if(r.isInterleavedBufferAttribute){let e=c/n;for(let t=0,i=r.count;t<i;t++)for(let i=0;i<n;i++){let n=r.getComponent(t,i);s.setComponent(t+e,i,n)}}else o.set(r.array,c);c+=r.count*n}return i!==void 0&&(s.gpuType=i),s}function jd(e,t){if(t===0)return console.warn(`THREE.BufferGeometryUtils.toTrianglesDrawMode(): Geometry already defined as triangles.`),e;if(t===2||t===1){let n=e.getIndex();if(n===null){let t=[],r=e.getAttribute(`position`);if(r!==void 0){for(let e=0;e<r.count;e++)t.push(e);e.setIndex(t),n=e.getIndex()}else return console.error(`THREE.BufferGeometryUtils.toTrianglesDrawMode(): Undefined position attribute. Processing not possible.`),e}let r=n.count-2,i=[];if(t===2)for(let e=1;e<=r;e++)i.push(n.getX(0)),i.push(n.getX(e)),i.push(n.getX(e+1));else for(let e=0;e<r;e++)e%2==0?(i.push(n.getX(e)),i.push(n.getX(e+1)),i.push(n.getX(e+2))):(i.push(n.getX(e+2)),i.push(n.getX(e+1)),i.push(n.getX(e)));i.length/3!==r&&console.error(`THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unable to generate correct amount of triangles.`);let a=e.clone();return a.setIndex(i),a.clearGroups(),a}return console.error(`THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unknown draw mode:`,t),e}function Md(e){let t=new Map,n=new Map,r=e.clone();return Nd(e,r,function(e,r){t.set(r,e),n.set(e,r)}),r.traverse(function(e){if(!e.isSkinnedMesh)return;let r=e,i=t.get(e),a=i.skeleton.bones;r.skeleton=i.skeleton.clone(),r.bindMatrix.copy(i.bindMatrix),r.skeleton.bones=a.map(function(e){return n.get(e)}),r.bind(r.skeleton,r.bindMatrix)}),r}function Nd(e,t,n){n(e,t);for(let r=0;r<e.children.length;r++)Nd(e.children[r],t.children[r],n)}var Pd=class extends fs{constructor(e){super(e),this.dracoLoader=null,this.ktx2Loader=null,this.meshoptDecoder=null,this.pluginCallbacks=[],this.register(function(e){return new Vd(e)}),this.register(function(e){return new Hd(e)}),this.register(function(e){return new Zd(e)}),this.register(function(e){return new Qd(e)}),this.register(function(e){return new $d(e)}),this.register(function(e){return new Wd(e)}),this.register(function(e){return new Gd(e)}),this.register(function(e){return new Kd(e)}),this.register(function(e){return new qd(e)}),this.register(function(e){return new Bd(e)}),this.register(function(e){return new Jd(e)}),this.register(function(e){return new Ud(e)}),this.register(function(e){return new Xd(e)}),this.register(function(e){return new Yd(e)}),this.register(function(e){return new Rd(e)}),this.register(function(e){return new ef(e,Ld.EXT_MESHOPT_COMPRESSION)}),this.register(function(e){return new ef(e,Ld.KHR_MESHOPT_COMPRESSION)}),this.register(function(e){return new tf(e)})}load(e,t,n,r){let i=this,a;if(this.resourcePath!==``)a=this.resourcePath;else if(this.path!==``){let t=zs.extractUrlBase(e);a=zs.resolveURL(t,this.path)}else a=zs.extractUrlBase(e);this.manager.itemStart(e);let o=function(t){r?r(t):console.error(t),i.manager.itemError(e),i.manager.itemEnd(e)},s=new hs(this.manager);s.setPath(this.path),s.setResponseType(`arraybuffer`),s.setRequestHeader(this.requestHeader),s.setWithCredentials(this.withCredentials),s.load(e,function(n){try{i.parse(n,a,function(n){t(n),i.manager.itemEnd(e)},o)}catch(e){o(e)}},n,o)}setDRACOLoader(e){return this.dracoLoader=e,this}setKTX2Loader(e){return this.ktx2Loader=e,this}setMeshoptDecoder(e){return this.meshoptDecoder=e,this}register(e){return this.pluginCallbacks.indexOf(e)===-1&&this.pluginCallbacks.push(e),this}unregister(e){return this.pluginCallbacks.indexOf(e)!==-1&&this.pluginCallbacks.splice(this.pluginCallbacks.indexOf(e),1),this}parse(e,t,n,r){let i,a={},o={},s=new TextDecoder;if(typeof e==`string`)i=JSON.parse(e);else if(e instanceof ArrayBuffer){if(s.decode(new Uint8Array(e,0,4))===nf){try{a[Ld.KHR_BINARY_GLTF]=new of(e)}catch(e){r&&r(e);return}i=JSON.parse(a[Ld.KHR_BINARY_GLTF].content)}else i=JSON.parse(s.decode(e))}else i=e;if(i.asset===void 0||i.asset.version[0]<2){r&&r(Error(`THREE.GLTFLoader: Unsupported asset. glTF versions >=2.0 are supported.`));return}let c=new Mf(i,{path:t||this.resourcePath||``,crossOrigin:this.crossOrigin,requestHeader:this.requestHeader,manager:this.manager,ktx2Loader:this.ktx2Loader,meshoptDecoder:this.meshoptDecoder});c.fileLoader.setRequestHeader(this.requestHeader);for(let e=0;e<this.pluginCallbacks.length;e++){let t=this.pluginCallbacks[e](c);t.name||console.error(`THREE.GLTFLoader: Invalid plugin found: missing name`),o[t.name]=t,a[t.name]=!0}if(i.extensionsUsed)for(let e=0;e<i.extensionsUsed.length;++e){let t=i.extensionsUsed[e],n=i.extensionsRequired||[];switch(t){case Ld.KHR_MATERIALS_UNLIT:a[t]=new zd;break;case Ld.KHR_DRACO_MESH_COMPRESSION:a[t]=new sf(i,this.dracoLoader);break;case Ld.KHR_TEXTURE_TRANSFORM:a[t]=new cf;break;case Ld.KHR_MESH_QUANTIZATION:a[t]=new lf;break;default:n.indexOf(t)>=0&&o[t]===void 0&&console.warn(`THREE.GLTFLoader: Unknown extension "`+t+`".`)}}c.setExtensions(a),c.setPlugins(o),c.parse(n,r)}parseAsync(e,t){let n=this;return new Promise(function(r,i){n.parse(e,t,r,i)})}};function Fd(){let e={};return{get:function(t){return e[t]},add:function(t,n){e[t]=n},remove:function(t){delete e[t]},removeAll:function(){e={}}}}function Id(e,t,n){let r=e.json.materials[t];return r.extensions&&r.extensions[n]?r.extensions[n]:null}var Ld={KHR_BINARY_GLTF:`KHR_binary_glTF`,KHR_DRACO_MESH_COMPRESSION:`KHR_draco_mesh_compression`,KHR_LIGHTS_PUNCTUAL:`KHR_lights_punctual`,KHR_MATERIALS_CLEARCOAT:`KHR_materials_clearcoat`,KHR_MATERIALS_DISPERSION:`KHR_materials_dispersion`,KHR_MATERIALS_IOR:`KHR_materials_ior`,KHR_MATERIALS_SHEEN:`KHR_materials_sheen`,KHR_MATERIALS_SPECULAR:`KHR_materials_specular`,KHR_MATERIALS_TRANSMISSION:`KHR_materials_transmission`,KHR_MATERIALS_IRIDESCENCE:`KHR_materials_iridescence`,KHR_MATERIALS_ANISOTROPY:`KHR_materials_anisotropy`,KHR_MATERIALS_UNLIT:`KHR_materials_unlit`,KHR_MATERIALS_VOLUME:`KHR_materials_volume`,KHR_TEXTURE_BASISU:`KHR_texture_basisu`,KHR_TEXTURE_TRANSFORM:`KHR_texture_transform`,KHR_MESH_QUANTIZATION:`KHR_mesh_quantization`,KHR_MATERIALS_EMISSIVE_STRENGTH:`KHR_materials_emissive_strength`,EXT_MATERIALS_BUMP:`EXT_materials_bump`,EXT_TEXTURE_WEBP:`EXT_texture_webp`,EXT_TEXTURE_AVIF:`EXT_texture_avif`,EXT_MESHOPT_COMPRESSION:`EXT_meshopt_compression`,KHR_MESHOPT_COMPRESSION:`KHR_meshopt_compression`,EXT_MESH_GPU_INSTANCING:`EXT_mesh_gpu_instancing`},Rd=class{constructor(e){this.parser=e,this.name=Ld.KHR_LIGHTS_PUNCTUAL,this.cache={refs:{},uses:{}}}_markDefs(){let e=this.parser,t=this.parser.json.nodes||[];for(let n=0,r=t.length;n<r;n++){let r=t[n];r.extensions&&r.extensions[this.name]&&r.extensions[this.name].light!==void 0&&e._addNodeRef(this.cache,r.extensions[this.name].light)}}_loadLight(e){let t=this.parser,n=`light:`+e,r=t.cache.get(n);if(r)return r;let i=t.json,a=((i.extensions&&i.extensions[this.name]||{}).lights||[])[e],o,s=new J(16777215);a.color!==void 0&&s.setRGB(a.color[0],a.color[1],a.color[2],We);let c=a.range===void 0?0:a.range;switch(a.type){case`directional`:o=new Rs(s),o.target.position.set(0,0,-1),o.add(o.target);break;case`point`:o=new Fs(s),o.distance=c;break;case`spot`:o=new Ns(s),o.distance=c,a.spot=a.spot||{},a.spot.innerConeAngle=a.spot.innerConeAngle===void 0?0:a.spot.innerConeAngle,a.spot.outerConeAngle=a.spot.outerConeAngle===void 0?Math.PI/4:a.spot.outerConeAngle,o.angle=a.spot.outerConeAngle,o.penumbra=1-a.spot.innerConeAngle/a.spot.outerConeAngle,o.target.position.set(0,0,-1),o.add(o.target);break;default:throw Error(`THREE.GLTFLoader: Unexpected light type: `+a.type)}return o.position.set(0,0,0),wf(o,a),a.intensity!==void 0&&(o.intensity=a.intensity),o.name=t.createUniqueName(a.name||`light_`+e),r=Promise.resolve(o),t.cache.add(n,r),r}getDependency(e,t){if(e===`light`)return this._loadLight(t)}createNodeAttachment(e){let t=this,n=this.parser,r=n.json.nodes[e],i=(r.extensions&&r.extensions[this.name]||{}).light;return i===void 0?null:this._loadLight(i).then(function(e){return n._getNodeRef(t.cache,i,e)})}},zd=class{constructor(){this.name=Ld.KHR_MATERIALS_UNLIT}getMaterialType(){return Hr}extendParams(e,t,n){let r=[];e.color=new J(1,1,1),e.opacity=1;let i=t.pbrMetallicRoughness;if(i){if(Array.isArray(i.baseColorFactor)){let t=i.baseColorFactor;e.color.setRGB(t[0],t[1],t[2],We),e.opacity=t[3]}i.baseColorTexture!==void 0&&r.push(n.assignTexture(e,`map`,i.baseColorTexture,Ue))}return Promise.all(r)}},Bd=class{constructor(e){this.parser=e,this.name=Ld.KHR_MATERIALS_EMISSIVE_STRENGTH}extendMaterialParams(e,t){let n=Id(this.parser,e,this.name);return n===null||n.emissiveStrength!==void 0&&(t.emissiveIntensity=n.emissiveStrength),Promise.resolve()}},Vd=class{constructor(e){this.parser=e,this.name=Ld.KHR_MATERIALS_CLEARCOAT}getMaterialType(e){return Id(this.parser,e,this.name)===null?null:Bo}extendMaterialParams(e,t){let n=Id(this.parser,e,this.name);if(n===null)return Promise.resolve();let r=[];if(n.clearcoatFactor!==void 0&&(t.clearcoat=n.clearcoatFactor),n.clearcoatTexture!==void 0&&r.push(this.parser.assignTexture(t,`clearcoatMap`,n.clearcoatTexture)),n.clearcoatRoughnessFactor!==void 0&&(t.clearcoatRoughness=n.clearcoatRoughnessFactor),n.clearcoatRoughnessTexture!==void 0&&r.push(this.parser.assignTexture(t,`clearcoatRoughnessMap`,n.clearcoatRoughnessTexture)),n.clearcoatNormalTexture!==void 0&&(r.push(this.parser.assignTexture(t,`clearcoatNormalMap`,n.clearcoatNormalTexture)),n.clearcoatNormalTexture.scale!==void 0)){let e=n.clearcoatNormalTexture.scale;t.clearcoatNormalScale=new U(e,e)}return Promise.all(r)}},Hd=class{constructor(e){this.parser=e,this.name=Ld.KHR_MATERIALS_DISPERSION}getMaterialType(e){return Id(this.parser,e,this.name)===null?null:Bo}extendMaterialParams(e,t){let n=Id(this.parser,e,this.name);return n===null||(t.dispersion=n.dispersion===void 0?0:n.dispersion),Promise.resolve()}},Ud=class{constructor(e){this.parser=e,this.name=Ld.KHR_MATERIALS_IRIDESCENCE}getMaterialType(e){return Id(this.parser,e,this.name)===null?null:Bo}extendMaterialParams(e,t){let n=Id(this.parser,e,this.name);if(n===null)return Promise.resolve();let r=[];return n.iridescenceFactor!==void 0&&(t.iridescence=n.iridescenceFactor),n.iridescenceTexture!==void 0&&r.push(this.parser.assignTexture(t,`iridescenceMap`,n.iridescenceTexture)),n.iridescenceIor!==void 0&&(t.iridescenceIOR=n.iridescenceIor),t.iridescenceThicknessRange===void 0&&(t.iridescenceThicknessRange=[100,400]),n.iridescenceThicknessMinimum!==void 0&&(t.iridescenceThicknessRange[0]=n.iridescenceThicknessMinimum),n.iridescenceThicknessMaximum!==void 0&&(t.iridescenceThicknessRange[1]=n.iridescenceThicknessMaximum),n.iridescenceThicknessTexture!==void 0&&r.push(this.parser.assignTexture(t,`iridescenceThicknessMap`,n.iridescenceThicknessTexture)),Promise.all(r)}},Wd=class{constructor(e){this.parser=e,this.name=Ld.KHR_MATERIALS_SHEEN}getMaterialType(e){return Id(this.parser,e,this.name)===null?null:Bo}extendMaterialParams(e,t){let n=Id(this.parser,e,this.name);if(n===null)return Promise.resolve();let r=[];if(t.sheenColor=new J(0,0,0),t.sheenRoughness=0,t.sheen=1,n.sheenColorFactor!==void 0){let e=n.sheenColorFactor;t.sheenColor.setRGB(e[0],e[1],e[2],We)}return n.sheenRoughnessFactor!==void 0&&(t.sheenRoughness=n.sheenRoughnessFactor),n.sheenColorTexture!==void 0&&r.push(this.parser.assignTexture(t,`sheenColorMap`,n.sheenColorTexture,Ue)),n.sheenRoughnessTexture!==void 0&&r.push(this.parser.assignTexture(t,`sheenRoughnessMap`,n.sheenRoughnessTexture)),Promise.all(r)}},Gd=class{constructor(e){this.parser=e,this.name=Ld.KHR_MATERIALS_TRANSMISSION}getMaterialType(e){return Id(this.parser,e,this.name)===null?null:Bo}extendMaterialParams(e,t){let n=Id(this.parser,e,this.name);if(n===null)return Promise.resolve();let r=[];return n.transmissionFactor!==void 0&&(t.transmission=n.transmissionFactor),n.transmissionTexture!==void 0&&r.push(this.parser.assignTexture(t,`transmissionMap`,n.transmissionTexture)),Promise.all(r)}},Kd=class{constructor(e){this.parser=e,this.name=Ld.KHR_MATERIALS_VOLUME}getMaterialType(e){return Id(this.parser,e,this.name)===null?null:Bo}extendMaterialParams(e,t){let n=Id(this.parser,e,this.name);if(n===null)return Promise.resolve();let r=[];t.thickness=n.thicknessFactor===void 0?0:n.thicknessFactor,n.thicknessTexture!==void 0&&r.push(this.parser.assignTexture(t,`thicknessMap`,n.thicknessTexture)),t.attenuationDistance=n.attenuationDistance||1/0;let i=n.attenuationColor||[1,1,1];return t.attenuationColor=new J().setRGB(i[0],i[1],i[2],We),Promise.all(r)}},qd=class{constructor(e){this.parser=e,this.name=Ld.KHR_MATERIALS_IOR}getMaterialType(e){return Id(this.parser,e,this.name)===null?null:Bo}extendMaterialParams(e,t){let n=Id(this.parser,e,this.name);return n===null?Promise.resolve():(t.ior=n.ior===void 0?1.5:n.ior,t.ior===0&&(t.ior=1e3),Promise.resolve())}},Jd=class{constructor(e){this.parser=e,this.name=Ld.KHR_MATERIALS_SPECULAR}getMaterialType(e){return Id(this.parser,e,this.name)===null?null:Bo}extendMaterialParams(e,t){let n=Id(this.parser,e,this.name);if(n===null)return Promise.resolve();let r=[];t.specularIntensity=n.specularFactor===void 0?1:n.specularFactor,n.specularTexture!==void 0&&r.push(this.parser.assignTexture(t,`specularIntensityMap`,n.specularTexture));let i=n.specularColorFactor||[1,1,1];return t.specularColor=new J().setRGB(i[0],i[1],i[2],We),n.specularColorTexture!==void 0&&r.push(this.parser.assignTexture(t,`specularColorMap`,n.specularColorTexture,Ue)),Promise.all(r)}},Yd=class{constructor(e){this.parser=e,this.name=Ld.EXT_MATERIALS_BUMP}getMaterialType(e){return Id(this.parser,e,this.name)===null?null:Bo}extendMaterialParams(e,t){let n=Id(this.parser,e,this.name);if(n===null)return Promise.resolve();let r=[];return t.bumpScale=n.bumpFactor===void 0?1:n.bumpFactor,n.bumpTexture!==void 0&&r.push(this.parser.assignTexture(t,`bumpMap`,n.bumpTexture)),Promise.all(r)}},Xd=class{constructor(e){this.parser=e,this.name=Ld.KHR_MATERIALS_ANISOTROPY}getMaterialType(e){return Id(this.parser,e,this.name)===null?null:Bo}extendMaterialParams(e,t){let n=Id(this.parser,e,this.name);if(n===null)return Promise.resolve();let r=[];return n.anisotropyStrength!==void 0&&(t.anisotropy=n.anisotropyStrength),n.anisotropyRotation!==void 0&&(t.anisotropyRotation=n.anisotropyRotation),n.anisotropyTexture!==void 0&&r.push(this.parser.assignTexture(t,`anisotropyMap`,n.anisotropyTexture)),Promise.all(r)}},Zd=class{constructor(e){this.parser=e,this.name=Ld.KHR_TEXTURE_BASISU}loadTexture(e){let t=this.parser,n=t.json,r=n.textures[e];if(!r.extensions||!r.extensions[this.name])return null;let i=r.extensions[this.name],a=t.options.ktx2Loader;if(!a){if(n.extensionsRequired&&n.extensionsRequired.indexOf(this.name)>=0)throw Error(`THREE.GLTFLoader: setKTX2Loader must be called before loading KTX2 textures`);return null}return t.loadTextureImage(e,i.source,a)}},Qd=class{constructor(e){this.parser=e,this.name=Ld.EXT_TEXTURE_WEBP}loadTexture(e){let t=this.name,n=this.parser,r=n.json,i=r.textures[e];if(!i.extensions||!i.extensions[t])return null;let a=i.extensions[t],o=r.images[a.source],s=n.textureLoader;if(o.uri){let e=n.options.manager.getHandler(o.uri);e!==null&&(s=e)}return n.loadTextureImage(e,a.source,s)}},$d=class{constructor(e){this.parser=e,this.name=Ld.EXT_TEXTURE_AVIF}loadTexture(e){let t=this.name,n=this.parser,r=n.json,i=r.textures[e];if(!i.extensions||!i.extensions[t])return null;let a=i.extensions[t],o=r.images[a.source],s=n.textureLoader;if(o.uri){let e=n.options.manager.getHandler(o.uri);e!==null&&(s=e)}return n.loadTextureImage(e,a.source,s)}},ef=class{constructor(e,t){this.name=t,this.parser=e}loadBufferView(e){let t=this.parser.json,n=t.bufferViews[e];if(n.extensions&&n.extensions[this.name]){let e=n.extensions[this.name],r=this.parser.getDependency(`buffer`,e.buffer),i=this.parser.options.meshoptDecoder;if(!i||!i.supported){if(t.extensionsRequired&&t.extensionsRequired.indexOf(this.name)>=0)throw Error(`THREE.GLTFLoader: setMeshoptDecoder must be called before loading compressed files`);return null}return r.then(function(t){let n=e.byteOffset||0,r=e.byteLength||0,a=e.count,o=e.byteStride,s=new Uint8Array(t,n,r);return i.decodeGltfBufferAsync?i.decodeGltfBufferAsync(a,o,s,e.mode,e.filter).then(function(e){return e.buffer}):i.ready.then(function(){let t=new ArrayBuffer(a*o);return i.decodeGltfBuffer(new Uint8Array(t),a,o,s,e.mode,e.filter),t})})}return null}},tf=class{constructor(e){this.name=Ld.EXT_MESH_GPU_INSTANCING,this.parser=e}createNodeMesh(e){let t=this.parser.json,n=t.nodes[e];if(!n.extensions||!n.extensions[this.name]||n.mesh===void 0)return null;let r=t.meshes[n.mesh];for(let e of r.primitives)if(e.mode!==pf.TRIANGLES&&e.mode!==pf.TRIANGLE_STRIP&&e.mode!==pf.TRIANGLE_FAN&&e.mode!==void 0)return null;let i=n.extensions[this.name].attributes,a=[],o={};for(let e in i)a.push(this.parser.getDependency(`accessor`,i[e]).then(t=>(o[e]=t,o[e])));return a.length<1?null:(a.push(this.parser.createNodeMesh(e)),Promise.all(a).then(e=>{let t=e.pop(),n=t.isGroup?t.children:[t],r=e[0].count,i=[];for(let e of n){let t=new q,n=new W,a=new jt,s=new W(1,1,1),c=new Ei(e.geometry,e.material,r);for(let e=0;e<r;e++)o.TRANSLATION&&n.fromBufferAttribute(o.TRANSLATION,e),o.ROTATION&&a.fromBufferAttribute(o.ROTATION,e),o.SCALE&&s.fromBufferAttribute(o.SCALE,e),c.setMatrixAt(e,t.compose(n,a,s));for(let t in o)if(t===`_COLOR_0`){let e=o[t];c.instanceColor=new vi(e.array,e.itemSize,e.normalized)}else t!==`TRANSLATION`&&t!==`ROTATION`&&t!==`SCALE`&&e.geometry.setAttribute(t,o[t]);En.prototype.copy.call(c,e),this.parser.assignFinalMaterial(c),i.push(c)}return t.isGroup?(t.clear(),t.add(...i),t):i[0]}))}},nf=`glTF`,rf=12,af={JSON:1313821514,BIN:5130562},of=class{constructor(e){this.name=Ld.KHR_BINARY_GLTF,this.content=null,this.body=null;let t=new DataView(e,0,rf),n=new TextDecoder;if(this.header={magic:n.decode(new Uint8Array(e.slice(0,4))),version:t.getUint32(4,!0),length:t.getUint32(8,!0)},this.header.magic!==nf)throw Error(`THREE.GLTFLoader: Unsupported glTF-Binary header.`);if(this.header.version<2)throw Error(`THREE.GLTFLoader: Legacy binary file detected.`);let r=this.header.length-rf,i=new DataView(e,rf),a=0;for(;a<r;){let t=i.getUint32(a,!0);a+=4;let r=i.getUint32(a,!0);if(a+=4,r===af.JSON){let r=new Uint8Array(e,rf+a,t);this.content=n.decode(r)}else if(r===af.BIN){let n=rf+a;this.body=e.slice(n,n+t)}a+=t}if(this.content===null)throw Error(`THREE.GLTFLoader: JSON content not found.`)}},sf=class{constructor(e,t){if(!t)throw Error(`THREE.GLTFLoader: No DRACOLoader instance provided.`);this.name=Ld.KHR_DRACO_MESH_COMPRESSION,this.json=e,this.dracoLoader=t,this.dracoLoader.preload()}decodePrimitive(e,t){let n=this.json,r=this.dracoLoader,i=e.extensions[this.name].bufferView,a=e.extensions[this.name].attributes,o={},s={},c={};for(let e in a){let t=vf[e]||e.toLowerCase();o[t]=a[e]}for(let t in e.attributes){let r=vf[t]||t.toLowerCase();if(a[t]!==void 0){let i=n.accessors[e.attributes[t]];c[r]=mf[i.componentType].name,s[r]=i.normalized===!0}}return t.getDependency(`bufferView`,i).then(function(e){return new Promise(function(t,n){r.decodeDracoFile(e,function(e){for(let t in e.attributes){let n=e.attributes[t],r=s[t];r!==void 0&&(n.normalized=r)}t(e)},o,c,We,n)})})}},cf=class{constructor(){this.name=Ld.KHR_TEXTURE_TRANSFORM}extendTexture(e,t){return(t.texCoord===void 0||t.texCoord===e.channel)&&t.offset===void 0&&t.rotation===void 0&&t.scale===void 0?e:(e=e.clone(),t.texCoord!==void 0&&(e.channel=t.texCoord),t.offset!==void 0&&e.offset.fromArray(t.offset),t.rotation!==void 0&&(e.rotation=t.rotation),t.scale!==void 0&&e.repeat.fromArray(t.scale),e.needsUpdate=!0,e)}},lf=class{constructor(){this.name=Ld.KHR_MESH_QUANTIZATION}},uf=class extends qo{constructor(e,t,n,r){super(e,t,n,r)}copySampleValue_(e){let t=this.resultBuffer,n=this.sampleValues,r=this.valueSize,i=e*r*3+r;for(let e=0;e!==r;e++)t[e]=n[i+e];return t}interpolate_(e,t,n,r){let i=this.resultBuffer,a=this.sampleValues,o=this.valueSize,s=o*2,c=o*3,l=r-t,u=(n-t)/l,d=u*u,f=d*u,p=e*c,m=p-c,h=-2*f+3*d,g=f-d,_=1-h,v=g-d+u;for(let e=0;e!==o;e++){let t=a[m+e+o],n=a[m+e+s]*l,r=a[p+e+o],c=a[p+e]*l;i[e]=_*t+v*n+h*r+g*c}return i}},df=new jt,ff=class extends uf{interpolate_(e,t,n,r){let i=super.interpolate_(e,t,n,r);return df.fromArray(i).normalize().toArray(i),i}},pf={FLOAT:5126,FLOAT_MAT3:35675,FLOAT_MAT4:35676,FLOAT_VEC2:35664,FLOAT_VEC3:35665,FLOAT_VEC4:35666,LINEAR:9729,REPEAT:10497,SAMPLER_2D:35678,POINTS:0,LINES:1,LINE_LOOP:2,LINE_STRIP:3,TRIANGLES:4,TRIANGLE_STRIP:5,TRIANGLE_FAN:6,UNSIGNED_BYTE:5121,UNSIGNED_SHORT:5123},mf={5120:Int8Array,5121:Uint8Array,5122:Int16Array,5123:Uint16Array,5125:Uint32Array,5126:Float32Array},hf={9728:o,9729:l,9984:s,9985:u,9986:c,9987:d},gf={33071:i,33648:a,10497:r},_f={SCALAR:1,VEC2:2,VEC3:3,VEC4:4,MAT2:4,MAT3:9,MAT4:16},vf={POSITION:`position`,NORMAL:`normal`,TANGENT:`tangent`,TEXCOORD_0:`uv`,TEXCOORD_1:`uv1`,TEXCOORD_2:`uv2`,TEXCOORD_3:`uv3`,COLOR_0:`color`,WEIGHTS_0:`skinWeight`,JOINTS_0:`skinIndex`},yf={scale:`scale`,translation:`position`,rotation:`quaternion`,weights:`morphTargetInfluences`},bf={CUBICSPLINE:void 0,LINEAR:Fe,STEP:Pe},xf={OPAQUE:`OPAQUE`,MASK:`MASK`,BLEND:`BLEND`};function Sf(e){return e.DefaultMaterial===void 0&&(e.DefaultMaterial=new zo({color:16777215,emissive:0,metalness:1,roughness:1,transparent:!1,depthTest:!0,side:0})),e.DefaultMaterial}function Cf(e,t,n){for(let r in n.extensions)e[r]===void 0&&(t.userData.gltfExtensions=t.userData.gltfExtensions||{},t.userData.gltfExtensions[r]=n.extensions[r])}function wf(e,t){t.extras!==void 0&&(typeof t.extras==`object`?Object.assign(e.userData,t.extras):console.warn(`THREE.GLTFLoader: Ignoring primitive type .extras, `+t.extras))}function Tf(e,t,n){let r=!1,i=!1,a=!1;for(let e=0,n=t.length;e<n;e++){let n=t[e];if(n.POSITION!==void 0&&(r=!0),n.NORMAL!==void 0&&(i=!0),n.COLOR_0!==void 0&&(a=!0),r&&i&&a)break}if(!r&&!i&&!a)return Promise.resolve(e);let o=[],s=[],c=[];for(let l=0,u=t.length;l<u;l++){let u=t[l];if(r){let t=u.POSITION===void 0?e.attributes.position:n.getDependency(`accessor`,u.POSITION);o.push(t)}if(i){let t=u.NORMAL===void 0?e.attributes.normal:n.getDependency(`accessor`,u.NORMAL);s.push(t)}if(a){let t=u.COLOR_0===void 0?e.attributes.color:n.getDependency(`accessor`,u.COLOR_0);c.push(t)}}return Promise.all([Promise.all(o),Promise.all(s),Promise.all(c)]).then(function(t){let n=t[0],o=t[1],s=t[2];return r&&(e.morphAttributes.position=n),i&&(e.morphAttributes.normal=o),a&&(e.morphAttributes.color=s),e.morphTargetsRelative=!0,e})}function Ef(e,t){if(e.updateMorphTargets(),t.weights!==void 0)for(let n=0,r=t.weights.length;n<r;n++)e.morphTargetInfluences[n]=t.weights[n];if(t.extras&&Array.isArray(t.extras.targetNames)){let n=t.extras.targetNames;if(e.morphTargetInfluences.length===n.length){e.morphTargetDictionary={};for(let t=0,r=n.length;t<r;t++)e.morphTargetDictionary[n[t]]=t}else console.warn(`THREE.GLTFLoader: Invalid extras.targetNames length. Ignoring names.`)}}function Df(e){let t,n=e.extensions&&e.extensions[Ld.KHR_DRACO_MESH_COMPRESSION];if(t=n?`draco:`+n.bufferView+`:`+n.indices+`:`+Of(n.attributes):e.indices+`:`+Of(e.attributes)+`:`+e.mode,e.targets!==void 0)for(let n=0,r=e.targets.length;n<r;n++)t+=`:`+Of(e.targets[n]);return t}function Of(e){let t=``,n=Object.keys(e).sort();for(let r=0,i=n.length;r<i;r++)t+=n[r]+`:`+e[n[r]]+`;`;return t}function kf(e){switch(e){case Int8Array:return 1/127;case Uint8Array:return 1/255;case Int16Array:return 1/32767;case Uint16Array:return 1/65535;default:throw Error(`THREE.GLTFLoader: Unsupported normalized accessor component type.`)}}function Af(e){return e.search(/\.jpe?g($|\?)/i)>0||e.search(/^data\:image\/jpeg/)===0?`image/jpeg`:e.search(/\.webp($|\?)/i)>0||e.search(/^data\:image\/webp/)===0?`image/webp`:e.search(/\.ktx2($|\?)/i)>0||e.search(/^data\:image\/ktx2/)===0?`image/ktx2`:`image/png`}var jf=new q,Mf=class{constructor(e={},t={}){this.json=e,this.extensions={},this.plugins={},this.options=t,this.cache=new Fd,this.associations=new Map,this.primitiveCache={},this.nodeCache={},this.meshCache={refs:{},uses:{}},this.cameraCache={refs:{},uses:{}},this.lightCache={refs:{},uses:{}},this.sourceCache={},this.textureCache={},this.nodeNamesUsed={};let n=!1,r=-1,i=!1,a=-1;if(typeof navigator<`u`&&navigator.userAgent!==void 0){let e=navigator.userAgent;n=/^((?!chrome|android).)*safari/i.test(e)===!0;let t=e.match(/Version\/(\d+)/);r=n&&t?parseInt(t[1],10):-1,i=e.indexOf(`Firefox`)>-1,a=i?e.match(/Firefox\/([0-9]+)\./)[1]:-1}this.textureLoader=typeof createImageBitmap>`u`||n&&r<17||i&&a<98?new vs(this.options.manager):new Vs(this.options.manager),this.textureLoader.setCrossOrigin(this.options.crossOrigin),this.textureLoader.setRequestHeader(this.options.requestHeader),this.fileLoader=new hs(this.options.manager),this.fileLoader.setResponseType(`arraybuffer`),this.options.crossOrigin===`use-credentials`&&this.fileLoader.setWithCredentials(!0)}setExtensions(e){this.extensions=e}setPlugins(e){this.plugins=e}parse(e,t){let n=this,r=this.json,i=this.extensions;this.cache.removeAll(),this.nodeCache={},this._invokeAll(function(e){return e._markDefs&&e._markDefs()}),Promise.all(this._invokeAll(function(e){return e.beforeRoot&&e.beforeRoot()})).then(function(){return Promise.all([n.getDependencies(`scene`),n.getDependencies(`animation`),n.getDependencies(`camera`)])}).then(function(t){let a={scene:t[0][r.scene||0],scenes:t[0],animations:t[1],cameras:t[2],asset:r.asset,parser:n,userData:{}};return Cf(i,a,r),wf(a,r),Promise.all(n._invokeAll(function(e){return e.afterRoot&&e.afterRoot(a)})).then(function(){for(let e of a.scenes)e.updateMatrixWorld();e(a)})}).catch(t)}_markDefs(){let e=this.json.nodes||[],t=this.json.skins||[],n=this.json.meshes||[];for(let n=0,r=t.length;n<r;n++){let r=t[n].joints;for(let t=0,n=r.length;t<n;t++)e[r[t]].isBone=!0}for(let t=0,r=e.length;t<r;t++){let r=e[t];r.mesh!==void 0&&(this._addNodeRef(this.meshCache,r.mesh),r.skin!==void 0&&(n[r.mesh].isSkinnedMesh=!0)),r.camera!==void 0&&this._addNodeRef(this.cameraCache,r.camera)}}_addNodeRef(e,t){t!==void 0&&(e.refs[t]===void 0&&(e.refs[t]=e.uses[t]=0),e.refs[t]++)}_getNodeRef(e,t,n){if(e.refs[t]<=1)return n;let r=n.clone(),i=(e,t)=>{let n=this.associations.get(e);n!=null&&this.associations.set(t,n);for(let[n,r]of e.children.entries())i(r,t.children[n])};return i(n,r),r.name+=`_instance_`+e.uses[t]++,r}_invokeOne(e){let t=Object.values(this.plugins);t.push(this);for(let n=0;n<t.length;n++){let r=e(t[n]);if(r)return r}return null}_invokeAll(e){let t=Object.values(this.plugins);t.unshift(this);let n=[];for(let r=0;r<t.length;r++){let i=e(t[r]);i&&n.push(i)}return n}getDependency(e,t){let n=e+`:`+t,r=this.cache.get(n);if(!r){switch(e){case`scene`:r=this.loadScene(t);break;case`node`:r=this._invokeOne(function(e){return e.loadNode&&e.loadNode(t)});break;case`mesh`:r=this._invokeOne(function(e){return e.loadMesh&&e.loadMesh(t)});break;case`accessor`:r=this.loadAccessor(t);break;case`bufferView`:r=this._invokeOne(function(e){return e.loadBufferView&&e.loadBufferView(t)});break;case`buffer`:r=this.loadBuffer(t);break;case`material`:r=this._invokeOne(function(e){return e.loadMaterial&&e.loadMaterial(t)});break;case`texture`:r=this._invokeOne(function(e){return e.loadTexture&&e.loadTexture(t)});break;case`skin`:r=this.loadSkin(t);break;case`animation`:r=this._invokeOne(function(e){return e.loadAnimation&&e.loadAnimation(t)});break;case`camera`:r=this.loadCamera(t);break;default:if(r=this._invokeOne(function(n){return n!=this&&n.getDependency&&n.getDependency(e,t)}),!r)throw Error(`Unknown type: `+e)}this.cache.add(n,r)}return r}getDependencies(e){let t=this.cache.get(e);if(!t){let n=this,r=this.json[e+(e===`mesh`?`es`:`s`)]||[];t=Promise.all(r.map(function(t,r){return n.getDependency(e,r)})),this.cache.add(e,t)}return t}loadBuffer(e){let t=this.json.buffers[e],n=this.fileLoader;if(t.type&&t.type!==`arraybuffer`)throw Error(`THREE.GLTFLoader: `+t.type+` buffer type is not supported.`);if(t.uri===void 0&&e===0)return Promise.resolve(this.extensions[Ld.KHR_BINARY_GLTF].body);let r=this.options;return new Promise(function(e,i){n.load(zs.resolveURL(t.uri,r.path),e,void 0,function(){i(Error(`THREE.GLTFLoader: Failed to load buffer "`+t.uri+`".`))})})}loadBufferView(e){let t=this.json.bufferViews[e];return this.getDependency(`buffer`,t.buffer).then(function(e){let n=t.byteLength||0,r=t.byteOffset||0;return e.slice(r,r+n)})}loadAccessor(e){let t=this,n=this.json,r=this.json.accessors[e];if(r.bufferView===void 0&&r.sparse===void 0){let e=_f[r.type],t=mf[r.componentType],n=r.normalized===!0,i=new t(r.count*e);return Promise.resolve(new mr(i,e,n))}let i=[];return r.bufferView===void 0?i.push(null):i.push(this.getDependency(`bufferView`,r.bufferView)),r.sparse!==void 0&&(i.push(this.getDependency(`bufferView`,r.sparse.indices.bufferView)),i.push(this.getDependency(`bufferView`,r.sparse.values.bufferView))),Promise.all(i).then(function(e){let i=e[0],a=_f[r.type],o=mf[r.componentType],s=o.BYTES_PER_ELEMENT,c=s*a,l=r.byteOffset||0,u=r.bufferView===void 0?void 0:n.bufferViews[r.bufferView].byteStride,d=r.normalized===!0,f,p;if(u&&u!==c){let e=Math.floor(l/u),n=`InterleavedBuffer:`+r.bufferView+`:`+r.componentType+`:`+e+`:`+r.count,c=t.cache.get(n);c||(f=new o(i,e*u,r.count*u/s),c=new kr(f,u/s),t.cache.add(n,c)),p=new jr(c,a,l%u/s,d)}else f=i===null?new o(r.count*a):new o(i,l,r.count*a),p=new mr(f,a,d);if(r.sparse!==void 0){let t=_f.SCALAR,n=mf[r.sparse.indices.componentType],s=r.sparse.indices.byteOffset||0,c=r.sparse.values.byteOffset||0,l=new n(e[1],s,r.sparse.count*t),u=new o(e[2],c,r.sparse.count*a);i!==null&&(p=new mr(p.array.slice(),p.itemSize,p.normalized)),p.normalized=!1;for(let e=0,t=l.length;e<t;e++){let t=l[e];if(p.setX(t,u[e*a]),a>=2&&p.setY(t,u[e*a+1]),a>=3&&p.setZ(t,u[e*a+2]),a>=4&&p.setW(t,u[e*a+3]),a>=5)throw Error(`THREE.GLTFLoader: Unsupported itemSize in sparse BufferAttribute.`)}p.normalized=d}return p})}loadTexture(e){let t=this.json,n=this.options,r=t.textures[e].source,i=t.images[r],a=this.textureLoader;if(i.uri){let e=n.manager.getHandler(i.uri);e!==null&&(a=e)}return this.loadTextureImage(e,r,a)}loadTextureImage(e,t,n){let r=this,i=this.json,a=i.textures[e],o=i.images[t],s=(o.uri||o.bufferView)+`:`+a.sampler;if(this.textureCache[s])return this.textureCache[s];let c=this.loadImageSource(t,n).then(function(t){t.flipY=!1,t.name=a.name||o.name||``,t.name===``&&typeof o.uri==`string`&&o.uri.startsWith(`data:image/`)===!1&&(t.name=o.uri);let n=(i.samplers||{})[a.sampler]||{};return t.magFilter=hf[n.magFilter]||1006,t.minFilter=hf[n.minFilter]||1008,t.wrapS=gf[n.wrapS]||1e3,t.wrapT=gf[n.wrapT]||1e3,t.generateMipmaps=!t.isCompressedTexture&&t.minFilter!==1003&&t.minFilter!==1006,r.associations.set(t,{textures:e}),t}).catch(function(){return null});return this.textureCache[s]=c,c}loadImageSource(e,t){let n=this,r=this.json,i=this.options;if(this.sourceCache[e]!==void 0)return this.sourceCache[e].then(e=>e.clone());let a=r.images[e],o=self.URL||self.webkitURL,s=a.uri||``,c=!1;if(a.bufferView!==void 0)s=n.getDependency(`bufferView`,a.bufferView).then(function(e){c=!0;let t=new Blob([e],{type:a.mimeType});return s=o.createObjectURL(t),s});else if(a.uri===void 0)throw Error(`THREE.GLTFLoader: Image `+e+` is missing URI and bufferView`);let l=Promise.resolve(s).then(function(e){return new Promise(function(n,r){let a=n;t.isImageBitmapLoader===!0&&(a=function(e){let t=new qt(e);t.needsUpdate=!0,n(t)}),t.load(zs.resolveURL(e,i.path),a,void 0,r)})}).then(function(e){return c===!0&&o.revokeObjectURL(s),wf(e,a),e.userData.mimeType=a.mimeType||Af(a.uri),e}).catch(function(e){throw console.error(`THREE.GLTFLoader: Couldn't load texture`,s),e});return this.sourceCache[e]=l,l}assignTexture(e,t,n,r){let i=this;return this.getDependency(`texture`,n.index).then(function(a){if(!a)return null;if(n.texCoord!==void 0&&n.texCoord>0&&(a=a.clone(),a.channel=n.texCoord),i.extensions[Ld.KHR_TEXTURE_TRANSFORM]){let e=n.extensions===void 0?void 0:n.extensions[Ld.KHR_TEXTURE_TRANSFORM];if(e){let t=i.associations.get(a);a=i.extensions[Ld.KHR_TEXTURE_TRANSFORM].extendTexture(a,e),i.associations.set(a,t)}}return r!==void 0&&(a.colorSpace=r),e[t]=a,a})}assignFinalMaterial(e){let t=e.geometry,n=e.material,r=t.attributes.tangent===void 0,i=t.attributes.color!==void 0,a=t.attributes.normal===void 0;if(e.isPoints){let e=`PointsMaterial:`+n.uuid,t=this.cache.get(e);t||(t=new Yi,Nr.prototype.copy.call(t,n),t.color.copy(n.color),t.map=n.map,t.sizeAttenuation=!1,this.cache.add(e,t)),n=t}else if(e.isLine){let e=`LineBasicMaterial:`+n.uuid,t=this.cache.get(e);t||(t=new Fi,Nr.prototype.copy.call(t,n),t.color.copy(n.color),t.map=n.map,this.cache.add(e,t)),n=t}if(r||i||a){let e=`ClonedMaterial:`+n.uuid+`:`;r&&(e+=`derivative-tangents:`),i&&(e+=`vertex-colors:`),a&&(e+=`flat-shading:`);let t=this.cache.get(e);t||(t=n.clone(),i&&(t.vertexColors=!0),a&&(t.flatShading=!0),r&&(t.normalScale&&(t.normalScale.y*=-1),t.clearcoatNormalScale&&(t.clearcoatNormalScale.y*=-1)),this.cache.add(e,t),this.associations.set(t,this.associations.get(n))),n=t}e.material=n}getMaterialType(){return zo}loadMaterial(e){let t=this,n=this.json,r=this.extensions,i=n.materials[e],a,o={},s=i.extensions||{},c=[];if(s[Ld.KHR_MATERIALS_UNLIT]){let e=r[Ld.KHR_MATERIALS_UNLIT];a=e.getMaterialType(),c.push(e.extendParams(o,i,t))}else{let n=i.pbrMetallicRoughness||{};if(o.color=new J(1,1,1),o.opacity=1,Array.isArray(n.baseColorFactor)){let e=n.baseColorFactor;o.color.setRGB(e[0],e[1],e[2],We),o.opacity=e[3]}n.baseColorTexture!==void 0&&c.push(t.assignTexture(o,`map`,n.baseColorTexture,Ue)),o.metalness=n.metallicFactor===void 0?1:n.metallicFactor,o.roughness=n.roughnessFactor===void 0?1:n.roughnessFactor,n.metallicRoughnessTexture!==void 0&&(c.push(t.assignTexture(o,`metalnessMap`,n.metallicRoughnessTexture)),c.push(t.assignTexture(o,`roughnessMap`,n.metallicRoughnessTexture))),a=this._invokeOne(function(t){return t.getMaterialType&&t.getMaterialType(e)}),c.push(Promise.all(this._invokeAll(function(t){return t.extendMaterialParams&&t.extendMaterialParams(e,o)})))}i.doubleSided===!0&&(o.side=2);let l=i.alphaMode||xf.OPAQUE;if(l===xf.BLEND?(o.transparent=!0,o.depthWrite=!1):(o.transparent=!1,l===xf.MASK&&(o.alphaTest=i.alphaCutoff===void 0?.5:i.alphaCutoff)),i.normalTexture!==void 0&&a!==Hr&&(c.push(t.assignTexture(o,`normalMap`,i.normalTexture)),o.normalScale=new U(1,1),i.normalTexture.scale!==void 0)){let e=i.normalTexture.scale;o.normalScale.set(e,e)}if(i.occlusionTexture!==void 0&&a!==Hr&&(c.push(t.assignTexture(o,`aoMap`,i.occlusionTexture)),i.occlusionTexture.strength!==void 0&&(o.aoMapIntensity=i.occlusionTexture.strength)),i.emissiveFactor!==void 0&&a!==Hr){let e=i.emissiveFactor;o.emissive=new J().setRGB(e[0],e[1],e[2],We)}return i.emissiveTexture!==void 0&&a!==Hr&&c.push(t.assignTexture(o,`emissiveMap`,i.emissiveTexture,Ue)),Promise.all(c).then(function(){let n=new a(o);return i.name&&(n.name=i.name),wf(n,i),t.associations.set(n,{materials:e}),i.extensions&&Cf(r,n,i),n})}createUniqueName(e){let t=rc.sanitizeNodeName(e||``);return t in this.nodeNamesUsed?t+`_`+ ++this.nodeNamesUsed[t]:(this.nodeNamesUsed[t]=0,t)}loadGeometries(e){let t=this,n=this.extensions,r=this.primitiveCache;function i(e){return n[Ld.KHR_DRACO_MESH_COMPRESSION].decodePrimitive(e,t).then(function(n){return Pf(n,e,t)})}let a=[];for(let n=0,o=e.length;n<o;n++){let o=e[n],s=Df(o),c=r[s];if(c)a.push(c.promise);else{let e;e=o.extensions&&o.extensions[Ld.KHR_DRACO_MESH_COMPRESSION]?i(o):Pf(new Or,o,t),r[s]={primitive:o,promise:e},a.push(e)}}return Promise.all(a)}loadMesh(e){let t=this,n=this.json,r=this.extensions,i=n.meshes[e],a=i.primitives,o=[];for(let e=0,t=a.length;e<t;e++){let t=a[e].material===void 0?Sf(this.cache):this.getDependency(`material`,a[e].material);o.push(t)}return o.push(t.loadGeometries(a)),Promise.all(o).then(function(n){let o=n.slice(0,n.length-1),s=n[n.length-1],c=[];for(let n=0,l=s.length;n<l;n++){let l=s[n],u=a[n],d,f=o[n];if(u.mode===pf.TRIANGLES||u.mode===pf.TRIANGLE_STRIP||u.mode===pf.TRIANGLE_FAN||u.mode===void 0)d=i.isSkinnedMesh===!0?new fi(l,f):new ei(l,f),d.isSkinnedMesh===!0&&d.normalizeSkinWeights(),u.mode===pf.TRIANGLE_STRIP?d.geometry=jd(d.geometry,1):u.mode===pf.TRIANGLE_FAN&&(d.geometry=jd(d.geometry,2));else if(u.mode===pf.LINES)d=new qi(l,f);else if(u.mode===pf.LINE_STRIP)d=new Ui(l,f);else if(u.mode===pf.LINE_LOOP)d=new Ji(l,f);else if(u.mode===pf.POINTS)d=new ea(l,f);else throw Error(`THREE.GLTFLoader: Primitive mode unsupported: `+u.mode);Object.keys(d.geometry.morphAttributes).length>0&&Ef(d,i),d.name=t.createUniqueName(i.name||`mesh_`+e),wf(d,i),u.extensions&&Cf(r,d,u),t.assignFinalMaterial(d),c.push(d)}for(let n=0,r=c.length;n<r;n++)t.associations.set(c[n],{meshes:e,primitives:n});if(c.length===1)return i.extensions&&Cf(r,c[0],i),c[0];let l=new Dn;i.extensions&&Cf(r,l,i),t.associations.set(l,{meshes:e});for(let e=0,t=c.length;e<t;e++)l.add(c[e]);return l})}loadCamera(e){let t,n=this.json.cameras[e],r=n[n.type];if(!r){console.warn(`THREE.GLTFLoader: Missing camera parameters.`);return}return n.type===`perspective`?t=new js(At.radToDeg(r.yfov),r.aspectRatio||1,r.znear||1,r.zfar||2e6):n.type===`orthographic`&&(t=new Is(-r.xmag,r.xmag,r.ymag,-r.ymag,r.znear,r.zfar)),n.name&&(t.name=this.createUniqueName(n.name)),wf(t,n),Promise.resolve(t)}loadSkin(e){let t=this.json.skins[e],n=[];for(let e=0,r=t.joints.length;e<r;e++)n.push(this._loadNodeShallow(t.joints[e]));return t.inverseBindMatrices===void 0?n.push(null):n.push(this.getDependency(`accessor`,t.inverseBindMatrices)),Promise.all(n).then(function(e){let n=e.pop(),r=e,i=[],a=[];for(let e=0,o=r.length;e<o;e++){let o=r[e];if(o){i.push(o);let t=new q;n!==null&&t.fromArray(n.array,e*16),a.push(t)}else console.warn(`THREE.GLTFLoader: Joint "%s" could not be found.`,t.joints[e])}return new _i(i,a)})}loadAnimation(e){let t=this.json,n=this,r=t.animations[e],i=r.name?r.name:`animation_`+e,a=[],o=[],s=[],c=[],l=[];for(let e=0,t=r.channels.length;e<t;e++){let t=r.channels[e],n=r.samplers[t.sampler],i=t.target,u=i.node,d=r.parameters===void 0?n.input:r.parameters[n.input],f=r.parameters===void 0?n.output:r.parameters[n.output];i.node!==void 0&&(a.push(this.getDependency(`node`,u)),o.push(this.getDependency(`accessor`,d)),s.push(this.getDependency(`accessor`,f)),c.push(n),l.push(i))}return Promise.all([Promise.all(a),Promise.all(o),Promise.all(s),Promise.all(c),Promise.all(l)]).then(function(e){let t=e[0],a=e[1],o=e[2],s=e[3],c=e[4],l=[];for(let e=0,r=t.length;e<r;e++){let r=t[e],i=a[e],u=o[e],d=s[e],f=c[e];if(r===void 0)continue;r.updateMatrix&&r.updateMatrix();let p=n._createAnimationTracks(r,i,u,d,f);if(p)for(let e=0;e<p.length;e++)l.push(p[e])}let u=new os(i,void 0,l);return wf(u,r),u})}createNodeMesh(e){let t=this.json,n=this,r=t.nodes[e];return r.mesh===void 0?null:n.getDependency(`mesh`,r.mesh).then(function(e){let t=n._getNodeRef(n.meshCache,r.mesh,e);return r.weights!==void 0&&t.traverse(function(e){if(e.isMesh)for(let t=0,n=r.weights.length;t<n;t++)e.morphTargetInfluences[t]=r.weights[t]}),t})}loadNode(e){let t=this.json,n=this,r=t.nodes[e],i=n._loadNodeShallow(e),a=[],o=r.children||[];for(let e=0,t=o.length;e<t;e++)a.push(n.getDependency(`node`,o[e]));let s=r.skin===void 0?Promise.resolve(null):n.getDependency(`skin`,r.skin);return Promise.all([i,Promise.all(a),s]).then(function(e){let t=e[0],n=e[1],r=e[2];r!==null&&t.traverse(function(e){e.isSkinnedMesh&&e.bind(r,jf)});for(let e=0,r=n.length;e<r;e++)t.add(n[e]);if(t.userData.pivot!==void 0&&n.length>0){let e=t.userData.pivot,r=n[0];t.pivot=new W().fromArray(e),t.position.x-=e[0],t.position.y-=e[1],t.position.z-=e[2],r.position.set(0,0,0),delete t.userData.pivot}return t})}_loadNodeShallow(e){let t=this.json,n=this.extensions,r=this;if(this.nodeCache[e]!==void 0)return this.nodeCache[e];let i=t.nodes[e],a=i.name?r.createUniqueName(i.name):``,o=[],s=r._invokeOne(function(t){return t.createNodeMesh&&t.createNodeMesh(e)});return s&&o.push(s),i.camera!==void 0&&o.push(r.getDependency(`camera`,i.camera).then(function(e){return r._getNodeRef(r.cameraCache,i.camera,e)})),r._invokeAll(function(t){return t.createNodeAttachment&&t.createNodeAttachment(e)}).forEach(function(e){o.push(e)}),this.nodeCache[e]=Promise.all(o).then(function(t){let o;if(o=i.isBone===!0?new pi:t.length>1?new Dn:t.length===1?t[0]:new En,o!==t[0])for(let e=0,n=t.length;e<n;e++)o.add(t[e]);if(i.name&&(o.userData.name=i.name,o.name=a),wf(o,i),i.extensions&&Cf(n,o,i),i.matrix!==void 0){let e=new q;e.fromArray(i.matrix),o.applyMatrix4(e)}else i.translation!==void 0&&o.position.fromArray(i.translation),i.rotation!==void 0&&o.quaternion.fromArray(i.rotation),i.scale!==void 0&&o.scale.fromArray(i.scale);if(!r.associations.has(o))r.associations.set(o,{});else if(i.mesh!==void 0&&r.meshCache.refs[i.mesh]>1){let e=r.associations.get(o);r.associations.set(o,{...e})}return r.associations.get(o).nodes=e,o}),this.nodeCache[e]}loadScene(e){let t=this.extensions,n=this.json.scenes[e],r=this,i=new Dn;n.name&&(i.name=r.createUniqueName(n.name)),wf(i,n),n.extensions&&Cf(t,i,n);let a=n.nodes||[],o=[];for(let e=0,t=a.length;e<t;e++)o.push(r.getDependency(`node`,a[e]));return Promise.all(o).then(function(e){for(let t=0,n=e.length;t<n;t++){let n=e[t];n.parent===null?i.add(n):i.add(Md(n))}return r.associations=(e=>{let t=new Map;for(let[e,n]of r.associations)(e instanceof Nr||e instanceof qt)&&t.set(e,n);return e.traverse(e=>{let n=r.associations.get(e);n!=null&&t.set(e,n)}),t})(i),i})}_createAnimationTracks(e,t,n,r,i){let a=[],o=e.name?e.name:e.uuid,s=[];function c(e){e.morphTargetInfluences&&s.push(e.name?e.name:e.uuid)}yf[i.path]===yf.weights?(c(e),e.isGroup&&e.children.forEach(c)):s.push(o);let l;switch(yf[i.path]){case yf.weights:l=ts;break;case yf.rotation:l=rs;break;case yf.translation:case yf.scale:l=as;break;default:switch(n.itemSize){case 1:l=ts;break;default:l=as}}let u=r.interpolation===void 0?Fe:bf[r.interpolation],d=this._getArrayFromAccessor(n);for(let e=0,n=s.length;e<n;e++){let n=new l(s[e]+`.`+yf[i.path],t.array,d,u);r.interpolation===`CUBICSPLINE`&&this._createCubicSplineTrackInterpolant(n),a.push(n)}return a}_getArrayFromAccessor(e){let t=e.array;if(e.normalized){let e=kf(t.constructor),n=new Float32Array(t.length);for(let r=0,i=t.length;r<i;r++)n[r]=t[r]*e;t=n}return t}_createCubicSplineTrackInterpolant(e){e.createInterpolant=function(e){return new(this instanceof rs?ff:uf)(this.times,this.values,this.getValueSize()/3,e)},e.createInterpolant.isInterpolantFactoryMethodGLTFCubicSpline=!0}};function Nf(e,t,n){let r=t.attributes,i=new Xn;if(r.POSITION!==void 0){let e=n.json.accessors[r.POSITION],t=e.min,a=e.max;if(t!==void 0&&a!==void 0){if(i.set(new W(t[0],t[1],t[2]),new W(a[0],a[1],a[2])),e.normalized){let t=kf(mf[e.componentType]);i.min.multiplyScalar(t),i.max.multiplyScalar(t)}}else{console.warn(`THREE.GLTFLoader: Missing min/max properties for accessor POSITION.`);return}}else return;let a=t.targets;if(a!==void 0){let e=new W,t=new W;for(let r=0,i=a.length;r<i;r++){let i=a[r];if(i.POSITION!==void 0){let r=n.json.accessors[i.POSITION],a=r.min,o=r.max;if(a!==void 0&&o!==void 0){if(t.setX(Math.max(Math.abs(a[0]),Math.abs(o[0]))),t.setY(Math.max(Math.abs(a[1]),Math.abs(o[1]))),t.setZ(Math.max(Math.abs(a[2]),Math.abs(o[2]))),r.normalized){let e=kf(mf[r.componentType]);t.multiplyScalar(e)}e.max(t)}else console.warn(`THREE.GLTFLoader: Missing min/max properties for accessor POSITION.`)}}i.expandByVector(e)}e.boundingBox=i;let o=new xr;i.getCenter(o.center),o.radius=i.min.distanceTo(i.max)/2,e.boundingSphere=o}function Pf(e,t,n){let r=t.attributes,i=[];function a(t,r){return n.getDependency(`accessor`,t).then(function(t){e.setAttribute(r,t)})}for(let t in r){let n=vf[t]||t.toLowerCase();n in e.attributes||i.push(a(r[t],n))}if(t.indices!==void 0&&!e.index){let r=n.getDependency(`accessor`,t.indices).then(function(t){e.setIndex(t)});i.push(r)}return K.workingColorSpace!==`srgb-linear`&&`COLOR_0`in r&&console.warn(`THREE.GLTFLoader: Converting vertex colors from "srgb-linear" to "${K.workingColorSpace}" not supported.`),wf(e,t),Nf(e,t,n),Promise.all(i).then(function(){return t.targets===void 0?e:Tf(e,t.targets,n)})}var Ff={type:`change`},If={type:`start`},Lf={type:`end`},Rf=new Vr,zf=new Ai,Bf=Math.cos(70*At.DEG2RAD),Vf=new W,Hf=2*Math.PI,Uf={NONE:-1,ROTATE:0,DOLLY:1,PAN:2,TOUCH_ROTATE:3,TOUCH_PAN:4,TOUCH_DOLLY_PAN:5,TOUCH_DOLLY_ROTATE:6},Wf=1e-6,Gf=class extends lc{constructor(n,r=null){super(n,r),this.state=Uf.NONE,this.target=new W,this.cursor=new W,this.minDistance=0,this.maxDistance=1/0,this.minZoom=0,this.maxZoom=1/0,this.minTargetRadius=0,this.maxTargetRadius=1/0,this.minPolarAngle=0,this.maxPolarAngle=Math.PI,this.minAzimuthAngle=-1/0,this.maxAzimuthAngle=1/0,this.enableDamping=!1,this.dampingFactor=.05,this.enableZoom=!0,this.zoomSpeed=1,this.enableRotate=!0,this.rotateSpeed=1,this.keyRotateSpeed=1,this.enablePan=!0,this.panSpeed=1,this.screenSpacePanning=!0,this.keyPanSpeed=7,this.zoomToCursor=!1,this.autoRotate=!1,this.autoRotateSpeed=2,this.keys={LEFT:`ArrowLeft`,UP:`ArrowUp`,RIGHT:`ArrowRight`,BOTTOM:`ArrowDown`},this.mouseButtons={LEFT:e.ROTATE,MIDDLE:e.DOLLY,RIGHT:e.PAN},this.touches={ONE:t.ROTATE,TWO:t.DOLLY_PAN},this.target0=this.target.clone(),this.position0=this.object.position.clone(),this.zoom0=this.object.zoom,this._cursorStyle=`auto`,this._domElementKeyEvents=null,this._lastPosition=new W,this._lastQuaternion=new jt,this._lastTargetPosition=new W,this._quat=new jt().setFromUnitVectors(n.up,new W(0,1,0)),this._quatInverse=this._quat.clone().invert(),this._spherical=new cc,this._sphericalDelta=new cc,this._scale=1,this._panOffset=new W,this._rotateStart=new U,this._rotateEnd=new U,this._rotateDelta=new U,this._panStart=new U,this._panEnd=new U,this._panDelta=new U,this._dollyStart=new U,this._dollyEnd=new U,this._dollyDelta=new U,this._dollyDirection=new W,this._mouse=new U,this._performCursorZoom=!1,this._pointers=[],this._pointerPositions={},this._controlActive=!1,this._onPointerMove=qf.bind(this),this._onPointerDown=Kf.bind(this),this._onPointerUp=Jf.bind(this),this._onContextMenu=tp.bind(this),this._onMouseWheel=Zf.bind(this),this._onKeyDown=Qf.bind(this),this._onTouchStart=$f.bind(this),this._onTouchMove=ep.bind(this),this._onMouseDown=Yf.bind(this),this._onMouseMove=Xf.bind(this),this._interceptControlDown=np.bind(this),this._interceptControlUp=rp.bind(this),this.domElement!==null&&this.connect(this.domElement),this.update()}set cursorStyle(e){this._cursorStyle=e,e===`grab`?this.domElement.style.cursor=`grab`:this.domElement.style.cursor=`auto`}get cursorStyle(){return this._cursorStyle}connect(e){super.connect(e),this.domElement.addEventListener(`pointerdown`,this._onPointerDown),this.domElement.addEventListener(`pointercancel`,this._onPointerUp),this.domElement.addEventListener(`contextmenu`,this._onContextMenu),this.domElement.addEventListener(`wheel`,this._onMouseWheel,{passive:!1}),this.domElement.getRootNode().addEventListener(`keydown`,this._interceptControlDown,{passive:!0,capture:!0}),this.domElement.style.touchAction=`none`}disconnect(){this.domElement.removeEventListener(`pointerdown`,this._onPointerDown),this.domElement.ownerDocument.removeEventListener(`pointermove`,this._onPointerMove),this.domElement.ownerDocument.removeEventListener(`pointerup`,this._onPointerUp),this.domElement.removeEventListener(`pointercancel`,this._onPointerUp),this.domElement.removeEventListener(`wheel`,this._onMouseWheel),this.domElement.removeEventListener(`contextmenu`,this._onContextMenu),this.stopListenToKeyEvents(),this.domElement.getRootNode().removeEventListener(`keydown`,this._interceptControlDown,{capture:!0}),this.domElement.style.touchAction=``}dispose(){this.disconnect()}getPolarAngle(){return this._spherical.phi}getAzimuthalAngle(){return this._spherical.theta}getDistance(){return this.object.position.distanceTo(this.target)}listenToKeyEvents(e){e.addEventListener(`keydown`,this._onKeyDown),this._domElementKeyEvents=e}stopListenToKeyEvents(){this._domElementKeyEvents!==null&&(this._domElementKeyEvents.removeEventListener(`keydown`,this._onKeyDown),this._domElementKeyEvents=null)}saveState(){this.target0.copy(this.target),this.position0.copy(this.object.position),this.zoom0=this.object.zoom}reset(){this.target.copy(this.target0),this.object.position.copy(this.position0),this.object.zoom=this.zoom0,this.object.updateProjectionMatrix(),this.dispatchEvent(Ff),this.update(),this.state=Uf.NONE}pan(e,t){this._pan(e,t),this.update()}dollyIn(e){this._dollyIn(e),this.update()}dollyOut(e){this._dollyOut(e),this.update()}rotateLeft(e){this._rotateLeft(e),this.update()}rotateUp(e){this._rotateUp(e),this.update()}update(e=null){let t=this.object.position;Vf.copy(t).sub(this.target),Vf.applyQuaternion(this._quat),this._spherical.setFromVector3(Vf),this.autoRotate&&this.state===Uf.NONE&&this._rotateLeft(this._getAutoRotationAngle(e)),this.enableDamping?(this._spherical.theta+=this._sphericalDelta.theta*this.dampingFactor,this._spherical.phi+=this._sphericalDelta.phi*this.dampingFactor):(this._spherical.theta+=this._sphericalDelta.theta,this._spherical.phi+=this._sphericalDelta.phi);let n=this.minAzimuthAngle,r=this.maxAzimuthAngle;isFinite(n)&&isFinite(r)&&(n<-Math.PI?n+=Hf:n>Math.PI&&(n-=Hf),r<-Math.PI?r+=Hf:r>Math.PI&&(r-=Hf),n<=r?this._spherical.theta=Math.max(n,Math.min(r,this._spherical.theta)):this._spherical.theta=this._spherical.theta>(n+r)/2?Math.max(n,this._spherical.theta):Math.min(r,this._spherical.theta)),this._spherical.phi=Math.max(this.minPolarAngle,Math.min(this.maxPolarAngle,this._spherical.phi)),this._spherical.makeSafe(),this.enableDamping===!0?this.target.addScaledVector(this._panOffset,this.dampingFactor):this.target.add(this._panOffset),this.target.sub(this.cursor),this.target.clampLength(this.minTargetRadius,this.maxTargetRadius),this.target.add(this.cursor);let i=!1;if(this.zoomToCursor&&this._performCursorZoom||this.object.isOrthographicCamera)this._spherical.radius=this._clampDistance(this._spherical.radius);else{let e=this._spherical.radius;this._spherical.radius=this._clampDistance(this._spherical.radius*this._scale),i=e!=this._spherical.radius}if(Vf.setFromSpherical(this._spherical),Vf.applyQuaternion(this._quatInverse),t.copy(this.target).add(Vf),this.object.lookAt(this.target),this.enableDamping===!0?(this._sphericalDelta.theta*=1-this.dampingFactor,this._sphericalDelta.phi*=1-this.dampingFactor,this._panOffset.multiplyScalar(1-this.dampingFactor)):(this._sphericalDelta.set(0,0,0),this._panOffset.set(0,0,0)),this.zoomToCursor&&this._performCursorZoom){let e=null;if(this.object.isPerspectiveCamera){let t=Vf.length();e=this._clampDistance(t*this._scale);let n=t-e;this.object.position.addScaledVector(this._dollyDirection,n),this.object.updateMatrixWorld(),i=!!n}else if(this.object.isOrthographicCamera){let t=new W(this._mouse.x,this._mouse.y,0);t.unproject(this.object);let n=this.object.zoom;this.object.zoom=Math.max(this.minZoom,Math.min(this.maxZoom,this.object.zoom/this._scale)),this.object.updateProjectionMatrix(),i=n!==this.object.zoom;let r=new W(this._mouse.x,this._mouse.y,0);r.unproject(this.object),this.object.position.sub(r).add(t),this.object.updateMatrixWorld(),e=Vf.length()}else console.warn(`WARNING: OrbitControls.js encountered an unknown camera type - zoom to cursor disabled.`),this.zoomToCursor=!1;e!==null&&(this.screenSpacePanning?this.target.set(0,0,-1).transformDirection(this.object.matrix).multiplyScalar(e).add(this.object.position):(Rf.origin.copy(this.object.position),Rf.direction.set(0,0,-1).transformDirection(this.object.matrix),Math.abs(this.object.up.dot(Rf.direction))<Bf?this.object.lookAt(this.target):(zf.setFromNormalAndCoplanarPoint(this.object.up,this.target),Rf.intersectPlane(zf,this.target))))}else if(this.object.isOrthographicCamera){let e=this.object.zoom;this.object.zoom=Math.max(this.minZoom,Math.min(this.maxZoom,this.object.zoom/this._scale)),e!==this.object.zoom&&(this.object.updateProjectionMatrix(),i=!0)}return this._scale=1,this._performCursorZoom=!1,i||this._lastPosition.distanceToSquared(this.object.position)>Wf||8*(1-this._lastQuaternion.dot(this.object.quaternion))>Wf||this._lastTargetPosition.distanceToSquared(this.target)>Wf?(this.dispatchEvent(Ff),this._lastPosition.copy(this.object.position),this._lastQuaternion.copy(this.object.quaternion),this._lastTargetPosition.copy(this.target),!0):!1}_getAutoRotationAngle(e){return e===null?Hf/60/60*this.autoRotateSpeed:Hf/60*this.autoRotateSpeed*e}_getZoomScale(e){let t=Math.abs(e*.01);return .95**(this.zoomSpeed*t)}_rotateLeft(e){this._sphericalDelta.theta-=e}_rotateUp(e){this._sphericalDelta.phi-=e}_panLeft(e,t){Vf.setFromMatrixColumn(t,0),Vf.multiplyScalar(-e),this._panOffset.add(Vf)}_panUp(e,t){this.screenSpacePanning===!0?Vf.setFromMatrixColumn(t,1):(Vf.setFromMatrixColumn(t,0),Vf.crossVectors(this.object.up,Vf)),Vf.multiplyScalar(e),this._panOffset.add(Vf)}_pan(e,t){let n=this.domElement;if(this.object.isPerspectiveCamera){let r=this.object.position;Vf.copy(r).sub(this.target);let i=Vf.length();i*=Math.tan(this.object.fov/2*Math.PI/180),this._panLeft(2*e*i/n.clientHeight,this.object.matrix),this._panUp(2*t*i/n.clientHeight,this.object.matrix)}else this.object.isOrthographicCamera?(this._panLeft(e*(this.object.right-this.object.left)/this.object.zoom/n.clientWidth,this.object.matrix),this._panUp(t*(this.object.top-this.object.bottom)/this.object.zoom/n.clientHeight,this.object.matrix)):(console.warn(`WARNING: OrbitControls.js encountered an unknown camera type - pan disabled.`),this.enablePan=!1)}_dollyOut(e){this.object.isPerspectiveCamera||this.object.isOrthographicCamera?this._scale/=e:(console.warn(`WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled.`),this.enableZoom=!1)}_dollyIn(e){this.object.isPerspectiveCamera||this.object.isOrthographicCamera?this._scale*=e:(console.warn(`WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled.`),this.enableZoom=!1)}_updateZoomParameters(e,t){if(!this.zoomToCursor)return;this._performCursorZoom=!0;let n=this.domElement.getBoundingClientRect(),r=e-n.left,i=t-n.top,a=n.width,o=n.height;this._mouse.x=r/a*2-1,this._mouse.y=-(i/o)*2+1,this._dollyDirection.set(this._mouse.x,this._mouse.y,1).unproject(this.object).sub(this.object.position).normalize()}_clampDistance(e){return Math.max(this.minDistance,Math.min(this.maxDistance,e))}_handleMouseDownRotate(e){this._rotateStart.set(e.clientX,e.clientY)}_handleMouseDownDolly(e){this._updateZoomParameters(e.clientX,e.clientX),this._dollyStart.set(e.clientX,e.clientY)}_handleMouseDownPan(e){this._panStart.set(e.clientX,e.clientY)}_handleMouseMoveRotate(e){this._rotateEnd.set(e.clientX,e.clientY),this._rotateDelta.subVectors(this._rotateEnd,this._rotateStart).multiplyScalar(this.rotateSpeed);let t=this.domElement;this._rotateLeft(Hf*this._rotateDelta.x/t.clientHeight),this._rotateUp(Hf*this._rotateDelta.y/t.clientHeight),this._rotateStart.copy(this._rotateEnd),this.update()}_handleMouseMoveDolly(e){this._dollyEnd.set(e.clientX,e.clientY),this._dollyDelta.subVectors(this._dollyEnd,this._dollyStart),this._dollyDelta.y>0?this._dollyOut(this._getZoomScale(this._dollyDelta.y)):this._dollyDelta.y<0&&this._dollyIn(this._getZoomScale(this._dollyDelta.y)),this._dollyStart.copy(this._dollyEnd),this.update()}_handleMouseMovePan(e){this._panEnd.set(e.clientX,e.clientY),this._panDelta.subVectors(this._panEnd,this._panStart).multiplyScalar(this.panSpeed),this._pan(this._panDelta.x,this._panDelta.y),this._panStart.copy(this._panEnd),this.update()}_handleMouseWheel(e){this._updateZoomParameters(e.clientX,e.clientY),e.deltaY<0?this._dollyIn(this._getZoomScale(e.deltaY)):e.deltaY>0&&this._dollyOut(this._getZoomScale(e.deltaY)),this.update()}_handleKeyDown(e){let t=!1;switch(e.code){case this.keys.UP:e.ctrlKey||e.metaKey||e.shiftKey?this.enableRotate&&this._rotateUp(Hf*this.keyRotateSpeed/this.domElement.clientHeight):this.enablePan&&this._pan(0,this.keyPanSpeed),t=!0;break;case this.keys.BOTTOM:e.ctrlKey||e.metaKey||e.shiftKey?this.enableRotate&&this._rotateUp(-Hf*this.keyRotateSpeed/this.domElement.clientHeight):this.enablePan&&this._pan(0,-this.keyPanSpeed),t=!0;break;case this.keys.LEFT:e.ctrlKey||e.metaKey||e.shiftKey?this.enableRotate&&this._rotateLeft(Hf*this.keyRotateSpeed/this.domElement.clientHeight):this.enablePan&&this._pan(this.keyPanSpeed,0),t=!0;break;case this.keys.RIGHT:e.ctrlKey||e.metaKey||e.shiftKey?this.enableRotate&&this._rotateLeft(-Hf*this.keyRotateSpeed/this.domElement.clientHeight):this.enablePan&&this._pan(-this.keyPanSpeed,0),t=!0}t&&(e.preventDefault(),this.update())}_handleTouchStartRotate(e){if(this._pointers.length===1)this._rotateStart.set(e.pageX,e.pageY);else{let t=this._getSecondPointerPosition(e),n=.5*(e.pageX+t.x),r=.5*(e.pageY+t.y);this._rotateStart.set(n,r)}}_handleTouchStartPan(e){if(this._pointers.length===1)this._panStart.set(e.pageX,e.pageY);else{let t=this._getSecondPointerPosition(e),n=.5*(e.pageX+t.x),r=.5*(e.pageY+t.y);this._panStart.set(n,r)}}_handleTouchStartDolly(e){let t=this._getSecondPointerPosition(e),n=e.pageX-t.x,r=e.pageY-t.y,i=Math.sqrt(n*n+r*r);this._dollyStart.set(0,i)}_handleTouchStartDollyPan(e){this.enableZoom&&this._handleTouchStartDolly(e),this.enablePan&&this._handleTouchStartPan(e)}_handleTouchStartDollyRotate(e){this.enableZoom&&this._handleTouchStartDolly(e),this.enableRotate&&this._handleTouchStartRotate(e)}_handleTouchMoveRotate(e){if(this._pointers.length==1)this._rotateEnd.set(e.pageX,e.pageY);else{let t=this._getSecondPointerPosition(e),n=.5*(e.pageX+t.x),r=.5*(e.pageY+t.y);this._rotateEnd.set(n,r)}this._rotateDelta.subVectors(this._rotateEnd,this._rotateStart).multiplyScalar(this.rotateSpeed);let t=this.domElement;this._rotateLeft(Hf*this._rotateDelta.x/t.clientHeight),this._rotateUp(Hf*this._rotateDelta.y/t.clientHeight),this._rotateStart.copy(this._rotateEnd)}_handleTouchMovePan(e){if(this._pointers.length===1)this._panEnd.set(e.pageX,e.pageY);else{let t=this._getSecondPointerPosition(e),n=.5*(e.pageX+t.x),r=.5*(e.pageY+t.y);this._panEnd.set(n,r)}this._panDelta.subVectors(this._panEnd,this._panStart).multiplyScalar(this.panSpeed),this._pan(this._panDelta.x,this._panDelta.y),this._panStart.copy(this._panEnd)}_handleTouchMoveDolly(e){let t=this._getSecondPointerPosition(e),n=e.pageX-t.x,r=e.pageY-t.y,i=Math.sqrt(n*n+r*r);this._dollyEnd.set(0,i),this._dollyDelta.set(0,(this._dollyEnd.y/this._dollyStart.y)**+this.zoomSpeed),this._dollyOut(this._dollyDelta.y),this._dollyStart.copy(this._dollyEnd);let a=(e.pageX+t.x)*.5,o=(e.pageY+t.y)*.5;this._updateZoomParameters(a,o)}_handleTouchMoveDollyPan(e){this.enableZoom&&this._handleTouchMoveDolly(e),this.enablePan&&this._handleTouchMovePan(e)}_handleTouchMoveDollyRotate(e){this.enableZoom&&this._handleTouchMoveDolly(e),this.enableRotate&&this._handleTouchMoveRotate(e)}_addPointer(e){this._pointers.push(e.pointerId)}_removePointer(e){delete this._pointerPositions[e.pointerId];for(let t=0;t<this._pointers.length;t++)if(this._pointers[t]==e.pointerId){this._pointers.splice(t,1);return}}_isTrackingPointer(e){for(let t=0;t<this._pointers.length;t++)if(this._pointers[t]==e.pointerId)return!0;return!1}_trackPointer(e){let t=this._pointerPositions[e.pointerId];t===void 0&&(t=new U,this._pointerPositions[e.pointerId]=t),t.set(e.pageX,e.pageY)}_getSecondPointerPosition(e){let t=e.pointerId===this._pointers[0]?this._pointers[1]:this._pointers[0];return this._pointerPositions[t]}_customWheelEvent(e){let t=e.deltaMode,n={clientX:e.clientX,clientY:e.clientY,deltaY:e.deltaY};switch(t){case 1:n.deltaY*=16;break;case 2:n.deltaY*=100}return e.ctrlKey&&!this._controlActive&&(n.deltaY*=10),n}};function Kf(e){this.enabled!==!1&&(this._pointers.length===0&&(this.domElement.setPointerCapture(e.pointerId),this.domElement.ownerDocument.addEventListener(`pointermove`,this._onPointerMove),this.domElement.ownerDocument.addEventListener(`pointerup`,this._onPointerUp)),!this._isTrackingPointer(e)&&(this._addPointer(e),e.pointerType===`touch`?this._onTouchStart(e):this._onMouseDown(e),this._cursorStyle===`grab`&&(this.domElement.style.cursor=`grabbing`)))}function qf(e){this.enabled!==!1&&(e.pointerType===`touch`?this._onTouchMove(e):this._onMouseMove(e))}function Jf(e){switch(this._removePointer(e),this._pointers.length){case 0:this.domElement.releasePointerCapture(e.pointerId),this.domElement.ownerDocument.removeEventListener(`pointermove`,this._onPointerMove),this.domElement.ownerDocument.removeEventListener(`pointerup`,this._onPointerUp),this.dispatchEvent(Lf),this.state=Uf.NONE,this._cursorStyle===`grab`&&(this.domElement.style.cursor=`grab`);break;case 1:let t=this._pointers[0],n=this._pointerPositions[t];this._onTouchStart({pointerId:t,pageX:n.x,pageY:n.y})}}function Yf(t){let n;switch(t.button){case 0:n=this.mouseButtons.LEFT;break;case 1:n=this.mouseButtons.MIDDLE;break;case 2:n=this.mouseButtons.RIGHT;break;default:n=-1}switch(n){case e.DOLLY:if(this.enableZoom===!1)return;this._handleMouseDownDolly(t),this.state=Uf.DOLLY;break;case e.ROTATE:if(t.ctrlKey||t.metaKey||t.shiftKey){if(this.enablePan===!1)return;this._handleMouseDownPan(t),this.state=Uf.PAN}else{if(this.enableRotate===!1)return;this._handleMouseDownRotate(t),this.state=Uf.ROTATE}break;case e.PAN:if(t.ctrlKey||t.metaKey||t.shiftKey){if(this.enableRotate===!1)return;this._handleMouseDownRotate(t),this.state=Uf.ROTATE}else{if(this.enablePan===!1)return;this._handleMouseDownPan(t),this.state=Uf.PAN}break;default:this.state=Uf.NONE}this.state!==Uf.NONE&&this.dispatchEvent(If)}function Xf(e){switch(this.state){case Uf.ROTATE:if(this.enableRotate===!1)return;this._handleMouseMoveRotate(e);break;case Uf.DOLLY:if(this.enableZoom===!1)return;this._handleMouseMoveDolly(e);break;case Uf.PAN:if(this.enablePan===!1)return;this._handleMouseMovePan(e)}}function Zf(e){this.enabled!==!1&&this.enableZoom!==!1&&this.state===Uf.NONE&&(e.preventDefault(),this.dispatchEvent(If),this._handleMouseWheel(this._customWheelEvent(e)),this.dispatchEvent(Lf))}function Qf(e){this.enabled!==!1&&this._handleKeyDown(e)}function $f(e){switch(this._trackPointer(e),this._pointers.length){case 1:switch(this.touches.ONE){case t.ROTATE:if(this.enableRotate===!1)return;this._handleTouchStartRotate(e),this.state=Uf.TOUCH_ROTATE;break;case t.PAN:if(this.enablePan===!1)return;this._handleTouchStartPan(e),this.state=Uf.TOUCH_PAN;break;default:this.state=Uf.NONE}break;case 2:switch(this.touches.TWO){case t.DOLLY_PAN:if(this.enableZoom===!1&&this.enablePan===!1)return;this._handleTouchStartDollyPan(e),this.state=Uf.TOUCH_DOLLY_PAN;break;case t.DOLLY_ROTATE:if(this.enableZoom===!1&&this.enableRotate===!1)return;this._handleTouchStartDollyRotate(e),this.state=Uf.TOUCH_DOLLY_ROTATE;break;default:this.state=Uf.NONE}break;default:this.state=Uf.NONE}this.state!==Uf.NONE&&this.dispatchEvent(If)}function ep(e){switch(this._trackPointer(e),this.state){case Uf.TOUCH_ROTATE:if(this.enableRotate===!1)return;this._handleTouchMoveRotate(e),this.update();break;case Uf.TOUCH_PAN:if(this.enablePan===!1)return;this._handleTouchMovePan(e),this.update();break;case Uf.TOUCH_DOLLY_PAN:if(this.enableZoom===!1&&this.enablePan===!1)return;this._handleTouchMoveDollyPan(e),this.update();break;case Uf.TOUCH_DOLLY_ROTATE:if(this.enableZoom===!1&&this.enableRotate===!1)return;this._handleTouchMoveDollyRotate(e),this.update();break;default:this.state=Uf.NONE}}function tp(e){this.enabled!==!1&&e.preventDefault()}function np(e){e.key===`Control`&&(this._controlActive=!0,this.domElement.getRootNode().addEventListener(`keyup`,this._interceptControlUp,{passive:!0,capture:!0}))}function rp(e){e.key===`Control`&&(this._controlActive=!1,this.domElement.getRootNode().removeEventListener(`keyup`,this._interceptControlUp,{passive:!0,capture:!0}))}var ip=new Is(-1,1,1,-1,0,1),ap=new class extends Or{constructor(){super(),this.setAttribute(`position`,new _r([-1,3,0,-1,-1,0,3,-1,0],3)),this.setAttribute(`uv`,new _r([0,2,0,0,2,0],2))}},op=class{constructor(e){this._mesh=new ei(ap,e)}dispose(){this._mesh.geometry.dispose()}render(e){e.render(this._mesh,ip)}get material(){return this._mesh.material}set material(e){this._mesh.material=e}},sp={name:`GTAOShader`,defines:{PERSPECTIVE_CAMERA:1,SAMPLES:16,NORMAL_VECTOR_TYPE:1,DEPTH_SWIZZLING:`x`,SCREEN_SPACE_RADIUS:0,SCREEN_SPACE_RADIUS_SCALE:100,SCENE_CLIP_BOX:0},uniforms:{tNormal:{value:null},tDepth:{value:null},tNoise:{value:null},resolution:{value:new U},cameraNear:{value:null},cameraFar:{value:null},cameraProjectionMatrix:{value:new q},cameraProjectionMatrixInverse:{value:new q},cameraWorldMatrix:{value:new q},radius:{value:.25},distanceExponent:{value:1},thickness:{value:1},distanceFallOff:{value:1},scale:{value:1},sceneBoxMin:{value:new W(-1,-1,-1)},sceneBoxMax:{value:new W(1,1,1)}},vertexShader:`

		varying vec2 vUv;

		void main() {
			vUv = uv;
			gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
		}`,fragmentShader:`
		varying vec2 vUv;
		uniform highp sampler2D tNormal;
		uniform highp sampler2D tDepth;
		uniform sampler2D tNoise;
		uniform vec2 resolution;
		uniform float cameraNear;
		uniform float cameraFar;
		uniform mat4 cameraProjectionMatrix;
		uniform mat4 cameraProjectionMatrixInverse;
		uniform mat4 cameraWorldMatrix;
		uniform float radius;
		uniform float distanceExponent;
		uniform float thickness;
		uniform float distanceFallOff;
		uniform float scale;
		#if SCENE_CLIP_BOX == 1
			uniform vec3 sceneBoxMin;
			uniform vec3 sceneBoxMax;
		#endif

		#include <common>
		#include <packing>

		#ifndef FRAGMENT_OUTPUT
		#define FRAGMENT_OUTPUT vec4(vec3(ao), 1.)
		#endif

		vec3 getViewPosition( const in vec2 screenPosition, const in float depth ) {
			#ifdef USE_REVERSED_DEPTH_BUFFER
				vec4 clipSpacePosition = vec4( vec2( screenPosition ) * 2.0 - 1.0, depth, 1.0 );
			#else
				vec4 clipSpacePosition = vec4( vec3( screenPosition, depth ) * 2.0 - 1.0, 1.0 );
			#endif
			vec4 viewSpacePosition = cameraProjectionMatrixInverse * clipSpacePosition;
			return viewSpacePosition.xyz / viewSpacePosition.w;
		}

		float getDepth(const vec2 uv) {
			return textureLod(tDepth, uv.xy, 0.0).DEPTH_SWIZZLING;
		}

		float fetchDepth(const ivec2 uv) {
			return texelFetch(tDepth, uv.xy, 0).DEPTH_SWIZZLING;
		}

		float getViewZ(const in float depth) {
			#if PERSPECTIVE_CAMERA == 1
				return perspectiveDepthToViewZ(depth, cameraNear, cameraFar);
			#else
				return orthographicDepthToViewZ(depth, cameraNear, cameraFar);
			#endif
		}

		vec3 computeNormalFromDepth(const vec2 uv) {
			vec2 size = vec2(textureSize(tDepth, 0));
			ivec2 p = ivec2(uv * size);
			float c0 = fetchDepth(p);
			float l2 = fetchDepth(p - ivec2(2, 0));
			float l1 = fetchDepth(p - ivec2(1, 0));
			float r1 = fetchDepth(p + ivec2(1, 0));
			float r2 = fetchDepth(p + ivec2(2, 0));
			float b2 = fetchDepth(p - ivec2(0, 2));
			float b1 = fetchDepth(p - ivec2(0, 1));
			float t1 = fetchDepth(p + ivec2(0, 1));
			float t2 = fetchDepth(p + ivec2(0, 2));
			float dl = abs((2.0 * l1 - l2) - c0);
			float dr = abs((2.0 * r1 - r2) - c0);
			float db = abs((2.0 * b1 - b2) - c0);
			float dt = abs((2.0 * t1 - t2) - c0);
			vec3 ce = getViewPosition(uv, c0).xyz;
			vec3 dpdx = (dl < dr) ? ce - getViewPosition((uv - vec2(1.0 / size.x, 0.0)), l1).xyz : -ce + getViewPosition((uv + vec2(1.0 / size.x, 0.0)), r1).xyz;
			vec3 dpdy = (db < dt) ? ce - getViewPosition((uv - vec2(0.0, 1.0 / size.y)), b1).xyz : -ce + getViewPosition((uv + vec2(0.0, 1.0 / size.y)), t1).xyz;
			return normalize(cross(dpdx, dpdy));
		}

		vec3 getViewNormal(const vec2 uv) {
			#if NORMAL_VECTOR_TYPE == 2
				return normalize(textureLod(tNormal, uv, 0.).rgb);
			#elif NORMAL_VECTOR_TYPE == 1
				return unpackRGBToNormal(textureLod(tNormal, uv, 0.).rgb);
			#else
				return computeNormalFromDepth(uv);
			#endif
		}

		vec3 getSceneUvAndDepth(vec3 sampleViewPos) {
			vec4 sampleClipPos = cameraProjectionMatrix * vec4(sampleViewPos, 1.);
			vec2 sampleUv = sampleClipPos.xy / sampleClipPos.w * 0.5 + 0.5;
			float sampleSceneDepth = getDepth(sampleUv);
			return vec3(sampleUv, sampleSceneDepth);
		}

		void main() {
			float depth = getDepth(vUv.xy);

			#ifdef USE_REVERSED_DEPTH_BUFFER
				if (depth <= 0.0) {
					discard;
					return;
				}
			#else
				if (depth >= 1.0) {
					discard;
					return;
				}
			#endif
			
			vec3 viewPos = getViewPosition(vUv, depth);
			vec3 viewNormal = getViewNormal(vUv);

			float radiusToUse = radius;
			float distanceFalloffToUse = thickness;
			#if SCREEN_SPACE_RADIUS == 1
				float radiusScale = getViewPosition(vec2(0.5 + float(SCREEN_SPACE_RADIUS_SCALE) / resolution.x, 0.0), depth).x;
				radiusToUse *= radiusScale;
				distanceFalloffToUse *= radiusScale;
			#endif

			#if SCENE_CLIP_BOX == 1
				vec3 worldPos = (cameraWorldMatrix * vec4(viewPos, 1.0)).xyz;
				float boxDistance = length(max(vec3(0.0), max(sceneBoxMin - worldPos, worldPos - sceneBoxMax)));
				if (boxDistance > radiusToUse) {
					discard;
					return;
				}
			#endif

			vec2 noiseResolution = vec2(textureSize(tNoise, 0));
			vec2 noiseUv = vUv * resolution / noiseResolution;
			vec4 noiseTexel = textureLod(tNoise, noiseUv, 0.0);
			vec3 randomVec = noiseTexel.xyz * 2.0 - 1.0;
			vec3 tangent = normalize(vec3(randomVec.xy, 0.));
			vec3 bitangent = vec3(-tangent.y, tangent.x, 0.);
			mat3 kernelMatrix = mat3(tangent, bitangent, vec3(0., 0., 1.));

			const int DIRECTIONS = SAMPLES < 30 ? 3 : 5;
			const int STEPS = (SAMPLES + DIRECTIONS - 1) / DIRECTIONS;
			float ao = 0.0;
			for (int i = 0; i < DIRECTIONS; ++i) {

				float angle = float(i) / float(DIRECTIONS) * PI;
				vec4 sampleDir = vec4(cos(angle), sin(angle), 0., 0.5 + 0.5 * noiseTexel.w);
				sampleDir.xyz = normalize(kernelMatrix * sampleDir.xyz);

				vec3 viewDir = normalize(-viewPos.xyz);
				vec3 sliceBitangent = normalize(cross(sampleDir.xyz, viewDir));
				vec3 sliceTangent = cross(sliceBitangent, viewDir);
				vec3 normalInSlice = normalize(viewNormal - sliceBitangent * dot(viewNormal, sliceBitangent));

				vec3 tangentToNormalInSlice = cross(normalInSlice, sliceBitangent);
				vec2 cosHorizons = vec2(dot(viewDir, tangentToNormalInSlice), dot(viewDir, -tangentToNormalInSlice));

				for (int j = 0; j < STEPS; ++j) {
					vec3 sampleViewOffset = sampleDir.xyz * radiusToUse * sampleDir.w * pow(float(j + 1) / float(STEPS), distanceExponent);

					vec3 sampleSceneUvDepth = getSceneUvAndDepth(viewPos + sampleViewOffset);
					vec3 sampleSceneViewPos = getViewPosition(sampleSceneUvDepth.xy, sampleSceneUvDepth.z);
					vec3 viewDelta = sampleSceneViewPos - viewPos;
					if (abs(viewDelta.z) < thickness) {
						float sampleCosHorizon = dot(viewDir, normalize(viewDelta));
						cosHorizons.x += max(0., (sampleCosHorizon - cosHorizons.x) * mix(1., 2. / float(j + 2), distanceFallOff));
					}

					sampleSceneUvDepth = getSceneUvAndDepth(viewPos - sampleViewOffset);
					sampleSceneViewPos = getViewPosition(sampleSceneUvDepth.xy, sampleSceneUvDepth.z);
					viewDelta = sampleSceneViewPos - viewPos;
					if (abs(viewDelta.z) < thickness) {
						float sampleCosHorizon = dot(viewDir, normalize(viewDelta));
						cosHorizons.y += max(0., (sampleCosHorizon - cosHorizons.y) * mix(1., 2. / float(j + 2), distanceFallOff));
					}
				}

				vec2 sinHorizons = sqrt(1. - cosHorizons * cosHorizons);
				float nx = dot(normalInSlice, sliceTangent);
				float ny = dot(normalInSlice, viewDir);
				float nxb = 1. / 2. * (acos(cosHorizons.y) - acos(cosHorizons.x) + sinHorizons.x * cosHorizons.x - sinHorizons.y * cosHorizons.y);
				float nyb = 1. / 2. * (2. - cosHorizons.x * cosHorizons.x - cosHorizons.y * cosHorizons.y);
				float occlusion = nx * nxb + ny * nyb;
				ao += occlusion;
			}

			ao = clamp(ao / float(DIRECTIONS), 0., 1.);
		#if SCENE_CLIP_BOX == 1
			ao = mix(ao, 1., smoothstep(0., radiusToUse, boxDistance));
		#endif
			ao = pow(ao, scale);

			gl_FragColor = FRAGMENT_OUTPUT;
		}`};function cp(e=5){let t=Math.floor(e)%2==0?Math.floor(e)+1:Math.floor(e),n=lp(t),i=n.length,a=new Uint8Array(i*4);for(let e=0;e<i;++e){let t=n[e],r=2*Math.PI*t/i,o=new W(Math.cos(r),Math.sin(r),0).normalize();a[e*4]=(o.x*.5+.5)*255,a[e*4+1]=(o.y*.5+.5)*255,a[e*4+2]=127,a[e*4+3]=255}let o=new mi(a,t,t);return o.wrapS=r,o.wrapT=r,o.needsUpdate=!0,o}function lp(e){let t=Math.floor(e)%2==0?Math.floor(e)+1:Math.floor(e),n=t*t,r=Array(n).fill(0),i=Math.floor(t/2),a=t-1;for(let e=1;e<=n;){if(i===-1&&a===t?(a=t-2,i=0):(a===t&&(a=0),i<0&&(i=t-1)),r[i*t+a]!==0){a-=2,i++;continue}r[i*t+a]=e++,a++,i--}return r}var up=class{owner;extent;depth;local=new Ai(new W(0,0,-1),10);world=new Ai(new W(0,0,-1),10);local2=new Ai(new W(0,0,-1),10);world2=new Ai(new W(0,0,-1),10);planes=[this.world];uPlane={value:new Jt(0,0,-1,10)};uPlane2={value:new Jt(0,0,0,-1)};wedge=0;uGlow={value:0};uCove={value:new Jt(0,0,0,0)};coveOn=!1;amount=0;materials=new Set;meshes=new Set;capsOn=!0;collect(e){e.traverse(e=>{let t=e;!t.isMesh||Array.isArray(t.material)||t.userData.fluid||this.materials.has(t.material)&&t.material.type!==`ShaderMaterial`&&this.meshes.add(t)});let t=this.capsOn;this.capsOn=!t,this.setCaps(t)}setCaps(e){if(e!==this.capsOn){this.capsOn=e;for(let t of this.materials){if(t.type!==`ShaderMaterial`)continue;let n=t;e?n.defines.CAPS=1:delete n.defines.CAPS,t.userData.caps=e,t.needsUpdate=!0}}this.applyCaps()}setCove(e){this.coveOn=!!e,e?this.uCove.value.set(e.xCut,e.blEnd,1,e.blIn):this.uCove.value.z=0,this.applyCaps()}applyCaps(){for(let e of this.meshes){let t=this.capsOn||this.coveOn&&!!e.userData.cove;if(!!e.userData.capsApplied===t&&e.userData.front)continue;let n=e.userData.front??e.material;e.userData.front=n;let r=e.geometry;if(t){let t=n.userData.makeBack;if(!t)continue;n.userData.back??=t();let i=r.index?r.index.count:r.attributes.position.count;r.clearGroups(),r.addGroup(0,i,0),r.addGroup(0,i,1),e.material=[n,n.userData.back],e.userData.capsApplied=!0}else r.clearGroups(),e.material=n,e.userData.capsApplied=!1}}axis=new W(0,0,-1);constructor(e,t,n=0,r=0,i){this.owner=e,this.extent=t,this.depth=n,i&&this.axis.copy(i).normalize(),this.wedge=r,r>0&&this.planes.push(this.world2)}get intersect(){return this.wedge>0}update(){let e=this.amount;this.setCaps(e>5e-4);let t=e<=0?1e4:this.depth+(this.extent-this.depth)*(1-e);if(this.owner.updateWorldMatrix(!0,!1),this.wedge>0){let e=Math.cos(this.wedge),n=Math.sin(this.wedge);this.local.normal.set(e,0,-n),this.local2.normal.set(-e,0,-n),this.local.constant=t,this.local2.constant=t,this.world2.copy(this.local2).applyMatrix4(this.owner.matrixWorld),this.uPlane2.value.set(this.world2.normal.x,this.world2.normal.y,this.world2.normal.z,this.world2.constant)}else this.local.normal.copy(this.axis);this.wedge<=0&&(this.local.constant=t),this.world.copy(this.local).applyMatrix4(this.owner.matrixWorld),this.uPlane.value.set(this.world.normal.x,this.world.normal.y,this.world.normal.z,this.world.constant),this.uGlow.value=e>.002&&e<.998?Math.sin(Math.PI*e):0}},dp={value:new q},fp={uPlane:{value:new Jt(0,0,-1,1e4)},uPlane2:{value:new Jt(0,0,0,-1)},uGlow:{value:0},uCove:{value:new Jt(0,0,0,0)}},pp=`
uniform vec4 uCutPlane;
uniform vec4 uCutPlane2;
varying vec3 vObj;
varying vec3 vCutObjCam;
varying vec4 vCutPlaneObj;
varying vec4 vCutPlane2Obj;
`,mp=`
{
  vec4 cutP = vec4(transformed, 1.0);
  #ifdef USE_BATCHING
    cutP = batchingMatrix * cutP;
  #endif
  #ifdef USE_INSTANCING
    cutP = instanceMatrix * cutP;
  #endif
  vObj = cutP.xyz;
  vCutObjCam = (inverse(modelMatrix) * vec4(cameraPosition, 1.0)).xyz;
  vCutPlaneObj = uCutPlane * modelMatrix;
  vCutPlane2Obj = uCutPlane2 * modelMatrix;
}
`,hp=`
uniform vec4 uCutPlane;
uniform vec4 uCutPlane2;
uniform mat4 uCutProj;
uniform float uCutGlow;
varying vec3 vObj;
varying vec3 vCutObjCam;
varying vec4 vCutPlaneObj;
varying vec4 vCutPlane2Obj;
// the removed region is where both planes are negative; clip a ray to it
void cutClip(vec4 P, vec3 ro, vec3 rd, inout float t0, inout float t1, inout int exitId, int id) {
  float dn = dot(P.xyz, rd);
  float d0 = dot(P.xyz, ro) + P.w;
  if (abs(dn) < 1e-9) { if (d0 >= 0.0) { t0 = 1.0; t1 = 0.0; } return; }
  float th = -d0 / dn;
  if (dn > 0.0) { if (th < t1) { t1 = th; exitId = id; } }
  else t0 = max(t0, th);
}
bool cutRemoved(vec3 p) {
  return dot(vCutPlaneObj.xyz, p) + vCutPlaneObj.w < 0.0 && dot(vCutPlane2Obj.xyz, p) + vCutPlane2Obj.w < 0.0;
}
`,gp=`
bool cutCap = false;
vec3 cutHit = vObj;
vec3 cutNW = uCutPlane.xyz;
#ifdef CAPS
{
  #ifdef FLIP_SIDED
    bool cutBack = gl_FrontFacing;
  #else
    bool cutBack = !gl_FrontFacing;
  #endif
  if (cutBack) {
    vec3 ro = vCutObjCam;
    vec3 toF = vObj - ro;
    float tf = length(toF);
    vec3 rd = toF / max(tf, 1e-6);
    float t0 = 0.0, t1 = 1e9;
    int exitId = -1;
    cutClip(vCutPlaneObj, ro, rd, t0, t1, exitId, 0);
    cutClip(vCutPlane2Obj, ro, rd, t0, t1, exitId, 1);
    if (exitId >= 0 && t0 < t1 && t1 > 0.0 && t1 < tf) {
      cutCap = true;
      cutHit = ro + rd * t1;
      if (exitId == 1) cutNW = uCutPlane2.xyz;
    }
  }
}
#endif
`;function _p(e=1){let t=e>>>0;return()=>{t=t+1831565813>>>0;let e=t;return e=Math.imul(e^e>>>15,e|1),e^=e+Math.imul(e^e>>>7,e|61),((e^e>>>14)>>>0)/4294967296}}function vp(e=64){let t=_p(7),n=e=>{let n=new Float32Array(e*e*e);for(let e=0;e<n.length;e++)n[e]=t();return n},i=[{p:8,w:.5,l:n(8)},{p:16,w:.25,l:n(16)},{p:32,w:.15,l:n(32)},{p:64,w:.1,l:n(64)}],a=new Uint8Array(e*e*e),o=e=>e*e*(3-2*e);for(let t=0;t<e;t++)for(let n=0;n<e;n++)for(let r=0;r<e;r++){let s=0;for(let a of i){let i=a.p/e,c=r*i,l=n*i,u=t*i,d=Math.floor(c),f=Math.floor(l),p=Math.floor(u),m=o(c-d),h=o(l-f),g=o(u-p),_=a.p,v=(e,t,n)=>a.l[e%_+t%_*_+n%_*_*_],y=d,b=d+1,x=f,S=f+1,C=p,w=p+1,T=v(y,x,C)*(1-m)+v(b,x,C)*m,E=v(y,S,C)*(1-m)+v(b,S,C)*m,D=v(y,x,w)*(1-m)+v(b,x,w)*m,O=v(y,S,w)*(1-m)+v(b,S,w)*m,k=T*(1-h)+E*h,A=D*(1-h)+O*h;s+=(k*(1-g)+A*g)*a.w}a[r+n*e+t*e*e]=Math.max(0,Math.min(255,Math.round(s*255)))}let s=new Qt(a,e,e,e);return s.format=A,s.type=f,s.minFilter=l,s.magFilter=l,s.wrapS=s.wrapT=s.wrapR=r,s.unpackAlignment=1,s.needsUpdate=!0,s}var yp={value:null},bp=`
uniform highp sampler3D uNoise3D;
float n3(vec3 p) { return texture(uNoise3D, p).r; }
float fbm2(vec3 p) { return n3(p) * 0.65 + n3(p * 2.7 + 0.31) * 0.35; }
float hash12(vec2 p) {
  vec3 p3 = fract(vec3(p.xyx) * .1031);
  p3 += dot(p3, p3.yzx + 33.33);
  return fract((p3.x + p3.y) * p3.z);
}
float ign(vec2 px) { return fract(52.9829189 * fract(dot(px, vec2(0.06711056, 0.00583715)))); }
`,xp=`
varying vec2 vUv;
void main() { vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }
`,Sp=`
precision highp float;
varying vec2 vUv;
uniform sampler2D tAO;
uniform sampler2D tDepth;
uniform vec2 uDir;
uniform float uNear, uFar;
float lin(float d) { return (uNear * uFar) / (uFar - d * (uFar - uNear)); }
void main() {
  float d0 = lin(texture2D(tDepth, vUv).x);
  float sum = 0.0, wsum = 0.0;
  for (int i = -4; i <= 4; i++) {
    vec2 uv = vUv + uDir * float(i);
    float a = texture2D(tAO, uv).r;
    float d = lin(texture2D(tDepth, uv).x);
    float w = exp(-float(i * i) / 10.0) * exp(-abs(d - d0) / (0.02 * d0 + 0.002) * 1.5);
    sum += a * w; wsum += w;
  }
  gl_FragColor = vec4(vec3(sum / max(wsum, 1e-4)), 1.0);
}
`,Cp=`
precision highp float;
varying vec2 vUv;
uniform sampler2D tAO;
uniform float uStrength;
void main() {
  float a = texture2D(tAO, vUv).r;
  a = mix(1.0, a, uStrength);
  gl_FragColor = vec4(vec3(a), 1.0);
}
`,wp=`
precision highp float;
${bp}
varying vec2 vUv;
uniform sampler2D tScene;
uniform float uTime;
uniform float uHaze;
uniform vec2 uTexel;
void main() {
  vec3 c = texture2D(tScene, vUv).rgb;
  // never let a stray NaN or inf from a shader bleed through bloom and blur
  if (any(isnan(c)) || any(isinf(c))) c = vec3(0.0);
  gl_FragColor = vec4(min(c, vec3(512.0)), 1.0);
}
`,Tp=`
precision highp float;
varying vec2 vUv;
uniform sampler2D tSrc;
uniform vec2 uTexel;
uniform float uThreshold;
uniform float uKnee;
vec3 prefilter(vec3 c) {
  float br = max(c.r, max(c.g, c.b));
  float rq = clamp(br - uThreshold + uKnee, 0.0, 2.0 * uKnee);
  rq = (rq * rq) / (4.0 * uKnee + 1e-5);
  float w = max(rq, br - uThreshold) / max(br, 1e-5);
  return c * w;
}
void main() {
  vec3 a = texture2D(tSrc, vUv + uTexel * vec2(-1.0, -1.0)).rgb;
  vec3 b = texture2D(tSrc, vUv + uTexel * vec2(1.0, -1.0)).rgb;
  vec3 c = texture2D(tSrc, vUv + uTexel * vec2(-1.0, 1.0)).rgb;
  vec3 d = texture2D(tSrc, vUv + uTexel * vec2(1.0, 1.0)).rgb;
  vec3 col = (a + b + c + d) * 0.25;
  col = min(col, vec3(64.0));
  gl_FragColor = vec4(prefilter(col), 1.0);
}
`,Ep=`
precision highp float;
varying vec2 vUv;
uniform sampler2D tSrc;
uniform vec2 uTexel;
void main() {
  vec2 t = uTexel;
  vec3 A = texture2D(tSrc, vUv + t * vec2(-2.0, 2.0)).rgb;
  vec3 B = texture2D(tSrc, vUv + t * vec2(0.0, 2.0)).rgb;
  vec3 C = texture2D(tSrc, vUv + t * vec2(2.0, 2.0)).rgb;
  vec3 D = texture2D(tSrc, vUv + t * vec2(-2.0, 0.0)).rgb;
  vec3 E = texture2D(tSrc, vUv).rgb;
  vec3 F = texture2D(tSrc, vUv + t * vec2(2.0, 0.0)).rgb;
  vec3 G = texture2D(tSrc, vUv + t * vec2(-2.0, -2.0)).rgb;
  vec3 H = texture2D(tSrc, vUv + t * vec2(0.0, -2.0)).rgb;
  vec3 I = texture2D(tSrc, vUv + t * vec2(2.0, -2.0)).rgb;
  vec3 J = texture2D(tSrc, vUv + t * vec2(-1.0, 1.0)).rgb;
  vec3 K = texture2D(tSrc, vUv + t * vec2(1.0, 1.0)).rgb;
  vec3 L = texture2D(tSrc, vUv + t * vec2(-1.0, -1.0)).rgb;
  vec3 M = texture2D(tSrc, vUv + t * vec2(1.0, -1.0)).rgb;
  vec3 col = E * 0.125 + (A + C + G + I) * 0.03125 + (B + D + F + H) * 0.0625 + (J + K + L + M) * 0.125;
  gl_FragColor = vec4(col, 1.0);
}
`,Dp=`
precision highp float;
varying vec2 vUv;
uniform sampler2D tSrc;
uniform sampler2D tPrev;
uniform vec2 uTexel;
uniform float uRadius;
void main() {
  vec2 t = uTexel * uRadius;
  vec3 s = texture2D(tSrc, vUv + vec2(-t.x, t.y)).rgb
    + texture2D(tSrc, vUv + vec2(0.0, t.y)).rgb * 2.0
    + texture2D(tSrc, vUv + vec2(t.x, t.y)).rgb
    + texture2D(tSrc, vUv + vec2(-t.x, 0.0)).rgb * 2.0
    + texture2D(tSrc, vUv).rgb * 4.0
    + texture2D(tSrc, vUv + vec2(t.x, 0.0)).rgb * 2.0
    + texture2D(tSrc, vUv + vec2(-t.x, -t.y)).rgb
    + texture2D(tSrc, vUv + vec2(0.0, -t.y)).rgb * 2.0
    + texture2D(tSrc, vUv + vec2(t.x, -t.y)).rgb;
  s /= 16.0;
  gl_FragColor = vec4(s + texture2D(tPrev, vUv).rgb, 1.0);
}
`,Op=`
precision highp float;
varying vec2 vUv;
uniform sampler2D tSrc;
uniform sampler2D tDepth;
uniform vec2 uTexel;
uniform float uNear, uFar;
uniform float uFocus;
uniform float uAperture;
uniform float uMaxBlur;
uniform float uTaps;
float lin(float d) { return (uNear * uFar) / (uFar - d * (uFar - uNear)); }
float coc(float z) { return clamp(abs(z - uFocus) / z * uAperture, 0.0, uMaxBlur); }
void main() {
  float z0 = lin(texture2D(tDepth, vUv).x);
  float c0 = coc(z0);
  vec3 base = texture2D(tSrc, vUv).rgb;
  if (c0 < 0.35) { gl_FragColor = vec4(base, 1.0); return; }
  vec3 acc = base;
  float wsum = 1.0;
  const float GA = 2.39996323;
  float r = 0.5;
  for (int i = 0; i < 40; i++) {
    if (float(i) >= uTaps) break;
    float fi = float(i) + 0.5;
    float rad = sqrt(fi / uTaps) * c0;
    vec2 o = vec2(cos(fi * GA), sin(fi * GA)) * rad * uTexel;
    float zs = lin(texture2D(tDepth, vUv + o).x);
    float cs = coc(zs);
    // do not let sharp foreground bleed onto the blurred background
    float w = zs < z0 ? smoothstep(rad - 1.0, rad + 1.0, cs) : 1.0;
    acc += texture2D(tSrc, vUv + o).rgb * w;
    wsum += w;
  }
  gl_FragColor = vec4(acc / wsum, 1.0);
}
`,kp=`
precision highp float;
${bp}
varying vec2 vUv;
uniform sampler2D tSrc;
uniform sampler2D tBloom;
uniform float uBloom;
uniform float uExposure;
uniform float uTime;
uniform float uVignette;
uniform float uGrain;
uniform float uCA;
uniform vec2 uRes;
uniform float uSharpen;
vec3 aces(vec3 x) {
  // ACES fitted (Stephen Hill)
  const mat3 i = mat3(0.59719, 0.07600, 0.02840, 0.35458, 0.90834, 0.13383, 0.04823, 0.01566, 0.83777);
  const mat3 o = mat3(1.60475, -0.10208, -0.00327, -0.53108, 1.10813, -0.07276, -0.07367, -0.00605, 1.07602);
  vec3 v = i * x;
  vec3 a = v * (v + 0.0245786) - 0.000090537;
  vec3 b = v * (0.983729 * v + 0.4329510) + 0.238081;
  return clamp(o * (a / b), 0.0, 1.0);
}
vec3 toSRGB(vec3 c) {
  return mix(c * 12.92, 1.055 * pow(c, vec3(1.0 / 2.4)) - 0.055, step(0.0031308, c));
}
void main() {
  vec2 d = vUv - 0.5;
  float r2 = dot(d, d);
  vec2 ca = d * r2 * uCA;
  vec3 col;
  col.r = texture2D(tSrc, vUv - ca).r;
  col.g = texture2D(tSrc, vUv).g;
  col.b = texture2D(tSrc, vUv + ca).b;
  if (uSharpen > 0.0) {
    vec2 px = 1.0 / uRes;
    vec3 nb = texture2D(tSrc, vUv + vec2(px.x, 0.0)).rgb + texture2D(tSrc, vUv - vec2(px.x, 0.0)).rgb
      + texture2D(tSrc, vUv + vec2(0.0, px.y)).rgb + texture2D(tSrc, vUv - vec2(0.0, px.y)).rgb;
    vec3 blur = nb * 0.25;
    vec3 d = col - blur;
    col = max(col + clamp(d, -0.35 * col - 0.02, 0.35 * col + 0.02) * uSharpen, 0.0);
  }
  col += texture2D(tBloom, vUv).rgb * uBloom;
  col *= uExposure;
  col = aces(col);
  // gentle grade: cool shadows, warm highlights
  float l = dot(col, vec3(0.2126, 0.7152, 0.0722));
  col = mix(col, col * vec3(0.93, 0.98, 1.06), (1.0 - smoothstep(0.0, 0.45, l)) * 0.6);
  col = mix(col, col * vec3(1.04, 1.0, 0.95), smoothstep(0.55, 1.0, l) * 0.5);
  col *= 1.0 - uVignette * smoothstep(0.12, 0.9, r2 * 2.2);
  col = toSRGB(clamp(col, 0.0, 1.0));
  float g = hash12(gl_FragCoord.xy + fract(uTime * 13.7) * 311.0) - 0.5;
  col += g * uGrain;
  col += (hash12(gl_FragCoord.xy * 1.37 + 17.0) - 0.5) / 255.0;
  gl_FragColor = vec4(col, 1.0);
}
`,Ap=class{renderer;w=1;h=1;quad=new op;sceneRT;aoRT;aoTmp;hdrRT;dofRT;bloom=[];bloomUp=[];gtao;aoBlur;aoApply;composite;bloomPre;bloomDown;bloomUpM;dof;final;params={exposure:1.32,bloom:.06,bloomThreshold:.9,bloomRadius:1,vignette:.55,grain:.018,ca:.005,haze:.012,ao:.85,aoRadius:.09,dofFocus:2.5,dofAperture:0,dofMax:14,sharpen:0,dofTaps:24};aoScale=.5;shadowDirty=!0;aoEnabled;bloomEnabled=!0;msaa;constructor(e,t){this.renderer=e,this.aoEnabled=t.ao,this.msaa=t.msaa;let n=(e,t,n=0,r={})=>new Lo({vertexShader:xp,fragmentShader:e,uniforms:t,blending:n,depthTest:!1,depthWrite:!1,...r});this.gtao=new Lo({defines:{...sp.defines,NORMAL_VECTOR_TYPE:0,SAMPLES:t.aoSamples??12},uniforms:Po.clone(sp.uniforms),vertexShader:sp.vertexShader,fragmentShader:sp.fragmentShader,blending:0,depthTest:!1,depthWrite:!1}),this.gtao.uniforms.tNoise.value=cp(),this.aoBlur=n(Sp,{tAO:{value:null},tDepth:{value:null},uDir:{value:new U},uNear:{value:.05},uFar:{value:60}}),this.aoApply=n(Cp,{tAO:{value:null},uStrength:{value:1}},5,{blendSrc:208,blendDst:200,blendEquation:100,blendSrcAlpha:200,blendDstAlpha:201,blendEquationAlpha:100}),this.composite=n(wp,{tScene:{value:null},uTime:{value:0},uHaze:{value:0},uTexel:{value:new U},uNoise3D:yp}),this.bloomPre=n(Tp,{tSrc:{value:null},uTexel:{value:new U},uThreshold:{value:1},uKnee:{value:.5}}),this.bloomDown=n(Ep,{tSrc:{value:null},uTexel:{value:new U}}),this.bloomUpM=n(Dp,{tSrc:{value:null},tPrev:{value:null},uTexel:{value:new U},uRadius:{value:1}}),this.dof=n(Op,{tSrc:{value:null},tDepth:{value:null},uTexel:{value:new U},uNear:{value:.05},uFar:{value:60},uFocus:{value:2},uAperture:{value:0},uMaxBlur:{value:12},uTaps:{value:24}}),this.final=n(kp,{tSrc:{value:null},tBloom:{value:null},uBloom:{value:.05},uExposure:{value:1},uTime:{value:0},uVignette:{value:.5},uGrain:{value:.02},uCA:{value:.01},uRes:{value:new U},uSharpen:{value:0},uNoise3D:yp})}configure(e){this.aoEnabled=e.ao,this.aoScale=e.aoScale,this.msaa=e.msaa,this.bloomEnabled=e.bloom,e.ao&&this.gtao.defines.SAMPLES!==e.aoSamples&&(this.gtao.defines.SAMPLES=e.aoSamples,this.gtao.needsUpdate=!0),(this.w>1||this.h>1)&&this.setSize(this.w,this.h)}setSize(e,t){this.w=e,this.h=t;let n={type:y,minFilter:l,magFilter:l,depthBuffer:!1};this.sceneRT?.dispose();let r=new ia(e,t);r.type=v,this.sceneRT=new Xt(e,t,{type:y,samples:this.msaa,depthTexture:r,depthBuffer:!0}),this.sceneRT.texture.minFilter=l;let i=Math.max(1,Math.round(e*this.aoScale)),a=Math.max(1,Math.round(t*this.aoScale));for(let e of[this.aoRT,this.aoTmp,this.hdrRT,this.dofRT])e?.dispose();this.aoEnabled&&(this.aoRT=new Xt(i,a,n),this.aoTmp=new Xt(i,a,n)),this.hdrRT=new Xt(e,t,n),this.dofRT=new Xt(e,t,n);for(let e of this.bloom)e.dispose();for(let e of this.bloomUp)e.dispose();this.bloom=[],this.bloomUp=[];let o=Math.max(1,Math.round(e/2)),s=Math.max(1,Math.round(t/2));for(let e=0;e<(this.bloomEnabled?7:0);e++)this.bloom.push(new Xt(o,s,n)),this.bloomUp.push(new Xt(o,s,n)),o=Math.max(1,Math.round(o/2)),s=Math.max(1,Math.round(s/2))}pass(e,t){this.quad.material=e,this.renderer.setRenderTarget(t),this.quad.render(this.renderer)}render(e,t,n){let r=this.renderer,i=this.params;if(dp.value.copy(t.projectionMatrix),r.autoClear=!1,this.shadowDirty&&=(r.shadowMap.needsUpdate=!0,!1),r.setRenderTarget(this.sceneRT),r.setClearColor(0,1),r.clear(!0,!0,!0),t.layers.set(0),r.render(e,t),this.aoEnabled&&i.ao>0){let e=this.gtao.uniforms;e.tDepth.value=this.sceneRT.depthTexture,e.resolution.value.set(this.aoRT.width,this.aoRT.height),e.cameraNear.value=t.near,e.cameraFar.value=t.far,e.cameraProjectionMatrix.value.copy(t.projectionMatrix),e.cameraProjectionMatrixInverse.value.copy(t.projectionMatrixInverse),e.cameraWorldMatrix.value.copy(t.matrixWorld),e.radius.value=i.aoRadius,e.distanceExponent.value=1.6,e.thickness.value=1,e.scale.value=1,this.pass(this.gtao,this.aoRT);let n=this.aoBlur.uniforms;n.tDepth.value=this.sceneRT.depthTexture,n.uNear.value=t.near,n.uFar.value=t.far,n.tAO.value=this.aoRT.texture,n.uDir.value.set(1/this.aoRT.width,0),this.pass(this.aoBlur,this.aoTmp),n.tAO.value=this.aoTmp.texture,n.uDir.value.set(0,1/this.aoRT.height),this.pass(this.aoBlur,this.aoRT),this.aoApply.uniforms.tAO.value=this.aoRT.texture,this.aoApply.uniforms.uStrength.value=i.ao,this.pass(this.aoApply,this.sceneRT)}r.setRenderTarget(this.sceneRT),t.layers.disableAll(),t.layers.enable(1),t.layers.enable(2),r.render(e,t),t.layers.set(0);let a=this.bloomEnabled||i.dofAperture>.001,o=this.sceneRT;if(a){let e=this.composite.uniforms;e.tScene.value=this.sceneRT.texture,e.uTime.value=n,e.uHaze.value=i.haze,this.pass(this.composite,this.hdrRT),o=this.hdrRT}if(i.dofAperture>.001){let e=this.dof.uniforms;e.tSrc.value=this.hdrRT.texture,e.tDepth.value=this.sceneRT.depthTexture,e.uTexel.value.set(1/this.w,1/this.h),e.uNear.value=t.near,e.uFar.value=t.far,e.uFocus.value=i.dofFocus,e.uAperture.value=i.dofAperture*(this.h/1080),e.uMaxBlur.value=i.dofMax*(this.h/1080),e.uTaps.value=i.dofTaps,this.pass(this.dof,this.dofRT),o=this.dofRT}let s=o;if(this.bloomEnabled){let e=this.bloomPre.uniforms;e.tSrc.value=o.texture,e.uTexel.value.set(.5/this.w,.5/this.h),e.uThreshold.value=i.bloomThreshold,e.uKnee.value=.6,this.pass(this.bloomPre,this.bloom[0]);for(let e=1;e<this.bloom.length;e++){let t=this.bloomDown.uniforms;t.tSrc.value=this.bloom[e-1].texture,t.uTexel.value.set(1/this.bloom[e-1].width,1/this.bloom[e-1].height),this.pass(this.bloomDown,this.bloom[e])}let t=this.bloom.length;s=this.bloom[t-1];for(let e=t-2;e>=0;e--){let t=this.bloomUpM.uniforms;t.tSrc.value=s.texture,t.tPrev.value=this.bloom[e].texture,t.uTexel.value.set(1/s.width,1/s.height),t.uRadius.value=i.bloomRadius,this.pass(this.bloomUpM,this.bloomUp[e]),s=this.bloomUp[e]}}let c=this.final.uniforms;c.tSrc.value=o.texture,c.tBloom.value=s.texture,c.uBloom.value=this.bloomEnabled?i.bloom:0,c.uExposure.value=i.exposure,c.uTime.value=n,c.uVignette.value=i.vignette,c.uGrain.value=i.grain,c.uCA.value=i.ca,c.uRes.value.set(this.w,this.h),c.uSharpen.value=i.sharpen,this.pass(this.final,null)}},jp={value:0},Mp={value:1080},Np=`
#include <common>
#include <clipping_planes_pars_vertex>
attribute float aS;
attribute float aSide;
attribute float aLen;
attribute vec3 aTan;
uniform float uHalfW;   // half-width, world units (metres)
uniform vec2 uPx;       // min, max half-width in drawing-buffer pixels
uniform float uViewH;
varying float vS;
varying float vX;
varying float vLen;
void main() {
  vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
  vec3 t = normalize((modelViewMatrix * vec4(aTan, 0.0)).xyz);
  vec3 v = normalize(-mvPosition.xyz);
  vec3 side = cross(t, v);
  float sl = length(side);
  side = sl > 1e-4 ? side / sl : vec3(1.0, 0.0, 0.0);
  float px = max(-mvPosition.z, 1e-4) * 2.0 / (projectionMatrix[1][1] * uViewH);   // world size of one pixel at this depth
  float hw = clamp(uHalfW, uPx.x * px, uPx.y * px);
  mvPosition.xyz += side * hw * aSide;
  gl_Position = projectionMatrix * mvPosition;
  #include <clipping_planes_vertex>
  vS = aS;
  vX = aSide;
  vLen = aLen;
}
`,Pp=`
#include <common>
#include <clipping_planes_pars_fragment>
varying float vS;
varying float vX;
varying float vLen;
uniform vec3 uColor;
uniform float uTime, uSpeed, uScale, uEmph, uBase, uRate, uPulse, uCore, uHalo, uHot, uDim;
void main() {
  #include <clipping_planes_fragment>
  float x2 = vX * vX;
  float core = exp(-x2 * 30.0);                               // the hot thread
  float halo = exp(-x2 * 3.2) * (1.0 - x2);                   // the coloured glow around it, zero at the ribbon's edge
  // comet pulses: a sharp bright head leading, a tail fading behind it, so the direction reads in a still
  float f = fract(vS / uScale - uTime * uSpeed * uRate);
  const float HEAD = 0.92;
  float pulse = f < HEAD ? pow(f / HEAD, 4.0) : 1.0 - smoothstep(HEAD, 1.0, f);
  float I = uBase + pulse * uPulse;
  float ends = smoothstep(0.0, 0.6, vS) * smoothstep(0.0, 0.6, vLen - vS);   // the thread fades in and out at its ends (inches)
  vec3 c = uColor * (core * uCore + halo * uHalo) * I + vec3(core * pulse * uHot);
  // premultiplied: the light is added, and the surface under the halo is dimmed by alpha, so the colour stays saturated on a pale laminate
  // the shadow is wider and flatter than the light, so there is a band where the surface is dark and the colour is not yet clipped
  float shade = exp(-x2 * 1.2) * (1.0 - x2 * x2);
  gl_FragColor = vec4(c * uEmph * ends, clamp(uDim * shade * ends * uEmph, 0.0, 1.0));
}
`;function Fp(e,t){let n=new Lo({vertexShader:Np,fragmentShader:Pp,uniforms:{uColor:{value:new J(t.color)},uTime:jp,uSpeed:{value:t.speed??1},uScale:{value:t.scale??.25},uEmph:t.emph,uBase:{value:t.base??.35},uRate:t.rate??{value:1},uPulse:{value:t.pulse??1},uCore:{value:t.core??2},uHalo:{value:t.halo??.5},uHot:{value:t.hot??.3},uDim:{value:t.dim??.4},uHalfW:{value:t.halfWidth??.008},uPx:{value:new U(...t.px??[3,16])},uViewH:Mp},clipping:!0,transparent:!0,depthWrite:!1,depthTest:!1,side:2,blending:5,blendEquation:100,blendSrc:201,blendDst:205});return n.clippingPlanes=e.planes,n.clipIntersection=e.intersect,n}function Ip(e,t=8){let n=new va(e,!1,`centripetal`),r=Math.max(2,(e.length-1)*t+1),i=n.getSpacedPoints(r-1),a=n.getLength(),o=new Float32Array(r*6),s=new Float32Array(r*6),c=new Float32Array(r*2),l=new Float32Array(r*2),u=new Float32Array(r*2),d=new W;for(let e=0;e<r;e++){n.getTangentAt(e/(r-1),d);for(let t=0;t<2;t++){let n=e*2+t;o.set([i[e].x,i[e].y,i[e].z],n*3),s.set([d.x,d.y,d.z],n*3),c[n]=t?1:-1,l[n]=e/(r-1)*a,u[n]=a}}let f=[];for(let e=0;e<r-1;e++){let t=e*2;f.push(t,t+1,t+2,t+1,t+3,t+2)}let p=new Or;return p.setAttribute(`position`,new mr(o,3)),p.setAttribute(`aTan`,new mr(s,3)),p.setAttribute(`aSide`,new mr(c,1)),p.setAttribute(`aS`,new mr(l,1)),p.setAttribute(`aLen`,new mr(u,1)),p.setIndex(f),p}var Lp=`
uniform vec4 uCove;
uniform float uCoveMat;
varying vec3 vCoveX;
varying vec3 vCoveZ;
// keep the part of the ray inside the half space n.p + c > 0; exitId is which space the ray leaves the removed box through
void coveClip(vec3 n, float c, vec3 ro, vec3 rd, inout float t0, inout float t1, inout int exitId, int id) {
  float dn = dot(n, rd);
  float d0 = dot(n, ro) + c;
  if (abs(dn) < 1e-9) { if (d0 <= 0.0) { t0 = 1.0; t1 = 0.0; } return; }
  float th = -d0 / dn;
  if (dn < 0.0) { if (th < t1) { t1 = th; exitId = id; } }
  else t0 = max(t0, th);
}
`,Rp=`
bool coveCap = false;
if (uCoveMat > 0.5 && uCove.z > 0.5) {
  if (vObj.x > uCove.x && abs(vObj.z) < uCove.y && abs(vObj.z) >= uCove.w) discard;
  #ifdef CAPS
  {
    #ifdef FLIP_SIDED
      bool coveBack = gl_FrontFacing;
    #else
      bool coveBack = !gl_FrontFacing;
    #endif
    if (coveBack && !cutCap) {
      vec3 ro = vCutObjCam;
      vec3 toF = vObj - ro;
      float tf = length(toF);
      vec3 rd = toF / max(tf, 1e-6);
      float bt1 = 1e9;
      int exitId = -1;
      // two boxes (z > 0 and z < 0), uCove.w < |z| < uCove.y: the earliest exit of the two
      for (int k = 0; k < 2; k++) {
        float t0 = 0.0, t1 = 1e9;
        int eid = -1;
        coveClip(vec3(1.0, 0.0, 0.0), -uCove.x, ro, rd, t0, t1, eid, 0);
        if (k == 0) {
          coveClip(vec3(0.0, 0.0, 1.0), -uCove.w, ro, rd, t0, t1, eid, 1);
          coveClip(vec3(0.0, 0.0, -1.0), uCove.y, ro, rd, t0, t1, eid, 2);
        } else {
          coveClip(vec3(0.0, 0.0, 1.0), uCove.y, ro, rd, t0, t1, eid, 1);
          coveClip(vec3(0.0, 0.0, -1.0), -uCove.w, ro, rd, t0, t1, eid, 2);
        }
        if (eid >= 0 && t0 < t1 && t1 > 0.0 && t1 < bt1) { bt1 = t1; exitId = eid; }
      }
      float t1 = bt1;
      if (exitId >= 0 && t1 < tf) {
        coveCap = true;
        cutCap = true;
        cutHit = ro + rd * t1;
        // the wall faces into the removed box: +x at the cut, and the two span ends of the box face each other
        cutNW = -normalize(exitId == 0 ? vCoveX : exitId == 1 ? vCoveZ : -vCoveZ);
      }
    }
  }
  #endif
}
`;function zp(e){let t=e.userData.u;t&&(t.uCoveMat.value=1)}function Bp(e){let t=new Vo({depthPacking:He});return t.onBeforeCompile=t=>{t.uniforms.uCove=e.uCove,t.vertexShader=t.vertexShader.replace(`#include <common>`,`#include <common>
varying vec3 vCoveP;`).replace(`#include <project_vertex>`,`#include <project_vertex>
vCoveP = transformed;`),t.fragmentShader=t.fragmentShader.replace(`#include <common>`,`#include <common>
uniform vec4 uCove;
varying vec3 vCoveP;`).replace(`#include <clipping_planes_fragment>`,`#include <clipping_planes_fragment>
if (uCove.z > 0.5 && vCoveP.x > uCove.x && abs(vCoveP.z) < uCove.y && abs(vCoveP.z) >= uCove.w) discard;`)},t.customProgramCacheKey=()=>`cove-depth`,t}var Vp=`
vec3 surfPerturb(vec3 surf_pos, vec3 surf_norm, vec2 dHdxy, float faceDir) {
  vec3 vSigmaX = normalize(dFdx(surf_pos.xyz));
  vec3 vSigmaY = normalize(dFdy(surf_pos.xyz));
  vec3 vN = surf_norm;
  vec3 R1 = cross(vSigmaY, vN);
  vec3 R2 = cross(vN, vSigmaX);
  float fDet = dot(vSigmaX, R1) * faceDir;
  vec3 vGrad = sign(fDet) * (dHdxy.x * R1 + dHdxy.y * R2);
  return normalize(abs(fDet) * surf_norm - vGrad);
}
`,Hp={on:!1},Up=`-0.42, 0.86, 0.29`,Wp=`1.05, 0.9, 0.7`,Gp=`0.5, 0.53, 0.62`,Kp=`0.22, 0.19, 0.16`;function qp(e,t){Hp.on=t;let n=e=>{e&&e.userData.u&&e.defines?.SURF_CHEAP===1!==t&&(e.defines={...e.defines??{}},t?e.defines.SURF_CHEAP=1:delete e.defines.SURF_CHEAP,e.needsUpdate=!0)};e.traverse(e=>{let t=e;if(!t.isMesh)return;let r=Array.isArray(t.material)?t.material:[t.material];for(let e of r)n(e),n(e.userData.back);let i=t.userData.front;n(i),n(i?.userData.back)})}function Jp(e){let t=(e.clearcoat??0)>0||(e.sheen??0)>0||(e.anisotropy??0)>0,n={color:new J(e.color),metalness:e.metalness??1,roughness:e.roughness??.4,envMapIntensity:e.envMapIntensity??1,transparent:e.transparent??!1,opacity:e.opacity??1,flatShading:e.flatShading??!1,vertexColors:e.vertexColors??!1,map:e.map??null,roughnessMap:e.roughnessMap??null},r=t?new Bo({color:new J(e.color),metalness:e.metalness??1,roughness:e.roughness??.4,envMapIntensity:e.envMapIntensity??1,clearcoat:e.clearcoat??0,clearcoatRoughness:e.clearcoatRoughness??.1,anisotropy:e.anisotropy??0,anisotropyRotation:e.anisotropyRotation??0,transparent:e.transparent??!1,opacity:e.opacity??1,flatShading:e.flatShading??!1,vertexColors:e.vertexColors??!1,map:e.map??null,roughnessMap:e.roughnessMap??null,sheen:e.sheen??0,sheenColor:new J(e.sheenColor??16777215)}):new zo(n);e.name&&(r.name=e.name),e.emissive!==void 0&&(r.emissive=new J(e.emissive),r.emissiveIntensity=e.emissiveIntensity??1);let i=e.cut??null,a=!!e.capPass;i?(r.side=+!!a,a&&(r.polygonOffset=!0,r.polygonOffsetFactor=-2,r.polygonOffsetUnits=-2),r.userData.caps=a,r.clippingPlanes=i.planes,r.clipIntersection=i.intersect,r.clipShadows=!0,a||(i.materials.add(r),r.userData.makeBack=()=>Jp({...e,capPass:!0,name:(e.name??`surf`)+`:caps`}))):e.side!==void 0&&(r.side=e.side),Hp.on&&(r.defines={...r.defines??{},SURF_CHEAP:1});let o=e.detail??0,s={uCutPlane:i?i.uPlane:fp.uPlane,uCutPlane2:i?i.uPlane2:fp.uPlane2,uCutGlow:i?i.uGlow:fp.uGlow,uCove:i?i.uCove:fp.uCove,uCoveMat:{value:0},uCutProj:dp,uCapColor:{value:new J(e.capColor??13225169)},uCapRough:{value:e.capRoughness??.42},uCapMetal:{value:e.capMetalness??.35},uDetail:{value:new Jt(o,e.roughVar??.35,e.colorVar??.12,e.bump??0)},uLayers:{value:new U(e.layers?.[0]??0,e.layers?.[1]??0)},uRibs:{value:new U(e.ribs?.[0]??0,e.ribs?.[1]??0)},uStreaks:{value:e.streaks??0},uTintA:{value:new J(e.tint?.a??0)},uTintB:{value:new J(e.tint?.b??0)},uTintC:{value:new J(e.tint?.c??0)},uTintRange:{value:new W(e.tint?.y0??0,e.tint?.y1??1,e.tint?.strength??0)},uNoise3D:yp,uFin:{value:new Jt(0,0,0,0)}},c=e.hooks??{};c.uniforms&&Object.assign(s,c.uniforms),r.userData.u=s;let l=[...(c.defs??[]).map(e=>`#define ${e}`)];i&&l.push(`#define SURF_CUT`),o>0&&l.push(`#define SURF_DETAIL`),e.tint&&l.push(`#define SURF_TINT`),(e.streaks??0)>0&&l.push(`#define SURF_STREAKS`),(c.bump||(e.bump??0)>0||(e.layers?.[1]??0)>0||(e.ribs?.[1]??0)>0)&&l.push(`#define SURF_BUMP`);let u=l.join(`
`)+`
`;return r.onBeforeCompile=e=>{Object.assign(e.uniforms,s);let t=a?`#define CAPS
#define CAP_ONLY
`:``;e.vertexShader=e.vertexShader.replace(`#include <common>`,`#include <common>\n${pp}\nvarying vec3 vCoveX;\nvarying vec3 vCoveZ;`).replace(`#include <project_vertex>`,`#include <project_vertex>\n${mp}\nvCoveX = mat3(modelMatrix) * vec3(1.0, 0.0, 0.0);\nvCoveZ = mat3(modelMatrix) * vec3(0.0, 0.0, 1.0);`);let n=e.fragmentShader;n=n.replace(`#include <common>`,`${u}#ifdef SURF_CHEAP
#undef SURF_DETAIL
#undef SURF_STREAKS
#endif
${t}#include <common>
${hp}
${Lp}
${bp}
${Vp}
uniform vec3 uCapColor; uniform float uCapRough; uniform float uCapMetal;
uniform vec4 uDetail; uniform vec2 uLayers; uniform vec2 uRibs; uniform float uStreaks;
uniform vec3 uTintA; uniform vec3 uTintB; uniform vec3 uTintC; uniform vec3 uTintRange;
uniform vec4 uFin;
${c.pars??``}
`),n=n.replace(`#include <clipping_planes_fragment>`,`#include <clipping_planes_fragment>
#ifdef SURF_CUT
${gp}
${Rp}
#ifdef CAP_ONLY
if (!cutCap) discard;
#endif
#else
bool cutCap = false; vec3 cutHit = vObj; vec3 cutNW = uCutPlane.xyz; bool coveCap = false;
#endif
float surfN1 = 0.5, surfN2 = 0.5, surfH = 0.0;
#ifdef SURF_DETAIL
{
  vec3 dp = vObj * uDetail.x;
  surfN1 = fbm2(dp);
  surfN2 = n3(dp * 3.3 + vec3(7.3, 1.1, 3.7));
  surfH = (surfN1 - 0.5) * uDetail.w;
  #ifdef SURF_STREAKS
    float st = n3(vec3(vObj.x * uDetail.x * 2.2, vObj.y * uDetail.x * 0.18, vObj.z * uDetail.x * 2.2));
    surfN1 = mix(surfN1, st, 0.55);
  #endif
}
#endif
if (uLayers.y > 0.0) surfH += sin(vObj.y * uLayers.x) * uLayers.y;
if (uRibs.y > 0.0) surfH += smoothstep(-0.2, 0.9, sin(atan(vObj.z, vObj.x) * uRibs.x)) * uRibs.y;
${c.surface??``}
`),n=n.replace(`#include <color_fragment>`,`#include <color_fragment>
#ifdef SURF_DETAIL
  diffuseColor.rgb *= 1.0 + (surfN1 - 0.5) * uDetail.z * 2.0;
#endif
#ifdef SURF_TINT
{
  float ty = clamp((vObj.y - uTintRange.x) / (uTintRange.y - uTintRange.x), 0.0, 1.0);
  ty = clamp(ty + (surfN2 - 0.5) * 0.18, 0.0, 1.0);
  vec3 tc = ty < 0.5 ? mix(uTintA, uTintB, ty * 2.0) : mix(uTintB, uTintC, ty * 2.0 - 1.0);
  diffuseColor.rgb = mix(diffuseColor.rgb, tc, uTintRange.z);
}
#endif
#ifdef SURF_STREAKS
  diffuseColor.rgb *= 1.0 - uStreaks * smoothstep(0.45, 0.8, surfN1);
#endif
${c.color??``}
if (!cutCap && uFin.w > 0.0) diffuseColor.rgb = mix(diffuseColor.rgb, uFin.rgb * (0.95 + 0.1 * surfN1), uFin.w);
if (cutCap) diffuseColor.rgb = uCapColor;
${c.capColor??``}
if (coveCap) {
  float hs = (cutHit.x + cutHit.y - cutHit.z) / 1.6;
  float tri = abs(fract(hs) - 0.5) * 2.0;
  float aa = clamp(fwidth(hs) * 2.0, 1e-4, 0.5);
  diffuseColor.rgb = mix(diffuseColor.rgb, vec3(0.80, 0.40, 0.08), 0.7 * smoothstep(0.52 - aa, 0.52 + aa, tri) * (1.0 - 0.6 * aa * 2.0));
}
`),n=n.replace(`#include <metalnessmap_fragment>`,`#include <metalnessmap_fragment>
#ifdef SURF_DETAIL
  roughnessFactor = clamp(roughnessFactor * (1.0 + (surfN2 - 0.5) * uDetail.y * 2.0), 0.03, 1.0);
#endif
${c.rough??``}
if (!cutCap && uFin.w > 0.0) roughnessFactor = mix(roughnessFactor, 0.55, uFin.w);
if (cutCap) {
  roughnessFactor = uCapRough + (n3(cutHit * 9.0) - 0.5) * 0.08;
  metalnessFactor = uCapMetal;
}
${c.capRough??``}
`),n=n.replace(`#include <normal_fragment_maps>`,`#include <normal_fragment_maps>
#if defined(SURF_BUMP) && !defined(SURF_CHEAP)
  if (!cutCap) normal = surfPerturb(-vViewPosition, normal, vec2(dFdx(surfH), dFdy(surfH)), faceDirection);
#endif
{
  // specular anti-aliasing: widen the lobe where the normal changes quickly across a pixel
  vec3 dn = fwidth(normal);
  float variance = dot(dn, dn);
  roughnessFactor = sqrt(clamp(roughnessFactor * roughnessFactor + min(variance * 0.6, 0.16), 0.0, 1.0));
}
if (cutCap) {
  normal = normalize((viewMatrix * vec4(-cutNW, 0.0)).xyz);
  nonPerturbedNormal = normal;
}
`),n=n.replace(`#include <emissivemap_fragment>`,`#include <emissivemap_fragment>
#if defined(SURF_CUT) && !defined(CAP_ONLY)
if (uCutGlow > 0.0) {
  float cdw = dot(vCutPlaneObj.xyz, vObj) + vCutPlaneObj.w;
  float cdw2 = dot(vCutPlane2Obj.xyz, vObj) + vCutPlane2Obj.w;
  float cde = uCutPlane2.w < 0.0 && dot(uCutPlane2.xyz, uCutPlane2.xyz) < 0.5 ? abs(cdw) : max(cdw, cdw2) < 0.0 ? 1.0 : min(abs(cdw), abs(cdw2));
  totalEmissiveRadiance += vec3(0.45, 0.85, 1.0) * exp(-cde * 900.0) * uCutGlow * 14.0;
}
#endif
`),n=n.replace(`#include <lights_fragment_begin>`,`#ifdef SURF_CHEAP
vec3 geometryViewDir = normalize(vViewPosition);
vec3 geometryClearcoatNormal = vec3(0.0);
{
  float cheapUp = dot(normal, normalize((viewMatrix * vec4(0.0, 1.0, 0.0, 0.0)).xyz)) * 0.5 + 0.5;
  float cheapNL = max(dot(normal, normalize((viewMatrix * vec4(${Up}, 0.0)).xyz)), 0.0);
  reflectedLight.indirectDiffuse += material.diffuseColor * mix(vec3(${Kp}), vec3(${Gp}), cheapUp);
  reflectedLight.directDiffuse += material.diffuseColor * vec3(${Wp}) * cheapNL;
}
#else
#include <lights_fragment_begin>
#endif`),n=n.replace(`#include <lights_fragment_maps>`,`#ifndef SURF_CHEAP
#include <lights_fragment_maps>
#endif`),n=n.replace(`#include <lights_fragment_end>`,`#ifndef SURF_CHEAP
#include <lights_fragment_end>
#endif`),c.lights&&(n=n.replace(`#include <lights_physical_fragment>`,`#include <lights_physical_fragment>\n${c.lights}`)),e.fragmentShader=n},r.customProgramCacheKey=()=>`surf|`+u+(c.pars?c.pars.length:``)+(a?`caps`:``),r}function Yp(e,t=.8,n={}){return Jp({color:e,metalness:0,roughness:t,detail:n.detail??0,...n})}function Xp(e,t,n,r=0){return{xCut:e-t,blEnd:n,blIn:r}}var Zp=`
if (uHatch > 0.5) {
  vec3 hp = cutCap ? cutHit : vObj;
  float hs = (hp.x + hp.y - hp.z) / 1.6;
  float tri = abs(fract(hs) - 0.5) * 2.0;
  float aa = clamp(fwidth(hs) * 2.0, 1e-4, 0.5);
  float hedge = mix(0.52, 0.8, cutCap ? 0.0 : clamp(uHatch - 1.0, 0.0, 1.0));
  float stripe = smoothstep(hedge - aa, hedge + aa, tri);
  diffuseColor.rgb = mix(diffuseColor.rgb, vec3(0.80, 0.40, 0.08), 0.7 * stripe * (1.0 - 0.6 * aa * 2.0));
}`,Qp=13395476,$p=`uniform float uGhost;
uniform float uFollow;
uniform float uHatch;`,em={value:0},tm=`
{ float fl = dot(diffuseColor.rgb, vec3(0.299, 0.587, 0.114)); diffuseColor.rgb = mix(diffuseColor.rgb, vec3(fl), (cutCap ? 0.1 : 0.45) * uFollow) * (1.0 - uFollow * (cutCap ? 0.1 : 0.5)); }`+Zp,nm=`{ float gl = dot(diffuseColor.rgb, vec3(0.299, 0.587, 0.114)); diffuseColor.rgb = mix(diffuseColor.rgb, vec3(gl), 0.75 * uGhost); }`,rm=$p+`
uniform float uWet;
uniform vec3 uPly;       // x: coordinate (along uAxis) of the ply's root end, y: 1 / span length (per inch), z: ply thickness (in)
uniform vec3 uAxis;      // the axis the ply unrolls along, from its root end; (0, 0, 1) for the canard (model Z)
uniform vec2 uLay;       // x: unrolled fraction of the span (from the root), y: wet-out front, as a fraction of the span
uniform float uWeb;      // 1 when the ply lies in the model Y-Z plane (shear web), 0 when it lies in X-Z (skins, caps), 2 in X-Y
uniform vec2 uAng;       // cos, sin of the first tow direction, measured from the span axis in the ply's plane
uniform vec4 uWv;        // x: weave period or foam cells per inch, y: relief in inches, z: UND stitch spacing (in), w: ply order in its op
uniform float uDryTone;  // the dry cloth's brightness, 1 as it always was; the fuselage lowers it where a pose faces the cloth into the light
vec3 h33(vec3 p) {
  p = fract(p * vec3(0.1031, 0.1030, 0.0973));
  p += dot(p, p.yxz + 33.33);
  return fract((p.xxy + p.yxx) * p.zyx);
}
float h11(float p) { p = fract(p * 0.1031); p *= p + 33.33; p *= p + p; return fract(p); }
// 3D Worley: x = distance to the nearest feature point, y = to the second nearest, z = random id of the nearest cell.
vec3 worley(vec3 p) {
  vec3 ip = floor(p), fp = fract(p);
  float f1 = 8.0, f2 = 8.0, id = 0.0;
  for (int k = -1; k <= 1; k++) for (int j = -1; j <= 1; j++) for (int i = -1; i <= 1; i++) {
    vec3 g = vec3(float(i), float(j), float(k));
    vec3 o = h33(ip + g);
    vec3 r = g + o - fp;
    float d = dot(r, r);
    if (d < f1) { f2 = f1; f1 = d; id = o.x; } else if (d < f2) f2 = d;
  }
  return vec3(sqrt(f1), sqrt(f2), id);
}
float towProfile(float f) { return pow(sin(3.14159265 * clamp(f, 0.0, 1.0)), 0.9); }
`,im=`
if (cutCap && uGhost > 0.5) discard;   // future work drawn as a ghost is not cut open: no cap
float cmpShade = 1.0, cmpRough = 0.0;
float cmpWetK = 1.0, cmpEdge = 0.0;   // wetness ahead of / at the wet-out front (1 = behind the front, or nothing is being laid)
#if defined(COMP_UND) || defined(COMP_BID)
{
  // Position along the span, 0 at the root end and 1 at the tip. A cut face is measured where the plane opens the ply.
  float sp = (uPly.x - dot(cutCap ? cutHit : vObj, uAxis)) * uPly.y;
  if (uLay.x < 1.0 && sp > uLay.x) discard;   // not unrolled yet
  if (uLay.y < 1.0) {
    // The wet-out front is a soft band about 1.1 in wide, so the front moves from fully dry (uLay.y = 0) to fully wet (1).
    float bw = 0.55 * uPly.y;
    float fr = uLay.y * (1.0 + 2.0 * bw) - bw;
    cmpWetK = 1.0 - smoothstep(fr - bw, fr + bw, sp);
    float ed = (sp - fr) / bw;
    cmpEdge = exp(-ed * ed) * step(0.001, uLay.y);
  }
}
#endif
float cmpWet = uWet * cmpWetK;
float cmpFp = max(max(length(dFdx(vObj)), length(dFdy(vObj))), 1e-5);
float cmpOn = cutCap ? 0.0 : 1.0;
vec3 capW = vec3(0.5, 0.5, 0.5);
float capFade = 1.0;
#if defined(COMP_FOAM)
{
  float cyc = cmpFp * uWv.x;
  float fade = (1.0 - smoothstep(0.18, 0.5, cyc)) * cmpOn;
  #ifdef SURF_CHEAP
  fade = 0.0; // low tier: the foam skin is its albedo only, no Worley cells
  #endif
  if (fade > 0.01) {
    vec3 w = worley(vObj * uWv.x);
    float wall = 1.0 - smoothstep(0.0, 0.2, w.y - w.x);
    cmpShade = 1.0 - fade * (0.16 * wall + 0.1 * (w.z - 0.5));
    cmpRough = fade * (0.1 * wall + 0.12 * (w.z - 0.5));
    surfH += fade * uWv.y * (1.0 - smoothstep(0.0, 0.65, w.x)) / cmpFp;
  }
  #ifndef SURF_CHEAP
  if (cutCap) {
    // the cut face shows finer cells than the skin's relief, the way a clean machined foam face looks
    capW = worley(cutHit * uWv.x * 2.5);
    capFade = 1.0 - smoothstep(0.2, 0.5, max(length(dFdx(cutHit)), length(dFdy(cutHit))) * uWv.x * 2.5);
  }
  #else
  capFade = 0.0;
  #endif
}
#elif defined(COMP_UND) || defined(COMP_BID)
#ifdef SURF_CHEAP
capFade = 0.0; // low tier: albedo only, no weave relief or tow shading; the cut face keeps its ply lines but drops the fibre dots
#else
{
  vec2 q = uWeb > 1.5 ? vObj.xy : uWeb > 0.5 ? vObj.zy : vObj.zx;
  float A = dot(q, uAng);                    // along the first tow direction
  float B = dot(q, vec2(-uAng.y, uAng.x));   // across it
  float P = uWv.x;
  float cyc = max(fwidth(A), fwidth(B)) / P;
  float fade = (1.0 - smoothstep(0.2, 0.5, cyc)) * cmpOn;
  float soften = 1.0 - 0.6 * cmpWet;           // flooded with resin: the weave relaxes
  #if defined(COMP_UND)
  {
    float ci = floor(B / P), cf = fract(B / P);
    float prof = towProfile(cf);
    float tv = h11(ci + 3.0);
    float fineF = B / (P * 0.14);
    float fine = h11(floor(fineF) + ci * 17.0);
    float fineFade = 1.0 - smoothstep(0.16, 0.42, cyc / 0.14);
    // wider bands of tows (about 1 in) carry a slight tone difference, so the direction still reads when single tows are too small
    float grp = h11(floor(B / (P * 5.0)) + 91.0);
    float grpFade = (1.0 - smoothstep(0.2, 0.5, cyc / 5.0)) * cmpOn;
    float sp = uWv.z;
    float sf = abs(fract(A / sp) * 2.0 - 1.0);
    float sw = 0.045 / sp;                   // stitch thread is ~0.045 in wide
    float band = smoothstep(1.0 - sw * 2.0, 1.0, sf);
    float bandFade = (1.0 - smoothstep(0.3, 0.8, fwidth(A) / 0.045)) * (0.35 + 0.65 * h11(ci + floor(A / sp) * 13.0));
    surfH += (fade * prof * uWv.y * soften - fade * bandFade * band * uWv.y * 0.35 * soften) / cmpFp;
    cmpShade = 1.0 + fade * (-0.14 * (1.0 - prof) * soften + (tv - 0.5) * 0.24 * soften + (fine - 0.5) * 0.16 * fineFade) - bandFade * band * 0.14 + (grp - 0.5) * 0.14 * grpFade * soften;
    cmpRough = fade * (-0.08 * prof + 0.06 * (tv - 0.5));
  }
  #else
  {
    vec2 c = vec2(A, B) / P;
    vec2 ic = floor(c), fc = fract(c);
    float par = mod(ic.x + ic.y, 2.0);
    float warpTop = par < 0.5 ? 1.0 : 0.0;   // warp (running along A) is over where the checker is even, weft elsewhere
    float wp = towProfile(fc.y), wa = pow(sin(3.14159265 * fc.x), 0.4);   // both go to zero at the cell border, so the relief has no jump
    float fw = towProfile(fc.x), fa = pow(sin(3.14159265 * fc.y), 0.4);
    float hh = mix(fw * fa, wp * wa, warpTop);
    float gap = mix(fw, wp, warpTop);
    float tv = h11(mix(ic.x, ic.y, warpTop) * 1.7 + warpTop * 31.0);
    surfH += fade * hh * uWv.y * soften / cmpFp;
    float fineB = h11(floor(mix(c.x, c.y, warpTop) * 9.0) + mix(ic.y, ic.x, warpTop) * 31.0 + warpTop * 7.0);
    float fineFade = 1.0 - smoothstep(0.16, 0.42, cyc * 9.0);
    cmpShade = 1.0 + fade * (-0.1 * (1.0 - gap) * soften + (tv - 0.5) * 0.18 * soften + (warpTop - 0.5) * 0.07 + (fineB - 0.5) * 0.14 * fineFade);
    cmpRough = fade * (-0.07 * hh + 0.05 * (tv - 0.5));
  }
  #endif
  if (cutCap) {
    capW = worley(cutHit * 26.0);
    capFade = 1.0 - smoothstep(0.16, 0.42, max(length(dFdx(cutHit)), length(dFdy(cutHit))) * 26.0);
  }
}
#endif
#endif
`,am=`
diffuseColor.rgb *= cmpShade;
// wet resin: darker and less saturated (the cloth goes translucent), with epoxy's faint amber cast
vec3 cmpWc = mix(vec3(dot(diffuseColor.rgb, vec3(0.3, 0.59, 0.11))), diffuseColor.rgb, 0.55) * vec3(0.8, 0.77, 0.66);
diffuseColor.rgb = mix(diffuseColor.rgb, cmpWc, cmpWet);
diffuseColor.rgb = mix(diffuseColor.rgb, vec3(0.89, 0.89, 0.86) * uDryTone * (0.5 + 0.5 * cmpShade), (1.0 - cmpWetK) * 0.94);
`+nm,om=`
#ifdef USE_CLEARCOAT
material.clearcoat = clamp(material.clearcoat * cmpWetK + cmpEdge * 0.55 * uWet, 0.0, 1.0);
material.clearcoatRoughness = mix(material.clearcoatRoughness, 0.12, cmpEdge);
#endif
`,sm={defs:[`COMP_FOAM`],pars:rm,surface:im,color:`diffuseColor.rgb *= cmpShade;
`+nm,rough:`roughnessFactor = clamp(roughnessFactor + cmpRough, 0.05, 1.0);`,capColor:`if (cutCap) { float wall = 1.0 - smoothstep(0.0, 0.12, capW.y - capW.x); diffuseColor.rgb = uCapColor * (1.0 - capFade * (0.13 * wall + (0.5 - capW.z) * 0.05)); }`+tm,capRough:`if (cutCap) roughnessFactor = clamp(0.9 + (capW.z - 0.5) * 0.06, 0.05, 1.0);`,bump:!0},cm=e=>({defs:[e],pars:rm,surface:im,color:am,lights:om,rough:`roughnessFactor = clamp(roughnessFactor + cmpRough - cmpWet * 0.12 + (1.0 - cmpWetK) * 0.38, 0.05, 1.0);`,capColor:`if (cutCap) {
    float dots = 1.0 - smoothstep(0.12, 0.4, capW.x);
    diffuseColor.rgb = uCapColor * mix(1.0, 0.8 + 0.5 * dots + (capW.z - 0.5) * 0.15, capFade);
    vec3 cgn = normalize(cross(dFdx(vObj), dFdy(vObj)));
    float chd = length(vObj - cutHit) * abs(dot(normalize(vObj - vCutObjCam), cgn));
    float cline = 1.0 - smoothstep(0.0, uPly.z * 0.16, chd);
    diffuseColor.rgb *= mix(1.0, 0.52, cline * step(chd, uPly.z * 1.3)) * (mod(uWv.w, 2.0) > 0.5 ? 0.9 : 1.0);
  }`+tm,capRough:`if (cutCap) roughnessFactor = clamp(0.5 + (capW.z - 0.5) * 0.12, 0.05, 1.0);`,bump:!0}),lm={foam:14078144,foamCap:16183518,und:11046738,undCap:11769425,bid:7311225,bidCap:7315334,flox:9202244,micro:14470308};function um(e){let t=e.attributes.position,n=e.index,r=n?n.count:t.count,i=new W,a=new W,o=new W,s=new W,c=new W,l=0,u=0;for(let e=0;e<r;e+=3){let r=n?n.getX(e):e,d=n?n.getX(e+1):e+1,f=n?n.getX(e+2):e+2;i.fromBufferAttribute(t,r),a.fromBufferAttribute(t,d),o.fromBufferAttribute(t,f),s.subVectors(a,i),c.subVectors(o,i);let p=s.cross(c);l+=Math.abs(p.x),u+=Math.abs(p.y)}return+(l>u)}function dm(e){e.computeBoundingBox();let t=e.boundingBox;return{rootZ:t.max.z,len:t.max.z-t.min.z}}function fm(e){let t=e.attributes.position,n=e.index,r=n?n.count:t.count,i=new W,a=new W,o=new W,s=new W,c=new W,l=[0,0,0];for(let e=0;e<r;e+=3){let r=n?n.getX(e):e,u=n?n.getX(e+1):e+1,d=n?n.getX(e+2):e+2;i.fromBufferAttribute(t,r),a.fromBufferAttribute(t,u),o.fromBufferAttribute(t,d),s.subVectors(a,i),c.subVectors(o,i);let f=s.cross(c);l[0]+=Math.abs(f.x),l[1]+=Math.abs(f.y),l[2]+=Math.abs(f.z)}let u=l[0]>=l[1]&&l[0]>=l[2]?0:l[1]>=l[2]?1:2;e.computeBoundingBox();let d=e.boundingBox,f=[d.max.x-d.min.x,d.max.y-d.min.y,d.max.z-d.min.z],[p,m]=[0,1,2].filter(e=>e!==u),h=f[p]>=f[m]?p:m,g=u===0?1:u===1?0:2;return h===2?{web:g,axis:new W(0,0,1),span:{rootZ:d.max.z,len:f[2]}}:{web:g,axis:h===0?new W(-1,0,0):new W(0,-1,0),span:{rootZ:h===0?-d.min.x:-d.min.y,len:f[h]}}}var pm=(e,t=0)=>e?1+At.clamp(t,0,1):0;function mm(e,t,n=0,r={rootZ:0,len:1},i={}){let a={value:pm(i.hatch,i.hatchSoft)},o={value:(i.axis??new W(0,0,1)).clone()},s={metalness:0,cut:t,detail:0},c;if(e.kind===`foam`)c=Jp({...s,name:`foam`,color:lm.foam,roughness:.86,capColor:lm.foamCap,capRoughness:.88,capMetalness:0,hooks:{...sm,uniforms:{uDryTone:i.dryTone??{value:1},uWet:{value:0},uGhost:{value:0},uFollow:em,uHatch:a,uAxis:o,uWeb:{value:0},uAng:{value:new U(1,0)},uWv:{value:new Jt(6,.015,1,0)}}}});else if(e.kind===`und`||e.kind===`bid`){let t=e.kind===`und`,l=At.degToRad(e.angles[0]??0);c=Jp({...s,name:e.ply?.node??e.kind,color:t?lm.und:lm.bid,roughness:.42,capColor:t?lm.undCap:lm.bidCap,capRoughness:.5,capMetalness:0,clearcoat:.12,clearcoatRoughness:.45,hooks:{...cm(t?`COMP_UND`:`COMP_BID`),uniforms:{uDryTone:i.dryTone??{value:1},uWet:{value:0},uGhost:{value:0},uFollow:em,uHatch:a,uAxis:o,uPly:{value:new W(r.rootZ,1/Math.max(r.len,.001),t?.009:.013)},uLay:{value:new U(1,1)},uWeb:{value:n},uAng:{value:new U(Math.cos(l),Math.sin(l))},uWv:{value:new Jt(t?.24:.18,t?.012:.008,1,e.ply?.order??0)}}}})}else throw Error(`compositeMaterial: "${e.kind}" is not a composite kind`);return c.userData.comp={kind:e.kind,angles:e.angles.slice(),wet:0},c.userData.hatch=!!i.hatch,c}function hm(e,t){let n=e.userData.comp;if(!n||n.kind===`foam`)return;let r=At.clamp(t,0,1);n.wet=r;let i=e.userData.u;i.uWet.value=r;let a=e;a.clearcoat=.12+.88*r,a.clearcoatRoughness=.45-.41*r,a.roughness=.42-.17*r;let o=e.userData.back;o&&(o.userData.u.uWet.value=r)}function gm(e,t){if(!e.userData.u)return;hm(e,1-t.cure);let n=e=>{let n=e.userData.u;n.uGhost.value=+!!t.ghost,n.uLay&&n.uLay.value.set(t.unroll,t.front);let r=e.userData.glass;if(r!==void 0){e.opacity=t.ghost?r*.35:r;return}e.transparent!==t.ghost&&(e.transparent=t.ghost,e.needsUpdate=!0),e.opacity=t.ghost?.2:1,e.depthWrite=!t.ghost};n(e);let r=e.userData.back;r&&n(r)}function _m(e,t){let n=e.color;if(!n)return;let r=e.userData.baseColor??=n.clone();n.copy(r).multiplyScalar(t)}function vm(e,t={}){let n=t.color??15130575,r=Jp({name:t.name??`part`,color:n,roughness:t.roughness??.85,metalness:t.metalness??0,detail:1.2,colorVar:.06,roughVar:.2,cut:e,capColor:n,hooks:{pars:$p,surface:`if (cutCap && uGhost > 0.5) discard;`,color:nm,capColor:tm,uniforms:{uGhost:{value:0},uFollow:em,uHatch:{value:pm(t.hatch,t.hatchSoft)}}}});return r.userData.hatch=!!t.hatch,r}function ym(e,t){switch(e){case`spanwise`:return 0;case`45 degrees`:return 45;case`crossed`:return t%2==1?45:-45;default:throw Error(`unknown ply orientation "${e}"`)}}function bm(e,t,n){if(!e)return t===`canard.core`?{kind:`foam`,angles:[]}:{kind:`part`,angles:[]};let r=n?.[e];if(!r)throw Error(`ply ${e} is not in the layup`);let i=r.order??0,a=ym(r.orientation??``,i);if(r.cloth===`UND`)return{kind:`und`,angles:[a],ply:{node:e,order:i,cloth:`UND`}};if(r.cloth===`BID`)return{kind:`bid`,angles:[a,a-90],ply:{node:e,order:i,cloth:`BID`}};throw Error(`unknown cloth "${r.cloth}" on ${e}`)}var xm=e=>[{key:`room.back`,n:[-1,0,0],d:-e.x1},{key:`room.door`,n:[1,0,0],d:e.x0},{key:`room.window`,n:[0,0,1],d:e.z0},{key:`room.side`,n:[0,0,-1],d:-e.z1},{key:`room.ceiling`,n:[0,-1,0],d:-e.h}],Sm=(e,t)=>e.n[0]*t[0]+e.n[1]*t[1]+e.n[2]*t[2]-e.d;function Cm(e,t,n=.05){return new Set(t.filter(t=>Sm(t,e)<n).map(e=>e.key))}function wm(e,t,n,r){return n.filter(n=>!r.has(n.key)&&Sm(n,e)*Sm(n,t)<0).map(e=>e.key)}var Tm=.9,Em={x0:-6.6,x1:2.9,z0:-4.2,z1:4.2,h:3.3},Dm=[-2.2,0,2.2].flatMap(e=>[-.5,1.3].map(t=>({x:t,z:e}))),Om=Em.h-.12,km=1.3,Am={z:Em.z0,x:.4,y:1.85,w:2.4,h:1.4},jm=class{mats;m=new Map;plane=``;constructor(e){this.mats=e}add(e,t,n=0,r=0,i=0,a=0,o=0,s=0){t.applyMatrix4(new q().compose(new W(n,r,i),new jt().setFromEuler(new ln(a,o,s)),new W(1,1,1)));let c=t.index?t.toNonIndexed():t;for(let e of Object.keys(c.attributes))e!==`position`&&e!==`normal`&&e!==`uv`&&c.deleteAttribute(e);let l=`${this.plane}|${e}`;this.m.has(l)||this.m.set(l,{key:e,plane:this.plane,mat:this.mats[e],geos:[]}),this.m.get(l).geos.push(c)}box(e,t,n,r,i,a,o,s=0){this.add(e,new sa(t,n,r),i,a,o,0,s,0)}cyl(e,t,n,r,i,a,o,s=16){this.add(e,new ca(t,t,n,s),i,a,o,r===`z`?Math.PI/2:0,0,r===`x`?Math.PI/2:0)}flush(e,t,n={}){let r=(e,n,r)=>{let i=new ei(kd(n,!1),this.mats[e]);return i.name=r,i.castShadow=t.cast.has(e),i.receiveShadow=t.receive.has(e),i},i=new Map;for(let{key:e,plane:t,geos:n}of this.m.values())i.set(e,[...i.get(e)??[],{plane:t,geos:n}]);let a=[],o=[];for(let[t,s]of i){let i=r(t,s.flatMap(e=>e.geos),`shop.${t}`);if(e.add(i),a.push(i),s.some(e=>e.plane))for(let{plane:i,geos:a}of s){let s=r(t,a,i?`shop.${t}`:`shop.${t}.rest`);(i?n[i]:e).add(s),i||o.push(s)}}return{combined:a,rest:o}}};function Mm(){let e=document.createElement(`canvas`);e.width=e.height=64;let t=e.getContext(`2d`);t.fillStyle=`#c9b18d`,t.fillRect(0,0,64,64),t.fillStyle=`#2a2018`;for(let[e,n]of[[16,16],[48,16],[16,48],[48,48]])t.beginPath(),t.arc(e,n,4.5,0,7),t.fill();let n=new ra(e);return n.wrapS=n.wrapT=r,n.repeat.set(20,9),n.colorSpace=Ue,n.anisotropy=4,n}var Nm=(e,t)=>new Hr({color:new J(e).multiplyScalar(t)});function Pm(e,t){let n=new Dn;n.name=`workshop`;let r=Em,i={floor:Jp({color:7828332,metalness:0,roughness:.62,detail:1.3,colorVar:.2,roughVar:.5,name:`concrete`}),seam:Yp(3486254,.9),apron:Yp(5065285,1),wall:Yp(11843773,.92,{detail:.8,colorVar:.07}),wainscot:Yp(4151398,.7,{detail:1.5,colorVar:.05}),ceiling:Yp(6974834,.95),beam:Yp(3816770,.7),wood:Jp({color:5914414,metalness:0,roughness:.55,detail:5,colorVar:.14,roughVar:.25,name:`plywood`}),steel:Jp({color:10133670,metalness:.9,roughness:.32,detail:3,roughVar:.3}),darksteel:Jp({color:2895667,metalness:.75,roughness:.45,detail:2}),jig:Jp({color:11831896,metalness:0,roughness:.62,detail:9,colorVar:.16,roughVar:.3,name:`mdf`}),peg:Jp({color:16777215,metalness:0,roughness:.85,map:Mm()}),red:Yp(11740702,.5),orange:Yp(14383644,.5),yellow:Yp(14202410,.55),blue:Yp(2842252,.6),chest:Jp({color:10692127,metalness:.3,roughness:.4,detail:2}),tyre:Yp(1315860,.9),cloth:Yp(14275261,.95,{detail:6,colorVar:.08}),carbon:Yp(2500394,.8),bin:Yp(5595241,.7),binb:Yp(4024966,.7),housing:Yp(2829359,.6),tube:Nm(16773340,5.5),win:Nm(13821695,3.2),frame:Yp(14211804,.6),led:Nm(3073736,3.5),lamp:Nm(16757850,4)},a=new jm(i),o=xm(r),s={};for(let e of o){let t=new Dn;t.name=e.key,s[e.key]=t,n.add(t)}let c=r.x1-r.x0,l=r.z1-r.z0,u=(r.x0+r.x1)/2,d=(r.z0+r.z1)/2;a.box(`floor`,c,.2,l,u,-.1,d);for(let e=r.x0+1.25;e<r.x1;e+=2.5)a.box(`seam`,.012,.004,l,e,.001,d);for(let e=r.z0+1.2;e<r.z1;e+=2.4)a.box(`seam`,c,.004,.012,u,.001,e);let f=(e,t,n,i,o,s,c)=>{a.plane=e,a.box(`wall`,i,r.h,o,t,r.h/2,n),a.box(`wainscot`,i+(s?.03:0),1.05,o+(c?.03:0),t+s*.015,.525,n+c*.015)};f(`room.back`,r.x1+.1,d,.2,l,-1,0),f(`room.window`,u,r.z0-.1,c,.2,0,1),f(`room.side`,u,r.z1+.1,c,.2,0,-1),f(`room.door`,r.x0-.1,d,.2,l,1,0),a.plane=`room.ceiling`,a.box(`ceiling`,c,.2,l,u,r.h+.1,d);for(let e=r.z0+.8;e<r.z1;e+=1.6)a.box(`beam`,c,.28,.14,u,r.h-.14,e);for(let e of Dm)a.box(`housing`,.22,.07,1.4000000000000001,e.x,Om+.05,e.z),a.box(`tube`,.1,.03,km,e.x,Om,e.z);a.plane=`room.window`;let p=Am;a.box(`win`,p.w,p.h,.02,p.x,p.y,p.z+.01);for(let e of[-p.w/4,p.w/4,0])a.box(`frame`,.05,p.h+.08,.05,p.x+e,p.y,p.z+.04);for(let e of[-p.h/2,0,p.h/2])a.box(`frame`,p.w+.1,.05,.05,p.x,p.y+e,p.z+.04);a.box(`frame`,p.w+.24,.06,.2,p.x,p.y-p.h/2-.05,p.z+.1),a.plane=`room.back`;let m=r.x1-.02;a.box(`peg`,.03,1.1,2.6,m,1.8,.6),a.box(`darksteel`,.05,.04,2.7,m-.02,2.37,.6);let h=(e,t,n)=>{let r=m-.05;n===0?(a.box(`steel`,.03,.22,.05,r,t+.1,e),a.box(`red`,.05,.16,.07,r-.01,t-.08,e)):n===1?(a.box(`steel`,.02,.3,.035,r,t,e),a.cyl(`steel`,.035,.02,`x`,r,t+.16,e)):n===2?(a.box(`orange`,.04,.2,.07,r,t,e),a.box(`steel`,.02,.1,.05,r,t-.14,e)):n===3?a.box(`yellow`,.04,.3,.035,r,t,e):(a.cyl(`darksteel`,.09,.05,`x`,r,t,e,20),a.cyl(`steel`,.03,.06,`x`,r,t,e,12))};for(let e=0;e<12;e++)h(-.6+e*.22,1.95-e%3*.1,e%5);for(let e=0;e<8;e++)h(-.45+e*.3,1.5+e%2*.05,(e+2)%5);let g=-2.95,_=1.7,v=.55,y=r.x1-v/2-.03;for(let e of[-1.7/2,_/2])for(let t of[-.55/2,v/2])a.box(`darksteel`,.05,2.2,.05,y+t,1.1,g+e);let b=[.35,.95,1.55,2.15];for(let e of b)a.box(`darksteel`,v,.03,_,y,e,g);a.box(`led`,.02,.02,1.5999999999999999,y-v/2+.01,b[3]-.03,g),a.box(`led`,.02,.02,1.5999999999999999,y-v/2+.01,b[2]-.03,g);for(let e=0;e<3;e++)a.cyl(`cloth`,.09,.49000000000000005,`x`,y,b[1]+.1,-3.5+e*.28,18);for(let e=0;e<2;e++)a.cyl(`carbon`,.085,.49000000000000005,`x`,y,b[2]+.1,-3.35+e*.3,18);a.cyl(`cloth`,.09,.49000000000000005,`x`,y,b[2]+.1,-2.6,18);for(let e=0;e<3;e++)a.box(e===1?`binb`:`bin`,.4,.22,.42,y,b[0]+.13,-3.45+e*.5);for(let e=0;e<4;e++)a.box(e%2?`binb`:`bin`,.4,.2,.3,y,b[3]+.12,-3.5500000000000003+e*.4);a.box(`led`,.02,.025,l-.4,r.x1-.02,1.07,d),a.box(`lamp`,.04,.04,.5,r.x1-.05,2.6,1.9),a.plane=``;let x=3.1,S=r.x1-.35;for(let e of[-.6,.6])a.box(`darksteel`,.05,1.3,.05,S,.65,x+e);for(let e of[.4,.85,1.25])a.box(`darksteel`,.05,.04,1.3,S,e,x);for(let e=0;e<4;e++)a.cyl(e%2?`cloth`:`carbon`,.09,.28,`z`,S,.5+e%2*.45,2.7+e*.27,16);let C=1.7,w=1.9;a.box(`chest`,.62,.62,.9,C,.62,w);for(let e of[.42,.62,.82])a.box(`darksteel`,.01,.03,.84,1.385,e,w);a.box(`darksteel`,.66,.04,.94,C,.95,w);for(let[e,t]of[[-.26,-.4],[.26,-.4],[-.26,.4],[.26,.4]])a.cyl(`tyre`,.06,.05,`z`,C+e,.06,w+t,14);a.box(`steel`,.18,.1,.22,C,1.02,2.1),a.box(`bin`,.3,.12,.28,1.65,1.03,1.7);let T=Math.max(e+.8,2.4),E=.95,D=new ei(new sa(E,.05,T),i.wood);D.position.set(0,.875,0),D.name=`shop.tabletop`,D.castShadow=!0,D.receiveShadow=!0,n.add(D);let O=E/2-.06,k=T/2-.08;for(let e of[-.415,O])for(let t of[-k,k])a.box(`steel`,.07,.85,.07,e,.85/2,t),a.box(`darksteel`,.11,.02,.11,e,.01,t);for(let e of[-k,k])a.box(`steel`,.85,.07,.05,0,.81,e);for(let e of[-.415,O])a.box(`steel`,.05,.07,T-.16,e,.81,0);let A=.14,ee=t*.42;for(let e of[-ee,ee])a.box(`steel`,.05,.05,T-.2,e,.925,0);let te=t+.1,j=.06,ne=new za;ne.moveTo(-te/2,0),ne.lineTo(te/2,0),ne.lineTo(te/2,A),ne.lineTo(t/2,A);for(let e=1;e<24;e++){let n=1-2*e/24;ne.lineTo(t/2*n,A-.022*(1-n*n))}ne.lineTo(-t/2,A),ne.lineTo(-te/2,A),ne.closePath();let M=[];for(let t=0;t<5;t++)M.push(-e/2+e*(.07+.215*t));for(let e of M){let t=new wo(ne,{depth:j,bevelEnabled:!1});a.add(`jig`,t,0,.9500000000000001,e-j/2)}let{combined:N,rest:re}=a.flush(n,{cast:new Set([`steel`,`darksteel`,`jig`,`chest`,`bin`,`binb`,`cloth`,`carbon`]),receive:new Set([`floor`,`wall`,`wainscot`,`steel`,`darksteel`,`jig`,`peg`,`chest`,`bin`,`binb`])},s);n.traverse(e=>{e.isMesh&&e.name===`shop.jig`&&(e.userData.representational=!0)}),n.userData.representational=!0;let ie=new ei(new sa(400,.02,400),i.apron);ie.name=`shop.apron`,ie.position.set(u,-.21,d),n.add(ie);let ae=e=>{let t=e.size>0;for(let e of N)e.visible=!t;for(let e of re)e.visible=t;ie.visible=t;for(let n of o)s[n.key].visible=t&&!e.has(n.key)};return ae(new Set),{group:n,jigTopY:1.09,jigZ:M,planes:o,planeGroups:s,setHidden:ae}}function Fm(e){let t=new Fn,n=Em,r=(e,t=1)=>new Hr({color:new J(e).multiplyScalar(t),side:1}),i=[r(7304315),r(7304315),r(4212043),r(7828332,.85),r(7304315),r(7304315)],a=new ei(new sa(n.x1-n.x0,n.h,n.z1-n.z0),i);a.position.set((n.x0+n.x1)/2,n.h/2-1,(n.z0+n.z1)/2),t.add(a);let o=(e,t)=>new Hr({color:new J(e).multiplyScalar(t)});for(let e of Dm){let n=new ei(new sa(.1,.03,km),o(16773340,9));n.position.set(e.x,Om-1,e.z),t.add(n)}let s=new ei(new sa(Am.w,Am.h,.05),o(13821695,4.5));s.position.set(Am.x,Am.y-1,Am.z+.05),t.add(s);let c=new ei(new sa(.05,.05,1.6),o(3073736,2.5));c.position.set(n.x1-.3,.6000000000000001,-2.95),t.add(c);let l=new Fc(e),u=l.fromScene(t,.03).texture;return l.dispose(),u}function Im(e,t){let n=new Map(e.ops.map(e=>[e.id,e]));return e.order.map(e=>n.get(e)).filter(e=>!!e&&(e.variants.includes(`both`)||e.variants.includes(t)))}var Lm=new Set([0,3,4,5,6,7,8,9,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]);function Rm(e,t){return Im(e,t).filter(e=>!Lm.has(e.chapter)&&!e.stub)}function zm(e){let t=new Map,n=e=>`longez.check.${e}`,r=r=>{if(!t.has(r)){let i=[];try{let t=JSON.parse(e.getItem(n(r))||`[]`);Array.isArray(t)&&(i=t.filter(Number.isInteger))}catch{}t.set(r,new Set(i))}return t.get(r)};return{get:r,toggle(t,i){let a=r(t);a.has(i)?a.delete(i):a.add(i);try{e.setItem(n(t),JSON.stringify([...a]))}catch{}}}}var Bm=`r30.turnover-twist-check`;function Vm(e,t,n){if(t!==`roncz`||!n)return`upright`;let r=Im(e,t).map(e=>e.id),i=r.indexOf(Bm),a=r.indexOf(n);return i<0||a<0?`upright`:a<i?`inverted`:`upright`}var Hm={dist:52,el:31,az:52},Um={"r30.bottom-spar-cap":{dist:50,el:31,az:52},"r30.bottom-skin":{dist:54,el:31,az:52},"r30.shear-web":{dist:46,el:32,az:52,vertical:!0},"r30.top-spar-cap":{dist:50,el:31,az:52},"r30.top-skin":{dist:54,el:31,az:52},"r30.elev-bond-cores":{dist:96,el:30,az:132},"r30.elev-balance-check":{dist:46,el:8,az:86},"r30.elev-uptravel-test":{dist:42,el:8,az:86},"r30.elev-travel-check":{dist:42,el:8,az:86},"r30.elev-nc2-inserts":{dist:96,el:30,az:132},"r30.elev-skin-bottom":{dist:96,el:30,az:132},"r30.elev-skin-top":{dist:96,el:30,az:132},"r30.elev-trim-ends":{dist:96,el:30,az:132},"r30.elev-hinges":{dist:84,el:30,az:130},"r30.elev-hinge-slots":{dist:84,el:30,az:130},"r30.elev-flox-hinges":{dist:84,el:30,az:130},"r30.elev-nc12a":{dist:84,el:30,az:130},"r30.canard-tips":{dist:84,el:30,az:130},"r30.elev-trim-belcrank":{dist:84,el:30,az:130},"r30.elev-mass-balance":{dist:84,el:30,az:130},"r30.elev-balance-pockets":{dist:84,el:30,az:130},"r30.elev-cs11":{dist:84,el:30,az:130}};function Wm(e){return e.position[1]>=e.target[1]?1:-1}function Gm(e,t=()=>`upright`){let n={};for(let[r,i]of Object.entries(e)){let e=Um[r]??Hm,a=e.el*Math.PI/180,o=e.az*Math.PI/180,s=e.vertical?t(r)===`inverted`?-1:1:Wm(i),c=Math.cos(a)*e.dist,l=[-c*Math.cos(o),s*Math.sin(a)*e.dist,c*Math.sin(o)];n[r]={target:[...i.target],position:[i.target[0]+l[0],i.target[1]+l[1],i.target[2]+l[2]]}}return n}var Km=e=>e<.5?4*e*e*e:1-(-2*e+2)**3/2,qm=class{camera;controls;from={pos:new W,target:new W,fov:30};to={pos:new W,target:new W,fov:30};lift=0;t=1;dur=1;flying=!1;lastUser=-1e9;scale=1;outsideScale=null;shots={};clampPos;onShot;scaled(e,t){t.set(...e.pos);let n=e.outside&&this.outsideScale!==null?this.outsideScale:this.scale;if(n!==1&&!e.noScale){let r=new W(...e.target);t.sub(r).multiplyScalar(n).add(r)}return e.outside||this.clampPos?.(t),t}constructor(e,t){this.camera=e,this.controls=t,t.addEventListener(`start`,()=>{this.flying=!1,this.t=1,this.lastUser=performance.now()})}resolve(e){return typeof e==`string`?this.shots[e]:e}landing(e){let t=this.resolve(e);return{pos:this.scaled(t,new W),target:new W(...t.target),fov:t.fov}}set(e){let t=this.resolve(e);this.onShot?.(t),this.scaled(t,this.camera.position),this.controls.target.set(...t.target),this.camera.fov=t.fov,this.camera.updateProjectionMatrix(),this.controls.update(),this.flying=!1,this.t=1}fly(e,t=1.8,n=0){let r=this.resolve(e);this.onShot?.(r),this.from.pos.copy(this.camera.position),this.from.target.copy(this.controls.target),this.from.fov=this.camera.fov,this.scaled(r,this.to.pos),this.to.target.set(...r.target),this.to.fov=r.fov,this.lift=n,this.t=0,this.dur=t,this.flying=!0}update(e){if(!this.flying)return;this.t=Math.min(1,this.t+e/this.dur);let t=Km(this.t),n=Km(Math.min(1,this.t*1.3)),r=new W().lerpVectors(this.from.pos,this.to.pos,t);r.y+=Math.sin(Math.PI*t)*this.lift,this.camera.position.copy(r),this.controls.target.lerpVectors(this.from.target,this.to.target,n),this.camera.fov=this.from.fov+(this.to.fov-this.from.fov)*t,this.camera.updateProjectionMatrix(),this.t>=1&&(this.flying=!1)}};function Jm(e,t){let n=new Map;for(let r of Im(e,t))for(let e of r.components)n.has(e)||n.set(e,r.id);return n}function Ym(e,t,n,r,i){let a=new Map(Im(e,t).map((e,t)=>[e.id,t])),o=Jm(e,t),s=a.get(n);if(s===void 0)throw Error(`op not in variant: ${n}`);let c=new Set(e.ops.map(e=>e.id)),l=new Set(e.ops.flatMap(e=>e.components)),u=e.__ghost?`ghost`:`hidden`,d=new Map;for(let e of i){if(e.ply?!c.has(e.ply.op):!l.has(e.component))throw Error(`unowned mesh ${e.name}`);let t=e.ply?e.ply.op:o.get(e.component),n=t===void 0?void 0:a.get(t);n===void 0?d.set(e.name,`hidden`):n<s?d.set(e.name,`built`):n===s&&(!e.ply||e.ply.order<=r)?d.set(e.name,`current`):d.set(e.name,u)}return d}function Xm(e,t){let n=t instanceof Map?[...t]:Object.entries(t??{});return e.parts.length>0&&e.parts.every(e=>n.some(([t,n])=>(t===e||t.startsWith(e+`.p`)&&/^\d+$/.test(t.slice(e.length+2)))&&(n===`built`||n===`current`)))}var Zm=1.2,Qm=1.5,$m=2.2,eh=3.7,th=e=>e<0?0:e>1?1:e,nh={state:`built`,unroll:1,front:1,cure:1};function rh(e){let t=Math.min(Math.max(Number.isFinite(e.t)?e.t:eh,0),eh),n=e.meshOpIndex;if(n===void 0)return{...nh,state:`hidden`};if(n<e.curOpIndex)return{...nh};if(n>e.curOpIndex||e.order>e.lay)return{...nh,state:e.ghost?`ghost`:`hidden`};let r=e.lay>=e.count?th((t-$m)/Qm):0;return e.order<e.lay?{state:`current`,unroll:1,front:1,cure:r}:{state:`current`,unroll:th(t/Zm),front:th((t-Zm)/1),cure:r}}function ih(e){return{state:e,unroll:1,front:1,cure:1}}var ah=2.5500000000000003;function oh(e,t){return Object.entries(e).filter(([,e])=>e.bl_max==null||t<=e.bl_max).sort(([,e],[,t])=>e.op_index-t.op_index||e.order-t.order).map(([e,t])=>({node:e,component:t.component,cloth:t.cloth,order:t.order}))}var sh=e=>`B.L. ${Math.round(e*10)/10}`;function ch(e,t){let n=new Map;for(let e of t){n.has(e.component)||n.set(e.component,new Map);let t=n.get(e.component);t.set(e.cloth,(t.get(e.cloth)??0)+1)}return n.size?[...n].map(([t,n])=>`${e.components?.[t]?.label??t}: ${[...n].map(([e,t])=>`${t} ${e}`).join(`, `)}`).join(` · `):`No layers cut here`}var Z=e=>document.getElementById(e);function lh(e,t){let n=Z(`chips`),r=Z(`step-title`),i=Z(`step-summary`),a=Z(`checklist`),o=Z(`step`),s=Z(`step-head`),c=Z(`variant`),l=[],u=null,d=matchMedia(`(max-width: 640px)`),f=matchMedia(`(max-width: 1180px)`),p=!1,m=e=>{o.dataset.open=String(e),s.setAttribute(`aria-expanded`,String(e)),h()};f.addEventListener(`change`,()=>m(!f.matches)),s.addEventListener(`click`,()=>m(o.dataset.open!==`true`));let h=()=>{if(o.dataset.compact=`false`,o.dataset.list=`open`,d.matches||o.dataset.open!==`true`)return;let e=Z(`dock`),t=Z(`step-body`),n=e.offsetHeight-t.offsetHeight+t.scrollHeight>Math.min(window.innerHeight*.4,.085*window.innerWidth*window.innerHeight/Math.max(1,e.offsetWidth))&&a.children.length>0;o.dataset.compact=String(n),o.dataset.list=n&&!p?`closed`:`open`,Z(`checklist-h`).setAttribute(`aria-expanded`,String(!n||p))};Z(`checklist-h`).addEventListener(`click`,()=>{o.dataset.compact===`true`&&(p=!p,h())});let g=Z(`more`),_=Z(`viewpop`),v=Z(`controls`),y=()=>{let e=v.getBoundingClientRect();_.style.top=`${Math.round(e.bottom+8)}px`,_.style.right=`${Math.round(window.innerWidth-e.right)}px`},b=e=>{_.hidden=!e,g.setAttribute(`aria-expanded`,String(e)),e&&y()};g.addEventListener(`click`,()=>b(_.hidden)),document.addEventListener(`pointerdown`,e=>{let t=e.target;!_.hidden&&!_.contains(t)&&!g.contains(t)&&b(!1)}),document.addEventListener(`keydown`,e=>{e.key===`Escape`&&!_.hidden&&(b(!1),g.focus())}),new ResizeObserver(()=>{_.hidden||y()}).observe(v),window.addEventListener(`resize`,()=>{h(),_.hidden||y()}),m(!f.matches);let x=`longez.fuseDetails`,S=(e,t)=>{if(Z(`fuse-rows`).dataset.open=String(e),Z(`fuse-more`).setAttribute(`aria-expanded`,String(e)),t)try{window.localStorage.setItem(x,e?`1`:`0`)}catch{}h()},C=!1;try{C=window.localStorage.getItem(x)===`1`}catch{C=!1}S(C,!1),Z(`fuse-more`).addEventListener(`click`,()=>S(Z(`fuse-rows`).dataset.open!==`true`,!0)),Z(`subject`)?.addEventListener(`click`,t=>{let n=t.target.closest(`button[data-subject]`);n&&e.onSubject?.(n.dataset.subject)}),c.addEventListener(`click`,t=>{let n=t.target.closest(`button[data-variant]`);n&&e.onVariant(n.dataset.variant)}),Z(`home`).addEventListener(`click`,()=>e.onHome()),Z(`tour`).addEventListener(`click`,()=>e.onTour()),Z(`bar-home`).addEventListener(`click`,()=>e.onHome()),Z(`ghost`).addEventListener(`change`,t=>e.onGhost(t.target.checked)),Z(`scrub`).addEventListener(`input`,t=>e.onScrub(+t.target.value)),Z(`play`).addEventListener(`click`,()=>e.onPlay());let w=Z(`section-on`),T=Z(`section-bl`),E=sh,D=()=>e.onSection(w.checked,+T.value);w.addEventListener(`change`,D),T.addEventListener(`input`,D);let O=Z(`stick-defl`);O.addEventListener(`input`,()=>e.onStick?.(+O.value));let k=Z(`canopy-open`);k.addEventListener(`input`,()=>e.onCanopy?.(+k.value));let A=Z(`aileron-defl`);A.addEventListener(`input`,()=>e.onAileron?.(+A.value));let ee=Z(`rudder-defl`);ee.addEventListener(`input`,()=>e.onRudder?.(+ee.value)),Z(`quality-seg`).addEventListener(`click`,t=>{let n=t.target.closest(`button[data-q]`);n&&e.onQuality(n.dataset.q)}),Z(`labels-on`).addEventListener(`change`,t=>e.onLabels(t.target.checked)),Z(`paths-on`).addEventListener(`change`,t=>e.onPaths(t.target.checked)),n.addEventListener(`click`,t=>{let n=t.target.closest(`button[data-op]`);n&&e.onSelect(n.dataset.op)});let te=e=>{let n=e?.completion?.length??0,r=e?[...t.get(e.id)].filter(e=>e<n).length:0;Z(`check-count`).textContent=n?`${r}/${n}`:``},j=e=>{if(a.replaceChildren(),!e){r.textContent=l.length?`Pick a step`:`No steps for this variant`,i.textContent=l.length?``:`The build steps for this canard are not written yet.`,Z(`step-count`).textContent=``,Z(`checklist-h`).hidden=!0,te(null);return}let n=l.findIndex(t=>t.id===e.id);Z(`step-count`).textContent=`${n+1} / ${l.length}`,r.textContent=e.title,i.textContent=e.summary;let o=t.get(e.id);(e.completion??[]).forEach((n,r)=>{let i=document.createElement(`li`),s=document.createElement(`label`),c=document.createElement(`input`);c.type=`checkbox`,c.checked=o.has(r),c.addEventListener(`change`,()=>{t.toggle(e.id,r),te(e)}),s.append(c,document.createTextNode(n)),i.append(s),a.append(i)}),Z(`checklist-h`).hidden=a.children.length===0,te(e),p=!1,h()};return{setGhost(e){Z(`ghost`).checked=e},setBuild(e,t){Z(`scrubwrap`).hidden=t===0;let n=Z(`scrub`);n.max=String(t),n.value=String(e),Z(`scrublabel`).textContent=`Ply ${e} of ${t}`},initSection(e,t){T.max=String(e),T.value=String(t),Z(`section`).hidden=!1,Z(`section-station`).textContent=E(t)},scaleSection(e,t,n){E=e.fmt,T.min=String(e.min),T.max=String(e.max),T.setAttribute(`aria-label`,e.label),w.checked=t,T.value=String(n),Z(`section`).hidden=!1,Z(`section-station`).textContent=E(n)},setSection(e,t){w.checked=e,T.value=String(t),Z(`section-station`).textContent=E(t)},setTouring(e){Z(`tour`).setAttribute(`aria-pressed`,String(e)),Z(`tour`).textContent=e?`Stop tour`:`Tour`},setPaths(e){Z(`paths-on`).checked=e},setLabels(e){Z(`labels-on`).checked=e},setReadout(e){Z(`ro-station`).textContent=e.station;let t=Z(`ro-layers`);t.textContent=e.layers,t.title=e.layers,Z(`t-plies`).hidden=e.plies===null,Z(`ro-plies`).textContent=e.plies??``,Z(`ro-cloth`).textContent=e.cloth},setPlaying(e){Z(`play`).setAttribute(`aria-pressed`,String(e)),Z(`play`).textContent=e?`Stop`:`Play`},setQuality(e,t){let n={high:`High`,mid:`Med`,low:`Low`}[e];Z(`quality-label`).textContent=`Quality: ${n}${t?` (auto)`:``}`;for(let n of Z(`quality-seg`).querySelectorAll(`button[data-q]`)){let r=n.dataset.q;n.setAttribute(`aria-pressed`,String(r===`auto`?t:!t&&r===e))}},setStick(e,t,n){Z(`stick`).hidden=!e,+O.value!==t&&(O.value=String(t)),Z(`stick-val`).textContent=n},setCanopy(e,t,n,r=105){Z(`canopy-ctl`).hidden=!e,+k.max!==r&&(k.max=String(r)),+k.value!==t&&(k.value=String(t)),Z(`canopy-val`).textContent=n},setAileron(e,t,n,r=20){Z(`aileron-ctl`).hidden=!e,+A.max!==r&&(A.max=String(r)),+A.value!==t&&(A.value=String(t)),Z(`aileron-val`).textContent=n},setRudder(e,t,n,r=30){Z(`rudder-ctl`).hidden=!e,+ee.max!==r&&(ee.max=String(r),ee.min=String(-r)),+ee.value!==t&&(ee.value=String(t)),Z(`rudder-val`).textContent=n},setSubject(e){for(let t of document.querySelectorAll(`#subject button[data-subject]`))t.setAttribute(`aria-pressed`,String(t.dataset.subject===e));c.hidden=e!==`canard`,document.body.dataset.subject=e},setCg(e){Z(`fuse-rows`).hidden=e===null,Z(`t-cg`).hidden=e===null,Z(`t-legend`).hidden=e===null,e&&(Z(`ro-cg`).textContent=e.value,Z(`ro-cg-sub`).textContent=e.sub??``,Z(`t-cg`).title=e.sub?`${e.value}. ${e.sub}`:e.value)},setKin(e){let t=Z(`t-kin`);if(!e){t.hidden=!0;return}t.hidden=!1,Z(`ro-kin-label`).textContent!==e.label&&(Z(`ro-kin-label`).textContent=e.label),Z(`ro-kin`).textContent!==e.value&&(Z(`ro-kin`).textContent=e.value),Z(`ro-kin-sub`).textContent!==e.sub&&(Z(`ro-kin-sub`).textContent=e.sub),t.title=`${e.value}. ${e.sub}`},setGround(e){Z(`t-ground`).hidden=e===null,e&&(Z(`ro-ground`).textContent=e.value,Z(`ro-ground-sub`).textContent=e.sub,Z(`t-ground`).title=`${e.value}. ${e.sub}`)},setRef(e){Z(`t-ref`).hidden=e===null,e&&(Z(`ro-ref`).textContent=e.value,Z(`t-ref`).title=`${e.value}. ${e.sub}`)},setVariant(e){for(let t of c.querySelectorAll(`button[data-variant]`))t.setAttribute(`aria-pressed`,String(t.dataset.variant===e))},setOps(e){if(l=e,n.replaceChildren(),!e.length){let e=document.createElement(`span`);e.className=`none`,e.textContent=`No steps for this variant yet`,n.append(e);return}for(let t of e){let e=document.createElement(`button`);e.type=`button`,e.dataset.op=t.id,e.title=t.title,e.textContent=t.title.length>34?t.title.slice(0,32).trimEnd()+`…`:t.title,n.append(e)}},setSelected(e){u=e;for(let t of n.querySelectorAll(`button[data-op]`)){let n=t.dataset.op===e;n?t.setAttribute(`aria-current`,`true`):t.removeAttribute(`aria-current`),n&&t.scrollIntoView?.({block:`nearest`,inline:`center`})}j(l.find(t=>t.id===e)??null)},get selected(){return u}}}var uh=[`high`,`mid`,`low`],dh={high:{ao:!0,aoSamples:8,aoScale:.5,dof:!0,dofTaps:14,bloom:!0,msaa:4,dprCap:2,maxPixels:1/0,shadowMap:4096,cheapShaders:!1},mid:{ao:!0,aoSamples:6,aoScale:.4,dof:!1,dofTaps:0,bloom:!0,msaa:2,dprCap:1.5,maxPixels:1/0,shadowMap:2048,cheapShaders:!1},low:{ao:!1,aoSamples:0,aoScale:.4,dof:!1,dofTaps:0,bloom:!1,msaa:0,dprCap:1,maxPixels:5e5,shadowMap:0,cheapShaders:!0}};function fh(e,t,n,r){let i=Math.sqrt(e.maxPixels/Math.max(1,n*r));return Math.max(.25,Math.min(t||1,e.dprCap,i))}function ph(e){let t=(e??``).trim().toLowerCase();return t===`high`||t===`low`?t:t===`mid`||t===`medium`?`mid`:null}function mh(e){return e.coarse?Math.min(e.width,e.height)>=700?`high`:`mid`:`high`}var hh=1e3,gh=(e,t=0)=>({tier:e,frames:[],sum:0,settle:t});function _h(e){if(!e.length)return 0;let t=e.slice().sort((e,t)=>e-t);return t[t.length>>1]}function vh(e,t){let n=Math.min(Math.max(t,0),500);if(e.settle>0)return{...e,settle:Math.max(0,e.settle-n)};let r=e.frames.concat(n),i=e.sum+n;for(;r.length>1&&i-r[0]>=1500;)i-=r.shift();let a=uh.indexOf(e.tier);return i>=1500&&r.length>=3&&_h(r)>34&&a<uh.length-1?{tier:uh[a+1],frames:[],sum:0,settle:hh}:{tier:e.tier,frames:r,sum:i,settle:0}}var yh=.08,bh=(e=0)=>({scale:1,frames:[],sum:0,settle:e});function xh(e,t){if(!e.length)return 0;let n=e.slice().sort((e,t)=>e-t);return n[Math.min(n.length-1,Math.floor(t*n.length))]}function Sh(e,t){let n=Math.min(Math.max(t,0),500);if(e.settle>0)return{...e,settle:Math.max(0,e.settle-n)};let r=e.frames.concat(n),i=e.sum+n;if(i<600||r.length<3)return{...e,frames:r,sum:i};if(xh(r,.75)>20&&e.scale>.08){let t=Math.min(.9,Math.max(.5,12/_h(r)));return{scale:Math.max(yh,e.scale*t),frames:[],sum:0,settle:800}}return{...e,frames:[],sum:0}}function Ch(e,t,n){let r=e.tours??{};return Im(e,t).filter(e=>e.chapter===n&&!e.stub).map(e=>({op:e.id,shot:r[e.id]??null}))}var wh=`f18.check-ab`,Th=`f18.cut-remove`,Eh=`f18.carve-inside`,Dh=`f18.pads-inside-glass`,Oh=`f18.hinges`,kh=`f18.latches`,Ah=`f18.front-cover`;function jh(e,t,n,r){if(!n||!t.includes(e))return`airplane`;let i=r.indexOf(n);return i>=r.indexOf(`f18.trim-plexi`)&&i<r.indexOf(`f18.locate-blocks`)?`bench-up`:i>=r.indexOf(`f18.cut-remove`)&&i<=r.indexOf(`f18.vent-brace`)?`bench-down`:`airplane`}var Mh=e=>e<.5?4*e*e*e:1-(-2*e+2)**3/2,Nh=e=>Math.min(1,Math.max(0,e)),Ph={wait:1.4,seconds:4.6},Fh=e=>Mh(Nh((e-Ph.wait)/Ph.seconds)),Ih=()=>Ph.wait+Ph.seconds+1.4,Lh={wait:1.8,seconds:3.8},Rh=e=>Mh(Nh((e-Lh.wait)/Lh.seconds)),zh=()=>Lh.wait+Lh.seconds+1.4,Bh=(e,t)=>Math.max(0,Math.min(t,e)),Vh=e=>(Math.round(e*100)/100).toString();function Hh(e,t){let n=Math.round(e);return n<=0?`Closed`:n<=90?`${n} deg open`:`${n} deg open: ${n-90} deg past vertical, representational`}var Uh=e=>Math.round(e)<=0?`Closed`:`${Math.round(e)} deg`;function Wh(e){let t=e.latch.derived_centres_fs.map(Vh).join(`, `),n=e.latch.printed_labels_fs.map(Vh).join(`, `);return{value:`Pad centres FS ${t} (derived)`,sub:`The printed labels read ${n}: ${Vh(e.latch.gap_in)} in apart, unresolved`}}function Gh(e){return`Front cut about FS ${Vh(e.front_cut.fs)}, datum not named (representational)`}function Kh(e){let t=e.pads.left_aft_edge_fwd_of_cut,n=e.pads.right_aft_edge_fwd_of_cut.map(Vh).join(`, `);return{value:`Aft edges forward of FS ${Vh(e.rear_cut_fs)}: right ${n}`,sub:`Left ${t.map((e,t)=>t===2?`${Vh(e)} (safety catch)`:Vh(e)).join(`, `)}; each pad ${Vh(e.pads.length_in)} in long. Hinge pads blue, latch pads green, catch pad red`}}function qh(e){return`${e.checks.map(e=>`${e.id} ${e.min?`at least `:``}${Vh(e.height_in)} in`).join(`, `)}, above WL ${Vh(e.checks[0]?.wl0??0)}`}var Jh={hinge:{label:`hinge`,color:3108828},latch:{label:`latch`,color:3123279},catch:{label:`safety catch`,color:13777723}};function Yh(e,t,n){switch(e){case wh:return{label:`Canopy height checks`,value:qh(t),sub:`A is taken 6 in forward of the headrest (the headrest station is fitted); B is taken 15 in forward of the firewall`};case Th:return{label:`Canopy cuts`,value:Gh(t),sub:`The rear cut at FS ${Vh(t.rear_cut_fs)} is the plans'. The front and rear covers stay on the fuselage`};case Ah:return{label:`Front cover`,value:Gh(t),sub:`The cover runs from F28 to the front cut`};case Eh:return{label:`Pads`,...Kh(t)};case Dh:return{label:`Pads`,value:`Hinge (blue, right, 4), latch (green, left, 3), catch (red, left, 1)`,sub:`15 BID plies each, wet flox between; the right pads are recessed for the hinges`};case Oh:return{label:`Canopy opening`,value:Hh(n,t.hinge),sub:`Hinged on the right: it swings up and out; the opening arc is representational`};case kh:{let e=Wh(t);return{label:`Latch pads`,value:e.value,sub:`${e.sub}. Three latches on the left, the handle on the front one`}}default:return null}}function Xh(e,t,n){let r=e?.prototype_weights?.rows?.canopy;return!r||!t||!/^f18\./.test(t)||n.indexOf(t)<n.indexOf(`f18.safety-catch`)?null:{value:`Canopy (CP26 builder weight, N26MS): ${r.weight_lb.toFixed(1)} lb, reference, not in CG`,sub:r.note}}var Zh=`f19.cut-cores`,Qh=`f19.shear-web`,$h=`f19.bottom-cap`,eg=`f19.bottom-skin`,tg=`f19.aileron-cut`,ng=`f19.aileron-build`,rg=`f19.attach`,ig=`f20.jig`,ag=`f20.rudder-hang`,og=[Zh,`f19.core-cutouts`,$h,eg],sg=new Set([`f19.controls`,ag]),cg=new Set([...sg,`f19.hardpoints`,`f19.pads-plates`,rg]),lg=e=>!!e&&cg.has(e.id),ug=e=>!!e&&sg.has(e.id),dg=[`f20.cut-cores`,`f20.skins`,`f20.trim`];function fg(e,t){if(!e)return`airplane`;if(dg.includes(e))return`winglet`;let n=t.indexOf(e);return n<t.indexOf(`f19.jig`)||n>=t.indexOf(`f19.attach`)?`airplane`:og.includes(e)?`table`:`jig`}var pg=(e,t)=>fg(e,t)!==`airplane`;function mg(e,t,n){return e!==`left`||!t||n.indexOf(t)>=n.indexOf(`f19.attach`)}function hg(e,t,n){if(!t)return!1;let r=n.indexOf(t);return e===`wing.jigs`?fg(t,n)===`jig`||fg(t,n)===`table`:e!==`winglet.jig`||r>=n.indexOf(`f20.jig`)&&r<=n.indexOf(`f20.outside-layups`)}var gg=e=>e<.5?4*e*e*e:1-(-2*e+2)**3/2,_g=e=>Math.min(1,Math.max(0,e)),vg={wait:1.6,seconds:3.4},yg=e=>gg(_g((e-vg.wait)/vg.seconds)),bg=()=>vg.wait+vg.seconds+1.4,xg={wait:1.6,seconds:3.4},Sg=e=>gg(_g((e-xg.wait)/xg.seconds)),Cg=()=>xg.wait+xg.seconds+1.4,wg=(e,t)=>Math.max(0,Math.min(t,e)),Tg=(e,t)=>Math.max(-t,Math.min(t,e)),Eg=e=>(Math.round(e*100)/100).toString(),Dg=e=>(Math.round(e*10)/10).toFixed(1);function Og(e,t){let n=Math.round(e);return n<=0?`Neutral`:n>=Math.round(t)?`${n} deg up: at the stop`:`${n} deg up`}var kg=e=>Math.round(e)<=0?`Neutral`:`${Math.round(e)} deg up`;function Ag(e,t){let n=Math.round(e);return n===0?`Neutral`:`${Math.abs(n)} deg, trailing edge ${n>0?`outboard`:`inboard`}${Math.abs(n)>=Math.round(t)?`: at the limit`:``}`}var jg=e=>Math.round(e)===0?`Neutral`:`${Math.abs(Math.round(e))} deg ${e>0?`out`:`in`}`;function Mg(e){let t=e.conflicts.le_bl_106_25;return{value:`Leading edge at BL 106.25: printed FS ${Eg(t.printed_fs)}, FS ${Eg(t.derived_fs)} from the chord and the trailing edge`,sub:`${Eg(Math.abs(t.printed_fs-t.derived_fs))} in apart, unresolved; the model uses the chord and the trailing edge`}}function Ng(e){let t=e.conflicts.aileron_inboard;return{value:`Aileron inboard end: BL ${Eg(t.p171_bl)} on p171, BL ${Eg(t.p124_bl)} cut at the foam joint`,sub:`${Eg(Math.abs(t.p124_bl-t.p171_bl))} in apart, unresolved; the model cuts at BL ${Eg(t.p124_bl)}`}}function Pg(e){let t=e.conflicts.attach_bolt_spacing;return{value:`Spar bolt spacing: ${Eg(t.drawing_in)} in on the drawing, ${Eg(t.text_in)} in in the text`,sub:`${Eg(Math.abs(t.drawing_in-t.text_in))} in apart, unresolved`}}function Fg(e){let t=e.shear_web.zones,n=t[t.length-1];return{value:`${t.slice(0,-1).map(e=>`BL ${Eg(e[0])} to ${Eg(e[1])}: ${e[2]} plies`).join(`, `)}, BL ${Eg(n[0])} to ${Eg(n[1])}: ${n[2]} plies (CP26 LPC 31; plans print ${e.shear_web.outboard_plies_printed})`,sub:`Two plies run the full span; the others step in 39 and 91 in from the tip`}}function Ig(e){let[t,n,r]=e.winglet.abc_book_in,[i,a,o]=e.winglet.abc_residual_in,[s,c]=e.winglet.wprp;return{value:`A ${Eg(t)}, B ${Eg(n)}, C ${Eg(r)} in from the reference point (BL ${Eg(c)}, FS ${Eg(s)})`,sub:`The model closes to A ${Eg(i)}, B ${Eg(a)}, C ${Eg(o)} in; the winglet's lean (${Eg(e.winglet.lean_in)} in) is derived, low confidence`}}function Lg(e,t){let n={a:0,b:1,c:2}[t];return`${t.toUpperCase()} ${Eg(e.winglet.abc_book_in[n])} in`}function Rg(e,t,n,r){switch(e){case Zh:return{label:`Core cut`,...Mg(t)};case Qh:return{label:`Shear web plies`,...Fg(t)};case tg:return{label:`Aileron cut`,...Ng(t)};case ng:return{label:`Aileron travel`,value:Og(n,t.aileron.max_up_deg),sub:`Up to the ${t.aileron.max_up_deg} deg stop (p125, p131); the arc is representational`};case rg:return{label:`Wing attach`,...Pg(t)};case ig:return{label:`Winglet jig`,...Ig(t)};case ag:return{label:`Rudder travel`,value:Ag(r,t.rudder.max_deg),sub:`Swings to ${t.rudder.max_deg} deg either way (p139); positive is the trailing edge outboard; the arc is representational`};default:return null}}function zg(e,t,n){let r=e?.prototype_weights?.rows;if(!r||!t||!/^f(19|20)\./.test(t))return null;let i=e=>n.indexOf(t)>=n.indexOf(e),a=`(CP26 builder weight, N26MS)`,o=`, reference, not in CG`;if(i(`f20.rudder-hang`)&&r.wing_complete){let e=[r.upper_winglet&&`upper winglet ${Dg(r.upper_winglet.weight_lb)} lb`,r.lower_winglet&&`lower winglet ${Dg(r.lower_winglet.weight_lb)} lb`].filter(Boolean).join(`, `);return{value:`Wing with winglets and rudder ${a}: ${Dg(r.wing_complete.weight_lb)} lb each${o}`,sub:`${e}; ${r.wing_complete.note}`}}if(i(`f20.lower-fin`)&&t.startsWith(`f20.`)&&r.lower_winglet)return{value:`Lower winglet ${a}: ${Dg(r.lower_winglet.weight_lb)} lb${o}`,sub:r.lower_winglet.note};if(i(`f19.attach`)&&t.startsWith(`f19.`)&&r.wing_ch19){let e=r.aileron?`; aileron ${Dg(r.aileron.weight_lb)} lb`:``;return{value:`Wing to the end of chapter 19 ${a}: ${Dg(r.wing_ch19.weight_lb)} lb each${e}${o}`,sub:r.wing_ch19.note}}return i(`f19.aileron-build`)&&t.startsWith(`f19.`)&&r.aileron?{value:`Aileron ${a}: ${Dg(r.aileron.weight_lb)} lb${o}`,sub:r.aileron.note}:null}var Bg=[`fuselage.`,`gear.`,`nose.`,`spar.`,`firewall.`,`controls.`,`trim.`,`canopy.`,`wing.`,`winglet.`,`strake.`,`elec.`,`engine.`,`cover.`,`upholstery.`],Vg=new Set([14,15,16,17,18,19,20,21,22,23,24,25,26]),Hg=`f14.fit-fuselage`,Ug=new Set([`spar.box`,`spar.cap_top`,`spar.cap_bottom`,`spar.bulkheads`,`spar.lwa`,`spar.spruce_blocks`,`spar.jig`]),Wg=new Set([`f16.pitch-pushrod`,`f17.pitch-trim`]),Gg=`f16.pitch-pushrod`,Kg=new Set([`spar.lwa`,`spar.spruce_blocks`]),qg=new Set([`f14.interior-layups`]);function Jg(e,t,n){return!Ug.has(e)||!t?`installed`:n.indexOf(t)<=n.indexOf(`f14.nut-access-hole`)?`bench`:`installed`}function Yg(e){return!!e&&(qg.has(e.id)||e.components.some(e=>Kg.has(e)))}var Xg={wait:1.6,seconds:3.4},Zg=e=>e<.5?4*e*e*e:1-(-2*e+2)**3/2;function Qg(e){return Zg(Math.min(1,Math.max(0,(e-Xg.wait)/Xg.seconds)))}var $g=()=>Xg.wait+Xg.seconds+1.2;function e_(e,t){if(Math.abs(e)<1e-12&&Math.abs(t)<1e-12)throw Error(`CG cannot be at the hinge.`);let n=-90-Math.atan2(t,e)*180/Math.PI;for(;n<=-180;)n+=360;for(;n>180;)n-=360;return n}var t_=(e,t)=>{let n=e_(e,t);return n>0&&n<180},n_=e=>e<.5?4*e*e*e:1-(-2*e+2)**3/2,r_=e=>Math.min(1,Math.max(0,e)),i_={wait:1,down:1.4,hold:.6,up:1.8};function a_(e,t){let n=e-i_.wait;if(n<=0)return 0;if(n<i_.down)return t.down_deg*n_(n/i_.down);let r=n-i_.down;if(r<i_.hold)return t.down_deg;let i=r_((r-i_.hold)/i_.up);return t.down_deg+(-t.up_target_deg-t.down_deg)*n_(i)}var o_=()=>i_.wait+i_.down+i_.hold+i_.up;function s_(e,t){let n=e=>(Math.round(e*10)/10).toFixed(1),r=e=>String(Math.round(e*100)/100);return Math.abs(e)<.05?`Neutral`:e<0?`Up ${n(-e)} deg  (target ${r(t.up_target_deg)}, floor ${r(t.up_floor_deg)})`:`Down ${n(e)} deg  (limit ${r(t.down_deg)})`}var c_={wait:.8,slide:1,decay:1.7,period:1.7};function l_(e,t){let n=10*n_(r_((e-c_.wait)/c_.slide)),r=e-c_.wait-c_.slide;if(r<=0)return{slide:n,degDown:0};let i=1-Math.exp(-c_.decay*r)*Math.cos(2*Math.PI*r/c_.period);return{slide:n,degDown:-t*i}}var u_=()=>c_.wait+c_.slide+6;function d_(e,t,n){return`${n?`Hangs`:`Swinging toward`} ${t?`nose down`:`nose up`}, about ${Math.round(e)} deg`}function f_(e,t,n){let r=e-t;if(r>n)throw Error(`Strut length insufficient for vertical drop.`);let i=Math.sqrt(n**2-r**2);return Math.atan2(i,r)*180/Math.PI}function p_(e,t,n,r){let i=n-t;if(i>r)throw Error(`Strut length insufficient for vertical drop.`);return[e-Math.sqrt(r**2-i**2),n]}function m_(e,t,n=90){if(!(e>=0&&e<=1))throw Error(`Retraction parameter t must be in [0, 1].`);return t+e*(n-t)}function h_(e,t,n){let r=n-e;if(Math.abs(r)>t)throw Error(`Strut too short to reach the clearance height.`);return 90+Math.asin(r/t)*180/Math.PI}function g_(e,t=10.8){if(!(e>=0&&e<=1))throw Error(`Retraction parameter t must be in [0, 1].`);return e*t}function __(e,t){let n=e.candidates[t].axle_fs,[r]=p_(n,e.axle_wl,e.pivot_wl,e.strut_length);return{pivot:[r,e.pivot_wl-e.wl_zero],axle:[n,e.axle_wl-e.wl_zero],thetaDown:f_(e.pivot_wl,e.axle_wl,e.strut_length),thetaUp:h_(e.pivot_wl,e.strut_length,e.clearance_wl)}}function v_(e,t){return m_(e,t.thetaDown,t.thetaUp)-t.thetaDown}function y_(e,t){let n=-v_(e,t)*Math.PI/180,r=Math.cos(n),i=Math.sin(n),[a,o]=t.pivot;return{r:[r,i,-i,r],tx:a-(r*a+i*o),tz:o-(-i*a+r*o)}}function b_(e,t){let n=y_(e,t);return[n.r[0]*t.axle[0]+n.r[1]*t.axle[1]+n.tx,n.r[2]*t.axle[0]+n.r[3]*t.axle[1]+n.tz]}function x_(e,t){return r_((e-2)/t)}function S_(e,t=10.8){let n=e=>(Math.round(e*10)/10).toFixed(1);return`Crank ${n(g_(e,t))} of ${n(t)} turns${e<=0?` (gear down)`:e>=1?` (retracted)`:``}`}function C_(e,t){if(!e||e.length<2)return null;let[n,r]=e;return`Nose wheel arm: F.S. ${n} (plans) / about ${r} (manual): ${t===`conflict`||!t?`conflict`:t}`}var w_=[`r30.elev-uptravel-test`,`r30.elev-travel-check`],T_=`r30.elev-balance-check`,E_=`f13.rig-nose-gear`,D_={[Hg]:$g(),[Th]:Ih(),[Oh]:zh(),[ng]:bg(),[ag]:Cg(),[Gg]:o_()+.8,"r30.elev-uptravel-test":o_()+.8,"r30.elev-travel-check":o_()+.8,[T_]:u_()+.8,[E_]:9.2},O_=(e,t)=>Math.max(-t.down_deg,Math.min(t.up_target_deg,e)),k_=(e,t)=>t*Math.sin(e*Math.PI/180);function A_(e,t){let n=Math.sin(t.cant_forward_deg*Math.PI/180)-k_(e,t.arm_in)/t.lever_in;if(Math.abs(n)>1)throw Error(`Stroke exceeds lever capacity.`);return Math.asin(n)*180/Math.PI}function j_(e,t){let n=e*Math.PI/180,r=t*Math.PI/180;return[-Math.sin(n),-Math.cos(n)*Math.sin(r),Math.cos(n)*Math.cos(r)]}function M_(e,t){return s_(-e,t)}var N_=`longez.subject`,P_=e=>e===`fuselage`?`fuselage`:`canard`,F_=new Set([4,5,6,7,8,9,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]),I_=[4,5,6,7,8,9,12,13],L_=[14,15,16,17],R_=new Set([12,13]);function z_(e,t){return Im(e,t).filter(e=>F_.has(e.chapter)&&!e.stub)}var B_={"fuselage.side_left":`f06.trial-fit`,"fuselage.side_right":`f06.trial-fit`,"fuselage.longerons":`f06.trial-fit`,"fuselage.front_seat_bkhd":`f06.bond-front-seat`,"fuselage.panel":`f06.bond-panel`,"fuselage.f22":`f06.bond-f22`,"fuselage.rear_seat_bkhd":`f06.bond-rear-seat`,"fuselage.firewall":`f06.bond-firewall`,"fuselage.f28":`f06.f28-install`,"fuselage.bottom":`f06.bottom-foam-fit`,"fuselage.gear_extrusions":`f06.trial-fit`,"fuselage.canard_cutout":`f07.canard-cutout`,"fuselage.belt_insert":`f07.belt-insert`,"fuselage.rollover":`f08.roll-over-bond`,"fuselage.rollover_inserts":`f08.roll-over-bond`,"fuselage.belt_attach":`f08.belt-attach`,"fuselage.step":`f08.step`,"gear.jig_blocks":`f09.jig-blocks`,"gear.strut":`f09.position-gear`,"gear.datum_board":`f09.position-gear`,"gear.axles":`f09.axles-brakes`,"gear.nose_strut":`f13.strut-reinforce`,"nose.ng30_plates":`f13.ng30-plates`,"nose.ng_hardware":`f13.ng-box-assemble`,"nose.ng31":`f13.ng31-f6`,"nose.floor_blocks":`f13.floor-blocks`,"nose.pivot_blocks":`f13.pedal-pivot-blocks`,"nose.side_blocks":`f13.side-pieces`,"nose.pedals":`f13.rudder-pedals`,"nose.strut_cover":`f13.strut-slot-sc`,"nose.nb_box":`f13.nb-box`,"nose.pitot":`f13.pitot-static`,"nose.static_port":`f13.pitot-static`,"nose.top_block":`f13.top-foam`,"nose.skin":`f13.carve-glass-nose`,"nose.door":`f13.nose-door`},V_=Object.keys(B_).filter(e=>e.startsWith(`nose.`)||e===`gear.nose_strut`),H_=new Set([`fuselage.gear_extrusions`,`fuselage.canard_cutout`,`fuselage.belt_insert`,`fuselage.belt_attach`,`fuselage.step`,`gear.jig_blocks`,`gear.datum_board`,`gear.axles`,...V_]),U_={"fuselage.bottom":[`f06.bottom-glass`]},W_=`f06.bottom-bond`;function G_(e,t,n,r=[]){if(!t)return`jig`;let i=n.indexOf(t);if(t===`f06.trial-fit`&&r.includes(e))return`jig`;if(U_[e]?.includes(t))return`table`;let a=B_[e],o=a?n.indexOf(a):-1;return o>=0&&i>=o?`jig`:`table`}var K_=[`gear.nose_strut`,`nose.ng30_plates`,`nose.ng_hardware`],q_=`f13.ng31-f6`;function J_(e,t,n){if(!t||!K_.includes(e))return!1;let r=n.indexOf(t),i=n.indexOf(B_[e]),a=n.indexOf(q_);return i>=0&&a>=0&&r>=i&&r<a}var Y_=`f09.position-gear`,X_=`f09.brake-lines`,Z_={"f07.skin-right":135,"f07.skin-left":-135};function Q_(e,t,n=Z_){let r=t.indexOf(Y_);if(!e)return r>=0?`on-gear`:`upright`;let i=t.indexOf(e),a=t.indexOf(W_);if(!(a>=0&&i>=a))return`inverted`;let o=t.indexOf(X_);if(r>=0&&o>=0&&i>o)return`on-gear`;if(r>=0&&i>=r)return`gear-table`;let s=n[e];return s?s>0?`bank-left-45`:`bank-right-45`:`upright`}function $_(e,t,n){if(!e)return!0;if(!t)return!e.until&&!e.only;if(e.only)return t===e.only;let r=n.indexOf(t);return!(e.from&&r<n.indexOf(e.from)||e.until&&r>=n.indexOf(e.until))}function ev(e,t,n){if(!e?.length)return null;if(!t)return e[e.length-1].node;let r=n.indexOf(t),i=null;for(let t of e)n.indexOf(t.from)<=r&&(i=t.node);return i}var tv=.6,nv=1.5;function rv(e,t=Z_){return e===`inverted`||e===`gear-table`?Math.PI:e===`bank-left-45`?(t[`f07.skin-right`]??Z_[`f07.skin-right`])*Math.PI/180:e===`bank-right-45`?(t[`f07.skin-left`]??Z_[`f07.skin-left`])*Math.PI/180:0}var iv=.5,av=.65,ov=e=>e===`bank-left-45`||e===`bank-right-45`,sv=e=>ov(e)?iv:1,cv=e=>ov(e)?av:1,lv=(e,t)=>e!==`on-gear`&&t!==`on-gear`,uv=3.4,dv={rollover_inserts:`rollover`,extrusions:`strut`,gear_tubes:`strut`,axles:`strut`,strut:`wheels`,side_right:`side_left`,top_longeron_left:`side_left`,top_longeron_right:`side_left`,step:`side_left`,carved_corners:`bottom`,belt_insert:`bottom`,belt_attach:`bottom`};function fv(e,t){let n=dv[e];return!n||!t(n)}var pv=e=>e===`gear-table`?11:0,mv=(e,t)=>{let n=Math.abs(Math.cos(e)),r=Math.abs(Math.sin(e));return t.h*(n>1-1e-12?1:n)+t.w*(r<1e-12?0:r)},hv=e=>e<.5?4*e*e*e:1-(-2*e+2)**3/2;function gv(e,t,n,r,i=Z_){let a=Math.min(1,Math.max(0,n)),o=hv(a),s=rv(e,i),c=rv(t,i),l=c-s;l>Math.PI+1e-9?l-=2*Math.PI:l<-Math.PI-1e-9&&(l+=2*Math.PI);let u=a>=1?c:a<=0?s:s+l*o,d=a>=1?pv(t):a<=0?pv(e):pv(e)+(pv(t)-pv(e))*o;return{angle:u,lift:a<=0||a>=1?d+mv(u,r):d+mv(u,r)+nv*Math.sin(Math.PI*o)}}var _v=[300,1500];function vv(e){let[t,n]=_v;return e>t?e>=n?1:Math.log(e/t)/Math.log(n/t):0}function yv(e,t,n,r){let i=t?n.indexOf(t):n.length,a=-1,o=`fwd`;for(let t of Object.values(r)){if(t.part!==e)continue;let r=n.indexOf(t.op);r<0||r>i||r<a||(t.region.startsWith(`face:fwd`)?(a=r,o=`fwd`):t.region.startsWith(`face:aft`)&&(a=r,o=`aft`))}return o}function bv(e,t){if(!e.length)return 0;if(t<=e[0][0])return e[0][1];for(let n=1;n<e.length;n++){let[r,i]=e[n-1],[a,o]=e[n];if(t<=a)return i+(o-i)*(t-r)/(a-r)}return e[e.length-1][1]}var xv={extent:10,depth:-200},Sv=e=>(e+xv.extent)/(xv.extent-xv.depth),Cv={min:22,max:125.5},wv={min:-6.8,max:125.5},Tv={min:22,max:130},Ev={min:-6.8,max:160},Dv=e=>e===13?wv:e!==null&&e>=21&&e<=26?Ev:e!==null&&e>=14&&e<=20?Tv:Cv,Ov=e=>`FS ${Math.round(e*10)/10}`,kv=.001,Av=(e,t)=>e.fs_max<t-kv,jv=(e,t)=>e.fs_min-.001<=t&&t<=e.fs_max+.001;function Mv(e){return e.inOp?3:e.cut?2:+!!e.fitted}function Nv(e,t,n){return Object.entries(e).filter(([e,r])=>r.fs_min-.001<=t&&t<=r.fs_max+.001&&(!n||n.has(e))).sort(([,e],[,t])=>e.op_index-t.op_index||e.op_order-t.op_order).map(([e,t])=>({node:e,part:t.part,cloth:t.cloth}))}function Pv(e,t,n){let r=e=>e.startsWith(`side_`)?0:e.startsWith(`top_longeron`)?1:e===`bottom`?3:2,i=Object.keys(e).filter(e=>t.includes(e)||n.some(t=>t.part===e)).sort((t,n)=>r(t)-r(n)||(e[t]?.fs_min??0)-(e[n]?.fs_min??0)||t.localeCompare(n));return i.length?i.map(t=>{let r=new Map;for(let e of n)e.part===t&&r.set(e.cloth,(r.get(e.cloth)??0)+1);let i=e[t]?.label??t;return r.size?`${i}: ${[...r].map(([e,t])=>`${t} ${e}`).join(`, `)}`:i}).join(` · `):`Nothing in the jig is cut here`}var Fv=e=>(Math.round(e*10)/10).toFixed(1);function Iv(e){if(!e)return{value:`not yet computed`,sub:`no mass ledger in this build`};let{cg:t,cg_lower_bound:n}=e,r=e.gear?.rows??[],i=r.filter(e=>n?.included.includes(e.name)),a=i.reduce((e,t)=>e+t.weight_lb,0),o=(n?.included.length??0)-i.length,s=i.map(e=>e.label.toLowerCase().replace(/ gear strut$/,``)),c=i.every(e=>/ gear strut$/i.test(e.label))?`${s.join(` and `)} strut${s.length>1?`s`:``}`:s.join(`, `),l=i.length?` and ${Fv(a)} lb of gear (${c})`:``,u=n&&n.weight_lb>0&&n.arm_in!=null?`≥ ${Fv(n.weight_lb)} lb at FS ${Fv(n.arm_in)}, lower bound, ${o} parts${l}`:null,d=r.filter(e=>e.status===`unsourced`).map(e=>`${e.label.replace(/\s*\(unsourced\)\s*$/,``)}: excluded, no source`);if(t.weight_lb>0&&t.arm_in!=null){let e=Object.keys(t.excluded).length;return{value:`${Fv(t.weight_lb)} lb at FS ${Fv(t.arm_in)}`,sub:`${t.included.length} parts${e?`; ${e} not yet computed`:``}`}}let f=Object.values(t.excluded),p=t.included.length+f.length,m=new Map;for(let e of f){let t=e.replace(/^not yet computed:\s*/,``).replace(/\s*\(.*\)\s*$/,``).replace(/\b(Left|Right) (\w)/g,(e,t,n)=>n.toLowerCase());m.set(t,(m.get(t)??0)+1)}let h=[...m].sort((e,t)=>t[1]-e[1]||e[0].localeCompare(t[0])),g=h.slice(0,2).map(([e,t])=>`${e} (${t})`).join(`; `)+(h.length>2?`; ${h.length-2} more`:``),_=`${f.length} of ${p} parts have no sourced mass${g?`: ${g}`:``}`,v=C_(e.gear?.nose_arm_candidates,e.gear?.nose_arm_candidates_status);return{value:`not yet computed`,sub:[_,...d,...v?[v]:[],...u?[u]:[]].join(` · `)}}var Lv=e=>{let t=/^not yet computed:?\s*(.*)$/.exec(e??``);return!t||/\d/.test(e??``)?`not yet computed`:t[1]?`not yet computed (${t[1]})`:`not yet computed`};function Rv(e){let t=e?.gear?.ground_handling;if(!t)return null;let n=t.nose_wheel_wl===void 0?[]:[`nose wheel W.L. ${t.nose_wheel_wl} (CP25 LPC 24)`];return{value:`Main axle F.S. ${t.main_axle_fs} (book)`,sub:[`${t.tip_back_line_deg}° tip-back line from the main tyre contact (p171)`,...n,`tip-back check: ${Lv(t.tip_back_check)}`,`tip-over check: ${Lv(t.tip_over_check)}`].join(` · `)}}function zv(e,t,n){let r=e?.prototype_weights?.rows?.spar;return!r||!t||n.indexOf(t)<n.indexOf(`f14.bond-spar`)||![14,15,16,17].includes(Number(/^f(\d+)\./.exec(t)?.[1]))?null:{value:`Spar (CP26 builder weight, N26MS): ${r.weight_lb.toFixed(1)} lb, reference, not in CG`,sub:r.note}}var Bv=1.4,Vv=`Set the canard on F22 (chapter 30, install and align)`,Hv=e=>e<.5?4*e*e*e:1-(-2*e+2)**3/2;function Uv(e,t=7,n=24){return e>0?e>=t?0:n*(1-Hv(e/t)):n}function Wv(e,t=7){return 1-Uv(e,t,1)}var Gv=e=>e<.5?4*e*e*e:1-(-2*e+2)**3/2,Kv=e=>`dur`in e?e.dur:`orbit`in e?e.orbit.dur:0,qv=class{hooks;steps=[];idx=0;t0=0;active=!1;busy=!1;seg=-1;duration=0;onEnd=null;cursor;cx=-100;cy=-100;move=null;drag=null;orbit=null;cardAnim=null;cardOpacity=0;clickT=-10;ring;ripple;card;constructor(e){this.hooks=e;let t=document.createElement(`div`);t.id=`cursor`,t.setAttribute(`aria-hidden`,`true`),t.innerHTML=`<svg width="30" height="30" viewBox="0 0 30 30"><circle cx="15" cy="15" r="11" fill="rgba(255,255,255,0.10)" stroke="rgba(255,255,255,0.9)" stroke-width="1.6"/></svg>
      <svg class="arrow" width="18" height="22" viewBox="0 0 18 22"><path d="M2 1.5v16.2l4.3-4.1 2.9 6.6 2.7-1.2-2.9-6.5h6.1z" fill="#fff" stroke="#0b0f17" stroke-width="1.3" stroke-linejoin="round"/></svg>
      <span class="ripple"></span>`,document.body.appendChild(t),this.cursor=t,this.ring=t.querySelector(`svg`),this.ripple=t.querySelector(`.ripple`);let n=document.createElement(`div`);n.id=`endcard`,n.setAttribute(`aria-hidden`,`true`),n.innerHTML=`<div class="ec-in"><span class="ec-t"></span><span class="ec-s"></span></div>`,document.body.appendChild(n),this.card=n}center(e,t=0,n=0){let r=document.querySelector(e);if(!r)return{x:this.cx,y:this.cy};let i=r.getBoundingClientRect();return{x:i.left+i.width/2+t,y:i.top+i.height/2+n}}thumb(e,t){let n=e.getBoundingClientRect(),r=Number(e.min),i=Number(e.max);return{x:n.left+8+(n.width-16)*(t-r)/(i-r||1),y:n.top+n.height/2}}setCard(e){this.cardOpacity=e,this.card.style.opacity=e.toFixed(3),this.card.style.display=e>.001?`grid`:`none`}load(e){this.steps=e.slice().sort((e,t)=>e.t-t.t),this.duration=Math.max(...this.steps.map(e=>e.t+Kv(e)))+.6,this.idx=0,this.active=!0,this.seg=0,this.move=this.drag=this.orbit=this.cardAnim=null,this.setCard(0),this.cx=window.innerWidth*.82,this.cy=window.innerHeight*1.05}start(e){this.t0=e}stop(){this.active=!1,this.busy=!1,this.setCard(0),this.cursor.style.opacity=`0`,this.move=this.drag=this.orbit=this.cardAnim=null}update(e){if(!this.active)return;let t=e-this.t0;this.busy=!0;try{for(;this.idx<this.steps.length&&this.steps[this.idx].t<=t;){let e=this.steps[this.idx++];if(`move`in e){let t=this.center(e.move,e.dx,e.dy);this.move={x0:this.cx,y0:this.cy,x1:t.x,y1:t.y,t:e.t,dur:e.dur}}else if(`click`in e)this.clickT=e.t,document.querySelector(e.click)?.click();else if(`drag`in e){let t=document.querySelector(e.drag);t&&(this.drag={el:t,from:e.from,to:e.to,t:e.t,dur:e.dur})}else`act`in e?this.hooks.act(e.act,e.arg,e.op):`cursor`in e?this.cursor.style.opacity=e.cursor===`show`?`1`:`0`:`orbit`in e?this.orbit={t:e.t,dur:e.orbit.dur,deg:e.orbit.deg,first:!0}:`card`in e?(e.card&&(this.card.querySelector(`.ec-t`).textContent=e.card.title,this.card.querySelector(`.ec-s`).textContent=e.card.sub??``),this.cardAnim={from:this.cardOpacity,to:+!!e.card,t:e.t,dur:e.dur}):`seg`in e&&(this.seg=e.seg);if(!this.active)return}if(this.move){let e=Math.min(1,(t-this.move.t)/this.move.dur),n=Gv(e),r=this.move,i=Math.sin(Math.PI*n)*Math.min(60,Math.hypot(r.x1-r.x0,r.y1-r.y0)*.12),a=-(r.y1-r.y0),o=r.x1-r.x0,s=Math.hypot(a,o)||1;this.cx=r.x0+(r.x1-r.x0)*n+a/s*i,this.cy=r.y0+(r.y1-r.y0)*n+o/s*i,e>=1&&(this.move=null)}if(this.drag){let e=this.drag,n=Math.min(1,(t-e.t)/e.dur),r=e.from+(e.to-e.from)*Gv(n),i=String(Math.round(r));e.el.value!==i&&(e.el.value=i,e.el.dispatchEvent(new Event(`input`,{bubbles:!0})));let a=this.thumb(e.el,r);this.cx=a.x,this.cy=a.y,n>=1&&(this.drag=null)}if(this.orbit){let e=this.orbit,n=Math.min(1,Math.max(0,(t-e.t)/e.dur));this.hooks.orbit(n,e.deg,e.first),e.first=!1,n>=1&&(this.orbit=null)}}finally{this.busy=!1}if(this.cardAnim){let e=this.cardAnim,n=Math.min(1,Math.max(0,(t-e.t)/e.dur));this.setCard(e.from+(e.to-e.from)*Gv(n)),n>=1&&(this.cardAnim=null)}let n=(t-this.clickT)/.55;n>=0&&n<=1?(this.ripple.style.opacity=(.9*(1-n)).toFixed(3),this.ripple.style.transform=`scale(${(.3+1.1*n).toFixed(3)})`):this.ripple.style.opacity=`0`;let r=t-this.clickT>=0&&t-this.clickT<.14||!!this.drag;this.ring.style.transform=r?`scale(0.8)`:`scale(1)`,this.cursor.style.transform=`translate(${this.cx.toFixed(1)}px, ${this.cy.toFixed(1)}px)`,t>this.duration&&(this.stop(),this.onEnd?.())}},Jv=2.5,Yv=e=>((e-1)*ah+eh)/Jv+.35;function Xv(e,t){let n=e.layup?.semi_span??70,r=0;for(let i of Object.values(e.layup?.nodes??{}))i.op===t&&(r=Math.max(r,i.bl_max??n));return r}function Zv(e,t){let n=t.includes(`shear-web`)?10:20;return Math.max(0,Math.min(n,Xv(e,t)))}var Qv=`#section-on`,$v=`#section-bl`,ey=20;function ty(e,t,n){let r=Im(e,t).find(e=>e.id===n);return r&&Ch(e,t,r.chapter).length?r.chapter:Rm(e,t)[0]?.chapter}function ny(e,t,n){let r=Ch(e,t,n),i=t=>Object.values(e.plies??{}).flat().filter(e=>e.op===t).length,a=!!e.layup?.nodes,o=e.layup?.semi_span??70,s=Math.round(o/2),c=[],l=t===`gu`?`GU`:`Roncz`,u=n===11;c.push({t:0,act:`reset`},{t:0,seg:0}),c.push({t:0,card:u?{title:ay(n)}:{title:`${l} canard`,sub:`Chapter ${n}`},dur:.4},{t:2.3,card:null,dur:.6}),c.push({t:2.6,cursor:`show`});let d=3;r.forEach((t,n)=>{let r=`#chips button[data-op="${t.op}"]`;c.push({t:d,move:r,dur:.55},{t:d+.6,click:r},{t:d+.6,seg:n});let o=i(t.op);if(!o){d+=.6+Math.max(1.7,D_[t.op]??0);return}if(d+=2.5,c.push({t:d,move:`#play`,dur:.4},{t:d+.45,click:`#play`}),d+=.5+Yv(o),a){let n=Zv(e,t.op);c.push({t:d,move:Qv,dur:.4},{t:d+.45,click:Qv}),c.push({t:d+.6,drag:$v,from:s,to:n,dur:1.1}),s=n,c.push({t:d+3,move:Qv,dur:.4},{t:d+3.45,click:Qv}),d+=3.9}});let f=u?r.at(-1)?.op:void 0;return c.push(f?{t:d,act:`finish`,op:f}:{t:d,act:`finish`}),a&&!u&&(c.push({t:d+.2,move:Qv,dur:.4},{t:d+.7,click:Qv}),s!==ey&&c.push({t:d+.9,drag:$v,from:s,to:ey,dur:1})),c.push({t:d+1.9,cursor:`hide`}),u||c.push({t:d+2,act:`closeup`}),c.push({t:d+4,orbit:{dur:9,deg:-40}}),c.push({t:d+13.4,card:{title:u?`Elevators, chapter ${n}`:`Canard, chapter ${n}`,sub:`Build rehearsal`},dur:1}),c.push({t:d+16.2,act:`noop`}),c}var ry={11:`Roncz elevators`,4:`Bulkheads and panels`,5:`Fuselage sides`,6:`Fuselage assembly`,7:`Fuselage exterior`,8:`Roll-over structure and seat belts`,9:`Main landing gear`,12:`Canard installation`,13:`Nose and nose gear`,14:`Centre-section spar`,15:`Firewall`,16:`Controls`,17:`Trim`,18:`Canopy`,19:`Wings`,20:`Winglets and rudders`,21:`Strakes and fuel`,22:`Electrical system`,23:`Engine and cowl`,24:`Covers and consoles`,25:`Finishing`,26:`Upholstery`},iy=new Set([12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]),ay=e=>`Chapter ${e} \u2014 ${ry[e]??`Fuselage`}`,oy={6:72,8:80,14:121.7},sy={80:{dist:98,lift:.2}},cy=tv+1,ly=3.6,uy=110;function dy(e,t,n){let r=z_(e,t).find(e=>e.id===n);return r?L_.includes(r.chapter)?[...L_]:[r.chapter]:[...I_]}function fy(e,t,n,r=[4,5,6]){let i=r.filter(n=>Ch(e,t,n).length),a=i.length===1,o=a?oy[i[0]]:void 0,s=[];s.push({t:0,act:`reset`},{t:0,seg:0}),s.push({t:0,card:a?{title:ay(i[0])}:{title:`Fuselage box`,sub:`Chapters ${r[0]}\u2013${r[r.length-1]}`},dur:.4},{t:2.3,card:null,dur:.6}),s.push({t:2.6,cursor:`show`});let c=3,l=0;i.forEach((r,i)=>{i&&(s.push({t:c,card:{title:ay(r)},dur:.4},{t:c+1.6,card:null,dur:.5}),c+=2.3);for(let i of Ch(e,t,r)){let e=`#chips button[data-op="${i.op}"]`;s.push({t:c,move:e,dur:.55},{t:c+.6,click:e},{t:c+.6,seg:l++});let t=n(i.op),r=i.op in Z_||i.op===`f09.position-gear`,a=i.op===`f09.position-gear`?cy+ly:r?Math.max(t?1.9:1.7,cy+.9):t?1.9:1.7;if(!t){c+=.6+Math.max(a,D_[i.op]??0);continue}c+=.6+a,s.push({t:c,move:`#play`,dur:.4},{t:c+.45,click:`#play`}),c+=.5+Yv(t)}});let u=i.length>0&&i.every(e=>L_.includes(e))?Ch(e,t,i[i.length-1]).at(-1)?.op:o!==void 0||a&&iy.has(i[0])?Ch(e,t,i[0]).at(-1)?.op:void 0;return s.push(u?{t:c,act:`finish`,op:u}:{t:c,act:`finish`}),o!==void 0&&(s.push({t:c+.2,move:Qv,dur:.4},{t:c+.7,click:Qv}),s.push({t:c+.8,act:`cutclose`,arg:o}),s.push({t:c+.9,drag:$v,from:70,to:uy,dur:1}),s.push({t:c+2,drag:$v,from:uy,to:o,dur:1.2}),c+=2),s.push({t:c+1.9,cursor:`hide`}),o===void 0?(s.push({t:c+2,act:`closeup`}),s.push({t:c+4,orbit:{dur:9,deg:-40}})):s.push({t:c+2.8,orbit:{dur:10.4,deg:-40}}),s.push({t:c+13.4,card:a?{title:`Fuselage, chapter ${i[0]}`,sub:`Build rehearsal`}:{title:`Fuselage box`,sub:`Build rehearsal`},dur:1}),s.push({t:c+16.2,act:`noop`}),s}var py=4.4,my=6.5,hy=2.3;function gy(e,t){let n=Ch(e,t,12),r=[];r.push({t:0,act:`reset`},{t:0,seg:0}),r.push({t:0,card:{title:ay(12)},dur:.4},{t:2.3,card:null,dur:.6}),r.push({t:hy,act:`lower`,arg:7,op:n[0]?.op});let i=hy+Bv+7+.6;return r.push({t:i-.4,cursor:`show`}),n.forEach((e,t)=>{let n=`#chips button[data-op="${e.op}"]`;r.push({t:i,move:n,dur:.55},{t:i+.6,click:n},{t:i+.6,seg:t}),i+=.6+Math.max(py,D_[e.op]??0)}),r.push({t:i,act:`finish`,op:n.at(-1)?.op}),r.push({t:i+.1,cursor:`hide`}),r.push({t:i+.2,act:`closeup`}),r.push({t:i+.2+1.8+my,act:`noop`}),r}var _y=[`side_right`,`side_left`],vy=(e,t,n,r)=>({focus:{parts:[e]},dist:t,el:n,az:r}),yy={"f04.front-seat-bkhd-front":vy(`front_seat_bkhd`,66,54,16),"f04.front-seat-bkhd-back":vy(`front_seat_bkhd`,66,54,16),"f04.rear-seat-bkhd-foam":vy(`rear_seat_bkhd`,58,54,12),"f04.rear-seat-bkhd-hole":vy(`rear_seat_bkhd`,58,54,12),"f04.panel-f22-f28-aft":{focus:{parts:[`panel`,`f22`,`f28`]},dist:84,el:54,az:6},"f04.panel-f22-f28-fwd":{focus:{parts:[`panel`,`f22`,`f28`]},dist:84,el:54,az:6},"f04.firewall-aft":vy(`firewall`,56,54,-10),"f04.firewall-fwd":vy(`firewall`,56,54,-10),"f05.side-blank":{focus:{parts:_y},dist:128,el:55,az:8},"f05.side-profile":{focus:{parts:_y},dist:128,el:55,az:8},"f05.side-layout":{focus:{parts:_y},dist:120,el:52,az:10},"f05.inside-layup":{focus:{parts:_y},dist:118,el:50,az:14},"f05.top-longeron-glass":{focus:{parts:_y,fs:55},dist:80,el:42,az:24},"f05.lower-longeron":{focus:{parts:_y,fs:70},dist:84,el:42,az:18},"f05.gear-pad":{focus:{parts:_y,fs:112},dist:60,el:48,az:-22},"f05.spar-cutout":{focus:{parts:_y,fs:120},dist:54,el:48,az:-26},"f05.gear-extrusions":{focus:{parts:_y,fs:112},dist:60,el:44,az:-22},"f06.trial-fit":{focus:`box`,dist:132,el:38,az:20},"f06.jig-check":{focus:`box`,dist:132,el:26,az:6},"f06.bond-front-seat":vy(`front_seat_bkhd`,92,44,24),"f06.bond-panel":vy(`panel`,92,44,28),"f06.bond-f22":vy(`f22`,90,44,32),"f06.bond-rear-seat":vy(`rear_seat_bkhd`,92,44,-18),"f06.bond-firewall":vy(`firewall`,92,42,-30),"f06.f28-install":vy(`f28`,86,44,34),"f06.rear-seat-tape":vy(`rear_seat_bkhd`,84,48,-14),"f06.bottom-foam-fit":{focus:`box`,dist:132,el:40,az:14},"f06.bottom-contour":{focus:`box`,dist:124,el:30,az:20},"f06.bottom-glass":vy(`bottom`,124,58,8),"f06.bottom-bond":{focus:`box`,dist:132,el:36,az:18},"f06.bottom-tape":{focus:`box`,dist:108,el:60,az:10},"f07.carve-corners":{focus:{parts:[`side_left`],fs:46},dist:70,el:20,az:34},"f07.canard-cutout":vy(`canard_cutout`,72,34,38),"f07.fuel-gauge-area":{focus:{parts:[`side_left`],fs:100},dist:70,el:22,az:-12},"f07.belt-insert":vy(`belt_insert`,52,8,18),"f07.skin-right":{focus:`box`,dist:150,el:24,az:136},"f07.skin-left":{focus:`box`,dist:134,el:34,az:12},"f08.roll-over-foam":vy(`rollover`,64,52,24),"f08.roll-over-inside":vy(`rollover`,52,62,20),"f08.roll-over-bond":vy(`rollover`,84,34,-34),"f08.roll-over-outside":vy(`rollover`,64,26,36),"f08.access-holes":vy(`rollover`,58,30,-62),"f08.shoulder-harness":vy(`rollover`,56,52,18),"f08.belt-attach":vy(`belt_attach`,92,58,10),"f08.step":vy(`step`,44,14,24),"f09.strut-stiffen":vy(`strut`,118,52,8),"f09.jig-blocks":vy(`jig_blocks`,56,14,-34),"f09.position-gear":{focus:`marks`,dist:118,el:16,az:-18},"f09.tab-layup":vy(`strut`,104,34,-18),"f09.tab-assembly":vy(`gear_tubes`,62,40,-30),"f09.axles-brakes":{focus:{parts:[`axles`],side:`right`},dist:42,el:14,az:-30},"f09.brake-lines":vy(`strut`,112,30,-12)},by=(e,t,n=0)=>({at:[e,t-17.4,-n]}),xy=(e,t,n,r=12,i=40,a=0)=>({focus:by(e,t),dist:n,el:r,az:i,pan:a}),Sy=(e,t=28,n=28,r=0,i=0)=>({focus:`bench`,dist:e,el:t,az:n,pan:r,up:i}),Cy=(e,t,n=72,r=16,i=-38)=>({focus:by(e,19,t),dist:n,el:r,az:i}),wy={"r30.f22-drill-tabs":Cy(35,-14,62,22,-52),"r30.elev-fuselage-clearance":Cy(35,-8,54,20,-58),"r30.lift-tab-bushings":Cy(35,-16,60,24,-46),"r30.f28-pins-permanent":Cy(36,-12,66,22,-56),"f13.strut-reinforce":Sy(90,32,30,10,7),"f13.worm-drive-bench":Sy(90,32,30,10,7),"f13.ng30-plates":Sy(84,32,30,10,7),"f13.ng-box-assemble":Sy(90,32,30,10,7),"f13.ng3-ng4":Sy(90,32,30,10,7),"f13.ng31-f6":xy(10,2,80,12,40,5),"f13.floor-blocks":xy(8,2,74,16),"f13.pedal-pivot-blocks":xy(10,2,74,16),"f13.side-pieces":xy(8,4,82,14),"f13.canard-attach-reinforce":Cy(35,-16,62,22,-50),"f13.rudder-pedals":xy(10,2,76,14),"f13.lower-gear":xy(8,-9,92,8),"f13.strut-slot-sc":xy(8,-8,92,8),"f13.nb-box":xy(14,-4,98,10),"f13.rig-nose-gear":xy(22,-8,122,8,36),"f13.pitot-static":xy(14,8,100,12,40,6),"f13.top-foam":xy(8,8,88,14),"f13.carve-glass-nose":xy(8,-2,102,10),"f13.nose-door":{focus:{parts:[`nose_door`]},dist:52,el:44,az:64,pan:4,up:9},"f13.shock-strut":xy(24,5,100,14,40,8)},Ty=(e,t,n=52,r=0,i=0,a=0)=>({focus:{spar:e},dist:t,el:n,az:r,pan:i,up:a}),Ey={"f14.jig":Ty(-26,96,56,0,0,4),"f14.foam-box":Ty(0,124,42,0,0,7),"f14.cs4-forward":Ty(0,124,42,0,0,7),"f14.lwa-fabricate":Ty(-25,50,52,180,0,2),"f14.interior-layups":Ty(-27,52,52,180,0,2),"f14.close-box":Ty(0,124,42,0,0,7),"f14.cap-troughs":Ty(0,124,42,0,0,7),"f14.shearweb-lwa45":Ty(-53,100,42,0,0,7),"f14.spar-caps":Ty(-32,104,42,0,0,7),"f14.spruce-layup6":Ty(-7.5,100,42,0,0,7),"f14.lwa23-layup7":Ty(-53,100,42,0,0,7),"f14.baggage-hole":Ty(0,124,42,0,0,7),"f14.end-bulkhead-layup9":Ty(-56,100,42,0,0,7),"f14.nut-access-hole":Ty(-53,100,42,0,0,7),"f14.fit-fuselage":{focus:by(121.7,17.75),dist:135,el:30,az:-90},"f14.bond-spar":{focus:by(121.7,17.75),dist:95,el:40,az:-70},"f14.sh1-tabs":{focus:by(120.6,22,0),dist:36,el:58,az:-40},"f15.parts-fab":{focus:by(125,15),dist:110,el:28,az:-70},"f15.stainless-firewall":{focus:by(125.5,15),dist:70,el:20,az:-80},"f15.belcrank-brackets":{focus:by(126,10,4),dist:34,el:20,az:-78},"f15.master-cylinders":{focus:by(127,17.75,3),dist:38,el:22,az:-76},"f16.side-consoles":{focus:by(78,13,6),dist:100,el:62,az:-20},"f16.pivot-bulkheads":{focus:by(78,13,6),dist:100,el:62,az:-20},"f16.firewall-bearing":{focus:by(118,12.3,6),dist:40,el:55,az:-30},"f16.torque-tubes":{focus:by(85,12.3,6),dist:70,el:62,az:-20},"f16.sticks-pushrods":{focus:by(47,16,5),dist:42,el:58,az:-60},"f16.pitch-pushrod":{focus:by(34,18,2),dist:145,el:44,az:-66},"f16.aileron-linkage":{focus:by(70,15,6),dist:110,el:58,az:-20},"f16.rudder-conduit":{focus:by(100,8,5),dist:55,el:58,az:-25},"f16.rudder-cable-rig":{focus:by(112,9,5),dist:45,el:55,az:-40},"f16.brake-cables":{focus:by(126,17.75,3),dist:40,el:24,az:-70},"f16.adjustable-pedals":{focus:by(20,8,0),dist:90,el:35,az:40},"f17.mount-blocks":{focus:by(82,13,6),dist:44,el:66,az:-62},"f17.parts":{focus:by(64,10,-3),dist:100,el:55,az:165},"f17.pitch-trim":{focus:by(45,9,-9.5),dist:38,el:56,az:165},"f17.roll-trim":{focus:by(82,13,6),dist:30,el:64,az:-20},"f17.fixed-trim-tab":{focus:by(45,9,-9.5),dist:60,el:52,az:165}},Dy={"f18.trim-plexi":{focus:{canopy:`bench-up`},dist:104,el:36,az:0,up:5},"f18.locate-blocks":{focus:by(86,27,-4),dist:100,el:34,az:14,up:4},"f18.check-ab":{focus:by(96,30,-4),dist:108,el:12,az:6,up:7},"f18.foam-core":{focus:by(66,25,-10),dist:74,el:36,az:18,up:3},"f18.carve-outside":{focus:by(66,25,-10),dist:74,el:36,az:18,up:3},"f18.glass-outside":{focus:by(54,25.5,-9),dist:58,el:42,az:28,up:3},"f18.cut-remove":{focus:{canopy:`mid`},dist:200,el:30,az:8},"f18.carve-inside":{focus:{canopy:`bench-down`},dist:132,el:55,az:0,up:6},"f18.pads-inside-glass":{focus:{canopy:`bench-down`},dist:132,el:55,az:0,up:6},"f18.rear-cover-inside":{focus:by(121,28,0),dist:60,el:40,az:-40},"f18.vent-brace":{focus:{canopy:`bench-down`},dist:104,el:52,az:0,up:5},"f18.hinges":{focus:by(80,32,4),dist:150,el:22,az:62},"f18.door":{focus:by(50,19,-12),dist:40,el:26,az:12,up:2},"f18.latches":{focus:by(60,25.5,-12.5),dist:56,el:34,az:26,up:2,pan:-9},"f18.front-cover":{focus:by(40,27,0),dist:60,el:34,az:24},"f18.safety-catch":{focus:by(57,24,-12),dist:34,el:24,az:10,up:2}},Oy=(e,t,n,r,i={})=>{let{fs:a,z:o,...s}=i;return{focus:{wing:{bl:e,fs:a,z:o}},dist:t,el:n,az:r,...s}},ky={"f19.jig":Oy(90,270,22,26,{pan:-10,up:-4}),"f19.cut-cores":Oy(90,270,50,0,{pan:-10,up:6}),"f19.core-cutouts":Oy(42,150,50,0,{pan:-22,up:6}),"f19.mount-cores":Oy(90,270,22,26,{pan:-10,up:-4}),"f19.hardpoints":Oy(60,215,52,22,{fs:138,pan:-10,up:-2}),"f19.shear-web":Oy(90,270,22,26,{pan:-10,up:-4}),"f19.pads-plates":Oy(60,215,52,22,{fs:138,pan:-10,up:-2}),"f19.le-cores":Oy(90,270,22,26,{pan:-10,up:-4}),"f19.bottom-cap":Oy(90,270,50,0,{pan:-10,up:6}),"f19.bottom-skin":Oy(90,270,50,0,{pan:-10,up:6}),"f19.top-cap":Oy(90,270,22,26,{pan:-10,up:-4}),"f19.rudder-conduit":Oy(120,150,24,20,{pan:-12,up:0}),"f19.top-skin":Oy(90,270,22,26,{pan:-10,up:-4}),"f19.ribs":Oy(36,120,22,14,{pan:-16,up:-2}),"f19.aileron-cut":Oy(88,190,24,22,{pan:-12,up:-2}),"f19.aileron-build":Oy(88,190,24,22,{pan:-12,up:-2}),"f19.controls":Oy(48,180,40,40,{fs:142,pan:-10,up:-2}),"f19.attach":{focus:by(134,20,0),dist:125,el:38,az:80,pan:-6},"f20.cut-cores":Oy(157,120,48,0,{pan:-8,up:4}),"f20.skins":Oy(157,120,48,0,{pan:-8,up:4}),"f20.trim":Oy(157,120,48,0,{pan:-8,up:4}),"f20.jig":{focus:by(172,30,108),dist:210,el:24,az:22,pan:-10},"f20.inside-layups":{focus:by(178,40,156),dist:120,el:22,az:24,pan:-12},"f20.outside-layups":{focus:by(178,40,156),dist:120,el:22,az:24,pan:-12},"f20.lower-fin":{focus:by(178,24,158),dist:120,el:16,az:24,pan:-12},"f20.rudder-cut":{focus:by(182,38,158),dist:100,el:20,az:24,pan:-10},"f20.rudder-hang":{focus:by(180,36,160),dist:55,el:14,az:24,pan:-8}},Ay=(e,t,n,r,i,a,o={})=>({focus:by(e,n,t),dist:r,el:i,az:a,...o}),jy={"f21.cut-parts":{focus:`strake-table`,dist:150,el:58,az:0,up:0},"f21.fuselage-cutouts":Ay(76,-12,14,120,24,16),"f21.jig-bond":Ay(88,-32,15,205,52,14),"f21.inside-layups":Ay(94,-32,17,190,54,14),"f21.vent-screen":Ay(111,-14,17,56,40,8),"f21.close-tank":Ay(98,-30,17,200,56,14),"f21.od-outlet":Ay(106,-32,17,170,54,20),"f21.outside-bottom":Ay(104,-26,14,190,48,14),"f21.outside-top":Ay(90,-32,18,210,54,14),"f21.pressure-check":Ay(98,-30,17,200,56,14),"f21.fairing-caps":Ay(104,-38,18,150,50,16),"f21.plumbing":Ay(90,0,14,240,42,20),"f22.panel-wiring":Ay(39,0,9,62,40,-28),"f22.microswitches":Ay(39,0,9,62,40,-28),"f22.battery-shelf":Ay(11,0,3,44,34,38),"f22.firewall-terminals":Ay(26,4,5,70,32,40),"f22.wing-wiring":Ay(145,95,19,250,62,18),"f22.antennas":Ay(34,-10,14,150,34,30),"f23.engine-install":Ay(142,0,20,110,24,-48),"f23.carb-bracket":Ay(134,0,14,74,24,-42),"f23.cowl-trim":Ay(137,0,21,112,26,-46),"f23.cowl-closeout":Ay(137,0,21,112,26,-46),"f23.root-rib":Ay(137,-23,18,84,-16,-38)},My=(e,t,n,r,i,a,o={})=>({focus:by(e,n,t),dist:r,el:i,az:a,...o}),Ny=(e={})=>My(60,0,16,800,50,0,{outside:!0,up:150,...e}),Py={"f24.aft-cover":My(116,0,0,55,-15,270,{outside:!0}),"f24.console-lc1":My(54,-9,10,60,52,185),"f24.consoles-left":My(56,-9,11,70,55,180),"f24.thigh-support":My(46,0,8,60,55,200),"f24.canard-cover":My(25,0,14,60,50,120),"f24.gap-seal":My(116,-23,14,90,40,160),"f25.inspect-repair":Ny(),"f25.coarse-fill":Ny(),"f25.feather-fill":Ny(),"f25.primer":Ny(),"f25.paint-seals":Ny(),"f26.cushions-headrests":My(85,0,10,100,70,90),"f26.suitcases":My(85,0,10,100,70,90)},Fy={focus:`box`,dist:130,el:38,az:16},Iy=e=>yy[e]??wy[e]??Ey[e]??Dy[e]??ky[e]??jy[e]??Py[e]??Fy;function Ly(e){let t=e.el*Math.PI/180,n=e.az*Math.PI/180,r=Math.cos(t)*e.dist;return[-Math.sin(n)*r,Math.sin(t)*e.dist,Math.cos(n)*r]}var Ry={nudge:24,pad:3,dot:13},zy=(e,t)=>e.l<t.r&&t.l<e.r&&e.t<t.b&&t.t<e.b;function By(e,t=[]){let n=e.map((e,t)=>t).sort((t,n)=>e[n].priority-e[t].priority||e[t].tie-e[n].tie||t-n),r=e.map(()=>({dy:0,collapsed:!0,hidden:!1})),i=[],{nudge:a,pad:o,dot:s}=Ry;for(let s of n){let n=e[s];for(let e of[0,-a,a]){let a={l:n.x-n.w/2-o,r:n.x+n.w/2+o,t:n.y+e-n.h/2-o,b:n.y+e+n.h/2+o};if(!(i.some(e=>zy(e,a))||t.some(e=>zy(e,a)))){i.push(a),r[s]={dy:e,collapsed:!1,hidden:!1};break}}}return e.forEach((e,n)=>{if(!r[n].collapsed)return;let a={l:e.x-s/2,r:e.x+s/2,t:e.y-s/2,b:e.y+s/2};r[n].hidden=i.some(e=>zy(e,a))||t.some(e=>zy(e,a))}),r}var Vy=class{root;camera;rule;items=[];v=new W;constructor(e,t,n=null){this.root=e,this.camera=t,this.rule=n}add(e){let t=document.createElement(`div`);t.className=`lbl `+(e.cls??``);let n=document.createElement(`i`);e.color&&(n.style.background=e.color);let r=document.createElement(`span`);r.textContent=e.text,t.append(n,r);let i=null;e.sub&&(i=document.createElement(`em`),t.appendChild(i)),this.root.appendChild(t),this.items.push({...e,el:t,subEl:i,op:0,w:0,x:0,y:0,yAdj:0,on:!1,dot:!1,sized:!1,target:0})}update(e,t,n){let r=this.camera,i=1-Math.exp(-n*9),a=[];for(let n of this.items){let o=n.vis(),s=o>.01?n.at():null,c=0;if(s){this.v.copy(s).project(r);let i=(this.v.x*.5+.5)*e,a=(-this.v.y*.5+.5)*t;this.v.z<1&&this.v.z>-1&&i>36&&i<e-36&&a>36&&a<t-36&&(c=o,n.x=i,n.y=a)}if(n.target=c,n.op+=(c-n.op)*i,n.op<.01&&c===0&&(n.op=0),n.op>0){if(n.subEl&&n.sub){let e=typeof n.sub==`function`?n.sub():n.sub;n.subEl.textContent!==e&&(n.subEl.textContent=e,n.w=0,n.sized=!1)}if(!n.w||this.rule&&!n.sized&&n.on){n.dot&&n.el.classList.remove(`dot`);let e=n.el.offsetWidth;n.w=e||120,n.sized=e>0,n.dot&&n.el.classList.add(`dot`)}a.push(n)}}for(let e of a)e.yAdj=e.y;if(this.rule&&a.length){let e=By(a.map(e=>({x:e.x,y:e.y,w:e.w,h:22,priority:e.target>0?e.priority?.()??0:-1,tie:e.tie?.()??0})),this.rule.obstacles());a.forEach((t,n)=>{t.yAdj=t.y+e[n].dy,e[n].collapsed!==t.dot&&(t.dot=e[n].collapsed,t.el.classList.toggle(`dot`,t.dot)),e[n].hidden!==t.el.classList.contains(`gone`)&&t.el.classList.toggle(`gone`,e[n].hidden)})}for(let e=0;e<(this.rule?0:6);e++){let e=!1;for(let t=0;t<a.length;t++)for(let n=t+1;n<a.length;n++){let r=a[t],i=a[n],o=Math.abs(r.x-i.x),s=r.yAdj-i.yAdj;if(o<(r.w+i.w)/2+6&&Math.abs(s)<26){let t=(26-Math.abs(s))/2+.5,n=s>=0?1:-1;r.yAdj+=n*t,i.yAdj-=n*t,e=!0}}if(!e)break}for(let e of this.items){let t=e.op>.004;t!==e.on&&(e.el.style.display=t?`flex`:`none`,e.on=t),t&&(e.el.style.opacity=e.op.toFixed(3),e.el.style.transform=`translate(${e.x.toFixed(1)}px, ${e.yAdj.toFixed(1)}px) translate(-50%, -50%)`)}}stats(){return this.items.map(e=>this.rule?{id:e.id,text:e.text,opacity:e.op,x:e.x,y:e.yAdj,collapsed:e.dot,hidden:e.el.classList.contains(`gone`)}:{id:e.id,text:e.text,opacity:e.op,x:e.x,y:e.yAdj})}},Q=.0254,Hy={table:{x:-3.9,z:-3.06,topY:Tm,len:120*Q,depth:68*Q},jig:{x:-3.9,z:-1.5,benchTopY:.78,benchLen:85*Q,benchDepth:28*Q,block:{across:30*Q,high:3*Q,along:3.5*Q},blockFs:[37,110]},fsMid:73.75,floor:{z:.3}},Uy=()=>Hy.jig.benchTopY+Hy.jig.block.high,Wy=e=>Hy.jig.x+(e-Hy.fsMid)*Q;function Gy(){let e=new Dn;e.name=`fuselageStation`;let t=new jm({wood:Jp({color:5914414,metalness:0,roughness:.55,detail:5,colorVar:.14,roughVar:.25,name:`plywood`}),top:Jp({color:9071180,metalness:0,roughness:.6,detail:5,colorVar:.1,roughVar:.25,name:`mdf-top`}),steel:Jp({color:10133670,metalness:.9,roughness:.32,detail:3,roughVar:.3}),darksteel:Jp({color:2895667,metalness:.75,roughness:.45,detail:2}),jig:Jp({color:11831896,metalness:0,roughness:.62,detail:9,colorVar:.16,roughVar:.3,name:`mdf`}),peg:Jp({color:16777215,metalness:0,roughness:.85,map:Mm()}),foam:Yp(12175318,.9,{detail:3,colorVar:.05}),foam2:Yp(14731404,.92,{detail:3,colorVar:.05}),red:Yp(11740702,.5),yellow:Yp(14202410,.55),orange:Yp(14383644,.5),housing:Yp(2829359,.6),tube:Nm(16773340,5.5),bucket:Yp(14275784,.55)}),n=Hy.table,r=Hy.jig;t.box(`top`,n.len,.04,n.depth,n.x,n.topY-.02,n.z);let i=n.len/2-.08,a=n.depth/2-.08;for(let e of[-i,0,i])for(let r of[-a,a])t.box(`steel`,.06,n.topY-.04,.06,n.x+e,(n.topY-.04)/2,n.z+r),t.box(`darksteel`,.1,.02,.1,n.x+e,.01,n.z+r);for(let e of[-a,a])t.box(`steel`,n.len-.12,.06,.04,n.x,n.topY-.08,n.z+e);t.box(`steel`,n.len-.12,.04,.04,n.x,.22,n.z),t.box(`wood`,r.benchLen,.05,r.benchDepth,r.x,r.benchTopY-.025,r.z);let o=r.benchLen/2-.07,s=r.benchDepth/2-.06;for(let e of[-o,o])for(let n of[-s,s])t.box(`darksteel`,.07,r.benchTopY-.05,.07,r.x+e,(r.benchTopY-.05)/2,r.z+n),t.box(`darksteel`,.1,.02,.1,r.x+e,.01,r.z+n);for(let e of[-o,o])t.box(`darksteel`,.05,.05,r.benchDepth-.1,r.x+e,.3,r.z);t.box(`darksteel`,r.benchLen-.14,.05,.05,r.x,.3,r.z);for(let e of r.blockFs)t.box(`jig`,r.block.along,r.block.high,r.block.across,Wy(e),r.benchTopY+r.block.high/2,r.z);let c=Em.z0+.02;t.box(`peg`,2.6,1,.03,n.x,1.75,c),t.box(`darksteel`,2.7,.04,.05,n.x,2.27,c+.02);for(let e=0;e<9;e++){let r=n.x-1.1+e*.27,i=1.8-e%3*.12,a=c+.05;e%3==0?(t.box(`darksteel`,.05,.28,.02,r,i,a),t.box(`red`,.07,.1,.03,r,i-.18,a)):e%3==1?t.box(`yellow`,.035,.34,.03,r,i,a):(t.box(`orange`,.07,.18,.04,r,i,a),t.box(`steel`,.02,.12,.03,r,i-.14,a))}for(let e=0;e<3;e++)t.box(e%2?`foam2`:`foam`,1.2,.6,.02,Em.x0+.9+e*.03,.31,c+.25+e*.03);t.cyl(`bucket`,.14,.3,`y`,n.x+n.len/2+.35,.15,n.z+.2,20);for(let e of[n.z+.3,r.z])t.box(`housing`,2.2,.07,.22,n.x,Em.h-.07,e),t.box(`tube`,2.1,.03,.1,n.x,Em.h-.12,e);return t.flush(e,{cast:new Set([`wood`,`top`,`steel`,`darksteel`,`jig`,`foam`,`foam2`,`bucket`]),receive:new Set([`wood`,`top`,`steel`,`darksteel`,`jig`,`peg`,`foam`,`foam2`])}),e.traverse(e=>{e.isMesh&&e.name===`shop.jig`&&(e.userData.representational=!0)}),e.userData.representational=!0,e}var Ky=`f21.cut-parts`,qy=`f21.fuselage-cutouts`,Jy=`f21.vent-screen`,Yy=`f21.close-tank`,Xy=`f21.od-outlet`,Zy=`f21.outside-bottom`,Qy=`f21.pressure-check`,$y=`f21.fairing-caps`,eb=`f21.plumbing`,tb=`f22.panel-wiring`,nb=`f22.battery-shelf`,rb=`f22.firewall-terminals`,ib=`f22.antennas`,ab=`f23.engine-install`,ob=`f23.carb-bracket`,sb=`f23.root-rib`,cb=new Set([`rib_r23`,`rib_r45`,`b23`,`db`,`bab`,`od`,`tle`,`ble`,`skin_bottom`,`skin_top`]),lb=new Set([Yy,Qy]),ub=new Set([qy,Jy,Yy,Xy,Zy,Qy,tb,nb,rb,ib,ob,sb]),db=e=>(Math.round(e*100)/100).toString(),fb=e=>(Math.round(e*10)/10).toFixed(1);function pb(e){return e.node.slice(e.component.length+1).replace(/\.(right|left)$/,``)}function mb(e,t,n){if(!t)return`none`;let r=n.indexOf(t),i=n.indexOf(e.show.from);return r<0||i<0?`none`:e.void?t===e.show.from?`jig`:`none`:e.component.startsWith(`strake.`)&&cb.has(pb(e))&&t===`f21.cut-parts`?e.side===`right`?`table`:`none`:r>=i?`jig`:`none`}var hb=e=>e===Ky;function gb(e,t){if(!e)return!1;let n=t.indexOf(e);return n>=t.indexOf(`f21.jig-bond`)&&n<t.indexOf(`f21.od-outlet`)}var _b=e=>!!e&&ub.has(e.id),vb=(e,t)=>!!e&&(lb.has(e.id)?t===`strake.tank`:e.components.includes(t)),yb={tank:2785232,cutout_baggage:14178122,cutout_tank:14178122},bb=e=>e===`tank`?.6:e.startsWith(`cutout_`)?.55:null;function xb(e){let t=e.fuel;return{value:`Tank capacity: plans 2 x ${db(t.plans_gal_per_tank)} gal, manual 2 x ${db(t.om_gal_per_tank)} gal (${db(t.om_total_gal)} in all); model ${db(t.model_gal_per_side)} a side`,sub:`Unresolved. Shaded envelope ${db(t.envelope_gal_per_side)} gal a side (fitted shape, not measured); fuel ${fb(t.lb_per_gal)} lb per gal at FS ${fb(t.arm_fs)}`}}function Sb(e){let t=e.conflicts.cutout_aft_top_depth,n=e.conflicts.baggage_arm;return{value:`Tank hole aft end: ${db(t.aft_end_in)} in below WL 23 once, ${db(t.mid_in)} in elsewhere on the page`,sub:`Unresolved. Baggage arm: FS ${db(n.om_fs)} in the manual, FS ${db(n.plan_centroid_fs)} from the floor's own centroid; which volume the ${db(n.om_fs)} covers is not known`}}function Cb(e){let[t,n]=e.conflicts.layup_7_numbering;return{value:`Layup 7 is printed twice: inside the outboard diagonal (${t.replace(`f21.`,``)}) and on the outside (${n.replace(`f21.`,``)})`,sub:`Unresolved. Both are laid; the model calls them 7a and 7b`}}function wb(e){let t=e.battery;return{value:`Battery station: FS ${db(t.fs_range[0])} to ${db(t.fs_range[1])}, not printed (A6 only)`,sub:`Drawn at FS ${db(t.model_fs)} for illustration only; the battery adds ${fb(t.added_lb)} lb with its cable and relay (reference, not in CG)`}}function Tb(e){let t=e.battery;return{value:`Starter, ring gear and alternator: station ${db(t.starter_fs_min)} or aft (CP27 page 4), not drawn`,sub:`A bound, not a station. The relays are on F22 near FS ${db(t.relay_fs)}; no engine, mount or starter station is printed`}}function Eb(e){let t=e.engine;return{value:`Engine with accessories at most ${db(t.limits_lb[0])} lb, vibrating mass at most ${db(t.limits_lb[1])} lb; oil ${db(t.oil.lb)} lb at FS ${db(t.oil.fs)}`,sub:`Fitted shape; installation in Section II, not held. O-235 component model (fitted shape) placed from the prop flange, ${db(t.down_thrust_deg)} deg down thrust`}}function Db(e){let t=e.engine.mass;return`component model, CG ${t.cg_from_flange_in.toFixed(2)} in from the flange vs TCDS ${db(t.tcds_cg_from_flange_in)}`}function Ob(e){if(!e.length)return null;let t=new Map,n=0;for(let r of e)t.set(r.cloth,(t.get(r.cloth)??0)+r.plies),n+=r.plies;return{value:`${n} plies: ${[...t].map(([e,t])=>`${t} ${e}`).join(` + `)}`,sub:e.map(e=>`${e.plies} ${e.cloth}, ${e.where}`).join(`; `)}}function kb(e,t,n=[]){if(!e||!/^f2[123]\./.test(e))return null;let r=Ob(n),i=(()=>{switch(e){case Ky:case Yy:case Qy:case $y:return{label:`Fuel capacity`,...xb(t)};case qy:return{label:`Cutout conflicts`,...Sb(t)};case Xy:case Zy:return{label:`Layup numbering`,...Cb(t)};case eb:return{label:`Fuel capacity`,...xb(t)};case nb:return{label:`Battery station`,...wb(t)};case rb:return{label:`Starter station`,...Tb(t)};case ab:{let e=Eb(t);return{label:`Engine limits`,value:e.value,sub:`${e.sub}. ${Db(t)}`}}default:return null}})();return r?i?{...i,sub:`${i.sub}. Plies: ${r.value} (${r.sub})`}:{label:`Layup schedule`,...r}:i}function Ab(e,t,n,r){let i=e?.prototype_weights?.rows;if(!i||!t||!n||!/^f2[123]\./.test(n))return null;let a=e=>r.indexOf(n)>=r.indexOf(e),o=`, reference, not in CG`,s=t.weights.rows.filter(e=>e.startsWith(`n26ms_empty_`)&&i[e]).map(e=>fb(i[e].weight_lb)),c=t.weights.closure_target,l=`Closure target: OM sample empty airplane ${db(c.empty_lb)} lb at FS ${fb(c.empty_arm_in)}${o}`;return a(`f23.root-rib`)&&s.length?{value:`${l}; N26MS ladder ${s.join(` / `)} lb`,sub:`FS ${db(c.loaded_envelope_fs[0])} to ${db(c.loaded_envelope_fs[1])} is the loaded envelope, not the empty CG. CG ${t.weights.cg}`}:a(`f23.cowl-trim`)&&n.startsWith(`f23.`)&&i.cowl_glass&&i.cowl_graphite?{value:`Cowl (CP27 page 5): ${fb(i.cowl_glass.weight_lb)} lb in glass, ${fb(i.cowl_graphite.weight_lb)} lb in graphite${o}`,sub:i.cowl_glass.note}:a(`f23.engine-install`)&&n.startsWith(`f23.`)&&i.dynafocal_mount?{value:`Dynafocal mount (CP26 builder weight, N26MS): ${db(i.dynafocal_mount.weight_lb)} lb${o}`,sub:i.dynafocal_mount.note}:a(`f22.battery-shelf`)&&n.startsWith(`f22.`)&&s.length?{value:`N26MS empty-weight ladder (CP27 page 4): ${s.join(` / `)} lb${o}`,sub:`${i.n26ms_empty_4?.note??``}`}:null}var jb=new Set([24,25,26]),Mb=`f24.aft-cover`,Nb=`f24.consoles-left`,Pb=`f24.gap-seal`,Fb=`f25.inspect-repair`,Ib=`f25.coarse-fill`,Lb=`f25.feather-fill`,Rb=`f25.primer`,zb=`f25.paint-seals`,Bb=`f26.cushions-headrests`,Vb=`f26.suitcases`,Hb=new Set([`f24.console-lc1`,Nb,`f24.thigh-support`,Bb,Vb]),Ub=new Set([Pb]),Wb=e=>!!e&&Ub.has(e.id),Gb=e=>e&&e.id===`f24.gap-seal`?.38:1,Kb=e=>!!e&&Hb.has(e.id),qb=Ib,Jb=e=>(Math.round(e*10)/10).toFixed(1),Yb=e=>(Math.round(e*100)/100).toString(),Xb=e=>parseFloat(e.toPrecision(3)).toString();function Zb(e){for(let t of[2,4,8,16,32])if(Math.abs(e*t-Math.round(e*t))<1e-9&&Math.round(e*t)>0)return`${Math.round(e*t)}/${t}`;return Xb(e)}function Qb(e,t,n){if(!t)return`none`;let r=n.indexOf(t),i=n.indexOf(e.show.from);return r<0||i<0?`none`:r>=i?`jig`:`none`}var $b=14074784,ex={"primer-grey":9146259,white:15987695};function tx(e,t,n){if(!t)return null;let r=n.indexOf(t);if(r<0)return null;let i=null;for(let t of e.stages){let e=n.indexOf(t.stage===`fill`?qb:t.from);e>=0&&r>=e&&(i=t.stage)}return i}function nx(e,t){return t===`fill`?$b:ex[e.stages.find(e=>e.stage===t)?.colour??`primer-grey`]??ex[`primer-grey`]}function rx(e,t,n){return e.find(e=>(e.component===t||(ix[e.component]??[]).includes(t))&&(e.match===null||n.includes(e.match)))??null}var ix={"fuselage.skin_right":[`fuselage.side_right`],"fuselage.skin_left":[`fuselage.side_left`]},ax=e=>e.finish.rows[0]?.stages.find(e=>e.stage===`fill`)?.thickness_in??[],ox=e=>e.finish.rows[0]?.stages.find(e=>e.stage===`primer`)?.thickness_in??[];function sx(e){let t=e.conflicts.aft_cover_plies,[n,r]=[t.scan_inside_outside,t.transcription_inside_outside];return{value:`Aft cover plies: scan ${n[0]} inside and ${n[1]} outside, transcription ${r[0]} inside and ${r[1]} outside`,sub:`Unresolved. ${t.note}`}}function cx(e){let t=e.conflicts.lc2_length_in;return{value:`Console top LC2 length: ${Jb(t.scan)} in on the scan, ${Jb(t.transcription)} in in the transcription`,sub:`Unresolved. Both are carried; the drawn console top is a fitted shape`}}function lx(e){return{value:`Gap seal: ${Zb(e.seal.gap_in)} in gap at the wing root, ${Zb(e.seal.front_gap_in)} in at the front`,sub:`Drawn as a fitted shape. ${e.seal.note}`}}function ux(e){return{value:`Finishing: shop held at ${e.finish.min_temp_f} F or above; glass weave ${Xb(e.finish.weave_in)} in rough`,sub:`Nothing goes on before every structure is inspected and repaired. ${e.finish.note}`}}function dx(e){let t=ax(e);return{value:`Feather fill ${Xb(t[0])} to ${Xb(t[1])} in over the ${Xb(e.finish.weave_in)} in weave, shop at ${e.finish.min_temp_f} F or above`,sub:`A layer drawn on the airframe, not a solid, and it carries no weight in the model (no finish weight is printed)`}}function fx(e){let t=ox(e);return{value:`Primer ${Xb(t[0])} to ${Xb(t[1])} in over the sanded fill`,sub:`Primer grey is a representational colour; the book prints no airplane colour. Fill ${Xb(ax(e)[0])} to ${Xb(ax(e)[1])} in under it`}}function px(e){return{value:`No finish weight printed. White on the upper wing and canard only; primer grey elsewhere`,sub:`White: ${e.finish.colours.white}. The grey is representational`}}function mx(){return{value:`No upholstery weight printed`,sub:`The cushions, headrests and suitcases are fitted shapes (the plans give outlines, not weights); nothing is added to the weight ledger for them`}}function hx(e){if(!e.length)return null;let t=new Map,n=0;for(let r of e)t.set(r.cloth,(t.get(r.cloth)??0)+r.plies),n+=r.plies;return{value:`${n} plies: ${[...t].map(([e,t])=>`${t} ${e}`).join(` + `)}`,sub:e.map(e=>`${e.plies} ${e.cloth}, ${e.where}`).join(`; `)}}var gx=/^f2[456]\./;function _x(e,t,n=[]){if(!e||!gx.test(e))return null;let r=hx(n),i=(()=>{switch(e){case Mb:return{label:`Aft cover plies`,...sx(t)};case Nb:return{label:`Console length`,...cx(t)};case Pb:return{label:`Gap seal`,...lx(t)};case Fb:return{label:`Finishing rules`,...ux(t)};case Lb:return{label:`Fill thickness`,...dx(t)};case Rb:return{label:`Primer thickness`,...fx(t)};case zb:return{label:`Finish weight`,...px(t)};case Bb:case Vb:return{label:`Upholstery weight`,...mx()};default:return null}})();return r?i?{...i,sub:`${i.sub}. Plies: ${r.value} (${r.sub})`}:{label:`Layup schedule`,...r}:i}function vx(e,t,n){if(!e||!t||!gx.test(t))return null;let r=`, reference, not in CG`,i=e.weights.closure_target;if(t===`f26.suitcases`){let t=i.sample_loadings,n=(e,n)=>{let r=t.find(t=>t.name===e);return r?`${n} pilot ${r.total_lb} lb at FS ${Yb(r.cg_in)} (${r.inside_envelope?`inside`:`outside the ${Yb(i.loaded_envelope_fs[1])} aft limit, as the manual says`})`:``};return{value:`Closure target: OM sample empty airplane ${Yb(i.empty_lb)} lb at FS ${Jb(i.empty_arm_in)}${r}`,sub:`OM samples: ${n(`light_pilot`,`light`)}; ${n(`heavy_pilot`,`heavy`)}. FS ${Yb(i.loaded_envelope_fs[0])} to ${Yb(i.loaded_envelope_fs[1])} is the loaded envelope, not the empty CG. CG ${e.weights.cg}`}}if(t.startsWith(`f25.`)&&(e=>n.indexOf(t)>=n.indexOf(e))(`f25.coarse-fill`)){let t=e.weights.finish_deltas,n=[[`canopy`,`finish_delta_canopy`],[`aileron`,`finish_delta_aileron`],[`wing`,`finish_delta_wing`]].filter(([,e])=>t[e]).map(([e,n])=>`${e} ${Xb(t[n].weight_lb)} lb`);if(n.length)return{value:`N26MS finish deltas (CP26 page 3 against CP27 page 1): ${n.join(`, `)}${r}`,sub:e.weights.note}}return null}var yx={firewall:13213802,top_longeron_left:14467214,top_longeron_right:14467214,belt_insert:13213802,rollover_inserts:13213802,belt_attach:13213802,jig_blocks:12160860,datum_board:13808252},bx={step:[12896461,.85,.35],extrusions:[12172996,.85,.4],gear_tubes:[9278362,.9,.3],axles:[9278362,.9,.3],strut:[14209200,.05,.45]},xx=new Set([`side_left`,`side_right`,`front_seat_bkhd`,`rear_seat_bkhd`,`top_longeron_left`,`top_longeron_right`,`f22`,`f28`,`panel`,`firewall`,`bottom`]),Sx={rollover_inserts:`rollover`},Cx=new Set([`carved_corners`]),wx={spar_box:`foam`,spar_bulkheads_end_bulkheads:`foam`,spar_bulkheads_interior_bulkheads:`foam`,spar_lwa_lwa1:[`metal`,12896461,.85,.35],spar_lwa_lwa2:[`metal`,12896461,.85,.35],spar_lwa_lwa3:[`metal`,12896461,.85,.35],spar_lwa_lwa4:[`metal`,12896461,.85,.35],spar_lwa_lwa5:[`metal`,12896461,.85,.35],spar_spruce_blocks:[`wood`,14467214,0,.6],spar_em12:[`metal`,9278362,.9,.3],spar_sh1:[`metal`,12896461,.85,.35],spar_jig:[`wood`,15326656,0,.62],fuselage_firewall_stainless:[`metal`,14014684,.9,.3],firewall_belcrank:[`metal`,9278362,.9,.3],firewall_master_cylinders:[`metal`,7172986,.7,.4],controls_consoles_front_console:`foam`,controls_consoles_rear_console:`foam`,controls_torque_tube:[`metal`,9278362,.9,.3],controls_sticks_front_stick:[`metal`,9278362,.9,.3],controls_sticks_rear_stick:[`metal`,9278362,.9,.3],controls_pitch_pushrod:[`metal`,12896461,.85,.35],controls_rudder_conduit:[`wood`,3026480,0,.7],trim_pitch_handle_pth:[`metal`,12896461,.85,.35],trim_pitch_handle_pth_pivot:[`metal`,9278362,.9,.3],trim_pitch_handle_pth_springs:[`metal`,10133670,.9,.35],trim_roll_trim_roll_trim:[`metal`,12896461,.85,.35],trim_roll_trim_roll_trim_springs:[`metal`,10133670,.9,.35],canopy_plexi:[`glass`,13625842,0,.06],canopy_pads_pads_hinge:[`wood`,Jh.hinge.color,0,.55],canopy_pads_pads_latch:[`wood`,Jh.latch.color,0,.55],canopy_pads_pad_catch:[`wood`,Jh.catch.color,0,.55],canopy_frame_foam:[`wood`,7319146,0,.85],canopy_frame_carved:[`wood`,8830334,0,.85],canopy_frame:[`wood`,8830334,0,.85],canopy_vent:[`wood`,10473362,0,.85],canopy_blocks:[`wood`,11817759,0,.7],canopy_brace_tubes:[`metal`,14727242,.5,.35],canopy_hinges_hinge_fuselage:[`metal`,14014684,.85,.3],canopy_hinges_hinge_canopy:[`metal`,11844290,.85,.3],canopy_latches:[`metal`,15118906,.6,.35],canopy_safety_catch_sc1:[`metal`,14014684,.9,.3],canopy_safety_catch_sc1_bolt:[`metal`,7172986,.9,.3],fuselage_front_cover:[`wood`,14275780,0,.7],fuselage_rear_cover:[`wood`,14275780,0,.7],fuselage_door:[`metal`,15001836,.3,.4]},Tx={tank:[`glass`,yb.tank,0,.1],cutout_baggage:[`glass`,yb.cutout_baggage,0,.3],cutout_tank:[`glass`,yb.cutout_tank,0,.3],sump_blister:[`wood`,13072954,0,.7],drain_insert:[`metal`,14014684,.85,.3],vent_line:[`wood`,16765503,0,.4],screen:[`wood`,3137768,0,.4],outlet_tube:[`metal`,14014684,.85,.3],fuel_cap:[`metal`,15118906,.6,.35],shelf:[`wood`,14275780,0,.7],battery:[`wood`,3095110,0,.5],cover:[`wood`,15328211,0,.7],strap:[`wood`,3026480,0,.7],start_relay:[`metal`,4014665,.7,.4],overvoltage_unit:[`metal`,7172986,.7,.4],battery_cable:[`wood`,12729135,0,.5],firewall_cable:[`wood`,12729135,0,.5],panel_bundle:[`wood`,3026480,0,.7],light_right:[`wood`,4054122,0,.4],light_left:[`wood`,14698568,0,.4],strobe_supply:[`metal`,15329774,.5,.4],nav_strip_right:[`metal`,14014684,.85,.3],nav_strip_left:[`metal`,14014684,.85,.3],comm_strips:[`metal`,14014684,.85,.3],block:[`metal`,7172986,.6,.45],bracket:[`metal`,12896461,.85,.35],cowl:[`glass`,14275780,0,.3],rib_right:[`metal`,12896461,.8,.35],rib_left:[`metal`,12896461,.8,.35]};for(let[e,t]of Object.entries({cover_aft_aft_cover:[`wood`,7315144,0,.7],cover_console_lc1_lc1:[`wood`,6263748,0,.7],cover_consoles_lc2:[`wood`,9286612,0,.7],cover_consoles_lc3:[`wood`,7315144,0,.7],cover_consoles_lc4:[`wood`,7315144,0,.7],cover_consoles_lc5:[`wood`,9286612,0,.7],cover_consoles_lc6:[`wood`,7315144,0,.7],cover_thigh_thigh_floor:[`wood`,8828314,0,.7],cover_thigh_thigh_rib_a:[`wood`,6265470,0,.7],cover_thigh_thigh_rib_b:[`wood`,6265470,0,.7],cover_valve_valve_cover:[`wood`,14727242,.2,.5],cover_canard_canard_cover:[`wood`,7315144,0,.7],cover_seal_seal_right:[`wood`,14709818,0,.8],cover_seal_seal_left:[`wood`,14709818,0,.8],upholstery_cushions_front_cushion:[`wood`,4152710,0,.9],upholstery_cushions_rear_cushion:[`wood`,4152710,0,.9],upholstery_headrests_front_headrest:[`wood`,5600927,0,.9],upholstery_headrests_rear_headrest:[`wood`,5600927,0,.9],upholstery_suitcases_suitcase_right:[`wood`,11109722,0,.75],upholstery_suitcases_suitcase_left:[`wood`,11109722,0,.75]}))wx[e]=t;for(let[e,t]of Object.entries({wing_jigs_jigs:[`wood`,11831896,0,.62],wing_hardpoints_hardpoints:[`wood`,7226152,0,.7],wing_ribs_ribs:[`wood`,14275780,0,.7],wing_conduit_conduit:[`wood`,3026480,0,.7],wing_aileron_aileron:[`wood`,15328211,0,.55],wing_aileron_hinges_hinge_pins:[`metal`,14014684,.85,.3],wing_aileron_hinges_hinge_leaves:[`metal`,11844290,.85,.3],wing_aileron_hinges_aileron_rod:[`metal`,12896461,.85,.35],wing_aileron_hinges_torque_tube:[`metal`,10133670,.9,.35],wing_controls_controls:[`metal`,4014665,.7,.4],wing_attach_spar_bolts:[`metal`,3093304,.7,.4],winglet_block_a_block_a:[`wood`,14731404,0,.8],winglet_skins_tip_cap:[`wood`,14275780,0,.7],winglet_rudder_rudder:[`wood`,15328211,0,.55],winglet_rudder_belhorn:[`metal`,4014665,.7,.4],winglet_rudder_hinge_rudder_hinge:[`metal`,4014665,.7,.4],winglet_jig_jig_lines:[`metal`,3837872,.4,.5]}))for(let n of[`right`,`left`])wx[`${e}_${n}`]=t;var Ex=-.2,Dx=e=>Ug.has(e)&&e!==`spar.jig`,Ox=new Set([`fuselage.firewall_stainless`,`firewall.belcrank`,`firewall.master_cylinders`]),kx=/^spar_(lwa_lwa[1-5]|spruce_blocks|bulkheads_interior_bulkheads)$/,Ax=new Set([`controls_sticks_front_stick`,`controls_sticks_rear_stick`]),jx=5,Mx=[`front_seat_bkhd`,`rear_seat_bkhd`,`panel`,`f22`,`f28`,`firewall`],Nx=-22.5,Px={side_left:1,side_right:23},Fx=2.4,Ix=e=>new W(e[0],e[2],-e[1]),Lx=e=>e.endsWith(`_right`),Rx=class{data;group=new Dn;jigFrame=new Dn;tableGroup=new Dn;station;cut;meshes=[];infos=[];phases=new Map;pose=`upright`;order;dry;yTop=-1e9;yBottom=1e9;tableM=new Map;spots=new Map;jigM=new Map;bank;gearTable=new Dn;cradles={"bank-left-45":new Dn,"bank-right-45":new Dn};marks=new Dn;dryTone={value:1};wheels=new Dn;noseStand=new Dn;wheelTop=null;markAt=null;marksOn=!1;firstIdx=new Map;turnFrom=`upright`;turnK=1;half={h:0,w:0};yMid=0;installed=new Dn;ghost=new Dn;opChapter=new Map;opOf=new Map;noseK=null;nosePts=null;noseT=0;noseShown=!1;ghostWheel=null;ghostStrut=null;ctl=null;slide=0;deflUp=0;stops=new Dn;sparBenchM=new Map;canopy=null;m26Parts=new Set;liftK=1;openDeg=0;canopyBenchM=new Map;selOp=null;checks=new Dn;checkAnchors=new Map;wing=null;m27Parts=new Set;aileronDeg=0;rudderDeg=0;wingStandM=new Map;abc=new Dn;abcAnchors=new Map;m28=null;m28Parts=new Set;m29=null;m29Parts=new Set;strakeTable=new Dn;strakeKitM=null;m25Chapter=!1;firewallAside=0;constructor(e,t,n){this.data=t,this.group.name=`fuselage`,this.station=Gy(),this.group.add(this.station,this.jigFrame,this.tableGroup),this.jigFrame.name=`fuselageJig`,this.jigFrame.matrixAutoUpdate=!1,this.order=n.order;for(let e of n.ops)this.opChapter.set(e.id,e.chapter),this.opOf.set(e.id,e);this.dry=n.ops.find(e=>e.id===`f06.trial-fit`)?.components??[];let r=new Map(n.ops.map(e=>[e.id,e]));this.order.forEach((e,t)=>{for(let n of r.get(e)?.components??[])this.firstIdx.has(n)||this.firstIdx.set(n,t)}),this.cut=new up(this.jigFrame,xv.extent,xv.depth,0,new W(1,0,0)),this.cut.amount=0,this.bank=t.bank_deg??Z_;let i=new Set(Object.keys(t.extras?.nose_parts??{}));this.canopy=t.extras?.m26?.canopy??null,this.m26Parts=new Set(Object.keys(t.extras?.m26?.parts??{})),this.wing=t.extras?.m27??null,this.m27Parts=new Set(Object.keys(t.extras?.m27?.parts??{})),this.m28=t.extras?.m28??null,this.m28Parts=new Set(Object.keys(t.extras?.m28?.parts??{})),this.m29=t.extras?.m29??null,this.m29Parts=new Set(Object.keys(t.extras?.m29?.parts??{}));let a=new Set([...Object.keys(t.extras?.m25?.parts??{}),...this.m26Parts,...this.m27Parts,...this.m28Parts,...this.m29Parts]);this.ctl=t.extras?.m25?.controls??null;let o=t.extras?.nose_gear;o&&(this.noseK=o,this.nosePts={plans:__(this.noseK,`plans`),manual:__(this.noseK,`manual`)});let s=new Map(Object.entries(t.parts).map(([e,t])=>[t.node,e])),c=new Map,l=new Set(Object.values(t.stages??{}).flat().map(e=>e.node));for(let t of e)l.has(t.name)&&(t.geo.computeBoundingBox(),c.set(t.name,t.geo));for(let n of e){if(l.has(n.name))continue;n.geo.computeBoundingBox();let e=n.node?t.nodes[n.node]??null:null,r=e?e.part:s.get(n.name);if(!r)throw Error(`fuselage mesh ${n.name} is not in layup.json`);let o=t.parts[r],u=o.fidelity===`representational`,d=n.geo.boundingBox.getSize(new W).toArray().sort((e,t)=>t-e),f=u&&!Cx.has(r)?vv(d[0]*d[1]):0,p=r.startsWith(`top_longeron_`)?r.replace(`top_longeron_`,`side_`):Sx[r]??r,m=p.startsWith(`side_`)?this.flatten(n.geo,Lx(p)):n.geo.clone();m.computeBoundingBox();let h,g,_;if(e){let t=e.orientation_deg??0,r=e.cloth===`UND`?`UND`:`BID`;h={kind:r===`UND`?`und`:`bid`,angles:r===`UND`?[t]:[t,t-90],ply:{node:n.name,order:e.stack,cloth:r}};let i=fm(n.geo),a=fm(m);g=mm(h,this.cut,i.web,i.span,{axis:i.axis,hatch:u,hatchSoft:f,dryTone:this.dryTone}),_=mm(h,null,a.web,a.span,{axis:a.axis,hatch:u,hatchSoft:f})}else if((this.m28Parts.has(r)?Tx[pb(this.m28.parts[r])]:wx[r])!==void 0&&(this.m28Parts.has(r)||wx[r]!==`foam`)){let[e,t,n,i]=this.m28Parts.has(r)?Tx[pb(this.m28.parts[r])]:wx[r];h={kind:`part`,angles:[]},g=vm(this.cut,{color:t,metalness:n,roughness:i,hatch:u,hatchSoft:f,name:r}),_=vm(null,{color:t,metalness:n,roughness:i,hatch:u,hatchSoft:f,name:r});let a=(this.m28Parts.has(r)?bb(pb(this.m28.parts[r])):null)??.34;if(e===`glass`)for(let e of[g,_])e.userData.glass=a,e.transparent=!0,e.opacity=a,e.depthWrite=!1,e.side=2}else if(yx[r]!==void 0)h={kind:`part`,angles:[]},g=vm(this.cut,{color:yx[r],hatch:u,hatchSoft:f,name:r}),_=vm(null,{color:yx[r],hatch:u,hatchSoft:f,name:r});else if(bx[r]!==void 0){let[e,t,n]=bx[r];h={kind:`part`,angles:[]},g=vm(this.cut,{color:e,metalness:t,roughness:n,hatch:u,hatchSoft:f,name:r}),_=vm(null,{color:e,metalness:t,roughness:n,hatch:u,hatchSoft:f,name:r})}else h={kind:`foam`,angles:[]},g=mm(h,this.cut,0,void 0,{hatch:u,hatchSoft:f}),_=mm(h,null,0,void 0,{hatch:u,hatchSoft:f});let v=new ei(n.geo,g);v.name=n.name;let y=new ei(m,_);y.name=n.name+`:table`,y.matrixAutoUpdate=!1;for(let e of[v,y])e.castShadow=!0,e.receiveShadow=!0,e.visible=!1;if(r===`belt_insert`)for(let e of[g,_])e.polygonOffset=!0,e.polygonOffsetFactor=-1,e.polygonOffsetUnits=-2;this.jigFrame.add(v),this.tableGroup.add(y);let b=n.geo.boundingBox;xx.has(r)&&(this.yTop=Math.max(this.yTop,b.max.y),this.yBottom=Math.min(this.yBottom,b.min.y),e||(this.half.w=Math.max(this.half.w,Math.abs(b.min.z),Math.abs(b.max.z))));let x=e?{op:e.op,order:e.op_order}:null,S=(t.stages?.[n.name]??[]).map(e=>({...e,geo:c.get(e.node)})).filter(e=>!!e.geo),C=e?e.component:o.component;this.meshes.push({name:n.name,part:r,cid:C,ply:x,row:e,fidelity:o.fidelity,hatch:u,spec:h,jig:v,table:y,jigMat:g,tableMat:_,carrier:p,base:n.geo,stages:S,show:o.show,jigOnly:H_.has(C),void:!!o.void,extra:i.has(r),m25:a.has(r),m27:this.m27Parts.has(r),m28:this.m28Parts.has(r),m29:this.m29Parts.has(r),finish:this.m29?rx(this.m29.finish.rows,C,n.name):null}),this.infos.push({name:n.name,component:e?e.component:o.component,ply:x})}this.buildWheels(),this.cut.collect(this.jigFrame),this.cut.update();let u=Uy(),d=Hy.jig;this.jigM.set(`inverted`,new q().makeTranslation(d.x,u,d.z).multiply(new q().makeScale(Q,Q,Q)).multiply(new q().makeRotationX(Math.PI)).multiply(new q().makeTranslation(-Hy.fsMid,-this.yTop,0))),this.jigM.set(`upright`,new q().makeTranslation(d.x,u,d.z).multiply(new q().makeScale(Q,Q,Q)).multiply(new q().makeTranslation(-Hy.fsMid,-this.yBottom,0))),this.half.h=(this.yTop-this.yBottom)/2,this.yMid=(this.yTop+this.yBottom)/2;for(let e of[`bank-left-45`,`bank-right-45`,`gear-table`]){let t=rv(e,this.bank);this.jigM.set(e,this.poseMatrix(t,pv(e)+mv(t,this.half)))}let f=this.wheelLow??this.yBottom;this.jigM.set(`on-gear`,new q().makeTranslation(d.x,0,Hy.floor.z).multiply(new q().makeScale(Q,Q,Q)).multiply(new q().makeTranslation(-Hy.fsMid,-f,0))),this.buildFurniture(),this.buildNoseStand(),this.buildMarks(),this.buildGhost(),this.buildStops(),this.buildChecks(),this.buildAbc(),this.buildStrakeTable();{let e=Math.max(...Object.values(t.nodes).filter(e=>e.part===`firewall`).map(e=>e.fs_max),-1/0),n=t.extras?.m25?.parts.fuselage_firewall_stainless?.fs_min;this.firewallAside=n!==void 0&&e>n?e-n+.02:0}this.group.add(this.gearTable,this.cradles[`bank-left-45`],this.cradles[`bank-right-45`],this.noseStand),this.jigFrame.add(this.marks,this.installed,this.ghost,this.stops,this.checks,this.abc,this.strakeTable),this.installed.name=`installedCanard`,this.installed.visible=!1,this.setPose(`upright`),this.pack()}poseMatrix(e,t){let n=Hy.jig;return new q().makeTranslation(n.x,Uy()+t*Q,n.z).multiply(new q().makeScale(Q,Q,Q)).multiply(new q().makeRotationX(e)).multiply(new q().makeTranslation(-Hy.fsMid,-this.yMid,0))}buildFurniture(){let e=Hy.jig,t=Yp(10122832,.7,{detail:5,colorVar:.12,name:`gear-table`}),n=Yp(7032888,.7,{detail:4,colorVar:.1}),r=(e,t,n,r,i,a,o,s)=>{let c=new ei(new sa(n,r,i),t);return c.position.set(a,o,s),c.castShadow=!0,c.receiveShadow=!0,e.add(c),c},i=Uy()+11*Q,a=.75*Q,o=i-a/2,s=Wy(14),c=Wy(134),l=31*Q,u=this.data.parts.rollover,d=Wy((u?.fs_min??79)-1.5),f=Wy((u?.fs_max??84)+1.5),p=13*Q;r(this.gearTable,t,d-s,a,2*l,(s+d)/2,o,e.z),r(this.gearTable,t,c-f,a,2*l,(c+f)/2,o,e.z);for(let n of[-1,1])r(this.gearTable,t,f-d,a,l-p,(d+f)/2,o,e.z+n*(p+l)/2);let m=i-a-e.benchTopY;for(let t of[34,113])for(let i of[-1,1])r(this.gearTable,n,3.5*Q,m,3.5*Q,Wy(t),e.benchTopY+m/2,e.z+i*11*Q);this.gearTable.name=`gearTable`,this.gearTable.visible=!1,this.gearTable.userData.representational=!0;let h=.75,g=3.5;for(let t of[`bank-left-45`,`bank-right-45`]){let i=this.cradles[t];i.name=`cradle-${t}`,i.visible=!1,i.userData.representational=!0;let a=this.jigM.get(t),o=t===`bank-left-45`?1:-1,{h:s,w:c}=this.half,l=Math.cos(rv(t,this.bank))<0?1:-1;for(let t of[40,100]){let u=[[new W(t,this.yMid+l*(s+h/2),0),new W(g,h,2*c+2*h),new W(t,this.yMid+l*(s+h/2),-o*(c+h))],[new W(t,this.yMid,o*(c+h/2)),new W(g,2*s+h,h),new W(t,this.yMid-l*s,o*(c+h/2))]];for(let[t,o,s]of u){let c=new ei(new sa(o.x,o.y,o.z),n);c.matrixAutoUpdate=!1,c.matrix.copy(a).multiply(new q().makeTranslation(t.x,t.y,t.z)),c.castShadow=!0,c.receiveShadow=!0,i.add(c);let l=s.clone().applyMatrix4(a),u=l.y-e.benchTopY;u>.02&&r(i,n,1.5*Q,u,1.5*Q,l.x,e.benchTopY+u/2,l.z)}}}}wheelLow=null;buildWheels(){let e=this.meshes.find(e=>e.part===`axles`);if(!e)return;let t=e.base.attributes.position,n=new W,r={1:new Xn,[-1]:new Xn};for(let e=0;e<t.count;e++)n.fromBufferAttribute(t,e),r[n.z>=0?1:-1].expandByPoint(n);let i=11/2,a=uv/2,o=new Oo(i-a,a,18,48),s=new ca(5/2,5/2,uv*.8,32).rotateX(Math.PI/2),c=vm(this.cut,{color:3026480,roughness:.82,hatch:!0,name:`tyre`}),l=vm(this.cut,{color:11120308,metalness:.8,roughness:.35,hatch:!0,name:`hub`});for(let e of[1,-1]){let t=r[e].getCenter(new W);for(let[e,n]of[[o,c],[s,l]]){let r=new ei(e,n);r.position.copy(t),r.castShadow=!0,r.receiveShadow=!0,r.name=`gear.wheels`,this.wheels.add(r)}this.wheelLow=t.y-i,e===-1&&(this.wheelTop=new W(t.x,t.y+i,t.z))}this.wheels.name=`gear.wheels`,this.wheels.visible=!1,this.wheels.userData.representational=!0,this.wheels.userData.hatch=!0,this.jigFrame.add(this.wheels)}buildNoseStand(){let e=this.jigM.get(`on-gear`),t=1/0;for(let e of this.meshes){if(e.ply||!xx.has(e.part))continue;let n=e.base.attributes.position;for(let e=0;e<n.count;e++)Math.abs(n.getX(e)-34)<3&&(t=Math.min(t,n.getY(e)))}if(!Number.isFinite(t))return;let n=new W(34,t,0).applyMatrix4(e),r=Yp(7032888,.7,{detail:4,colorVar:.1}),i=Yp(3816770,.9),a=(e,t,n,r,i,a,o)=>{let s=new ei(new sa(t*Q,n*Q,r*Q),e);s.position.set(i,a,o),s.castShadow=!0,s.receiveShadow=!0,this.noseStand.add(s)},o=n.y/Q;a(i,4,1,18,n.x,n.y-.5*Q,n.z),a(r,3.5,1.5,20,n.x,n.y-1.75*Q,n.z),a(r,3.5,o-4,3.5,n.x,(1.5+(o-4)/2)*Q,n.z),a(r,16,1.5,16,n.x,.75*Q,n.z),this.noseStand.name=`noseStand`,this.noseStand.visible=!1,this.noseStand.userData.representational=!0}buildMarks(){let e=this.data.gear_marks,t=this.meshes.find(e=>e.part===`axles`);if(!e||!t)return;let n=new Hr({color:3130623,toneMapped:!1,depthTest:!0}),r=e.axle_z,i=-e.board_bl,a=(e,t,r,i,a,o,s=.3)=>{let c=new ei(new sa(Math.max(Math.abs(i-e),s),Math.max(Math.abs(a-t),s),Math.max(Math.abs(o-r),s)),n);c.position.set((e+i)/2,(t+a)/2,(r+o)/2),c.castShadow=!1,c.receiveShadow=!1,this.marks.add(c)},o=e.axle_fs,s=e.board_fs;a(o,r,i,s,r,i);for(let e of[o,s])a(e,r-2,i,e,r+2,i);let c=t.base.boundingBox.min.z+5;for(let e=0,t=i;t>c;e++,t-=2)a(o,r,t,o,r,Math.max(c,t-1.2));this.markAt={dim:new W((o+s)/2,r,i),axle:new W(o,r,c)},this.marks.name=`gearMarks`,this.marks.visible=!1}furniture(){let e=this.turnK>=1;this.gearTable.visible=e&&this.pose===`gear-table`,this.cradles[`bank-left-45`].visible=e&&this.pose===`bank-left-45`,this.cradles[`bank-right-45`].visible=e&&this.pose===`bank-right-45`,this.marks.visible=e&&this.marksOn,this.noseStand.visible=e&&this.pose===`on-gear`&&!(this.noseShown&&this.noseT<1)}get marksShown(){return this.marks.visible}flatten(e,t){let n=e.clone(),r=n.attributes.position;for(let e=0;e<r.count;e++){let n=bv(this.data.plan_bend,r.getX(e));r.setZ(e,r.getZ(e)+(t?n:-n))}return r.needsUpdate=!0,n.computeVertexNormals(),n}setPose(e,t=!1){if(this.toneFor(e),t&&e!==this.pose&&lv(this.pose,e)){if(this.turnK<=0){this.pose=e,this.turnK=1,this.applyMatrix(this.jigM.get(e)),this.furniture();return}this.turnK=this.turnK<1?1-this.turnK:-tv/1,this.turnFrom=this.pose,this.pose=e,this.applyTurn(),this.furniture();return}this.pose=e,this.turnK=1,this.applyMatrix(this.jigM.get(e)),this.furniture()}get turning(){return this.turnK<1}stepTurn(e){return this.turnK>=1?!1:(this.turnK=Math.min(1,this.turnK+e/1),this.applyTurn(),this.furniture(),!0)}restMatrix(e){return this.jigM.get(e)??this.jigM.get(`upright`)}poseFor(e){return Q_(e,this.order,this.bank)}applyTurn(){if(this.turnK>=1){this.applyMatrix(this.jigM.get(this.pose));return}let{angle:e,lift:t}=gv(this.turnFrom,this.pose,Math.max(0,this.turnK),this.half,this.bank);this.applyMatrix(this.poseMatrix(e,t))}toneFor(e){this.dryTone.value=cv(e)}applyMatrix(e){this.jigFrame.matrix.copy(e),this.jigFrame.matrixWorldNeedsUpdate=!0,this.jigFrame.updateMatrixWorld(!0),this.cut.update()}flatRotation(e,t){let n=new W(0,1,0);if(e.startsWith(`side_`))return new jt().setFromUnitVectors(new W(0,0,Lx(e)?1:-1),n);if(e===`rollover`)return new jt().setFromAxisAngle(new W(1,0,0),Math.PI);if(e===`strut`)return new jt().setFromRotationMatrix(new q().makeBasis(new W(0,1,0),new W(0,0,1),new W(1,0,0)));let r=this.data.parts[e]?.fwd_normal;if(!r)return new jt;let i=Ix(r).normalize();return t===`aft`&&i.negate(),new jt().setFromUnitVectors(i,n)}carrierGeo(e){let t=this.data.parts[e]?.node??`fuselage.${e}`;return this.meshes.find(e=>e.name===t)?.table.geometry??null}rotatedBox(e,t){let n=this.carrierGeo(e);n.computeBoundingBox();let r=n.boundingBox.getCenter(new W),i=new Xn,a=new W,o=n.attributes.position;for(let e=0;e<o.count;e++)i.expandByPoint(a.fromBufferAttribute(o,e).sub(r).applyQuaternion(t));return{box:i,c:r}}pack(){let e=-Hy.table.len/Q/2+2;for(let t of Mx){if(!this.carrierGeo(t))continue;let{box:n}=this.rotatedBox(t,this.flatRotation(t,`fwd`)),r=n.max.x-n.min.x;this.spots.set(t,e+r/2),e+=r+Fx}}tableMatrix(e,t){let n=`${e}|${t}`,r=this.tableM.get(n);if(r)return r;let i=this.flatRotation(e,t),{box:a,c:o}=this.rotatedBox(e,i),s=Hy.table,c=e.startsWith(`side_`)||e===`bottom`||e===`strut`?0:this.spots.get(e)??0,l=Px[e]??(e===`bottom`||e===`strut`?0:Nx),u=a.getCenter(new W),d=new q().makeTranslation(s.x+c*Q,s.topY+.0015,s.z+l*Q).multiply(new q().makeScale(Q,Q,Q)).multiply(new q().makeTranslation(-u.x,-a.min.y,-u.z)).multiply(new q().makeRotationFromQuaternion(i)).multiply(new q().makeTranslation(-o.x,-o.y,-o.z));return this.tableM.set(n,d),d}benchM=null;benchMatrix(){if(this.benchM)return this.benchM;let e=Hy.jig,t=new q().set(0,1,0,0,0,0,1,0,1,0,0,0,0,0,0,1),n=new Xn;for(let e of this.meshes)!e.ply&&K_.includes(e.cid)&&n.union(e.base.boundingBox.clone().applyMatrix4(t));let r=n.getCenter(new W);return this.benchM=new q().makeTranslation(e.x,e.benchTopY+.0015,e.z).multiply(new q().makeScale(Q,Q,Q)).multiply(new q().makeTranslation(-r.x,-n.min.y,-r.z)).multiply(t),this.benchM}benchAssemblyBox(){let e=this.benchMatrix(),t=new Xn;for(let n of this.meshes)!n.ply&&K_.includes(n.cid)&&t.union(n.base.boundingBox.clone().applyMatrix4(e));return t}faceFor(e,t){return this.data.parts[e]?.fwd_normal?yv(e,t,this.order,this.data.nodes):`fwd`}placeOf(e,t){return this.m26Parts.has(e.part)?this.canopyPlaceOf(e,t)===`airplane`?`jig`:`table`:e.m29?`jig`:e.m28?this.m28WhereOf(e,t)===`table`?`table`:`jig`:e.m27?fg(t,this.order)===`airplane`?`jig`:`table`:e.m25?Jg(e.cid,t,this.order)===`bench`?`table`:`jig`:G_(e.cid,t,this.order,this.dry)}opCount(e){return e?this.meshes.filter(t=>t.ply?.op===e&&(!t.m27||this.wingShown(t,e))).length:0}paint(e,t,n,r,i,a,o=null){let s=!e&&o&&this.order.includes(o)?o:null,c=e?t:s;this.selOp=c;let l=this.poseFor(c);l!==this.pose&&this.setPose(l);let u=c?this.opChapter.get(c)??-1:-1,d=u===13,f=Vg.has(u)&&!!e;this.m25Chapter=f;let p=c?this.opOf.get(c)??null:null,m=f&&Yg(p),h=f&&pg(c,this.order),g=f&&ug(p),_=f&&lg(p),v=f&&hb(c),y=f&&_b(p),b=f&&Kb(p),x=f&&Wb(p),S=f&&!!c&&this.order.indexOf(c)>=this.order.indexOf(`f14.jig`)&&this.order.indexOf(c)<=this.order.indexOf(`f14.nut-access-hole`),C=e&&c?a.get(c):void 0,w=this.opCount(c),T=s?this.order.indexOf(s):-1,E=e=>(e.ply?this.order.indexOf(e.ply.op):this.firstIdx.get(e.cid)??1/0)<=T,D=l,O=!1;for(let t of this.meshes){let o=e?e.get(t.name)??`hidden`:s?E(t)?`built`:`hidden`:`built`,l=t.ply&&C!==void 0?rh({meshOpIndex:a.get(t.ply.op),curOpIndex:C,order:t.ply.order,lay:n,count:w,t:r,ghost:i}):ih(o);this.phases.set(t.name,l);let u=o!==`ghost`&&!t.ply&&J_(t.cid,c,this.order),T=o===`ghost`?`jig`:u?`table`:this.placeOf(t,c),k=o!==`hidden`&&!(t.ply&&o===`current`&&l.unroll<=0)&&(u||(t.m29?this.m29WhereOf(t,c)!==`none`:t.m28?this.m28WhereOf(t,c)!==`none`:$_(t.show,c,this.order)))&&!(t.jigOnly&&T===`table`&&!u)&&(!t.extra||d)&&(!t.m25||f)&&!(S&&!t.m25&&T===`jig`)&&!(h&&!t.m27)&&!(v&&!t.m28)&&(!t.m27||this.wingShown(t,c))&&!(b&&t.cid.startsWith(`canopy.`)),A=ev(t.stages.map(e=>({from:e.from,node:e.node})),c,this.order),ee=A?t.stages.find(e=>e.node===A).geo:t.base;if(t.jig.geometry!==ee&&this.swapGeometry(t.jig,ee),A&&(D+=A),t.void&&(t.jig.position.y=jx),t.jig.visible=k&&T===`jig`,t.table.visible=k&&T===`table`,t.part===`datum_board`&&t.jig.visible&&(O=!0),t.table.visible){let e=this.faceFor(t.carrier,c);t.table.matrix.copy(u?this.benchMatrix():this.m26Parts.has(t.part)?this.canopyMatrix(t,c):t.m28?this.strakeKitMatrix(t):t.m27?this.wingMatrix(t,c):t.m25?this.sparBenchMatrix(this.sparStand(c)):this.tableMatrix(t.carrier,e)),t.table.matrixWorldNeedsUpdate=!0,D+=t.carrier+e+(u?`b`:``)}let te=g&&t.m27&&!p.components.includes(t.cid)&&t.cid!==`wing.jigs`,j=(y||x)&&!vb(p,t.cid),ne=x&&j&&o!==`ghost`,M=m&&t.m25&&t.part!==`spar_box`&&kx.test(t.part)||_&&t.m27&&p.components.includes(t.cid)||y&&t.m28&&vb(p,t.cid)||x&&t.m29&&vb(p,t.cid);for(let e of[t.jigMat,t.tableMat])e.depthTest=!M;this.applyFinish(t,c),t.jig.renderOrder=t.table.renderOrder=M?5:0;let N=o===`built`||o===`current`&&l.unroll>=1;t.jig.castShadow=t.table.castShadow=N;let re={unroll:l.unroll,front:l.front,cure:l.cure,ghost:o===`ghost`||m&&t.part===`spar_box`||te||j&&!ne};if(gm(t.jigMat,re),_m(t.jigMat,ne?Gb(p):1),_m(t.tableMat,ne?Gb(p):1),gm(t.tableMat,re),t.m28||t.m29)for(let e of[t.jigMat,t.tableMat]){let t=M||!!e.userData.glass;e.transparent!==t&&(e.transparent=t,e.needsUpdate=!0),M&&(e.depthWrite=!1)}D+=(t.jig.visible?`j`:t.table.visible?`t`:`-`)+(N?`1`:`0`)}this.tableGroup.updateMatrixWorld(!0);let k=this.meshes.find(e=>e.part===`axles`);this.wheels.visible=this.pose===`on-gear`&&!!k?.jig.visible,D+=this.wheels.visible?`w`:``,this.marksOn=O,this.installed.visible=!!e&&(R_.has(u)||jb.has(u)||!!c&&(Wg.has(c)||c===`f22.antennas`)),this.stops.visible=f&&u<18&&!!c&&this.order.indexOf(c)>=this.order.indexOf(`f16.pitch-pushrod`),this.checks.visible=f&&c===`f18.check-ab`,this.abc.visible=f&&c===`f20.jig`,this.strakeTable.visible=f&&gb(c,this.order),D+=this.strakeTable.visible?`s`:``,this.applyM25(),this.applyInstalledFinish(c),D+=this.installed.visible?`c`:``;let A=this.meshes.find(e=>e.part===`gear_nose_strut`);return this.noseShown=!!A?.jig.visible,this.ghost.visible=this.noseShown,this.applyNose(),D+=this.noseShown?`n`+this.noseT.toFixed(3):``,this.furniture(),D+(O?`m`:``)+(this.gearTable.visible?`g`:``)+(this.cradles[`bank-left-45`].visible?`l`:``)+(this.cradles[`bank-right-45`].visible?`r`:``)}swapGeometry(e,t){let n=e.geometry;if(n.groups.length){let e=t.index?t.index.count:t.attributes.position.count;t.clearGroups();for(let r of n.groups)t.addGroup(0,e,r.materialIndex)}else t.clearGroups();e.geometry=t}setStation(e,t,n){this.cut.amount=e?Sv(t):0,this.cut.update(),this.cut.uGlow.value=e?n:0}capped(e,t){return this.meshes.filter(n=>{let r=t(n.name);if(!n.jig.visible||r!==`built`&&r!==`current`)return!1;let i=n.jig.geometry.boundingBox;return i.min.x-.001<=e&&e<=i.max.x+.001})}shown(e){let t=this.meshes.find(t=>t.name===e);return t?t.jig.visible?t.jig:t.table.visible?t.table:null:null}worldBoxAt(e,t){if(!e.ply&&J_(e.cid,t,this.order))return e.base.boundingBox.clone().applyMatrix4(this.benchMatrix());let n=this.placeOf(e,t),r=n===`jig`?this.restMatrix(this.poseFor(t)):this.m26Parts.has(e.part)?this.canopyMatrix(e,t):e.m28?this.strakeKitMatrix(e):e.m27?this.wingMatrix(e,t):e.m25?this.sparBenchMatrix(this.sparStand(t)):this.tableMatrix(e.carrier,this.faceFor(e.carrier,t));return(n===`jig`?e.base:e.table.geometry).boundingBox.clone().applyMatrix4(r)}shots(e,t){let n={};for(let r of e){let e=Iy(r),i=new W;if(e.focus===`bench`)i.copy(this.benchAssemblyBox().getCenter(new W));else if(e.focus===`marks`&&this.markAt)i.copy(this.markAt.dim).lerp(this.markAt.axle,.5).applyMatrix4(this.restMatrix(this.poseFor(r)));else if(typeof e.focus==`object`&&`spar`in e.focus){let t=Jg(`spar.box`,r,this.order)===`bench`,n=new W(121.7,.35,-e.focus.spar);i.copy(n).applyMatrix4(t?this.sparBenchMatrix(this.sparStand(r)):this.restMatrix(this.poseFor(r)))}else if(typeof e.focus==`object`&&`canopy`in e.focus){let t=this.canopyBox().getCenter(new W),n=t.clone().applyMatrix4(this.canopyBenchMatrix(e.focus.canopy!==`bench-up`));e.focus.canopy===`mid`?i.copy(n).lerp(t.clone().applyMatrix4(this.restMatrix(this.poseFor(r))),.5):i.copy(n)}else if(e.focus===`strake-table`)i.copy(this.strakeKitBox().getCenter(new W));else if(typeof e.focus==`object`&&`wing`in e.focus){let t=e.focus.wing,n=fg(r,this.order),a=this.wingBox(n===`jig`,n===`winglet`).getCenter(new W),o=new W(t.fs??a.x,t.z===void 0?a.y:t.z,-t.bl);i.copy(o).applyMatrix4(n===`airplane`?this.restMatrix(this.poseFor(r)):this.wingStandMatrix(n))}else if(typeof e.focus==`object`&&`at`in e.focus)i.set(...e.focus.at).applyMatrix4(this.restMatrix(this.poseFor(r)));else if(e.focus===`box`||e.focus===`marks`){let e=new Xn;for(let t of this.meshes)!t.ply&&xx.has(t.part)&&this.placeOf(t,r)===`jig`&&this.isMade(t,r)&&e.union(this.worldBoxAt(t,r));e.isEmpty()?i.set(Hy.jig.x,Uy()+.25,Hy.jig.z):e.getCenter(i)}else{let t=e.focus.parts.map(e=>this.meshes.find(t=>t.part===e&&!t.ply)).filter(e=>!!e);if(e.focus.fs!==void 0&&t.length){let n=t[0],a=this.placeOf(n,r),o=(a===`jig`?n.base:n.table.geometry).boundingBox.getCenter(new W);o.x=e.focus.fs;let s=a===`jig`?this.restMatrix(this.poseFor(r)):this.tableMatrix(n.carrier,this.faceFor(n.carrier,r));i.copy(o.applyMatrix4(s))}else if(e.focus.side&&t.length){let n=e.focus.side===`right`,a=new Xn,o=new W;for(let e of t){let t=this.placeOf(e,r),i=t===`jig`?e.base:e.table.geometry,s=t===`jig`?this.restMatrix(this.poseFor(r)):this.tableMatrix(e.carrier,this.faceFor(e.carrier,r)),c=i.attributes.position;for(let e=0;e<c.count;e++)c.getZ(e)<0===n&&a.expandByPoint(o.fromBufferAttribute(c,e).applyMatrix4(s))}a.getCenter(i)}else{let e=new Xn;for(let n of t)e.union(this.worldBoxAt(n,r));e.getCenter(i)}}let a=Ly(e);if(e.pan){let t=new W(a[0],0,a[2]).normalize().cross(new W(0,1,0)).negate().multiplyScalar(e.pan*Q);i.add(t)}e.up&&(i.y-=e.up*Q);let o=i.clone().add(new W(a[0],a[1],a[2]).multiplyScalar(Q));n[r]={pos:[o.x,o.y,o.z],target:[i.x,i.y,i.z],fov:t,...e.outside?{outside:!0}:{}}}return n}cutShot(e,t,n=null,r={}){let i=new Xn;for(let e of this.meshes)!e.ply&&xx.has(e.part)&&this.placeOf(e,n)===`jig`&&(n===null||this.isMade(e,n))&&i.union(this.worldBoxAt(e,n));let a=i.isEmpty()?new W(Hy.jig.x,Uy()+.25,Hy.jig.z):i.getCenter(new W);a.x=Wy(e),a.y+=r.lift??0;let o=Ly({focus:`box`,dist:r.dist??58,el:24,az:72}),s=a.clone().add(new W(o[0],o[1],o[2]).multiplyScalar(Q));return{pos:[s.x,s.y,s.z],target:[a.x,a.y,a.z],fov:t}}isNewOn(e,t){return!!t&&this.firstIdx.get(e)===this.order.indexOf(t)}isMade(e,t){let n=this.firstIdx.get(e.cid);return n!==void 0&&n<=this.order.indexOf(t)}homeBox(){let e=Hy.table,t=Hy.jig;return new Xn(new W(e.x-e.len/2,t.benchTopY,e.z-e.depth/2),new W(e.x+e.len/2,Uy()+.6,t.z+t.benchDepth/2))}finishedBox(){let e=this.restMatrix(`on-gear`),t=new Xn;for(let n of this.meshes)!n.ply&&!n.m25&&this.placeOf(n,null)===`jig`&&$_(n.show,null,this.order)&&t.union(n.base.boundingBox.clone().applyMatrix4(e));for(let n of this.wheels.children)t.union((n.geometry.boundingBox??(n.geometry.computeBoundingBox(),n.geometry.boundingBox)).clone().translate(n.position).applyMatrix4(e));return t.expandByPoint(new W(t.min.x,0,t.min.z)),t}benchBox(){let e=Hy.jig;return new Xn(new W(e.x-e.benchLen/2,0,e.z-e.benchDepth/2),new W(e.x+e.benchLen/2,Uy(),e.z+e.benchDepth/2))}wheelAnchor(e){return!this.wheels.visible||!this.wheelTop?null:e.copy(this.wheelTop).applyMatrix4(this.jigFrame.matrixWorld)}sparBox(e,t=!0){let n=new Xn;for(let r of this.meshes)r.m25&&Ug.has(r.cid)&&(e||r.cid!==`spar.jig`)&&(t||!r.cid.startsWith(`spar.cap_`))&&n.union(r.base.boundingBox);return n}sparStand(e){return{jig:$_(this.data.parts.spar_jig?.show,e,this.order),caps:!!e&&this.order.indexOf(e)>=this.order.indexOf(`f14.spar-caps`)}}sparBenchMatrix(e){let t=`${e.jig}${e.caps}`,n=this.sparBenchM.get(t);if(n)return n;let r=Hy.table,i=this.sparBox(e.jig,e.caps),a=this.sparBox(!0,!0).getCenter(new W);return n=new q().makeTranslation(r.x,r.topY+.002,r.z+.5).multiply(new q().makeScale(Q,Q,Q)).multiply(new q().makeRotationY(e.jig?Math.PI/2:-Math.PI/2)).multiply(new q().makeTranslation(-a.x,-i.min.y,-a.z)),this.sparBenchM.set(t,n),n}sparBenchWorldBox(e){return this.sparBox(e.jig,!0).clone().applyMatrix4(this.sparBenchMatrix(e))}slideDistance(){let e=this.sparBox(!1);return(e.max.z-e.min.z)/2+this.half.w+6}setSparSlide(e){let t=(1-Math.min(1,Math.max(0,e)))*this.slideDistance();t!==this.slide&&(this.slide=t,this.applyM25())}get sparSlideInches(){return this.slide}setStick(e){e!==this.deflUp&&(this.deflUp=e,this.applyM25())}get stickDeflUp(){return this.deflUp}pm(e){return new W(e[0],e[2],-e[1])}stickBase(e){let t=this.ctl;return[t.pivot_fs[e],t.tube_bl,t.tube_wl-t.wl_zero]}applyM25(){let e=this.ctl,t=e?A_(0,e):0,n=e?A_(this.deflUp,e):0,r=(t,n)=>{let r=j_(t,e.cant_inboard_deg),i=this.stickBase(n);return[i[0]+r[0]*e.lever_in,i[1]+r[1]*e.lever_in,i[2]+r[2]*e.lever_in]};for(let i of this.meshes){if(!i.m25)continue;let a=new q;if(Ox.has(i.cid))a.makeTranslation(this.firewallAside,0,0);else if(Dx(i.cid))a.makeTranslation(0,0,this.slide);else if(e&&Ax.has(i.part)){let e=this.pm(this.stickBase(i.part===`controls_sticks_front_stick`?`front`:`rear`));a.makeTranslation(e.x,e.y,e.z).multiply(new q().makeRotationZ((n-t)*Math.PI/180)).multiply(new q().makeTranslation(-e.x,-e.y,-e.z))}else if(e&&i.part===`controls_pitch_pushrod`){let e=this.pm(r(t,`front`)),i=this.pm(r(n,`front`));a.makeTranslation(i.x-e.x,i.y-e.y,i.z-e.z)}else if(this.canopy&&this.m26Parts.has(i.part)&&this.data.parts[i.part]?.turns&&this.canopyPlaceOf(i,this.selOp)===`airplane`)a.copy(this.openMatrix());else if(this.wing&&i.m27&&fg(this.selOp,this.order)===`airplane`){let e=this.deflection(i);e&&a.copy(e)}i.jig.matrixAutoUpdate=!1,i.jig.matrix.copy(a),i.jig.matrixWorldNeedsUpdate=!0}this.applyElevators(),this.applyCanopy(),this.applyWing(),this.jigFrame.updateMatrixWorld(!0)}applyElevators(){let e=this.data.extras?.elevators;if(!e)return;let[t,n]=e.hinge_xz,r=-this.deflUp,i=new q().makeTranslation(t,n,0).multiply(new q().makeRotationZ(-r*Math.PI/180)).multiply(new q().makeTranslation(-t,-n,0));for(let e of this.installedMeshes())e.name.startsWith(`installed:elevator.`)&&!e.name.includes(`hinges`)&&(e.matrixAutoUpdate=!1,e.matrix.copy(i),e.matrixWorldNeedsUpdate=!0)}buildStops(){let e=this.ctl;if(!e)return;let t=vm(this.cut,{color:12160860,hatch:!0,name:`pitch-stop`}),[n,r,i]=e.stop_size_in,a=this.stickBase(`front`);for(let o of[e.up_target_deg,-e.down_deg]){let s=j_(A_(o,e)+(o>0?-1:1)*4,e.cant_inboard_deg),c=this.pm([a[0]+s[0]*e.lever_in,a[1]+s[1]*e.lever_in,a[2]+s[2]*e.lever_in]),l=new ei(new sa(n,i,r),t);l.position.copy(c),l.castShadow=!0,l.receiveShadow=!0,this.stops.add(l)}this.stops.name=`controls.pitch_stops`,this.stops.visible=!1,this.stops.userData.representational=!0,this.stops.userData.hatch=!0}stopsAnchor(e){if(!this.stops.visible||!this.stops.children.length)return null;let t=new W;for(let e of this.stops.children)t.add(e.position);return t.multiplyScalar(1/this.stops.children.length).add(new W(0,1.4,0)),e.copy(t).applyMatrix4(this.jigFrame.matrixWorld)}canopyPlaceOf(e,t){return jh(e.cid,this.canopy?.lift??[],t,this.order)}canopyBox(){let e=new Xn;for(let t of this.meshes)this.m26Parts.has(t.part)&&this.canopy?.lift.includes(t.cid)&&e.union(t.base.boundingBox);return e}canopyBenchMatrix(e){let t=this.canopyBenchM.get(e);if(t)return t;let n=Hy.table,r=this.canopyBox(),i=r.getCenter(new W),a=e?-(r.max.y-i.y):r.min.y-i.y,o=new q().makeTranslation(n.x,n.topY+.002,n.z).multiply(new q().makeScale(Q,Q,Q)).multiply(new q().makeTranslation(0,-a,0)).multiply(new q().makeRotationX(e?Math.PI:0)).multiply(new q().makeTranslation(-i.x,-i.y,-i.z));return this.canopyBenchM.set(e,o),o}liftMatrix(e){let t=this.restMatrix(this.poseFor(Th)),n=this.canopyBenchMatrix(!0),r=this.canopyBox().getCenter(new W),i=r.clone().applyMatrix4(t),a=r.clone().applyMatrix4(n),o=new jt().setFromRotationMatrix(new q().extractRotation(t)),s=new jt().setFromRotationMatrix(new q().extractRotation(n)),c=Math.min(1,Math.max(0,e)),l=i.clone().lerp(a,c).add(new W(0,.55*Math.sin(Math.PI*c),0)),u=o.clone().slerp(s,c);return new q().makeTranslation(l.x,l.y,l.z).multiply(new q().makeRotationFromQuaternion(u)).multiply(new q().makeScale(Q,Q,Q)).multiply(new q().makeTranslation(-r.x,-r.y,-r.z))}canopyMatrix(e,t){return this.canopyPlaceOf(e,t)===`bench-up`?this.canopyBenchMatrix(!1):t===`f18.cut-remove`&&this.liftK<1?this.liftMatrix(this.liftK):this.canopyBenchMatrix(!0)}setCanopyLift(e){let t=Math.min(1,Math.max(0,e));t!==this.liftK&&(this.liftK=t,this.applyCanopy())}get canopyLiftK(){return this.liftK}setCanopyOpen(e){e!==this.openDeg&&(this.openDeg=e,this.applyM25())}get canopyOpenDeg(){return this.openDeg}openMatrix(){let e=this.canopy.hinge;return new q().makeTranslation(0,e.z,-e.y).multiply(new q().makeRotationX(-this.openDeg*Math.PI/180)).multiply(new q().makeTranslation(0,-e.z,e.y))}applyCanopy(){if(this.canopy){for(let e of this.meshes)this.m26Parts.has(e.part)&&e.table.visible&&(e.table.matrix.copy(this.canopyMatrix(e,this.selOp)),e.table.matrixWorldNeedsUpdate=!0);this.tableGroup.updateMatrixWorld(!0)}}canopyWorldBox(){let e=new Xn;for(let t of this.meshes){if(!this.m26Parts.has(t.part))continue;let n=this.shown(t.name);n&&this.canopy?.lift.includes(t.cid)&&e.union(new Xn().setFromObject(n))}return e}buildChecks(){let e=this.canopy,t=e?.wl_zero;if(!e||t===void 0)return;let n=new Hr({color:3130623,toneMapped:!1,depthTest:!1}),r=this.half.w+5,i=(e,t,r,i,a,o,s=.3)=>{let c=new ei(new sa(Math.max(Math.abs(i-e),s),Math.max(Math.abs(a-t),s),Math.max(Math.abs(o-r),s)),n);c.position.set((e+i)/2,(t+a)/2,(r+o)/2),c.castShadow=!1,c.receiveShadow=!1,c.renderOrder=9,this.checks.add(c)};for(let n of e.checks){let e=n.wl0-t,a=n.wl1-t,o=n.fs;i(o,e,r,o,a,r,.4);for(let t of[e,a]){i(o-1.6,t,r,o+1.6,t,r,.4);for(let e=r,n=0;e>.5&&n<40;e-=2.2,n++)i(o,t,e,o,t,Math.max(0,e-1.2),.25)}this.checkAnchors.set(n.id,new W(o,a+1.2,r))}this.checks.name=`canopyChecks`,this.checks.visible=!1}checkAnchor(e,t){let n=this.checkAnchors.get(e);return!n||!this.checks.visible?null:t.copy(n).applyMatrix4(this.jigFrame.matrixWorld)}wingBox(e,t=!1){let n=new Xn;if(t){for(let e of this.meshes)e.m27&&e.part.endsWith(`_right`)&&e.cid.startsWith(`winglet.`)&&e.cid!==`winglet.jig`&&n.union(e.base.boundingBox);return n}for(let t of this.meshes)t.m27&&t.part.endsWith(`_right`)&&t.cid.startsWith(`wing.`)&&(e||t.cid!==`wing.jigs`)&&n.union(t.base.boundingBox);return n}wingStandMatrix(e){let t=this.wingStandM.get(e);if(t)return t;let n=this.wingBox(e===`jig`,e===`winglet`),r=n.getCenter(new W),i=new q;e===`winglet`?i.makeBasis(new W(0,0,1),new W(1,0,0),new W(0,1,0)):e===`jig`?i.makeBasis(new W(0,-1,0),new W(0,0,1),new W(-1,0,0)):i.makeBasis(new W(0,0,-1),new W(0,-1,0),new W(-1,0,0));let a=new q().makeScale(Q,Q,Q).multiply(i).multiply(new q().makeTranslation(-r.x,-r.y,-r.z)),o=n.clone().applyMatrix4(a).min.y,s=Hy.table,c=Hy.jig,l=(e===`table`||e===`winglet`?new q().makeTranslation(s.x,s.topY+.002-o,s.z):new q().makeTranslation(c.x,.002-o,Ex)).multiply(a);return this.wingStandM.set(e,l),l}wingMatrix(e,t){let n=fg(t,this.order),r=this.wingStandMatrix(n===`winglet`?`winglet`:n===`table`&&e.cid!==`wing.jigs`?`table`:`jig`),i=this.deflection(e);return i?r.clone().multiply(i):r}wingShown(e,t){let n=this.data.parts[e.part];return fg(t,this.order)===`winglet`&&(!e.cid.startsWith(`winglet.`)||e.part.endsWith(`_left`))?!1:mg(e.part.endsWith(`_left`)?`left`:`right`,t,this.order)&&(!n?.workshop||hg(e.cid,t,this.order))}deflection(e){let t=this.wing,n=this.data.parts[e.part]?.turns;if(!t||!n||!e.part.endsWith(`_right`))return null;let r=n===`aileron`,i=r?-this.aileronDeg:this.rudderDeg;if(i===0)return null;let a=(r?t.aileron.axis:t.rudder.axis).map(e=>this.pm(e)),o=a[0],s=a[1].clone().sub(o).normalize();return new q().makeTranslation(o.x,o.y,o.z).multiply(new q().makeRotationAxis(s,i*Math.PI/180)).multiply(new q().makeTranslation(-o.x,-o.y,-o.z))}applyWing(){if(this.wing){for(let e of this.meshes)e.m27&&e.table.visible&&(e.table.matrix.copy(this.wingMatrix(e,this.selOp)),e.table.matrixWorldNeedsUpdate=!0);this.tableGroup.updateMatrixWorld(!0)}}setAileron(e){e!==this.aileronDeg&&(this.aileronDeg=e,this.applyM25())}get aileronUpDeg(){return this.aileronDeg}setRudder(e){e!==this.rudderDeg&&(this.rudderDeg=e,this.applyM25())}get rudderOutDeg(){return this.rudderDeg}buildAbc(){let e=this.wing;if(!e)return;let t=new Hr({color:3130623,toneMapped:!1,depthTest:!1}),n=t=>this.pm(e.winglet.points[t]),r=(e,n,r)=>{let i=n.clone().sub(e),a=new ei(new ca(r,r,i.length(),8),t);a.position.copy(e).addScaledVector(i,.5),a.quaternion.setFromUnitVectors(new W(0,1,0),i.normalize()),a.castShadow=!1,a.receiveShadow=!1,a.renderOrder=9,this.abc.add(a)},i=n(`wprp`);for(let e of[`a`,`b`,`c`]){let t=n(e);r(i,t,.28),t.clone().sub(i).length();let a=new W(0,1,0);r(t.clone().addScaledVector(a,-1.4),t.clone().addScaledVector(a,1.4),.2),this.abcAnchors.set(e,t.clone().add(new W(0,2.4,0)))}r(i.clone().add(new W(0,-1.4,0)),i.clone().add(new W(0,1.4,0)),.2),this.abcAnchors.set(`wprp`,i.clone().add(new W(0,2.4,0))),this.abc.name=`winglet.abc`,this.abc.visible=!1}abcAnchor(e,t){let n=this.abcAnchors.get(e);return!n||!this.abc.visible?null:t.copy(n).applyMatrix4(this.jigFrame.matrixWorld)}abcText(e){return this.wing?Lg(this.wing,e):e}attachInstalled(e){let t=this.data.extras?.canard_install;this.installed.position.set(t?.fs_le??18.7,t?.z_le??1.5,0),this.installedBaseY=this.installed.position.y;for(let{mesh:t,mirror:n}of e)n&&(t.scale.z=-1),t.castShadow=!0,t.receiveShadow=!0,this.installed.add(t);this.cut.collect(this.jigFrame),this.cut.update()}installedBaseY=0;setInstalledLift(e){this.installed.position.y=this.installedBaseY+e,this.installed.updateMatrixWorld(!0)}installedBox(e=0){let t=new Xn;for(let e of this.installedMeshes())e.updateMatrix(),e.geometry.boundingBox||e.geometry.computeBoundingBox(),t.union(e.geometry.boundingBox.clone().applyMatrix4(e.matrix));return t.translate(new W(this.installed.position.x,this.installedBaseY+e,this.installed.position.z))}installedMeshes(){return this.installed.children.filter(e=>e.isMesh)}setNose(e){e!==this.noseT&&(this.noseT=e,this.applyNose(),this.furniture())}get noseProgress(){return this.noseT}get nosePresent(){return this.noseShown}buildGhost(){let e=this.noseK;if(!e)return;let t=vm(this.cut,{color:13159634,hatch:!0,name:`nose-ghost`});gm(t,{unroll:1,front:1,cure:1,ghost:!0});let n=e.tire_od/2,r=e.tire_width/2,i=new ei(new Oo(n-r,r,14,40),t),a=new ei(new sa(1,1,1.8),t);for(let e of[i,a])e.castShadow=!1,e.receiveShadow=!1,this.ghost.add(e);this.ghostWheel=i,this.ghostStrut=a,this.ghost.name=`noseGhost`,this.ghost.visible=!1,this.ghost.userData.representational=!0,this.ghost.userData.hatch=!0}applyNose(){let e=this.nosePts;if(!e)return;let t=this.noseT,n=this.meshes.find(e=>e.part===`gear_nose_strut`);if(n){let r=y_(t,e.plans);n.jig.matrixAutoUpdate=!1,n.jig.matrix.set(r.r[0],r.r[1],0,r.tx,r.r[2],r.r[3],0,r.tz,0,0,1,0,0,0,0,1),n.jig.matrixWorldNeedsUpdate=!0}if(this.ghostWheel&&this.ghostStrut){let n=e.manual,[r,i]=b_(t,n);this.ghostWheel.position.set(r,i,0);let[a,o]=n.pivot,s=Math.hypot(r-a,i-o);this.ghostStrut.scale.set(1,s,1.8),this.ghostStrut.position.set((r+a)/2,(i+o)/2,0),this.ghostStrut.rotation.set(0,0,Math.atan2(i-o,r-a)-Math.PI/2)}this.jigFrame.updateMatrixWorld(!0)}noseWheelAt(e){return this.nosePts?b_(this.noseT,this.nosePts[e]):null}noseWheelAnchor(e,t){let n=this.noseWheelAt(e);if(!n||!this.noseShown||!this.nosePts)return null;let r=(this.noseK?.tire_od??9)/2;return t.set(n[0],e===`plans`?n[1]+r:n[1]-r,e===`plans`?-1:1).applyMatrix4(this.jigFrame.matrixWorld)}m29WhereOf(e,t){return Qb(this.m29.parts[e.part],t,this.order)}setFin(e,t){let n=t===null?null:new J(t);for(let t of Array.isArray(e)?e:[e])for(let e of[t,t.userData.back]){let t=e?.userData.u;t?.uFin&&(n?t.uFin.value.set(n.r,n.g,n.b,1):t.uFin.value.set(0,0,0,0))}}applyFinish(e,t){if(!e.finish)return;let n=tx(e.finish,t,this.order),r=n?nx(e.finish,n):null;this.setFin(e.jigMat,r),this.setFin(e.tableMat,r),this.finished.set(e.name,n)}applyInstalledFinish(e){let t=this.m29?.finish.rows;if(t)for(let n of this.installedMeshes()){let r=n.name.replace(/^installed:/,``).replace(/:left$/,``),i=t.find(e=>e.component.startsWith(`canard.`)&&(r===e.component||r.startsWith(e.component+`.`)));if(!i)continue;let a=tx(i,e,this.order);this.setFin(n.userData.front??n.material,a?nx(i,a):null),this.finished.set(n.name,a)}}finished=new Map;m28WhereOf(e,t){return mb(this.m28.parts[e.part],t,this.order)}kitBox(){let e=new Xn;for(let t of this.meshes){let n=this.m28?.parts[t.part];n&&n.side===`right`&&n.component.startsWith(`strake.`)&&cb.has(pb(n))&&e.union(t.base.boundingBox)}return e}strakeKitMatrix(e){if(!this.strakeKitM){let e=Hy.table,t=this.kitBox(),n=t.getCenter(new W);this.strakeKitM=new q().makeTranslation(e.x,e.topY+.002,e.z).multiply(new q().makeScale(Q,Q,Q)).multiply(new q().makeTranslation(-n.x,-t.min.y,-n.z))}return e&&pb(this.m28.parts[e.part])===`skin_top`?this.strakeKitM.clone().multiply(new q().makeTranslation(0,12,0)):this.strakeKitM}strakeKitBox(){let e=this.kitBox().clone(),t=this.meshes.find(e=>this.m28?.parts[e.part]?.side===`right`&&pb(this.m28.parts[e.part])===`skin_top`);return t&&e.union(t.base.boundingBox.clone().translate(new W(0,12,0))),e.applyMatrix4(this.strakeKitMatrix())}buildStrakeTable(){let e=Object.entries(this.m28?.parts??{}).filter(([,e])=>e.component===`strake.skins`&&pb(e)===`skin_bottom`);if(!e.length)return;let t=vm(this.cut,{color:11831896,hatch:!0,name:`strake-jig-table`});for(let[n,r]of e){let e=this.meshes.find(e=>e.part===n);if(!e)continue;let i=e.base.boundingBox,a=r.fs_min-4,o=r.fs_max+4,s=r.side===`right`,c=i.min.z-(s?4:.2),l=i.max.z+(s?.2:4),u=new ei(new sa(o-a,1,l-c),t);u.position.set((a+o)/2,i.min.y-.6-1/2,(c+l)/2),u.castShadow=!0,u.receiveShadow=!0,this.strakeTable.add(u)}this.strakeTable.name=`strake.jig_table`,this.strakeTable.visible=!1,this.strakeTable.userData.representational=!0,this.strakeTable.userData.hatch=!0}strakeTableAnchor(e){if(!this.strakeTable.visible||!this.strakeTable.children.length)return null;let t=this.strakeTable.children[0],n=new Xn().setFromObject(t);return e.set((n.min.x+n.max.x)/2,n.max.y+.01,n.min.z+(n.max.z-n.min.z)*.15)}labelColor(e){let t=this.data.parts[e.part]?.role;return t&&Jh[t]?`#`+Jh[t].color.toString(16).padStart(6,`0`):`#`+(e.hatch?Qp:yx[e.part]??bx[e.part]?.[0]??lm.foam).toString(16).padStart(6,`0`)}},zx=.0254,Bx=new URLSearchParams(location.search),Vx=Bx.get(`test`)===`1`,Hx=Bx.get(`rec`)===`1`;Bx.get(`clean`)===`1`&&document.body.classList.add(`clean`),Hx&&document.body.classList.add(`rec`);var Ux=document.getElementById(`status`),Wx=(e,t=!1)=>{Ux.hidden=e===null,Ux.textContent=e??``,Ux.classList.toggle(`err`,t)},$={ready:!1,meshNames:()=>[],stats:()=>({calls:0,triangles:0,pixels:0}),advance:()=>{},touring:()=>!1,tourIndex:()=>-1,strakeTable:()=>!1,finish:()=>({}),selected:()=>null,select:()=>{},camera:()=>({pos:[0,0,0],target:[0,0,0],fov:0}),shot:()=>null,flying:()=>!1,pose:()=>`upright`,flipping:()=>!1,tableTopY:()=>Tm,labShots:()=>({}),material:()=>null,setWet:()=>{},meshBox:()=>null,cut:()=>({enabled:!1,bl:0,planeConstant:null,keepsOutboard:!1,removesInboard:!1,cappedNodes:[],capsVisible:0,capNodesVisible:[],clipped:0}),plyBox:()=>null,setSection:()=>{},labels:()=>[],labelsAll:()=>[],cutGlow:()=>0,toWorld:e=>e,setCamera:()=>{},contextLost:()=>!1,loseContext:()=>!1,restoreContext:()=>!1,resScale:()=>1,tier:()=>`high`,setTier:()=>{},auto:()=>!1,setAuto:()=>{},feedFrame:()=>{},paths:()=>[],project:()=>[0,0],state:()=>({}),phase:()=>null,lay:()=>0,setLay:()=>{},play:()=>!1,playing:()=>!1,ghost:()=>{},freeze:()=>{},subject:()=>`canard`,setSubject:()=>{},placement:()=>({}),jigPose:()=>`upright`,fuseShots:()=>({}),cg:()=>({value:`not yet computed`,sub:null}),fuseToWorld:e=>e,fuseRestToWorld:e=>e,fuseTurning:()=>!1,fuseFloor:()=>null,gearMarks:()=>null,ground:()=>null,ref:()=>null,stateAll:()=>({}),stick:()=>null,setStick:()=>{},sparSlide:()=>null,canopy:()=>null,setCanopyOpen:()=>{},wing:()=>null,setAileron:()=>{},setRudder:()=>{},hide:()=>{},room:()=>({hidden:[],blocks:[],apron:!1}),zoomTo:()=>{},opIds:()=>[],kin:()=>null,cove:()=>null,elevators:()=>null,noseGear:()=>null,installedCanard:()=>null},Gx={dim:e=>`${e} in`,axle:e=>`Axle C.L. F.S. ${e} (book)`};Vx&&(window.__lab=$);function Kx(e,t){let n=e.geometry.clone().applyMatrix4(e.matrixWorld),r=n.attributes.position,i=n.attributes.normal,a=new Or,o=new Float32Array(r.count*3),s=new Float32Array(r.count*3);for(let e=0;e<r.count;e++)o.set([r.getX(e),r.getY(e),r.getZ(e)],e*3),i&&s.set([i.getX(e),i.getY(e),i.getZ(e)],e*3);let c=n.index?Array.from(n.index.array):Array.from({length:r.count},(e,t)=>t);if(t)for(let e=0;e<c.length;e+=3)[c[e+1],c[e+2]]=[c[e+2],c[e+1]];return a.setAttribute(`position`,new mr(o,3)),a.setIndex(c),i?a.setAttribute(`normal`,new mr(s,3)):a.computeVertexNormals(),a}function qx(e,t,n=new Set){e.updateMatrixWorld(!0);let r=new Map,i=e=>e.userData?.name??e.name;e.traverse(e=>{let a=e;if(!a.isMesh)return;let o=e,s=e=>!!t.components[i(e)]||n.has(i(e));for(;o&&!s(o)&&o.parent;)o=o.parent;let c=s(o)?i(o):i(e),l=e;for(;l&&!/\.p\d+$/.test(i(l))&&l.parent;)l=l.parent;let u=l&&/\.p\d+$/.test(i(l))?i(l):null;if(!u&&c.startsWith(`elevator.`)){let t=e;for(;t&&!/\.(left|right)$/.test(i(t))&&t.parent;)t=t.parent;t&&i(t).startsWith(`elevator.`)&&/\.(left|right)$/.test(i(t))&&(u=i(t))}let d=`${c}|${u??``}`;r.has(d)||r.set(d,{cid:c,node:u,geos:[]}),r.get(d).geos.push(Kx(a,a.matrixWorld.determinant()<0))});let a=[];for(let e of r.values()){let t=e.geos.length===1?e.geos[0]:kd(e.geos);if(!t)throw Error(`could not merge ${e.node??e.cid}`);a.push({cid:e.cid,node:e.node,geo:t})}return a}var Jx={dir:[.62,.6,.5],dx:-.32,dy:-.12,fill:.56};function Yx(e,t,n,r,i,a){let o=new js(r,i,.05,90),s=[];for(let t of[e.min.x,e.max.x])for(let n of[e.min.y,e.max.y])for(let r of[e.min.z,e.max.z])s.push(new W(t,n,r));let c=e=>{o.position.copy(t).addScaledVector(n,e),o.lookAt(t),o.updateMatrixWorld(!0),o.updateProjectionMatrix();let r=1e9,i=-1e9;for(let e of s){let t=e.clone().project(o).x;r=Math.min(r,t),i=Math.max(i,t)}return(i-r)/2},l=.5,u=12;for(let e=0;e<40;e++){let e=(l+u)/2;c(e)>a?l=e:u=e}let d=(l+u)/2,f=t.clone().addScaledVector(n,d);return{pos:[f.x,f.y,f.z],target:t.toArray(),fov:r}}async function Xx(){yp.value=vp(64);let e=document.getElementById(`gl`),t;try{t=new Od({canvas:e,antialias:!1,alpha:!1,powerPreference:`high-performance`,stencil:!1})}catch{Wx(`This page needs WebGL 2. Try a recent Chrome, Safari or Firefox.`,!0);return}t.outputColorSpace=Ue,t.toneMapping=0,t.shadowMap.enabled=!0,t.shadowMap.autoUpdate=!1,t.localClippingEnabled=!0,t.info.autoReset=!1;let n=matchMedia(`(pointer: coarse)`).matches,r=ph(Bx.get(`q`)),i=`lab.tierCap`,a=null;try{a=ph(window.sessionStorage.getItem(i))}catch{}let o=r??(Hx?`high`:mh({coarse:n,width:window.innerWidth,height:window.innerHeight}));!r&&!Hx&&a&&uh.indexOf(a)>uh.indexOf(o)&&(o=a);let s=bh(3e3),c=!Hx&&Bx.get(`freeze`)!==`1`,l=!r&&!Hx&&Bx.get(`freeze`)!==`1`;Hp.on=dh[o].cheapShaders;let u=new Fn;u.background=null;let d=Fm(t);u.environment=dh[o].cheapShaders?null:d,u.environmentIntensity=1.5;let f=new Ns(16770760,21,0,.5,1,2);f.position.set(-.7,Em.h-.35,.5),f.castShadow=!0,f.shadow.mapSize.set(Math.max(1,dh[o].shadowMap),Math.max(1,dh[o].shadowMap)),f.shadow.camera.near=.5,f.shadow.camera.far=6,f.shadow.bias=-8e-4,f.shadow.normalBias=.03,f.shadow.radius=4,u.add(f,f.target);let p=new Rs(12177407,.9);p.position.set(-3,1.6,2.4),u.add(p),f.visible=p.visible=!dh[o].cheapShaders,t.shadowMap.enabled=!dh[o].cheapShaders;let m=new js(30,16/9,.05,90);m.position.set(-3.4,1.9,2.6);let h=new Gf(m,e);h.enableDamping=!0,h.dampingFactor=.075,h.minDistance=.15,h.maxDistance=7.5,h.maxPolarAngle=Math.PI*.495,h.rotateSpeed=.7;let g=new qm(m,h),_=new Ap(t,{ao:dh[o].ao,msaa:dh[o].msaa,aoSamples:Hx?16:dh[o].aoSamples});_.params.ao=.55,_.params.sharpen=.25,_.params.bloom=.12;let v=()=>{let e=dh[o];_.configure({ao:e.ao,aoSamples:Hx?16:e.aoSamples,aoScale:e.aoScale,msaa:e.msaa,bloom:e.bloom}),_.params.dofTaps=Hx?40:e.dofTaps};v();let y=()=>{let e=window.innerWidth,n=window.innerHeight,r=Math.max(.1,fh(dh[o],window.devicePixelRatio,e,n)*Math.sqrt(s.scale));t.setPixelRatio(r),t.setSize(e,n,!1),m.aspect=e/n,m.updateProjectionMatrix(),_.setSize(Math.round(e*r),Math.round(n*r)),Mp.value=Math.round(n*r),g.scale=m.aspect>=1?Math.max(1,1.6/m.aspect):Math.min(3.2,1.6/m.aspect*.82),g.outsideScale=m.aspect>=1?null:1.8,g.lastUser<0&&!g.flying&&b&&g.set(b)},b=null;g.onShot=e=>{h.maxDistance=e.outside?Math.max(7.5,new W(...e.pos).sub(new W(...e.target)).length()*(g.outsideScale??g.scale)*1.05):7.5},g.clampPos=e=>{e.x=At.clamp(e.x,Em.x0+.4,Em.x1-.5),e.z=At.clamp(e.z,Em.z0+.5,Em.z1-.4),e.y=At.clamp(e.y,.25,Em.h-.45)},window.addEventListener(`resize`,y),y();let x=0,S=()=>{},C=()=>{},w=()=>{},T=()=>{},E=()=>{},D=()=>{},O=()=>{},k=()=>{},A=e=>{x+=e,jp.value=x,O(x),S(e),D(e),k(e),C(e),w(e),E(e),g.update(e),h.update(),T(e)},ee=!1,te=!1,j=document.getElementById(`gl-lost`),ne=Vx&&Bx.get(`nocull`)===`1`,M=null,N=``,re=new Set,ie=()=>{if(!M)return;re=ne?new Set:Cm(m.position.toArray(),M.planes);let e=[...re].sort().join();e!==N&&(N=e,M.setHidden(re))},ae=()=>{ee||(ie(),_.params.dofFocus=m.position.distanceTo(h.target),_.params.dofAperture=dh[o].dof?9:0,t.info.reset(),_.render(u,m,x),te&&t.info.render.calls>0&&!t.getContext().isContextLost()&&(te=!1,j&&(j.hidden=!0)))},oe=performance.now(),se=gh(o,3e3),ce=()=>{},le=e=>{if(e===o)return;o=e,s=bh(1500);let n=dh[e];v(),f.shadow.mapSize.set(Math.max(1,n.shadowMap),Math.max(1,n.shadowMap)),f.shadow.dispose(),_.shadowDirty=!0,u.environment=n.cheapShaders?null:d,f.visible=p.visible=!n.cheapShaders,t.shadowMap.enabled=!n.cheapShaders,u.traverse(e=>{let t=e.material;if(t)for(let e of Array.isArray(t)?t:[t])e.needsUpdate=!0}),qp(u,n.cheapShaders),y(),ce()},P=e=>{l=e,se=gh(o),ce()},ue=e=>{if(o!==`low`||!c)return;let t=Sh(s,e),n=t.scale!==s.scale;s=t,n&&y()},de=e=>{if(ue(e),!l)return;let t=vh(se,e),n=t.tier!==se.tier;se=t,n&&le(t.tier)},fe=!Vx||Bx.get(`realframes`)===`1`,pe=Vx&&Bx.get(`freeze`)===`1`;Hx||t.setAnimationLoop(()=>{let e=performance.now(),t=Math.min((e-oe)/1e3,.1);fe&&$.ready&&!pe&&!ee&&de(e-oe),oe=e,pe||A(t),ae()});let me=document.getElementById(`gl-lost-reload`);e.addEventListener(`webglcontextlost`,e=>{e.preventDefault(),ee=!0,te=!1,se=gh(o),j&&(j.hidden=!1)}),e.addEventListener(`webglcontextrestored`,()=>{try{yp.value&&(yp.value.needsUpdate=!0),d.dispose(),d=Fm(t),u.environment=dh[o].cheapShaders?null:d,f.shadow.dispose(),_.shadowDirty=!0,u.traverse(e=>{let t=e.material;if(t)for(let e of Array.isArray(t)?t:[t])e.needsUpdate=!0}),y();let e=uh[uh.indexOf(o)+1];if(l&&e){le(e);try{window.sessionStorage.setItem(i,e)}catch{}}se=gh(o,3e3),oe=performance.now(),ee=!1,te=!0}catch(e){console.error(`context restore failed`,e)}}),me?.addEventListener(`click`,()=>{let e=new URL(location.href),t=$.selected();t&&e.searchParams.set(`op`,t),location.replace(e.toString())});let F=t.getContext().getExtension(`WEBGL_lose_context`),he=()=>F;$.contextLost=()=>ee,$.loseContext=()=>{let e=he();return e?(e.loseContext(),!0):!1},$.restoreContext=()=>{let e=he();return e?(e.restoreContext(),!0):!1},$.freeze=e=>{pe=e},$.advance=e=>{A(e),ae()},$.resScale=()=>s.scale,$.tier=()=>o,$.setTier=e=>{l=!1,e===o?ce():le(e)},$.auto=()=>l,$.setAuto=P,$.feedFrame=de,$.stats=()=>({calls:t.info.render.calls,triangles:t.info.render.triangles,pixels:_.w*_.h});let ge=[],_e=new Dn;_e.name=`canardRoot`,u.add(_e);let ve=new Dn;ve.scale.setScalar(zx),_e.add(ve),$.meshNames=()=>ge.map(e=>e.node??e.cid);try{let t=document.querySelector(`meta[name="data-base"]`)?.content||`./`,[n,r]=await Promise.all([fetch(t+`graph.json`).then(e=>{if(!e.ok)throw Error(`graph.json ${e.status}`);return e.json()}),fetch(t+`config.json`).then(e=>{if(!e.ok)throw Error(`config.json ${e.status}`);return e.json()})]),i=fetch(t+`ledger.json`).then(e=>e.ok?e.json():null).catch(()=>null),a=await new Pd().loadAsync(t+r.model),s=n.layup?.fuselage??null,c=s?{...s,parts:{...s.parts,...s.extras?.nose_parts??{},...s.extras?.m25?.parts??{},...s.extras?.m26?.parts??{},...s.extras?.m27?.parts??{},...s.extras?.m28?.parts??{},...s.extras?.m29?.parts??{}},nodes:{...s.nodes,...s.extras?.m25?.nodes??{},...s.extras?.m26?.nodes??{},...s.extras?.m27?.nodes??{}}}:null,d=new Set(s?[...Object.values(s.parts).map(e=>e.node),...Object.keys(s.nodes)]:[]),p=new Set([...Object.values(c?.parts??{}).map(e=>e.node),...Object.values(c?.stages??{}).flat().map(e=>e.node)]),v=qx(a.scene,n,p),y=e=>Bg.some(t=>e.startsWith(t)),ee=e=>e.startsWith(`elevator.`),te=v.filter(e=>!y(e.cid)&&!ee(e.cid)),j=v.filter(e=>ee(e.cid)),ne=v.filter(e=>y(e.cid)).map(e=>({...e,name:e.node??e.cid})),N=await i,oe=new up(ve,80,-80);oe.amount=0;let se=n.layup?.nodes??null,le=new Map;for(let e of Object.values(n.plies??{}))for(let t of e)le.set(t.node,t);let ue=(e,t)=>{let n=bm(e.node,e.cid,se);return{spec:n,mat:n.kind===`part`?vm(t):mm(n,t,um(e.geo),dm(e.geo))}};for(let e of te){let{spec:t,mat:n}=ue(e,oe),r=new ei(e.geo,n);r.name=e.node??e.cid,r.castShadow=!0,r.receiveShadow=!0,zp(n),r.userData.cove=!0,r.customDepthMaterial=Bp(oe),ve.add(r);let i=e.node?le.get(e.node):void 0;if(e.node&&!i)throw Error(`ply ${e.node} is not in graph.plies`);ge.push({cid:e.cid,node:e.node,mesh:r,mat:n,spec:t,ply:i?{op:i.op,order:i.order}:null})}oe.collect(ve),oe.update(),ve.updateMatrixWorld(!0);let de=new Xn().setFromObject(ve),fe=de.getCenter(new W),pe=de.getSize(new W),me=Pm(pe.z,pe.x);u.add(me.group),M={planes:me.planes,setHidden:me.setHidden};let F=c&&ne.length?new Rx(ne,c,n):null;F&&u.add(F.group),ve.position.copy(fe).multiplyScalar(-1);let he=me.jigTopY+pe.y/2+.001,ye=pe.x/2,be=pe.y/2,xe=e=>e===`inverted`?Math.PI:0,Se=`upright`,Ce=0,we=0,Te=1,Ee=(e,t)=>{let n=Math.abs(Math.sin(e)),r=Math.abs(Math.cos(e));_e.rotation.set(0,0,e),_e.position.set(0,he+(ye*n+be*r-be)+.03*Math.sin(Math.PI*t),0),_e.updateMatrixWorld(!0)};Ee(0,0),S=e=>{if(F?.stepTurn(e)&&(_.shadowDirty=!0),Te>=1)return;Te=Math.min(1,Te+e/1.2);let t=Km(Te);Ee(Ce+(we-Ce)*t,t),_.shadowDirty=!0};let De=(e,t)=>{if(e===Se&&Te>=1)return;let n=Te>=1?xe(Se):Ce+(we-Ce)*Km(Te);Se=e,Ce=n,we=xe(e),Te=+!t,Ee(t?Ce:we,0),_.shadowDirty=!0},Oe=e=>new q().compose(new W(0,he,0),new jt().setFromAxisAngle(new W(0,0,1),xe(e)),new W(1,1,1)).multiply(new q().compose(ve.position.clone(),new jt,new W(zx,zx,zx))),ke=new Xn().setFromObject(ve),Ae=ke.getCenter(new W);f.target.position.copy(Ae),f.target.updateMatrixWorld(),_.shadowDirty=!0;let je=s?.extras?.elevators??null,Me=je?.cove?Xp(je.tube_le_x,je.cove.slot_gap,je.cove.bl_end,je.cove.bl_start):null,I=!1,Ne=[],Pe=(e,t,n=!1)=>e===`elevator.right`||e===`elevator.left`?n?mm({kind:`foam`,angles:[]},t,0,void 0,{hatch:!0}):vm(t,{color:lm.und,hatch:!0,name:`elevator-skin`,roughness:.55}):e===`elevator.tube`?vm(t,{color:9278362,metalness:.9,roughness:.3,hatch:!0,name:`elevator-tube`}):e===`elevator.hinges`?vm(t,{color:12172996,metalness:.85,roughness:.35,hatch:!0,name:`elevator-hinges`}):vm(t,{color:6119784,metalness:.7,roughness:.5,hatch:!0,name:`elevator-weight`}),Fe=e=>e.cid===`elevator.left`||(e.node??``).endsWith(`.left`);for(let e of j.filter(e=>!Fe(e))){let t=(t,n)=>{let r=Pe(e.cid,oe,n),i=new ei(n?e.geo.clone():e.geo,r);i.name=t,i.castShadow=!0,i.receiveShadow=!0,i.matrixAutoUpdate=!1,ve.add(i);let a={cid:e.cid,node:t,mesh:i,mat:r,spec:{kind:n?`foam`:`part`,angles:[]},ply:null};ge.push(a),Ne.push(a)};t(e.node??e.cid,!1),e.cid===`elevator.right`&&t((e.node??e.cid)+`~core`,!0)}let L=new Dn;L.name=`tubeJigs`,L.visible=!1;let Ie=[];{let e=j.find(e=>e.node===`elevator.tube.right`);if(e&&je){e.geo.computeBoundingBox();let t=e.geo.boundingBox,n=(Tm-he-ve.position.y)/zx,r=t.min.y,i=r-n,a=vm(oe,{color:12160860,hatch:!0,name:`nc7-jig`});for(let e of[t.min.z+5,t.max.z-5]){let n=new ei(new sa(2.4,i,1.6),a);n.position.set((t.min.x+t.max.x)/2,r-i/2,e),n.castShadow=!0,n.receiveShadow=!0,L.add(n),Ie.push(new W((t.min.x+t.max.x)/2,r,e))}ve.add(L)}}if(oe.collect(ve),oe.update(),F&&s?.extras){let e=[];for(let t of te){let n=t.geo.clone(),{mat:r}=ue({...t,geo:n},F.cut);zp(r);for(let i of[!1,!0]){let a=new ei(n,r);a.userData.cove=!0,a.customDepthMaterial=Bp(F.cut),a.name=`installed:${t.node??t.cid}${i?`:left`:``}`,e.push({mesh:a,mirror:i})}}for(let t of j){let n=new ei(t.geo.clone(),Pe(t.cid,F.cut));n.name=`installed:${t.node??t.cid}`,e.push({mesh:n,mirror:!1})}F.attachInstalled(e),Me&&(F.cut.setCove(Me),_.shadowDirty=!0)}let Le=Ae.clone().add(new W(0,-.06,0));g.shots.home=Yx(ke,Le,new W(-.66,.26,.7).normalize(),30,1.6,.7);let Re={},ze=e=>{Re=Gm(n.tours??{},t=>Vm(n,e,t));for(let e of Object.keys(g.shots))e!==`home`&&e!==`cutclose`&&!He.has(e)&&delete g.shots[e];for(let[t,r]of Object.entries(Re)){let i=Oe(Vm(n,e,t)),a=new W(...r.target).applyMatrix4(i),o=new W(...r.position).applyMatrix4(i);g.shots[t]={pos:[o.x,o.y,o.z],target:[a.x,a.y,a.z],fov:30}}},Be={dist:47,el:27,az:-55,target:[4,.4,-25]};{let e=Oe(`upright`),t=Be.el*Math.PI/180,n=Be.az*Math.PI/180,r=new W(...Be.target),i=r.clone().add(new W(Be.dist*Math.cos(t)*Math.sin(n),Be.dist*Math.sin(t),Be.dist*Math.cos(t)*Math.cos(n)));r.applyMatrix4(e),i.applyMatrix4(e),g.shots.cutclose={pos:i.toArray(),target:r.toArray(),fov:30}}let Ve=n.order.filter(e=>F_.has(n.ops.find(t=>t.id===e)?.chapter??-1)),He=new Set(F?[...Ve,`fhome`,`fcut`,`ffinal`,`flowerA`,`flowerB`,`fwide12`,`fwide13`,...Object.values(oy).map(e=>`fcut${e}`)]:[]),We=Ve.filter(e=>n.ops.find(t=>t.id===e)?.chapter===6).at(-1)??null;if(F){Object.assign(g.shots,F.shots(Ve,30));let e=F.homeBox(),t=e=>Ve.filter(t=>n.ops.find(e=>e.id===t)?.chapter===e).at(-1)??null;g.shots.fcut=F.cutShot(72,30,t(6));for(let[e,n]of Object.entries(oy))g.shots[`fcut${n}`]=F.cutShot(n,30,t(Number(e)),sy[n]);g.shots.fhome=Yx(e,e.getCenter(new W).add(new W(-.22,-.05,0)),new W(-.22,.6,.77).normalize(),30,1.6,.62);let r=F.finishedBox();g.shots.ffinal=Yx(r,r.getCenter(new W).add(new W(Jx.dx,Jx.dy,0)),new W(...Jx.dir).normalize(),30,1.6,Jx.fill);let i=F.restMatrix(`on-gear`),a=e=>e.clone().applyMatrix4(i),o=a(F.installedBox(24)),s=a(F.installedBox(0)),c=(e,t)=>new W(...Ly({focus:`box`,dist:1,el:t,az:e})).normalize(),l=c(-52,24);c(-48,34),g.shots.flowerA=Yx(o.clone().union(r),o.getCenter(new W).add(new W(Jx.dx*.3,-.2,0)),l,30,1.6,.74),g.shots.flowerB=Yx(s,s.getCenter(new W).add(new W(Jx.dx*.3,-.1,0)),l,30,1.6,.64);let u=r.clone().union(s);g.shots.fwide12=Yx(u,u.getCenter(new W).add(new W(Jx.dx*.3,-.08,0)),l,30,1.6,.66),g.shots.fwide13=Yx(u,u.getCenter(new W).add(new W(Jx.dx*.3,-.08,0)),c(40,20),30,1.6,.66)}let Ge=e=>{if(!g.shots[e])return null;let t=g.landing(e);return{pos:t.pos.toArray(),target:t.target.toArray(),fov:t.fov}},Ke=null;try{Ke=window.localStorage}catch{Ke=null}let qe=zm(Ke??{getItem:()=>null,setItem:()=>{}}),Je=`roncz`,R=null,z=`canard`,Ye={canard:void 0,fuselage:void 0},Xe=!0,Ze=`longez.ghost`,Qe=!1;try{Qe=Ke?.getItem(Ze)===`1`}catch{Qe=!1}n.__ghost=Qe;let $e=ge.map(e=>({name:e.node??e.cid,component:e.cid,ply:e.ply})),et=e=>e?Object.values(n.plies??{}).flat().filter(t=>t.op===e).length:0,B=e=>et(e)+(F?F.opCount(e):0),V=0,tt=eh,nt=!1,rt=1,it=new Map,at=new Map,ot=new Map,st=``,ct=``,lt=(Bx.get(`hide`)??``).split(`,`).filter(Boolean),H=e=>e?n.ops.find(t=>t.id===e)?.chapter??-1:-1,ut=e=>e?n.order.indexOf(e):-1,dt=new Set(w_),ft=new Set([`r30.elev-nc2-inserts`,`r30.elev-bond-cores`,`r30.elev-skin-bottom`,`r30.elev-skin-top`,`r30.elev-trim-ends`]),pt=()=>H(R)!==11,mt=()=>z!==`canard`||!R?`none`:dt.has(R)?`travel`:R===`r30.elev-balance-check`?`hang`:ft.has(R)?`apart`:`none`,ht=je?.hinge_xz??[0,0],gt=je?e_(je.hang_cg.dx,je.hang_cg.dz):0,_t=je?t_(je.hang_cg.dx,je.hang_cg.dz):!1,vt=0,yt=0,bt=0,xt=new q,St=new q,Ct=new q,wt=()=>{if(!je)return;let e=mt(),t=ut(R)>=ut(`r30.elev-skin-bottom`),[n,r]=ht;for(let i of Ne){(i.node.endsWith(`~core`)?t:i.cid===`elevator.right`&&!t)&&(i.mesh.visible=!1);let a=i.cid!==`elevator.hinges`||e===`hang`;xt.makeTranslation(yt,0,0),a&&xt.multiply(St.makeTranslation(n,r,0)).multiply(Ct.makeRotationZ(-bt*Math.PI/180)).multiply(St.makeTranslation(-n,-r,0)),i.mesh.matrix.copy(xt),i.mesh.matrixWorldNeedsUpdate=!0}L.visible=z===`canard`&&(e===`apart`||e===`hang`)&&[`built`,`current`].includes(it.get(`elevator.tube.right`)??``),L.position.x=e===`hang`?yt:10;let i=!!Me&&z===`canard`&&Ne.some(e=>(it.get(e.node)??`hidden`)!==`hidden`);i!==I&&(I=i,oe.setCove(i?Me:null),_.shadowDirty=!0),ve.updateMatrixWorld(!0)},Tt=s?.extras?.nose_gear??null,Et=()=>z!==`fuselage`||!R||!Tt?0:R===`f13.rig-nose-gear`?x_(vt,Tt.retract_seconds):+(ut(R)>ut(`f13.rig-nose-gear`)),Dt=()=>{if(z===`canard`&&je){let e=mt();return e===`travel`?{label:`Elevator travel`,value:s_(bt,je.travel),sub:`Roncz limits: 30 down, 15 up (12.5 is the absolute floor)`}:e===`hang`?{label:`Elevator hang`,value:d_(gt,_t,vt>u_()),sub:`Hung on its hinge line; ${je.hang_cg.note}`}:null}if(z===`fuselage`&&F&&Mt){let e=Yh(R,Mt,It());if(e)return e}if(z===`fuselage`&&F&&K){let e=Rg(R,K,Bt(),Vt());if(e)return e}if(z===`fuselage`&&F&&Nt){let e=kb(R,Nt,n.ops.find(e=>e.id===R)?.materials??[]);if(e)return e}if(z===`fuselage`&&F&&G){let e=_x(R,G,n.ops.find(e=>e.id===R)?.materials??[]);if(e)return e}if(z===`fuselage`&&F&&Ot&&R===`f16.pitch-pushrod`)return{label:`Pitch stick and elevators`,value:M_(U(),Ot),sub:`Roncz limits: 30 down, 15 up (12.5 is the absolute floor)`};if(z===`fuselage`&&F&&R===`f14.fit-fuselage`){let e=At();return{label:`Spar slide-in`,value:e>=1?`In the box`:`${Math.round(e*100)}% in`,sub:`Entering from the side; the plywood firewall is still loose`}}if(z===`fuselage`&&F&&Tt&&F.nosePresent){let e=Tt.candidates;return{label:`Nose gear`,value:S_(F.noseProgress,Tt.crank_turns),sub:`Axle station is a conflict: F.S. ${e.plans.axle_fs} (plans, drawn) or about ${e.manual.axle_fs} (manual, ghost)`}}return null},Ot=s?.extras?.m25?.controls??null,kt=null,At=()=>R===`f14.fit-fuselage`?Qg(vt):1,U=()=>!Ot||!je?0:O_(kt??(R===`f16.pitch-pushrod`?-a_(vt,je.travel):0),Ot),Mt=s?.extras?.m26?.canopy??null,Nt=s?.extras?.m28??null,G=s?.extras?.m29??null,Pt=null,Ft=()=>R===`f18.cut-remove`?Fh(vt):1,It=()=>!Mt||R!==`f18.hinges`?0:Bh(Pt??Rh(vt)*Mt.hinge.max_open_deg,Mt.hinge.max_open_deg),Lt=()=>Y.setCanopy(z===`fuselage`&&R===`f18.hinges`&&!!Mt,It(),Uh(It()),Mt?.hinge.max_open_deg),K=s?.extras?.m27??null,Rt=null,zt=null,Bt=()=>!K||R!==`f19.aileron-build`?0:wg(Rt??yg(vt)*K.aileron.max_up_deg,K.aileron.max_up_deg),Vt=()=>!K||R!==`f20.rudder-hang`?0:Tg(zt??Sg(vt)*K.rudder.max_deg,K.rudder.max_deg),Ht=()=>{Y.setAileron(z===`fuselage`&&R===`f19.aileron-build`&&!!K,Bt(),kg(Bt()),K?.aileron.max_up_deg),Y.setRudder(z===`fuselage`&&R===`f20.rudder-hang`&&!!K,Vt(),jg(Vt()),K?.rudder.max_deg)},Ut=e=>Math.abs(e)<.05?`Neutral`:e>0?`${e.toFixed(1)} up`:`${(-e).toFixed(1)} down`,Wt=()=>Y.setStick(z===`fuselage`&&R===`f16.pitch-pushrod`&&!!Ot,U(),Ut(U())),Gt=()=>{Y.setKin(Dt()),Wt(),Lt(),Ht()},Kt=()=>{F&&z===`fuselage`&&Ot&&(F.setSparSlide(At()),F.setStick(U())),F&&z===`fuselage`&&Mt&&(F.setCanopyLift(Ft()),F.setCanopyOpen(It())),F&&z===`fuselage`&&K&&(F.setAileron(Bt()),F.setRudder(Vt())),yt=mt()===`apart`?10:0,bt=0,wt()};D=e=>{if(vt+=e,z===`canard`&&je){let t=mt(),n=1-Math.exp(-e*3.5),r=yt,i=bt;if(t===`travel`)i=a_(vt,je.travel),r+=(0-r)*n;else if(t===`hang`){let e=l_(vt,gt);i=e.degDown,r=e.slide}else r+=((t===`apart`?10:0)-r)*n,i+=(0-i)*n;t!==`hang`&&(Math.abs(r-(t===`apart`?10:0))<.001&&(r=t===`apart`?10:0),Math.abs(i)<.001&&t!==`travel`&&(i=0)),(r!==yt||i!==bt)&&(yt=r,bt=i,wt(),_.shadowDirty=!0)}if(z===`fuselage`&&F){let e=Et();if(e!==F.noseProgress&&(F.setNose(e),_.shadowDirty=!0),Ot){let e=At(),t=U();(Math.abs(F.sparSlideInches-(1-e)*F.slideDistance())>1e-9||t!==F.stickDeflUp)&&(_.shadowDirty=!0),F.setSparSlide(e),F.setStick(t)}if(Mt){let e=Ft(),t=It();(e!==F.canopyLiftK||t!==F.canopyOpenDeg)&&(_.shadowDirty=!0),F.setCanopyLift(e),F.setCanopyOpen(t)}if(K){let e=Bt(),t=Vt();(e!==F.aileronUpDeg||t!==F.rudderOutDeg)&&(_.shadowDirty=!0),F.setAileron(e),F.setRudder(t)}}Gt()};let qt=()=>{at=new Map(Im(n,Je).map((e,t)=>[e.id,t]));let e=z===`canard`?$e:F?.infos??[];if(it=R&&at.has(R)?Ym(n,Je,R,V,e):new Map(e.map(e=>[e.name,`built`])),z===`canard`&&pt())for(let e of Ne)it.set(e.node,`hidden`)},Jt=()=>{let e=R?at.get(R):void 0,t=B(R),n=``;for(let r of ge){let i=r.node??r.cid,a=it.get(i)??`hidden`,o=r.ply&&e!==void 0?rh({meshOpIndex:at.get(r.ply.op),curOpIndex:e,order:r.ply.order,lay:V,count:t,t:tt,ghost:Qe}):ih(a);ot.set(i,o),r.mesh.visible=a!==`hidden`&&!(r.ply&&a===`current`&&o.unroll<=0)&&!lt.some(e=>i.startsWith(e)),r.mesh.castShadow=a===`built`||a===`current`&&o.unroll>=1,gm(r.mat,{unroll:o.unroll,front:o.front,cure:o.cure,ghost:a===`ghost`}),n+=r.mesh.visible&&r.mesh.castShadow?`1`:`0`}if(wt(),F&&(z===`fuselage`||Xe)&&(ct=z===`fuselage`?F.paint(it,R,V,tt,Qe,at):F.paint(null,null,V,tt,Qe,at,We),Xe=!1),F&&lt.length)for(let e of F.installedMeshes())e.visible=!lt.some(t=>e.name.startsWith(t));if(F&&lt.length)for(let e of F.meshes)lt.some(t=>e.name.startsWith(t))&&(e.jig.visible=e.table.visible=!1);n+=ct,n!==st&&(st=n,_.shadowDirty=!0)},Yt=`longez.paths`,Xt={bending:{color:16738832,speed:.9,scale:9},shear:{color:2787071,speed:.9,scale:8},lift:{color:1106032,speed:1.2,scale:2.5}},Zt={base:.45,pulse:2.2,core:1.6,halo:.9,hot:.08,dim:.85,halfWidth:.4*zx,px:[7,20]},Qt=!0,$t={labels:null,paths:null},en=()=>$t.paths??Qt;try{Qt=Ke?.getItem(Yt)!==`0`}catch{Qt=!0}let tn=new Dn;tn.name=`loadPaths`,tn.rotation.x=-Math.PI/2,ve.add(tn);let nn={value:1},rn={};for(let[e,t]of Object.entries(Xt))rn[e]=Fp(oe,{...Zt,color:t.color,emph:nn,speed:t.speed,scale:t.scale});let an=[];for(let e of n.loadpaths??[]){let t=rn[e.kind],n=new Dn;n.name=e.id,n.visible=!1;for(let r of t?e.segments:[]){let i=r.map(([e,t,n])=>new W(e,t,n));(e.kind===`bending`||e.kind===`shear`)&&i[0].y<i[i.length-1].y&&(i=i.reverse());let a=new ei(Ip(i),t);a.layers.set(2),a.renderOrder=10,a.frustumCulled=!1,n.add(a)}tn.add(n),an.push({p:e,group:n,visible:!1})}let on=()=>{for(let e of an)e.visible=z===`canard`&&Xm(e.p,it),e.group.visible=e.visible&&en()};E=e=>{let t=+!!an.some(e=>e.group.visible);em.value+=(t-em.value)*(1-Math.exp(-e*5)),Math.abs(t-em.value)<.001&&(em.value=t)};let sn=e=>{Qt=e;try{Ke?.setItem(Yt,e?`1`:`0`)}catch{}Y.setPaths(e),on()},cn=()=>{qt(),Jt(),on(),Y.setBuild(V,B(R)),Ln()},ln=()=>{nt=!1,Y.setPlaying(!1)},un=()=>{ln(),V=B(R),tt=eh,cn()},dn=e=>{ln(),V=Math.max(0,Math.min(e,B(R))),tt=0,cn()},fn=()=>{if(nt){ln();return}B(R)&&(V=1,tt=0,nt=!0,Y.setPlaying(!0),cn())},pn=e=>{Qe=e,n.__ghost=e,Xe=!0;try{Ke?.setItem(Ze,e?`1`:`0`)}catch{}Y.setGhost(e),cn()};C=e=>{let t=B(R),n=tt,r=!1;if(tt+=e*rt,nt){for(;V<t&&tt>=2.5500000000000003;)tt-=ah,V++,r=!0;V>=t&&tt>=3.7&&ln()}tt=Math.min(tt,eh),r?cn():tt!==n&&Jt()};let mn=(e,t)=>{b=e,t?g.fly(e,1.8,.05):g.set(e)},hn=.001,gn=n.layup?.nodes??null,_n=n.layup?.semi_span??70,vn=!1,yn=Math.round(_n/2),bn=0;for(let e of ge)e.mesh.geometry.computeBoundingBox();let xn=e=>e.node??e.cid,Sn=e=>it.get(xn(e)),Cn=e=>{let t=Sn(e);return(t===`built`||t===`current`)&&e.mesh.visible},wn=e=>{let t=e.mesh.geometry.boundingBox;return t.min.z-hn<=-yn&&-yn<=t.max.z+hn},Tn=e=>vn&&Cn(e)&&wn(e),En=()=>{oe.amount=vn?1-(-yn+hn-oe.depth)/(oe.extent-oe.depth):0,oe.update(),oe.uGlow.value=vn?bn:0};w=e=>{bn>0&&(bn*=Math.exp(-e*4),bn<.01&&(bn=0)),vn&&(En(),e>0&&bn>0&&(_.shadowDirty=!0)),F&&Mn>0&&(Mn*=Math.exp(-e*4),Mn<.01&&(Mn=0)),F&&An&&(F.setStation(!0,jn,Mn),e>0&&Mn>0&&(_.shadowDirty=!0))};let On=22,kn=125.5,An=!1,jn=70,Mn=0,Nn=(e,t)=>{let n=An;An=e&&!!F,jn=Math.max(On,Math.min(t,kn)),Mn=1,F?.setStation(An,jn,Mn),An!==n&&Jt(),_.shadowDirty=!0,Y.setSection(An,jn),Ln()},J=(e,t)=>{if(z===`fuselage`){Nn(e,t);return}let n=vn;vn=e&&!!gn,yn=Math.max(0,Math.min(t,_n)),bn=1,En(),vn!==n&&Jt(),_.shadowDirty=!0,Y.setSection(vn,yn),Ln()},Pn=[`UND`,`BID`],Fn=()=>F&&An?F.capped(jn,e=>it.get(e)):[],In=()=>{if(!F)return;let e=B(R),t=new Map;for(let e of F.meshes){let n=it.get(e.name);!e.row||n!==`built`&&n!==`current`||t.set(e.row.cloth,(t.get(e.row.cloth)??0)+1)}let r=[...t].sort(([e],[t])=>(Pn.indexOf(e)+1||99)-(Pn.indexOf(t)+1||99)||e.localeCompare(t)).map(([e,t])=>`${e} ${t}`).join(` · `),i=`Turn on the section to list the layers there`;if(An){let e=Fn(),t=new Set(e.filter(e=>e.row).map(e=>e.name));i=Pv(F.data.parts,e.filter(e=>!e.row).map(e=>e.part),Nv(F.data.nodes,jn,t))}Y.setReadout({station:An?Ov(jn):`Section off`,layers:i,plies:e?`${V} / ${e}`:null,cloth:r||`none yet`}),Y.setCg(Iv(N)),Y.setGround(Rv(N)),Y.setRef(zv(N,R,n.order)??Xh(N,R,n.order)??zg(N,R,n.order)??Ab(N,Nt,R,n.order)??vx(G,R,n.order)),Gt()},Ln=()=>{if(z===`fuselage`){In();return}Y.setCg(null),Y.setGround(null),Y.setRef(null);let e=B(R),t=new Map,r={};for(let e of ge){if(!e.node||!gn?.[e.node])continue;let n=it.get(e.node);(n===`built`||n===`current`)&&(t.set(gn[e.node].cloth,(t.get(gn[e.node].cloth)??0)+1),r[e.node]=gn[e.node])}let i=[...t].sort(([e],[t])=>(Pn.indexOf(e)+1||99)-(Pn.indexOf(t)+1||99)||e.localeCompare(t)).map(([e,t])=>`${e} ${t}`).join(` · `),a=gn?`Turn on the section to list the layers there`:``;if(vn){let e=Object.keys(n.components),t=ge.filter(e=>!e.node&&Tn(e)).sort((t,n)=>e.indexOf(t.cid)-e.indexOf(n.cid)).map(e=>n.components[e.cid]?.label??e.cid),i=oh(r,yn);(i.length||!t.length)&&t.push(ch(n,i)),a=t.join(` · `)}Y.setReadout({station:vn?sh(yn):`Section off`,layers:a,plies:e?`${V} / ${e}`:null,cloth:i||`none yet`}),Gt()},Rn=`longez.labels`,zn=!0;try{zn=Ke?.getItem(Rn)!==`0`}catch{zn=!0}let Bn=new Vy(document.getElementById(`labels`),m),Vn=e=>`#`+e.toString(16).padStart(6,`0`),Hn=new ac,Un=ve.matrixWorld.clone(),Wn=(e,t)=>{let n=ge.filter(t=>t.cid===e).map(e=>e.mesh);if(!n.length)return null;let r=new Xn;for(let e of n)r.union(e.geometry.boundingBox);let i=e.includes(`bottom`)?new W(0,1,0):e.includes(`shear_web`)?new W(1,0,0):new W(0,-1,0),a=r.getCenter(new W),o=Math.min(Math.max(-t,r.min.z+.3),r.max.z-.3);for(let e of[.5,.4,.6,.3,.7,.2,.8]){let t=new W(r.min.x+(r.max.x-r.min.x)*e,a.y,o);i.x?t.set(r.min.x-4,a.y,o):t.y=i.y<0?r.max.y+4:r.min.y-4,Hn.set(t.clone().applyMatrix4(Un),i);let s=Hn.intersectObjects(n,!1)[0];if(s)return{bl:-o,p:s.point.clone().applyMatrix4(Un.clone().invert()),n:(s.face?.normal??i.clone().negate()).clone()}}return null},Gn=new W,Kn=new W,qn=new W,Jn=new Xn,Yn=new W;for(let e of Object.keys(n.components)){if(e.startsWith(`elevator.`)){let t=ge.filter(t=>t.cid===e);if(!t.length)continue;Bn.add({id:e,text:je?.parts[e]?.label??`${n.components[e]?.label??e} (fitted shape)`,color:Vn(Qp),cls:`fitted`,at:()=>{Jn.makeEmpty();for(let e of t)e.mesh.visible&&Jn.union(new Xn().setFromObject(e.mesh));return Jn.isEmpty()?null:Yn.set((Jn.min.x+Jn.max.x)/2,Jn.max.y+.015,Jn.min.z+(Jn.max.z-Jn.min.z)*.3)},vis:()=>z!==`canard`||!($t.labels??zn)||!t.some(Cn)?0:1});continue}let t=[e.includes(`skin`)?40:e.includes(`shear_web`)?14:e.includes(`spar_cap`)?26:32,5,11,18,25,32,40,48,56,64].map(t=>Wn(e,t)).filter(e=>!!e);if(!t.length)continue;let r=ge.filter(t=>t.cid===e),i=r[0].spec.kind,a=Vn(i===`und`?lm.und:i===`bid`?lm.bid:i===`foam`?lm.foam:15130575),o=[...t].sort((e,t)=>e.bl-t.bl),s=()=>vn?o.find(e=>e.bl>=yn+2)??null:t[0];Bn.add({id:e,text:n.components[e]?.label??e,color:a,at:()=>{let e=s();return e?Gn.copy(e.p).applyMatrix4(ve.matrixWorld):null},vis:()=>{let e=s();return z!==`canard`||!($t.labels??zn)||!e||!r.some(Cn)?0:(Gn.copy(e.p).applyMatrix4(ve.matrixWorld),Kn.copy(e.n).transformDirection(ve.matrixWorld),+(Kn.dot(qn.copy(m.position).sub(Gn))>0))}})}let Zn=new Vy(document.getElementById(`labels`),m,{obstacles:()=>{let e=window.innerWidth,t=window.innerHeight,n=1e5;return[`controls`,`dock`,`opbar`,`viewpop`].map(e=>document.getElementById(e)).filter(e=>!!e&&!e.hidden).map(e=>{let t=e.getBoundingClientRect();return{l:t.left,t:t.top,r:t.right,b:t.bottom}}).filter(e=>e.r>e.l&&e.b>e.t).concat([{l:-1e5,t:-1e5,r:0,b:n},{l:e,t:-1e5,r:n,b:n},{l:-1e5,t:-1e5,r:n,b:0},{l:-1e5,t,r:n,b:n}])}}),Qn=[],$n=()=>z===`fuselage`&&[12,13,14,15,16,17,18,19,20,21,22,23,24,25,26].includes(H(R)),er=(e,t,n)=>(Qn.push({id:e,wants:t,score:n}),()=>t()?$n()?+!!Qn.map((e,t)=>({c:e,i:t})).filter(e=>e.c.wants()).sort((e,t)=>t.c.score()-e.c.score()||e.i-t.i).slice(0,10).some(t=>t.c.id===e):1:0),tr=new W,nr=new Xn;if(F){let e=new Map;for(let t of F.meshes)t.row||e.set(t.part,t);let t=t=>t===`wheels`?F.wheels.visible:!!(e.get(t)&&F.shown(e.get(t).name)&&[`built`,`current`].includes(it.get(e.get(t).name)??``)),r=e=>e.startsWith(`side_`)?.72:e.startsWith(`top_longeron`)?.3:e===`bottom`?.42:.5;for(let[i,a]of e){let e=F.data.parts[i],o=()=>F.shown(a.name)===a.jig,s=()=>An&&o()&&jv(e,jn),c=()=>R?n.ops.find(e=>e.id===R)??null:null,l=()=>{let e=F.shown(a.name);if(!e)return null;nr.setFromObject(e);let t=nr.min.x+(nr.max.x-nr.min.x)*r(i);return An&&o()&&(t=Math.max(t,Wy(jn)+.5*zx)),tr.set(t,nr.max.y+.02,(nr.min.z+nr.max.z)/2)},u=er(a.name,()=>{if(z!==`fuselage`||!($t.labels??zn))return!1;let n=it.get(a.name);if(n!==`built`&&n!==`current`||!F.shown(a.name)||/^spar_lwa_lwa[2-5]$/.test(i)&&t(`spar_lwa_lwa1`)||An&&o()&&Av(e,jn))return!1;let r=c();return r?a.hatch||r.components.includes(a.cid)||s():fv(i,t)||s()},()=>F.isNewOn(a.cid,R)?90:c()?.components.includes(a.cid)?80:s()?70:i.startsWith(`nose_`)||i.startsWith(`gear_`)?i===`nose_pivot_blocks`||i===`nose_ng_hardware`?5:20:10);Zn.add({id:a.name,text:e.label,color:F.labelColor(a),cls:a.hatch?`fitted`:``,at:l,vis:u,priority:()=>Mv({inOp:!!c()?.components.includes(a.cid),cut:s(),fitted:a.hatch}),tie:()=>e.fs_max-e.fs_min})}}if(F){let e=new Set;for(let t of F.meshes)t.row||e.add(t.part);let t=new Map;for(let n of F.meshes)n.row&&!e.has(n.part)&&t.set(n.part,[...t.get(n.part)??[],n]);for(let[e,r]of t){let t=F.data.parts[e],i=()=>r.filter(e=>F.shown(e.name)&&[`built`,`current`].includes(it.get(e.name)??``)),a=()=>R?n.ops.find(e=>e.id===R)??null:null;Zn.add({id:e,text:t.label,color:Vn(Qp),cls:`fitted`,at:()=>{nr.makeEmpty();for(let e of i())nr.union(new Xn().setFromObject(F.shown(e.name)));if(nr.isEmpty())return null;let t=e.endsWith(`bottom`)?.78:.22;return tr.set((nr.min.x+nr.max.x)/2,e.endsWith(`bottom`)?nr.min.y-.02:nr.max.y+.02,nr.min.z+(nr.max.z-nr.min.z)*t)},vis:er(e,()=>z===`fuselage`&&!!($t.labels??zn)&&!!a()&&i().length>0&&!An,()=>F.isNewOn(t.component,R)?90:a()?.components.includes(t.component)?80:10),priority:()=>Mv({inOp:!!a()?.components.includes(t.component),cut:!1,fitted:!0}),tie:()=>t.fs_max-t.fs_min})}}if(F&&Mt)for(let e of Mt.checks)Zn.add({id:`canopy.check.${e.id}`,text:`Check ${e.id}: ${e.min?`at least `:``}${e.height_in} in above WL ${e.wl0}`,color:`#2fc4ff`,cls:``,at:()=>F.checkAnchor(e.id,tr),vis:()=>z===`fuselage`&&($t.labels??zn)&&F.checks.visible?1:0,priority:()=>4,tie:()=>0});if(F&&K){for(let e of[`a`,`b`,`c`])Zn.add({id:`winglet.abc.${e}`,text:F.abcText(e),color:`#2fc4ff`,cls:``,at:()=>F.abcAnchor(e,tr),vis:()=>z===`fuselage`&&($t.labels??zn)&&F.abc.visible?1:0,priority:()=>4,tie:()=>0});Zn.add({id:`winglet.abc.wprp`,text:`Reference point: BL ${K.winglet.wprp[1]}, FS ${K.winglet.wprp[0]}`,color:`#2fc4ff`,cls:``,at:()=>F.abcAnchor(`wprp`,tr),vis:()=>z===`fuselage`&&($t.labels??zn)&&F.abc.visible?1:0,priority:()=>4,tie:()=>0})}if(F&&Nt&&Zn.add({id:`strake.jig_table`,text:`Strake jig table (fitted shape)`,color:Vn(Qp),cls:`fitted`,at:()=>F.strakeTableAnchor(tr),vis:er(`strake.jig_table`,()=>z===`fuselage`&&!!($t.labels??zn)&&F.strakeTable.visible,()=>85),priority:()=>Mv({inOp:!1,cut:!1,fitted:!0}),tie:()=>0}),F&&Ot&&Zn.add({id:`controls.pitch_stops`,text:Ot.stop_label,color:Vn(Qp),cls:`fitted`,at:()=>F.stopsAnchor(tr),vis:er(`controls.pitch_stops`,()=>z===`fuselage`&&!!($t.labels??zn)&&F.stops.visible,()=>60),priority:()=>Mv({inOp:!1,cut:!1,fitted:!0}),tie:()=>0}),F&&Zn.add({id:`gear.wheels`,text:`Main gear and wheels (fitted shape)`,color:`#`+Qp.toString(16).padStart(6,`0`),cls:`fitted`,at:()=>F.wheelAnchor(tr)?.add(new W(0,.02,0))??null,vis:er(`gear.wheels`,()=>z===`fuselage`&&!!($t.labels??zn)&&F.wheels.visible,()=>10),priority:()=>Mv({inOp:!1,cut:!1,fitted:!0}),tie:()=>0}),F&&je){let e=[`installed:elevator.right`,`installed:elevator.left`].map(e=>F.installedMeshes().find(t=>t.name===e)).filter(e=>!!e),t=new W;Zn.add({id:`elevator.installed`,text:je.installed_label,color:Vn(Qp),cls:`fitted`,at:()=>{if(!e.length||!F.installed.visible)return null;let n=null;for(let r of[.5,.25,.75,.08])for(let i of e)if(nr.setFromObject(i),tr.set((nr.min.x+nr.max.x)/2,nr.max.y+.02,nr.min.z+(nr.max.z-nr.min.z)*r),n??=tr.clone(),t.copy(tr).project(m),Math.abs(t.x)<.55&&t.y>-.6&&t.y<.75)return tr;return n?tr.copy(n):null},vis:er(`elevator.installed`,()=>z===`fuselage`&&!!($t.labels??zn)&&F.installed.visible,()=>R===`r30.elev-fuselage-clearance`?80:H(R)===12?75:15),priority:()=>Mv({inOp:H(R)===12&&R===`r30.elev-fuselage-clearance`,cut:!1,fitted:!0}),tie:()=>0})}if(F&&Tt){let e=Tt.candidates,t=(e,t,n)=>Zn.add({id:e,text:t,color:Vn(Qp),cls:`fitted`,at:()=>F.noseWheelAnchor(n,tr),vis:er(e,()=>z===`fuselage`&&!!($t.labels??zn)&&F.nosePresent&&F.noseProgress<1,()=>100),priority:()=>4,tie:()=>0});t(`mark.nose-plans`,`Nose wheel, plans candidate F.S. ${e.plans.axle_fs}: conflict (fitted shape)`,`plans`),t(`mark.nose-manual`,`Ghost: manual candidate about F.S. ${e.manual.axle_fs}: conflict (fitted shape)`,`manual`)}if(F?.markAt&&F.data.gear_marks){let e=F.data.gear_marks,t=(e,t,n)=>Zn.add({id:e,text:t,color:`#2fc4ff`,cls:`mark`,at:()=>tr.copy(n).applyMatrix4(F.jigFrame.matrixWorld),vis:()=>z===`fuselage`&&($t.labels??zn)&&F.marksShown?1:0,priority:()=>4,tie:()=>0});t(`mark.dim`,Gx.dim(e.axle_fwd_of_board_in),F.markAt.dim),t(`mark.axle`,Gx.axle(e.axle_fs),F.markAt.axle)}if(Me&&je?.cove){let e=new W;Bn.add({id:`elevator.cove`,text:je.cove.label,color:Vn(Qp),cls:`fitted`,at:()=>e.set(Me.xCut,.9,-Me.blEnd*.62).applyMatrix4(ve.matrixWorld),vis:()=>z===`canard`&&($t.labels??zn)&&I?1:0})}je&&L.children.length&&Bn.add({id:`elevator.jigs`,text:je.jig_label,color:Vn(Qp),cls:`fitted`,at:()=>Yn.copy(Ie[0]).applyMatrix4(L.matrixWorld).add(new W(0,.04,0)),vis:()=>z===`canard`&&($t.labels??zn)&&L.visible?1:0}),T=e=>{m.updateMatrixWorld(),Bn.update(window.innerWidth,window.innerHeight,e),Zn.update(window.innerWidth,window.innerHeight,e)};let rr=e=>{zn=e;try{Ke?.setItem(Rn,e?`1`:`0`)}catch{}Y.setLabels(e)};ze(Je);let ir=()=>z===`canard`?`home`:R===null&&F?.pose===`on-gear`?`ffinal`:`fhome`,ar=(e,t=!0)=>{R=e,Ye[z]=e,vt=0,kt=null,Y.setSelected(e),F&&z===`fuselage`&&(F.setPose(F.poseFor(e),t),cr(),F.setNose(Et()),lr()),un(),t||Kt(),Pt=null,Rt=null,zt=null,F&&z===`fuselage`&&Ot&&(F.setSparSlide(At()),F.setStick(U()),Jt()),F&&z===`fuselage`&&Mt&&(F.setCanopyLift(Ft()),F.setCanopyOpen(It()),Jt()),F&&z===`fuselage`&&K&&(F.setAileron(Bt()),F.setRudder(Vt()),Jt()),z===`canard`&&De(Vm(n,Je,e),t),mn(e&&g.shots[e]?e:ir(),t)},or=()=>z===`canard`?Rm(n,Je):z_(n,Je),sr={pos:f.position.clone(),target:f.target.position.clone(),angle:f.angle,penumbra:f.penumbra,intensity:f.intensity},cr=()=>{z===`canard`||!F?(f.position.copy(sr.pos),f.target.position.copy(sr.target),f.angle=sr.angle,f.penumbra=sr.penumbra,f.intensity=sr.intensity):F.pose===`on-gear`?(f.position.set(Hy.jig.x+.2,Em.h-.35,(Hy.jig.z+Hy.floor.z)/2+.5),f.target.position.set(Hy.jig.x,.6,(Hy.jig.z+Hy.floor.z)/2+.35),f.angle=.92,f.penumbra=.75,f.intensity=sr.intensity*sv(F.pose)):(f.position.set(Hy.table.x+.2,Em.h-.35,(Hy.table.z+Hy.jig.z)/2+.55),f.target.position.set(Hy.table.x,1,(Hy.table.z+Hy.jig.z)/2),f.angle=.92,f.penumbra=.75,f.intensity=sr.intensity*sv(F.pose)),f.target.updateMatrixWorld(),_.shadowDirty=!0},lr=()=>{let e=Dv(H(R));(e.min!==On||e.max!==kn)&&(On=e.min,kn=e.max,jn=Math.max(On,Math.min(jn,kn)),An&&F?.setStation(!0,jn,0),Y.scaleSection(ur(),An,jn))},ur=()=>z===`canard`?{min:0,max:_n,fmt:sh,label:`Section station in buttock line inches`}:{min:On,max:kn,fmt:Ov,label:`Section station in fuselage station inches`},dr=(e,t=!0,n=!0)=>{if(!F&&e===`fuselage`||e===z)return;if(z=e,n)try{Ke?.setItem(N_,e)}catch{}_e.visible=e===`canard`,Y.setSubject(e),(gn||F)&&Y.scaleSection(ur(),e===`canard`?vn:An,e===`canard`?yn:jn),cr(),Xe=!0;let r=or();Y.setOps(r);let i=Ye[e];ar(i!==void 0&&(i===null||r.some(e=>e.id===i))?i:r[0]?.id??null,t),on()},fr=null,pr=()=>{fr!==null&&(fr=null,F?.setInstalledLift(0),_.shadowDirty=!0)},mr=e=>{if(!F||z!==`fuselage`)return;ln(),ar(e??null,!1),fr=-Bv,F.setInstalledLift(24),mn(`flowerA`,!1);let t=document.getElementById(`step-title`),n=document.getElementById(`step-summary`);t&&(t.textContent=Vv),n&&(n.textContent=`The canard, with its elevators, comes down onto F22 at the chapter 7 cutout.`),_.shadowDirty=!0};k=e=>{if(fr===null||!F)return;fr+=e,F.setInstalledLift(Uv(fr));let t=g.landing(`flowerA`),n=g.landing(`flowerB`),r=Wv(fr);fr>0&&(g.flying=!1,m.position.lerpVectors(t.pos,n.pos,r),h.target.lerpVectors(t.target,n.target,r),b=`flowerB`),_.shadowDirty=!0,fr>=7&&(fr=null)};let hr=null,gr=new qv({act(e,t,n){e===`reset`?(pr(),ln(),ar(null,!Hx),$t.labels=!0,$t.paths=!0,on(),(z===`canard`?vn:An)&&J(!1,z===`canard`?yn:jn)):e===`finish`?(ln(),ar(n??null,!0)):e===`cutclose`?mn(z===`canard`?`cutclose`:t!==void 0&&g.shots[`fcut${t}`]?`fcut${t}`:`fcut`,!0):e===`closeup`?mn(z===`canard`?`cutclose`:H(R)===12&&g.shots.fwide12?`fwide12`:H(R)===13&&g.shots.fwide13?`fwide13`:Vg.has(H(R))&&R&&g.shots[R]?R:ir(),!0):e===`lower`&&mr(n)},orbit(e,t,n){if(n){let e=m.position.clone().sub(h.target);hr={r:Math.hypot(e.x,e.z),y:e.y,a0:Math.atan2(e.x,e.z)},g.flying=!1}if(!hr)return;let r=hr.a0-t*Math.PI/180*e;m.position.set(h.target.x+hr.r*Math.sin(r),h.target.y+hr.y,h.target.z+hr.r*Math.cos(r)),h.update()}}),_r=null,vr=()=>{if(pr(),rt=1,$t.labels=$t.paths=null,_r){let e=_r;_r=null,J(e.secOn,e.secBl)}on(),Y.setTouring(!1)},yr=()=>{gr.active&&(gr.stop(),ln(),vr())};gr.onEnd=vr;let br=e=>{ln(),_r={secOn:An,secBl:jn},gr.load(gy(n,Je)),gr.start(x),rt=Jv,Y.setTouring(!0)},xr=e=>{if(z===`fuselage`&&F){ln(),_r={secOn:An,secBl:jn},gr.load(fy(n,Je,e=>F.opCount(e),e?[e]:dy(n,Je,R))),gr.start(x),rt=Jv,Y.setTouring(!0);return}let t=e??ty(n,Je,R);t!==void 0&&(ln(),_r={secOn:vn,secBl:yn},gr.load(ny(n,Je,t)),gr.start(x),rt=Jv,Y.setTouring(!0))},Sr=()=>{gr.active&&!gr.busy&&yr()};O=e=>gr.update(e),h.addEventListener(`start`,Sr),document.addEventListener(`keydown`,e=>{e.key===`Escape`&&yr()});let Y=lh({onVariant(e){if(e===Je||(Sr(),Je=e,ze(e),Y.setVariant(e),z!==`canard`))return;let t=Rm(n,e);Y.setOps(t),ar(t.some(e=>e.id===R)?R:t[0]?.id??null)},onSubject(e){e!==z&&(Sr(),dr(e))},onAileron(e){Sr(),Rt=e,F&&K&&(F.setAileron(Bt()),_.shadowDirty=!0),Gt()},onRudder(e){Sr(),zt=e,F&&K&&(F.setRudder(Vt()),_.shadowDirty=!0),Gt()},onCanopy(e){Sr(),Pt=e,F&&Mt&&(F.setCanopyOpen(It()),_.shadowDirty=!0),Gt()},onStick(e){Sr(),kt=e,F&&Ot&&(F.setStick(U()),_.shadowDirty=!0),Gt()},onHome:()=>mn(ir(),!0),onTour:()=>gr.active?yr():xr(),onSelect:e=>{Sr(),ar(e)},onGhost:e=>{Sr(),pn(e)},onScrub:e=>{Sr(),dn(e)},onPlay:()=>{Sr(),fn()},onSection:(e,t)=>{Sr(),J(e,t)},onLabels:e=>{Sr(),rr(e)},onPaths:e=>{Sr(),sn(e)},onQuality:e=>{e===`auto`?P(!0):$.setTier(e)}},qe);Y.setGhost(Qe),ce=()=>Y.setQuality(o,l),ce(),Y.setLabels(zn),Y.setPaths(Qt),gn&&Y.initSection(_n,yn),Y.setVariant(Je),Y.setSubject(`canard`);let Cr=document.getElementById(`subject`);Cr&&(Cr.hidden=!F);let wr=Bx.get(`op`),Tr=null;try{Tr=Ke?.getItem(`longez.subject`)??null}catch{Tr=null}let Er=n.ops.find(e=>e.id===wr);if((F?Er?F_.has(Er.chapter)?`fuselage`:`canard`:P_(Tr):`canard`)===`fuselage`)Ye.fuselage=z_(n,Je).find(e=>e.id===wr)?.id,dr(`fuselage`,!1,!1);else{let e=Rm(n,Je);Y.setOps(e),ar(e.find(e=>e.id===wr)?.id??e[0]?.id??null,!1)}F&&($.meshNames=()=>[...ge.map(e=>e.node??e.cid),...F.meshes.map(e=>e.name)]),$.subject=()=>z,$.setSubject=e=>dr(e),$.placement=()=>{let e={};for(let t of F?.meshes??[])t.row||(e[t.part]=t.jig.visible?`jig`:t.table.visible?`table`:`none`);for(let t of F?.meshes??[])t.row&&!(t.part in e)&&e[t.part]===void 0&&(e[t.part]=`none`);for(let t of F?.meshes??[])if(t.row&&t.m25){let n=t.jig.visible?`jig`:t.table.visible?`table`:null;n&&(e[t.part]=n)}return e},$.jigPose=()=>F?.pose??`upright`,$.fuseShots=()=>Object.fromEntries([...He].map(e=>[e,Ge(e)])),$.cg=()=>Iv(N),$.ground=()=>Rv(N),$.ref=()=>zv(N,R,n.order)??Xh(N,R,n.order)??zg(N,R,n.order)??Ab(N,Nt,R,n.order)??vx(G,R,n.order),$.fuseToWorld=e=>F?new W(e[0],e[1],e[2]).applyMatrix4(F.jigFrame.matrixWorld).toArray():e,$.fuseRestToWorld=(e,t)=>F?new W(e[0],e[1],e[2]).applyMatrix4(F.restMatrix(t)).toArray():e,$.gearMarks=()=>{let e=F?.data.gear_marks;if(!F||!e||!F.markAt)return null;let t=e=>e.clone().applyMatrix4(F.jigFrame.matrixWorld).toArray();return{shown:F.marksShown,axleFs:e.axle_fs,boardFs:e.board_fs,dimText:Gx.dim(e.axle_fwd_of_board_in),axleText:Gx.axle(e.axle_fs),dimModel:F.markAt.dim.toArray(),axleModel:F.markAt.axle.toArray(),dimWorld:t(F.markAt.dim),axleWorld:t(F.markAt.axle)}},$.fuseTurning=()=>!!F?.turning,$.fuseFloor=()=>{if(!F)return null;F.group.updateMatrixWorld(!0);let e=e=>[e.min.toArray(),e.max.toArray()],t={};for(let n of F.meshes)(n.cid.startsWith(`gear.`)||n.cid===`fuselage.gear_extrusions`)&&!n.ply&&n.jig.visible&&(t[n.name]=e(new Xn().setFromObject(n.jig,!0)));return F.wheels.visible&&(t[`gear.wheels`]=e(new Xn().setFromObject(F.wheels,!0))),{bench:e(F.benchBox()),gear:t,noseStand:F.noseStand.visible}},$.stick=()=>F&&Ot?{deflUp:F.stickDeflUp,manual:kt!==null,text:M_(F.stickDeflUp,Ot),shown:!document.getElementById(`stick`).hidden}:null,$.setStick=e=>{kt=e,F&&Ot&&(F.setStick(U()),_.shadowDirty=!0),Gt()},$.canopy=()=>F&&Mt?{openDeg:F.canopyOpenDeg,manual:Pt!==null,text:Hh(F.canopyOpenDeg,Mt.hinge),shown:!document.getElementById(`canopy-ctl`).hidden,liftK:F.canopyLiftK,checks:F.checks.visible}:null,$.setCanopyOpen=e=>{Pt=e,F&&Mt&&(F.setCanopyOpen(It()),_.shadowDirty=!0),Gt()},$.wing=()=>F&&K?{aileronDeg:F.aileronUpDeg,rudderDeg:F.rudderOutDeg,aileronManual:Rt!==null,rudderManual:zt!==null,aileronText:Og(F.aileronUpDeg,K.aileron.max_up_deg),rudderText:Ag(F.rudderOutDeg,K.rudder.max_deg),aileronShown:!document.getElementById(`aileron-ctl`).hidden,rudderShown:!document.getElementById(`rudder-ctl`).hidden,abc:F.abc.visible}:null,$.setAileron=e=>{Rt=e,F&&K&&(F.setAileron(Bt()),_.shadowDirty=!0),Gt()},$.setRudder=e=>{zt=e,F&&K&&(F.setRudder(Vt()),_.shadowDirty=!0),Gt()},$.room=()=>{ie();let e=m.position.toArray(),t=h.target.toArray();return{hidden:[...re].sort(),blocks:M?wm(e,t,M.planes,re):[],apron:!!u.getObjectByName(`shop.apron`)?.visible}},$.zoomTo=e=>{let t=m.position.clone().sub(h.target);m.position.copy(h.target).addScaledVector(t.normalize(),Math.min(Math.max(e,h.minDistance),h.maxDistance)),h.update(),g.lastUser=performance.now()},$.opIds=()=>or().map(e=>e.id),$.hide=e=>{lt.splice(0,lt.length,...e),Xe=!0,cn()},$.sparSlide=()=>F?{inches:F.sparSlideInches,distance:F.slideDistance()}:null,$.strakeTable=()=>!!F&&F.strakeTable.visible,$.finish=()=>F?Object.fromEntries(F.finished):{},$.touring=()=>gr.active,$.tourIndex=()=>gr.seg,$.selected=()=>R,$.select=e=>ar(e),$.camera=()=>({pos:m.position.toArray(),target:h.target.toArray(),fov:m.fov}),$.shot=Ge,$.flying=()=>g.flying,$.pose=()=>Se,$.flipping=()=>Te<1,$.labShots=()=>Re,$.material=e=>{if(e===`gear.wheels`&&F){let e=F.wheels.children.map(e=>e.material);return{kind:`part`,angles:[],wet:0,hatch:e.length>0&&e.every(e=>!!e.userData.hatch),fidelity:`representational`}}let t=ge.find(t=>(t.node??t.cid)===e);if(!t){let t=F?.meshes.find(t=>t.name===e);if(!t)return null;let n=t.jig.visible||!t.table.visible?t.jigMat:t.tableMat,r=n.userData.comp;return{kind:t.spec.kind,angles:t.spec.angles.slice(),wet:r?.wet??0,hatch:!!n.userData.hatch,fidelity:t.fidelity,opacity:n.opacity,transparent:n.transparent,color:n.color?.getHex?.()??null}}let n=t.mesh.material.userData.comp,r=t.cid.startsWith(`elevator.`)?{hatch:!!t.mesh.material.userData.hatch,fidelity:`representational`}:{};return{kind:t.spec.kind,angles:t.spec.angles.slice(),wet:n?.wet??0,...r}},$.setWet=(e,t)=>{let n=ge.find(t=>(t.node??t.cid)===e);n&&hm(n.mesh.material,t);let r=F?.meshes.find(t=>t.name===e);r&&(hm(r.jigMat,t),hm(r.tableMat,t))},$.meshBox=e=>{let t=ge.find(t=>(t.node??t.cid)===e),n=t?t.mesh:F?.shown(e)??null;if(!n)return null;let r=new Xn().setFromObject(n);return[r.min.toArray(),r.max.toArray()]},$.state=()=>Object.fromEntries([...it].filter(([e])=>z===`canard`?e.startsWith(`canard.`):d.has(e))),$.stateAll=()=>Object.fromEntries(it),$.kin=()=>Dt(),$.cove=()=>Me?{xCut:Me.xCut,blEnd:Me.blEnd,blIn:Me.blIn,open:I,installed:!!F&&F.cut.coveOn}:null,$.elevators=()=>{if(!je)return null;let e={};for(let t of Ne)if(t.mesh.visible){let n=new Xn().setFromObject(t.mesh);e[t.node]=[n.min.toArray(),n.max.toArray()]}return{mode:mt(),degDown:bt,slide:yt,hangPitch:gt,noseDown:_t,jigs:L.visible,installed:!!F?.installed.visible,boxes:e}},$.noseGear=()=>{if(!F||!Tt)return null;let e={};for(let t of[`plans`,`manual`]){let n=F.noseWheelAt(t);n&&(e[t]=n)}return{t:F.noseProgress,crank:S_(F.noseProgress,Tt.crank_turns),shown:F.nosePresent,wheel:e,ghostShown:F.ghost.visible,stand:F.noseStand.visible}},$.installedCanard=()=>{if(!F)return null;F.group.updateMatrixWorld(!0);let e={};for(let t of F.installedMeshes()){let n=new Xn().setFromObject(t);e[t.name]=[n.min.toArray(),n.max.toArray()]}return{shown:F.installed.visible,at:F.installed.position.toArray(),nodes:F.installedMeshes().length,boxes:e}},$.phase=e=>ot.get(e)??F?.phases.get(e)??null,$.lay=()=>V,$.setLay=dn,$.play=()=>(fn(),nt),$.playing=()=>nt,$.ghost=pn,$.setSection=J,$.cutGlow=()=>oe.uGlow.value,$.toWorld=e=>new W(e[0],e[1],e[2]).applyMatrix4(ve.matrixWorld).toArray(),$.setCamera=(e,t)=>{m.position.set(e[0],e[1],e[2]),h.target.set(t[0],t[1],t[2]),h.update(),g.lastUser=performance.now()},$.labels=()=>z===`canard`?Bn.stats().filter(e=>e.id.startsWith(`canard.`)):Zn.stats(),$.labelsAll=()=>z===`canard`?Bn.stats():Zn.stats(),$.paths=()=>(tn.updateWorldMatrix(!0,!0),an.map(e=>{let t=e.p.segments.flat().map(e=>new W(e[0],e[1],e[2]).applyMatrix4(tn.matrixWorld)),n=rn[e.p.kind]?.uniforms.uColor.value,r=n?n.getRGB({r:0,g:0,b:0},Ue):{r:0,g:0,b:0};return{id:e.p.id,kind:e.p.kind,visible:e.visible,drawn:e.visible&&en(),color:[r.r,r.g,r.b],worldPoints:t.map(e=>e.toArray()),clipped:vn&&t.some(e=>oe.world.distanceToPoint(e)<0)}})),$.project=t=>{m.updateMatrixWorld();let n=new W(t[0],t[1],t[2]).project(m),r=e.getBoundingClientRect();return[(n.x*.5+.5)*r.width+r.left,(-n.y*.5+.5)*r.height+r.top]},$.plyBox=e=>{let t=ge.filter(t=>xn(t)===e||t.cid===e),n=F?.meshes.find(t=>t.name===e);if(!t.length&&n){let e=n.jig.geometry.boundingBox;return{min:e.min.toArray(),max:e.max.toArray()}}if(!t.length)return null;let r=new Xn;for(let e of t)r.union(e.mesh.geometry.boundingBox);return{min:r.min.toArray(),max:r.max.toArray()}},$.cut=()=>{if(z===`fuselage`&&F){let e=Fn(),t=e=>F.cut.world.distanceToPoint(new W(e,0,0).applyMatrix4(F.jigFrame.matrixWorld))>=0,n=e.filter(e=>Array.isArray(e.jig.material)&&e.jigMat.userData.back?.userData.u.uGhost.value===0).map(e=>e.name);return{enabled:An,bl:jn,fs:jn,planeConstant:An?F.cut.local.constant:null,keepsOutboard:!1,removesInboard:!1,keepsAft:An&&t(jn+5),removesForward:An&&!t(jn-5),cappedNodes:e.map(e=>e.name),capsVisible:n.length,capNodesVisible:n,clipped:An?F.meshes.filter(e=>e.jig.visible&&e.jig.geometry.boundingBox.min.x<jn).length:0}}let e=e=>oe.world.distanceToPoint(new W(0,0,e).applyMatrix4(ve.matrixWorld))>=0,t=ge.filter(e=>Tn(e)&&Array.isArray(e.mesh.material)&&e.mat.userData.back?.userData.u.uGhost.value===0).map(xn);return{enabled:vn,bl:yn,planeConstant:vn?oe.local.constant:null,keepsOutboard:vn&&e(-yn-5),removesInboard:vn&&!e(-yn+5),cappedNodes:ge.filter(Tn).map(xn),capsVisible:t.length,capNodesVisible:t,clipped:vn?ge.filter(e=>e.mesh.visible&&e.mesh.geometry.boundingBox.min.z<-yn+hn).length:0}};for(let e of(Bx.get(`wet`)??``).split(`,`).filter(Boolean))$.setWet(e,1);let Dr=(Bx.get(`cam`)??``).split(`,`).map(Number);Dr.length===6&&Dr.every(Number.isFinite)&&(m.position.set(Dr[0],Dr[1],Dr[2]),h.target.set(Dr[3],Dr[4],Dr[5]),h.update(),g.lastUser=performance.now()),Wx(null),$.ready=!0,Hx&&(window.__rec={start(e){let t=/^fuselage(6|8|9|14)$/.exec(e);if(e!==`canard`&&e!==`canard12`&&!t)throw Error(`no film called ${e}`);return e===`canard12`?(dr(`fuselage`,!1,!1),br(`canard12`)):t?(dr(`fuselage`,!1,!1),xr(Number(t[1]))):xr(30),gr.duration},frame(e,t=!0){return A(e),t&&ae(),{t:x,active:gr.active}}})}catch(e){console.error(e),Wx(`Could not load the canard model (${e.message}). The rest of the guide still works at the site root.`,!0)}}Xx().catch(e=>{console.error(e),Wx(`The lab failed to start: ${e.message}`,!0)});