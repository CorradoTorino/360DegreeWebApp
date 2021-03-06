from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

import uuid

class Survey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_name = models.CharField(max_length=100, blank=True, default='')
    employee_last_name = models.CharField(max_length=100, blank=True, default='')
    employee_email = models.EmailField(max_length=100)
    
    @classmethod
    def create(cls, name, lastName, email):
        instance = cls(employee_name=name, employee_last_name=lastName, employee_email=email)
        instance.save()
        return instance
        
    def __str__(self):
        return '{} {}'.format(self.employee_name, self.employee_last_name)
    
class RelationType(models.Model):
    relation_type = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    
    @classmethod
    def create(cls, relation_type, description, survey):
        instance = cls(relation_type=relation_type, description=description, survey=survey)
        instance.save()
        return instance
    
    def __str__(self):
        return '{}'.format(self.relation_type, self.description) 
    
class FeedbackProvider(models.Model):
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, default='')
    email = models.EmailField(max_length=100)
    relation_type = models.ForeignKey(RelationType, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
        
    @classmethod
    def create(cls, name, last_name, email, relation_type, survey):
        instance = cls(name=name, last_name=last_name, email=email, relation_type=relation_type, survey=survey)
        instance.save()
        return instance
    
    def __str__(self):
        return '{} {} ({})'.format(self.name, self.last_name, self.email)
    
    class Meta:
        unique_together = (("survey", "email"),)

class QuestionSection(models.Model):
    description = models.CharField(max_length=100)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
        
    def __str__(self):
        return self.description

    class Meta:
        unique_together = (
            ("survey", "description"),
            ("survey", "order")
            )
    
class Question(models.Model):
    text = models.CharField(max_length=200)
    section = models.ForeignKey(QuestionSection, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)

    MULTICHOICE = 0
    OPEN = 1

    ANSWER_TYPE = (
        (MULTICHOICE, 'MultiChoice'),
        (OPEN, 'Open'),
    )
    
    answer = models.IntegerField( choices=ANSWER_TYPE, default=MULTICHOICE)

    def __str__(self):
        return '{}: {}'.format(self.section, self.text)
    
    class Meta:
        unique_together = (
            ("section", "order"),
            ("section", "text")
            )

class MultiChoiceAnswer(models.Model):
    feedback_provider = models.ForeignKey(FeedbackProvider, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    
    NEVER = 0
    RARELY = 1
    SOMETIMES = 2
    OFTEN = 3
    ALWAYS = 4

    ANSWER_CHOICES = (
        (NEVER, 'Never'),
        (RARELY, 'Rarely'),
        (SOMETIMES, 'Sometimes'),
        (OFTEN, 'Often'),
        (ALWAYS, 'Always'),
    )
    
    answer = models.IntegerField( choices=ANSWER_CHOICES, default=NEVER)
    
    @classmethod
    def create(cls, feedback_provider, question, answer=NEVER):
        instance = cls(feedback_provider=feedback_provider, question=question, answer=answer)
        instance.save()
        return instance             
    
    def __str__(self):
        return '{} {}'.format(self.question, self.ANSWER_CHOICES[self.answer][1])
    
    class Meta:
        unique_together = (("feedback_provider", "question"),)

class OpenAnswer(models.Model):
    feedback_provider = models.ForeignKey(FeedbackProvider, on_delete=models.CASCADE)    
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=1000, blank=True, default='')
            
    @classmethod
    def create(cls, feedback_provider, question, answer=''):
        instance = cls(feedback_provider=feedback_provider, question=question, answer=answer)
        instance.save()
        return instance     
    
    def __str__(self):
        return '{}...'.format(self.answer[0:50])

#Signals and Methods to ensure consistency in the models
def createAnswer(feedbackProvider, question):
    
    answerClass = MultiChoiceAnswer 
        
    if(question.answer == Question.OPEN):
        answerClass = OpenAnswer
    
    if(answerClass.objects.filter(feedback_provider = feedbackProvider, question = question).count() == 0):
        answerClass.create(feedbackProvider, question)   
    
@receiver(post_save, sender=Question, dispatch_uid="createAnswersWhenNewQuestionIsSaved")
def createAnswersWhenNewQuestionIsSaved(sender, instance, **kwargs):

    for feedbackProvider in FeedbackProvider.objects.filter(survey = instance.section.survey):
        createAnswer(feedbackProvider, question = instance)

@receiver(post_save, sender=FeedbackProvider, dispatch_uid="createAnswersWhenNewFeedbackProviderIsSaved")
def createAnswersWhenNewFeedbackProviderIsSaved(sender, instance, **kwargs):   

    for question in Question.objects.filter(section__survey = instance.survey):
        createAnswer(feedbackProvider = instance, question = question)
