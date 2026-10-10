# Convert white-background product renders to RGBA with unmixed edges, crop to content.
import sys, numpy as np
from PIL import Image
def key(src, dst, soft=70):
    im=np.array(Image.open(src).convert('RGB')).astype(np.float32)
    mn=im.min(axis=2)
    a=np.clip((255-mn)/soft,0,1)
    # unmix against white
    fg=np.where(a[...,None]>0.02,(im-(1-a[...,None])*255)/np.maximum(a[...,None],0.02),im)
    fg=np.clip(fg,0,255)
    rgba=np.dstack([fg,a*255]).astype(np.uint8)
    ys,xs=np.where(a>0.03); pad=8
    y0,y1,x0,x1=max(0,ys.min()-pad),min(rgba.shape[0],ys.max()+pad),max(0,xs.min()-pad),min(rgba.shape[1],xs.max()+pad)
    out=Image.fromarray(rgba[y0:y1,x0:x1],'RGBA'); out.save(dst); print(dst,out.size)
for name in sys.argv[1:]:
    key(name, name.replace('_sr.png','_cut.png'))
