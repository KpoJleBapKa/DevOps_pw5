import markdown
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy
from django.utils.feedgenerator import Atom1Feed
from .models import Post

class LatestPostsFeed(Feed):
    title = "Мій блог"
    link = reverse_lazy('blog:post_list')
    description = 'Останні публікації у блозі.'
    description_template = 'blog/feeds/post_description.html'

    def items(self):
        return Post.published.all()[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return truncatewords_html(markdown.markdown(item.body), 50)

    def item_pubdate(self, item):
        return item.publish
    
    def item_author_name(self, item):
        return item.author.get_full_name() or item.author.username
    
    def item_categories(self, item):
        return [tag.name for tag in item.tags.all()]

class AtomSiteNewsFeed(LatestPostsFeed):
    feed_type = Atom1Feed
    subtitle = LatestPostsFeed.description
