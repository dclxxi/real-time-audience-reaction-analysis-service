# Create your views here.
import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt

from live.models import Lecture
from report.models import Reaction


@login_required
def result(request, id):
    if request.method == 'GET':
        lecture = get_object_or_404(Lecture, pk=id)
        reactions = Reaction.objects.filter(lecture=lecture).order_by('time')

        reactions_with_feedbacks = [
            {
                'time': reaction.time,
                'concentration': reaction.concentration,
                'negative': reaction.negative,
                'neutral': reaction.neutral,
                'positive': reaction.positive,
                'feedback': escape_control_characters(reaction.feedback.content) if reaction.feedback else '피드백이 없습니다.',
            }
            for reaction in reactions
        ]

        reactions_json = json.dumps(reactions_with_feedbacks, ensure_ascii=False)
        time_diff = calculate_elapsed_time(lecture.start_time, lecture.end_time)

        context = {
            'lecture': lecture,
            'reactions_json': reactions_json,
            'time_diff': time_diff,
        }

        return render(request, 'report/report_page.html', context)

    if request.method == 'POST':
        pass


def escape_control_characters(s):
    if not isinstance(s, str):
        return ''

    return s.translate(str.maketrans({
        '\b': '\\b',
        '\f': '\\f',
        '\n': '\\n',
        '\r': '\\r',
        '\t': '\\t',
    }))


def calculate_elapsed_time(start_time, end_time):
    if start_time and end_time:
        start_time = datetime.combine(datetime.today(), start_time)
        end_time = datetime.combine(datetime.today(), end_time)
        time_diff = end_time - start_time

        return round(time_diff.total_seconds() / 60)

    return 0


@login_required
def list_lectures(request):
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        page_number = request.GET.get('page', 1)

        lectures_query = (Lecture.objects
                          .filter(Q(user=request.user), Q(topic__icontains=search_query))
                          .order_by('-datetime').distinct())

        paginator = Paginator(lectures_query, 10)

        try:
            lectures = paginator.page(page_number)
        except PageNotAnInteger:
            lectures = paginator.page(1)
        except EmptyPage:
            lectures = paginator.page(paginator.num_pages)

        context = {'lectures': lectures}
        return render(request, 'report/storage_list.html', context)


@csrf_exempt
def delete_lecture(request):
    if request.method == "POST":
        lecture_id = request.POST.get("lecture_id")
        if not lecture_id:
            return JsonResponse({'error': 'No lecture ID provided'}, status=400)

        lecture = get_object_or_404(Lecture, id=lecture_id, user=request.user)
        lecture.delete()

        return JsonResponse({'message': 'Lecture deleted successfully'})
