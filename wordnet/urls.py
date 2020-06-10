from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^$', 'wordnet.views.index', name='index'),
    url(r'^login$', 'wordnet.views.log_in', name='login'),
    url(r'^logout$', 'wordnet.views.log_out', name='logout'),
    url(r'^register$', 'wordnet.views.register_user', name='register'),
    
    url(r'^synset$', 'wordnet.views.synset', name='synset'),
    url(r'^synset/(?P<obj_id>[^\.]{24})$', 'wordnet.views.synset', name='synset_obj_id'),
    url(r'^synset/(?P<offset_pos>[0-9]{4,8}\.[nvars])$', 'wordnet.views.synset', name='synset_offset_pos'),
    url(r'^synset/(?P<synset_synset>.*\.[nvars]\.[0-9]+)$', 'wordnet.views.synset', name='synset_synset'),
    
    url(r'^overview$', 'wordnet.views.overview', name='overview'),
    url(r'^overview/(?P<obj_id>[^\.]{24})$', 'wordnet.views.overview', name='overview'),
    url(r'^overview/(?P<complete>all)$', 'wordnet.views.overview', name='overview'),
    url(r'^overview/(?P<offset_pos>[0-9]{4,8}\.[nvars])$', 'wordnet.views.overview', name='overview'),
    url(r'^overview/(?P<synset_synset>.*\.[nvars]\.[0-9]+)$', 'wordnet.views.overview', name='overview'),
    # url(r'^blog/', include('blog.urls')),

    
)
