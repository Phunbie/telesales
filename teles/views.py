from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate, logout
from .models import Agent
from django.contrib import messages




def home(request):
    users = User.objects.all()
    return render(request, 'index.html', {'users': users})

def dashboard(request):
    return render(request, 'dashboard.html')


def signOut(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request,f'You have been logged out.')
        return redirect('home')   
    
def logIn(request):
    if request.method == 'POST':
        username = request.POST.get('uname')
        password = request.POST.get('psw')
        user = authenticate(request,username=username,password=password)
        if user:
            login(request, user)
            messages.success(request,f'Hi, welcome back!')
            print('Hi, welcome back!')
            return redirect('home')
        messages.success(request,f'wrong password or name')
        return redirect('home')
        


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
            #return render(request, 'index.html', {'error': 'Please fill in all the required fields.'})
            messages.success(request,f'Please fill in all the required fields.')
            return redirect('home')
        if password != password2:
            #return render(request, 'index.html', {'error': 'Passwords do not match.'})
            messages.success(request,f'Passwords do not match.')
            return redirect('home')

        # Create a new User object.
        user = User.objects.create_user(username, password=password)


        # Create a new Employee object.
        agent = Agent(
            user=user,
            role=role,
            angaza_id=angaza_id,
            country=country,
        )

        # Save the employee object to the database.
        agent.save()
        print("saved")
        # Log in the user.
        login(request, user)
        messages.success(request,f'Hi, welcome!')
        print("logged in")

        # Redirect the user to the home page.
        return redirect('/')