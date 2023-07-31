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
    def daily_goal(self):
        """
        Retorna a meta diária de consumo de água. Resultado em ML
        """

        # Fórmula: Peso em KG * 35ML
        return self.weight * 35

    def __str__(self):
        return self.name


class History(models.Model):
    """
    Registra o consumo de água de um dia para um usuário
    """

    user_id = models.ForeignKey(
        User,
        verbose_name="Usuário",
        related_name="history",
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )
    goal = models.DecimalField(
        verbose_name="Meta",
        max_digits=6,
        decimal_places=2,
        help_text="Meta do dia em ML",
        null=False,
        blank=False
    )
    date = models.DateField(
        verbose_name="Data",
        auto_now_add=True,
        help_text="Data",
        null=False,
        blank=True
    )

    @property
    def amount_taken(self):
        """
        Retorna o total de água consumido no dia
        """

        total = self.intake.aggregate(
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
    def amount_left(self):
        """
        Retorna o valor faltante para bater a meta do dia
        """

        amount_left = self.goal - self.amount_taken

        # Caso a meta seja passada (mais água consumida), é retornado 0
        if amount_left < 0:
            return Decimal(0)

        return amount_left

    @property
    def reached_goal(self):
        """
        Retorna se a meta do dia foi batida ou não
        """

        # Se a quantia restante for igual a zero, a meta foi batida
        return self.amount_left == 0

    @property
    def percent_amount(self):
        """
        Calcula o percentual da meta já bebido
        """

        return round((self.amount_taken * 100) / self.goal, 2)

    def __str__(self):
        return f"Consumo do dia {self.date} por {self.user_id}"

    class Meta:
        unique_together = [['user_id', 'date']]


class Intake(models.Model):
    """
    Registra o consumo de água para um usuário
    """

    history_id = models.ForeignKey(
        History,
        verbose_name="Histórico",
        related_name="intake",
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

    def __str__(self):
        return f"Quantidade: {self.quantity}ML"
