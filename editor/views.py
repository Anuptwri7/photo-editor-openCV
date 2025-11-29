import base64, json, sys
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .processing import apply_server_filter
from PIL import Image

def index(request):
    return render(request, 'editor/index.html')

@csrf_exempt
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        from .models import Photo
        p = Photo.objects.create(original=request.FILES['image'])
        return JsonResponse({'status':'ok','url': p.original.url})
    return JsonResponse({'status':'error','msg':'POST an image file'}, status=400)


@csrf_exempt
def process_image(request):
    print("=== process_image called ===", file=sys.stdout)
    print("method:", request.method, file=sys.stdout)
    print("body length:", len(request.body), file=sys.stdout)
    sys.stdout.flush()

    if request.method != "POST":
        return JsonResponse({'status':'error','msg':'POST only'}, status=400)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception as e:
        print("json parse error:", e, file=sys.stdout)
        sys.stdout.flush()
        return JsonResponse({'status':'error','msg':'invalid json'}, status=400)

    filter_name = data.get('filter')
    print("filter_name received:", filter_name, file=sys.stdout)

    img_b64 = data.get('image_b64')
    if not img_b64:
        print("no image_b64 in payload", file=sys.stdout)
        sys.stdout.flush()
        return JsonResponse({'status':'error','msg':'no image'}, status=400)

    print("image_b64 length:", len(img_b64), file=sys.stdout)
    sys.stdout.flush()

    try:
        header, b64 = img_b64.split(',', 1)
        img_bytes = base64.b64decode(b64)
    except Exception as e:
        print("base64 decode error:", e, file=sys.stdout)
        sys.stdout.flush()
        return JsonResponse({'status':'error','msg':'bad base64'}, status=400)

    out_bytes = apply_server_filter(img_bytes, filter_name)
    if out_bytes is None:
        print("apply_server_filter returned None", file=sys.stdout)
        sys.stdout.flush()
        return JsonResponse({'status':'error','msg':'processing failed'}, status=500)

    out_b64 = "data:image/png;base64," + base64.b64encode(out_bytes).decode('utf-8')

    print("sending processed image back", file=sys.stdout)
    sys.stdout.flush()

    return JsonResponse({'status':'ok','image_b64': out_b64})
