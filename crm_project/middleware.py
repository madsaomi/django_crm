from django.shortcuts import render
from django.http import Http404

class CustomErrorMiddleware:
    """
    Middleware для перехвата 404 и 500 ошибок и рендеринга кастомных анимированных шаблонов,
    даже если DEBUG = True.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Перехватываем 404, если URL не найден (Django не бросает исключение, а генерирует пустой 404 response)
        if response.status_code == 404:
            return render(request, '404.html', status=404)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, Http404):
            return render(request, '404.html', status=404)
        
        # Перехват остальных серверных ошибок
        import traceback
        import sys
        
        # Для логов
        print(f"Exception caught in CustomErrorMiddleware: {exception}", file=sys.stderr)
        traceback.print_exc()

        # Показываем причину
        context = {
            'error_message': str(exception) or "Неизвестная внутренняя ошибка сервера"
        }
        return render(request, '500.html', context, status=500)
