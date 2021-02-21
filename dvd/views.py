from rest_framework.views import APIView
from .models import Film
from .serializers import DvdSerializer
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from rest_framework import status
from django.db import connection, transaction
from django.http import Http404
from rest_framework.settings import api_settings
import psycopg2
import psycopg2.extras

import json
import logging
conn = psycopg2.connect(database="dvd", user="postgres", password="22063shi")
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
cursor = connection.cursor()
logger = logging.getLogger('dvdapi')
class CategoryView(APIView):
    def get(self, request):
        query = ("""
            select
                name
            from
                category
            group by
                name
        """)
        cursor.execute(query)
        categories = cursor.fetchall()
        category_list = {'category':[]}
        for category in categories:
            category_list['category'].append(category[0])
        return Response(category_list)

class LanguageView(APIView):
    def get(self, request):
        query = ("""
            select
                name
            from
                language
            group by
                name
        """)
        cursor.execute(query)
        languages = cursor.fetchall()
        language_list = {'language':[]}
        for language in languages:
            language_list['language'].append(language[0])
        return Response(language_list)

class DvdListView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = DvdSerializer
    def get(self, request):
        where = 'where 1 = 1 '
        if "category" in request.GET and request.GET.get("category") != "":
            category = request.GET.get("category")
            where += "and category.name = '{}'".format(category)
        query = ("""
            
            select
                film.film_id as film_id,
                film.title as title,
                actor.first_name || actor.last_name as actor_name,
                category.name,
                language.name,
                film.rating,
                film.release_year,
                film.replacement_cost,
                film.rental_flag
            from
                film
            inner join
                (select 
                    film_id, 
                    (select 
                        fa2.actor_id 
					from 
                        film_actor as fa2 
                    where 
                        fa2.film_id = fa1.film_id 
                    limit 1) as actor_id
				 from 
                    film_actor as fa1 
				 group by 
                    film_id
                )as film_actor
            on
                film.film_id = film_actor.film_id
            inner join
                actor
            on
               film_actor.actor_id = actor.actor_id
            inner join
                film_category
            on
               film.film_id = film_category.film_id
            inner join
                category
            on
                film_category.category_id = category.category_id
            inner join
                language
            on
                film.language_id = language.language_id
            {}
            order by
                film.film_id
            limit 10
        """)
        cursor.execute(query.format(where))
        results = cursor.fetchall()
        logger.info(results)
        film = {}
        for result in results:
            film_id  = result[0]
            title    = result[1]
            actor    = result[2]
            category = result[3]
            language = result[4]
            rating   = result[5]
            releace  = result[6]
            cost     = result[7]
            flag     = result[8]
            film[film_id] = {'title':title, 'actor':actor, 'ctegory':category, 'language':language, 'rating':rating, 'release':releace, 'cost':cost, 'flag':flag}
        return Response(film)

    def get_object(self, pk):
        try:
            return Film.objects.get(pk=pk)
        except Film.DoesNotExist:
            raise Http404

    def patch(self, request):
            response_data = []
            for d in request.data['id']:
                film = self.get_object(pk=d)
                serializer = self.serializer_class(film, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    response_data.append(serializer.data)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(response_data)

class RentalView(APIView):
    serializer_class = DvdSerializer
    def post(self, request):
        keys = ["title", "language"]
        if all(key in request.data for key in keys):
            title = request.data["title"]
            language = request.data["language"]
        else:
            raise Http404
        try:
            query = ("""
                insert into 
                    film (title, language_id)
                values
                    ('%s', %s)
                returning film_id, title, language_id
            """%(title, language))
            cur.execute(query)
            results = cur.fetchall()
        except Exception:
            print('error')
        connection.commit()
        
        data = []

        for row in results:
            data.append(dict(row))
        return Response(data)
        # serializer = self.serializer_class(data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # else:
        #     print(serializer.errors)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        

class GetPostAPI(APIView):
    serializer_class = DvdSerializer
#   @transaction.atomic
    def get_object(self, pk):
        try:
            return Film.objects.get(pk=pk)
        except Film.DoesNotExist:
            raise Http404
    def get(self, request, pk, format=None):
        film = self.get_object(pk)
        serializer = self.serializer_class(film)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        film = self.get_object(pk)
        serializer = self.serializer_class(film, data=request.data, partial=True)
        logger.info(serializer)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)