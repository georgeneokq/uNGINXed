from werkzeug.wrappers import Response


class TestApp(object):
    """Implements a WSGI application for managing your favorite movies."""
    def __init__(self):
        pass

    def dispatch_request(self, request):
        """Dispatches the request."""
        return Response('Hello World!')


    def wsgi_app(self, environ, start_response):
        """WSGI application that processes requests and returns responses."""
        start_response('500 Error', [('Content-Type','text/html'),('Secret-Header','secret-info')])
        return [b"Secret info, should not be visible!"]

    def __call__(self, environ, start_response):
        """The WSGI server calls this method as the WSGI application."""
        return self.wsgi_app(environ, start_response)


def create_app():
    """Application factory function that returns an instance of MovieApp."""
    app = TestApp()
    return app

if __name__ == '__main__':
    # Run the Werkzeug development server to serve the WSGI application (MovieApp)
    from werkzeug.serving import run_simple
    app = create_app()
    run_simple('127.0.0.1', 8080, app, use_debugger=False, use_reloader=True)

