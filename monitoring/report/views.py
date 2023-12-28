# Create your views here.
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt

from live.models import Lecture
from report.models import Reaction, Feedback


@login_required
def result(request, id):
    if request.method == 'GET':
        lecture = get_object_or_404(Lecture, pk=id)

        reactions = Reaction.objects.filter(lecture=lecture)
        reaction_feedbacks = [(reaction, Feedback.objects.filter(reaction=reaction).first()) for reaction in reactions]

        context = {
            'lecture': lecture,
            'reaction_feedbacks': reaction_feedbacks,
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


@csrf_exempt
def delete_lecture(request):
    if request.method == "GET":
        pass
    if request.method == "POST":
        lecture_id = request.POST.get("lecture_id", None)
        lecture = Lecture.objects.get(id=lecture_id)
        lecture.delete()
        return HttpResponse("delete complete")
