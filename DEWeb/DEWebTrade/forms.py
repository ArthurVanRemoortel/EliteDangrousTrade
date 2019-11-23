from django import forms
from bootstrap_datepicker_plus import DatePickerInput, TimePickerInput, DateTimePickerInput, MonthPickerInput, YearPickerInput
from django.forms.widgets import NumberInput
from django.core.validators import MaxValueValidator, MinValueValidator


class ItemForm(forms.Form):
    from_system = forms.CharField(label='System', max_length=200, required=False)

class RunForm(forms.Form):
    """
    The form used to filter events on the home page.
    """

    forced_command = forms.CharField(label='Command', max_length=200, required=False)

    from_system = forms.CharField(label='From system', max_length=100, required=False)
    from_station = forms.CharField(label='From station', max_length=100, required=False)

    to_type = forms.ChoiceField(choices=[(0, "To"), (1, "Towards")])
    to_system = forms.CharField(label='To system', max_length=100, required=False)
    to_station = forms.CharField(label='To station', max_length=100, required=False)

    via_system = forms.CharField(label='Via system', max_length=100, required=False)
    via_station = forms.CharField(label='Via station', max_length=100, required=False)

    hops_type = forms.ChoiceField(choices=[(0, "Hops"), (1, "Direct")])
    hops_n = forms.IntegerField(widget=NumberInput(),
                                validators=[MaxValueValidator(30), MinValueValidator(1)], required=False)
    do_loop = forms.BooleanField(widget=forms.CheckboxInput, required=False)
    loop_n = forms.IntegerField(widget=NumberInput(),
                                validators=[MaxValueValidator(30), MinValueValidator(0)], required=False)
    end_jumps = forms.IntegerField(widget=NumberInput(),
                                   validators=[MaxValueValidator(30), MinValueValidator(0)], required=False)
    credits = forms.IntegerField(widget=NumberInput(),
                                 validators=[MaxValueValidator(99999999999999999), MinValueValidator(0)], required=False)
    cargo = forms.IntegerField(widget=NumberInput(),
                               validators=[MaxValueValidator(99999999999999999), MinValueValidator(0)], required=True)
    ly = forms.FloatField(widget=NumberInput(),
                          validators=[MaxValueValidator(99999999999999999), MinValueValidator(0)], required=False)
