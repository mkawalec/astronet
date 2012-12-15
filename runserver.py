if __name__ == '__main__':
    from astronet import app
#    from gevent.wsgi import WSGIServer
#    http_server = WSGIServer(('', 5000), app, log=None)
#    http_server.serve_forever()
    
    app.run(debug=True)
