from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Question, Choice
from django.template import loader

# Using F to avoid race conditions
from django.db.models import F

# Create your views here.

def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    template = loader.get_template("polls/index.html")
    context= { "latest_question_list": latest_question_list}
    return HttpResponse(template.render(context, request))

def detail(request, question_id):
    # Traditionnal try catch structure
    # try:
    #     question = Question.objects.get(pk=question_id)
    # except Question.DoesNotExist:
    #     raise Http404("Question does not exist")

    # Handy built-in shortcut:
    question = get_object_or_404(Question, pk=question_id)
    # Another way to send back a HttpResponse with a shortcut
    return render(request, "polls/detail.html", { "question": question})

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/results.html", {"question": question})

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request, 
            "polls/detail.html",
            {
                "question": question,
                "error_mesage": "You didn't select a choice.",
            },
        )
    else:
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        # Introducing F for dealing with race conditions (in case of simultaneus POST requests)
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
    return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))