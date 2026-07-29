from django.contrib.auth.models import Permission
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType

      
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'content_type', 'codename']
        
    
    
      
class PermissionListSerializer(serializers.ModelSerializer):
  class Meta:
    model = Permission
    fields = ['id', 'name', 'content_type', 'codename']
  
  def group_by_content_type(self, data_list):
    content_types_queryset = ContentType.objects.all()
    grouped_data = {}
    for item in data_list:
        content_type = item['content_type']
        content_type_name = content_types_queryset.filter(id=content_type).first()
        if not content_type_name:
            continue
        
        content_type_name = content_type_name.model + '_' + content_type_name.app_label
        if content_type_name not in grouped_data:
            grouped_data[content_type_name] = []

        grouped_data[content_type_name].append(item)
    return grouped_data  
  
  
  def to_representation(self, instance):
        queryset_list = instance.values('id','name','content_type','codename')
        sorted_by_content = self.group_by_content_type(queryset_list)
        return sorted_by_content
