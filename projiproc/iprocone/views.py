from django.shortcuts import render
import datetime
from django.http import*
from django.core.files.storage import FileSystemStorage
import uuid  
import os
import cv2
import numpy as np
from pathlib import Path

def index(request):
 print(request.session);
 today=datetime.datetime.now()
 return render(request,'index.html',{
 "today":today.strftime("%d-%m=%Y")})

def isFileOpen(request):
 stack=request.session['stack']
 if stack>0 and request.session.get('name')!=None and request.session.get('email')!=None:
  return true
  
 else:
  return false
   
	

def getState(request):
 if(isFileOpen):
  fileName=request.session['stack'][0]
  email=request.session['email']
  name=request.session['name']
  return JsonResponse({'state':'open','name':name,'email':email,'fileName':fileName})
  
 else:
  return JsonResponse({'state':none,'name':'',email:'','fileName':''})	
  
  

def openFile(request):
 if request.method=='POST' and request.FILES['fileName']:
  imageFile=request.FILES['fileName']
  fs=FileSystemStorage()
  imageFileName=fs.save(imageFile.name,imageFile)
  stack=[]
  redostack=[]
 
  imgpath=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','filestore/%s'%imageFileName))
  img=cv2.imread(imgpath)
  (h, w) = img.shape[:2]
  r = 500 / float(h)
  dim = (int(w * r),500)
  
  stdimg=cv2.resize(img,dim,interpolation=cv2.INTER_AREA)
  stdimgPath=str(Path(imgpath).with_suffix(''))+str(uuid.uuid4())[-3:]+'.png' 
  print(stdimgPath)
  cv2.imwrite(stdimgPath,stdimg)
  stdFileName=stdimgPath.split('/')[-1];

  stack.append(stdFileName)
  request.session['stack']=stack
  print(img.shape)
  request.session['size']=()
  request.session['redo']=True
  request.session['oriImg']=imageFileName
  request.session['borderSize']=0;
  request.session['email']=request.POST['email']
  request.session['name']=request.POST.get('name')
  request.session['redostack']=redostack
  	
  return JsonResponse({'fileName':imageFileName})

def getImage(request):
 if request.method=="GET" and request.session.has_key('stack'):
  stack=request.session['stack']
 if len(stack)>0:
  fileToServer=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','filestore/%s'%stack[0]))
   
  return FileResponse(open(fileToServer,'rb'))
 return HttpResponse('')


def showOrignal(request):
 if request.method=="GET" and request.session.has_key('oriImg'):
  stack=request.session['stack']
  for file in stack:
   fileDelete=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','filestore/%s'%file))
   os.remove(fileDelete);
  request.session.pop('stack')
  stack=[]
  stack.insert(0,request.session['oriImg'])
  request.session['stack']=stack
  return JsonResponse({'response':'orignal'})
 else:
  return HttpResponse('')
  
 


def closeFile(request):
 if request.method=="GET" and request.session.has_key('stack'):
  stack=request.session['stack']
  for file in stack:
   fileDelete=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','filestore/%s'%file))
   os.remove(fileDelete);
  request.session.pop('stack')
  request.session.pop('email')
  request.session.pop('name')
  return JsonResponse({'response':'closed'})
 else:
  return HttpResponse('');

def undo(request):
 if request.method=="GET" and request.session.has_key('stack') and len(request.session['stack'])>1:
   stack=request.session['stack']
   fileDelete=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','filestore/%s'%stack.pop(0)))
   os.remove(fileDelete);
   request.session['stack']=stack;
   return JsonResponse({"response":"undid"})
 else:
   return HttpResponse('')

def redo(request):
 if request.method=="GET" and request.session.has_key('redostack') and len(request.session['redostack'])>0:
   redoStack=request.session['redostack']
   request.session['redo']=False;
   value=redoStack.pop()
   if(value=='grayscale'):
    toGrayscale(request)
   if(value=='cool'):
    cool(request)
   if(value=='scaleIt'):
    scaleit(request)
   if(value=='setBorder'):
    setBorder(request); 
   request.session['redostack']=redoStack;
 return JsonResponse({'response':'redo'})


def toGrayscale(request):
 if request.method=="GET" and request.session.has_key('stack'):
  stack=request.session['stack']
  redostack=request.session['redostack']
 if len(stack)>0:
  fileAbsPath=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','filestore/%s'%stack[0]));
  grayscalefilepath=str(Path(fileAbsPath).with_suffix(''))+str(uuid.uuid4())+'.png' #here dirty coding......
  grayImage=cv2.imread(fileAbsPath)
  grayImage=cv2.cvtColor(grayImage,cv2.COLOR_BGR2GRAY)
  cv2.imwrite(grayscalefilepath,grayImage)
  gfilename=grayscalefilepath.split('/')[-1];
  stack.insert(0,gfilename)
  if request.session['redo']:
   redostack.insert(0,'grayscale')
  request.session['redo']=True
  request.session['stack']=stack
  request.session['redostack']=redostack
  return JsonResponse({'response':'convertedToGrayscale'}) 
 else:
  return HttpResponse()

def scaleit(request):
 if request.method=="POST" and request.session.has_key('stack'):
  newX=int(request.POST['newX'])
  newY=int(request.POST['newY'])
  
  request.session['size']=(newX,newY)
  stack=request.session['stack']
  redostack=request.session['redostack']
 
  fileAbsPath=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','filestore/%s'%stack[0]));
  scalefilepath=str(Path(fileAbsPath).with_suffix(''))+str(uuid.uuid4())+'.png' #here dirty coding...
  
  oriimg=cv2.imread(fileAbsPath)
  newimg=cv2.resize(oriimg,(newX,newY),interpolation=cv2.INTER_AREA)
  request.session['size']=newimg.shape;
  cv2.imwrite(scalefilepath,newimg);
  
  scalefilename=scalefilepath.split('/')[-1]
  stack.insert(0,scalefilename)
  redostack.insert(0,'scaleIt')
  request.session['redostack']=redostack
  request.session['stack']=stack;
  return JsonResponse({'response':'scaled'})
 if request.method=="GET" and request.session.has_key('size'):
  newX=request.session['size'][0]
  newY=request.session['size'][1]
  
  
  stack=request.session['stack']
  redostack=request.session['redostack']
 
  fileAbsPath=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','filestore/%s'%stack[0]));
  scalefilepath=str(Path(fileAbsPath).with_suffix(''))+str(uuid.uuid4())+'.png' #here dirty coding...
  
  oriimg=cv2.imread(fileAbsPath)
  newimg=cv2.resize(oriimg,(int(newX),int(newY)))
  request.session['size']=newimg.shape;
  cv2.imwrite(scalefilepath,newimg);
  
  scalefilename=scalefilepath.split('/')[-1]
  stack.insert(0,scalefilename)
  redostack.insert(0,'scaleit')
  request.session['redostack']=redostack
  request.session['stack']=stack;
  return JsonResponse({'response':'scaled'})
 else:
  return HttpResponse('')
 

def cropIt(request):
 if request.method=="POST" and request.session.has_key('stack'):
  x=int(request.POST['X']);
  y=int(request.POST['Y']);
  h=int(request.POST['h'])
  w=int(request.POST['w'])
  stack=request.session['stack']
  redostack=request.session['redostack']
  
  fileAbsPath=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','filestore/%s'%stack[0]));
  cropfilepath=str(Path(fileAbsPath).with_suffix(''))+str(uuid.uuid4())+'.png' #here dirty coding...

  oriimg=cv2.imread(fileAbsPath)

  
  crop_img = oriimg[y:h, x:w]
  cv2.imwrite(cropfilepath,crop_img);
  cropfilename=cropfilepath.split('/')[-1]
  stack.insert(0,cropfilename)
  
  request.session['redostack']=redostack;
  request.session['stack']=stack;

  return JsonResponse({'response':'croped'})
 else:
  return HttpResponse('') 
 
def setBorder(request):
 if request.method=="POST" and request.session.has_key('stack'):
  bordersize=int(request.POST['size']);
  stack=request.session['stack']
  redostack=request.session['redostack']
  request.session['borderSize']=bordersize
  fileAbsPath=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','filestore/%s'%stack[0]));
  borderfilepath=str(Path(fileAbsPath).with_suffix(''))+str(uuid.uuid4())+'.png' #here dirty coding...

  oriimg=cv2.imread(fileAbsPath)

  row,col=oriimg.shape[:2]
  bottom=oriimg[row-2:row,0:col]
  mean=cv2.mean(bottom)[0]
  border=cv2.copyMakeBorder(oriimg, top=bordersize, bottom=bordersize, left=bordersize, right=bordersize, borderType= cv2.BORDER_CONSTANT, value=[mean,mean,mean]) 
  
  cv2.imwrite(borderfilepath,border);
  borderfilename=borderfilepath.split('/')[-1]
  stack.insert(0,borderfilename)
  if request.session['redo']:
   redostack.insert(0,'setBorder')
  request.session['redo']=True
  request.session['redostack']=redostack
  request.session['stack']=stack;
  return JsonResponse({'response':'croped'})
 if request.method=="GET" and request.session.has_key('borderSize'):
  bordersize=request.session['borderSize'];
  stack=request.session['stack']
  fileAbsPath=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','filestore/%s'%stack[0]));
  borderfilepath=str(Path(fileAbsPath).with_suffix(''))+str(uuid.uuid4())+'.png' #here dirty coding...
  oriimg=cv2.imread(fileAbsPath)
  row,col=oriimg.shape[:2]
  bottom=oriimg[row-2:row,0:col]
  mean=cv2.mean(bottom)[0]
  border=cv2.copyMakeBorder(oriimg, top=bordersize, bottom=bordersize, left=bordersize, right=bordersize, borderType= cv2.BORDER_CONSTANT, value=[mean,mean,mean])
  cv2.imwrite(borderfilepath,border);
  borderfilename=borderfilepath.split('/')[-1]
  stack.insert(0,borderfilename)
  request.session['stack']=stack;
  return JsonResponse({'response':'croped'})

 else:
  return HttpResponse('')


def cool(request):
 if request.method=="GET" and request.session.has_key('stack'):
  stack=request.session['stack']
  redostack=request.session['redostack']
 if len(stack)>0:
  fileAbsPath=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','filestore/%s'%stack[0]));
  grayscalefilepath=str(Path(fileAbsPath).with_suffix(''))+str(uuid.uuid4())+'.png' #here dirty coding......
  grayImage=cv2.imread(fileAbsPath)
  grayImage=cv2.applyColorMap(grayImage,cv2.COLORMAP_PARULA)
  cv2.imwrite(grayscalefilepath,grayImage)
  gfilename=grayscalefilepath.split('/')[-1];
  stack.insert(0,gfilename)
  if request.session['redo']:
   redostack.insert(0,'cool')
  request.session['redo']=True
  request.session['stack']=stack
  request.session['redostack']=redostack
  return JsonResponse({'response':'convertedToGrayscale'})
 else:
  return HttpResponse()







def addWatermark(request):
 if request.method=="POST" and request.session.has_key('stack'):
  text=request.POST['t']
  print(text);
  stack=request.session['stack']
  redostack=request.session['redostack']
  request.session['text']=text
  fileAbsPath=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','filestore/%s'%stack[0]));
  textimgPath=str(Path(fileAbsPath).with_suffix(''))+str(uuid.uuid4())+'.png' #here dirty coding...

  oriimg=cv2.imread(fileAbsPath)

  overlay=oriimg.copy()
  output=oriimg.copy()
  cv2.putText(overlay,text.format(0.5),(10,30),cv2. cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
  

  cv2.addWeighted(overlay,0.5,output,1-0.5,0,output)
  
  cv2.imwrite(textimgPath,output);
  textimgName=textimgPath.split('/')[-1]
  stack.insert(0,textimgName)
  if request.session['redo']:
   redostack.insert(0,'addWatermark')
  request.session['redo']=True
  request.session['redostack']=redostack
  request.session['stack']=stack;
  return JsonResponse({'response':'croped'})
 if request.method=="GET" and request.session.has_key('borderSize'):
  bordersize=request.session['borderSize'];
  stack=request.session['stack']
  fileAbsPath=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','filestore/%s'%stack[0]));
  borderfilepath=str(Path(fileAbsPath).with_suffix(''))+str(uuid.uuid4())+'.png' #here dirty coding...
  oriimg=cv2.imread(fileAbsPath)
  row,col=oriimg.shape[:2]
  bottom=oriimg[row-2:row,0:col]

def rotateRight(request):
 if request.method=="GET" and request.session.has_key('stack'):
  stack=request.session['stack']
  redostack=request.session['redostack']
 if len(stack)>0:
  fileAbsPath=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','filestore/%s'%stack[0]));
  rotatefilepath=str(Path(fileAbsPath).with_suffix(''))+str(uuid.uuid4())+'.png' #here dirty coding......
  rotateImage=cv2.imread(fileAbsPath)
  (h,w)=rotateImage.shape[:2]
  center=(w/2,h/2)
  angle90=90
  scale=1.0
  M=cv2.getRotationMatrix2D(center,angle90,scale)
  rotated180=cv2.warpAffine(rotateImage,M,(h,w))

  cv2.imwrite(rotatefilepath,rotated180)
  gfilename=rotatefilepath.split('/')[-1];
  stack.insert(0,gfilename)
  if request.session['redo']:
   redostack.insert(0,'rotateRight')
  request.session['redo']=True
  request.session['stack']=stack
  request.session['redostack']=redostack
  return JsonResponse({'response':'rotated'})
 else:
  return HttpResponse()

def overlay(request):
 if request.method=="POST" and request.session.has_key('stack'):
  stack=request.session['stack']
  if len(stack)>0:
   imageFile=request.FILES['fileName']
   fs=FileSystemStorage()
   imageFileName=fs.save(imageFile.name,imageFile)
   imgpath=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','filestore/%s'%imageFileName))
   img=cv2.imread(imgpath)
   oriimgpath=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','filestore/%s'%stack[0]))
   oriimg=cv2.imread(oriimgpath)
   h,w=oriimg.shape[:2]
   print(h,w);

   tsa='large_white_square.png'; 
   transImgPath=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','filestore/%s'%tsa))
   tsa=cv2.imread(transImgPath);
   tsa=cv2.resize(tsa,(w,h))
   h,w=tsa.shape[:2]
   print(h,w)
   x_offset=y_offset=50
   tsa[y_offset:y_offset+img.shape[0], x_offset:x_offset+img.shape[1]] = img
   h,w=tsa.shape[:2]
   print(h,w)

   
   dst=cv2.addWeighted(oriimg,0.7,tsa,0.3,0);
   uui=str(uuid.uuid4())
   print(uui)
   print(uui[-3:])
   overlayfilepath=str(Path(oriimgpath).with_suffix(''))+uui[-3:]+'.png' #here dirty coding......
   cv2.imwrite(overlayfilepath,dst);
   overlayfilename=overlayfilepath.split('/')[-1]
   stack.insert(0,overlayfilename) 
   print(stack[0]);
   if request.session['redo']:
    #redostack.insert(0,'overlayed')
    request.session['redo']=True
    request.session['stack']=stack
    #request.session['redostack']=redostack
    return JsonResponse({'response':'rotated'})
 else:
  return HttpResponse()

   

