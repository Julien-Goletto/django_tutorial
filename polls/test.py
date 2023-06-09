import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

# Unit tests
class QuestionModelTests(TestCase):
    def test_was_published_recently_with_old_question(self):
        # was_published_recently() returns False for questions whose pub_date is older than 1 day
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_future_question(self):
        # was_published_recently() returns False for questions whose pub_date is in the future
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)
    
    def test_was_published_recently_with_recent_question(self):
        # was_published_recently() returns True for questions whose pub_date is within the last day
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

# Utilitary for question creation
def create_question(question_text, days):
    """
    Create a question with the given question_text 
    and published the given number of days offset to now (either negative or positive)
    """

    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

# Testing index view
class QuestionIndexViewTests(TestCase):
    def test_no_question(self):
        # If no question exist, an appropriate message is displayed
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])
    
    def test_past_question(self):
        # Questions with a pub_date in the past are displayed on the index page
        question = create_question("Past question", -2)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [question])

    def test_future_question(self):
        # Questions with a pub_date in the future are not displayed on the index page
        question = create_question("Future question", 2)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        # Even if both past and future questions exist, only past questions are displayed.
        past_question = create_question("Past question.", -30)
        create_question("Future question.", 30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [past_question],
        )

    def test_future_question_and_past_question(self):
        # Two past questions are displayed.
        past_question_1 = create_question("Past question 1.", -3)
        past_question_2 = create_question("Past question 2.", -30)
        create_question("Future question.", 30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [past_question_1, past_question_2],
        )
  
# Testing detail view
class QuestionDetailViewTests(TestCase):
  def test_future_question(self):
      # Returns a 404 on future questions
      future_question = create_question("Future question", 2)
      response = self.client.get(reverse("polls:detail", args=(future_question.id,)))
      self.assertEqual(response.status_code, 404)
  
  def test_past_question(self):
      # Displays the detail page for a past question, containing its question_text
      past_question_text = "Past question"
      past_question = create_question(past_question_text, -2)
      response = self.client.get(reverse("polls:detail", args=(past_question.id,)))
      self.assertEqual(response.status_code, 200)
      self.assertContains(response, past_question_text)