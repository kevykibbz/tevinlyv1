from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse
from channels.layers import get_channel_layer
import json
from django.template import RequestContext
# Create your views here.


from asgiref.sync import async_to_sync
def send_notification(request):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "notification_broadcast",
        {
            'type': 'send_notification',
            'message': json.dumps("Notification")
        }
    )
    return HttpResponse("Done")