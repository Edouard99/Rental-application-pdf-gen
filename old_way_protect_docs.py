from pdf2image import convert_from_path
import numpy as np
import cv2 as cv
from PIL import Image
import argparse
from pathlib import Path
import glob
import os

POPPLER_PATH=r"C:\Users\ecastets\Desktop\Recherche Appart\script\poppler-23.05.0\Library\bin"

def rotate_text(src, angle):
    size = (src.shape[0], src.shape[1])
    org= (size[0]//2, size[1]//2)
    rotation = cv.getRotationMatrix2D(org,angle,1.0)
    dst=cv.warpAffine(src,rotation,size[::-1])
    return dst

def smart_add(image,overlay):
    new_image=np.zeros_like(image)
    condition=np.expand_dims(np.mean(overlay,axis=2)!=0,2)
    condition=np.concatenate([condition,condition,condition],axis=2)
    new_image=np.where(condition,0.4*overlay+0.6*image,image)
    return new_image

def protect_pdf(path,text,save_dir):
    protected_images=[]
    extension=path.parts[-1].split(".")[-1]
    pdf_name=path.parts[-1].split(".")[0]
    if extension=="jpg" or extension=="png":
        images=[cv.cvtColor(cv.imread(str(path)),cv.COLOR_BGR2RGB)]
    elif extension=="pdf":
        images= convert_from_path(str(path),poppler_path = POPPLER_PATH)
    else:
        return -1
    for k,image in enumerate(images):
        image=np.array(image).astype(np.uint8)
        overlay=np.zeros((3*image.shape[0],3*image.shape[1],3)).astype(np.uint8)
        overlay=cv.putText(overlay,text,(0,8*image.shape[0]//4),cv.FONT_HERSHEY_SIMPLEX,2.0,(200,0,0),3)
        overlay=cv.putText(overlay,text,(0,7*image.shape[0]//4),cv.FONT_HERSHEY_SIMPLEX,2.0,(200,0,0),3)
        overlay=cv.putText(overlay,text,(0,3*image.shape[0]//2),cv.FONT_HERSHEY_SIMPLEX,2.0,(200,0,0),3)
        overlay=cv.putText(overlay,text,(0,5*image.shape[0]//4),cv.FONT_HERSHEY_SIMPLEX,2.0,(200,0,0),3)
        overlay=rotate_text(overlay,-45)
        overlay=overlay[image.shape[0]:2*image.shape[0],image.shape[1]:2*image.shape[1],:]
        image=smart_add(image,overlay)
        protected_images.append(Image.fromarray(image.astype(np.uint8)))
    protected_images[0].save(f'{str(save_dir / pdf_name)}_f.pdf', save_all=True, append_images=protected_images[1:])

if __name__=="__main__":
    text="Documents reserves a la location d'appartement"
    text_overlay=""
    for i in range(1000):
        text_overlay+=f"{text}   "
    parser=argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--source",
        type=Path,
        required=True
    )
    args=parser.parse_args()
    save_dir=args.source / "protected_files"
    os.makedirs(save_dir,exist_ok=True)
    for folder in os.listdir(args.source):
        if folder!="protected_files":
            name_template=str(args.source / folder / "*")
            file_in_folder=glob.glob(name_template)
            for file in file_in_folder:
                protect_pdf(Path(file),text_overlay,save_dir)
            

    # protect_pdf("Société-SARL-FRENCH-INDIES-REALTY.pdf",text_overlay)
 
# # Store Pdf with convert_from_path function
# images = convert_from_path('Société-SARL-FRENCH-INDIES-REALTY.pdf',poppler_path = POPPLER_PATH)
# for k,image in enumerate(images):
#     image=np.array(image).astype(np.uint8)

#     imagecv=cv.cvtColor(image,cv.COLOR_RGB2BGR)
#     cv.imwrite(f"{k}_image.png",imagecv)

# im = Image.fromarray(np.uint8(cm.gist_earth(myarray)*255))
# # storing image path
# img_path = "C:/Users/Admin/Desktop/GfG_images/do_nawab.png"
 
# # storing pdf path
# pdf_path = "C:/Users/Admin/Desktop/GfG_images/file.pdf"
 
# # opening image
# image = Image.open(img_path)
 
# # converting into chunks using img2pdf
# pdf_bytes = img2pdf.convert(image.filename)
 
# # opening or creating pdf file
# file = open(pdf_path, "wb")
 
# # writing pdf files with chunks
# file.write(pdf_bytes)
 
# # closing image file
# image.close()
 
# # closing pdf file
# file.close()
 
# # output
# print("Successfully made pdf file")