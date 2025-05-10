from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views import View
from authors.models import Author
import json
import uuid
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

#  Fetch Author as JSON
class AuthorDetailJSONView(View):
    def get(self, request, author_id):
        author = get_object_or_404(Author, id=author_id)
        return JsonResponse({
            "id": str(author.id),
            "global_id": author.global_id,
            "display_name": author.display_name,
            "host": author.host,
            "github": author.github,
            "profile_image": author.profile_image,
        })
    
@method_decorator(csrf_exempt, name='dispatch')
class AuthorListView(View):
    """Handles listing all authors and creating new authors."""

    def get(self, request):
        """Retrieve a list of all authors."""
        authors = Author.objects.all().values("global_id", "display_name", "host", "github", "profile_image")
        authors = [
            {
                "type": "author",
                "id": str(author["global_id"]),
                "displayName": author["display_name"],
                "host": author["host"],
                "github": author["github"],
                "profileImage": author["profile_image"],
            }
            for author in authors
        ]
        return JsonResponse({"type":"authors", "authors":authors}, safe=False)

    def post(self, request):
        """Create a new author and generate a unique `global_id`."""
        try:
            data = json.loads(request.body)
            author_id = uuid.uuid4()
            global_id = f"http://127.0.0.1:8000/authors/{author_id}"  #  Ensure uniqueness

            author = Author.objects.create(
                id=author_id,
                display_name=data["display_name"],
                host=data["host"],
                global_id=global_id,
                github=data.get("github", ""),
                profile_image=data.get("profile_image", ""),
            )

            return JsonResponse({
                "id": str(author.id),
                "global_id": author.global_id,
                "display_name": author.display_name,
                "host": author.host,
                "github": author.github,
                "profile_image": author.profile_image,
            }, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        
