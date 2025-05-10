import requests
from authors.models import Node, ForeignComments, ForeignPost, ForeignAuthor, ForeignPostLike
from requests.auth import HTTPBasicAuth
from django.utils import timezone

def fetch_foreign_comments(foreign_post):
    '''Fetch the comments for a given foreign post and store them in the database'''

    try:
        node = Node.objects.get(base_url__in=foreign_post.global_id)
    except Node.DoesNotExist:
        print(f'No matching node found for {foreign_post.global_id}')
        return []
    
    url = f'{foreign_post.global_id.rstrip('/')}/comments/'
    try:
        response = requests.get(
            url, 
            auth=HTTPBasicAuth(node.username, node.password),
            headers={'Accept': 'application/json'},
            timeout=10
        )
    except Exception as e:
        print(f'Error fetching comments for {foreign_post.global_id}: {e}')
        return []

    if response.status_code == 200:
        data = response.json()
        comments = data.get('comments', data.get('items', []))

        for c in comments:
            global_id = c.get('id')
            if not global_id or ForeignComments.objects.filter(global_id=global_id).exists():
                continue # Skip if the comment is already in the database

            author_data = c.get('author', {})
            foreign_author, _ = ForeignAuthor.objects.get_or_create(
                global_id=author_data.get('id'),
                defaults={
                    'display_name': author_data.get('displayName', 'Unknown'),
                    'host': author_data.get('host', ''),
                    'url': author_data.get('url', author_data.get('id')),
                }
            )
            ForeignComments.objects.create(
                global_id=global_id,
                foreign_post=foreign_post,
                foreign_author=foreign_author,
                comment = c.get('comment', ''),
                content_type = c.get('contentType', 'text/plain'),
                published = c.get('published', timezone.now())
            )
        print(f'Fetched {len(comments)} comments for {foreign_post.global_id}')
    else:
        print(f'Error fetching comments for {foreign_post.global_id}: {response.status_code}')
        return []

    return ForeignComments.objects.filter(foreign_post=foreign_post)

def fetch_foreign_post_likes(foreign_post):
    '''Fetch the likes for a given foreign post and store them in the database'''
    try:
        node = Node.objects.get(base_url__in=foreign_post.global_id)
    except Node.DoesNotExist:
        print(f'No matching node found for {foreign_post.global_id}')
        return []
    
    url = f'{foreign_post.global_id.rstrip('/')}/likes/'
    try:
        response = requests.get(
            url,
            auth=HTTPBasicAuth(node.username, node.password),
            headers={'Accept': 'application/json'},
            timeout=10
        )
    except Exception as e:
        print(f'Error fetching likes for {foreign_post.global_id}: {e}')
        return []
    
    if response.status_code == 200:
        data = response.json()
        likes = data.get('likes', data.get('items', []))

        for like in likes:
            global_id = like.get('id')
            if not global_id or ForeignPostLike.objects.filter(global_id=global_id).exists():
                continue # Skip if the like is already in the database

            author_data = like.get('author', {})
            foreign_author, _ = ForeignAuthor.objects.get_or_create(
                global_id=author_data.get('id'),
                defaults={
                    'display_name': author_data.get('displayName', 'Unknown'),
                    'host': author_data.get('host', ''),
                    'url': author_data.get('url', author_data.get('id')),
                }
            )
            ForeignPostLike.objects.create(
                global_id=global_id,
                foreign_post=foreign_post,
                foreign_author=foreign_author,
                published = like.get('published', timezone.now())
            )

        print(f'Fetched {len(likes)} likes for {foreign_post.global_id}')
    else:
        print(f'Error fetching likes for {foreign_post.global_id}: {response.status_code}')
        return []
    
    return ForeignPostLike.objects.filter(foreign_post=foreign_post)