from datetime import datetime

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response

from tracker.models import User, History
from tracker.serializers import UserSerializer, IntakeSerializer, HistorySerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self, pk):
        """
        Override do método get_object da view para caso não encontrar
        o record correspondente a pk, fazer o raise do código 404
        """
        return get_object_or_404(User, pk=pk)

    def get_or_create_point_in_history(self, pk):
        """
        Caso o dia do histórico exista ele é retornado, caso contrário é criado
        """

        user = self.get_object(pk)

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

        point_in_history = self.get_or_create_point_in_history(pk)
        intake_serializer = IntakeSerializer(
            data={
                **request.data,
                "history_id": point_in_history.pk
            }
        )
        intake_serializer.is_valid(raise_exception=True)
        intake_serializer.save()

        return Response(intake_serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'])
    def resume(self, request: Request, pk=None):
        """
            Endpoint que retorna o resumo do dia especificado caso exista
        """

        # Caso o usuário envie uma data como parâmetro da query
        if param_date := request.query_params.get("date", None):
            date = datetime.strptime(param_date, "%Y-%m-%d").date()
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

        queryset = History.objects.filter(user_id__exact=pk)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = HistorySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = HistorySerializer(queryset, many=True)
        return Response(serializer.data)
