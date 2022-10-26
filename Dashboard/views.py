from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
# Create your views here.
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .decorators import unauthenticated_user, allowed_users, admin_only
from django.core.files.storage import FileSystemStorage
# import pickle
# import joblib
# import pandas as pd
import numpy as np
# import datetime
from keras.models import load_model
# from keras.preprocessing import image
# import json
from tensorflow import Graph
from tensorflow import compat
import tensorflow as tf
from pathlib import Path


img_height, img_width=150,150



labelInfo= {0:'Negatif', 1:'Unidentifiable',2:'Positif'}



model_graph = Graph()
with model_graph.as_default():
    tf_session = tf.compat.v1.Session()
    with tf_session.as_default():
        model=load_model('./models/model.h5')



#@allowed_users(allowed_roles=['admin'])
@login_required(login_url='login')
def predict(request):


    fileObj = request.FILES.get('filePath')

    fs = FileSystemStorage()
    if fileObj is not None:
        fileName=fs.save(fileObj.name,fileObj)
        filePathName=fs.url(fileName)
        testimage = '.' + filePathName

        img = tf.keras.utils.load_img(testimage, target_size=(img_height, img_width))
        x = tf.keras.utils.img_to_array(img)

        x=x/255
        x=x.reshape(-1, img_height, img_width, 1)
        with model_graph.as_default():
            with tf_session.as_default():
                pred = model.predict(x)
        predicted_index=np.argmax(pred)
        predictedLabel=labelInfo[predicted_index]

        message=""
        if (predicted_index == 0):
            message='Pneumonia is not detected'

        elif (predicted_index == 1):
            message="We're sorry we're having trouble processing the image! " \
                    "Please try uploading more accurate X-Ray scan "
        elif (predicted_index == 2):
            message='Pneumonia is detected'
        context = {'filePathName': filePathName, 'fileName': fileName, 'predictedLabel': predictedLabel, 'message': message}
    else:
        context = {}
    return render(request, 'dashboard.html', context)



def history(request):
    media_path='./media'
    import os
    if not os.path.exists(media_path):
        os.makedirs(media_path)
    listOfImagesPath = [str(path) for path in sorted(Path(media_path).iterdir(), key=os.path.getmtime)]
    listOfImagesPath.reverse()

    listOfImagesName= [name[6:] for name in listOfImagesPath]

    dict=zip(listOfImagesName,listOfImagesPath)
    context = {'dict': dict}
    return render(request,'history.html',context)


#@unauthenticated_user
@login_required(login_url='login')
def registerForm(request):

    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            group = Group.objects.get(name='customer')

            if request.user.groups.filter(name='admin').exists():
                group = Group.objects.get(name='admin')

            user.groups.add(group)
            messages.success(request, 'Account was created for ' + username +' !')
            return redirect('register')

    context = {'form': form}
    return render(request, 'register1.html', context)
    # in return render we specify the path for the page



@unauthenticated_user
def loginForm(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, 'Username or password is incorrect !')

    context = {}
    return render(request, 'login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def index(request):
    return render(request, 'dashboard.html')






