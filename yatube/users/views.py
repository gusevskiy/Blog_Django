from django.views.generic import CreateView

from django.urls import reverse_lazy

from .forms import CreationForm


# Создаём свой класс, наследуем его от CreateView
class SignUp(CreateView):
    # C какой формой будет работать этот view-класс
    form_class = CreationForm
    # Куда переадресовать пользователя после того, как он отправит форму
    sussess_url = reverse_lazy('posts:index')
    # Какой шаблон применить для отображения веб-формы
    template_name = 'users/signup.html'
