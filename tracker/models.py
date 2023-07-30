from _decimal import Decimal

from django.db import models
from django.db.models import Sum


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
    def daily_water_intake_goal(self):
        """
        Retorna a meta diária de consumo de água. Resultado em ML
        """

        # Fórmula: Peso em KG * 35ML
        return self.weight * 35

    @property
    def water_amount_taken_today(self):
        """
        Retorna o total de água consumido hoje
        """
        
        total = self.water_intake.aggregate(
            amount=Sum(
                'quantity',
                output_field=models.DecimalField(
                    max_digits=6,
                    decimal_places=2
                )
            )
        )

        return total['amount'] or Decimal(0)
    
    @property
    def amount_left_to_goal(self):
        """
        Retorna o valor faltante para bater a meta
        """

        amount_left = self.daily_water_intake_goal - self.water_amount_taken_today

        # Caso a meta seja passada (mais água consumida), é retornado 0
        if amount_left < 0:
            return Decimal(0)

        return amount_left

    @property
    def goal_reached(self):
        """
        Retorna se a meta foi batida ou não
        """

        return True if self.amount_left_to_goal == 0 else False


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
