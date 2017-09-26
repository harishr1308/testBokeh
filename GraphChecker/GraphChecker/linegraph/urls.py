from django.conf.urls import url
from GraphChecker.linegraph.views import index, general_plot, world_plot_json

urlpatterns = [
    url(r'^$', index),
    url(r'^general$', general_plot),
    url(r'^world', world_plot_json),
]
