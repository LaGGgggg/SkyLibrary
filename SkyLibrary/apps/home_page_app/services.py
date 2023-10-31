from typing import Literal, get_args

from django.db.models import QuerySet, Count, Case, When, Value, IntegerField
from django.utils.translation import gettext_lazy as _

from media_app.models import Media, MediaTags, MediaRating


RATING_DIRECTION_CHOICES_LITERAL = Literal['ascending', 'descending']
_ASCENDING, _DESCENDING = get_args(RATING_DIRECTION_CHOICES_LITERAL)
RATING_DIRECTION_CHOICES = (
    (_ASCENDING, _('ascending')),
    (_DESCENDING, _('descending')),
)
RATING_DIRECTION_CHOICES_LIST = [_ASCENDING, _DESCENDING]


class MediaFilter:

    def __init__(self) -> None:
        self._media = Media.objects.filter(active=Media.ACTIVE)

    def filter_by_rating(
            self,
            direction: RATING_DIRECTION_CHOICES_LITERAL = _DESCENDING,
            minimum_value: int = min(MediaRating.rating_choices_list),
            maximum_value: int = max(MediaRating.rating_choices_list),
    ) -> None:

        # filtering media by minimum and maximum rating values
        result_media = filter(lambda media: minimum_value <= media.get_rating() <= maximum_value, self._media)

        # sorting media by rating with a given direction
        result_media = sorted(result_media, key=lambda media: media.get_rating(), reverse=direction == _DESCENDING)

        result_pks = [media.pk for media in result_media]

        # adds a QuerySet, not a filter object and orders it correctly
        self._media = Media.objects.filter(pk__in=result_pks).order_by(
            Case(
                *[When(pk=pk, then=Value(i)) for i, pk in enumerate(result_pks)],
                output_field=IntegerField(),
            ).asc(),
        )

    def _filter_by_text(self, text: str, media_field_name: str) -> None:
        # filtering by text in a given media field name
        # full chain after substitution example: self._media = self._media.filter(title__contains=text)
        self._media = self._media.filter(**{f'{media_field_name}__contains': text})

    def filter_by_title(self, text: str) -> None:
        self._filter_by_text(text, 'title')

    def filter_by_author(self, text: str) -> None:
        self._filter_by_text(text, 'author')

    def filter_by_user_who_added(self, text: str) -> None:
        self._media = self._media.filter(user_who_added__username__contains=text)

    def filter_by_tags(self, tags: QuerySet[MediaTags]) -> None:

        tags_list = list(tags)

        # filtering by tags (all tags in the media must be present)
        self._media = self._media.filter(tags__in=tags_list).annotate(
            tags_founded=Count('tags')
        ).filter(tags_founded=len(tags_list))

    def get(self, amount: int | None) -> QuerySet[Media]:

        if amount:
            return self._media[:amount]

        else:
            return self._media
