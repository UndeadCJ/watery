from _decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.utils import timezone


class User(models.Model):
    """
    Usuário do sistema | Sem autenticação
    """

    name = models.CharField(max_length=128, null=False, blank=False)
    weight = models.DecimalField(
        verbose_name="Peso",
        max_digits=5,
        decimal_places=2,
        help_text="Peso em KG",
        null=False,
        blank=False
    )

    @property
    def daily_goal(self):
        """
        Retorna a meta diária de consumo de água. Resultado em ML
        """

        # Fórmula: Peso em KG * 35ML
        return self.weight * 35

    def amount_taken(self, date=timezone.now()):
        """
        Retorna o total de água consumido no dia
        """

        total = self.water_intake.filter(date__exact=date).aggregate(
            amount=Sum(
                'quantity',
                output_field=models.DecimalField(
                    max_digits=6,
                    decimal_places=2
                )
            )
        )

        return total['amount'] or Decimal(0)

    def amount_left(self, date=timezone.now()):
        """
        Retorna o valor faltante para bater a meta do dia
        """

        amount_left = self.daily_goal - self.amount_taken(date)

        # Caso a meta seja passada (mais água consumida), é retornado 0
        if amount_left < 0:
            return Decimal(0)

        return amount_left

    def reached_goal(self, date=timezone.now()):
        """
        Retorna se a meta do dia foi batida ou não
        """

        # Se a quantia restante for igual a zero, a meta foi batida
        return self.amount_left(date) == 0

    def percent_amount(self, date=timezone.now()):
        """
        Calcula o percentual da meta já bebido
        """

        return round((self.amount_taken(date) * 100) / self.daily_goal, 2)

    def __str__(self):
        return self.name


class WaterIntake(models.Model):
    """
    Registra o consumo de água para um usuário
    """

    user_id = models.ForeignKey(
        User,
        verbose_name="Usuário",
        related_name="water_intake",
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )
    quantity = models.DecimalField(
        verbose_name="Quantidade",
        max_digits=6,
        decimal_places=2,
        help_text="Quantidade em ML",
        null=False,
        blank=False
    )
    date = models.DateField(
        verbose_name="Data",
        auto_now_add=True,
        help_text="Data do consumo",
        null=False,
        blank=True
    )

    def __str__(self):
        return f"Quantidade: {self.quantity}ML"
