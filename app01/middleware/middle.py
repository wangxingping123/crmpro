import re
from django.shortcuts import redirect,HttpResponse
from django.conf import settings

class MiddlewareMixin(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super(MiddlewareMixin, self).__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response

class MiddleWare(MiddlewareMixin):

    def process_request(self,request):

        url=request.path_info

        for white_url in settings.WHITE_LIST:
            if re.match(white_url,url):
                return None

        status=request.session.get("userinfo").get("status")
        if not status:
            return redirect("/user_login/")

        return None


