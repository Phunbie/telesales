from django.shortcuts import render
from django.contrib.auth.models import User
# Create your views here.
def home(request):
    users = User.objects.all()
    return render(request, 'index.html', {'users': users})

def signUp(request):
   if request.method == 'POST':
        # Get the user data from the request.
        username = request.POST.get('uname')
        role = request.POST.get('role')
        country = request.POST.get('country')
        angaza_id = request.POST.get('angaza')
        password = request.POST.get('psw')
        password2 = request.POST.get('psw2')

        # Validate the user data.
        if not username or not role or not country or not angaza_id or not password or not password2:
            return render(request, 'sign_up.html', {'error': 'Please fill in all the required fields.'})

        if password != password2:
            return render(request, 'sign_up.html', {'error': 'Passwords do not match.'})

        # Create a new User object.
        user = User.objects.create_user(username, password=password)

        # Add the user to the group.
        user.groups.add(Group.objects.get(name=role))

        # Create a new Employee object.
        employee = Employee(
            user=user,
            angaza_id=angaza_id,
            country=country,
        )

        # Save the employee object to the database.
        employee.save()
        print("saved")
        # Log in the user.
        login(request, user)
        print("logged in")

        # Redirect the user to the home page.
        return redirect('/')