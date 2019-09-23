import coreapi
import coreschema
from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import status, renderers
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

# Create your views here.
from rest_framework.viewsets import ModelViewSet
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer

from games.game import RandomGameStarter, GameInformationService, InvalidSizeParameterException, \
    InvalidMinesParameterException, GameInteractor
from games.models import Game
from rest.schemas import CustomSchema
from rest.serializers import UserSerializer


class GamesView(APIView):
    """ Game service """

    authentication_classes = [TokenAuthentication ]
    permission_classes = [AllowAny ]
    game_starter_service = RandomGameStarter()
    game_marker = GameInteractor()
    game_manager = Game.objects

    schema = CustomSchema(fields_post=[
        coreapi.Field('size',
                      required=True,
                      description="Size of map",
                      schema=coreschema.Integer(5) ),
        coreapi.Field('mines',
                      required=True,
                      description="Amount of mines to set",
                      schema=coreschema.Integer(1) ),
    ],
        fields_put=[
            coreapi.Field('game_id',
                          required=True,
                          description="Game id",
                          schema=coreschema.Integer()),
            coreapi.Field('x',
                          required=True,
                          description="Position in x starting with 0",
                          schema=coreschema.Integer()),
            coreapi.Field('y',
                          required=True,
                          description="Position in y starting with 0",
                          schema=coreschema.Integer(0)),
        ]
    )


    def post(self, request):
        """
        Starts a new game

        Precondition:
        - size is an integer bigger than zero
        - mines is an integer bigger than zero such that mines is lesser than (size^2)
        """
        try:
            data = request.data
            game_information = self.game_starter_service.start_game(int(data.get('size')), int(data.get('mines')), request.user)
            information = {
                'map': game_information.notrevealed_matrix_string,
                'game_id': game_information.pk,
                'mine_count': game_information.mine_count,
            }
            return Response(
                {'message': "Game started", 'tx': information},
                status=status.HTTP_201_CREATED)
        except KeyError as ke:
            return Response({'messages': str(ke)}, status.HTTP_412_PRECONDITION_FAILED)
        except InvalidSizeParameterException as ve:
            return Response({'messages': {str(ve)}}, status.HTTP_412_PRECONDITION_FAILED)
        except InvalidMinesParameterException as ve:
            return Response({'messages': {str(ve)}}, status.HTTP_412_PRECONDITION_FAILED)
        except ValueError as ve:
            return Response({'messages': {str(ve)}}, status.HTTP_401_UNAUTHORIZED)

    def put(self, request):
        """
        Marks a position in a game

        Precondition:
        - game_id is id of existing and active game
        - x is lesser than game size
        - y is lesser than game size
        """
        try:
            data = request.data
            game = self.game_manager.find_game_by_id(request.data.get('game_id'))
            result = self.game_marker.mark(GameInformationService(game), int(data.get('x')), int(data.get('y')))
            return Response(
                {'message': "Game marked", 'tx': result},
                status=status.HTTP_201_CREATED)
        except KeyError as ke:
            return Response({'messages': str(ke)}, status.HTTP_412_PRECONDITION_FAILED)
        except InvalidSizeParameterException as ve:
            return Response({'messages': {str(ve)}}, status.HTTP_412_PRECONDITION_FAILED)
        except InvalidMinesParameterException as ve:
            return Response({'messages': {str(ve)}}, status.HTTP_412_PRECONDITION_FAILED)


class GameInteractionView(APIView):
    game_manager = Game.objects

    def get(self, request, game_id):
        """
        Retrieves a game by id
        """
        game_model = self.game_manager.find_game_by_id(game_id)
        game_information = GameInformationService(game_model)
        information = {
            'map': game_information.notrevealed_matrix_string,
            'mine_count': game_information.mine_count,
        }
        return Response(information, status=status.HTTP_200_OK)


class UsersView(CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny ]