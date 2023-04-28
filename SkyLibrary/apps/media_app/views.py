from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.views import View
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db.models import QuerySet

from crispy_forms.utils import render_crispy_form

from json import dumps

from .models import Media, MediaDownload, Comment, CommentRating, Report
from .forms import CreateMediaForm, CreateCommentForm, CreateReplyCommentForm, CreateReportCommentForm,\
    CreateReportMediaForm
from staff_app.models import ModeratorTask
from staff_app.views import ViewModeratorPage
from home_page_app.views import handler403, handler404


User = get_user_model()
ViewModeratorPage = ViewModeratorPage()


class ViewCreateMedia(LoginRequiredMixin, CreateView):

    form_class = CreateMediaForm
    model = Media
    template_name = 'media_app/create_media.html'
    success_url = reverse_lazy('create_media_successful')

    def form_valid(self, form):

        form.instance.user_who_added = self.request.user

        return super().form_valid(form)


def get_all_replies_to_replies(
        replies: QuerySet[Comment],
        result: list[dict[str: Comment, str: int]] = None,
        nesting: int = 1,
) -> list[dict[str: Comment, str: int]]:
    """
        Function returns all existing replies to received replies (from newest to oldest).

        "result" contains all replies in order like this:
            media comment 1, media comment reply 1, media comment reply 2, media comment reply reply 1,
            media comment reply reply 2, media comment 2, ...

        Structure:
            result = [
                {'comment': Comment, 'nesting': int},  # comment is a Comment object, nesting >= 1
                ...
            ]
    """

    if result is None:
        result = []

    for reply in replies:

        result.append({'comment': reply, 'nesting': nesting})

        result = get_all_replies_to_replies(reply.get_replies(), result, nesting + 1)

    return result


class ViewViewMedia(View):

    template_name = 'media_app/view_media.html'

    error_messages = {
        'bad_request':
            _('Something went wrong with your request, please try again or contact support (code: {error_code})'),
        'bad_comment':
            _('Something went wrong with your comment, please try again or contact support (code: {error_code})'),
        'bad_report':
            _('Something went wrong with your report, please try again or contact support (code: {error_code})'),
        'no_report_type_choice':
            _('Please select a reason for the report.'),
    }

    @staticmethod
    def get_media(media_id: int) -> Media | None:

        try:
            return Media.objects.get(id=media_id)

        except Media.DoesNotExist:
            return None

    @staticmethod
    def is_moderate(request, media: Media) -> bool:

        if not request.user.is_anonymous and request.user.role == User.MODERATOR:

            try:

                ModeratorTask.objects.get(user_who_added=request.user, media=media)

                return True

            except ModeratorTask.DoesNotExist:
                return False

        else:
            return False

    def check_user_can_be_on_page(self, request, media: Media) -> bool:
        # Works only for page, handled by media_app/views/ViewViewMedia.

        if request.user.is_anonymous:
            user_role = None

        else:
            user_role = request.user.role

        is_user_moderator: bool = user_role == User.MODERATOR

        is_moderate = self.is_moderate(request, media)

        if media.active != Media.ACTIVE and not is_user_moderator:
            return False

        elif media.active != Media.ACTIVE and is_user_moderator and not is_moderate:
            return False

        else:
            return True

    def get(self, request, media_id: int):

        media = self.get_media(media_id)

        if not media:
            return handler404(request)

        if not self.check_user_can_be_on_page(request, media):
            return handler403(request)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':

            if request.user.is_anonymous:
                return handler403(request)

            if request.GET.get('request_type') == 'get_comment_reply_form':

                create_reply_comment_form = CreateReplyCommentForm()

                return HttpResponse(
                    dumps({'under_comment_form': render_crispy_form(create_reply_comment_form)}),
                    content_type='application/json',
                )

            elif request.GET.get('request_type') == 'get_comment_report_form':

                create_report_comment_form = CreateReportCommentForm()

                return HttpResponse(
                    dumps({'under_comment_form': render_crispy_form(create_report_comment_form)}),
                    content_type='application/json',
                )

            elif request.GET.get('request_type') == 'get_media_report_form':

                create_report_media_form = CreateReportMediaForm()

                return HttpResponse(
                    dumps({'media_report_form': render_crispy_form(create_report_media_form)}),
                    content_type='application/json',
                )

            else:
                return handler404(request)

        else:

            media_comments = Comment.objects.filter(
                target_type=Comment.MEDIA_TYPE, target_id=media_id
            ).order_by('-pub_date')

            media_comments_with_replies = []

            for media_comment in media_comments:
                media_comments_with_replies += get_all_replies_to_replies(
                    media_comment.get_replies(), result=[{'comment': media_comment, 'nesting': 0}]
                )

            render_data = {
                'media': media,
                'is_moderate': self.is_moderate(request, media),
                'form': CreateCommentForm(),
                'comments': media_comments_with_replies,
            }

            return render(request, self.template_name, render_data)

    @staticmethod
    def messages_to_json(request) -> str:

        result = []

        for message in messages.get_messages(request):
            result.append(
                {
                    'level': message.level,
                    'message': message.message[0] if isinstance(message.message, list) else message.message,
                    'tags': message.tags,
                }
            )

        return dumps({'messages': result})

    def post(self, request, media_id: int):

        media = self.get_media(media_id)

        if not media:
            return handler404(request)

        if not self.check_user_can_be_on_page(request, media):
            return handler403(request)

        if request.user.is_anonymous:
            return handler403(request)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and \
                request.POST.get('request_type') == 'download_file':

            try:
                MediaDownload.objects.create(media=media, user_who_added=request.user)

            except ValidationError:
                pass

            return HttpResponse(
                dumps({'downloads_number': media.get_downloads_number()}),
                content_type='application/json',
            )

        elif request.headers.get('x-requested-with') == 'XMLHttpRequest' and \
                request.POST.get('request_type') == 'create_comment':

            target_type = request.POST.get('target_type')

            if target_type == 'media':
                request_form = CreateCommentForm(request.POST)

            elif target_type == 'comment':
                request_form = CreateReplyCommentForm(request.POST)

            else:

                messages.error(request, self.error_messages.get('bad_request').format(error_code='1.5'))

                return HttpResponse(self.messages_to_json(request), content_type='application/json')

            if request_form.is_valid():

                if target_type == 'media':

                    target_type = Comment.MEDIA_TYPE
                    target_id = media_id

                elif target_type == 'comment':

                    target_type = Comment.COMMENT_TYPE
                    target_id = request.POST.get('target_id')

                    try:
                        Comment.objects.get(id=target_id)

                    except Comment.DoesNotExist:

                        messages.error(request, self.error_messages.get('bad_request').format(error_code='1.1'))

                        return HttpResponse(self.messages_to_json(request), content_type='application/json')

                else:

                    messages.error(request, self.error_messages.get('bad_request').format(error_code='1.2'))

                    return HttpResponse(self.messages_to_json(request), content_type='application/json')

                try:
                    comment = Comment.objects.create(
                        target_type=target_type,
                        target_id=target_id,
                        content=request_form.cleaned_data['content'],
                        user_who_added=request.user,
                    )

                except ValidationError as e:

                    messages_with_code = [f'{message} (code: 1.3)' for message in e.messages]

                    messages.error(request, messages_with_code)

                    return HttpResponse(self.messages_to_json(request), content_type='application/json')

                comment_json = {
                    'id': comment.id,
                    'target_type': comment.target_type,
                    'target_id': comment.target_id,
                    'content': comment.content,
                    'pub_date': str(naturaltime(comment.pub_date)),
                    'user_who_added': str(comment.user_who_added),
                    'reply_translate': str(_('Reply')),
                }

                return HttpResponse(dumps({'comment': comment_json}), content_type='application/json')

            else:

                messages.error(request, self.error_messages.get('bad_comment').format(error_code='1.4'))

                return HttpResponse(self.messages_to_json(request), content_type='application/json')

        elif request.headers.get('x-requested-with') == 'XMLHttpRequest' and \
                request.POST.get('request_type') == 'add_comment_vote':

            target_types: dict = {
                'upvote': 'upvote',
                'downvote': 'downvote',
            }

            try:
                target_comment = Comment.objects.get(id=request.POST.get('target_id'))

            except Comment.DoesNotExist:

                messages.error(request, self.error_messages.get('bad_request').format(error_code='2.1'))

                return HttpResponse(self.messages_to_json(request), content_type='application/json')

            if request.POST.get('vote_type') == target_types['upvote']:
                vote_type = CommentRating.UPVOTE

            elif request.POST.get('vote_type') == target_types['downvote']:
                vote_type = CommentRating.DOWNVOTE

            else:

                messages.error(request, self.error_messages.get('bad_request').format(error_code='2.2'))

                return HttpResponse(self.messages_to_json(request), content_type='application/json')

            try:
                CommentRating.objects.create(
                    comment=target_comment,
                    rating=vote_type,
                    user_who_added=request.user,
                )

            except ValidationError as e:
                if e.messages[0]:  # error message != '', see model clean method for more info

                    messages_with_code = [f'{message} (code: 2.3)' for message in e.messages]

                    messages.error(request, messages_with_code)

                    return HttpResponse(self.messages_to_json(request), content_type='application/json')

            if request.POST.get('vote_type') == target_types['upvote']:
                not_target_type = target_types['downvote']

            else:
                not_target_type = target_types['upvote']

            return HttpResponse(
                dumps({
                    'new_rating': target_comment.get_rating(),
                    'target_id': request.POST.get('target_id'),
                    'not_target_type': not_target_type,
                }),
                content_type='application/json',
            )

        elif request.headers.get('x-requested-with') == 'XMLHttpRequest' and \
                request.POST.get('request_type') == 'create_report':

            if not request.POST.get('report_type'):

                messages.error(request, f'{self.error_messages.get("no_report_type_choice")}')

                return HttpResponse(self.messages_to_json(request), content_type='application/json')

            request_post_mutable = request.POST.copy()

            try:
                request_post_mutable.setlist('report_type', request_post_mutable['report_type'].split(','))

            except KeyError:

                messages.error(request, self.error_messages.get('bad_report').format(error_code='4.2'))

                return HttpResponse(self.messages_to_json(request), content_type='application/json')

            request_form = CreateReportCommentForm(request_post_mutable)

            if request_form.is_valid():

                target_type: str = request.POST.get('target_type')

                if target_type == 'comment':

                    try:

                        target_id = request.POST.get('target_id')

                        # object existence check
                        Comment.objects.get(id=target_id)

                    except Comment.DoesNotExist:

                        messages.error(request, self.error_messages.get('bad_request').format(error_code='4.4'))

                        return HttpResponse(self.messages_to_json(request), content_type='application/json')

                    try:
                        report = Report.objects.create(
                            content=request_form.cleaned_data['content'],
                            target_type=Report.COMMENT_TYPE,
                            target_id=target_id,
                            user_who_added=request.user,
                        )

                    except ValidationError as e:

                        if e.messages[0]:  # error message != '', see model clean method for more info
                            messages.error(request, e.messages)

                        return HttpResponse(self.messages_to_json(request), content_type='application/json')

                    report.report_type.set(request_form.cleaned_data['report_type'])

                    report_success_message: str = f'{_("Your report has been successfully created")}!'

                    return HttpResponse(
                        dumps({'report_success_message': report_success_message}),
                        content_type='application/json',
                    )

                elif target_type == 'media':

                    try:
                        report = Report.objects.create(
                            content=request_form.cleaned_data['content'],
                            target_type=Report.MEDIA_TYPE,
                            target_id=media_id,
                            user_who_added=request.user,
                        )

                    except ValidationError as e:

                        if e.messages[0]:  # error message != '', see model clean method for more info
                            messages.error(request, e.messages)

                        return HttpResponse(self.messages_to_json(request), content_type='application/json')

                    report.report_type.set(request_form.cleaned_data['report_type'])

                    report_success_message: str = f'{_("Your report has been successfully created")}!'

                    return HttpResponse(
                        dumps({'report_success_message': report_success_message}),
                        content_type='application/json',
                    )

                else:

                    messages.error(request, self.error_messages.get('bad_report').format(error_code='4.3'))

                    return HttpResponse(self.messages_to_json(request), content_type='application/json')

            else:

                messages.error(request, self.error_messages.get('bad_report').format(error_code='4.1'))

                return HttpResponse(self.messages_to_json(request), content_type='application/json')

        elif 'approve_button' in request.POST:
            return ViewModeratorPage.post_from_view_page(request, self.get_media(media_id))

        else:
            return handler404(request)
