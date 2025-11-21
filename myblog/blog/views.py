from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail, send_mass_mail
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.contrib import messages
from django.conf import settings
from .models import Post, Comment, Tag, Subscriber
from .forms import EmailPostForm, CommentForm, EmailSubscribeForm, SearchForm

def post_share(request, post_id):
    # Отримуємо публікацію за ідентифікатором
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    
    if request.method == 'POST':
        # Форма була надіслана
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Вілідація полів пройшла успішно
            cd = form.cleaned_data
            # Створюємо абсолютний URL для поста
            post_url = request.build_absolute_uri(post.get_absolute_url())
            
            # Тема листа
            subject = f"{cd['name']} радить вам прочитати " \
                     f"{post.title}"
            
            # Тіло листа
            message = f"Прочитайте '{post.title}' за посиланням {post_url}\n\n" \
                     f"{cd['name']} залишив(ла) коментар: {cd['comments']}"
            
            # Відправляємо листа
            send_mail(subject, message, 'krolvalakasa@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    
    return render(request, 'blog/post/share.html', {
        'post': post,
        'form': form,
        'sent': sent
    })

def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    query = None
    
    # Initialize forms
    search_form = SearchForm()
    subscribe_form = EmailSubscribeForm()
    
    # Handle search
    if 'query' in request.GET:
        search_form = SearchForm(request.GET)
        if search_form.is_valid():
            query = search_form.cleaned_data['query']
            if query:
                post_list = post_list.filter(
                    Q(title__icontains=query) |
                    Q(body__icontains=query) |
                    Q(tags__name__icontains=query)
                ).distinct()
    
    # Handle tag filtering
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    
    # Get all tags for the sidebar
    tags = Tag.objects.all()
    
    # Pagination
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post/list.html', {
        'posts': posts,
        'tag': tag,
        'tags': tags,
        'search_form': search_form,
        'query': query,
        'subscribe_form': subscribe_form,
    })

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subscribe_form'] = EmailSubscribeForm()
        return context

def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    
    # Список активних коментарів до цього поста
    comments = post.comments.filter(active=True)
    
    # Форма для коментування
    if request.method == 'POST':
        # Коментар був опублікований
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Створюємо об'єкт Comment, але ще не зберігаємо в базу даних
            new_comment = comment_form.save(commit=False)
            # Прив'язуємо коментар до поточного поста
            new_comment.post = post
            # Зберігаємо коментар в базі даних
            new_comment.save()
            # Перенаправляємо на ту саму сторінку, щоб уникнути повторного відправлення форми
            return redirect(post.get_absolute_url())
    else:
        comment_form = CommentForm()
    
    # Отримуємо список ID тегів поточного поста
    post_tags_ids = post.tags.values_list('id', flat=True)
    
    # Отримуємо пости, які мають спільні теги (за винятком поточного поста)
    similar_posts = Post.published.filter(tags__in=post_tags_ids)\
                              .exclude(id=post.id)
    
    # Додаємо кількість спільних тегів для кожного поста
    similar_posts = similar_posts.annotate(same_tags=models.Count('tags'))\
                               .order_by('-same_tags', '-publish')[:4]
    
    # Get all tags for the sidebar
    tags = Tag.objects.all()
    
    return render(
        request,
        'blog/post/detail.html',
        {
            'post': post,
            'comments': comments,
            'comment_form': comment_form,
            'similar_posts': similar_posts,
            'subscribe_form': EmailSubscribeForm(),
            'tags': tags,
        }
    )


@require_POST
def subscribe(request):
    form = EmailSubscribeForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data['email']
        try:
            # Перевіряємо чи існує вже такий email
            subscriber, created = Subscriber.objects.get_or_create(
                email=email,
                defaults={'is_active': True}
            )
            
            if not created:
                # Якщо підписка вже існує, але неактивна, активуємо її
                if not subscriber.is_active:
                    subscriber.is_active = True
                    subscriber.save()
                    message = 'Вашу підписку успішно поновлено!'
                else:
                    message = 'Ви вже підписані на нашу розсилку.'
            else:
                message = 'Дякуємо за підписку!'
                
                # Відправляємо листа з підтвердженням
                subject = 'Підтвердження підписки на розсилку'
                message = render_to_string('blog/emails/subscription_confirmation.html', {
                    'email': email,
                })
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    html_message=message,
                    fail_silently=False,
                )
                
            return JsonResponse({
                'success': True,
                'message': message
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Сталася помилка. Будь ласка, спробуйте пізніше.'
            }, status=400)
    
    # Якщо форма не валідна, повертаємо помилки
    return JsonResponse({
        'success': False,
        'message': 'Будь ласка, введіть коректну email адресу.',
        'errors': form.errors
    }, status=400)
