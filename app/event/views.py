import os

from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import DetailView, ListView, RedirectView, View
from django.urls import reverse_lazy
from django.db.models import Q
from django.db import IntegrityError
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from .models import Event, Participation, Comment, Frame
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.apps import apps
from django.template.loader import get_template
from django.template import Context
from base.utils import send_template_mail
from django.core.mail import send_mail
from tag.models import Tag
from user.models import User
from django.conf import settings
from django.core.files import File
from django.utils.translation import ugettext_lazy as _

import sys
import re
from datetime import datetime
import io
import json
import requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


@method_decorator(login_required, name='dispatch')
class EventCreate(CreateView):
    model = Event
    fields = [
        'name',
        'start_time',
        'end_time',
        'meeting_place',
        'image',
        'contact',
        'details',
        'notes',
        'private_notes',
        'region',
    ]

    template_name = "event/add.html"

    def get_context_data(self, **kwargs):
        context = super(EventCreate, self).get_context_data(**kwargs)
        context['all_tags'] = Tag.objects.all

        if 'copy_event_id' in self.request.GET:
            copy_event_id = self.request.GET['copy_event_id']
            copy_event = Event.objects.get(pk=copy_event_id)
            copy_event.start_time = None
            copy_event.end_time = None
            context['event'] = copy_event

        """Google MAP KEY
        MAP KEY from settings
        """
        context['google_map_key'] = settings.GOOGLE_MAP_KEY

        return context

    def form_valid(self, form):
        form.instance.host_user = self.request.user
        form_redirect = super(EventCreate, self).form_valid(form)
        event = form.save()

        # Admins
        event.admin.clear()
        raw_admins = self.request.POST.getlist('admins') or []
        new_admins = User.objects.filter(username__in=raw_admins)

        for admin_id in new_admins.values_list('id', flat=True):
            event.admin.add(admin_id)
        event.admin.add(event.host_user.id)

        new_admin_names = new_admins.values_list('username', flat=True)
        for name in set(raw_admins) - set(new_admin_names):
            error_msg = _("There is no user named %(name)s.") % {'name': name}
            messages.error(self.request, error_msg)

        # Tags
        event.tag.clear()
        for tag_id in self.request.POST.getlist('tags'):
            event.tag.add(int(tag_id))

        # Frames
        # XXX: Unspecified large numbere of Frames via POST
        req_post = self.request.POST

        for n in req_post.getlist('frame_number'):
            frame_id = req_post.get('frame_' + n + '_id')
            if frame_id is None:
                frame = Frame(event=event)
            else:
                frame = Frame.objects.get(pk=frame_id)

            description_key = 'frame_' + n + '_description'
            frame.description = req_post.get(description_key)

            upperlimit_key = 'frame_' + n + '_upperlimit'
            frame.upper_limit = req_post.get(upperlimit_key) or None

            deadline_key = 'frame_' + n + '_deadline'
            frame.deadline = req_post.get(deadline_key) or event.end_time

            frame.save()

        # Lng, Lat
        latitude = self.request.POST.get('latitude')
        longitude = self.request.POST.get('longitude')
        if latitude and longitude:
            event.latitude = latitude
            event.longitude = longitude
            event.save()

        # Image
        if 'image_url' in self.request.POST and not event.image:
            url = self.request.POST['image_url']
            new_url = os.path.join(settings.BASE_DIR, url[1:])
            print(new_url, file=sys.stderr)
            reopen = open(new_url, "rb")
            django_file = File(reopen)
            event.image.save(new_url, django_file, save=True)

            info_msg = _("Your event was successfully added.")
            messages.info(self.request, info_msg)
        return form_redirect

    def form_invalid(self, form):
        return super(EventCreate, self).form_invalid(form)

    def get_success_url(self):
        self.object.admin.add(self.request.user)
        sys.stderr.write("Added User")
        p = Participation(
            user=self.request.user,
            event=self.object,
            status="管理者",
        )
        p.save()
        self.object.participation_set.add(p)
        sys.stderr.write("Added participation")
        return super(EventCreate, self).get_success_url()


class EventDetailView(DetailView):
    template_name = 'event/detail.html'
    model = Event
    context_object_name = 'event'

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            error_msg = _("Event not found.")
            messages.error(request, error_msg)
            return redirect('top')
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        login_user = self.request.user
        context['participants'] = self.object.participant.all()
        login_user_participating = login_user in self.object.participant.all()
        context['login_user_participating'] = login_user_participating

        if login_user_participating:
            context['participation'] \
                = Participation.objects \
                               .filter(event=self.object) \
                               .get(user=login_user)

        """Google MAP KEY
        MAP KEY from settings
        """
        context['google_map_key'] = settings.GOOGLE_MAP_KEY

        return context


class EventIndexView(ListView):
    template_name = 'event/index.html'
    context_object_name = 'all_events'

    def get_queryset(self):
        date = timezone.now()

        return Event.objects \
                    .filter(start_time__gte=date) \
                    .order_by('start_time')


class EventEditView(UserPassesTestMixin, UpdateView):
    model = Event
    fields = [
        'name',
        'start_time',
        'end_time',
        'meeting_place',
        'image',
        'details',
        'notes',
        'private_notes',
        'region'
    ]
    template_name = 'event/edit.html'

    def form_valid(self, form):
        form_redirect = super(EventEditView, self).form_valid(form)
        event = form.save(commit=False)

        # Admins
        event.admin.clear()
        raw_admins = self.request.POST.getlist('admins') or []
        new_admins = User.objects.filter(username__in=raw_admins)

        for admin_id in new_admins.values_list('id', flat=True):
            event.admin.add(admin_id)
        event.admin.add(event.host_user.id)

        new_admin_names = new_admins.values_list('username', flat=True)
        for name in set(raw_admins) - set(new_admin_names):
            error_msg = _("No users found matching %(name)s.") % {'name': name}
            messages.error(self.request, error_msg)

        # Tags
        new_tags = set([int(t) for t in self.request.POST.getlist('tags')])
        old_tags = set([t.id for t in event.tag.all()])

        for tag_id in new_tags - old_tags:
            event.tag.add(tag_id)

        for tag_id in old_tags - new_tags:
            event.tag.remove(tag_id)

        # Frames
        # XXX: Unspecified large numbere of Frames via POST
        # FIXME: dup
        req_post = self.request.POST

        for n in req_post.getlist('frame_number'):
            frame_id = self.request.POST.get('frame_' + n + '_id')
            if frame_id is None:
                frame = Frame(event=event)
            else:
                frame = Frame.objects.get(pk=frame_id)

            description_key = 'frame_' + n + '_description'
            frame.description = req_post.get(description_key)

            upperlimit_key = 'frame_' + n + '_upperlimit'
            frame.upper_limit = req_post.get(upperlimit_key) or None

            deadline_key = 'frame_' + n + '_deadline'
            frame.deadline = req_post.get(deadline_key) or event.end_time

            frame.save()

        # Lng, Lat
        latitude = self.request.POST.get('latitude')
        longitude = self.request.POST.get('longitude')
        if latitude and longitude:
            event.latitude = latitude
            event.longitude = longitude
            event.save()

        messages.info(self.request, _("Event detail has been updated."))
        return form_redirect

    def test_func(self):
        return self.request.user.is_manager_for(self.get_object())

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(EventEditView, self).get_context_data(**kwargs)
        context['all_tags'] = Tag.objects.all

        """Google MAP KEY
        MAP KEY from settings
        """
        context['google_map_key'] = settings.GOOGLE_MAP_KEY

        return context


class EventDeleteView(UserPassesTestMixin, DeleteView):
    model = Event
    template_name = 'event/check_delete.html'

    def get_context_data(self, **kwargs):
        context = super(EventDeleteView, self).get_context_data()
        return context

    def dispatch(self, request, *args, **kwargs):
        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def test_func(self):
        return self.request.user.is_manager_for(self.get_object())

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_url(self):
        messages.info(self.request, _("Event has been deleted."))
        return reverse_lazy('top')


class EventParticipantsView(DetailView):
    model = Event
    template_name = 'event/participants.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super(EventParticipantsView, self).get_context_data(**kwargs)

        participation_objects = self.object.participation_set.all()
        context['participants'] = [p.user for p in participation_objects]

        # XXX: user for user ???
        context['admins'] = [user for user in self.object.admin.all()]

        return context


class EventSearchResultsView(ListView):
    model = Event
    template_name = 'event/search_results.html'
    context_object_name = 'result_events'
    paginate_by = 10

    def split_string_to_terms(self, string):
        findterms = re.compile(r'"([^"]+)"|(\S+)').findall
        normspace = re.compile(r'\s{2,}').sub

        return [normspace(' ', (t[0] or t[1]).strip()) for t
                in findterms(string)]

    def make_query_from_string(self, string):
        query = None
        fields = ['name', 'details']
        terms = self.split_string_to_terms(string)
        for term in terms:
            term_query = None
            for field in fields:
                q = Q(**{"%s__icontains" % field: term})
                if term_query is None:
                    term_query = q
                else:
                    term_query = term_query | q
            if query is None:
                query = term_query
            else:
                query = query & term_query

        return query

    def get_queryset(self):

        query = Q()

        # Free Word
        if 'q' in self.request.GET:
            user_entry = self.request.GET['q']
            if user_entry is not None and user_entry != "":
                freeword_query = self.make_query_from_string(user_entry)
                if freeword_query is None:
                    messages.error(self.request, _("No events found matching your search."))
                    return Event.objects.none()
                else:
                    query = query & freeword_query

        # Date
        if 'date' in self.request.GET:
            begin_date_string = self.request.GET['date']
            if begin_date_string is not None and begin_date_string != "":
                date = datetime.strptime(begin_date_string, "%Y-%m-%d")
                date_query = Q(start_time__gte=date)
                query = query & date_query

        if 'end_date' in self.request.GET:
            end_date_string = self.request.GET['end_date']
            if end_date_string is not None and end_date_string != "":
                end_date = datetime.strptime(end_date_string, "%Y-%m-%d")
                date = end_date + datetime.timedelta(days=1)
                date_query = Q(start_time__lt=date)
                query = query & date_query

        # Tag
        if 'tags' in self.request.GET:
            tags = [int(t) for t in self.request.GET.getlist('tags')]

            if len(tags) > 0:
                Tag = apps.get_model('tag', 'Tag')
                tag_query = None
                for t in tags:
                    tag = Tag.objects.get(pk=t)
                    if tag_query is None:
                        tag_query = Q(tag=tag)
                    else:
                        tag_query = tag_query | Q(tag=tag)
                query = query & tag_query

        # Place
        if 'region' in self.request.GET:
            place = self.request.GET['region']

            if place is not None and place != "":
                place_query = Q(region=place)
                query = query & place_query

        results = Event.objects.filter(query).order_by('-id').distinct()

        if 'order_by' in self.request.GET:
            order_by = self.request.GET['order_by']
            criterion = order_by.split("-")[0]
            desc = order_by.split("-")[1]
            if desc == "desc":
                criterion = "-" + criterion
            else:
                pass

            results = results.order_by(criterion)

        # Include events that are already over?
        if self.request.GET.get('exclude_full_events') == "on":
            results = [event for event in results if not event.is_full()]

        # Include events with no openings?
        if self.request.GET.get('exclude_closed_events') == "on":
            results = [event for event in results if not event.is_closed()]

        if len(results) == 0:
            messages.error(self.request, _("No events found matching your search."))

        # Filter based on page and number per page
        if 'numperpage' in self.request.GET:
            num_per_page = self.request.GET["numperpage"]
            if num_per_page is not None and num_per_page != "":
                self.paginate_by = int(num_per_page)

        return results

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["all_tags"] = Tag.objects.all()

        prefectures = settings.PREFECTURES
        prefs = prefectures.items()
        prefs = sorted(prefs, key=lambda x: x[1][1])
        context['prefectures'] = [(k, v[0]) for k, v in prefs]

        tags = self.request.GET.getlist('tags')
        context['checked_tags'] = [int(t) for t in tags]

        return context


@method_decorator(login_required, name='dispatch')
class EventJoinView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        event_id = kwargs['event_id']
        frame_id = kwargs['frame_id']

        event = Event.objects.get(pk=event_id)

        if event.is_over():
            messages.error(self.request, _("This event has already ended."))
        else:

            frame = Frame.objects.get(pk=frame_id)
            status = "キャンセル待ち" if frame.is_full() else "参加中"

            if frame.is_closed():
                messages.error(self.request, _("This position is closed."))
            else:
                try:
                    p = Participation.objects.create(
                        user=self.request.user,
                        event_id=kwargs['event_id'],
                        frame_id=kwargs['frame_id'],
                        status=status,
                    )
                    p.save()
                    if status == "キャンセル待ち":
                        messages.success(self.request, _("You are on the waiting list."))
                    else:
                        messages.success(self.request, _("You joined this event."))
                except IntegrityError:
                    event = Event.objects.get(pk=event_id)
                    if event in self.request.user.participating_event.all():
                        messages.error(self.request, _("You have already joined."))
                    else:
                        messages.error(self.request, _("An error occurred while processing."))

        self.url = reverse_lazy('event:detail', kwargs={'pk': event_id})
        return super(EventJoinView, self).get_redirect_url(*args, **kwargs)


@method_decorator(login_required, name='dispatch')
class EventSupportView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        event = Event.objects.get(pk=kwargs['event_id'])

        if 'cancel' in kwargs:
            messages.error(self.request, _("You cannot undo your like."))
            # event.supporter.remove(self.request.user.id)
        else:
            if event.is_over():
                messages.error(self.request, _("You cannot like events ended."))
            else:
                messages.info(self.request, _("Liked this event!"))
                event.supporter.add(self.request.user.id)

        self.url = reverse_lazy('event:detail', kwargs={'pk': event.id})
        return super().get_redirect_url(*args, **kwargs)


@method_decorator(login_required, name='dispatch')
class EventFollowView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        event_id = kwargs['event_id']
        event = Event.objects.get(pk=event_id)

        if event.is_closed():
            messages.error(self.request, _("This event is already closed."))
        else:
            try:
                p = Participation.objects.create(
                    user=self.request.user,
                    event_id=kwargs['event_id'],
                    status="興味あり",
                )
                p.save()
                messages.error(self.request, "興味ありボランティアに追加しました")
            except IntegrityError:
                event = Event.objects.get(pk=event_id)
                if event in self.request.user.participating_event.all():
                    messages.error(self.request, _("You have already joined."))
                else:
                    messages.error(self.request, _("An error occurred while processing."))

        self.url = reverse_lazy('event:detail', kwargs={'pk': event_id})
        return super(EventFollowView, self).get_redirect_url(*args, **kwargs)


class ParticipationDeleteView(DeleteView, UserPassesTestMixin):
    model = Participation

    def get_object(self, event_id=None, queryset=None):
        return Participation.objects.get(event_id=self.kwargs['event_id'],
                                         user=self.request.user)

    def get_success_url(self):
        if self.object.status == "参加中":
            participations = self.object.frame.participation_set

            waiting_list = participations.filter(status="キャンセル待ち") \
                                         .order_by('created')

            if len(waiting_list) > 0:
                carry_up = waiting_list.first()
                carry_up.status = "参加中"
                carry_up.save()

                # Send Email
                template = get_template("email/carry_up.txt")

                context = Context({'user': carry_up.user,
                                   'event': carry_up.event})

                content = template.render(context)
                subject, message = content.split("\n", 1)

                # XXX: Hardcoded From address
                send_mail(subject,
                          message,
                          "reminder@sovol.moe",
                          [carry_up.user.email])

        messages.success(self.request, _("Canceled your participation."))

        return reverse_lazy('event:detail', kwargs={
            'pk': self.kwargs['event_id']
        })

    def test_func(self):
        # FIXME: Not in use?
        return True

    def handle_no_permission(self):
        return HttpResponseForbidden()


@method_decorator(login_required, name='dispatch')
class CommentCreate(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        event_id = kwargs["event_id"]

        verify = requests.get(
            url="https://www.google.com/recaptcha/api/siteverify",
            params={
                "secret": settings.GOOGLE_RECAPTCHA_SECRET,
                "response": self.request.POST['g-recaptcha-response']
            }
        )
        data = json.loads(verify.text)
        if not data['success']:
            messages.error(self.request, _("Authentication failed."))
            return reverse_lazy('event:detail', kwargs={'pk': event_id})

        text = self.request.POST["text"]
        if text.strip() != "":
            comment = Comment(
                user=self.request.user,
                event=Event.objects.get(pk=event_id),
                text=text,
            )
            comment.save()

        return reverse_lazy('event:detail', kwargs={'pk': event_id})


class CommentDeleteView(DeleteView):
    model = Comment

    def get_success_url(self):
        event_id = self.kwargs["event_id"]
        return reverse_lazy('event:detail', kwargs={'pk': event_id})


class SendMessage(UserPassesTestMixin, SingleObjectMixin, View):
    model = Event

    def get(self, request, *args, **kwargs):
        return render(request, 'event/message.html', {
            'event': self.get_object()
        })

    def post(self, request, *args, **kwargs):
        target = request.POST.get('target')
        message = request.POST.get('message')
        event = self.get_object()

        if target == "admin":
            users = event.participant \
                         .filter(participation__status__in=["管理者"])
        elif target == "participants":
            users = event.participant.all()
        elif target == "members":
            users = event.participant \
                         .filter(participation__status__in=["管理者", "参加中"])
        elif target == "waiting":
            users = event.participant \
                         .filter(participation__status__in=["管理者", "キャンセル待ち"])
        else:
            messages.error(request, _("Invalid recipient"))
            return redirect(reverse_lazy('event:message',
                                         kwargs={'pk': kwargs['pk']}))

        for user in users:
            # XXX: Hardcoded From address
            send_template_mail(
                "email/message.txt",
                {
                    "event": event,
                    "user": user,
                    "sender": request.user,
                    "message": message,
                },
                "Sovol Info <info@sovol.moe>",
                [user.email],
            )

        messages.success(self.request, _("Your message has been sent successfully."))
        return redirect(reverse_lazy('event:message',
                                     kwargs={'pk': kwargs['pk']}))

    def test_func(self):
        is_authenticated = self.request.user.is_authenticated
        is_manager = self.request.user.is_manager_for(self.get_object())
        return is_authenticated and is_manager

    def handle_no_permission(self):
        return HttpResponseForbidden()
