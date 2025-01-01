import os
import django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from account.models import Review

reviews = Review.objects.all()
for review in reviews:
	review.review_at = str(review.review_at)
