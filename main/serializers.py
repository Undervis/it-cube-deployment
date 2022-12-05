from rest_framework.serializers import ModelSerializer
from .models import Student, PaidGroupEnroll

class StudentsSerializer(ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'last_name', 'first_name', 'middle_name', 'birthday',
                  'group', 'paid_group', 'parent_name', 'parent_number', 'status', 'school']
        
    def to_representation(self, instance):
        presentation = super().to_representation(instance)
        try:
            presentation['group'] = instance.group.group_name
            pgs = PaidGroupEnroll.objects.filter(student=instance)
            presentation['paid_status'] = False
            for pg in range(len(presentation['paid_group'])):
                presentation['paid_group'][pg] = {'name': pgs[pg].paid_group.group_name, 'status': pgs[pg].paid_status} 
                if pgs[pg].paid_status == 0:
                    presentation['paid_status'] = True
        except AttributeError:
            presentation['paid_status'] = True
        return presentation