from django.shortcuts import render

from .models import Policy

def index(request):
	try:
		policy = Policy.objects.order_by('-pk').filter(is_active=True)[:1].get()
	except Policy.DoesNotExist:
		policy = None

	return render(request, 'policy/index.html', {'policy': policy})
