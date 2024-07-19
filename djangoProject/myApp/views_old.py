from django.shortcuts import render
from .models import *
from django.http import JsonResponse


def event_details_func(eventObj):
    event_data = {
        'id': eventObj.id,
        'name': eventObj.name,
        'description': eventObj.description,
        'date': eventObj.eventDate.strftime('%Y-%m-%d'),  # Convert date time to string
        'time': eventObj.eventDate.strftime('%H:%M:%S'),  # Convert date time to string
        'location': eventObj.location,
        'agenda': eventObj.agenda,
        'speakers': eventObj.speakers,
        'total_num_of_seats': eventObj.total_num_of_seats,
        'registered_seats': eventObj.registered_seats,
        'remaining_seats': eventObj.remaining_seats,
    }
    return event_data


# Create your views here.
def index(request):
    data = {}
    try:
        modelObj = Event.objects.all()
        events = []
        for each in modelObj:
            event_data = event_details_func(each)
            events.append(event_data)
        data['events'] = events
        return JsonResponse(data)
    except Exception as e:
        data["message"] = str(e)
        return JsonResponse(data)


def eventSearch(request, userInput):
    data = {}
    try:
        searchEventObj = Event.objects.filter(name__icontains=userInput)
        events = []
        for each in searchEventObj:
            event_data = event_details_func(each)
            events.append(event_data)
        data['events'] = events
        return JsonResponse(data)
    except Exception as e:
        data["message"] = str(e)
        return JsonResponse(data)


def eventDetails(request, id):
    data = {}
    try:
        eventObj = Event.objects.get(id=id)
        data[eventObj.id] = event_details_func(eventObj)
        return JsonResponse(data)
    except Exception as e:
        data["message"] = str(e)
        return JsonResponse(data)
