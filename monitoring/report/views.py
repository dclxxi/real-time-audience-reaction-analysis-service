# Create your views here.
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from live.models import Lecture
from report.models import Reaction, Feedback


@login_required
def result(request, id):
    if request.method == 'GET':
        lecture = get_object_or_404(Lecture, pk=id)

        reactions = Reaction.objects.filter(lecture=lecture)
        feedback = Feedback.objects.get(lecture=lecture)

        context = {
            'lecture': lecture,
            'reactions': reactions,
            'feedback': feedback.content,
        }

        return render(request, 'result.html', context)

    if request.method == 'POST':
        pass


@login_required
def list(request):
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        page_number = request.GET.get('page', 1)

        lectures = (Lecture.objects
                    .filter(Q(user=request.user), Q(topic__icontains=search_query))
                    .order_by('-datetime')
                    .distinct()
                    )

        paginator = Paginator(lectures, 10)
        page_obj = paginator.get_page(page_number)

        context = {
            'lectures': page_obj,
        }

        return render(request, 'lecture_list.html', context)

    if request.method == 'POST':
        pass
