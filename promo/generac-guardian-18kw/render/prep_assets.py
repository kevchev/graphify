# Derive animation layers from the plates: a darkened house plate, a warm window-bloom layer, and rain sprites.
import numpy as np, cv2, os, math, random
here=os.path.dirname(os.path.abspath(__file__)); IMG=f"{here}/../assets/img"
lit=cv2.imread(f"{IMG}/bg-lit.jpg").astype(np.float32)/255.0   # BGR
b,g,r=lit[:,:,0],lit[:,:,1],lit[:,:,2]
lum=0.114*b+0.587*g+0.299*r
warm=np.clip((r-b)*3.0,0,1)*np.clip((lum-0.35)/0.3,0,1)        # warm bright = windows, porch, reflections
mask=cv2.GaussianBlur(warm,(0,0),3)
mask=np.clip((mask-0.15)/0.5,0,1)
# dark plate: cool, dim, windows killed
dark=lit*np.array([0.42,0.30,0.22],dtype=np.float32)            # BGR multipliers: cool night
dark=dark*(1-mask[...,None]*0.85)+np.array([0.10,0.07,0.05])*mask[...,None]*0.85
cv2.imwrite(f"{IMG}/house_dark.jpg",np.clip(dark*255,0,255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,94])
# glow layer: blurred warm mask, RGBA, used with screen/plus-lighter blend
glow=cv2.GaussianBlur(mask,(0,0),28)*1.6+cv2.GaussianBlur(mask,(0,0),90)*0.9
glow=np.clip(glow,0,1)
rgba=np.dstack([np.full_like(glow,0.35),np.full_like(glow,0.62),np.full_like(glow,1.0),glow])  # BGRA warm
cv2.imwrite(f"{IMG}/house_glow.png",(rgba*255).astype(np.uint8))
print("mask coverage",round(float(mask.mean()),3))
# rain sprites (tileable vertically): near and far
random.seed(7)
def rain(w,h,n,len_rng,th_rng,alpha,angle_deg,name):
    img=np.zeros((h,w,4),np.uint8); ang=math.radians(angle_deg)
    for _ in range(n):
        x=random.randint(0,w); y=random.randint(0,h); L=random.uniform(*len_rng); t=random.uniform(*th_rng)
        a=int(255*alpha*random.uniform(0.5,1.0))
        x2=x+int(L*math.sin(ang)); y2=y+int(L*math.cos(ang))
        for off in (0,-h,h):   # draw wrapped so the tile loops vertically
            cv2.line(img,(x,y+off),(x2,y2+off),(255,255,255,a),int(round(t)),cv2.LINE_AA)
    img[:,:,3]=cv2.GaussianBlur(img[:,:,3],(0,0),0.6)
    cv2.imwrite(f"{IMG}/{name}",img)
rain(1920,2160,1500,(40,90),(1,2),0.55,-9,"rain_far.png")
rain(1920,2160,500,(110,220),(2,3.2),0.5,-11,"rain_near.png")
print("ok")
