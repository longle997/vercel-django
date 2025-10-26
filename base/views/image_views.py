from pathlib import Path
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest, Http404
from rest_framework.decorators import api_view

@api_view(["POST"])
def images_in_folder(request):
    folder = (request.data.get("folder") or "").strip("/")  # subfolder under MEDIA_ROOT

    base = Path(settings.MEDIA_ROOT).resolve()
    target = (base / folder).resolve()

    # simple safety: keep inside MEDIA_ROOT
    if base not in target.parents and base != target:
        return HttpResponseBadRequest("Invalid folder path.")

    if not target.exists() or not target.is_dir():
        raise Http404("Folder not found.")

    exts = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
    results = []
    for p in target.iterdir():  # non-recursive, simplest
        if p.is_file() and p.suffix.lower() in exts:
            rel = p.relative_to(base).as_posix()
            results.append({
                "name": p.name,
                "url": request.build_absolute_uri(settings.MEDIA_URL + rel),
            })

    return JsonResponse({"folder": folder, "count": len(results), "results": results})
