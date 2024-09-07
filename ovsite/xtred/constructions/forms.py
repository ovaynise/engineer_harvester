from django import forms


from .models import (
    ConstructionsCompany,
    ConstructionsWorks,
    Location,
    Constructions,
    BrandType
)


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['country', 'city']


class ConstructionsCompanyForm(forms.ModelForm):
    class Meta:
        model = ConstructionsCompany
        exclude = ('author', 'is_published')


class BrandTypeForm(forms.ModelForm):
    class Meta:
        model = BrandType
        exclude = ('author', 'is_published')


class ConstructionsForm(forms.ModelForm):
    class Meta:
        model = Constructions
        exclude = ('author',
                   'is_published',
                   'description',
                   'longitude',
                   'latitude')


class ConstructionsWorksForm(forms.ModelForm):
    class Meta:
        model = ConstructionsWorks
        fields = [
            'work',
            'unit_of_measurement',
            'quantity',
            'constructions_company',
            'date_start',
            'date_finish'
        ]
