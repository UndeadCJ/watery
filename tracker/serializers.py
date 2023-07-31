from rest_framework import serializers

from tracker.models import User, Intake, History


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'weight', 'daily_goal']


class IntakeSerializer(serializers.ModelSerializer):
    history_id = serializers.PrimaryKeyRelatedField(queryset=History.objects.all(), write_only=True)

    class Meta:
        model = Intake
        fields = '__all__'


class HistorySerializer(serializers.ModelSerializer):
    """
    Read-Only serializer. Responsável por gerar a tela de resumo
    """

    intakes = IntakeSerializer(source='intake', many=True)
    goal = serializers.DecimalField(max_digits=6, decimal_places=2)
    amount_taken = serializers.DecimalField(max_digits=6, decimal_places=2)
    amount_left = serializers.DecimalField(max_digits=6, decimal_places=2)
    percent_reached = serializers.CharField(source='percent_amount')
    reached_goal = serializers.BooleanField()

    class Meta:
        model = History
        fields = [
            'id',
            'date',
            'intakes',
            'goal',
            'amount_taken',
            'amount_left',
            'percent_reached',
            'reached_goal',
        ]