from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector
from django.db.models import Q
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import ReaderSerializer


# Create your views here.

@api_view(['GET'])
def search_readers(request):
    search = request.query_params.get('search_readers')
    readers = (User.objects.filter(groups__name='reader')
               .annotate(search=SearchVector('first_name', 'last_name'))
               .filter(Q(search=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search)))
    serialized_readers = ReaderSerializer(readers, many=True)
    return Response(serialized_readers.data)
