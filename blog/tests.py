from django.test import TestCase, Client
from bs4 import BeautifulSoup   # 반드시 BeautifulSoup 모듈을 미리 설치한 후 임포트할 것!
from django.contrib.auth.models import User
from .models import Post, Category, Tag, Comment

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create_user(username='trump', password='somepassword')
        self.user_obama = User.objects.create_user(username='obama', password='somepassword')
        self.user_obama.is_staff = True
        self.user_obama.save()

        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_music = Category.objects.create(name='music', slug='music')

        self.tag_python_kr = Tag.objects.create(name='파이썬 공부', slug='파이썬-공부')
        self.tag_python = Tag.objects.create(name='python', slug='python')
        self.tag_hello = Tag.objects.create(name='hello', slug='hello')

        self.post_001 = Post.objects.create(
            title='첫 번째 포스트입니다.',
            content='Hello world. We are the world',
            category=self.category_programming, # programming 카테고리 지정
            author=self.user_trump
        )
        self.post_001.tags.add(self.tag_hello)

        self.post_002 = Post.objects.create(
            title='두 번째 포스트입니다.',
            content='1등이 전부는 아니잖아요?',
            category=self.category_music,   # music 카테고리 지정
            author=self.user_obama
        )

        self.post_003 = Post.objects.create(
            title='세 번째 포스트입니다.',
            content='카테고리가 없을 수도 있죠.',
            author=self.user_obama
        )
        self.post_003.tags.add(self.tag_python_kr)
        self.post_003.tags.add(self.tag_python)

        self.comment_001 = Comment.objects.create(
            post=self.post_001,
            author=self.user_obama,
            content='첫 번째 댓글입니다.'
        )

    def navbar_test(self, soup):
        # 1.1 내비게이션 바가 있다.
        navbar = soup.nav
        # 1.2 Blog, About, Me라는 문구가 내비게이션 바에 있다.
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        logo_btn = navbar.find('a', text='W. J. KIM')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text='About Me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')

    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(f'{self.category_programming.name} ({self.category_programming.post_set.count()})',
                      categories_card.text)
        self.assertIn(f'{self.category_music.name} ({self.category_music.post_set.count()})',
                      categories_card.text)
        self.assertIn(f'미분류 (1)', categories_card.text)

    def test_post_list(self):
        # 포스트가 있는 경우
        self.assertEqual(Post.objects.count(), 3)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.post_001.author.username.upper(), post_001_card.text)
        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertNotIn(self.tag_python.name, post_001_card.text)
        self.assertNotIn(self.tag_python_kr.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertIn(self.post_002.author.username.upper(), post_002_card.text)
        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_python.name, post_002_card.text)
        self.assertNotIn(self.tag_python_kr.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn('미분류', post_003_card.text)
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn(self.post_003.author.username.upper(), post_003_card.text)
        self.assertNotIn(self.tag_hello.name, post_003_card.text)
        self.assertIn(self.tag_python.name, post_003_card.text)
        self.assertIn(self.tag_python_kr.name, post_003_card.text)

        self.assertIn(self.user_trump.username.upper(), main_area.text)
        self.assertIn(self.user_obama.username.upper(), main_area.text)

        # 포스트가 없는 경우
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)

    def test_post_detail(self):
        # 1.2. 그 포스트의 url은 '/blog/1/'이다.
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')

        # 2.0 첫 번째 포스트의 상세 페이지 테스트
        # 2.1 첫 번째 포스트의 url로 접근하면 정상적으로 작동한다(status code: 200).
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 2.2 포스트 목록 페이지와 똑같은 내비게이션 바가 있다.
        self.navbar_test(soup)

        # 2.3 첫 번째 포스트의 제목이 웹 브라우저 탭 타이틀에 들어 있다.
        self.assertIn(self.post_001.title, soup.title.text)

        # 2.4 첫 번째 포스트의 제목이 포스트 영역에 있다.
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)

        # 2.5 태그 출력하기
        self.assertIn(self.tag_hello.name, post_area.text)
        self.assertNotIn(self.tag_python.name, post_area.text)
        self.assertNotIn(self.tag_python_kr.name, post_area.text)

        # 2.5 첫 번째 포스트의 작성자(author)가 포스트 영역에 있다.
        self.assertIn(self.user_trump.username.upper(), post_area.text)

        # 2.6 첫 번째 포스트의 내용(content)이 포스트 영역에 있다.
        self.assertIn(self.post_001.content, post_area.text)

        # comment area
        comments_area = soup.find('div', id='comment-area')
        comment_001_area = comments_area.find('div', id='comment-1')
        self.assertIn(self.comment_001.author.username, comment_001_area.text)
        self.assertIn(self.comment_001.content, comment_001_area.text)

    def test_tag_page(self):
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.tag_hello.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_hello.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_category_page(self): # 카테고리 페이지에 구성하고 싶은 요소를 테스트할 함수
        response = self.client.get(self.category_programming.get_absolute_url())    # 카테고리 페이지도 고유 URL을 갖도록 get_absolute_url() 함수를 사용
        self.assertEqual(response.status_code, 200)   # 페이지가 잘 열리는지 검사하기 위해 status_code가 200인지 검사

        soup = BeautifulSoup(response.content, 'html.parser')   # bs4로 html 파일을 파싱하기
        self.navbar_test(soup)  # 네비개이션 바 구성 확인
        self.category_card_test(soup)   # 카테고리 카드 구성 확인

        main_area = soup.find('div', id='main-area') # 파싱된 html 문서 내에서 div#main-area 태그 요소 찾기
        self.assertIn(self.category_programming.name, main_area.text)   # 위에서 선택한 카테고리 이름인 programming이 있는지 확인
        self.assertIn(self.post_001.title, main_area.text)  # programming 카테고리에 해당하는 포스트만 노출되어 있는지 확인
        self.assertNotIn(self.post_002.title, main_area.text)   # 그렇지 않은 post_002, post_003의 타이틀은 메인 영역에 존재해서는 안됨
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_create_post(self):  # 포스트 작성 페이지 실행 코드
        # 로그인하지 않으면 status code가 200이면 안된다!
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # staff가 아닌 Trump가 로그인을 한다.
        self.client.login(username='trump', password='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # staff인 obama로 로그인한다.
        self.client.login(username='obama', password='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Create Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Create New Post', main_area.text)

        # 포스트 작성 페이지에 태그 입력 기능 부여하기
        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)

        self.client.post(   # 첫 번째 인수인 해당 경로로 두 번째 인수인 딕셔너리 정보를 POST 방식으로 보냄
            '/blog/create_post/',
            {
                'title': 'Post Form 만들기',
                'content': 'Post Form 페이지를 만듭시다.',
                'tags_str': 'new tag; 한글 태그, python'
            }
        )
        self.assertEqual(Post.objects.count(), 4)
        last_post = Post.objects.last()     # Post 레코드 중 맨 마지막 레코드를 가져와 저장
        self.assertEqual(last_post.title, "Post Form 만들기")
        self.assertEqual(last_post.author.username, 'obama')

        self.assertEqual(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name='new tag'))
        self.assertTrue(Tag.objects.get(name='한글 태그'))
        self.assertEqual(Tag.objects.count(), 5)

    def test_update_post(self):
        update_post_url = f'/blog/update_post/{self.post_003.pk}/'

        # 로그인하지 않은 경우
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200)

        # 로그인은 했지만 작성자가 아닌 경우
        self.assertNotEqual(self.post_003.author, self.user_trump)
        self.client.login(
            username = self.user_trump.username,
            password = 'somepassword'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 403)

        # 작성자(obama)가 접근하는 경우
        self.client.login(
            username = self.post_003.author.username,
            password = 'somepassword'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edit Post', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)
        self.assertIn('파이썬 공부; python', tag_str_input.attrs['value'])

        response = self.client.post(
            update_post_url,
            {
                'title': '세 번째 포스트를 수정했습니다',
                'content': '안녕 세계? 우리는 하나!',
                'category': self.category_music.pk,
                'tags_str': '파이썬 공부; 한글 태그, some tag'
            },
            follow=True
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('세 번째 포스트를 수정했습니다', main_area.text)
        self.assertIn('안녕 세계? 우리는 하나!', main_area.text)
        self.assertIn(self.category_music.name, main_area.text)
        self.assertIn('파이썬 공부', main_area.text)
        self.assertIn('한글 태그', main_area.text)
        self.assertIn('some tag', main_area.text)
        self.assertNotIn('python', main_area.text)

    def test_comment_form(self):
        self.assertEqual(Comment.objects.count(), 1)    # setUp 함수에 이미 댓글이 하나 있는 상태에서 시작
        self.assertEqual(self.post_001.comment_set.count(), 1)  # 이 댓글은 self.post_001에 달린 댓글이라 self.post_001의 댓글 개수도 1개

        # 로그인하지 않은 상태
        response = self.client.get(self.post_001.get_absolute_url())    # 먼저 로그인하지 않은 상태를 테스트
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')  # id가 comment-area인 div 요소를 찾아 comment-area에 저장
        self.assertIn('Log in and leave a comment', comment_area.text)  # 로그인하지 않은 상태이므로 'Log in and leave a comment'라는 문구가 보여야 함.
        self.assertFalse(comment_area.find('form', id='comment-form'))  # 로그인하지 않은 상태이므로 id가 comment-form인 form 요소는 존재하지 않음

        # 로그인한 상태
        self.client.login(username='obama', password='somepassword')    # 이번에는 로그인한 상태를 테스트
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertNotIn('Log in and leave a comment', comment_area.text)   # 로그인한 상태이므로 'Log in and leave a comment'라는 문구는 보이지 않음.

        comment_form = comment_area.find('form', id='comment-form') # 로그인한 상태라 댓글 폼이 보이고,
        self.assertTrue(comment_form.find('textarea', id='id_content')) # 그 안에 textarea도 있음.
        response = self.client.post(    # POST 방식으로 댓글 내용을 서버에 보내고 그 결과를 response에 담음.
            self.post_001.get_absolute_url() + 'new_comment/',  # post_detail.html을 수정할 때 적용할 URL
            {
                'content': "오바마의 댓글입니다.",
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(Comment.objects.count(), 2) # 댓글이 원래 하나였다가 response에서 새로 하나 추가되어 2개가 됨.
        self.assertEqual(self.post_001.comment_set.count(), 2) # self.post_001에서 댓글이 1개였다가 이제 2개가 됨.
        new_comment = Comment.objects.last()    # 마지막으로 생성된 comment를 가져옮.

        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertIn(new_comment.post.title, soup.title.text)  # POST 방식으로 서버에 요청에 comment가 달린 포스트 상세 페이지가 리다이렉트됨.

        comment_area = soup.find('div', id='comment-area')  # 새로 만든 comment의 작성자가 나타남.
        new_comment_div = comment_area.find('div', id=f'comment-{new_comment.pk}')
        self.assertIn('obama', new_comment_div.text)
        self.assertIn('오바마의 댓글입니다.', new_comment_div.text)

    def test_comment_update(self):
        comment_by_trump = Comment.objects.create(  # 다른 사람이 작성한 댓글이 있어야 하므로 comment_by_trump로 새로 만듦.
            post=self.post_001,
            author=self.user_trump,
            content='트럼프의 댓글입니다.'
        )
        response = self.client.get(self.post_001.get_absolute_url())    # 로그인하지 않은 상태에서 댓글이 2개 있는 self.post_001 페이지를 엶.
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')  # 댓글 영역에 수정 버튼이 둘 다 보이지 않아야 하므로
        self.assertFalse(comment_area.find('a', id='comment-1-update-btn')) # 수정 버튼의 id는 comment-해당 comment의 pk-update-btn으로 만들기
        self.assertFalse(comment_area.find('a', id='comment-2-update-btn')) # 수정 버튼의 id는 comment-해당 comment의 pk-update-btn으로 만들기

        # 로그인한 상태
        self.client.login(username='obama', password='somepassword')    # obama로 로그인했으므로
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertFalse(comment_area.find('a', id='comment-2-update-btn')) # trump가 작성한 댓글에 대한 수정 버튼은 보이지 않아야 함.
        comment_001_update_btn = comment_area.find('a', id='comment-1-update-btn')  # 반면 obama가 작성한 댓글 self.comment_001에 대한 수정 버튼은 나타나야 함.
        self.assertIn('edit', comment_001_update_btn.text)  # 이 수정 버튼에는 edit라고 써 있어야 함.
        self.assertEqual(comment_001_update_btn.attrs['href'], '/blog/update_comment/1/')   # 링크 경로를 담은 속성: blog/update_comment/해당 comment의 pk

        self.assertIn('edit', comment_001_update_btn.text)
        self.assertEqual(comment_001_update_btn.attrs['href'], '/blog/update_comment/1/')

        response = self.client.get('/blog/update_comment/1/')   # edit 버튼을 클릭하면 댓글 수정 폼으로 넘어감.
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Comment - Blog', soup.title.text)    # 페이지 타이틀: Edit Comment - Blog
        update_comment_form = soup.find('form', id='comment-form')
        content_textarea = update_comment_form.find('textarea', id='id_content')
        self.assertIn(self.comment_001.content, content_textarea.text)  # 폼 안에 id_content인 textarea가 담기고 그 안에 수정 전 comment 내용이 담겨야 함.

        response = self.client.post(    # self.client.post로 content를 수정하고 submit하면 수정되는 기능을 구현
            f'/blog/update_comment/{self.comment_001.pk}/',
            {
                'content': "오바마의 댓글을 수정합니다.",
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        comment_001_div = soup.find('div', id='comment-1')
        self.assertIn('오바마의 댓글을 수정합니다.', comment_001_div.text)
        self.assertIn('Updated: ', comment_001_div.text)