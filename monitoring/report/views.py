# Create your views here.
from django.shortcuts import get_object_or_404, render

from live.models import Lecture
from report.models import Reaction, Feedback


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


def list(request):
    if request.method == 'GET':
        lectures = Lecture.objects.filter(user=request.user)

        context = {
            'lectures': lectures,
        }

        return render(request, 'list.html', context)

    if request.method == 'POST':
        pass
