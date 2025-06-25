from django.shortcuts import render, redirect
from .models import (
Student, 
CustomUser,
 Document, 
 Hod, 
 Hostel,
Exam_and_record,
Library, 
Sport_director, 
Student_affair,
Sug,
Statement_Result,
Review

) 

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as log, logout
from django.contrib import messages
from .forms import StudentForm
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import redirect, get_object_or_404

import os
from django.core.files import File
from PIL import Image
from io import BytesIO
import os
from django.core.files import File
from django.utils import timezone   
from django.core.mail import send_mail
from django.conf import settings

from .models import Announcement
from .forms import AnnouncementForm





from .models import Hod, Sug, Sport_director, Library, Hostel, Student_affair, Exam_and_record
from .forms import (
    HodForm, SugForm, SportDirectorForm, LibraryForm, 
    HostelForm, StudentAffairForm, ExamAndRecordForm
)





def remove_signature_from_document(doc):
    """
    Function to remove the signature from the document by restoring the original file.
    This assumes the signed document has a prefix 'signed_' and the original document is backed up.
    """
    try:
        # Assuming the signed document has 'signed_' prefix
        original_file_path = doc.file.path.replace("signed_", "")
        
        # Check if the original document exists
        if os.path.exists(original_file_path):
            with open(original_file_path, "rb") as f:
                # Restore the original file
                doc.file.save(os.path.basename(original_file_path), File(f), save=True)
                return "Signature removed and original document restored."
        else:
            return "Original document not found. Signature not removed."
    except Exception as e:
        return f"Error removing signature: {e}"




def attach_signature(doc, profile):
    base_img_path = doc.file.path
    base_img = Image.open(base_img_path).convert("RGBA")

    signature_path = profile.signature.path
    signature = Image.open(signature_path).convert("RGBA")

    # Resize signature
    max_width = 150
    if signature.width > max_width:
        ratio = max_width / signature.width
        signature = signature.resize((int(signature.width * ratio), int(signature.height * ratio)))

    # Position bottom-right
    base_w, base_h = base_img.size
    sig_w, sig_h = signature.size
    position = (base_w - sig_w - 10, base_h - sig_h - 10)

    # Paste signature
    base_img.paste(signature, position, signature)

    # Save to in-memory buffer
    buffer = BytesIO()
    base_img.convert("RGB").save(buffer, format="JPEG")
    buffer.seek(0)

    # Generate new filename
    original_filename = os.path.basename(base_img_path)
    new_filename = f"signed_{original_filename}"

    # Save as new file object and update model
    doc.file.save(new_filename, File(buffer), save=True)



@login_required(login_url="login")
def dashboard(request):
    if request.user.position == "student":
        profile = Student.objects.get(user = request.user)
      
        return render(request, 'dashboard/dashboard.html', context = {"profile" : profile})
    

    
    elif request.user.position == "hod":
        profile = Hod.objects.get(user = request.user)
      
        return render(request, 'dashboard/dashboard.html', context = {"profile" : profile})
    

    elif request.user.position == "sport_director":
        profile = Sport_director.objects.get(user = request.user)
      
        return render(request, 'dashboard/dashboard.html', context = {"profile" : profile})
    

    elif request.user.position == "exams_records":
        profile = Exam_and_record.objects.get(user = request.user)
      
        return render(request, 'dashboard/dashboard.html', context = {"profile" : profile})
    

    elif request.user.position == "hostel":
        profile = Hostel.objects.get(user = request.user)
      
        return render(request, 'dashboard/dashboard.html', context = {"profile" : profile})
    

    elif request.user.position == "library":
        profile = Library.objects.get(user = request.user)
      
        return render(request, 'dashboard/dashboard.html', context = {"profile" : profile})
    

    elif request.user.position == "student_affair":
        profile = Student_affair.objects.get(user = request.user)
      
        return render(request, 'dashboard/dashboard.html', context = {"profile" : profile})
    

    elif request.user.position == "sug":
        profile = Sug.objects.get(user = request.user)
      
        return render(request, 'dashboard/dashboard.html', context = {"profile" : profile})
    
        
        
    return render(request, 'dashboard/dashboard.html', context = {"profile" : profile})





def register(request):
    return render(request, 'auth/register.html')






def upload_doc(request):

    if request.method == 'POST':
        title = request.POST['title']
        file = request.FILES['file']
        student = Student.objects.get(user=request.user)

        document = Document(
            title = title,
            file = file,
            student = student
        )

        document.save()
        messages.success(request, "Document Uploaded Successfully ")
        return redirect('upload_doc')

    return render(request, 'dashboard/upload_doc.html')




def remove_doc(request, doc_id):
    document = Document.objects.get(id=doc_id)
    document.delete()
    messages.success(request, "Document Deleted Successfully")
    return redirect('my_doc')



def my_doc(request):
    student = Student.objects.get(user=request.user)

    document = Document.objects.filter(student = student)

    context = {
        'documents': document
    }
    return render(request, 'dashboard/my_doc.html', context)






def send_doc(request):
    return render(request, 'base.html')






@login_required(login_url="login")
def student_doc(request):
    user = request.user
    form = StatementResultForm()


    # Get all distinct student IDs that have a document
    student_ids = Document.objects.values_list('student_id', flat=True).distinct()

    if user.position == "hod":
        # Get HOD's department (assuming it's stored in their profile)
        try:
            hod_profile = get_object_or_404(Hod, user=user)  # or whatever model stores their department
            students = Student.objects.filter(
                id__in=student_ids,
                department=hod_profile.department
            )
        except:
            messages.error(request, "Unable to find your department info.")
            students = Student.objects.none()
    else:
        # For other users (non-HODs), show all students with documents
        students = Student.objects.filter(id__in=student_ids)

    context = {
        'students': students,
        'form': form
    }

    return render(request, 'dashboard/student_doc.html', context)





def view_student_docs(request, student_id):
    student = Student.objects.get(id=student_id)
    documents = Document.objects.filter(student=student)

    context = {
        'student': student,
        'documents': documents
    }
    return render(request, 'dashboard/student_documents.html', context)









def approve_doc(request, doc_id, field):
    doc = get_object_or_404(Document, id=doc_id)
    profile, created = Student.objects.get_or_create(user=request.user)
    student_user = doc.student  # Assuming Document model has a ForeignKey to User as 'student'

    # Define readable names for fields
    field_names = {
        'hod_approved': 'HOD',
        'student_affair_approved': 'Student Affairs',
        'hostel_approved': 'Hostel Warden',
        'sug_approved': 'SUG',
        'library_approved': 'Library',
        'sport_director_approved': 'Sport Director',
        'Exam_and_record_approved': 'Exams & Records'
    }

    if field in field_names:
        setattr(doc, field, True)
        setattr(doc, f"{field}_by", request.user)
        doc.save()

        approver_title = field_names[field]
        subject = f"Approval of your document by {approver_title}"
        message = (
            f"Dear {student_user.user.username},\n\n"
            f"Your document titled '{doc.title}' has been approved by the {approver_title}.\n"
            f"Please log in to your dashboard to view the updated status.\n\n"
            "Best regards,\n"
            f"{approver_title} Office"
        )
        recipient = [student_user.user.email]

        # Send email only if user has an email set
        if student_user.user.email:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient, fail_silently=True)

        messages.success(request, f"{approver_title} Approval Successful.")
    else:
        messages.error(request, "Invalid approval field.")

    return redirect(request.META.get('HTTP_REFERER', '/'))








def disapprove_doc(request, doc_id, field):
    doc = get_object_or_404(Document, id=doc_id)
    student_user = doc.student.user  # Assuming `student` is a ForeignKey to `User` in Document model


    field_names = {
        'hod_approved': 'HOD',
        'student_affair_approved': 'Student Affairs',
        'hostel_approved': 'Hostel Warden',
        'sug_approved': 'SUG',
        'library_approved': 'Library',
        'sport_director_approved': 'Sport Director',
        'Exam_and_record_approved': 'Exams & Records'
    }

    if field in field_names:
        setattr(doc, field, False)
        setattr(doc, f"{field}_by", None)
        doc.save()

        approver_title = field_names[field]
        messages.success(request, f"{approver_title} disapproved the document.")

        # ✅ Send email notification
        if student_user.email:
            subject = f"Your Document Was Disapproved by {approver_title}"
            message = (
                f"Dear {student_user.get_full_name() or student_user.username},\n\n"
                f"Your document titled '{doc.title}' was reviewed and disapproved by the {approver_title}.\n"
                "Please log in to your portal to make the necessary corrections and resubmit.\n\n"
                "Best regards,\n"
                f"{approver_title} Office"
            )
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [student_user.email], fail_silently=True)
    else:
        messages.error(request, "Invalid approval field.")

    return redirect(request.META.get('HTTP_REFERER', '/'))









@login_required(login_url='login')
def profile(request):
    user = request.user
    position = user.position.lower()

    profile_model = {
        'hod': Hod,
        'sug': Sug,
        'sport_director': Sport_director,
        'library': Library,
        'hostel': Hostel,
        'student_affair': Student_affair,
        'exam_and_record': Exam_and_record,
    }.get(position)

    form_class = {
        'hod': HodForm,
        'sug': SugForm,
        'sport_director': SportDirectorForm,
        'library': LibraryForm,
        'hostel': HostelForm,
        'student_affair': StudentAffairForm,
        'exam_and_record': ExamAndRecordForm,
    }.get(position)

    if not profile_model or not form_class:
        return render(request, 'dashboard/profile.html', {'error': 'Unsupported role'})

    profile_instance = get_object_or_404(profile_model, user=user)

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=profile_instance, user=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
        else:
            return render(request, 'dashboard/profile.html', {'form': form, 'profile': profile_instance})
    else:
        form = form_class(instance=profile_instance, user=user)

    return render(request, 'dashboard/profile.html', {
        'form': form,
        'profile': profile_instance,
    })











@login_required
def student_profile(request):
    student, created = Student.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('student_profile')
        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        form = StudentForm(instance=student)

    return render(request, 'dashboard/student-profile.html', {'form': form, 'profile': student})




def login(request):
    if request.user.is_anonymous:
        if request.method == "POST":
                email = request.POST["email"].lower()
                password = request.POST["password"]
                try:
                    customuser = CustomUser.objects.get(email=email)
                    user = authenticate(username=customuser.username, password=password)  # Authenticate with email
                    if user is not None:
                        log(request, user)
                        messages.success(request, "Login successful!")
                        return redirect("dashboard")  # Redirect to home page or any other desired page
                    else:
                        messages.error(request, "Invalid email or password")
                except :
                    messages.error(request, "Invalid email or password")
                    return redirect('login')
    else:
        return redirect("dashboard")
    

    
   
    return render(request, 'auth/login.html')











def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')








@login_required(login_url="login")
def statement_result(request):
    # Only allow students to view their statement
    if request.user.position != "student":
        messages.error(request, "Only students can view their Statement of Result.")
        return redirect("dashboard")

    try:
        student_profile = get_object_or_404(Student, user=request.user)

        try:
            # Try to get the statement linked to the logged-in user
            statement = Statement_Result.objects.get(student=student_profile)

            context = {
                'statement': statement,
                'student_profile': student_profile,
                'results': [],  # Replace with real results if needed
                'today': statement.created,  # ✅ Use issued date from the model
                'not_generated': False
            }
            return render(request, 'dashboard/statement_result.html', context)

        except Statement_Result.DoesNotExist:
            # Statement not yet generated
            messages.info(request, "Your Statement of Result has not been generated yet.")
            context = {
                'statement': None,
                'student_profile': student_profile,
                'results': [],
                'today': None,  # No date since there's no statement
                'not_generated': True
            }
            return render(request, 'dashboard/statement_result.html', context)

    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect("dashboard")









from .forms import StatementResultForm



@login_required(login_url="login")
def create_statement_of_result(request, student_id):
    if request.user.position != "student_affair":
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('student_doc')

    student_profile = get_object_or_404(Student, id=student_id)
    student_user = student_profile.user

    if student_profile.overall_clearance_status != "Completely Approved":
        messages.error(
            request,
            f"Cannot generate Statement of Result. {student_user.username}'s clearance is still in progress."
        )
        return redirect('student_doc')

    if Statement_Result.objects.filter(student=student_profile).exists():
        messages.info(
            request,
            f"Statement of Result has already been generated for {student_user.username}."
        )
        return redirect('student_doc')

    if request.method == 'POST':
        form = StatementResultForm(request.POST)
        if form.is_valid():
            sor = form.save(commit=False)
            sor.student = student_profile
            sor.issued_by = request.user
            sor.signature_1 = getattr(student_profile, 'signature', None)
            sor.signature_2 = getattr(student_profile, 'signature', None)
            sor.save()

            messages.success(
                request,
                f"Statement of Result generated successfully for {student_user.username}."
            )

            # Send email
            if student_user.email:
                subject = "Your Statement of Result Has Been Generated"
                message = (
                    f"Dear {student_user.username},\n\n"
                    f"Your Statement of Result has been successfully generated.\n"
                    f"You can now log in to your dashboard to view or download it.\n\n"
                    "Best regards,\n"
                    "Student Affairs Office"
                )
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [student_user.email], fail_silently=True)
        else:
            messages.error(request, "Please correct the errors in the form.")
        
        return redirect('student_doc')

    return redirect('student_doc')









def send_review(request, doc_id):
    if request.method == "POST":
        doc = get_object_or_404(Document, id=doc_id)
        student_user = doc.student.user
        reviewer = request.user
        message = request.POST.get('message')
        reviewer_position = getattr(reviewer, 'position', 'Reviewer')

        # Save to Review model
        Review.objects.create(
            reviewer=reviewer,
            student=student_user,
            document=doc,
            message=message
        )

        # Prepare and send email
        subject = f"Feedback on your document from {reviewer_position}"
        email_body = (
            f"Dear {student_user.username},\n\n"
            f"You have received a review regarding your document titled '{doc.title}'.\n\n"
            f"Reviewer ({reviewer_position}) says:\n\n"
            f"{message}\n\n"
            "Please log in to your dashboard for further updates.\n\n"
            "Best regards,\n"
            f"{reviewer_position} Position"
        )

        if student_user.email:
            send_mail(subject, email_body, settings.DEFAULT_FROM_EMAIL, [student_user.email], fail_silently=True)
            messages.success(request, "Review sent and saved successfully.")
        else:
            messages.error(request, "Student has no email address on file.")

        return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        return redirect('/')














@login_required(login_url='login')
def statement_result_list(request):
    if request.user.position != 'student_affair':
        messages.error(request, "You do not have permission to view this page.")
        return redirect('dashboard')

    statements = Statement_Result.objects.select_related('student').all()
    return render(request, 'dashboard/statement_list.html', {'statements': statements})








@login_required(login_url='login')
def statement_result_detail(request, pk):
    statement = get_object_or_404(Statement_Result, pk=pk)
    student_profile = statement.student  # already a Student instance

    return render(request, 'dashboard/statement_preview.html', {
        'statement': statement,
        'student_profile': student_profile,
        'today': statement.created,
    })












@login_required(login_url="login")
def send_announcement(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.sender_position = request.user.position
            announcement.save()

            recipients = []

            if request.user.position == 'hod':
                try:
                    # Assuming you have a Hod model with department FK
                    hod_profile = request.user.hod  # replace if your related name is different
                    dept_students = Student.objects.filter(department=hod_profile.department)
                    recipients = [student.user for student in dept_students]
                except Exception as e:
                    messages.error(request, "Could not determine your department.")
                    recipients = []

            else:
                # Everyone else (e.g. student_affair) gets all students
                recipients = [student.user for student in Student.objects.all()]

            # Save recipients
            announcement.recipients.set(recipients)

            # Send emails
            for user in recipients:
                if user.email:
                    send_mail(
                        subject=announcement.title,
                        message=announcement.message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=True,
                    )

            messages.success(request, "Announcement sent successfully.")
            return redirect('dashboard')

    else:
        form = AnnouncementForm()

    return render(request, 'dashboard/send_announcement.html', {'form': form})