# biology_app/views.py

from rest_framework import viewsets, serializers, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Avg, Count, Q, F, Case, When, FloatField, Sum
from django.db import transaction
from django.conf import settings
import google.generativeai as genai

from .models import BiologyClass, Student, Test, Question, Standard, Comment, Score
from .serializers import (
    BiologyClassSerializer, StudentSerializer, TestSerializer, 
    QuestionSerializer, StandardSerializer, CommentSerializer, 
    StudentDetailSerializer, ScoreSerializer, TestListSerializer
)

class BiologyClassViewSet(viewsets.ModelViewSet):
    queryset = BiologyClass.objects.all()
    serializer_class = BiologyClassSerializer

    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        biology_class = self.get_object()
        latest_test = Test.objects.filter(assigned_class=biology_class).order_by('-date_administered').first()
        students_in_class = Student.objects.filter(biology_class=biology_class).order_by('last_name', 'first_name')
        student_serializer = StudentDetailSerializer(students_in_class, many=True)
        if not latest_test:
            return Response({
                'class_info': BiologyClassSerializer(biology_class).data,
                'students': student_serializer.data,
                'summary': { "message": "No tests found for this class." }
            })
        students_performance = Student.objects.filter(
            biology_class=biology_class
        ).annotate(
            total_awarded=Sum('score__mark_awarded', filter=Q(score__question__test=latest_test)),
            total_possible=Sum('score__question__max_mark', filter=Q(score__question__test=latest_test)),
            percentage=Case(When(total_possible__gt=0, then=(F('total_awarded') * 100.0) / F('total_possible')), default=0.0, output_field=FloatField())
        ).order_by('-percentage')
        average_data = students_performance.aggregate(avg_percent=Avg('percentage'))
        average_score_percentage = round(average_data['avg_percent'] or 0, 2)
        red_flag_count = students_performance.filter(percentage__lt=70).count()
        bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        labels = [f"{bins[i]}-{bins[i+1]}%" for i in range(len(bins)-1)]
        histogram_counts = {label: 0 for label in labels}
        for student in students_performance:
            percentage = student.percentage
            for i in range(len(bins) - 1):
                if bins[i] <= percentage < bins[i+1] or (i == len(bins) - 2 and percentage == 100):
                    histogram_counts[labels[i]] += 1
                    break
        histogram_data = {'labels': list(histogram_counts.keys()), 'data': list(histogram_counts.values())}
        summary_payload = {
            "latest_test_title": latest_test.title,
            "test_file_link": latest_test.test_file_link,
            "average_score_percentage": average_score_percentage,
            "red_flag_count": red_flag_count,
            "histogram_data": histogram_data
        }
        response_data = {
            'class_info': BiologyClassSerializer(biology_class).data,
            'students': student_serializer.data,
            'summary': summary_payload
        }
        return Response(response_data)

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all().order_by('last_name', 'first_name')
    serializer_class = StudentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['=biology_class__id']

    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        student = self.get_object()
        comments = student.comments.order_by('-created_at')
        comment_serializer = CommentSerializer(comments, many=True)
        standards_performance = Standard.objects.filter(questions__score__student=student).distinct().annotate(total_awarded=Sum('questions__score__mark_awarded', filter=Q(questions__score__student=student)), total_possible=Sum('questions__max_mark', filter=Q(questions__score__student=student)), percentage=Case(When(total_possible__gt=0, then=(F('total_awarded') * 100.0) / F('total_possible')), default=0.0, output_field=FloatField())).values('id', 'unit', 'code', 'description', 'percentage')
        response_data = {'student_info': StudentDetailSerializer(student).data, 'comments': comment_serializer.data, 'standards_performance': list(standards_performance)}
        return Response(response_data)

    @action(detail=False, methods=['post'])
    def generate_summary(self, request):
        student_info = request.data.get('student_info', {})
        standards_performance = request.data.get('standards_performance', [])
        comments = request.data.get('comments', [])
        if not student_info:
            return Response({'error': 'Missing student data.'}, status=status.HTTP_400_BAD_REQUEST)
        prompt = f"""
        You are an expert, insightful, and encouraging high school biology teaching assistant.
        Your task is to provide a diagnostic summary for a teacher about a student's performance.
        The summary should be structured, clear, and provide actionable suggestions.

        **Student:** {student_info.get('first_name')} {student_info.get('last_name')}

        **Quantitative Data (Mastery on Standards):**
        """
        if standards_performance:
            for standard in standards_performance:
                prompt += f"- {standard.get('code')} ({standard.get('unit')}): {round(standard.get('percentage', 0))}% mastery\n"
        else:
            prompt += "- No quantitative performance data available.\n"
        prompt += "\n**Qualitative Data (Teacher's Comments):**\n"
        if comments:
            for comment in comments:
                prompt += f"- {comment.get('text')}\n"
        else:
            prompt += "- No teacher comments available.\n"
        prompt += """
        **Instructions:**
        Based on all the data above, generate a diagnostic report with the following three sections.
        Use markdown for formatting (bold headings).

        **1. Areas of Strength:**
        Identify 1-2 key units or concepts where the student is demonstrating strong understanding (high scores). Be specific.

        **2. Areas for Improvement:**
        Identify 1-2 specific units or concepts where the student is struggling (low scores). If there are relevant teacher comments, connect them to the quantitative data.

        **3. Suggested Next Steps:**
        Provide 2-3 concrete, actionable suggestions for the teacher to help this student. These could include targeted review activities, different teaching strategies, or specific topics to revisit.
        """
        try:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            response = model.generate_content(prompt)
            summary_text = response.text
            return Response({'summary': summary_text})
        except Exception as e:
            print(f"Google AI API error: {e}")
            return Response({'error': 'Failed to generate summary due to a Google API error.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def generate_comment(self, request):
        student_info = request.data.get('student_info', {})
        standards_performance = request.data.get('standards_performance', [])
        if not student_info:
            return Response({'error': 'Missing student data.'}, status=status.HTTP_400_BAD_REQUEST)
        prompt = f"""
        You are a professional and encouraging high school biology teacher.
        Your task is to write a 3-sentence report card comment for a student.

        **Student Name:** {student_info.get('first_name')} {student_info.get('last_name')}

        **Performance Data (Mastery on Standards):**
        """
        if standards_performance:
            for standard in standards_performance:
                prompt += f"- {standard.get('code')} ({standard.get('unit')}): {round(standard.get('percentage', 0))}% mastery\n"
        else:
            prompt += "- No performance data available.\n"
        prompt += """
        **Instructions:**
        Based on the data, write a 3-sentence comment with the following structure:
        1. Start with a general, positive description of the student's engagement or progress.
        2. Mention one specific area of strength (a high-scoring unit or concept) and one specific area for improvement (a low-scoring unit or concept), referencing the competency code if possible.
        3. End with an encouraging remark about their potential or next steps.
        The tone must be professional, supportive, and concise.
        """
        try:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            response = model.generate_content(prompt)
            comment_text = response.text.strip()
            return Response({'comment': comment_text})
        except Exception as e:
            print(f"Google AI API error: {e}")
            return Response({'error': 'Failed to generate comment due to an API error.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['=assigned_class__id']
    def get_serializer_class(self):
        if self.action == 'list':
            return TestListSerializer
        return TestSerializer
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def bulk_score_entry(self, request, pk=None):
        scores_data = request.data.get('scores', {})
        for student_id, question_scores in scores_data.items():
            for question_id, mark in question_scores.items():
                if mark is not None and mark != '':
                    Score.objects.update_or_create(student_id=student_id, question_id=question_id, defaults={'mark_awarded': int(mark)})
        return Response({'status': 'Scores updated successfully'}, status=status.HTTP_200_OK)
    @action(detail=True, methods=['get'])
    def scores(self, request, pk=None):
        test = self.get_object()
        existing_scores = Score.objects.filter(question__test=test)
        serializer = ScoreSerializer(existing_scores, many=True)
        return Response(serializer.data)

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class StandardViewSet(viewsets.ModelViewSet):
    queryset = Standard.objects.all().order_by('code')
    serializer_class = StandardSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    all_classes = BiologyClass.objects.all().order_by('name')
    class_averages = []
    for bio_class in all_classes:
        latest_test = Test.objects.filter(assigned_class=bio_class).order_by('-date_administered').first()
        if latest_test:
            avg_data = Score.objects.filter(
                question__test=latest_test
            ).aggregate(
                avg_percent=Avg(
                    (F('mark_awarded') * 100.0) / F('question__max_mark'),
                    output_field=FloatField()
                )
            )
            average_score = round(avg_data.get('avg_percent') or 0, 1)
        else:
            average_score = 0
        class_averages.append({
            'class_name': bio_class.name,
            'average_score': average_score
        })
    chart_data = {
        'labels': [item['class_name'] for item in class_averages],
        'data': [item['average_score'] for item in class_averages]
    }
    response_data = {
        'class_performance_chart': chart_data
    }
    return Response(response_data)