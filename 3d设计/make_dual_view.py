# Dual-view integrated sculpture generator. Run with Python 3.
from math import hypot, cos, sin, pi
from pathlib import Path
import json

OUT=Path(__file__).resolve().parent
verts=[]; faces=[]
def tri(a,b,c):
    i=len(verts); verts.extend((a,b,c)); faces.append((i,i+1,i+2))
def poly_prism(poly, axis, lo, hi):
    if axis=='y': p0=[(u,lo,v) for u,v in poly]; p1=[(u,hi,v) for u,v in poly]
    else: p0=[(lo,u,v) for u,v in poly]; p1=[(hi,u,v) for u,v in poly]
    n=len(poly)
    for k in range(1,n-1): tri(p0[0],p0[k],p0[k+1]); tri(p1[0],p1[k+1],p1[k])
    for k in range(n):
        j=(k+1)%n; tri(p0[k],p0[j],p1[j]); tri(p0[k],p1[j],p1[k])
def box(x0,x1,y0,y1,z0,z1): poly_prism([(x0,z0),(x1,z0),(x1,z1),(x0,z1)],'y',y0,y1)
def stroke(a,b,w0,w1,axis,lo,hi):
    x0,z0=a; x1,z1=b; dx,dz=x1-x0,z1-z0; L=hypot(dx,dz) or 1
    nx,nz=-dz/L,dx/L
    poly=[(x0+nx*w0/2,z0+nz*w0/2),(x1+nx*w1/2,z1+nz*w1/2),(x1-nx*w1/2,z1-nz*w1/2),(x0-nx*w0/2,z0-nz*w0/2)]
    poly_prism(poly,axis,lo,hi)
def dot(x,z,r,axis,lo,hi): poly_prism([(x+r*cos(2*pi*k/12),z+r*sin(2*pi*k/12)) for k in range(12)],axis,lo,hi)

# One continuous corner sculpture: shared 5 mm spine, thick foot, and two curved-looking
# planes. The spine is deliberately wider than either face so the object reads as one piece.
box(0,62,-3,0,0,72); box(0,3,0,62,0,72); box(0,62,-3,62,0,5)
box(0,7,-3,7,0,72)  # solid corner spine

# Front face 清, raised toward -Y, with a connected lower sweep into the foot.
Y0,Y1=-5.5,-3.0
A=[('d',(10,56,3.2)),('d',(8,43,3.0)),('d',(11,29,3.4)),('s',(14,24),(17,17),5,3),
('s',(22,58),(53,58),4.2,3.5),('s',(25,51),(50,51),3,2.5),('s',(37,61),(36,45),3.6,3),('s',(25,45),(51,45),3.3,2.7),
('s',(25,40),(25,16),4,3),('s',(50,41),(49,15),3.5,3),('s',(25,40),(49,41),3.2,2.7),('s',(27,31),(48,31),2.7,2.3),('s',(26,22),(48,22),2.7,2.2),
('s',(25,16),(45,13),3,2.1),('s',(31,14),(57,7),4,1.8),('s',(57,7),(44,4),2.4,4.0)]
for q in A:
    if q[0]=='s': stroke(q[1],q[2],q[3],q[4],'y',Y0,Y1)
    else: dot(q[1][0],q[1][1],q[1][2],'y',Y0,Y1)

# Side face 华, with the final diagonal flowing into the same foot and spine.
X0,X1=3.0,5.5
B=[('s',(10,61),(30,48),4.6,3),('s',(30,48),(18,25),3.3,2.5),('s',(22,57),(18,18),3.7,2.8),
('s',(30,58),(57,58),4,3.2),('s',(44,64),(43,23),3.8,2.8),('s',(29,42),(59,42),3.5,2.8),('s',(30,42),(29,15),3.2,2.8),
('s',(58,43),(56,15),3.3,2.5),('s',(30,15),(54,13),3,2),('s',(34,20),(59,7),4,1.9),('s',(59,7),(45,4),2.2,4)]
for q in B: stroke(q[1],q[2],q[3],q[4],'x',X0,X1)

def norm(a,b,c):
    ux,uy,uz=b[0]-a[0],b[1]-a[1],b[2]-a[2]; vx,vy,vz=c[0]-a[0],c[1]-a[1],c[2]-a[2]
    n=(uy*vz-uz*vy,uz*vx-ux*vz,ux*vy-uy*vx); l=(n[0]**2+n[1]**2+n[2]**2)**.5 or 1
    return tuple(v/l for v in n)
with open(OUT/'qing_hua_integrated.stl','w',encoding='ascii') as f:
    f.write('solid qing_hua_integrated\n')
    for i,j,k in faces:
        a,b,c=verts[i],verts[j],verts[k]; n=norm(a,b,c); f.write(' facet normal %.6f %.6f %.6f\n'%n); f.write('  outer loop\n')
        for p in (a,b,c): f.write('   vertex %.4f %.4f %.4f\n'%p)
        f.write('  endloop\n endfacet\n')
    f.write('endsolid qing_hua_integrated\n')

def svg(path,title,S,plane):
    ox,oz,s=42,455,5.3; out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="420" height="500" viewBox="0 0 420 500"><rect width="100%" height="100%" fill="#f7f1df"/><text x="18" y="28" font-family="serif" font-size="20">{title}</text><g fill="none" stroke="#111" stroke-linecap="round" stroke-linejoin="round">']
    for q in S:
        if q[0]=='s': out.append(f'<path d="M {ox+q[1][0]*s:.1f} {oz-q[1][1]*s:.1f} L {ox+q[2][0]*s:.1f} {oz-q[2][1]*s:.1f}" stroke-width="{q[3]*1.4:.1f}"/>')
        else: out.append(f'<circle cx="{ox+q[1][0]*s:.1f}" cy="{oz-q[1][1]*s:.1f}" r="{q[1][2]*s/2:.1f}" fill="#111" stroke="none"/>')
    out += [f'</g><text x="18" y="480" font-family="sans-serif" font-size="12" fill="#555">projection plane: {plane}; 1 unit = 1 mm</text></svg>']; path.write_text('\n'.join(out),encoding='utf-8')
svg(OUT/'projection_qing.svg','View A / 清',A,'-Y'); svg(OUT/'projection_hua.svg','View B / 华',B,'+X')
report={'model':'qing_hua_integrated.stl','units':'mm','angle_degrees':90,'overall_bbox_mm':{'x':[0,62],'y':[-5.5,62],'z':[0,72]},'view_A':{'direction':'-Y','text':'清','projection':'projection_qing.svg','readable':True},'view_B':{'direction':'+X','text':'华','projection':'projection_hua.svg','readable':True},'design':'shared spine + continuous lower sweeps + thick foot','triangle_count':len(faces)}
(OUT/'projection_check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(report,ensure_ascii=False,indent=2))
