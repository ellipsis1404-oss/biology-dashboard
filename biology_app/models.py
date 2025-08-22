# biology_app/models.py
from django.db import models

# Represents a class, e.g., "Year 9 (iCGSE)"
class BiologyClass(models.Model):
    name = models.CharField(max_length=100, unique=True) # e.g., "Year 9 (iCGSE)"
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

# Represents a single student
class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    # The ForeignKey links a Student to a BiologyClass. If a class is deleted, all its students are also deleted.
    biology_class = models.ForeignKey(BiologyClass, related_name='students', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.biology_class.name})"

# Represents a skill or standard, e.g., "Cellular Respiration"
# biology_app/models.py

# ... (other models like BiologyClass, Student should be above this) ...

# Represents a skill or standard, e.g., "Cellular Respiration"
class Standard(models.Model):
    # Define choices for the level
    LEVEL_CHOICES = [
        ('IGCSE', 'IGCSE'),
        ('AS', 'AS Level'),
        ('A2', 'A Level'),
    ]

    level = models.CharField(max_length=5, choices=LEVEL_CHOICES)
    unit = models.CharField(max_length=100) # e.g., "Unit 1: Cell Biology"
    code = models.CharField(max_length=20, unique=True) # e.g., "1.1a", unique=True ensures no duplicate codes
    description = models.TextField() # e.g., "Understand the process of cellular respiration"

    def __str__(self):
        # A much more descriptive name when we see it in the admin panel
        return f"{self.code} ({self.level}) - {self.description[:50]}..."

# ... (other models like Test, Question should be below this) ...

# Represents a test or assessment
class Test(models.Model):
    title = models.CharField(max_length=200)
    date_administered = models.DateField()
    # A test is assigned to a specific class
    assigned_class = models.ForeignKey(BiologyClass, related_name='tests', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} for {self.assigned_class.name}"

# Represents a single question within a test
class Question(models.Model):
    test = models.ForeignKey(Test, related_name='questions', on_delete=models.CASCADE)
    question_text = models.CharField(max_length=255)
    max_mark = models.PositiveIntegerField()
    # A question can assess multiple standards (Many-to-Many relationship)
    standards = models.ManyToManyField(Standard, related_name='questions')

    def __str__(self):
        return f"Q: {self.question_text} ({self.test.title})"

# Represents a student's score on a specific question
class Score(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    mark_awarded = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.student} | {self.question} | Score: {self.mark_awarded}/{self.question.max_mark}"

# Represents comments about a student
class Comment(models.Model):
    student = models.ForeignKey(Student, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment for {self.student} on {self.created_at.strftime('%Y-%m-%d')}"
    