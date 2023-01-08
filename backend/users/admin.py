from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from recipes.admin import FavoriteInline, ShoppingCartInline

from .models import Follow

User = get_user_model()

admin.site.unregister(Group)


class FollowInline(admin.StackedInline):
    model = Follow
    fk_name = 'user'
    extra = 0


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'user',
        'author'
    )
    search_fields = ('user__username', 'author__username')


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'is_admin'
                    )
    list_filter = ('is_admin', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_admin', 'is_superuser'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    inlines = [FollowInline, ShoppingCartInline, FavoriteInline]
