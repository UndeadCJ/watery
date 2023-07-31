from datetime import datetime

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response

from tracker.errors import BadParams
from tracker.models import User, History
from tracker.serializers import UserSerializer, IntakeSerializer, HistorySerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_or_create_point_in_history(self):
        """
        Caso o dia do histórico exista ele é retornado, caso contrário é criado
        """

        user = self.get_object()

        if history_obj := History.objects.filter(date__exact=timezone.now(), user_id__exact=user.pk).first():
            obj = history_obj
        else:
            obj = History(
                user_id=user,
                goal=user.daily_goal
            )
            obj.save()

        return obj

    @action(detail=True, methods=['POST'])
    def drink(self, request: Request, pk=None):
        """
            Endpoint que registra o consumo de água de um usuário
        """

        point_in_history = self.get_or_create_point_in_history()
        intake_serializer = IntakeSerializer(
            data={
                **request.data,
                "history_id": point_in_history.pk
            }
        )
        intake_serializer.is_valid(raise_exception=True)
        intake_serializer.save()

        return Response(intake_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['GET'])
    def resume(self, request: Request, pk=None):
        """
            Endpoint que retorna o resumo do dia especificado caso exista
        """

        # Checa se o usuário existe
        self.get_object()

        # Caso o usuário envie uma data como parâmetro da query
        if param_date := request.query_params.get("date", None):
            try:
                date = datetime.strptime(param_date, "%Y-%m-%d").date()
            except ValueError:
                raise BadParams(f"Parâmetro 'date' inválido")

        else:
            date = timezone.now()

        history = History.objects.filter(user_id__exact=pk, date__exact=date).first()
        if not history:
            raise NotFound(f"Dia '{date}' não existe no histórico do usuário")

        serializer = HistorySerializer(history)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'])
    def history(self, request: Request, pk=None):
        """
            Endpoint que retorna o histórico do usuário de forma paginada
        """

        # Checa se o usuário existe
        self.get_object()

        queryset = History.objects.filter(user_id__exact=pk)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = HistorySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = HistorySerializer(queryset, many=True)
        return Response(serializer.data)
