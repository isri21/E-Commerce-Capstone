import os
import django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from authenticate.models import User
from store.models import Purchase
from django.db.models import Count, Case, When, F, Sum, DecimalField
from django.db.models.functions import Cast
user = User.objects.get(username="root")
print(user.money_spent)
print(user.money_earned)
