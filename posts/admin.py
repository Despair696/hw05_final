from django.contrib import admin


from .models import Post, Group, Comment, Follow


class PostAdmin(admin.ModelAdmin):
    
    list_display = ("text", "pub_date", "author")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class GroupAdmin(admin.ModelAdmin):
    
    list_display = ("title", "slug", "description")
    search_fields = ("title",)
    empty_value_display = "-пусто-"


class CommentAdmin(admin.ModelAdmin):
    
    list_display = ("text", "author")
    search_fields = ("author",)
    empty_value_display = "-пусто-"


class FollowAdmin(admin.ModelAdmin):

    list_display = ("user", "author")
    search_fields = ("author",)
    empty_value_display = "-пусто-"


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
