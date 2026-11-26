from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render


def registro(request):
    """Registra una cuenta nueva reutilizando UserCreationForm de Django."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts:login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/registro.html', {'form': form})


@login_required
def panel(request):
    """Muestra el panel protegido únicamente a usuarios autenticados."""
    return render(request, 'accounts/panel.html')
