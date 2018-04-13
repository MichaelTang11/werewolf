import tornado.ioloop
import tornado.httpserver

from application import MyApplication

def main():
    http_server=tornado.httpserver.HTTPServer(MyApplication(), xheaders=True)
    http_server.listen(8888)
    print('Development server is running at http://127.0.0.1:8888')
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
