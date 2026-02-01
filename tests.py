from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Post, Comment
from .forms import PostForm, CommentForm
from datetime import datetime


class PostModelTests(TestCase):
    """Post-mallin testit"""
    
    def setUp(self):
        """Luo test-käyttäjän ja postauksen"""
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.post = Post.objects.create(
            title='Test Postaus',
            content='Test sisältö',
            author=self.user
        )
    
    def test_post_creation(self):
        """Testi: Postaus luodaan oikein"""
        self.assertEqual(self.post.title, 'Test Postaus')
        self.assertEqual(self.post.content, 'Test sisältö')
        self.assertEqual(self.post.author, self.user)
    
    def test_post_str_method(self):
        """Testi: Post __str__ palauttaa otsikon"""
        self.assertEqual(str(self.post), 'Test Postaus')
    
    def test_post_ordering(self):
        """Testi: Postaukset lajitellaan uusimmista ensin"""
        post2 = Post.objects.create(
            title='Uudempi postaus',
            content='Sisältö',
            author=self.user
        )
        posts = Post.objects.all()
        self.assertEqual(posts[0], post2)
        self.assertEqual(posts[1], self.post)
    
    def test_post_auto_timestamps(self):
        """Testi: created_at ja updated_at asetetaan automaattisesti"""
        self.assertIsNotNone(self.post.created_at)
        self.assertIsNotNone(self.post.updated_at)


class CommentModelTests(TestCase):
    """Comment-mallin testit"""
    
    def setUp(self):
        """Luo test-käyttäjän, postauksen ja kommentin"""
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.post = Post.objects.create(
            title='Test Postaus',
            content='Test sisältö',
            author=self.user
        )
        self.comment = Comment.objects.create(
            content='Test kommentti',
            author=self.user,
            post=self.post
        )
    
    def test_comment_creation(self):
        """Testi: Kommentti luodaan oikein"""
        self.assertEqual(self.comment.content, 'Test kommentti')
        self.assertEqual(self.comment.author, self.user)
        self.assertEqual(self.comment.post, self.post)
    
    def test_comment_str_method(self):
        """Testi: Comment __str__ palauttaa kuvauksen"""
        expected = f"Kommentti 'Test Postaus' kirjoittajalta testuser"
        self.assertEqual(str(self.comment), expected)
    
    def test_comment_related_name(self):
        """Testi: Post.comments.all() palauttaa kommentit"""
        self.assertEqual(self.post.comments.count(), 1)
        self.assertEqual(self.post.comments.first(), self.comment)
    
    def test_comment_deleted_with_post(self):
        """Testi: Kommentti poistetaan kun postaus poistetaan"""
        self.post.delete()
        self.assertEqual(Comment.objects.count(), 0)


class PostFormTests(TestCase):
    """PostForm-testit"""
    
    def test_post_form_valid(self):
        """Testi: Kelvollinen lomake hyväksytään"""
        form_data = {
            'title': 'Test Postaus',
            'content': 'Test sisältö'
        }
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_post_form_no_title(self):
        """Testi: Lomake ilman otsikkoa hylätään"""
        form_data = {
            'title': '',
            'content': 'Test sisältö'
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_post_form_no_content(self):
        """Testi: Lomake ilman sisältöä hylätään"""
        form_data = {
            'title': 'Test Postaus',
            'content': ''
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())


class CommentFormTests(TestCase):
    """CommentForm-testit"""
    
    def test_comment_form_valid(self):
        """Testi: Kelvollinen kommenttilomake hyväksytään"""
        form_data = {'content': 'Test kommentti'}
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_comment_form_no_content(self):
        """Testi: Tyhjä kommenttilomake hylätään"""
        form_data = {'content': ''}
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())


class PostListViewTests(TestCase):
    """PostListView-testit"""
    
    def setUp(self):
        """Luo test-käyttäjän ja postauksia"""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        for i in range(7):
            Post.objects.create(
                title=f'Postaus {i+1}',
                content=f'Sisältö {i+1}',
                author=self.user
            )
    
    def test_post_list_view_status_code(self):
        """Testi: PostListView palauttaa 200 OK"""
        response = self.client.get(reverse('post-list'))
        self.assertEqual(response.status_code, 200)
    
    def test_post_list_view_template(self):
        """Testi: PostListView käyttää oikeaa templatea"""
        response = self.client.get(reverse('post-list'))
        self.assertTemplateUsed(response, 'blogisysteemi/post_list.html')
    
    def test_post_list_view_context(self):
        """Testi: Kontekstissa on 'posts'"""
        response = self.client.get(reverse('post-list'))
        self.assertIn('posts', response.context)
    
    def test_post_list_view_pagination(self):
        """Testi: Sivulla näytetään 5 postausta (paginate_by=5)"""
        response = self.client.get(reverse('post-list'))
        self.assertEqual(len(response.context['posts']), 5)
    
    def test_post_list_view_ordering(self):
        """Testi: Postaukset ovat uusimmasta vanhimpaan"""
        response = self.client.get(reverse('post-list'))
        posts = list(response.context['posts'])
        self.assertEqual(posts[0].title, 'Postaus 7')
        self.assertEqual(posts[-1].title, 'Postaus 3')


class PostDetailViewTests(TestCase):
    """PostDetailView-testit"""
    
    def setUp(self):
        """Luo test-käyttäjän ja postauksen"""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.post = Post.objects.create(
            title='Test Postaus',
            content='Test sisältö',
            author=self.user
        )
        self.comment = Comment.objects.create(
            content='Test kommentti',
            author=self.user,
            post=self.post
        )
    
    def test_post_detail_view_status_code(self):
        """Testi: PostDetailView palauttaa 200 OK"""
        response = self.client.get(reverse('post-detail', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_post_detail_view_template(self):
        """Testi: PostDetailView käyttää oikeaa templatea"""
        response = self.client.get(reverse('post-detail', kwargs={'pk': self.post.pk}))
        self.assertTemplateUsed(response, 'blogisysteemi/post_detail.html')
    
    def test_post_detail_view_context(self):
        """Testi: Kontekstissa on postaus ja kommentit"""
        response = self.client.get(reverse('post-detail', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.context['post'], self.post)
        self.assertIn('comments', response.context)
        self.assertEqual(response.context['comments'].count(), 1)
    
    def test_post_detail_view_404(self):
        """Testi: Olemattoman postauksen näyttäminen palauttaa 404"""
        response = self.client.get(reverse('post-detail', kwargs={'pk': 999}))
        self.assertEqual(response.status_code, 404)


class PostCreateViewTests(TestCase):
    """PostCreateView-testit"""
    
    def setUp(self):
        """Luo test-käyttäjän"""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
    
    def test_post_create_view_not_authenticated(self):
        """Testi: Kirjautumaton käyttäjä ohjataan kirjautumissivulle"""
        response = self.client.get(reverse('post-create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_post_create_view_authenticated(self):
        """Testi: Kirjautunut käyttäjä näkee lomakkeen"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('post-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blogisysteemi/post_form.html')
    
    def test_post_create_post_authenticated(self):
        """Testi: Uusi postaus luodaan oikein"""
        self.client.login(username='testuser', password='testpass123')
        post_data = {
            'title': 'Uusi postaus',
            'content': 'Uusi sisältö'
        }
        response = self.client.post(reverse('post-create'), post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.title, 'Uusi postaus')
        self.assertEqual(post.author, self.user)


class PostDeleteViewTests(TestCase):
    """PostDeleteView-testit"""
    
    def setUp(self):
        """Luo test-käyttäjät ja postauksia"""
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        self.post1 = Post.objects.create(
            title='User1 postaus',
            content='Sisältö',
            author=self.user1
        )
        self.post2 = Post.objects.create(
            title='User2 postaus',
            content='Sisältö',
            author=self.user2
        )
    
    def test_post_delete_not_authenticated(self):
        """Testi: Kirjautumaton käyttäjä ohjataan kirjautumissivulle"""
        response = self.client.get(reverse('post-delete', kwargs={'pk': self.post1.pk}))
        self.assertEqual(response.status_code, 302)
    
    def test_post_delete_not_author(self):
        """Testi: Muiden postauksia ei voi poistaa"""
        self.client.login(username='user2', password='pass123')
        response = self.client.post(reverse('post-delete', kwargs={'pk': self.post1.pk}))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Post.objects.filter(pk=self.post1.pk).exists())
    
    def test_post_delete_author(self):
        """Testi: Oma postaus voidaan poistaa"""
        self.client.login(username='user1', password='pass123')
        response = self.client.post(reverse('post-delete', kwargs={'pk': self.post1.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Post.objects.filter(pk=self.post1.pk).exists())


class CommentCreateViewTests(TestCase):
    """CommentCreateView-testit"""
    
    def setUp(self):
        """Luo test-käyttäjän ja postauksen"""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.post = Post.objects.create(
            title='Test Postaus',
            content='Test sisältö',
            author=self.user
        )
    
    def test_comment_create_not_authenticated(self):
        """Testi: Kirjautumaton käyttäjä ohjataan kirjautumissivulle"""
        response = self.client.post(reverse('comment-create', kwargs={'post_pk': self.post.pk}))
        self.assertEqual(response.status_code, 302)
    
    def test_comment_create_authenticated(self):
        """Testi: Kommentti luodaan oikein"""
        self.client.login(username='testuser', password='testpass123')
        comment_data = {'content': 'Uusi kommentti'}
        response = self.client.post(
            reverse('comment-create', kwargs={'post_pk': self.post.pk}),
            comment_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.content, 'Uusi kommentti')
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)
    
    def test_comment_create_redirect(self):
        """Testi: Kommentin jälkeen ohjataan takaisin postaukseen"""
        self.client.login(username='testuser', password='testpass123')
        comment_data = {'content': 'Uusi kommentti'}
        response = self.client.post(
            reverse('comment-create', kwargs={'post_pk': self.post.pk}),
            comment_data,
            follow=False
        )
        expected_url = reverse('post-detail', kwargs={'pk': self.post.pk})
        self.assertIn(expected_url, response.url)


class AuthenticationViewsTests(TestCase):
    """Autentikointinäkymien testit"""
    
    def setUp(self):
        """Luo test-käyttäjän"""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
    
    def test_login_view_status_code(self):
        """Testi: Kirjautumissivu on saatavilla"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_valid_credentials(self):
        """Testi: Oikeilla tunnisteilla kirjautuminen onnistuu"""
        response = self.client.post(
            reverse('login'),
            {'username': 'testuser', 'password': 'testpass123'}
        )
        self.assertEqual(response.status_code, 302)
    
    def test_login_invalid_credentials(self):
        """Testi: Väärillä tunnisteilla kirjautuminen epäonnistuu"""
        response = self.client.post(
            reverse('login'),
            {'username': 'testuser', 'password': 'wrongpassword'}
        )
        self.assertEqual(response.status_code, 200)
    
    def test_logout_authenticated(self):
        """Testi: Kirjautunut käyttäjä voi kirjautua ulos"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)

