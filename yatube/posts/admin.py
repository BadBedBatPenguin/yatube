from .models import Comment, Follow, Group, Post

from django.contrib import admin


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
    )
    empty_value_display = '-пусто-'
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Group, GroupAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'post',
        'author',
        'text',
        'created',
    )
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


admin.site.register(Comment, CommentAdmin)


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'user',
    )
    list_filter = ('author', 'user',)
    empty_value_display = '-пусто-'


admin.site.register(Follow, FollowAdmin)
