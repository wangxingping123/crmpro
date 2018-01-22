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


class LoginMiddleware(MiddlewareMixin):
    def process_request(self,request):
        current_url=request.path_info
        for url in settings.LOGIN_WHITE_LIST:
            if re.match(url,current_url):
                return None
        if request.session.get('user_info'):
            return None
        return redirect('/user_login/')


class MiddleWare(MiddlewareMixin):

    def process_request(self,request):

        url=request.path_info

        for white_url in settings.WHITE_LIST:

            if re.match(white_url,url):

                return None

        db_urls=request.session.get(settings.PERMISSIONS_URL_DIC)
        if not db_urls:
            return redirect("/user_login/")
        flag=False
        for group_id,code_url in db_urls.items():
            for db_url in code_url["urls"]:
                db_url='^{0}$'.format(db_url)
                if re.match(db_url,url):
                    request.permission_code_list = code_url['codes']
                    flag=True
                    break
            if flag:
                break
        if not flag:
            return HttpResponse("抱歉，你无权访问")



