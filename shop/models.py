from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import validate_email
from timestamps.models import models, Model, Timestampable

User = get_user_model()


class Shop(Model):
    """Магазин"""
    name = models.CharField(
        max_length=512,
        null=False,
        verbose_name=_("название")
    )
    description = models.TextField(
        max_length=5000,
        verbose_name=_("описание")
    )
    phone = PhoneNumberField(
        null=False,
        blank=False,
        unique=True,
        verbose_name=_("телефон")
    )
    email = models.EmailField(
        max_length=100,
        blank=False,
        null=False,
        unique=True,
        validators=[validate_email],
        verbose_name=_("электронная почта")
    )
    address = models.CharField(
        max_length=512,
        null=False,
        verbose_name=_("адрес")
    )
    image = models.ImageField(
        blank=True,
        upload_to="shop_logo/%Y/%m/%d",
        verbose_name=_("логотип")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name=_("владелец")
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("магазин")
        verbose_name_plural = _("магазины")


# предлагаю добавить таблицу в нашу схему
class ShopImage(Timestampable):
    """Фотографии магазинов"""
    image = models.ImageField(
        blank=False,
        upload_to="shop_photo/%Y/%m/%d",
        verbose_name=_("фото")
    )
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        verbose_name=_("магазин")
    )
