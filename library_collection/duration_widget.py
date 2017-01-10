# -*- coding: utf-8 -*-
# from : http://www.columbia.edu/~njn2118/journal/2015/10/30.html
from datetime import timedelta
from django import forms


class SplitDurationWidget(forms.MultiWidget):
    """
    A Widget that splits duration input into tow number input boxes.
    For months & days
    """
    def __init__(self, attrs=None):
        if attrs:
            month_attrs = dict(attrs)
            day_attrs = dict(attrs)
        else:
            month_attrs = {}
            day_attrs = {}
        month_attrs['title'] = 'number of months'
        day_attrs['title'] = 'number of days'
        widgets = (forms.NumberInput(attrs=month_attrs),
                   forms.NumberInput(attrs=day_attrs))
        super(SplitDurationWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            d = value
            if d:
                #hours = d.seconds // 3600
                #minutes = (d.seconds % 3600) // 60
                #seconds = d.seconds % 60
                months = d.days // 30
                days = d.days % 30
                return [int(months), int(days), ]#int(hours), int(minutes), int(seconds)]
        return [0, 0]

class MultiValueDurationField(forms.MultiValueField):
    widget = SplitDurationWidget

    def __init__(self, *args, **kwargs):
        fields = (
            #forms.IntegerField(),
            #forms.IntegerField(),
            forms.IntegerField(min_value=0),
            forms.IntegerField(min_value=0, max_value=29),
        )
        super(MultiValueDurationField, self).__init__(
            fields=fields,
            require_all_fields=True, *args, **kwargs)

    def compress(self, data_list):
        if len(data_list) == 2:
            months = int(data_list[0])
            days = int(data_list[1]) 
            days_total = days + (months * 30)
            if days_total:
                return timedelta(
                    days=int(days_total)
                    )
        return None


