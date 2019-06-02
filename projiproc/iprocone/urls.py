from django.urls import path
from . import views
urlpatterns=[ path('',views.index,name='index'),
path('openFile',views.openFile,name='openFile'),
path('getImage',views.getImage,name='getImage'),
path('toGrayscale',views.toGrayscale,name='toGrayscale'),
path('getState',views.getState,name='getState'),
path('closeFile',views.closeFile,name='closeFile'),
path('undo',views.undo,name='undo'),
path('scaleit',views.scaleit,name='scaleit'),
path('cropIt',views.cropIt,name='cropIt'),
path('setBorder',views.setBorder,name='setBorder'),
path('cool',views.cool,name='cool'),
path('redo',views.redo,name='redo'),
path('showOrignal',views.showOrignal,name='showOrignal'),
path('addWatermark',views.addWatermark,name='addWatermark'),
path('rotateRight',views.rotateRight,name='rotateRight'),
path('overlay',views.overlay,name='overlay'),
]

