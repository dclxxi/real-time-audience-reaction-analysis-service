# Create your views here.
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.db.models import Q, Max
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt

from live.models import Lecture
from report.models import Reaction


@login_required
def result(request, id):
    if request.method == 'GET':
        lecture = get_object_or_404(Lecture, pk=id)

        reactions = Reaction.objects.filter(lecture=lecture).order_by('time')
        reactions_json = serialize('json', reactions,
                                   fields=('time', 'concentration', 'negative', 'neutral', 'positive'))

        feedbacks = [reaction.feedback.content for reaction in reactions if reaction.feedback is not None]

        max_time = reactions.aggregate(Max('time'))['time__max']
        time_diff = max_time if max_time else elapsed_time(lecture.start_time, lecture.end_time)

        context = {
            'lecture': lecture,
            'feedbacks': feedbacks,
            'reactions_json': reactions_json,
            'time_diff': time_diff,
        }

        return render(request, 'report/report_page.html', context)

    if request.method == 'POST':
        pass


def elapsed_time(start_time, end_time):
    if start_time and end_time:
        start_time = datetime.combine(datetime.today(), start_time)
        end_time = datetime.combine(datetime.today(), end_time)
        elapsed_time = end_time - start_time

        return round(elapsed_time.total_seconds() / 60, 2)

    return 0


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

        return render(request, 'report/storage_list.html', context)

    if request.method == 'POST':
        pass


@csrf_exempt
def delete_lecture(request):
    if request.method == "GET":
        pass

    if request.method == "POST":
        lecture_id = request.POST.get("lecture_id", None)
        lecture = Lecture.objects.get(id=lecture_id)
        lecture.delete()
        return HttpResponse("delete complete")
