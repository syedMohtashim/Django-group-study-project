from pyexpat import model
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Room, Topic, Message
from .forms import RoomForm
# To search rooms on the basis of topics , Name etc
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm

rooms = [
    {'id':1, 'name':'Room01'},
    {'id':2, 'name':'Room02'},
    {'id':3, 'name':'Room03'},
    {'id':4, 'name':'Room04'},

]



def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Oops , this User doesnot exists!!')

        user = authenticate(request, username = username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Oops , cannot log in because of Incorrect credentials !!!')

    context = {'page':page}
    return render(request, 'app1/login_register.html', context)


def logoutPage(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Oops , we encountered an error from your side during registeration !!')

    return render(request, 'app1/login_register.html',{'form':form})


def home(request):
    # q is the topic-type querried by the user
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # so get the rooms available for the specific topic
    # topic__name__icontains will check all the valid topics , if '' then it will print all the topics
    # if the user is searching for Web-dev , and there is a room of topic Web-development
    # than becuase some of the string matches so the room with the topic Web-development will be shown
    
    # This one will show only topic name based search
    # rooms = Room.objects.filter(topic__name__icontains = q)
    
    # This one will show results of either Room-name or topic based search
    rooms = Room.objects.filter(Q(topic__name__icontains = q) | Q(name__icontains=q))
    room_count = rooms.count()
    # rooms = Room.objects.all()

    # To sort the messages from newest to oldest , I changed the models.py
    # room_messeges = Message.objects.all() 
    # If I want to see topic related messages in a room 
    room_messeges = Message.objects.filter(Q(room__topic__name__icontains = q))
    # room_messeges = Message.objects.all().order_by('-created')

    topics = Topic.objects.all()
    context = {"rooms":rooms, "topics":topics, "room_count":room_count, 'room_messeges':room_messeges}
    return render(request, 'app1/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    # room_messages = room.message_set.all()  This will give you all the messages/comments
    room_messages = room.message_set.all().order_by('-created')   # This will give you the most recent ones first
    # Now we will look for all the participants
    participants = room.participants.all()
    if request.method == 'POST':
        room_messages = Message.objects.create(
            user = request.user, 
            room = room, 
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        # Now , we will redirect the user to the room
        # But wait , which room , the room.id will tell this!
        return redirect('room', pk=room.id)

    context = {"room":room, 'room_messages':room_messages, 'participants':participants}
    return render(request, 'app1/room.html', context)

# def userProfile(request, pk):
#     user = User.objects.get(id=pk)
#     rooms = user.room_set.all()
#     room_messeges = user.message_set.all()
#     topics = Topic.objects.all()
#     context = {'user':user, 'rooms':rooms, 'room_messeges':room_messeges, 'topics':topics}
#     return render(request, 'app1/profile.html', context)
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms,
               'room_messages': room_messages, 'topics': topics}
    return render(request, 'app1/profile.html', context)
@login_required(login_url='login')
def createRoom(request):

    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid:
            room = form.save(commit = False)
            room.host = request.user
            room.save()
            return redirect('home')

        
    context = {'form':form}
    return render(request, 'app1/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse('Only the creator can Update !!')

    if request.method == 'POST':
        #  form = RoomForm(request.POST) will work for all , but 
        # we want to edit a specific room , so we add instance = room
        form = RoomForm(request.POST, instance = room)
        if form.is_valid:
            form.save()
            return redirect('home')


    context = {'form':form}
    return render(request, 'app1/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('Only the creator can Delete !!')
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'app1/delete.html',{'obj':room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    msg = Message.objects.get(id=pk)
    if request.user != msg.user:
        return HttpResponse('Only the creator can Delete !!')
    if request.method == 'POST':
        msg.delete()
        return redirect('home')
    return render(request, 'app1/delete.html',{'obj':msg})