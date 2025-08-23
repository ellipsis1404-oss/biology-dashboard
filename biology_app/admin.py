# biology_app/admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
import pandas as pd
from .models import BiologyClass, Student, Standard, Test, Question, Score, Comment
from .forms import StandardUploadForm

@admin.register(Standard)
class StandardAdmin(admin.ModelAdmin):
    list_display = ('code', 'level', 'chapter', 'chapter_order', 'unit', 'unit_order', 'description')
    list_filter = ('level', 'chapter', 'unit') # Adds filters on the right side
    search_fields = ('code', 'description', 'unit','chapter') # Adds a search bar

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('upload-excel/', self.upload_excel),
        ]
        return my_urls + urls

    # This is the view that will handle the upload
    def upload_excel(self, request):
        if request.method == "POST":
            form = StandardUploadForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file = request.FILES["file"]
                try:
                    # Check the file extension to decide which pandas function to use
                    if uploaded_file.name.endswith('.xlsx'):
                        df = pd.read_excel(uploaded_file)
                    elif uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                    else:
                        # If the file is not an excel or csv, show an error
                        self.message_user(request, "Unsupported file format. Please upload a .xlsx or .csv file.", level=messages.ERROR)
                        return redirect(".") # Redirect back to the upload page
                    
                    # Loop through each row in the DataFrame
                    for index, row in df.iterrows():
                        # Use update_or_create to avoid duplicates based on the 'code'
                        Standard.objects.update_or_create(
                            level=row['level'],
                            code=row['code'],
                            defaults={
                                'chapter': row['chapter'],
                                'chapter_order': row['chapter_order'],                              
                                'unit': row['unit'],
                                'unit_order': row['unit_order'],
                                'description': row['description'],
                            }
                        )
                    
                    # Send a success message to the user
                    self.message_user(request, "Standards have been successfully uploaded.")
                    return redirect("..") # Redirect back to the standards list
                except Exception as e:
                    # If there's an error, show it to the user
                    self.message_user(request, f"Error uploading file: {e}", level=messages.ERROR)
            
        form = StandardUploadForm()
        context = {"form": form}
        return render(request, "admin/standard_upload.html", context)

admin.site.register(BiologyClass)
admin.site.register(Student)
admin.site.register(Test)
admin.site.register(Question)
admin.site.register(Score)
admin.site.register(Comment)