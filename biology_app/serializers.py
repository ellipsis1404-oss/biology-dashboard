# biology_app/serializers.py

from rest_framework import serializers
from .models import BiologyClass, Student, Test, Question, Standard, Comment, Score

class BiologyClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiologyClass
        fields = ['id', 'name', 'description']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'first_name', 'last_name', 'biology_class']

# --- Standard Serializer ---
class StandardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Standard
        fields = '__all__'

# --- Question Serializer ---
class QuestionSerializer(serializers.ModelSerializer):
    standards = serializers.PrimaryKeyRelatedField(queryset=Standard.objects.all(), many=True)
    
    class Meta:
        model = Question
        fields = ['id', 'test', 'question_number', 'question_text', 'max_mark', 'standards']

class TestListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        # This simple version only includes basic fields for the list view
        fields = ['id', 'title', 'date_administered', 'assigned_class', 'test_file_link']

# --- Test Serializer ---
class TestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Test
        fields = ['id', 'title', 'date_administered', 'assigned_class', 'questions', 'test_file_link']

# --- Comment Serializer ---
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'text', 'created_at', 'student']

# --- Student Detail Serializer (for modals) ---
class StudentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'first_name', 'last_name']

class ScoreSerializer(serializers.ModelSerializer):
    # We only need the IDs for student and question to map the scores on the frontend.
    student = serializers.ReadOnlyField(source='student.id')
    question = serializers.ReadOnlyField(source='question.id')

    class Meta:
        model = Score
        fields = ['student', 'question', 'mark_awarded']