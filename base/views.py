from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm

# from django.http import HttpResponse

# Create your views here.

# rooms = [
#     {'id':1, 'name':'Lets learn python!'},
#     {'id':2, 'name':'Design with me'},
#     {'id':3, 'name':'Frontend developers'},
# ]


def loginPage(request):

    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exist.")

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Username or password does not exist.")
    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            #si queremos acceder al usuario de inmediato ponemos el commit false
            #si por ejemplo queremos formatear lo que puso el usuario antes de enviar el form
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'base/login_register.html', {'form':form})

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # Esto es un inline if, q= request si q != None, si es None, se le asigna ''
    # Se podría escribir también así: q = request.GET.get('q', '')
    # Es un filtro para mostrar solo los cuartos que contengan 'q' en el nombre
    # Se le asigna '' porque el caracter vacío vendría a esta en todos, entonces si no hay nada, muestra todos
    # si no ponemos '' da error porque None no puede ser un query value
    rooms = Room.objects.filter(
            Q(topic__name__icontains=q) |
            Q(name__icontains=q) |
            Q(description__icontains=q)
        )
    #La búsqueda era así al principio, luego importó Q y pudimos afinar
    # rooms = Room.objects.filter(topic__name__icontains=q)

    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {"rooms": rooms, 'topics': topics, 
               'room_count':room_count, 'room_messages': room_messages}
    return render(request, "base/home.html", context)


def room(request, pk):
    # return HttpResponse('ROOM')
    room = Room.objects.get(id=pk)
    # for i in rooms:
    #     if i['id'] == int(pk):
    #         room=i

    # podemos acceder a los hijos de la clase que estén 
    # en modelos que no son el de la clase en sí
    # en models.py tenemos Messages que tiene un room asignado
    room_messages = room.message_set.all()
    # 1- si agregamos al final .order_by('-created')
    # ordena en orden descendente según hora de creación
    # 2- de esta forma accedemos al set de messages 
    # que tenga asignado el room desde el que se está consultando
    
    participants = room.participants.all()
    
    if request.method == 'POST':
        message = Message.objects.create(
           user=request.user,
           room=room,
           body=request.POST.get('body')
           # El body que estamos pasando es el nombre del input
           # del form que estamos tomando la indormación
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    
    context = {"room": room, 'room_messages': room_messages,
               'participants': participants}

    return render(request, "base/room.html", context)

def userProfile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 
               'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)

@login_required(login_url='/login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        print(request.POST)
        # Podríamos hacer algo como request.POST.get('name')
        # y extraer así todos los datos, y luego usar
        # método de guardar en el modelo, pero ta todo cubierto
        # por el model form
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        # De esta forma, se fija si el topic_name ya existe
        # Si ya existe, get_or_create va a buscar el nombre del topic y lo va a retornar en un objeto Topic-
        # Created da false ya que ya estaba creado sabe que el topic ya existe en la base de datos
        # Si no existe, created da true, lo acabo de crear, crea un objeto Topic nuevo y lo agrega a la base de datos

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
        return redirect("home")

    context = {"form": form, "topics": topics}
    return render(request, "base/room_form.html", context)

@login_required(login_url='/login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    # esto sirve para pre-rellenar el form, si los valores no
    # matchean, no va a funcionar
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('decscription')
        room.save()
        # form = RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()

        return redirect("home")

    context = {"form": form, "topics": topics, "room": room}
    return render(request, "base/room_form.html", context)

@login_required(login_url='/login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')
    
    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, "base/delete.html", {"obj": room})


@login_required(login_url='/login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed here!!')
    
    if request.method == "POST":
        message.delete()
        return redirect("home")
    return render(request, "base/delete.html", {"obj": message})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    context = {"form": form}
    return render(request, 'base/update-user.html', context)