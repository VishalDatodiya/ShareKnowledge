from django.shortcuts import render, redirect
from django.contrib import messages
# from django.template import loader

from django.http import HttpResponse

# from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout

from django.contrib.auth.decorators import login_required

# from django.contrib.auth.forms import UserCreationForm

# all the models including custom USER Model
from .models import Room, Topic, Messages, User
from .forms import RoomForm, UserForm, MyUserCreationForm
# lookup message
from django.db.models import Q



# rooms = [
#     {'id': 1, 'name':'Learning Python'},
#     {'id': 2, 'name':'Learning HTML'},
#     {'id': 3, 'name':'Learning Django'},
# ]


def loginPage(request):
    
    page = 'login'
    
    # if user is logged in already and if he manually type in url bar login so it should redirect to home page
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        # username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist!')
            
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist!')
            
    context = {'page':page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = MyUserCreationForm()
    
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) # commit=False bcz if user by mistake use capical so we can change in lower case
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Something is not valid please try again!')
    context = {'form':form}
    return render(request, 'base/login_register.html',context)

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # rooms = Room.objects.all()
    # searching
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) 
        # Q(description__icontains=q)
    )
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    
    room_messages = Messages.objects.filter(Q(room__topic__name__icontains=q))
    
    context = {
        'rooms':rooms,
        'topics': topics,
        'room_count':room_count,
        'room_messages':room_messages,
    }
    return render(request, 'base/index.html', context)
    
    # template = loader.get_template('base/home.html')
    # return HttpResponse(template.render())

def room(request, pk):
    room = Room.objects.get(pk=pk)
    # here we are query chinld object of specific room
    # we have parent model is Room and message is child Model 
    # here we use Message model in small case letter __set is a method
    room_messages = room.messages_set.all().order_by('-created')
    
    participants = room.participants.all()

        
    if request.method == 'POST':
        
        if not request.user.is_authenticated:
            messages.error(request,"Please Login First")
            return redirect('login')
        
    # We want to write the message and save in db so in create method we use user, room and body bcz we defined in Message Model we don't need updated and created bcz of autogenerated
        message = Messages.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body') # body in get method bcz in form we used body as name
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {
        'room':room, 
        'room_messages':room_messages, 'participants':participants
        }
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(pk=pk)
    rooms = user.room_set.all()     # i use rooms bcz in feed_component.html i iterate rooms data. then room is model and set is method
    room_messages = user.messages_set.all()  # i used same as above line
    topics = Topic.objects.all() # here I want to show all the topics and not only user's topics
    
    context = {
        'user':user,
        'rooms':rooms,
        'room_messages':room_messages,
        'topics':topics,
        
    }
    return render(request, 'base/profile.html', context)



@login_required(login_url='login')
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        # if we want to create new topic then it will create and bring in topic if we want to add in existing topic then we will get.
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'), 
        )
        return redirect('home')
        
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     # form.save()
        #     # here we are excluded the host and participants from create room and we here automatically save if user is authenticated
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
            # return redirect('home')
    context = {
        'form':form,
        'topics':topics,
    }
    
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def update_room(request,pk):
    room = Room.objects.get(pk=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    # if someone has id of room so they can edit but we are restricted them
    if request.user != room.host:
        return HttpResponse('You are not allowed here!')
    
    
    if request.method == "POST":
        
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
        
        
        
        # request.POST take whole data but instance=room tell that which data we want to update
        # form = RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()
        #     return redirect('home')
    context = {
        'form':form,
        'topics':topics,
        'room':room,
    }
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def detete_room(request,pk):
    room = Room.objects.get(pk=pk)
    
    if request.user != room.host:
        return HttpResponse('You are not allowed here!')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})


@login_required(login_url='login')
def detete_message(request,pk):
    message = Messages.objects.get(pk=pk)
    
    if request.user != message.user:
        return HttpResponse('You are not allowed here!')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':message})


@login_required(login_url='login')
def update_user(request):
    user = request.user
    form = UserForm(instance=user)
    
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
        
    context = {
        'form':form,
    }
    return render(request, 'base/update_user.html', context)


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics':topics})


def activityPage(request):
    # q = request.GET.get('q') if request.GET.get('q') != None else ''
    room_messages = Messages.objects.all()
    return render(request, 'base/activity.html', {'room_messages':room_messages})
