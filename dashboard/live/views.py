from django.shortcuts import render


def index(request):
    return render(request, 'live/index.html')


def room(request, room_name):
    return render(request, 'live/room.html', {
        'room_name': room_name
    })
