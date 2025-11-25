from django.db import models

class BaseModel(models.Model):
    class Meta:
        abstract = True

    def get_business(self):
        """
        Retorna el business asociado siguiendo relaciones hacia atrás.
        """
        # Busca si el modelo tiene business_key, llave foránea directa a business
        if hasattr(self, "business_key"):
            return self.business_key

        # Si no tiene business_key, revisa campos con relación a otros modelos
        for field in self._meta.get_fields():
            # revisa solamente los campos que son relaciones many-to-one (ForeignKey)
            if field.is_relation and field.many_to_one and hasattr(self, field.name):
                related_obj = getattr(self, field.name)
                if related_obj:
                    # Si ese objeto tiene business, retornarlo
                    if hasattr(related_obj, "get_business"):
                        return related_obj.get_business()
                    if hasattr(related_obj, "business_key"):
                        return related_obj.business

        return None
    
    