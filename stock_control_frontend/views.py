from django.views import View
from django.shortcuts import render


class FrontendView(View):
    TEMPLATE_NAME = 'frontend.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context = {}

    def get(self, request, *args, **kwargs):
        return render(request, self.TEMPLATE_NAME, self.context)
