import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd
src=np.asarray(Image.open('/mnt/user-data/uploads/589f1fca-image.png').convert('RGB')).astype(int)
H,W,_=src.shape
mn=src.min(2); mx=src.max(2)
purple=(src[:,:,2]>150)&(src[:,:,1]<80)
white=(mn>170)&~purple
dark=(mx<90)
lab,n=nd.label(white); sizes=nd.sum(white,lab,range(1,n+1))
# fist = big white blobs not touching the image border
keep=np.zeros_like(white)
for i,s in enumerate(sizes,1):
    ys,xs=np.where(lab==i)
    if s>2000 and xs.min()>40 and xs.max()<W-40 and ys.min()>40: keep|=lab==i
white=keep
# close the slit in the forearm (horizontal closing below the palm)
reg=np.zeros_like(white); reg[740:1125,:]=True
closed=nd.binary_closing(white,structure=np.ones((1,61)))
white=white|(closed&reg)
dlab,dn=nd.label(dark); ds=nd.sum(dark,dlab,range(1,dn+1))
dk=np.zeros_like(dark)
for i,s in enumerate(ds,1):
    if s>1500: dk|=dlab==i
dark=dk&~white
def comp(scale,cy_shift=0):
    S=1254; out=Image.new('RGB',(S,S),(0x4f,0x2b,0xd0))
    def paste(mask,col):
        m=Image.fromarray((mask*255).astype('uint8'))
        w=int(S*scale); m=m.resize((w,w),Image.LANCZOS)
        layer=Image.new('RGB',(w,w),col)
        ox=(S-w)//2; oy=(S-w)//2+cy_shift
        out.paste(layer,(ox,oy),m)
    paste(dark,(0x0b,0x0b,0x10)); paste(white,(255,255,255))
    return out
big=comp(0.8,40)
big.save('trace_big.png')
