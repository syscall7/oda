from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from oda.apps.odaweb.disassembler import Disassembler
from oda.apps.odaweb.models import BinaryString, Symbol


@receiver(post_save, sender=BinaryString)
def binary_string_update(sender, instance, **kwargs):

    ctype = ContentType.objects.get_for_model(instance)
    Symbol.objects.filter(content_type=ctype, object_id=instance.id).delete()

    Disassembler(instance).analyze_first_time()