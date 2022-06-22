from django.contrib.auth.models import User
from django.template.loader import get_template

from .forms import UserRegistrationForm, SearchHistoryForm
from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import ModelFormMixin, FormMixin
from django.contrib import messages
from django.shortcuts import redirect, render
from .models import Item
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy

import datetime
from itertools import chain
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce


from django.http import HttpResponse
import json


class ItemListView(LoginRequiredMixin, ListView, FormMixin):
    template_name = 'items.html'
   
    model = Item
    
    form_class = SearchHistoryForm

  

    def get_context_data(self, *args, **kwargs):
        time = []
        total = []
        today_items = []
        today_total = 0
        # context = self.get_context_data(**kwargs)
        # form = context['form']
        user = get_object_or_404(User, username=self.request.user.username)
        print(user)
        today_items_query = Item.objects.filter(user=user, added_on__day=(datetime.datetime.now()).day).order_by('-added_on')
        # q = User.objects.values('username').filter(username=user.username).annotate(total=Sum('item__price'))
        # print(q.query)
        if today_items_query:
            for item in today_items_query:
                today_items.append(item)
                q = today_items_query.aggregate(total=Sum('price'))
                today_total += q['total']

       

        # print(f'COunt{}')
        print(f'Four days total = {list(total)}')
        # daily = list(chain(last_three, today))
        print(f'TODAY = {today_items}')
        context = {
            'today_items': today_items,
            'today_total': today_total,
            'total': total,
            'time': time,
            'form': self.get_form_class()
        }
        return context




class SignupView(CreateView):
    template_name = 'register.html'
    form_class = UserRegistrationForm

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data.get('username')

        messages.success(self.request, f'User with username {username} is created!')
        return redirect('login')


class AddItemView(CreateView):
    model = Item
    fields = ['name', 'price']
    template_name = 'add_item.html'

    # success_url = reverse_lazy('items')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class UpdateItemView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Item
    fields = ['name', 'price']
    template_name = 'item_update.html'

    # success_url = reverse_lazy('items')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Item successfully deleted!")
        return super().form_valid(form)

    def test_func(self):
        item = self.get_object()
        if self.request.user == item.user:
            return True
        return False


class DeleteItemView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    template_name = 'item_delete.html'
    model = Item
    success_url = reverse_lazy('items')

    def test_func(self):
        item = self.get_object()
        if self.request.user == item.user:
            return True
        return False






