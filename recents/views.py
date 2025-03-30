from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import SuricataAlert
from .serializers import SuricataAlertSerializer
import json

@csrf_exempt
@api_view(['POST'])
def recent_timestamps(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')

            if not username or not email:
                return Response({'error': 'Username and email are required'}, status=400)

            matching_alerts = SuricataAlert.objects.filter(username=username, email=email)

            if matching_alerts.exists():
                serializer = SuricataAlertSerializer(matching_alerts, many=True)
                return Response(serializer.data)
            else:
                return Response({'message': 'No matching records found'}, status=404)

        except json.JSONDecodeError:
            return Response({'error': 'Invalid JSON format'}, status=400)

    return Response({'error': 'Invalid request method'}, status=405)
