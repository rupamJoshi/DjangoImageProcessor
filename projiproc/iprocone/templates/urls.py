form django.urls import path
form . import views
urlpatterns=[path(",view.index,name='index'"),
path('openFile',view.openFile,name='openFile'),
path('getImage',views.getImage,name='getImage'),
path('toGrayscale',views.toGrayscale,name='toGrayscale'),
path('getState',views.getState,name='getState'),
path('closeFile',views.closeFile,name='closeFile'),
]
