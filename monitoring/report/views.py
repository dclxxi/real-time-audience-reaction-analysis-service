# Create your views here.
from django.shortcuts import get_object_or_404, render

from live.models import Lecture
from report.models import Reaction, Feedback


def result(request, id):
    if request.mehtod == 'GET':
        lecture = get_object_or_404(Lecture, pk=id)

        reactions = Reaction.objects.filter(lecture=lecture)
        feedback = Feedback.objects.get(lecture=lecture)

        context = {
            'reactions': reactions,
            'feedback': feedback.content,
        }

        return render(request, 'result.html', context)

    if request.method == 'POST':
        pass
