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

class Standard(models.Model):
    LEVEL_CHOICES = [
        ('IGCSE', 'IGCSE'),
        ('AS', 'AS Level'),
        ('A2', 'A Level'),
    ]

    level = models.CharField(max_length=5, choices=LEVEL_CHOICES)
    
    # --- NEW: Fields for ordering and grouping ---
    chapter = models.CharField(max_length=100) # e.g., "Chapter 1: Cell Structure"
    chapter_order = models.PositiveIntegerField(default=0) # A number to sort chapters by, e.g., 1
    
    unit = models.CharField(max_length=100)
    unit_order = models.PositiveIntegerField(default=0) # A number to sort units within a chapter
    
    # --- MODIFIED: 'code' is no longer unique by itself ---
    code = models.CharField(max_length=20) 
    
    description = models.TextField()

    class Meta:
        # --- NEW: This is the correct uniqueness rule ---
        # It allows ('IGCSE', '1.1.1') and ('AS', '1.1.1') to coexist.
        unique_together = ('level', 'code')
        
        # --- NEW: This enforces the correct sorting order everywhere ---
        ordering = ['level', 'chapter_order', 'unit_order', 'code']

    def __str__(self):
        return f"{self.code} ({self.level}) - {self.description[:50]}..."

class TestManager(models.Manager):
    def get_queryset(self):
        # By default, only return tests that are not archived.
        return super().get_queryset().filter(is_archived=False)

# Represents a test or assessment
class Test(models.Model):
    title = models.CharField(max_length=200)
    date_administered = models.DateField()
    assigned_class = models.ForeignKey(BiologyClass, related_name='tests', on_delete=models.CASCADE)
    test_file_link = models.URLField(max_length=500, blank=True, null=True)
    
    # --- NEW: The soft-delete flag ---
    is_archived = models.BooleanField(default=False)

    # --- NEW: Connecting our managers ---
    objects = TestManager() # The default manager only sees active tests.
    all_objects = models.Manager() # A second manager to see ALL tests.

    def __str__(self):
        return f"{self.title} for {self.assigned_class.name}"

# Represents a single question within a test
class Question(models.Model):
    test = models.ForeignKey(Test, related_name='questions', on_delete=models.CASCADE)
    question_number = models.PositiveIntegerField()
    question_text = models.CharField(max_length=255)
    max_mark = models.PositiveIntegerField()
    # A question can assess multiple standards (Many-to-Many relationship)
    standards = models.ManyToManyField(Standard, related_name='questions')

    class Meta:
        # --- ADD THIS META CLASS ---
        # This ensures questions are always ordered by their number
        ordering = ['question_number']

    def __str__(self):
        return f"Q{self.question_number}: {self.question_text} ({self.test.title})"

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
    