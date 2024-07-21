from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import AuthorSerializer
from main.models import Author


# Create your views here.

@api_view(['GET'])
def search_authors(request):
    authors = Author.objects.filter(last_name__icontains=request.query_params.get('search_authors'))
    serialized_authors = AuthorSerializer(authors, many=True)
    return Response(serialized_authors.data)
