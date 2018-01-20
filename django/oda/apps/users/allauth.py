from __future__ import absolute_import
from allauth.account.adapter import DefaultAccountAdapter
from django import forms
import logging

__author__ = 'davis'

logger = logging.getLogger(__name__)

class AccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        return "/odaweb/"

class SignupForm(forms.Form):
    def signup(self, request, user):
        logger.info("creating user")
        user.save()