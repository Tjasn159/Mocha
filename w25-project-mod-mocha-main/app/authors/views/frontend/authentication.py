from django.shortcuts import render, redirect
from authors.forms import AuthorForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login , logout 
from authors.models import Author
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.urls import reverse
from constance import config
# reference : https://www.youtube.com/watch?v=DIFaOkxy6TE


def register_view(request):
    if request.method == "POST":
        # Validating form
        form = AuthorForm(request.POST)
        if form.is_valid():
            try:
                author = form.save(commit=False)
                # Check if approval is required
                if not config.USER_REGISTRATION_APPROVAL_REQUIRED:
                    author.approved = True  # Automatically approved

                author.save()
                # fix the global id
                author.global_id = f"http://{request.get_host()}/api/authors/{author.id}"
                author.host = f"http://{request.get_host()}/api/"
                author.save()
                # redirect to login page 
                return HttpResponseRedirect(f"{reverse('authors:login_view')}?from=register")
            except IntegrityError:
                form.add_error('display_name', 'This display name is already taken.')
    else:
        # first comes to the page 
        form = AuthorForm()
    return render(request, 'authors/register.html', { 'form': form })

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            author = Author.objects.get(user=user)
            if author.approved == False:
                return render(request, 'authors/login.html', { 'form': form, 'error': 'Account not approved yet' })
            login(request, form.get_user())
            if "next" in request.POST:
                return redirect(request.POST.get("next"))
            return redirect("index")
    else:
        form = AuthenticationForm()  
    return render(request, 'authors/login.html', { 'form': form })

def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("index")
    return redirect("index")