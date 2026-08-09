from django.views.generic import DetailView, ListView

from .models import Vacancy


class VacancyListView(ListView):
    template_name = "vacancies/vacancy_list.html"
    context_object_name = "vacancies"
    paginate_by = 12

    def get_queryset(self):
        return Vacancy.objects.publicly_visible()


class VacancyDetailView(DetailView):
    template_name = "vacancies/vacancy_detail.html"
    context_object_name = "vacancy"

    def get_queryset(self):
        return Vacancy.objects.publicly_visible()
