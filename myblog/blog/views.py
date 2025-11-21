from .models import Post
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm
from django.core.mail import send_mail
from django.utils import timezone

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

def post_list(request):
    post_list = Post.published.all()
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post/list.html', {'posts': posts})

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

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
    
    return render(
        request,
        'blog/post/detail.html',
        {
            'post': post,
            'comments': comments,
            'comment_form': comment_form,
        }
    )
