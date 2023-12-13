from django.forms import ModelChoiceField

class UserChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.first_name} {obj.last_name}'