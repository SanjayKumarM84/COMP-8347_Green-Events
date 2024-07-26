from django import forms
from django.utils.safestring import mark_safe


class StarRatingWidget(forms.RadioSelect):
    template_name = 'widgets/star_rating.html'

    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.attrs.update({'class': 'star-rating'})

    def render(self, name, value, attrs=None, renderer=None):
        output = super().render(name, value, attrs, renderer)
        return mark_safe(f'<fieldset class="rating">{output}</fieldset>')
